# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class bsg_vehicle_odometer(models.Model):
	_inherit = 'fleet.vehicle.odometer'

	fleet_trip_id = fields.Many2one(string="Trip ID", comodel_name="fleet.vehicle.trip")
	src_location = fields.Many2one(string="Source", comodel_name="bsg_route_waypoints")
	dest_location = fields.Many2one(string="Destination", comodel_name="bsg_route_waypoints")

	# driver_id = fields.Many2one("hr.employee", string="Driver", readonly=False, required=False)
	bsg_driver = fields.Many2one(string="Driver", comodel_name="hr.employee",track_visibility=True)



	extra_distance = fields.Integer(string="Extra Distance")
	trip_distance = fields.Float(string="Trip Distance", store=True)
	# date = fields.Datetime(string='Date', store=True)
	date = fields.Datetime(string='Date', store=True)



	@api.onchange('vehicle_id')
	def onchange_vehicleee_id(self):
		if self.vehicle_id:
			self.bsg_driver = self.vehicle_id.bsg_driver

# 	@api.model
# 	def create(self, vals):
# 		rec_id = super(bsg_vehicle_odometer, self).create(vals)
# 		res = self.env['fleet.vehicle'].search([('id','=', vals['vehicle_id'])])

# 		rec_id.vehicle_id.fleet_bx_trip_id = rec_id.fleet_bx_trip_id.id
# 		rec_id.vehicle_id.trip_id = rec_id.fleet_trip_id.id
# 		rec_id.vehicle_id.expected_end_date = rec_id.date

# 		return rec_id
	
# 	@api.model
# 	def create(self, vals):
# 		rec_id = super(bsg_vehicle_odometer, self).create(vals)
# 		vehicle = self.env['fleet.vehicle'].search([('id','=', vals['vehicle_id'])])

# 		vehicle.fleet_bx_trip_id = rec_id.fleet_bx_trip_id.id
# 		vehicle.trip_id = rec_id.fleet_trip_id.id
# 		vehicle.expected_end_date = rec_id.date
# 		# vehicle.co2 = rec_id.value + vehicle.co2

# 		return rec_id


	# 
	# @api.constrains('fleet_bx_trip_id')
	# def check_vehicle_id(self):
	# 	if self.fleet_bx_trip_id:
	# 		record_id = self.env['fleet.vehicle.odometer'].search(
	# 			[('vehicle_id', '=', self.vehicle_id.id), ('id', '!=', self.id), ('fleet_bx_trip_id', '=', self.fleet_bx_trip_id.id)])
	# 		if record_id:
	# 			raise UserError(_("vehicle Id And Bx trip ID must Be Unique...!"))

	# 
	# @api.constrains('fleet_trip_id')
	# def check_fleet_trip_id(self):
	# 	if self.fleet_trip_id:
	# 		record_id = self.env['fleet.vehicle.odometer'].search(
	# 			[('vehicle_id', '=', self.vehicle_id.id), ('id', '!=', self.id),
	# 			 ('fleet_trip_id', '=', self.fleet_bx_trip_id.id)])
	# 		if record_id:
	# 			raise UserError(_("vehicle Id And trip ID must Be Unique...!"))


class bsg_vehicle_contract(models.Model):
	_inherit = 'fleet.vehicle.log.contract'

	ishtimara_no = fields.Char(string="Ishtimara No.")
