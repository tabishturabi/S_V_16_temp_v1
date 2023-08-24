# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError


class EmployeeDirectoryReportWizard(models.TransientModel):
    _name = 'employee.directory.report.wizard'

    MODE_SEL = [
        ('specific', 'Specific Employee'),
        ('branch', 'By Branch'),
        ('dept', 'By Department'),
        ('company', 'By Company'),
        ('emp_tag', 'By Employee Tag'),
    ]
    EMPLOYEE_STATE = [
        ('on_job', 'On Job'),
        ('on_leave', 'On leave'),
        ('return_from_holiday', 'Return From Holiday'),
        ('resignation', 'Resignation'),
        ('suspended', 'Suspended'),
        ('service_expired', 'Service Expired'),
        ('contract_terminated', 'Contract Terminated'),
        ('ending_contract_during_trial_period', 'Ending Contract During Trial Period')
    ]

    GROUPING_SEL = [
        ('all', 'All'),
        ('by_branches', 'Employee Directory Report Group By Branches'),
        ('by_departments', 'Employee Directory Report Group By Departments'),
        ('by_job_positions', 'Employee Directory Report Group By Job Position'),
        ('by_nationality', 'Employee Directory Report Group By Nationality'),
    ]

    mode = fields.Selection(MODE_SEL, default='specific')
    branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="Branches")
    department_ids = fields.Many2many('hr.department', string="Department")
    is_parent_dempart = fields.Boolean(string='Is Parent Dept?')
    company_ids = fields.Many2many('res.company', string="Company")
    employee_tags_ids = fields.Many2many('hr.employee.category', string="Tags")
    employee_ids = fields.Many2many('hr.employee', string="Employee Names")
    employee_status = fields.Selection(EMPLOYEE_STATE, string='Employee State')
    grouping_by = fields.Selection(GROUPING_SEL, required=True, string='Grouping By', default="all")
    print_date_time = fields.Datetime(string='Print Datetime', default=lambda self: fields.datetime.now())

    # @api.multi
    def print_report(self):
        sudoed_self = self.sudo()
        all_recs = sudoed_self.env['hr.employee'].search([], limit=1)
        if all_recs:
            sudoed_self.ensure_one()
            [data] = sudoed_self.read()
            return sudoed_self.env.ref('bsg_employee_reports.employee_directory_report_xlsx_action').report_action(
                all_recs, data=data)

    # @api.multi
    def _get_report_base_filename(self):
        self.ensure_one()
        name = "Employee Directory Report"
        return name



