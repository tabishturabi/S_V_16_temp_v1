# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


# Migration Note
# class InheritFleetVehicleLogFuel(models.Model):
# 	_inherit = 'fleet.vehicle.log.fuel'
#
# 	fleet_trip_id = fields.Many2one(string="Trip ID", comodel_name="fleet.vehicle.trip")
# 	route_id = fields.Many2one(string="Route", track_visibility=True, related="fleet_trip_id.route_id")
# 	trip_distance = fields.Float(string="Trip Distance", related="route_id.total_distance", store=True)
# 	fuel_trip_amt = fields.Float(string="Fuel Expense Amount", related="fleet_trip_id.fuel_trip_amt", store=True)
# 	fuel_exp_method_id = fields.Many2one(string='Fuel Expense Rule', related="fleet_trip_id.fuel_exp_method_id",track_visibility=True,)
# 	extra_distance = fields.Integer(string="Extra Distance", related="fleet_trip_id.extra_distance")
# 	extra_distance_amount = fields.Float(string="Extra Distance Amount" , related="fleet_trip_id.extra_distance_amount")
# 	driver_id = fields.Many2one(string="Driver",related="vehicle_id.bsg_driver",store=True)
# 	driver_num = fields.Char(string="Driver Name",)
# 	voucher_num = fields.Char(string='Voucher Number')
# 	payment_seq = fields.Char(string='Payment Sequence')
# 	paymnet_date = fields.Date(string='Payment Date')
# 	payment_amount = fields.Float(string='Payment Amount')