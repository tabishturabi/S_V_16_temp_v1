# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class EmployeeNidReportWizard(models.TransientModel):
    _name = 'employee.nid.report.wizard'

    mode = fields.Selection([('all', 'All'),('by_branch', 'By Branch'),
                             ('by_department', 'By Department'), ('by_company', 'By Company'),
                             ('by_employee_tag', 'By Employee Tag')], required=True, string='Mode', default='all')
    grouping_by = fields.Selection(
        [('all', 'All'),('by_branch', 'By Branch'),
         ('by_department', 'By Department'), ('by_company', 'By Company'),
         ('by_employee_tag', 'By Employee Tag'),('by_job_position','By Job Position')], required=True, string='Grouping By', default='all')
    branches = fields.Many2many('bsg_branches.bsg_branches', string='Branches')
    department = fields.Many2many('hr.department', string='Departments')
    company = fields.Many2many('res.company', string='Company')
    employee_tag = fields.Many2many('hr.employee.category', string='Employee Tags')
    guarantor = fields.Many2many('bsg.hr.guarantor', string='Guarantor')
    expiry_date_by = fields.Selection([('hijri_date', 'Hijri Date'), ('gregorian_date', 'Gregorian Date')],
                                      default='gregorian_date')
    expire_date_condition = fields.Selection(
        [('all', 'All'), ('is_equal_to', 'is equal to '), ('is_not_equal_to', 'is not equal to'),
         ('is_after', 'is after'), ('is_before', 'is before'),
         ('is_after_or_equal_to', 'is after or equal to'),
         ('is_before_or_equal_to', 'is before or equal to'), ('is_between', 'is between'),
         ('is_set', 'is set'), ('is_not_set', 'is not set')], required=True, string='Expire Date Condition',
        default='all')
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    expiry_date = fields.Date(string='Expiry Date')
    issue_date_hijri = fields.Char(string='Issue Date Hijri')
    expiry_date_hijri = fields.Char(string='Expiry Date Hijri')
    arrival_date_hijri = fields.Char(string='Arrival Date Hijri')
    employee_state = fields.Selection([('all', 'All'), ('on_job', 'On Job '), ('on_leave', 'On Leave'),
                                       ('return_from_holiday', 'Return From Holiday'), ('resignation', 'Resignation'),
                                       ('suspended', 'Suspended'), ('service_expired', 'Service Expired'),
                                       ('contract_terminated', 'Contract Terminated'),
                                       ('ending_contract_during_trial_period', 'Ending Contract During Trial Period')],
                                      required=True, string='Employee State', default='all')
    print_date = fields.Date(string='Today Date', default=fields.date.today())



    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_documents_expire_reports.employee_nid_report_xlsx_id').report_action(self,data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_documents_expire_reports.employee_nid_report_pdf_id').report_action(self,data=data)










