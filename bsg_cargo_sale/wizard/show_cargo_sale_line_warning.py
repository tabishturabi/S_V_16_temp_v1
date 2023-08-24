# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class CargoSaleLineWarning(models.TransientModel):

	_name = "change_cargo_sale_line_warning"
	_description = "Change Cargo Sale Line Warning"

	msg = fields.Char(string='Message')


	
	def create_invoice(self):
		cargo_sale_id = self.env['bsg_vehicle_cargo_sale_line'].search([('id','=',self._context.get('default_id'))])
		return cargo_sale_id.validate_invoice_from_wizard()