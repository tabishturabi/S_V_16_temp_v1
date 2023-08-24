# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BsgIntFuelAmount(models.Model):
	_name = 'bsg.int.fuel.amount'
	_description = "International Fuel Amount"
	_inherit = ['mail.thread']
	_rec_name = "int_route_id"

	active = fields.Boolean(string="Active", track_visibility=True, default=True)
	amount = fields.Float(string='Amount')
	int_route_id = fields.Many2one('bsg_route',string='Int Route ID')

	_sql_constraints = [
		('int_route_id_uniq', 'unique (int_route_id)', _('Same route can not have different prices! !')),
	]

	# 
	@api.constrains('amount')
	def _check_negative_values(self):
		if self.amount <= 0:
			raise UserError(_('Price must be non-negative or zero.'))
