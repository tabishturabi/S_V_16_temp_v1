# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BsgFuelExpenseMethod(models.Model):
	_name = 'bsg.fuel.expense.method'
	_description = "Fuel Expense Method"
	_inherit = ['mail.thread']
	_rec_name = "vehicle_type"

	method_name = fields.Char(string='Method Name', compute="_compute_rec_name")
	active = fields.Boolean(string="Active", default=True,track_visibility='onchange')
	# fuel_expense_type this field must have same options as route_type in bsg_master_config/models/route.py
	
	el_reward = fields.Float( string='EL Reward', digits = (12,3))
	fl_reward = fields.Float( string='FL Reward' , digits = (12,3))
	nel_reward = fields.Float( string='nEL Reward', digits = (12,3))
	nfl_reward = fields.Float( string='nFL Reward' , digits = (12,3))
	
	fuel_expense_type = fields.Selection([
		('km','Per KM'),
		('route','Route'),
		('local','Local'),
		('port','Port'),
		('hybrid', 'Hybrid')], string="Fuel Expense Method"
		,track_visibility='onchange')
	trailer_category_id = fields.Many2one('bsg.trailer.categories', string='Trailer Category',track_visibility='onchange')
	vehicle_type = fields.Many2one('bsg.vehicle.type.table', string='Vehicle Type' ,track_visibility='onchange')
	empty_load_amt = fields.Float( string='EL Fuel Amt', digits = (12,3),track_visibility='onchange')
	full_load_amt = fields.Float( string='FL Fuel Amt' , digits = (12,3),track_visibility='onchange')
	amt_empty_without_reward = fields.Float( string='nEL Fuel Amt', digits = (12,3),track_visibility='onchange')
	amt_full_without_reward = fields.Float( string='nFL Fuel Amt' , digits = (12,3),track_visibility='onchange')
	int_fuel_amt_id = fields.Many2one('bsg.int.fuel.amount', string='Int Fuel Amount ID',track_visibility='onchange')
	port_fuel_amt_id = fields.Many2one('bsg.port.fuel.amount', string='Port Fuel Amount',track_visibility='onchange')
	fuel_amount = fields.Float(stirng="Fuel Amount", compute="_compute_fuel_amt",track_visibility='onchange')
	route_type = fields.Selection([
	('km','Domestic'),
	('route','International'),
	('port','Port'),
	('local','Local'),
	('hybrid','Hybrid Route'),
	], string="Route Type", help='This is to determine if the route is international/domestic or between ports',track_visibility='onchange' 
	)
	port_rule_option = fields.Selection(string="Port Fuel Rule Per", selection=[
		('trip', 'Trip'),
		('car', 'Car'),
		('na', 'Not Applicable'),

	], track_visibility=True,)
	route_id = fields.Many2one('bsg_route',string="Route",track_visibility='onchange')
	expense_amount = fields.Float(string="Expense Amount",track_visibility='onchange')


	@api.constrains('vehicle_type','fuel_expense_type','route_type','route_id')
	def cehck_constaint(self):
		if self.vehicle_type and self.fuel_expense_type and self.route_type and self.route_id:
			search_id = self.search([('route_id','=',self.route_id.id),('vehicle_type','=',self.vehicle_type.id),('route_type','=',self.route_type),('fuel_expense_type','=',self.fuel_expense_type),('id','!=',self.id)])
			if search_id:
				raise UserError(_("Vehicle Type,Fuel Expense Method,Route Type,Route Should be Unique...!"))
	
	# 
	@api.constrains('full_load_amt')
	def _check_negative_values(self):
		if self.fuel_expense_type == 'km':
			if self.full_load_amt < 0:
				raise UserError(_('Price must be non-negative or zero.'))

	# 
	@api.depends('int_fuel_amt_id','port_fuel_amt_id')
	def _compute_fuel_amt(self):
		self.fuel_amount = 0
		if self.port_fuel_amt_id:
			self.fuel_amount = self.port_fuel_amt_id.rule_amount
		if self.int_fuel_amt_id:
			self.fuel_amount = self.int_fuel_amt_id.amount

	# 
	@api.depends('fuel_expense_type','trailer_category_id')
	def _compute_rec_name(self):
		if self.fuel_expense_type and self.trailer_category_id:
			if self.trailer_category_id.trailer_cat_ar_name:
				self.method_name = self.fuel_expense_type +" / "+self.trailer_category_id.trailer_cat_id +" / "+ self.trailer_category_id.trailer_cat_ar_name
			else:
				self.method_name = self.fuel_expense_type +" / "+self.trailer_category_id.trailer_cat_id
				
	@api.onchange('fuel_expense_type')
	def _onchange_fuel_expense_type(self):
		if self.fuel_expense_type:
			self.int_fuel_amt_id = False
			self.port_fuel_amt_id = False

	        
