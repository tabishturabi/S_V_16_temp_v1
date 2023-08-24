# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class VehicleDetailsReportWizard(models.TransientModel):
    _name = 'vehicle.details.report.wizard'

    grouping_by = fields.Selection([('all','All'),('by_maker_name','Vehicle Details Report Group By Maker Name'), ('by_model_name','Vehicle Details Report Group By Model Name'), ('by_manufacturing_year', 'Vehicle Details Report Group By Manufacturing Year'),
                                    ('by_vehicle_type_name', 'Vehicle Details Report Group By Vehicle Type Name'), ('by_domain_name', 'Vehicle Details Report Group By Domain Name'),('vehicle_group_name', 'Vehicle Details Report Group By Vehicle Group Name'),('vehicle_status_name', 'Vehicle Details Report Group By Vehicle Status Name'),
                                    ('by_state_name', 'Vehicle Details Report Group By Vehicle State Name'),('by_trailer_group_name', 'Vehicle Details Report Group By Trailer Group Name'),('by_last_trip_route_name', 'Vehicle Details Report Group By Last Trip Route Name'),('by_current_branch_name', 'Vehicle Details Report Group By Current Branch Name'),
                                    ('by_current_location_name', 'Vehicle Details Report Group By Current Location Name'),('by_created_by','Vehicle Details Report Group By Created By')], required=True,string='Grouping By')
    vehicle_make = fields.Many2many('fleet.vehicle.model.brand',string='Vehicle Make')
    vehicle_sticker_no = fields.Many2many('fleet.vehicle',string='Vehicle Sticker NO')
    model_year =  fields.Many2many('bsg.car.year',string='Model Year')
    vehicle_state = fields.Many2many('fleet.vehicle.state',string='Vehicle State')
    vehicle_status = fields.Many2many('bsg.vehicle.status' ,string='Vehicle Status')
    vehicle_type = fields.Many2many('bsg.vehicle.type.table',string='Vehicle Type')
    domain_name = fields.Many2many('vehicle.type.domain',string='Domain Name')
    print_date = fields.Date(string='Today Date', default=fields.date.today())
    driver_link = fields.Selection([('linked','Linked'),('unlinked','Un_Linked')],string='Driver Link')
    driver_name = fields.Many2many('hr.employee', string='Driver Name')
    trailer_link = fields.Selection([('linked','Linked'),('unlinked','Un_Linked')],string='Trailer Link')
    trailer_group = fields.Many2many('bsg.fleet.asset.group',string='Trailer Group')
    current_branches = fields.Many2many('bsg_branches.bsg_branches',string='Current Branches')
    vehicle_group = fields.Many2many('bsg.vehicle.group',string='Vehicle Group')
    trailer_sticker_no = fields.Many2many('bsg_fleet_trailer_config',string='Trailer Sticker NO')
    route_name = fields.Many2many('bsg_route',string='Route Name')
    current_locations = fields.Many2many('bsg_route_waypoints',string='Current Locations')



    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_action(self,data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_vehicle_details_reports.vehicle_details_report_pdf_id').report_action(self,data=data)














