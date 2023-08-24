# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class PayslipMonthlyVariableReportWizard(models.TransientModel):
    _name = 'monthly.variable.report.wizard'

    grouping_by = fields.Selection([('all','All'),('by_department','Monthly Variables On Payslip Report Group By Department'),
                                    ('by_branch','Monthly Variables On Payslip Report Group By Branch'),
                                    ('by_job_position','Monthly Variables On Payslip Report Group By Job Position'),
                                    ('by_payslip_batch','Monthly Variables On Payslip Report Group By Payslip Batches'),
                                    ('by_salary_rule_name','Monthly Variables On Payslip Report Group By Salary Rule Name'),
                                    ('by_salary_rule_category','Monthly Variables On Payslip Report Group By Salary Rule Category'),
                                    ('by_payslip_periods','Monthly Variables On Payslip Report Group By Payslip Periods'),
                                    ('by_nationality','Monthly Variables On Payslip Report Group By Nationality'),
                                    ('by_salary_payment_method','Monthly Variables On Payslip Report Group By Salary Payment Method'),
                                    ('by_salary_structure','Monthly Variables On Payslip Report Group By Salary Structure'),
                                    ('by_employee','Monthly Variables On Payslip Report Group By Employee')],required=True,string='Grouping By',default="all")
    period_grouping_by = fields.Selection([('month', 'Month'),('year', 'Year'), ('quarterly', 'Quarterly') ],string='Period Grouping By')
    # start_date_condition_by = fields.Selection([('contract', 'Contract'),('payslip', 'Payslip')],string='Start Date Condition By',default='payslip',required=True)
    start_date_condition = fields.Selection(
        [('all', 'All'), ('is_equal_to', 'is equal to '), ('is_not_equal_to', 'is not equal to'),
         ('is_after', 'is after'), ('is_before', 'is before'),
         ('is_after_or_equal_to', 'is after or equal to'),
         ('is_before_or_equal_to', 'is before or equal to'), ('is_between', 'is between'),
         ('is_set', 'is set'), ('is_not_set', 'is not set')], required=True, string='Contract Start Date Condition',
        default='all')
    slip_start_date_condition = fields.Selection(
        [('all', 'All'), ('is_equal_to', 'is equal to '), ('is_not_equal_to', 'is not equal to'),
         ('is_after', 'is after'), ('is_before', 'is before'),
         ('is_after_or_equal_to', 'is after or equal to'),
         ('is_before_or_equal_to', 'is before or equal to'), ('is_between', 'is between'),
         ('is_set', 'is set'), ('is_not_set', 'is not set')], required=True, string='Slip Start Date Condition',
        default='all')
    date_from = fields.Date(string='Contract From')
    date_to = fields.Date(string='Contract To')
    start_date = fields.Date(string='Contract Start Date')
    slip_date_from = fields.Date(string='Slip From')
    slip_date_to = fields.Date(string='Slip To')
    slip_start_date = fields.Date(string='Slip Start Date')
    period_month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'),
                              ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'),
                              ('11', 'November'), ('12', 'December')], string='Month')
    period_year = fields.Many2one('bsg.car.year',string='Year')
    payslip_batch_ids = fields.Many2many('hr.payslip.run', string='Payslip Batches')
    department_ids = fields.Many2many('hr.department', string='Department')
    job_position_ids = fields.Many2many('hr.job', string='Job Position')
    employee_ids = fields.Many2many('hr.employee', string='Employee')
    employee_state_id = fields.Many2one("bsg.hr.state",  string='Employee State')
    employee_status = fields.Selection([('on_job', 'On Job '), ('on_leave', 'On Leave'),
                                        ('return_from_holiday', 'Return From Holiday'), ('resignation', 'Resignation'),
                                        ('suspended', 'Suspended'), ('service_expired', 'Service Expired'),
                                        ('contract_terminated', 'Contract Terminated'),
                                        ('ending_contract_during_trial_period', 'Ending Contract During Trial Period')],
                                       string='Employee Status')
    branch_ids = fields.Many2many('bsg_branches.bsg_branches',string='Branch')
    salary_payment_method = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')], string='Salary Payment Method')
    country_ids = fields.Many2many('res.country',string='Nationality')
    company_ids = fields.Many2many('res.company',string='Company')
    salary_structure_ids = fields.Many2many('hr.payroll.structure',string='Salary Structure')
    from_payslip_ref = fields.Char(string='From Payslip Reference')
    to_payslip_ref = fields.Char(string='To Payslip Reference')
    rule_category_ids = fields.Many2many('hr.salary.rule.category',string='Rule Category')
    rule_ids = fields.Many2many('hr.salary.rule',string='Rule Name')
    print_date_time = fields.Datetime(string='Print Datetime',default=lambda self:fields.datetime.now())
    print_date = fields.Date(string='Today Date', default=fields.date.today())




    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_payslip_variable_report.payslip_variable_report_xlsx_id').report_action(self,data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_payslip_variable_report.salary_info_report_pdf_id').report_action(self,data=data)




class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    country_id = fields.Many2one(related='employee_id.country_id',store=True,string='Nationality')



class CarYear(models.Model):
    _inherit = 'bsg.car.year'
    _order = 'car_year_name desc'






