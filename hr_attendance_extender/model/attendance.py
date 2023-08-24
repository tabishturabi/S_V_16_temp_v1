# -*- coding: utf-8 -*-
import time
import pytz
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil import relativedelta as re


class HrAttendanceLog(models.Model):
    _name = 'hr.attendance.log'
    _order = "time desc"

    #@api.multi
    def name_get(self):
        result = []
        for att in self:
            fullname = ''
            name = att.employee_id
            name_mec = att.machine_user
            code = att.employee_code
            if name:
                fullname = '[' + str(name.name) + ']'
            if not name and name_mec:
                fullname += '[' + str(name_mec) + ']'
            if code:
                fullname += '[' + str(code) + ']'
            result.append((att.id, fullname))
        return result

    #@api.multi
    @api.onchange('machine_id')
    def onchange_machine_id(self):
        """ timezone according to the machine """
        machine = self.machine_id
        if machine:
            self.time_zone = machine.time_zone

    @api.model
    def _tz_get(self):
        """ returns selection of all timezones in pytz lib """
        return [(x, x) for x in pytz.all_timezones]

    machine_user = fields.Char(string='Employee Machine Name')
    employee_id = fields.Many2one('hr.employee', string="Employee", ondelete='restrict', index=True)
    employee_code = fields.Char(string='Employee Code', related="employee_id.employee_code")
    machine_id = fields.Many2one('biometric.machine', string='Machine No', required=True)
    time = fields.Datetime(string="Time", required=True)
    flag = fields.Boolean(string="Linked", default=False, index=True)
    add_by_cron = fields.Boolean(string="Automatic Generation", default=False)
    time_zone = fields.Selection('_tz_get', string='Timezone', required=True)
    attend_id = fields.Many2one('hr.attendance', string='Attendance Link')

    #@api.multi
    def unlink(self):
        """ prevent deleting  """
        for log in self:
            if log:
                raise UserError(_("You Cannot Delete Attendance Log."))
        super(HrAttendanceLog, self).unlink()

###################################################################

##################################################################


#############################################################################


#########################################################################


class AttendanceSheet(models.Model):
    _name = 'hr.attendance.sheet'
    _inherit = ['mail.thread']

    SHEET_SEL = [
        ('draft', 'Draft'),
        ('validate', 'Validated'),
        ('w_payslip', 'Waiting Processing'),  # for future use, in case of sheet can be excluded from payroll,
        # currently not handled
        ('done', 'Done'),
        ('reject', 'Rejected')]

    #@api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = rec.employee_id.name
            number = rec.number
            if name:
                name = name
            if number:
                name += '[' + str(number) + ']'
            result.append((rec.id, name))
        return result

    state = fields.Selection(SHEET_SEL, default='draft', copy=False, track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string='Employee Name',
                                  readonly=True, states={'draft': [('readonly', False)]})
    employee_code = fields.Char(string="Employee Code", related="employee_id.employee_code", store=True, readonly=True)

    date_from = fields.Date(string='Date From', default=time.strftime('%Y-%m-01'),
                            readonly=True, states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='Date To',
                          default=str(datetime.now() + re.relativedelta(months=+1, day=1, days=-1))[:10],
                          readonly=True, states={'draft': [('readonly', False)]})
    note = fields.Text(string='Note')
    number = fields.Char(string='Reference', readonly=True, copy=False,
                         states={'draft': [('readonly', False)]})
    attendance_lines = fields.One2many('hr.attendance', 'sheet_id',
                                      readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Company', default=lambda x: x.env.user.company_id.id,
                                 readonly=True, states={'draft': [('readonly', False)]})
    over_time = fields.Float(string='Over Time', readonly=True)
    under_time = fields.Float(string='Under Time', readonly=True)
    over_time_off = fields.Float(string='Over Time Duty Off', readonly=True)
    worked_hours = fields.Float(string='Total Work Hours', readonly=True)
    absent_days = fields.Integer(string='Total Absent Days', readonly=True)
    is_compute = fields.Boolean(string="Sheet Computed", default=False)
    payslip_id = fields.Many2one("hr.payslip", string="Sheet Payslip")

    #@api.multi
    def action_validate(self):
        """ validate computed sheets """
        for rec in self:
            if rec.is_compute:
                rec.state = 'validate'
            else:
                raise UserError(_('You need to compute the attendance sheet before validating it!'))

    #@api.multi
    def action_done_sheet(self):
        """ set sheet to done """
        for rec in self:
                rec.state = 'done'

    #@api.multi
    def action_waiting_payslip(self):
        for rec in self:
            if rec.state == "validate":
                rec.state = "w_payslip"
            else: raise UserError(_("Sheet needs to be validated before "))

    #@api.multi
    def action_reject(self):
        """" reject sheet """
        for rec in self:
            rec.state = 'reject'

    #@api.multi
    def action_reset_draft(self):
        """" Set sheet to Draft """
        for rec in self:
            if rec.state == 'reject':
                rec.state = 'draft'

    #@api.multi
    def action_compute_sheet(self):
        """" set values for: worked_hours, overtime, undertime, overtime_off, and absent days """
        for sheet in self:
            number = sheet.number or self.env['ir.sequence'].with_context(force_company=sheet.company_id.id,
                                                               force_create=True).next_by_code('attendance.sheet')
            if sheet.attendance_lines:
                balance = [(x.worked_hours,x.over_time,x.under_time,x.over_time_off,x.write({'append_in_sheet':True})) for x in self.attendance_lines]
                over_time = sum(o[1] for o in balance) or 0.00
                under_time = sum(u[2] for u in balance) or 0.00
                if over_time > abs(under_time):
                    sheet.over_time = over_time - abs(under_time)
                    sheet.under_time = 0.00
                elif over_time < abs(under_time):
                    sheet.under_time = abs(under_time) - over_time
                    sheet.over_time = 0.00
                elif over_time == abs(under_time):
                    sheet.under_time = 0.00
                    sheet.over_time = 0.00
                sheet.worked_hours = sum(w[0] for w in balance) or 0.00
                sheet.over_time_off = sum(of[3] for of in balance) or 0.00
                sheet.write({'is_compute': True, 'number': number})
                # absent days
                absent_days = len(sheet.attendance_lines.filtered(lambda r: r.is_absent))
                sheet.absent_days = absent_days
            else:
                raise UserError(_("Can't compute sheet without attendance lines"))
        return True

