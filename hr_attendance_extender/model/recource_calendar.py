# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil import relativedelta as re


class InheritResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    sms_time_delay = fields.Integer(string='Message Time Delay',required=True,default=120)
    early_checked_in = fields.Integer(string='Early Check In',required=True,default=120)
    late_checked_in = fields.Integer(string='Late Check In',required=True,default=120)
    early_checked_out = fields.Integer(string='Early Check Out', required=True, default=120)
    late_checked_out = fields.Integer(string='Late Check Out', required=True, default=120)

    @api.constrains('early_checked_in', 'late_checked_in', 'early_checked_out','late_checked_out','sms_time_delay')
    def _check_time_period(self):
        for check in self:
            if check.sms_time_delay < 0 \
                    or check.early_checked_in < 0 or check.late_checked_in < 0 \
                    or check.early_checked_out < 0 or check.late_checked_out < 0:
                raise ValidationError(_('Please enter a positive value.'))


#################################################################################################################


class InheritResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    date_from = fields.Date(string='Starting Date',default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='End Date',default=str(datetime.now() + re.relativedelta(month=1, day=1, days=-1))[:10])
    hour_from = fields.Float(string='Work from', required=True, index=True, help="Start and End time of working.",default=08.5)
    hour_to = fields.Float(string='Work to', required=True,default=16.5)
    span_days = fields.Integer(string='Span to Next Day', default=0)
    is_work = fields.Boolean(string='Is Work',defualt=True)
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)

    @api.depends('hour_from', 'hour_to', 'span_days')
    def _compute_worked_hours(self):
        for attendance in self:
            date_from = datetime.today().date()
            if attendance.hour_to is not False and attendance.hour_from is not False and attendance.span_days != -1:
                hour_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(attendance.hour_from * 60, 60))
                hour_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(attendance.hour_to * 60, 60))

                date_to = (
                datetime.strptime(str(date_from), fields.DATE_FORMAT) + timedelta(days=attendance.span_days)).date()
                dtime_from = "%s %s:00" % (date_from, str(hour_from).replace('.', ':0'))
                dtime_to = "%s %s:00" % (date_to, str(hour_to).replace('.', ':0'))
                # get the difference between two dates
                delta = datetime.strptime(dtime_to, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(
                    dtime_from, DEFAULT_SERVER_DATETIME_FORMAT)
                attendance.worked_hours = abs(delta.total_seconds() / 3600.0)

    _sql_constraints = [
        ('unique_dayofweek', 'UNIQUE(dayofweek,calendar_id)', _('The Day of Week is already Exist '))
    ]

