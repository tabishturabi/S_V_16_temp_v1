# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class EmployeeSalaryInfoReportWizard(models.TransientModel):
    _name = 'salary.info.report.wizard'

    grouping_by = fields.Selection([('all','All'),('by_branches','Employee Salary Info Report Group By Branches'),
                                    ('by_departments','Employee Salary Info Report Group By Departments'),
                                    ('by_job_positions','Employee Salary Info Report Group By Job Position'),
                                    ('by_nationality','Employee Salary Info Report Group By Nationality'),
                                    ('by_guarantors','Employee Salary Info Report Group By Guarantor'),
                                    ('by_emp_tags','Employee Salary Info Report Group By Employee Tags'),
                                    ('by_working_hours','Employee Salary Info Report Group By Working Hours'),
                                    ('by_religion','Employee Salary Info Report Group By Religion'),
                                    ('by_emp_status','Employee Salary Info Report Group By Employee Status'),
                                    ('by_partner_type','Employee Salary Info Report Group By Partner Type'),
                                    ('by_company','Employee Salary Info Report Group By Company'),
                                    ('by_salary_payment_method','Employee Salary Info Report Group By Salary Payment Method'),
                                    ('by_is_driver','Employee Salary Info Report Group By Is Driver'),
                                    ('by_region','Employee Salary Info Report Group By Region')],required=True,string='Grouping By',default="all")
    employee_ids = fields.Many2many('hr.employee', string='Employee')
    branch_ids = fields.Many2many('bsg_branches.bsg_branches',string='Branch')
    department_ids = fields.Many2many('hr.department',string='Department')
    is_parent_dempart = fields.Boolean(string='Is Parent Dept?')
    resource_calendar_ids =  fields.Many2many('resource.calendar',string='Working Hours')
    job_position_ids = fields.Many2many('hr.job',string='Job Position')
    country_ids = fields.Many2many('res.country',string='Nationality')
    employee_state_id = fields.Many2one("bsg.hr.state",  string='Employee State')
    employee_status = fields.Selection([('on_job', 'On Job '), ('on_leave', 'On Leave'),
                                       ('return_from_holiday', 'Return From Holiday'), ('resignation', 'Resignation'),
                                       ('suspended', 'Suspended'), ('service_expired', 'Service Expired'),
                                       ('contract_terminated', 'Contract Terminated'),
                                       ('ending_contract_during_trial_period','Ending Contract During Trial Period')],string='Employee Status')
    religion_ids = fields.Many2many('hr.employee.religion',string='Religion')
    region_ids = fields.Many2many('region.config',string='Region')
    salary_payment_method = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')],string='Salary Payment Method')
    guarantor_ids = fields.Many2many('bsg.hr.guarantor',string='Guarantor')
    company_ids = fields.Many2many('res.company',string='Company')
    partner_type_ids = fields.Many2many('partner.type',string='Partner')
    is_driver = fields.Selection([('yes', 'Yes'), ('no', 'No')],string='Is Driver')
    employee_tags_ids = fields.Many2many('hr.employee.category',string='Employee Tags')
    print_date_time = fields.Datetime(string='Print Datetime',default=lambda self:fields.datetime.now())
    print_date = fields.Date(string='Today Date', default=fields.date.today())



    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_employee_salary_report.salary_info_report_xlsx_id').report_action(self,data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_employee_salary_report.salary_info_report_pdf_id').report_action(self,data=data)


class EmployeeInheritSalaryInfoReport(models.Model):
    _inherit = 'hr.employee'

    region_id = fields.Many2one(related='branch_id.region',store=True,string='Region')

class CompanyInheritSalaryInfoReport(models.Model):
    _inherit = 'res.company'

    company_code = fields.Char(string='Company Code')











