# -*- coding: utf-8 -*-

import datetime as dtime
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError, ValidationError
from dateutil import relativedelta as re
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ModifyAttendanceLines(models.TransientModel):
    _name = 'modify.attendance.lines'
    _description = 'Swap Log Records'

    log_id = fields.Many2one("hr.attendance.log", string="Log")
    flag = fields.Boolean(string="Flag", related="log_id.flag", store=True)
    machine_id = fields.Many2one('biometric.machine', string='Machine No', related="log_id.machine_id")
    time = fields.Datetime(string="Time", related="log_id.time")
    attendance_id = fields.Many2one("hr.attendance", string="Attendance")
    wizard_id = fields.Many2one("modify.attendance.record.wizard", string="Wizard")
    select = fields.Boolean(string="Select", default=False)
    to_add = fields.Boolean(string="Can Be Added", default=False)
    to_remove = fields.Boolean(string="Can Be Removed", default=False)

# ###################################################################################


class ModifyAttendanceRecordWizard(models.TransientModel):
    _name = 'modify.attendance.record.wizard'
    _description = 'Change Attendance Record'

    TYPE_SEL = [
        ('off_overtime_hours', 'Off Duty Overtime Hours'),
        ('swap_logs', 'Swap'),
    ]

    @api.model
    def default_get(self, fields):
        result = super(ModifyAttendanceRecordWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        type = self._context.get('type')
        if type != "swap" and active_id:
            record = self.env["hr.attendance"].browse([active_id])
            result['attendance_id'] = record.id
            result['employee_id'] = record.employee_id.id
            check_in = record.expected_check_in
            date_from = check_in and dtime.datetime.strptime(check_in, DEFAULT_SERVER_DATETIME_FORMAT).date()
            check_out = record.expected_check_out
            date_to = dtime.datetime.strptime(check_out, DEFAULT_SERVER_DATETIME_FORMAT).date()
            result['date_from'] = str(date_from)
            result['date_to'] = str(date_to)
            if record.is_off_duty_overtime:
                result['original_hours'] = record.over_time_off
        return result

    # current record
    attendance_id = fields.Many2one("hr.attendance", string="Attendance")
    employee_id = fields.Many2one("hr.employee", string="Employee")

    # wizard
    type = fields.Selection(TYPE_SEL, string="Operation Type")

    # overtime
    original_hours = fields.Float(string="Current Hours")
    new_hours = fields.Float(string="Correct Hours")

    # swap
    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date from")
    log_lines = fields.One2many("modify.attendance.lines", "wizard_id", string="Other Logs")

    #@api.multi
    def do_set_overtime_hours(self):
        """ sets the correct hours for overtime off duty record """
        attendance = self.attendance_id
        new_ov_hours = self.new_hours
        if attendance and new_ov_hours:
            if attendance.is_off_duty_overtime:
                vals = {
                    'over_time_off': new_ov_hours,
                    'is_complete': True,
                    'is_passed': True,
                    'state_attendance': 'off_duty_complete',
                    'is_manual_modify': True,
                }
                attendance.write(vals)
            else:
                raise UserError(_("This attendance record type is not Overtime Off Duty"))
        else: raise UserError(_("Missing Information"))

# ##########################################################################################
    #@api.multi
    def action_next_view(self):
        attendance = self.attendance_id
        # can't manually modify record until cron is done with it
        if not attendance.is_passed:
            raise UserError(_("This Attendance Record is still active and can be edited automatically,\
                              please wait until the time is greater than the maximum checkout time."))
        self.get_attendance_logs()
        action = self.env.ref('hr_attendance_extender.modify_attendance_record_window_action_2').read()[0]
        if action:
            action['views'] = [(self.env.ref('hr_attendance_extender.swap_attendance_record_form').id, 'form')]
            action['res_id'] = self.id
            action['active_id'] = self.id
        return action

    def get_attendance_logs(self):
        t = dtime.time()
        date_from = dtime.datetime.combine(dtime.datetime.strptime(self.date_from, fields.DATE_FORMAT), t)
        date_to = dtime.datetime.combine(
            dtime.datetime.strptime(self.date_to, fields.DATE_FORMAT), t.replace(hour=23, minute=59, second=59))
        employee = self.employee_id
        attendance = self.attendance_id
        if attendance:

            other_log_ids = self.env['hr.attendance.log'].search(
                [('time', '>=', str(date_from)), ('time', '<=', str(date_to)), ('employee_id', '=', employee.id),
                 '|', ('attend_id', '!=', attendance.id), ('attend_id', '=', False)])
            lines_obj = self.env["modify.attendance.lines"]
            # add log ids that are not in the current attendance record
            for log in other_log_ids:
                vals = {
                    'log_id': log.id,
                    'to_add': True,
                }
                line = lines_obj.create(vals)
                self.log_lines += line

            # add log ids that are in the current attendance record
            for log in attendance.log_ids:
                vals = {
                    'log_id': log.id,
                    'to_remove': True,
                }
                line = lines_obj.create(vals)
                self.log_lines += line

    def reset_record(self, state_attendance):
        if state_attendance in ["in_out_missing", "absent"]:
            worked_hours = overtime = under_time = over_time_off = 0
        # if state_attendance in ["in_out_missing", "absent"]:
            vals= {
                'worked_hours': worked_hours,
                'overtime': overtime,
                'under_time': under_time,
                'over_time_off': over_time_off,
            }
            return vals

    def recompute_attendance_record(self, attendance):
        """" mimic the behaviour of HRAttendance.compute_attendance
            or the behaviour of compute_over_time_off_duty
        """
        if not attendance.is_off_duty_overtime:
            values = attendance.get_check_in_and_check_out()
            is_passed = values.get('is_passed')
            is_complete = values.get('is_complete')
            if is_passed:
                values = attendance.get_absent(values)
                absent = values.get('is_absent')
                if absent:
                    values.update({
                        'worked_hours': 0,
                        'over_time': 0,
                        'under_time': 0,
                        'over_time_off': 0,
                    })
                else:
                    values = attendance.get_state(values)
                if is_complete and not absent:
                    values = attendance.get_hours(values)
            else:
                values.update(
                    {
                        'state_attendance': False,
                        'state': "draft",
                        'check_in': False,
                        'check_out': False,
                        'worked_hours': 0,
                        'over_time': 0,
                        'under_time': 0,
                        'over_time_off': 0,
                    }
                )

        #####################################################

        else:
            values = attendance.get_check_in_and_check_out()
            if values.get("is_passed"):
                if not values.get("check_out"):
                    values.update({
                        "state_attendance": "off_duty_out_missing",
                    })
                    state_attendance = values.get("state_attendance")
                    values.update(self.reset_record(state_attendance))
                elif values.get("check_in") and values.get("check_out"):
                    values = attendance.get_hours(values)
                    values.update(
                        {
                            "state_attendance": "off_duty_complete",
                            "is_complete": True,
                            "state": 'validate',
                        })
            else:
                values.update(
                    {
                        'state_attendance': False,
                        'state': "draft",
                        'check_in': False,
                        'check_out': False,
                        'worked_hours': 0,
                        'over_time': 0,
                        'under_time': 0,
                        'over_time_off': 0,
                    }
                )
        attendance.write(values)

    def remove_logs(self, attendance, logs):
        attendance.log_ids -= logs
        logs.write({
            'flag': False
        })
        self.recompute_attendance_record(attendance)

    def add_logs(self, current_attendance, logs):
        attendance_ids = logs.mapped("attend_id")
        for attendance in attendance_ids:
            remove_logs = logs.filtered(lambda r: r.attend_id == attendance.id)
            self.remove_logs(attendance, remove_logs)
            # recompute record for every attendance that has logs removed from it
            self.recompute_attendance_record(attendance)
        current_attendance.log_ids += logs
        # handle unflagged
        unflagged = logs.filtered(lambda r: not r.flag)
        unflagged.write({
                    'flag': True})
        self.recompute_attendance_record(current_attendance)

    #@api.multi
    def do_swap(self):
        current_attendance = self.attendance_id
        all_log = self.log_lines.filtered(lambda r: r.select)
        add_lines = all_log.filtered(lambda r: r.to_add)
        add_logs = add_lines.mapped("log_id")
        remove_lines = all_log.filtered(lambda r: r.to_remove)
        remove_logs = remove_lines.mapped("log_id")
        if remove_logs:
            self.remove_logs(current_attendance, remove_logs)
        if add_logs:
            self.add_logs(current_attendance, add_logs)



