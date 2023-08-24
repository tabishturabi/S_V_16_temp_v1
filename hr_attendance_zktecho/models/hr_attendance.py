# -*- coding: utf-8 -*-

from __future__ import division
from datetime import *
import pytz
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from pytz import timezone, UTC

from odoo import api, fields, models, exceptions, _


class CalendarResource(models.Model):

    _inherit = 'resource.calendar'

    max_late_minutes = fields.Float('Max Late Minutes', default=5.0)
    max_early_muintes = fields.Float('Max Early Munites')
    break_duration = fields.Float("Break Duration", default=0.0)

#########################################################################


class hr_attendance(models.Model):

    _inherit = "hr.attendance"

    check_in = fields.Datetime(string="Check In", required=False, default=False)

    # @api.multi
    def name_get(self):
        result = []
        for attendance in self:
            if not attendance.check_out:
                result.append((attendance.id, _("%(empl_name)s") % {
                    'empl_name': attendance.employee_id.name,
                }))
            else:
                result.append((attendance.id, _("%(empl_name)s to %(check_out)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_out': fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance,
                                                                                             fields.Datetime.from_string(
                                                                                                 attendance.check_out))),
                }))
                
        return result
    

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        for attendance in self:
            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], limit=1, order="check_in ASC")
                # if no_check_out_attendances:
                #     raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                #         'empl_name': attendance.employee_id.name,
                #         'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(no_check_out_attendances.check_in))),
                #     })
        return True
        # super(hr_attendance, self)._check_validity()
        
    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                if attendance.check_out < attendance.check_in:
                    raise exceptions.ValidationError(_('"Check Out" time cannot be earlier than "Check In" time.\n Employee: "%s"\n Check in: "%s"\n Check out: "%s"')%(attendance.employee_id.name,str(attendance.check_in),str(attendance.check_out)))
    
    def convert_to_float(self, time_att):
        h_m_s = time_att.split(":")
        hours = int(h_m_s[0])
        minutes_1 = float(h_m_s[1])/60.0
        minutes = ("%.2f" % minutes_1)
        return hours+float(minutes)
    
    def minutes_late(self, calendar, check_in, max_late_minutes,att):
        day_of_week = {'Monday':'0' ,'Tuesday':'1' ,'Wednesday':'2' ,'Thursday':'3' ,'Friday':'4' ,'Saturday':'5' ,'Sunday':'6' }
        date_from = check_in
        time_2 = str(date_from.time())
        day_id = date_from.strftime('%A')
        shifted_time = False
        att_line_target = False 
        if calendar:
            for day in calendar.attendance_ids:
                if str(day.dayofweek) == day_of_week[day_id]:
                    time_float = self.convert_to_float(time_2)
                    time_hour = day.hour_from
                    if shifted_time != False:
                        if shifted_time > abs(time_float - time_hour):
                            shifted_time = abs(time_float - time_hour)
                            att_line_target = day
                    else:
                        shifted_time = abs(time_float - time_hour)
                        att_line_target = day
                        
                    if check_in.hour <= att_line_target.hour_to:
                        break
            if att_line_target:
                time_hour = att_line_target.hour_from
                start_hour = int(time_hour)
                start_minute = int((time_hour - start_hour)*60)
                att_hour = int(date_from.strftime('%H'))
                att_minute = int(date_from.strftime('%M'))
                att_second = int(date_from.strftime('%S'))
                new_hour = (att_hour-start_hour)
                new_minute = (att_minute-start_minute)
                new_minute_1 = int(max_late_minutes)
                
                if check_in.hour >= att_line_target.hour_to:
                    return 0.0
                if new_hour > 0:
                    return (new_hour*60)+new_minute
                elif new_hour == 0 and new_minute > max_late_minutes:
                    return new_minute
                elif new_hour == 0 and new_minute == max_late_minutes and att_second > 0:
                    return new_minute_1
        return 0.0
    
    def get_inside_calendar_duration(self, calendar, check_in, check_out, att):
        day_of_week = {'Monday':'0' ,'Tuesday':'1' ,'Wednesday':'2' ,'Thursday':'3' ,'Friday':'4' ,'Saturday':'5' ,'Sunday':'6' }
        day_id = check_in.strftime('%A')
        att_line_target = False 
        att_line_target_1 = False
        in_duration = 0.0
        out_duration = 0.0
        period_deff = 0.0
        working_hours = 0.0
        if calendar:
            for day in calendar.attendance_ids:
                if str(day.dayofweek) == day_of_week[day_id]:
                    att_line_target = day
                    if att_line_target_1 == False:
                        att_line_target_1 = day
                    if att_line_target_1 == day:
                        att_line_target_1 = day
            period_deff = att_line_target.hour_from - att_line_target_1.hour_to if att_line_target != att_line_target_1 else calendar.break_duration
            worked_hours = att.worked_hours
            if att_line_target and att_line_target_1:
                first_from_hour = att_line_target_1.hour_from
                first_to_hour = att_line_target_1.hour_to
                second_from_hour = att_line_target.hour_from
                second_to_hour = att_line_target.hour_to
                check_in_time = self.convert_to_float(str(check_in.time()))
                check_out_time = self.convert_to_float(str(check_out.time()))
                if att_line_target != att_line_target_1:
                    working_hours = att_line_target_1.hour_to- att_line_target_1.hour_from
                else:
                    working_hours = (att_line_target.hour_to-att_line_target.hour_from)-period_deff
                    
                if att_line_target != att_line_target_1 and check_out_time > att_line_target.hour_from and check_in.day == check_out.day:
                    working_hours = (att_line_target_1.hour_to- att_line_target_1.hour_from)+(att_line_target.hour_to- att_line_target.hour_from)
                
                if check_in_time >= first_from_hour and check_out_time <= second_to_hour and check_out_time >= second_from_hour and check_in_time <= first_to_hour and check_out_time < second_to_hour and check_in.day == check_out.day:
                    in_duration = check_out_time-check_in_time
                    out_duration = period_deff
                elif check_in_time >= first_from_hour and  check_out_time <= second_from_hour and check_in_time <= first_to_hour and check_out_time >=first_to_hour and check_in.day == check_out.day:
                    in_duration = first_to_hour-check_in_time
                    out_duration = check_out_time-first_to_hour
                elif check_in_time >= first_from_hour and check_out_time <= first_to_hour  and check_in.day == check_out.day:
                    in_duration = working_hours-((check_in_time-first_from_hour)+(first_to_hour-check_out_time))
                    out_duration = 0.0
                elif check_in_time > first_from_hour and check_in_time >= second_from_hour and check_in_time < second_to_hour and check_out_time > second_to_hour and check_in.day == check_out.day and first_from_hour != second_from_hour:
                    in_duration = second_to_hour-check_in_time
                    out_duration = check_out_time-second_to_hour
                elif check_in_time <= first_from_hour and check_out_time < first_to_hour and att_line_target != att_line_target_1 and check_in.day == check_out.day: 
                    in_duration = working_hours-(first_to_hour-check_out_time)
                    out_duration = first_from_hour-check_in_time
                elif check_in_time > first_from_hour and check_in_time < second_from_hour and check_in_time >= first_to_hour and check_out_time >= second_to_hour and check_in.day == check_out.day:
                    in_duration = second_to_hour-second_from_hour
                    out_duration = (second_from_hour-check_in_time)+(check_out_time-second_to_hour)
                elif check_in_time >= second_to_hour and check_in.day == check_out.day:
                    in_duration = 0.0
                    out_duration = check_out_time-check_in_time
                elif check_in_time >= first_from_hour and check_out_time >= second_to_hour and check_in_time < first_to_hour and check_in.day == check_out.day:
                    in_duration = (second_to_hour-check_in_time)-period_deff
                    out_duration = period_deff+(check_out_time-second_to_hour)
                elif check_in_time <= first_from_hour and check_out_time >= first_to_hour and check_out_time <= second_from_hour:
                    in_duration = working_hours
                    out_duration = (first_from_hour-check_in_time)+(check_out_time-first_to_hour)
                elif check_in_time <= first_to_hour and check_in_time >= first_from_hour and check_out_time <= second_to_hour and check_out_time > second_from_hour and check_in.day == check_out.day:
                    in_duration = worked_hours-period_deff
                    out_duration = period_deff
                elif check_in_time >= first_to_hour and check_in_time > first_from_hour and check_out_time <= second_to_hour and check_out_time > second_from_hour:
                    in_duration = worked_hours-(second_from_hour-check_in_time)
                    out_duration = second_from_hour-check_in_time
                elif check_in_time < first_from_hour and check_out_time > second_to_hour:
                    in_duration = (second_to_hour-first_from_hour)-period_deff
                    out_duration = ((first_from_hour-check_in_time)+(check_out_time-second_to_hour))+period_deff
                elif check_in_time < first_from_hour and check_out_time >= second_from_hour and check_out_time <= second_to_hour:
                    in_duration = (check_out_time-first_from_hour)-period_deff
                    out_duration = (first_from_hour-check_in_time)+period_deff
                elif check_in_time >= first_to_hour and check_out_time <= second_from_hour:
                    in_duration = 0.0
                    out_duration = check_out_time-check_in_time
                
        if in_duration < 0 and in_duration > -1:
            in_duration = period_deff+in_duration
        elif in_duration < 0 and in_duration <= -1:
            in_duration = in_duration*-1
            
        if out_duration < 0:
            out_duration = out_duration*-1
        
        return [in_duration, out_duration, working_hours,period_deff]

    # @api.multi
    @api.depends('check_in', 'check_out')
    def _get_attendance_duration(self):
        for att in self:

            calendar = att.employee_id.resource_calendar_id
            max_hours = 0.0
            checkin_weekday = att.check_in.weekday()
            attendance_days = self.env['resource.calendar.attendance'].search([('dayofweek', '=', checkin_weekday), ('calendar_id', '=', att.employee_id.resource_calendar_id.id)])
            for day in attendance_days:
                hour_diff = day.hour_to - day.hour_from 
                max_hours += hour_diff
            
            max_hours = max_hours - calendar.break_duration
            if calendar and att.check_in and att.check_out and max_hours:
                max_late_minutes = calendar.max_late_minutes
                max_hours_per_day = max_hours
                timezone = self._context.get("tz","UTC") if self._context else "UTC"
                if not timezone:
                    timezone = "UTC"
                active_tz = pytz.timezone(timezone)
                check_out = att.check_out.replace(tzinfo=pytz.utc).astimezone(active_tz)
                check_in = att.check_in.replace(tzinfo=pytz.utc).astimezone(active_tz)
                all_duration = self.get_inside_calendar_duration(calendar, check_in, check_out, att)
                att.inside_calendar_duration = all_duration[0]
                att.outside_calendar_duration = all_duration[1]
                working_hours = all_duration[2]
                period_deff = all_duration[3]
                late_minutes = self.minutes_late(calendar, check_in, max_late_minutes,att)/60.0
                if late_minutes-period_deff <= working_hours:
                    att.late_minutes = late_minutes
                else:
                    att.late_minutes = 0.0
            else:
                att.outside_calendar_duration = att.worked_hours
                att.inside_calendar_duration = 0.0
                att.late_minutes = 0.0
    
    # @api.multi
    @api.depends('draft_zkteco_attendance.moved_to')
    def _find_linked_device_attendance(self):
        for att in self:
            att.zkteco_device_attendance = True if att.draft_zkteco_attendance else False                 
    
    outside_calendar_duration = fields.Float(compute='_get_attendance_duration', string="Duration (Out Work schedule)")
    inside_calendar_duration = fields.Float(compute='_get_attendance_duration', string="Duration (In Work schedule)")
    late_minutes = fields.Float(compute='_get_attendance_duration', string="Late Minutes")
    draft_zkteco_attendance = fields.One2many(comodel_name='hr.draft.attendance', inverse_name='moved_to', string='Draft Attendance Records')
    zkteco_device_attendance = fields.Boolean(string='Zkteco Device Attendance?', compute='_find_linked_device_attendance')
    # rules
    calendar_id = fields.Many2one('resource.calendar', 'Default Working Hours')
    calendar_line = fields.Many2one("resource.calendar.attendance")
    rule_type = fields.Selection([("emp", "Employee"), ("other", "Other")])
    attendance_rule_id = fields.Many2one("hr.attendance.rule")
    emp_attendance_rule_id = fields.Many2one("hr.attendance.rule.emp")

    # workday
    late_min = fields.Integer("Late Minutes", compute="compute_workday", store=True, readonly=True)
    early_min = fields.Integer("Early Minutes",  compute="compute_workday", store=True,  readonly=True)
    expected_work_hours = fields.Float("Expected Worked Hours", store=True, compute="compute_workday")
    normal_hours = fields.Float("Normal Hours",  compute="compute_workday", store=True, readonly=True)

    # penalties
    early_penalty_min = fields.Integer("Early Checkout Penalty", store=True, compute="compute_penalty")
    late_penalty_min = fields.Integer("Late CheckIn Penalty", store=True, compute="compute_penalty")

    # absent
    is_absent = fields.Boolean("Is Absent", compute="compute_workday", store=True, readonly=True)
    is_leave = fields.Boolean("Is on Leave", compute="compute_workday", store=True, readonly=True)

    # overtime
    ot_before_min = fields.Float("OT Before Minutes Actual", compute="compute_workday", store=True, readonly=True)
    ot_after_min = fields.Float("OT After Minutes", compute="compute_workday", store=True, readonly=True)
    granted_before_ot = fields.Integer("OT Before Minutes", compute="compute_granted_overtime", store=True, readonly=True)
    granted_after_ot = fields.Integer("OT After Minutes", compute="compute_granted_overtime", store=True, readonly=True)
    total_ot = fields.Integer("Total Overtime", compute="compute_granted_overtime", store=True, readonly=True)

    def calculate_rules(self, calendar_line):
        employee = self.employee_id
        self.calendar_line = calendar_line
        self.calendar_id = calendar_line.calendar_id
        emp_rule = self.env["hr.attendance.rule.emp"].search([("employee_id", "=", employee.id)])
        if emp_rule:
            self.rule_type = "emp"
            self.emp_attendance_rule_id = emp_rule
        else:
            attendance_rule = self.env["hr.attendance.rule"].search(
                ["|", ("work_schedule_id", "in", self.calendar_id.id), ("branch_id", "in", self.employee_id.branch_id.id)],
                                                                    limit=1)
            self.rule_type = "other"
            self.attendance_rule_id = attendance_rule

    def get_differance(self, day, expected_time, actual_datetime, sub_type):
        tz = 'Asia/Riyadh'
        expected_time = float_to_time(
            abs(expected_time) - 0.5 if expected_time < 0 else expected_time)
        # print("expected_time", expected_time)
        expected_datetime = timezone(tz).localize(datetime.combine(day, expected_time)).astimezone(
            UTC).replace(tzinfo=None)

        # new_actua_datetime = timezone(tz).localize(actual_datetime).astimezone(
        #     UTC).replace(tzinfo=None)
        delta = expected_datetime - actual_datetime if sub_type == "in" else actual_datetime - expected_datetime
        # print("expected_datetime", expected_datetime)
        # print("actual_datetime", actual_datetime)
        # print("new_actua_datetime", new_actua_datetime)
        # print("delta", delta)
        return (delta).total_seconds()/ 60

    def get_applied_rule(self):
        return self.emp_attendance_rule_id if self.rule_type == "emp" else self.attendance_rule_id

    def check_leave(self):
        tz = self.employee_id.tz
        expected_time = self.calendar_line.hour_from
        expected_time = float_to_time(
            abs(expected_time) - 0.5 if expected_time < 0 else expected_time)
        expected_datetime = timezone(tz).localize(datetime.combine(self.day, expected_time)).astimezone(
            UTC).replace(tzinfo=None)
        domain = [('employee_id', '=', self.employee_id.id), ("state", "=", "validate"),
                  ('date_from', '<=', expected_datetime), ('date_to', '>=', expected_datetime)]
        is_leave = self.env["hr.leave"].search(domain)
        return True if is_leave else False

    def get_is_absent(self, late_min, early_min):
        result = {"is_leave": False, "is_absent": False}
        is_leave = self.check_leave()
        rule = self.get_applied_rule()
        if is_leave: # on leave
            result.update({"is_leave": True})
        else: # not on leave
            if not (self.check_in or self.check_out): # both check in and out are misising
                result.update({"is_absent": True})
            rule = self.get_applied_rule()
            if not self.check_in and rule.no_checkin_options == "absent":
                result.update({"is_absent": True})
            if not self.check_out and rule.no_checkout_options == "absent":
                result.update({"is_absent": True})
            if rule.checkin_late_as_abs and late_min != 0 and (late_min > rule.checkin_late_as_abs):
                result.update({"is_absent": True})
            if rule.checkout_early_as_abs and early_min != 0 and (early_min > rule.checkout_early_as_abs):
                result.update({"is_absent": True})
        return result

    @api.depends('check_in', 'check_out', 'day',
                 'calendar_line.hour_from', 'calendar_line.hour_to', 'calendar_id.hours_per_day')
    def compute_workday(self):
        for rec in self:
            day = rec.day
            calendar_line = rec.calendar_line
            if day and calendar_line:
                if rec.check_in:

                    hour_from = calendar_line.hour_from
                    check_in_diff = rec.get_differance(day, hour_from, rec.check_in, "in")
                    rec.late_min = abs(check_in_diff) if check_in_diff < 0 else 0
                    # before_mins = rec.get_differance(day, hour_from, rec.check_in, "out")
                    rec.ot_before_min = check_in_diff if check_in_diff > 0 else 0
                    print("================check_in", rec.check_in)
                    print("================hour_from", hour_from)
                    print("================day", day)
                if rec.check_out:
                    hour_to = calendar_line.hour_to
                    check_out_diff = rec.get_differance(day, hour_to, rec.check_out, "out")
                    rec.early_min = abs(check_out_diff) if check_out_diff < 0 else 0
                    # after_mins = rec.get_differance(day, hour_to, rec.check_in, "in")
                    rec.ot_after_min = check_out_diff if check_out_diff > 0 else 0

                if rec.check_in and rec.check_out:
                    rec.expected_work_hours = calendar_line.calendar_id.hours_per_day
                    overtime_hours = rec.worked_hours - rec.expected_work_hours
                    rec.normal_hours = rec.worked_hours - overtime_hours
                    # rec.overtime_hours = overtime_hours if overtime_hours > 0 else 0

                result_dic = rec.get_is_absent(rec.late_min, rec.early_min)
                rec.is_absent = result_dic.get("is_absent")
                rec.is_leave = result_dic.get("is_leave")

    @api.depends('late_min', 'early_min', 'calendar_id', 'check_in', 'check_out',
                 'calendar_id.max_late_minutes', 'calendar_id.max_early_muintes')
    def compute_penalty(self):
        for rec in self:
            calendar = rec.calendar_id
            rule = rec.get_applied_rule()
            if calendar:
                if rec.late_min:
                    if rec.late_min <= calendar.max_late_minutes:
                        rec.late_penalty_min = 0
                    elif rec.permission_type == "signin" and rec.permission_id.state == 'validate':
                        rec.late_penalty_min = rec.late_min - rec.permission_duration
                    else:
                        rec.late_penalty_min = rec.late_min
                if rec.early_min:
                    if rec.early_min <= calendar.max_early_muintes:
                        rec.early_penalty_min = 0
                    elif rec.permission_type == "singout" and rec.permission_id.state == 'validate':
                        rec.early_penalty_min = rec.late_min - rec.permission_duration
                    else:
                        rec.early_penalty_min = rec.early_min
                if not rec.check_in and rule.no_checkin_options == 'late':
                    rec.late_penalty_min = rule.no_checkin_late_min
                if not rec.check_out and rule.no_checkout_options == 'late':
                    rec.early_penalty_min = rule.no_checkout_leave_min

    @api.depends('worked_hours', 'ot_before_min', 'ot_after_min')
    def compute_granted_overtime(self):
        for rec in self:
            rule = rec.get_applied_rule()
            ot_before_min = rec.ot_before_min
            ot_after_min = rec.ot_after_min
            if ot_before_min >= rule.min_before_ot and rule.is_allowed_before_ot:
                rec.granted_before_ot = int(ot_before_min) if ot_before_min <= rule.max_before_ot else rule.max_before_ot
            if ot_after_min >= rule.min_after_ot and rule.is_allowed_after_ot:
                rec.granted_after_ot = int(ot_after_min) if ot_after_min <= rule.max_after_ot else rule.max_after_ot
            rec.total_ot = rec.granted_before_ot + rec.granted_after_ot

    # @api.multi
    def unlink(self):
        for rec in self:
            linked_draft_moves = self.env["hr.draft.attendance"].search([("moved_to", "=", rec.id)])
            linked_draft_moves.write({"moved_to": False, "moved": False})
        return super(hr_attendance, self).unlink()





    
