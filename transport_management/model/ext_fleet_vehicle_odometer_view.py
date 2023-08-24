# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class ext_bsg_vehicle_odometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    fleet_bx_trip_id = fields.Many2one(string="Bx Trip ID", comodel_name="transport.management")
    fleet_trip_id = fields.Many2one(string="Trip ID", comodel_name="fleet.vehicle.trip")

    @api.onchange('fleet_bx_trip_id')
    def onchange_fleet_bx_trip_id(self):
        if self.fleet_bx_trip_id:
            self.src_location = self.fleet_bx_trip_id.route_id.waypoint_from
            self.bsg_driver = self.fleet_bx_trip_id.transportation_driver
            self.extra_distance = self.fleet_bx_trip_id.extra_distance
            self.trip_distance = self.fleet_bx_trip_id.trip_distance
            self.value = self.fleet_bx_trip_id.total_distance
            self.date = self.fleet_bx_trip_id.loading_date
            # self.dest_location = self.fleet_bx_trip_id.route_id.waypoint_from
            self.dest_location = self.fleet_bx_trip_id.route_id.waypoint_to_ids[-1].waypoint
        else:

            self.src_location = False
            self.bsg_driver = False
            self.extra_distance = False
            self.trip_distance = False
            self.value = False
            self.date = False
            self.dest_location = False

    @api.onchange('fleet_trip_id')
    def onchange_fleet_trip_id(self):
        if self.fleet_trip_id:

            self.src_location = self.fleet_trip_id.route_id.waypoint_from
            self.bsg_driver = self.fleet_trip_id.driver_id
            self.extra_distance = self.fleet_trip_id.extra_distance
            self.trip_distance = self.fleet_trip_id.trip_distance
            self.value = self.fleet_trip_id.extra_distance + self.fleet_trip_id.trip_distance
            # self.date = self.fleet_trip_id.loading_date
            self.dest_location = self.fleet_trip_id.route_id.waypoint_to_ids[-1].waypoint
        else:

            self.src_location = False
            self.bsg_driver = False
            self.extra_distance = False
            self.trip_distance = False
            # self.value = False
            # self.date = False
            # self.dest_location = False

class ExtvehicleTrip(models.Model):
    _inherit = 'fleet.vehicle'

    fleet_bx_trip_id = fields.Many2one(string="Bx Trip ID", comodel_name="transport.management")
