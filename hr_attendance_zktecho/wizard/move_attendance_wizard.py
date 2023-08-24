# -*- coding: utf-8 -*-

import operator
import logging
_logger = logging.getLogger('move_attendance')

from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import except_orm, UserError


class move_attendance_wizard(models.TransientModel):
    
    _name = "move.draft.attendance.wizard"
    
    date1 = fields.Datetime('From', required=True)
    date2 = fields.Datetime('To', required=True)
    employee_ids = fields.Many2many('hr.employee', 'move_att_employee_rel', 'employee_id', 'wiz_id')

    def remove_mid_day_attendance(self, attendance_dic):
        """ keeps only 2 draft attendances per day max for any day
        """
        for key, value in attendance_dic.items():
            if len(value) > 2:
                draft_recs = self.env["hr.draft.attendance"]
                for rec in value:
                    draft_recs += rec
                max_record = draft_recs.filtered(lambda x: x.name == max(draft_recs.mapped("name")))
                min_record = draft_recs.filtered(lambda x: x.name == min(draft_recs.mapped("name")))
                new_value = [max_record, min_record]

                attendance_dic.update({key: new_value})
        return attendance_dic

    def get_employees(self):
        if self.employee_ids:
            employees = self.employee_ids
        else:
            employees = self.env['hr.employee'].search([])
        return employees

    def get_employee_calendar(self, employee):
        active_calendar_line = employee.calender_lines and employee.calender_lines.filtered(lambda x: x.is_current)
        current_calendar = active_calendar_line.calender_id
        if not current_calendar:
            current_calendar = employee.resource_calendar_id
        return current_calendar

    def update_drafts_dict(self, employee, drafts_dict):
        """
        :param employee:
        :param drafts_dict: old dict to be updates
        :return:  {"employee_id": {date: [list of draft attendance], ..}, ...} """
        domain = [('employee_id', '=', employee.id), ('attendance_status', '!=', 'sign_none'),
                  ('name', '>=', self.date1), ('name', '<=', self.date2), ('moved', '=', False)]
        draft_attendances = self.env['hr.draft.attendance'].search(domain, order='name asc')
        if draft_attendances:
            drafts_dict[employee.id] = {}
            for draft_attend in draft_attendances:
                if draft_attend.date in drafts_dict[employee.id]:
                    drafts_dict[employee.id][draft_attend.date].append(draft_attend)
                else:
                    drafts_dict[employee.id][draft_attend.date] = []
                    drafts_dict[employee.id][draft_attend.date].append(draft_attend)

            # attend_dict = self.remove_mid_day_attendance(drafts_dict[employee.id])
            # drafts_dict.update({employee.id: attend_dict})
        else:
            _logger.warning('Valid Draft Attendance records not found for employee ' + str(employee.name))
        return drafts_dict

    # @api.one
    def move_confirm(self):
        try:
            attendance_obj = self.env['hr.attendance']
            employees = self.get_employees()
            drafts_dict = {}    # {employee_id: {date: [draft attendance on that day]}, ..}
            for employee in employees:
                drafts_dict = self.update_drafts_dict(employee, drafts_dict)
            if drafts_dict:
                _logger.info('\n ** Processing draft attendances ** \n')
                for emp in drafts_dict:
                    _logger.info('..Processing employee with id ' + str(emp))
                    employee_dic = drafts_dict[emp]     # {date: [draft attendance on that day], ..}
                    sorted_employee_dic = sorted(employee_dic.items(), key=operator.itemgetter(0))
                    # [(date, [draft attendace for that day]), ....]
                    last_action = False
                    for emp_attendance_day in sorted_employee_dic: # item here is a tuple (date, [list of records])
                        _logger.info('...Processing draft records on date ' + str(emp_attendance_day))
                        day_drafts_list = emp_attendance_day[1]     # list of records
                        # line here means a draft record
                        for line in day_drafts_list:
                            _logger.info('....Processing draft record ' + str(line) + " On time: " + str(line.name))
                            # check if this line matches check_in or check_our
                            # ###############################
                            emp_check = float("%d.%d"%(line.name.hour+3, round(line.name.minute, 0)))
                            emp_resource_calendar_id = self.get_employee_calendar(line.employee_id)
                            # emp_resource_calendar_id = line.employee_id.resource_calendar_id
                            check_in_line = emp_resource_calendar_id.attendance_ids.filtered(lambda l:l.dayofweek == str(line.name.weekday()) and emp_check >= l.begin_in and  emp_check <= l.end_in )
                            check_out_line = emp_resource_calendar_id.attendance_ids.filtered(lambda l:l.dayofweek == str(line.name.weekday()) and emp_check >= l.begin_out and  emp_check <= l.end_out )
                            # ##############################################
                            attendance_status = 'sign_none'

                            if check_in_line:
                                attendance_status = 'sign_in'
                            if check_out_line:
                                attendance_status = 'sign_out'

                            # ########################################################
                            if line.attendance_status != 'sign_none':

                                if attendance_status == 'sign_in':
                                    _logger.info('.....Processing CHECK IN draft record ' + str(line) + ' -- ' + str(attendance_status))
                                    line.moved = True
                                    check_in = line.name

                                    hr_attendance = attendance_obj.search([
                                        ('day', '=', line.date), ('employee_id', '=', line.employee_id.id), ("check_in", "!=", False)])
                                    vals = {
                                        'employee_id': line.employee_id.id,
                                        'name': check_in,
                                        'day': line.date,
                                        'check_in': check_in,
                                    }
                                    if not hr_attendance:
                                        # if last_action != attendance_status:
                                        created_rec = hr_attendance.create(vals)
                                        created_rec.calculate_rules(check_in_line)
                                        line.moved_to = created_rec.id
                                        _logger.info('Create Attendance ' + str(created_rec) + ' for '+ str(line.employee_id.name)+ ' on ' + str(line.name))
                                        # else:
                                    else:  # overwrite existing values with an earlier check in time
                                        line.moved_to = hr_attendance.ids[0]
                                        hr_attendance.calculate_rules(check_in_line)
                                        if hr_attendance.check_in > line.name:
                                            hr_attendance.write(vals)
                                            _logger.info('overwriting check_in time because an eariler one was found')
                                        else:
                                            _logger.info('new check_in was not eariler so it will not be used')

                                        # _logger.info('Skipping Create Attendance because it already exists for '+ str(line.employee_id.name)+' on ' + str(line.name))
                                elif attendance_status == 'sign_out':
                                    _logger.info('.....Processing CHECK OUT draft record ' + str(line) + ' -- ' + str(attendance_status))
                                    check_out = line.name
                                    line.moved = True
                                    hr_attendance_ids = attendance_obj.search([('employee_id','=',line.employee_id.id), ('day','=',line.date)])
                                    if hr_attendance_ids:
                                        for attend_id in hr_attendance_ids:
                                            if attend_id.day == line.date and attend_id.check_in:
                                                # here
                                                attend_id.calculate_rules(check_out_line)
                                                line.moved_to = attend_id.id
                                                if not attend_id.check_out:
                                                    attend_id.write({'check_out': check_out})
                                                    _logger.info('Updated '+str(attend_id.day)+ "'s Attendance, "+str(line.employee_id.name)+ ' Checked Out at: '+ str(check_out))
                                                elif attend_id.check_out < line.name:
                                                    attend_id.write({'check_out': check_out})

                                        # if not line.moved:
                                        #     _logger.warn('Unable to find relevant attendance record on '+str(line.date)+ " for Attendance, "+str(line.employee_id.name)+ ' Checked Out at: '+ str(check_out))
                                    else:
                                        # no record found but going to create one anyways
                                        vals = {
                                            'employee_id': line.employee_id.id,
                                            'name': line.name,
                                            'day': line.date,
                                            'check_out': check_out,
                                            'check_in': False,
                                        }
                                        created_rec = attendance_obj.create(vals)
                                        created_rec.calculate_rules(check_out_line)
                                        line.moved_to = created_rec.id
                                        _logger.info('Create Attendance  with only check out' + str(created_rec) + ' for ' + str(
                                            line.employee_id.name) + ' on ' + str(line.name))
                                else:
                                    # this line did not match check in or check out
                                    line.moved = True
                                    line.skipped = True
                                    _logger.warning('Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in) at '+str(line.name)+' for '+str(line.employee_id.name))
                                last_action = attendance_status

                            else:
                                # this line did not match check in or check out
                                line.moved = True
                                line.skipped = True
                                _logger.warning('....invalid draft state ' + str(attendance_status) + ' -- ' + str(line))
        except Exception as e:
            # raise any error occurred during the move process
            raise UserError("The following error occurred while moving attendances.\n\n" + str(e))
