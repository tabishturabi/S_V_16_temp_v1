# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class VehicledriverReportWizard(models.TransientModel):
    _name = 'vehicle.drivers.report.wizard'

    grouping_by = fields.Selection([('all','All'),('by_nationality','Vehicle Drivers Report Group By Nationality'), ('by_employee_status','Vehicle Drivers Report Group By Employee Status'), ('by_vehicle_make', 'Vehicle Drivers Report Group By Vehicle Make'),
                                    ('by_vehicle_type_name', 'Vehicle Drivers Report Group By Vehicle Type'), ('by_domain_name', 'Vehicle Drivers Report Group By Domain Name'),('by_link_name', 'Vehicle Drivers Report Group by Driver Link'),('by_iqama_expiry', 'Vehicle Drivers Report Group By Iqama Expiry Period'),
                                    ('by_nid_expiry', 'Vehicle Drivers Report Group By National ID Expiry Period'),('by_passport_expiry', 'Vehicle Drivers Report Group By Passport Expiry Period'),
                                    ('by_licence_expiry', 'Vehicle Drivers Report Group By Licence Expiry Period')],default='all' ,required=True,string='Grouping By')
    period_grouping_by = fields.Selection(
        [('day', 'Day'), ('weekly', 'Weekly'), ('month', 'Month'), ('quarterly', 'Quarterly'), ('year', 'Year'), ],
        string='Period Grouping By')
    expiry_date_on = fields.Selection([('emp_iqama','Employee Iqama'),('national_id','Employee National ID'),('passport','Employee Passport'),('emp_licence','Employee Licence')],default='emp_iqama',required=True,string='Expiry Date On')
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
    vehicle_make = fields.Many2many('fleet.vehicle.model.brand',string='Vehicle Make')
    vehicle_sticker_no = fields.Many2many('fleet.vehicle',string='Vehicle Sticker NO')
    vehicle_group = fields.Many2many('bsg.vehicle.group',string='Vehicle Group')
    model_year =  fields.Many2many('bsg.car.year',string='Model Year')
    vehicle_state = fields.Many2many('fleet.vehicle.state',string='Vehicle State')
    vehicle_type = fields.Many2many('bsg.vehicle.type.table',string='Vehicle Type')
    domain_name = fields.Many2many('vehicle.type.domain',string='Domain Name')
    print_date = fields.Date(string='Today Date', default=fields.date.today())
    driver_link = fields.Selection([('linked','Linked'),('unlinked','Un_Linked')],string='Driver Link')
    driver_name = fields.Many2many('hr.employee', string='Driver Name')



    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_action(self,data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_pdf_id').report_action(self,data=data)














