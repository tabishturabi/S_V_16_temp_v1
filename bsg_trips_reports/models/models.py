# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class TripsReport(models.TransientModel):
    _name = 'trips.report.wizard'

    form = fields.Datetime(string='From',required=True)
    to = fields.Datetime(string='To',required=True)
    vehicle_type = fields.Many2many('bsg.vehicle.type.table', string="Vehicle Type")
    trip_type = fields.Selection([
        ('auto', 'تخطيط تلقائي'),
        ('manual', 'تخطيط يدوي'),
        ('local', 'خدمي')
    ], string="Trip Type")
    branch_from = fields.Many2many('bsg_route_waypoints','trips_report_wiz_start_branch_rel','trips_report_wiz_id','start_branch_id', string="From Branch")
    branch_to = fields.Many2many('bsg_route_waypoints','trips_report_wiz_end_branch_rel','trips_report_wiz_id','end_branch_id', string="To Branch")
    trip_status = fields.Selection(string="Trip Status", selection=[
        ('draft', 'Draft'),
        ('on_transit', 'On Transit'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Operation'),
        ('done', 'Done'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled')
    ])
    vehicle_group_id = fields.Many2one('bsg.vehicle.group', string="Vehicle Group Name")
    truck_load = fields.Selection([
        ('full', 'Full Load'),
        ('empty', 'Empty Load')
    ], string="Truck Load")
    user_register_arrival = fields.Many2one('res.users',string="User Register Arrival")
    user_id = fields.Many2one('res.users', string="User")
    car_load = fields.Selection([
        ('full', 'Full Load'),
        ('empty', 'Empty Load')
    ], string="Car Load")
    print_date = fields.Date(string="Print Date",default=fields.date.today())



    # @api.multi
    def click_print_excel(self):
        domain = [('expected_start_date', '>=', self.form), ('expected_start_date', '<=', self.to)]
        if self.vehicle_type:
            domain.append(('vehicle_id.vehicle_type', 'in', self.vehicle_type.ids))
        if self.trip_type:
            domain.append(('trip_type', '=', self.trip_type))
        if self.branch_from:
            domain.append(('start_branch', 'in', self.branch_from.ids))
        if self.branch_to:
            domain.append(('end_branch', 'in', self.branch_to.ids))
        if self.trip_status:
            domain.append(('state', '=', self.trip_status))
        if self.vehicle_group_id:
            domain.append(('vehicle_id.vehicle_group_name', '=', self.vehicle_group_id.id))
        if self.truck_load:
            domain.append(('display_truck_load', '=', self.truck_load))
        if self.user_register_arrival:
            domain.append(('write_uid', '=', self.user_register_arrival.id))
        if self.user_id:
            domain.append(('create_uid', '=', self.user_id.id))

        print('.............domain................', domain)

        trip_ids = self.env['fleet.vehicle.trip'].search(domain)
        if trip_ids:
            data = {
                'ids': self.ids,
                'model': self._name,
            }
            return self.env.ref('bsg_trips_reports.trips_reports_xlsx_id').report_action(self,data=data)
        else:
            raise UserError("No Trips found against these parameters.")

    # @api.multi
    def click_print_pdf(self):
        domain = [('expected_start_date', '>=', self.form), ('expected_start_date', '<=', self.to)]
        if self.vehicle_type:
            domain.append(('vehicle_id.vehicle_type', 'in', self.vehicle_type.ids))
        if self.trip_type:
            domain.append(('trip_type', '=', self.trip_type))
        if self.branch_from:
            domain.append(('start_branch', 'in', self.branch_from.ids))
        if self.branch_to:
            domain.append(('end_branch', 'in', self.branch_to.ids))
        if self.trip_status:
            domain.append(('state', '=', self.trip_status))
        if self.vehicle_group_id:
            domain.append(('vehicle_id.vehicle_group_name', '=', self.vehicle_group_id.id))
        if self.truck_load:
            domain.append(('display_truck_load', '=', self.truck_load))
        if self.user_register_arrival:
            domain.append(('write_uid', '=', self.user_register_arrival.id))
        if self.user_id:
            domain.append(('create_uid', '=', self.user_id.id))

        print('.............domain................',domain)

        trip_ids = self.env['fleet.vehicle.trip'].search(domain)
        if trip_ids:
            data = {
                'ids': self.ids,
                'model': self._name,
            }
            return self.env.ref('bsg_trips_reports.trips_report_pdf_id').report_action(self,data=data)
        else:
            raise UserError("No Trips found against these parameters.")














