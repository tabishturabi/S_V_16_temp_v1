# -*- coding: utf-8 -*-
import os

import pytz
import time
from datetime import datetime, timedelta
from pytz import timezone

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from lxml import etree
from odoo.osv.orm import setup_modifiers

import logging

_logger = logging.getLogger(__name__)


def un_upset_datetime(datetime_wo_tz, tzone):
    """"  takes naive datetime (datetime_wo_tz) and it's timezone (tzone)
        returns the datetime aware with timezone changed to UTC
    """
    aware_datetime = pytz.timezone(tzone).localize(datetime_wo_tz)
    aware_datetime_utc = aware_datetime.astimezone(pytz.UTC)
    return aware_datetime_utc


def upset_datetime(datetime_wo_tz, tzone):
    """"  takes naive datetime (datetime_wo_tz) and it's timezone (tzone)
            returns the datetime aware with timezone changed to UTC
        """
    localized_datetime = pytz.UTC.localize(fields.Datetime.from_string(datetime_wo_tz))
    datetime_with_tz = localized_datetime.astimezone(timezone(tzone))
    return datetime_with_tz


def convert_date_to_dayinweek(date):
    formatted_date = datetime.strptime(str(date), DEFAULT_SERVER_DATETIME_FORMAT)
    day_in_week = formatted_date.strftime("%A")
    return day_in_week


def get_time_from_float(float_hour):
    hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(float_hour * 60, 60))
    hour = hour.replace('.', ':0')
    return hour

#################################################################################################################


class InheritHrAttendance(models.Model):
    _name = 'hr.attendance'
    _inherit = 'hr.attendance'
    _inherit = ['hr.attendance', 'mail.thread']
    _order = "create_date desc"

    ATT_RECORD_STATE_SEL = [
        ('draft', 'Draft'),
        ('complete', 'Complete'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('reject', 'Rejected')]


    ATT_STATE_SEL = [
        ('complete', 'Duty Complete'),
        ('in_missing', 'Duty In Missing'),
        ('out_missing', 'Duty Out Missing'),
        ('in_out_missing', 'Duty In And Out Missing'),
        ('absent', 'Duty Absent'),
        ('off_duty_complete', 'Off Duty Complete'),
        ('off_duty_in_missing', 'Off Duty In Missing'),
        ('off_duty_out_missing', 'Off Duty Out Missing')]

    # no need for employee_id to be editable since no one should create attendance manually

    #@api.multi
    def name_get(self):
        result = []
        for attendance in self:
            if not attendance.check_in and not attendance.check_out:
                result.append((attendance.id, _("%(empl_name)s") % {
                    'empl_name': attendance.employee_id.name}))

            if not attendance.check_out and attendance.check_in:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance,
                                                                                            fields.Datetime.from_string(
                                                                                                attendance.check_in))),
                }))

            if attendance.check_out and not attendance.check_in:
                result.append((attendance.id, _("%(empl_name)s from %(check_out)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_out': fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance,
                                                                                             fields.Datetime.from_string(
                                                                                                 attendance.check_out))),
                }))
            if attendance.check_out and attendance.check_in:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s to %(check_out)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance,
                                                                                            fields.Datetime.from_string(
                                                                                                attendance.check_in))),
                    'check_out': fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance,
                                                                                             fields.Datetime.from_string(
                                                                                                 attendance.check_out))),
                }))
        return result

    name = fields.Char(string="No.", readonly=True)

    check_in = fields.Datetime(string="Check In", required=False,
                               track_visibility="onchange")
    check_out = fields.Datetime(string="Check Out", required=False, track_visibility="onchange")

    expected_check_in = fields.Datetime(string="Expected Check In")
    expected_check_out = fields.Datetime(string="Expected Check In")

    expected_check_in_min = fields.Datetime(string="Expected Check In")
    expected_check_in_max = fields.Datetime(string="Expected Check In Max")

    expected_check_out_min = fields.Datetime(string="Expected Check Out")
    expected_check_out_max = fields.Datetime(string="Expected Check Out Max")

    expected_work_hours = fields.Float(string="Expected Worked Hours")

    over_time = fields.Float(string='Over Time', store=True, readonly=True)
    under_time = fields.Float(string='Under Time', store=True, readonly=True)
    over_time_off = fields.Float(string='Over Time Duty Off', store=True, readonly=True)
    log_ids = fields.One2many('hr.attendance.log', 'attend_id')

    is_complete = fields.Boolean(string="Check-in and check-out", default=False)
    is_passed = fields.Boolean(string="Time for this record has passed", default=False, index=True)
    state_attendance = fields.Selection(ATT_STATE_SEL, string="Attendance State", track_visibility='onchange', copy=False)

    is_off_duty_overtime = fields.Boolean(string="Off duty Overtime", default=False, index=True)

    is_absent = fields.Boolean(default=False)
    abs_reason = fields.Text(string='Absent Reason')
    append_in_sheet = fields.Boolean(default=False)
    sheet_id = fields.Many2one('hr.attendance.sheet', string='Attendance Sheet', readonly=True)
    state = fields.Selection(ATT_RECORD_STATE_SEL, default='draft', track_visibility='onchange', copy=False)

    is_manual_modify = fields.Boolean(string="Manually Modified", default=False)

    #####################################################
    #  create regular attendance                        #
    #####################################################

    def on_holiday(self, employee, day):
        employee_leaves = self.env['hr.holidays'].search([
            ('employee_id', '=', employee.id), ('date_from', '<=', str(day)),
            ('state', '=', 'validate'), ('type', '=', 'remove')])
        returned_leaves = employee_leaves.filtered(lambda r: r.return_date and r.return_date >= str(day))
        non_returned_leaves = employee_leaves.filtered(lambda r: not r.return_date and r.date_to >= str(day))

        if returned_leaves or non_returned_leaves:
            return True
        else:
            return False

    def get_check_in_out_min_max(self, type, work_schedule, span_days, today, work_line=False):
        if type == "bywork":
            early_check_in = work_schedule.early_checked_in
            late_check_in = work_schedule.late_checked_in
            early_check_out = work_schedule.early_checked_out
            late_check_out = work_schedule.late_checked_out
            hours_from = get_time_from_float(work_line.hour_from)
            hours_to = get_time_from_float(work_line.hour_to)

        start_datetime = datetime.strptime(
            "%s %s:00" % (str(today.date()), str(hours_from).replace('.', ':0')), DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = start_datetime.date() + timedelta(days=span_days)
        end_datetime = datetime.strptime(
            "%s %s:00" % (str(end_date), str(hours_to).replace('.', ':0')), DEFAULT_SERVER_DATETIME_FORMAT)
        f = os.popen("cat /etc/timezone")
        now = f.read()
        tz = pytz.timezone(str(now[:-1]))
        tzone = str(tz)
        start_datetime = un_upset_datetime(start_datetime, tzone)
        end_datetime = un_upset_datetime(end_datetime, tzone)
        expected_check_in_min = start_datetime - timedelta(minutes=early_check_in)
        expected_check_in_max = start_datetime + timedelta(minutes=late_check_in)
        expected_check_out_min = end_datetime - timedelta(minutes=early_check_out)
        expected_check_out_max = end_datetime + timedelta(minutes=late_check_out)
        return start_datetime, end_datetime, expected_check_in_min, expected_check_in_max, expected_check_out_min, expected_check_out_max


    def create_attendance_by_work(self, starting_check_date, employee):
        """ create attendance records with expected check-in and check-out for employees who have a work schedule """
        contract = employee.contract_id
        attendance_obj = self.env["hr.attendance"]
        work_schedule = employee.contract_id.working_hours
        work_schedule_lines = work_schedule.attendance_ids
        today = datetime.now(pytz.timezone("UTC")).replace(second=0, microsecond=0)   # check_in day
        check_date = starting_check_date
        while check_date.date() <= today.date():
            if not self.on_holiday(employee, check_date):
                check_day_in_weekdays = convert_date_to_dayinweek(str(check_date))
                for work_line in work_schedule_lines:
                    span_days = work_line.span_days
                    if span_days >= 0:
                        selection_day_of_week = dict(
                            contract.working_hours.attendance_ids.fields_get(allfields=['dayofweek'])['dayofweek']['selection'])[work_line.dayofweek]

                        if check_day_in_weekdays == selection_day_of_week and work_line.is_work:

                            mins_maxs = self.get_check_in_out_min_max("bywork", work_schedule, span_days, check_date, work_line)
                            expected_check_in = mins_maxs[0]
                            expected_check_out = mins_maxs[1]
                            expected_check_in_min = mins_maxs[2]
                            expected_check_in_max = mins_maxs[3]
                            expected_check_out_min = mins_maxs[4]
                            expected_check_out_max = mins_maxs[5]


                            attendance_vals = {
                                'employee_id': employee.id,
                                'expected_check_in': expected_check_in,
                                'expected_check_out': expected_check_out,
                                'expected_check_in_min': expected_check_in_min,
                                'expected_check_in_max': expected_check_in_max,
                                'expected_check_out_min': expected_check_out_min,
                                'expected_check_out_max': expected_check_out_max,
                                'expected_work_hours': work_line.worked_hours,
                            }
                            attendance_obj.create(attendance_vals)
            check_date += timedelta(days=1)

    @api.model
    def create_attendance(self, next_execution_date):
        """ create attendants records for all employees with contracts """
        employees = self.env["hr.employee"].search([('contract_id', '!=', False)])
        req_attend_employees = employees.filtered(lambda r: not r.contract_id.is_not_required_attendance)

        for employee in req_attend_employees:
            contract = employee.contract_id
            # first we create attendance records with expected check_in values and expected check_out values
            if contract.working_hours:
                self.create_attendance_by_work(next_execution_date, employee)
        return req_attend_employees

    #####################################################
    #  create overtime off duty attendance              #
    #####################################################

    def get_log_slot(self, working_type, employee, log):
        log_date = datetime.strptime(log.time, DEFAULT_SERVER_DATETIME_FORMAT)
        attendances = self.env["hr.attendance"].search(
            [('employee_id', '=', employee.id),
             ('expected_check_out_max', '<', log.time), ('expected_check_in_min', '>', log.time)])

        attendances_before_log = attendances.filtered(lambda r: r.expected_check_out_max < log.time)
        attendances_after_log = attendances.filtered(lambda r: r.expected_check_out_max > log.time)

        # getting beginning of slot
        if attendances_before_log:
            slot_begin = max(attendances_before_log.mapped("expected_check_out_max"))
            expected_start_date = datetime.strptime(slot_begin, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(seconds=30)
        else:
            expected_start_date = log_date

        # getting end of slot
        if attendances_after_log:
            # if there are attendance records after log then just take 30 seconds
            # before the first one as the end of slot
            slot_end = min(attendances_after_log.mapped("expected_check_in_min"))
            expected_end_date = datetime.strptime(slot_end, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(seconds=-30)
        else:
            expected_end_date = False
            log_date = datetime.strptime(log.time, DEFAULT_SERVER_DATETIME_FORMAT)

            if working_type == "bywork":
                work_schedule = employee.contract_id.working_hours
                work_schedule_lines = work_schedule.attendance_ids.filtered(lambda r: r.span_days >= 0 and r.is_work)
                if work_schedule_lines:
                    check_date = expected_start_date
                    halt_loop_date = check_date + timedelta(days=14)

                    while check_date.date() <= halt_loop_date.date():
                        check_day_in_weekdays = convert_date_to_dayinweek(str(check_date.replace(microsecond=0)))
                        for work_line in work_schedule_lines:
                            selection_day_of_week = dict(
                                work_schedule_lines.fields_get(allfields=['dayofweek'])['dayofweek'][
                                    'selection'])[work_line.dayofweek]
                            if check_day_in_weekdays == selection_day_of_week:
                                ######################
                                # first: get the from hour
                                # -delta the grace period
                                # -delta the timezone
                                time_zone = time.timezone / 3600.0
                                hour_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_line.hour_from * 60, 60))
                                min_check_in_minutes = work_line.calendar_id.early_checked_in

                                f = os.popen("cat /etc/timezone")
                                now = f.read()
                                tz = pytz.timezone(str(now[:-1]))
                                tzone = str(tz)

                                check_date_date = str(check_date)[:10]
                                expected_end_date_string = "%s %s:00" % (check_date_date, str(hour_from))
                                expected_end_date_string = expected_end_date_string.replace('.', ':0')
                                expected_end_date = datetime.strptime(
                                    expected_end_date_string, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(minutes=-min_check_in_minutes)
                                expected_end_date = un_upset_datetime(expected_end_date, tzone)
                                break
                        if expected_end_date:
                            break
                        check_date += timedelta(days=1)


        expected_start_date = expected_start_date and expected_start_date.replace(microsecond=0) or datetime.today().replace(microsecond=0)
        expected_end_date = expected_end_date and expected_end_date.replace(microsecond=0)
        return expected_start_date, expected_end_date

    def create_off_duty_overtime_attendance(self):
        """" create attendance records for off duty log """
        floating_logs = self.env['hr.attendance.log'].search([('flag', '=', False)], order="id ASC")
        employees = floating_logs.mapped("employee_id")
        for employee in employees:
            employee_logs = floating_logs.filtered(lambda r: r.employee_id == employee)
            work_schedule_type = employee.contract_id.type_attendance
            employee_attendance_recs = self.env["hr.attendance"]

            for log in employee_logs:
                expected_start_date, expected_end_date = self.get_log_slot(work_schedule_type, employee, log)
                if expected_start_date and expected_end_date:
                    log_time = log.time
                    existing_overtime_record = self.env["hr.attendance"].search(
                         [('is_off_duty_overtime', '=', True),
                          ('expected_check_in_min', '<=', str(log_time)),
                          ('expected_check_out_max', '>=', str(log_time)),
                          ])
                    if existing_overtime_record:
                        if existing_overtime_record not in employee_attendance_recs:
                            employee_attendance_recs += existing_overtime_record
                    else:
                        vals = {
                                'employee_id': employee.id,
                                'is_off_duty_overtime': True,
                                'expected_check_in_min': expected_start_date,
                                'expected_check_in_max': expected_start_date,
                                'expected_check_out_min': expected_end_date,
                                'expected_check_out_max': expected_end_date,

                        }
                        rec = employee_attendance_recs.create(vals)
                        employee_attendance_recs += rec
            employee_attendance_recs._insert_logs(employee_logs, employee_attendance_recs)

    #####################################################
    #  link logs to attendance record                   #
    #####################################################

    def _insert_logs(self, employee_logs, employee_attendance_records):
        for log in employee_logs:
            time = log.time
            attendance_record = employee_attendance_records.filtered(
                lambda r: r.expected_check_in_min <= time and
                          r.expected_check_out_max >= time
            )
            if attendance_record:
                attendance_record.log_ids += log
                log.write({'flag': True})

    def insert_attendance_logs(self, employees, next_execution_date):
        last_execution_date = next_execution_date + timedelta(days=-1)
        all_log_attendance = self.env['hr.attendance.log'].search(
            [('flag', '=', False), ('time', '>=', str(last_execution_date))], order="id ASC")
        all_attendance_records = self.env['hr.attendance'].search(
            [('is_passed', '=', False), ('is_off_duty_overtime', '=', False)],
            order="id ASC")
        for employee in employees:
            employee_attendance_logs = all_log_attendance.filtered(lambda r: r.employee_id == employee)
            employee_attendance_records = all_attendance_records.filtered(lambda r: r.employee_id == employee)

            # insert logs into appropriate attendance records (not off duty)
            self._insert_logs(employee_attendance_logs, employee_attendance_records)
        return all_attendance_records

    #####################################################
    #  compute regular attendance                       #
    #####################################################

    def send_absent_list_email(self, attendances):
        absent_employees = attendances.filtered(lambda r: r.is_absent)
        absent_employees_dict = {}
        for rec in absent_employees:
            employee = rec.employee_id
            date = rec.expected_check_in and str(datetime.strptime(rec.expected_check_in, DEFAULT_SERVER_DATETIME_FORMAT).date())
            company_id = employee.company_id.id
            if not absent_employees_dict.get(company_id):
                absent_employees_dict.update({company_id: [(employee, date)]})
            else:
                (absent_employees_dict[company_id]).append((employee, date))

        # send an email with a list of all absent employees in a company
        hr_manager_group = ['hr_attendance.group_hr_attendance_manager']
        for company, employees in absent_employees_dict.iteritems():
            s = "<br/>"
            emp_names = list(map((lambda x: str(x[0].name) + " on Date:" + str(x[1])), employees))
            body = "List of absent employees<br/>" + s.join(emp_names)
            thread = self.env['mail.thread']
            try:
                thread.message_post_by_company(company, hr_manager_group, body=body)
            except:
                pass

    def get_absent(self, values):
        """ updates values with: is_absent """
        if not self.log_ids:
            values.update({
                'is_absent': True,
                'state_attendance': "absent",
                'is_complete': True,
                'state': 'validate',
            })
            self.send_absent_employee_email(values)

        return values

    def get_hours(self, values):
        expected_hours = self.expected_work_hours
        check_in = values.get('check_in')
        check_out = values.get('check_out')
        delta = datetime.strptime(check_out, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(
                    check_in, DEFAULT_SERVER_DATETIME_FORMAT)
        actual_hours = delta.total_seconds() / 3600.0

        diff = actual_hours - expected_hours
        if not self.is_off_duty_overtime:
            if diff >= 0:
                values.update({'over_time': diff})
            else:
                values.update({'under_time': diff})
        else:
            if check_in and check_out:
                values.update({'over_time_off': actual_hours})
        return values

    def send_absent_employee_email(self, values):
        employee = self.employee_id
        employee_partner = employee.user_id.partner_id.id
        state_attendance = values.get('state_attendance')
        record_date = datetime.strptime(self.expected_check_in, DEFAULT_SERVER_DATETIME_FORMAT).date()
        if state_attendance == "absent":
            body = "You were absent from your %s working day <br/> Please Justify" % str(record_date)
        message = employee_partner and self.message_post(body=body, partner_ids=[employee_partner])

    def send_missing_check_in_out_email(self, values):
        employee = self.employee_id
        employee_partner = employee.user_id.partner_id.id
        state_attendance = values.get('state_attendance')
        record_date = datetime.strptime(self.expected_check_in, DEFAULT_SERVER_DATETIME_FORMAT).date()
        if state_attendance != "absent":
            body = "You have an attendance record with %s , on date %s <br/> Please Justify!" %(state_attendance, str(record_date))
        message = employee_partner and self.message_post(body=body, partner_ids=[employee_partner])

    def get_state(self, values):

        check_in = values.get('check_in')
        check_out = values.get('check_out')

        if check_in and not check_out:
            values.update({'state_attendance': "out_missing"})
        elif not check_in and check_out:
            values.update({'state_attendance': "in_missing"})
        elif not check_in and not check_out:
            values.update({'state_attendance': "in_out_missing"})
        self.send_missing_check_in_out_email(values)

        return values

    def get_check_in_and_check_out_times(self, attendance_logs):
        expected_check_in_min = self.expected_check_in_min
        expected_check_in_max = self.expected_check_in_max
        expected_check_out_min = self.expected_check_out_min
        expected_check_out_max = self.expected_check_out_max
        if not self.is_off_duty_overtime:
            check_in_list = attendance_logs.filtered(lambda r: r.time >= str(expected_check_in_min) and
                                                               r.time <= str(expected_check_in_max)).mapped("time")
            check_out_list = attendance_logs.filtered(lambda r: r.time >= str(expected_check_out_min) and
                                                                r.time <= str(expected_check_out_max)).mapped("time")
            check_in = check_in_list != [] and min(check_in_list)
            check_out = check_out_list != [] and min(check_out_list)
        else:
            times_list = attendance_logs.sorted(key=lambda r: r.time).mapped("time")
            if times_list != []:
                check_in = min(times_list)
                check_out = max(times_list)

        return check_in, check_out

    def get_check_in_and_check_out(self):
        """ returns dictionary that may contain: check_in, check_out
            is_complete, is_passed
            if check_in and check
         """
        values = {}
        attendance_logs = self.log_ids
        if not self.is_off_duty_overtime:
            check_in, check_out = self.get_check_in_and_check_out_times(attendance_logs)
            values.update({
                'check_in': check_in,
                'check_out': check_out,
            })
            if check_in and check_out:
                    values.update({'is_complete': True,
                                   'state': 'validate',
                                   'state_attendance': 'complete'})
        else:
            if len(attendance_logs) == 1:
                check_in = attendance_logs.time
                values.update({
                    'check_in': check_in})
            if len(attendance_logs) > 1:
                check_in, check_out = self.get_check_in_and_check_out_times(attendance_logs)
                values.update({
                    'check_in': check_in,
                    'check_out': check_out,
                })

        now = datetime.now(pytz.timezone("UTC")).replace(second=0, microsecond=0)
        expected_check_out_max = self.expected_check_out_max
        if str(now) > expected_check_out_max:
            values.update({'is_passed': True})
        return values

    #@api.multi
    def compute_attendance(self, all_attendance):

        absent_attendances = self.env["hr.attendance"]
        for attendance in all_attendance:
            # first get check in and check out
            values = attendance.get_check_in_and_check_out()
            # change state (using is history or not to get  )
            is_passed = values.get('is_passed')
            is_complete = values.get('is_complete')
            if is_passed:
                # state is only determined after the time has passed and no more logs can be added
                # or determine is_absent when no more records can be added
                values = attendance.get_absent(values)
                absent = values.get('is_absent')
                if absent:
                    absent_attendances += attendance
                else:
                    values = attendance.get_state(values)
                if is_complete and not absent:
                    # record has both check-in and check-out and now we can calculate the working hours
                    values = attendance.get_hours(values)
            attendance.write(values)

        self.send_absent_list_email(absent_attendances)

    #####################################################
    #  compute overtime off duty attendance             #
    #####################################################

    def compute_over_time_off_duty(self):
        all_off_duty_attendance_records = self.search([
            ('is_off_duty_overtime', '=', True), ('is_passed', '=', False)])
        for attendance in all_off_duty_attendance_records:
            values = attendance.get_check_in_and_check_out()
            if values.get("is_passed"):
                # only determine state when time has passed
                if not values.get("check_out"):
                    values.update({"state_attendance": "off_duty_out_missing"})
                elif values.get("check_in") and values.get("check_out"):
                    values = attendance.get_hours(values)
                    values.update({"state_attendance": "off_duty_complete"})
                    values.update({"is_complete": True})
                    values.update({"state": 'validate'})
            attendance.update(values)

    # ORM functions

    @api.model
    def create(self, vals):
        """" add attendance sequence  """
        if not vals.get('name'):
            sequence_no = self.env['ir.sequence'].with_context(force_company=vals.get('company_id'),
                                                               force_create=True).next_by_code('hr.attendance')
            vals['name'] = sequence_no or 'New'
        return super(InheritHrAttendance, self).create(vals)

    #@api.multi
    def unlink(self):
        """ prevent unlinking in some states  """
        for attendance in self:
            if attendance.state in ['complete', 'confirm', 'validate']:
                raise UserError(_("You Cannot Delete Attendance Record in State %s.") % attendance.state)
        super(InheritHrAttendance, self).unlink()

    # workflow functions

    #@api.multi
    def action_compute_hours(self):
        """ manually compute hours  """
        for rec in self:
            if not rec.employee_id.contract_id:
                raise UserError(_("This Employee Doesn't have contract"))
            check_in = rec.check_in
            check_out = rec.check_out
            if not check_in or not check_out:
                raise UserError(_("Missing Check In or Check Out"))
            else:
                vals = {
                    'is_complete': True,
                }
                # set state
                if not self.is_off_duty_overtime:
                    vals.update({'state_attendance': 'complete'})
                else:
                    vals.update({'state_attendance': 'off_duty_complete'})

                vals.update(rec.get_hours({
                    'check_in': check_in,
                    'check_out': check_out
                }))
                rec.update(vals)

    #@api.multi
    def action_complete(self):
        """ confirm completion of check_in and check_out and compute working hours """
        for rec in self:
            if not rec.check_in or not rec.check_out:
                raise UserError(_("Missing Check In or Check Out"))
            rec.state = 'complete'
            rec.action_compute_hours()

    #@api.multi
    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    #@api.multi
    def action_validate(self):
        for rec in self:
            # condition added for when server action calls function
            if rec.state == 'confirm':
                rec.state = 'validate'

    #@api.multi
    def action_reject(self):
        for rec in self:
            rec.state = 'reject'

    #@api.multi
    def action_reset_draft(self):
        for rec in self:
            if rec.state == 'reject':
                rec.state = 'draft'

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = datetime.strptime(attendance.check_out, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(
                    attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                attendance.worked_hours = delta.total_seconds() / 3600.0

    # constraint functions
    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ verifies if check_in is earlier than check_out. """

    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        pass
        # checkin = self.check_in
        # checkout = self.check_out
        # if checkin and checkout:
        #     if checkin > checkout:
        #         raise UserError(_("Check In can't be greater than Check Out"))
        # min_in = self.expected_check_in_min
        # max_out = self.expected_check_out_max
        # if min_in and max_out:
        #     if (checkin > max_out or checkin < min_in) or checkout < min_in or checkout > max_out:
        #         raise UserError(_("Check In or Check Out Time Error"))

    # ################################## #

    # cron function

    @api.model
    def call_attendance_daily_functions(self):
        _logger.info('******** Starting attendance scheduler ********')

        machine_obj = self.env['biometric.machine']

        machine_obj.download_attendance()
        next_execution_date = datetime.strptime(self.env.ref("hr_attendance_extender.attendance_scheduler").nextcall,
                                                DEFAULT_SERVER_DATETIME_FORMAT)
        employees = self.create_attendance(next_execution_date)
        attendances = self.insert_attendance_logs(employees, next_execution_date)
        self.compute_attendance(attendances)

        # handle floating records
        # which are off duty overtime
        try:
            # create off duty overtime records
            self.create_off_duty_overtime_attendance()
            # compute overtime work hours and state
            self.compute_over_time_off_duty()
        except:
            pass



