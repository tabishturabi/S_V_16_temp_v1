# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class EmployeeSalarySumaryReportWizard(models.TransientModel):
    _name = 'salary.sumary.report.wizard'

    grouping_by = fields.Selection([('all','All'),('by_departments','Employee Salary Summary Report Group By Department'),
                                    ('by_parent_departments', 'Employee Salary Summary Report Group By Parent Department'),
                                    ('by_branches', 'Employee Salary Summary Report Group By Branch'),
                                    ('by_job_positions','Employee Salary Summary Report Group By Job Position'),
                                    ('by_region', 'Employee Salary Summary Report Group By Region'),
                                    ('by_nationality','Employee Salary Summary Report Group By Nationality')],required=True,string='Grouping By',default="all")
    employee_ids = fields.Many2many('hr.employee', string='Employee')
    branch_ids = fields.Many2many('bsg_branches.bsg_branches',string='Branch')
    department_ids = fields.Many2many('hr.department',string='Department')
    is_parent_dempart = fields.Boolean(string='Is Parent Dept?')
    resource_calendar_ids =  fields.Many2many('resource.calendar',string='Working Hours')
    job_position_ids = fields.Many2many('hr.job',string='Job Position')
    country_ids = fields.Many2many('res.country',string='Nationality')
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
    print_date_time = fields.Datetime(string='Print Datetime', default=lambda self: fields.datetime.now())
    print_date = fields.Date(string='Today Date', default=fields.date.today())



    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_salary_sumary_report.salary_sumary_report_xlsx_id').report_action(self,data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_salary_sumary_report.salary_sumary_report_pdf_id').report_action(self,data=data)













