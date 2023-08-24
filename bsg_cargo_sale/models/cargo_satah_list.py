# -*- coding: utf-8 -*-
import math
import re
from collections import defaultdict
from datetime import datetime
from odoo import _, api, fields, models
from odoo.exceptions import UserError
import requests

class SatahVehicaleList(models.Model):
	_name = 'satah.vehicale.list'
	_description = "Satah Vehicale List"

	# @api.model
	# def default_get(self, fields):
	# 	result = super(SatahVehicaleList, self).default_get(fields)
	# 	print ("self._context",self._context)
	# 	result['cargo_sale_id'] = self._context.get('default_parent_id', False)
	# 	return result

	# 
	@api.depends('price','discount')
	def _final_amount(self):
		self.final_amount = 0
		if self.discount:
			self.final_amount = (self.price - self.discount)
		else:
			self.final_amount = self.price

	plate_no = fields.Char(string="Plate No")
	loc_src = fields.Many2one(string="Source", comodel_name="bsg_route_waypoints")
	loc_dest = fields.Many2one(string="Destination", comodel_name="bsg_route_waypoints")
	satah_type = fields.Selection(string="Satah Type", selection=[
		('satah_big', 'Satah Big'),
		('satah_small', 'Satah Small')
	], default="")
	distance = fields.Float('Distance')
	price = fields.Float('Amount', compute="_get_amount")
	final_amount = fields.Float('Final Amount',compute="_final_amount")
	discount = fields.Float('Discount')
	cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale', 'Cargo Sale')
	cargo_sale_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line', 'Car',
										 domain="[('bsg_cargo_sale_id', '=', cargo_sale_id)]")
	product_id = fields.Many2one('product.template', 'Satah Type.',
								 default=lambda self: self.env['product.template'].search([('is_satah', '=', True)])[
									 0].id)
	type = fields.Selection([('none', 'None'),('pickup', 'pickup'), ('delivery', 'delivery'), ('both', 'Both')], 'Satah Service.',
							help="Vehicle pickup or delivery charge type", default="none")
	is_google_cords = fields.Boolean(string="Is Google Location")
	location_lat = fields.Char(string="Latitude")
	location_long = fields.Char(string="Longitude")
	map = fields.Text('Map')
	
	@api.depends('distance', 'satah_type')
	def _get_amount(self):
		for rec in self:
			rec.price = 0
			if rec.distance and rec.satah_type:
				for line in rec.product_id.satah_line_ids:
					if line.satah_type == rec.satah_type:
						if (rec.distance >= line.from_km) and (rec.distance <= line.to_km):
							rec.price = line.price

	# 
	def ActionGteDistance(self):
		google_maps_api_key = self.env['website'].get_current_website().google_maps_api_key
		if not google_maps_api_key:
			raise UserError(
				_('Please Check google api key is missing. Go to website and configuration...'),
			)
		URL = "https://maps.googleapis.com/maps/api/distancematrix/json?key=" + str(google_maps_api_key) + "&"
		# for rec in self:
		rec = self
		destinations = origins = False
		if not rec.is_google_cords:
			if rec.loc_src.location_long and rec.loc_src.location_lat:
				origins = 'origins=' + str(rec.loc_src.location_lat) + ',' + str(rec.loc_src.location_long)
			else:
				raise UserError(
					_('Please Check From Location Not founde Google Lat.. & Lan..'),
				)
			if rec.loc_dest.location_long and rec.loc_dest.location_lat:
				destinations = 'destinations=' + str(rec.loc_dest.location_lat) + ',' + str(
					rec.loc_dest.location_long)
			else:
				raise UserError(
					_('Please Check To Location Not founde Google Lat.. & Lan..'),
				)
		else:
			if rec.loc_src:
				origins = 'origins=' + str(rec.loc_src.location_lat) + ',' + str(rec.loc_src.location_long)
				destinations = 'destinations=' + str(rec.location_lat) + ',' + str(rec.location_long)
			elif rec.loc_dest:
				origins = 'origins=' + str(rec.location_lat) + ',' + str(rec.location_long)
				destinations = 'destinations=' + str(rec.loc_dest.location_lat) + ',' + str(
					rec.loc_dest.location_long)
			else:
				raise UserError(
					_('Please Check To Location Not founde Google Lat.. & Lan..'),
				)
		if destinations and origins:
			Response = requests.get(URL + origins + '&' + destinations)
			RespJson_Payload = Response.json()
			if RespJson_Payload['rows'] and RespJson_Payload['rows'][0].get('elements'):
				if RespJson_Payload['rows'][0].get('elements')[0].get('distance'):
					distance = RespJson_Payload['rows'][0].get('elements')[0]['distance'].get('text')
					distance.split(' ')
					rec.distance = float(distance[0])
