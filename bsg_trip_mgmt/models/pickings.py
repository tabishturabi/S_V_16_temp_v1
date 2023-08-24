# -*- coding: utf-8 -*-
import math
import re
from collections import defaultdict
from datetime import datetime
from odoo import _, api, fields, models
from odoo.exceptions import UserError,ValidationError
import requests
from pytz import timezone, UTC

class BsgFleetVehiclePickings(models.Model):
	_name = 'fleet.vehicle.trip.pickings'
	_description = "Pickings"
	_inherit = ['mail.thread','mail.activity.mixin']
	_rec_name = "picking_name"

	@api.model
	def _get_sorted_lines(self):
		records = []
		if self.bsg_fleet_trip_id:
			car_sale_order = self.env['bsg_vehicle_cargo_sale'].search([('route','=',self.bsg_fleet_trip_id.route_id.id)])
			if car_sale_order:
				for so in car_sale_order:
					car_sale_order_lines = self.env['bsg_vehicle_cargo_sale_line'].search([('bsg_cargo_sale_id','=',so.id)])
					if car_sale_order_lines:
						for sol in car_sale_order_lines:
							records.append(sol.id)
		# print(records)
		domain = [('id','in',records)]
		return domain

	# state= fields.Selection(string="Status", selection=[
	# 	('draft','Draft'),
	# 	('confirmed','Confirmed'),
	# 	('progress','In Operation'),
	# 	('done','Done'),
	# 	('cancelled','Cancelled')
	
	# ], default="draft")

	picking_name = fields.Many2one(string="Reference", comodel_name="bsg_vehicle_cargo_sale_line", domain=_get_sorted_lines)
	state = fields.Selection(related="picking_name.state",store=True)
	active = fields.Boolean(string="Active", track_visibility=True, default=True)
	loc_from = fields.Many2one(string="From", comodel_name="bsg_route_waypoints", related="picking_name.loc_from",store=True)
	loc_to = fields.Many2one(string="To", comodel_name="bsg_route_waypoints", related="picking_name.loc_to",store=True)
	is_package = fields.Boolean(string="Is Package", comodel_name="bsg_vehicle_cargo_sale_line",
								related="picking_name.is_package")
	pickup_loc = fields.Many2one('bsg_route_waypoints', related="picking_name.pickup_loc", store=True ,string="Pickup Location")
	drop_loc = 	fields.Many2one('bsg_route_waypoints', related="picking_name.drop_loc", store=True, string="Drop")
	picking_date = fields.Datetime(string="Date")
	scheduled_date = fields.Datetime(string="Scheduled Date")
	bsg_fleet_trip_id = fields.Many2one(string="Trip ID", comodel_name="fleet.vehicle.trip")
	bsg_state_id = fields.Selection(related="bsg_fleet_trip_id.state",store=True)
	car_maker_id = fields.Many2one(
		'bsg_car_config',
		string='Car Maker',
		related="picking_name.car_make",store=True
	)
	car_model_id = fields.Many2one(
		'bsg_car_model',
		string='Car Model',
		related="picking_name.car_model",store=True
	)
	car_size_id = fields.Many2one(
		'bsg_car_size',
		string='Car Maker',
		related="picking_name.car_size",
	)

	chassis_no = fields.Char(
		string='Chassis No',
		related="picking_name.chassis_no",store=True
	)
	plate_no = fields.Char(
		string='Plate No',
		related="picking_name.general_plate_no",store=True
	)

	group_name = fields.Char(
		string='Group Number',
		store=True,
		compute="btn_get_group_by"
	)

	def get_current_tz_time(self, expected_date):
		tz = timezone(self.env.context.get('tz') or self.env.user.tz)
		return UTC.localize(expected_date).astimezone(tz).replace(tzinfo=None)

	@api.constrains('picking_name')
	def check_picking_name_duplicates(self):
		count = self.search_count([('picking_name', '=', self.picking_name.id), ('bsg_fleet_trip_id', '=', self.bsg_fleet_trip_id.id)])
		if count > 1:
			raise ValidationError(_('Sale line [ %s ] already added to this trip!')%self.picking_name.sale_line_rec_name)

	#These method made in hurry need to refactor this two methods 
	@api.depends('bsg_fleet_trip_id')
	# 
	def btn_get_group_by(self):
		if self.bsg_fleet_trip_id:
			data = []
			for line in self.bsg_fleet_trip_id.stock_picking_id:
				active_record = self.get_records(line.picking_name.bsg_cargo_sale_id.customer_type
					, line.loc_from.id, line.loc_to.id)
				if active_record not in data:
					data.append(active_record)
			counter = 1
			for rec in data:
				for item in rec:
					self.browse(item).group_name = self.bsg_fleet_trip_id.name +"/"+str(counter)
				counter +=1


	def get_records(self, customer_type,loc_from,loc_to):
		active_rec = []
		for k in self.bsg_fleet_trip_id.stock_picking_id:
			if customer_type == str(k.picking_name.bsg_cargo_sale_id.customer_type) \
			and int(loc_from) == k.loc_from.id and int(loc_to) == k.loc_to.id:
				active_rec.append(k.id)
		return active_rec


	# @api.multi
	def unlink(self):
		"""
			Delete all record(s) from table heaving record id in ids
			return True on success, False otherwise

			@return: True on success, False otherwise
		"""
		for rec in self:
			if rec.bsg_fleet_trip_id.state != 'draft':
				raise UserError(_('You can delete Picking only when Trip in Draft state'))

		for rec in self:
			if rec.picking_name and rec.bsg_state_id =='draft':
				if rec.bsg_fleet_trip_id.trip_type != 'local':
					rec.picking_name.state = 'confirm'
				rec.picking_name.added_to_local_to_shipment_branch = False
				rec.picking_name.added_to_local_from_arrival_branch = False
				rec.picking_name.added_to_trip = False
				rec.picking_name.fleet_trip_id = False
				if rec.bsg_fleet_trip_id.trip_waypoint_ids:
					for line in rec.bsg_fleet_trip_id.trip_waypoint_ids:
						if rec.picking_name.id in line.picked_items.ids:
							line.picked_items = [(3, rec.picking_name.id)]
						if rec.picking_name.id in line.delivered_items.ids:
							line.delivered_items = [(3, rec.picking_name.id)]
				rec._update_arriva_lines(rec.bsg_fleet_trip_id, rec.picking_name)
				rec.bsg_fleet_trip_id.total_capacity += rec.picking_name.car_size.trailer_capcity
			if rec.picking_name and rec.bsg_state_id =='on_transit':
				rec.picking_name.state = 'on_transit'
				rec.picking_name.added_to_local_to_shipment_branch = False
				rec.picking_name.added_to_local_from_arrival_branch = False
				rec.picking_name.added_to_trip = False
				rec.picking_name.fleet_trip_id = False
				if rec.bsg_fleet_trip_id.trip_waypoint_ids:
					for line in rec.bsg_fleet_trip_id.trip_waypoint_ids:
						if rec.picking_name.id in line.picked_items.ids:
							line.picked_items = [(3, rec.picking_name.id)]
						if rec.picking_name.id in line.delivered_items.ids:
							line.delivered_items = [(3, rec.picking_name.id)]
				rec._update_arriva_lines(rec.bsg_fleet_trip_id, rec.picking_name)
				rec.bsg_fleet_trip_id.total_capacity += rec.picking_name.car_size.trailer_capcity
		return super(BsgFleetVehiclePickings, self).unlink()



	# # Update arrival screen on sale order Confirmation
	def _update_arriva_lines(self, trip, delivery_id):
		if trip:
			if delivery_id:
				for line in trip.bsg_trip_arrival_ids:
					for rec in line.arrival_line_ids:
						if rec.delivery_id.id == delivery_id.id:
							rec.unlink()
