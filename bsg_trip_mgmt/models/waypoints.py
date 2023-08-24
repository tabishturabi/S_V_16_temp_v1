# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BsgFleetVehicleWaypoints(models.Model):
	_name = 'fleet.vehicle.trip.waypoints'
	_description = "Waypoints"
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(string="Reference" ,default="/", readonly=True)
	waypoint = fields.Many2one(string="Branch/City", comodel_name="bsg_route_waypoints")
	picked_items = fields.Many2many("bsg_vehicle_cargo_sale_line","bsg_vehicle_cargo_sale_line_rel","line_id","pick_id",string="Picked")
	delivered_items = fields.Many2many("bsg_vehicle_cargo_sale_line","bsg_vehicle_cargo_deliver_line_rel","line_id","delivered_id", string="Delivered")
	bsg_fleet_trip_id = fields.Many2one(string="Trip ID", comodel_name="fleet.vehicle.trip")
	picked_items_count = fields.Integer(string="Picking Count", compute="_compute_items")
	delivered_items_count = fields.Integer(string="Delivered Count", compute="_compute_items")

	# 
	@api.depends('picked_items','delivered_items')
	def _compute_items(self):
		self.picked_items_count = len(self.picked_items.filtered(lambda s:not s.is_package))
		self.delivered_items_count = len(self.delivered_items.filtered(lambda s:not s.is_package))

#############################################


class BsgRouteWaypoints(models.Model):
	_inherit = 'bsg_route_waypoints'

	not_local = fields.Boolean("Is Not Local Trip")
