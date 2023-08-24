# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BsgPortFuelAmount(models.Model):
	_name = 'bsg.port.fuel.amount'
	_description = "Port & internal Transport"
	_inherit = ['mail.thread']
	_rec_name = "rules_description"

	active = fields.Boolean(string="Active", track_visibility=True, default=True)
	rule_seq = fields.Integer(string='Seq No',track_visibility=True)
	rules_description = fields.Char(string='Rule Description',track_visibility=True)
	rule_amount = fields.Float(string='Rule Amount',track_visibility=True)
	rule_option = fields.Selection(string="Port Fuel Rule Per", selection=[
		('trip', 'Trip'),
		('car', 'Car'),

	], default="trip", track_visibility=True,)
	distance_from = fields.Integer(string='Distance From',track_visibility=True)
	distance_to = fields.Integer(string='Distance To',track_visibility=True)
	trip_wise_config_ids = fields.One2many('bsg.port.fuel.trip','fuel_trip_config_id',string='Trip Config IDS',track_visibility=True)
	car_wize_ids = fields.One2many('bsg.port.fuel.car','fuel_trip_config_id',string='Car Config IDS',track_visibility=True)
	vehicle_type = fields.Many2one('bsg.vehicle.type.table', string='Vehicle Type',track_visibility=True)
	route_type = fields.Selection([
	('km','Domestic'),
	('route','International'),
	('port','Port'),
	('local','Local'),
	('hybrid','Hybrid Route')], string="Route Type", help='This is to determine if the route is international/domestic or between ports',track_visibility=True 
	)

	
	_sql_constraints = [
		('port_rule_seq_uniq', 'unique (rule_seq)', _('The Seq must be unique !')),
	]

	#as no more need as told by mr hamdan
	# 
	# @api.constrains('rule_amount')
	# def _check_negative_values(self):
	# 	if self.rule_amount <= 0:
	# 		raise UserError(_('Price must be non-negative or zero.'))




class BsgPortFuelTrip(models.Model):
	_name = 'bsg.port.fuel.trip'
	_description = "Port Fuel Trip Wise"
	_inherit = ['mail.thread']

	name = fields.Char(string='Description')
	loc_from = fields.Integer(string='From')
	loc_to = fields.Integer(string='To')
	amount = fields.Float(string='Amount')
	fuel_trip_config_id = fields.Many2one('bsg.port.fuel.amount',
	    string='Fuel Config ID')

	#for tracking value on change on line
	# @api.multi
	def write(self, vals):
		old_values = {
		'name' : self.name,
		'loc_from' : self.loc_from,
		'loc_to' : self.loc_to,
		'amount' : self.amount,
		'fuel_trip_config_id' : self.fuel_trip_config_id,
		}
		res = super(BsgPortFuelTrip,self).write(vals)
		tracked_fields = self.env['bsg.port.fuel.trip'].fields_get(vals)
		changes, tracking_value_ids = self._message_track(tracked_fields, old_values)
		if changes:
			self.fuel_trip_config_id.message_post(tracking_value_ids=tracking_value_ids)
			return res


class BsgPortFuelCar(models.Model):
	_name = 'bsg.port.fuel.car'
	_description = "Port Fuel Car Wise"
	_inherit = ['mail.thread']



	name = fields.Char(string='Description')
	amount = fields.Float(string='Amount')
	car_size_id = fields.Many2one('bsg_car_size',string='Car Size')
	vehicle_class = fields.Char(string='Vehicle Class')
	fuel_trip_config_id = fields.Many2one('bsg.port.fuel.amount',
	    string='Fuel Config ID')
	
	
	#for tracking value on change on line
	# @api.multi
	def write(self, vals):
		old_values = {
		'name' : self.name,
		'amount' : self.amount,
		'car_size_id' : self.car_size_id,
		'vehicle_class' : self.vehicle_class,
		'fuel_trip_config_id' : self.fuel_trip_config_id,
		}
		res = super(BsgPortFuelCar,self).write(vals)
		tracked_fields = self.env['bsg.port.fuel.car'].fields_get(vals)
		changes, tracking_value_ids = self._message_track(tracked_fields, old_values)
		if changes:
			self.fuel_trip_config_id.message_post(tracking_value_ids=tracking_value_ids)
			return res