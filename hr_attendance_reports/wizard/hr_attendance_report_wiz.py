# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrAttendanceReport(models.TransientModel):
    _name = "attendance.report.wizard"
    _description = "Attendance Report Wizard"

    grouping_by = fields.Selection([('all', 'All'),
                                    ('by_branches', 'Group By Branches'),
                                    ('by_departments', 'Group By Departments'),
                                    ('by_job_positions', 'Group By Job Position')],
                                   required=True, string='Grouping By', default="all")
    report_list = fields.Selection([("daily", 'Daily Report'),
                                    ('summary', "Summary Report"),
                                    ('permission', "Permission Report"),
                                    ], equired=True, string='Report', default="daily")
    # Modes
    employee_ids = fields.Many2many('hr.employee', string='Employee')
    branch_ids = fields.Many2many('bsg_branches.bsg_branches', string='Branch')
    department_ids = fields.Many2many('hr.department', string='Department')
    is_parent_dep = fields.Boolean(string='Is Parent Dept?')
    resource_calendar_ids = fields.Many2many('resource.calendar', string='Working Hours')
    job_position_ids = fields.Many2many('hr.job', string='Job Position')
    company_ids = fields.Many2many('res.company', string='Company')
    employee_status = fields.Selection([('on_job', 'On Job '), ('on_leave', 'On Leave'),
                                       ('return_from_holiday', 'Return From Holiday'), ('resignation', 'Resignation'),
                                       ('suspended', 'Suspended'), ('service_expired', 'Service Expired'),
                                       ('contract_terminated', 'Contract Terminated'),
                                       ('ending_contract_during_trial_period', 'Ending Contract During Trial Period')],
                                       string='Employee Status')
    # religion_ids = fields.Many2many('hr.employee.religion',string='Religion')
    # region_ids = fields.Many2many('region.config', string='Region')
    # guarantor_ids = fields.Many2many('bsg.hr.guarantor', string='Guarantor')
    partner_type_ids = fields.Many2many('partner.type', string='Partner')
    country_ids = fields.Many2many('res.country', string='Nationality')
    employee_tags_ids = fields.Many2many('hr.employee.category', string='Employee Tags')
    # dates
    date_from = fields.Date("Date From")
    date_to = fields.Date("Date From")

    print_date_time = fields.Datetime(string='Print Datetime', default=lambda self: fields.datetime.now())
    print_date = fields.Date(string='Today Date', default=fields.date.today())

    def get_employee_domain(self):
        domain = []
        if self.employee_ids:
            domain += [('id', 'in', self.employee_ids.ids)]
        if self.branch_ids:
            domain += [('branch_id', 'in', self.branch_ids.ids)]
        if self.department_ids:
            child_dep = self.department_ids.mapped("child_ids")
            child_dep += self.department_ids
            domain += [('department_id', 'in', child_dep.ids)]
        if self.resource_calendar_ids:
            domain += [('resource_calendar_id', 'in', self.resource_calendar_ids.ids)]
        if self.job_position_ids:
            domain += [('job_id', 'in', self.job_position_ids.ids)]
        if self.country_ids:
            domain += [('country_id', 'in', self.country_ids.ids)]
        # if self.religion_ids:
        #     domain += [('bsg_religion_id', 'in', self.religion_ids.ids)]
        # if self.region_ids:
        #     domain += [('branch_id.region', 'in', self.region_ids.ids)]
        # if self.guarantor_ids:
        #     domain += [('guarantor_id', 'in', self.guarantor_ids.ids)]
        if self.company_ids:
            domain += [('company_id', 'in', self.company_ids.ids)]
        if self.partner_type_ids:
            domain += [('partner_type_id', 'in', self.partner_type_ids.ids)]
        if self.employee_tags_ids:
            domain += [('vehicle_status', 'in', self.employee_tags_ids.ids)]
        if self.employee_status == 'on_job':
            domain += [('employee_state', '=', 'on_job')]
        if self.employee_status == 'on_leave':
            domain += [('employee_state', '=', 'on_leave')]
        if self.employee_status == 'return_from_holiday':
            domain += [('employee_state', '=', 'return_from_holiday')]
        if self.employee_status:
            domain += [('employee_state', '=', str(self.employee_status))]
        return domain

    def get_report_data(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'employee_domain': self.get_employee_domain(),
            'grouping_by': self.grouping_by,
            'print_date': self.print_date,
        }
        return data

    def do_print_excel(self):
        data = self.get_report_data()
        report_type = self.report_list
        # if report_type == "daily":
        #     return self.env.ref('hr_attendance_reports.attendance_daily_report_id').report_action(self, data=data)
        if report_type == "summary":
            return self.env.ref('hr_attendance_reports.attendance_summary_excel_report_id').report_action(
                self, data=data)

    def do_print(self):
        data = self.get_report_data()
        report_type = self.report_list
        if report_type == "daily":
            return self.env.ref('hr_attendance_reports.attendance_daily_report_id').report_action(self, data=data)
        if report_type == "summary":
            return self.env.ref('hr_attendance_reports.attendance_summary_report_id').report_action(self, data=data)
        if report_type == "permission":
            return self.env.ref('hr_attendance_reports.attendance_permission_report_id').report_action(self, data=data)