# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ChangeSoCustomer(models.TransientModel):
	_name = "cange_so_customer"
	_description = "Change Sale Order Customer"

	cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale',string="Cargo Sale Line")
	partner_types = fields.Many2one("partner.type", string="Partner Type")
	cargo_sale_customer_id = fields.Many2one(string="Current Customer ID", comodel_name="res.partner", related="cargo_sale_id.customer")
	new_customer_id = fields.Many2one(string="New Customer ID", comodel_name="res.partner")

	
	def update_customer(self):
		return self.cargo_sale_id.write({'customer' : self.new_customer_id.id})