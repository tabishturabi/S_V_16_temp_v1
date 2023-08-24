# -*- coding: utf-8 -*-
import time

from odoo import models, fields, api, _


class AttendanceReportWizard(models.TransientModel):
    _name = 'attendance.report.wizard'
    _description = 'Attendance Report Wizard'

    TYPE_SEL = [
        ('complete', 'Complete'),
        ('absent', 'Absent'),
        ('off_duty', 'Off Duty'),
        ('missing', 'Missing'),
        ('all', 'All Types'),
    ]

    MISSING_SEL = [
        ('in_missing', 'In Missing'),
        ('out_missing', 'Out Missing'),
        ('in_out_missing', 'In and Out Missing'),
        ('all', 'All Types')

    ]

    MODE_SEL = [
        ('employee', 'By Employee'),
        ('department', 'By Department')
    ]

    date_from = fields.Datetime(string='From Date', default=time.strftime('%Y-%m-01'))
    date_to = fields.Datetime(string='From To', default=fields.Datetime.now)
    mode = fields.Selection(MODE_SEL, string="Mode", required=True)
    employee_ids = fields.Many2many("hr.employee", string="Employees", help="Leave Empty for all department Employees")
    department_ids = fields.Many2many("hr.department", string="Departments", help="Leave empty for all departments")
    attendance_type = fields.Selection(TYPE_SEL, string="Attendance Type", required=True)
    missing_type = fields.Selection(MISSING_SEL, string="Missing Type")

    #@api.multi
    def print_report(self):
        self.ensure_one()
        data = {}
        data['form'] = self.read()[0]
        res = self.env['report'].get_action(self, 'hr_attendance_extender.report_attendance', data=data)
        return res
