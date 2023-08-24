# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp

class SupportTeamCargoSaleLinePriceUpdate(models.Model):
	_name = 'support_team_cahange_so_line_price'
	_description = "Support Team Change Cargo Sale Line Price"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = "cargo_sale_line_id"

	cargo_sale_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line',string="Cargo Sale ID", track_visibility="onchange")
	charges = fields.Float(related="cargo_sale_line_id.charges")
	updated_charges = fields.Float(string="Updated Price", track_visibility="onchange")
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')], string='Status', track_visibility=True, default='draft')

	
	def update_price(self):
		if self.cargo_sale_line_id and self.updated_charges:
			self.cargo_sale_line_id.charges = self.updated_charges
			self.cargo_sale_line_id.bsg_cargo_sale_id._amount_all()