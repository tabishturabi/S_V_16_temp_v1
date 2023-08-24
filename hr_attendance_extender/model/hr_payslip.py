# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PayslipAttendSheetLines(models.Model):
    _name = "payslip.attend.sheet.line"

    attendance_sheet_id = fields.Many2one('hr.attendance.sheet', string='Sheet')
    state = fields.Selection(related="attendance_sheet_id.state", string="State")
    over_time = fields.Float(string="Over Time", related="attendance_sheet_id.over_time")
    under_time = fields.Float(string="Under Time", related="attendance_sheet_id.under_time")
    over_time_off = fields.Float(string="Over Time in Off Day", related="attendance_sheet_id.over_time_off")
    absent_days = fields.Integer(string="Absent Days", related="attendance_sheet_id.absent_days")
    payslip_id = fields.Many2one("hr.payslip", string="Payslip")

###################################################################################################


class InheritHrPayslip(models.Model):
    _inherit = "hr.payslip"

    attendance_lines = fields.One2many(comodel_name='payslip.attend.sheet.line', inverse_name="payslip_id",
                                       string="Attendants Sheet",
                                       help='Latest attendance sheet of the employee',
                                       compute='_compute_attendance_sheet', store=True)

    over_time = fields.Float(string="Total Over Time", compute='_compute_attendance_sheet')
    under_time = fields.Float(string="Total Under Time", compute='_compute_attendance_sheet')
    over_time_off = fields.Float(string="Total Over Time in Off Day", compute='_compute_attendance_sheet')
    absent_days = fields.Integer(string="Absent Days", compute='_compute_attendance_sheet')

    #@api.multi
    @api.depends('employee_id')
    def _compute_attendance_sheet(self):
        """" get all attendances sheets not in a previous payslip """
        sheet_obj = self.env['hr.attendance.sheet']
        for payslip in self:
            attend_sheets = sheet_obj.search([
                ('employee_id', '=', payslip.employee_id.id), ('state', 'in', ['validate'])])
            attendance_lines = []
            for sheet in attend_sheets:
                vals = {'attendance_sheet_id': sheet.id,
                        }
                attendance_lines.append(vals)
            payslip.attendance_lines = attendance_lines
            over_time = under_time = over_time_off = absent_days = 0
            for line in payslip.attendance_lines:
                over_time += line.over_time
                under_time += line.under_time
                over_time_off += line.over_time_off
                absent_days += line.absent_days
            payslip.over_time = over_time
            payslip.under_time = under_time
            payslip.over_time_off = over_time_off
            payslip.absent_days = absent_days

    #@api.multi
    def process_sheet(self):
        for payslip in self:
            for sheet in payslip.attendance_lines:
                sheet.state = 'done'
                sheet.payslip_id = payslip
        return super(InheritHrPayslip, self).process_sheet()

