# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import pandas as pd
from datetime import date, datetime, timedelta, timezone
import collections, functools, operator
from collections import OrderedDict


class SimCardReportWizard(models.TransientModel):
    _name = 'sim.card.report.wizard'

    grouping_by = fields.Selection([('sim_card_report', 'Sim Card Report'),
                                    ('by_service', 'SIM CARD Report Group By Service Provider'),
                                    ('by_package_type_name', 'SIM CARD Report Group By Package Type Name'),
                                    ('by_job_position', 'SIM CARD Report Group By Job Position'),
                                    ('by_branch', 'SIM CARD Report Group By Branch'),
                                    ('by_department', 'SIM CARD Report Group By Department'),
                                    ('by_bear_of_cost', 'SIM CARD Report Group by Bear Of Cost'),
                                    ('by_activation_date', 'SIM CARD Report Group By Activation Date'),
                                    ('by_last_delivered', 'SIM CARD Report Group By Last Delivered Date'),
                                    ('by_last_receipt', 'SIM CARD Report Group By Last Receipt Date')],
                                   default='sim_card_report', required=True, string='Grouping By')
    period_grouping_by = fields.Selection(
        [('month', 'Month'), ('quarterly', 'Quarterly'), ('year', 'Year'), ],
        string='Period Grouping By')

    service_provider = fields.Many2many('service.provider', string='Service Provider')
    job_id = fields.Many2many('hr.job', string="Job Position")
    package_type = fields.Many2many('package.type', string="Package Type Name")
    branch_id = fields.Many2many('bsg_branches.bsg_branches', string='Branch')
    department_id = fields.Many2many('hr.department', string="Department")
    sim_type = fields.Selection([('voice', 'Voice'), ('data', 'Data')], string='Sim Type')
    bear_cost = fields.Selection(string="Bear The Cost", selection=[('company', 'Company'), ('employee', 'Employee')])
    sim_card_link = fields.Selection(string="Sim Card Link", selection=[('link', 'Link'), ('unlink', 'Unlink')])\


    activation_date_from = fields.Date(string='Activation Date From')
    activation_date_to = fields.Date(string='Activation Date To')
    activation_date = fields.Date(string='Activation Date')
    activation_date_condition = fields.Selection(
        [('all', 'All'),('is_equal_to', 'is equal to '), ('is_not_equal_to', 'is not equal to'),
         ('is_after', 'is after'), ('is_before', 'is before'),
         ('is_after_or_equal_to', 'is after or equal to'),
         ('is_before_or_equal_to', 'is before or equal to'), ('is_between', 'is between'),
         ('is_set', 'is set'), ('is_not_set', 'is not set')], string='Activation Date Condition',default='all')

    last_delivery_date_from = fields.Date(string='Last Delivery Date From')
    last_delivery_date_to = fields.Date(string='Last Delivery Date To')
    last_delivery_date = fields.Date(string='Last Delivery Date')
    last_delivery_date_condition = fields.Selection(
        [('all', 'All'),('is_equal_to', 'is equal to '), ('is_not_equal_to', 'is not equal to'),
         ('is_after', 'is after'), ('is_before', 'is before'),
         ('is_after_or_equal_to', 'is after or equal to'),
         ('is_before_or_equal_to', 'is before or equal to'), ('is_between', 'is between'),
         ('is_set', 'is set'), ('is_not_set', 'is not set')], string='Last Delivery Date Condition',default='all')

    last_receipt_date_from = fields.Date(string='Last Receipt Date From')
    last_receipt_date_to = fields.Date(string='Last Receipt Date To')
    last_receipt_date = fields.Date(string='Last Receipt Date')
    last_receipt_date_condition = fields.Selection(
        [('all', 'All'),('is_equal_to', 'is equal to '), ('is_not_equal_to', 'is not equal to'),
         ('is_after', 'is after'), ('is_before', 'is before'),
         ('is_after_or_equal_to', 'is after or equal to'),
         ('is_before_or_equal_to', 'is before or equal to'), ('is_between', 'is between'),
         ('is_set', 'is set'), ('is_not_set', 'is not set')], string='Last Receipt Date Condition',default='all')

    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('sim_card_reports.sim_card_report').report_action(self, data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('sim_card_reports.vehicle_drivers_report_pdf_id').report_action(self, data=data)
