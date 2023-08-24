# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class VehicleDriverAssignReportWizard(models.TransientModel):
    _name = 'driver.assign.report'

    grouping_by = fields.Selection([('all','All'),('by_sticker_no','Vehicle Driver Assignment Group By Sticker NO. Report'), ('by_vehicle_type','Vehicle Driver Assignment Group By Vehicle Type Report'), ('by_domain_name', 'Vehicle Driver Assignment Group By Domain Name Report'),
                                    ('by_trailer_no', 'Vehicle Driver Assignment Group By Trailer NO. Report'), ('by_assign_driver', 'Vehicle Driver Assignment Group By Assign Driver Report'),
                                    ('by_unassign_driver', 'Vehicle Driver Assignment Group By Unassign Driver Report'),('created_by','Vehicle Driver Assignment Group By Created By Report'),
                                    ('by_assignment_date', 'Vehicle Driver Assignment Group By Assignment Date Report')],default='all' ,required=True,string='Grouping By')
    assignment_date_condition = fields.Selection([('all', 'All'), ('is_equal_to', 'is equal to '), ('is_not_equal_to', 'is not equal to'),
                                              ('is_after', 'is after'), ('is_before', 'is before'),
                                              ('is_after_or_equal_to', 'is after or equal to'),
                                              ('is_before_or_equal_to', 'is before or equal to'), ('is_between', 'is between'),
                                              ('is_set', 'is set'), ('is_not_set', 'is not set')], required=True, string='Assignment',default='all')
    period_grouping_by = fields.Selection([('day', 'Day'),('weekly', 'Weekly'),('month', 'Month'),('quarterly', 'Quarterly'),('year', 'Year'),], string='Period Grouping By')
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    assignment_date = fields.Datetime(string='Assign Date')
    vehicle_make = fields.Many2many('fleet.vehicle.model.brand',string='Vehicle Make')
    vehicle_sticker_no = fields.Many2many('fleet.vehicle',string='Vehicle Sticker NO')
    assign_driver_name = fields.Many2many('hr.employee','assign_driver_report_rel','assign_report_id','assign_driver_id',string="Assign Driver Name")
    maintenance_workshop = fields.Selection([('janadriah_workshop','Janadriah Workshop'),('bahra_workshop','Bahra Workshop'),('insurance_workshop','Insurance Workshop')],string="Maintenance Workshop")
    vehicle_group = fields.Many2many('bsg.vehicle.group',string='Vehicle Group')
    trailer_group = fields.Many2many('bsg.fleet.asset.group', string='Trailer Group')
    unassign_driver_name = fields.Many2many('hr.employee','unassign_driver_report_rel','unassign_report_id','unassign_driver_id',string='Unassign Driver Name')
    model_year =  fields.Many2many('bsg.car.year',string='Model Year')
    vehicle_state = fields.Many2many('fleet.vehicle.state',string='Vehicle State')
    vehicle_status = fields.Many2many('bsg.vehicle.status' ,string='Vehicle Status')
    vehicle_type = fields.Many2many('bsg.vehicle.type.table',string='Vehicle Type')
    domain_name = fields.Many2many('vehicle.type.domain',string='Domain Name')
    trailer_sticker_no = fields.Many2many('bsg_fleet_trailer_config', string='Trailer Sticker NO')
    creator_user = fields.Many2many('res.users',string="Create User")
    print_date = fields.Date(string='Today Date', default=fields.date.today())



    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_action(self,data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_pdf_id').report_action(self,data=data)













