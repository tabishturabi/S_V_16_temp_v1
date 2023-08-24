# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class CancelMultiSoLine(models.TransientModel):

	_name = "cancel.multi.so.line.record"
	_description = "Cancel Multi So Line"

	cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale',string="Cargo Sale",required=True)
	cargo_sale_line_ids = fields.Many2many('bsg_vehicle_cargo_sale_line',string="Cargo Sale Lines",required=True)

	#for canceling Multi so line
	
	def cancel_so_line(self):
		if self.cargo_sale_line_ids:
			for line in self.cargo_sale_line_ids:
				line.write({'state':'cancel'})
		if all(st == 'cancel' for st in self.cargo_sale_id.order_line_ids.mapped('state')):
			self.cargo_sale_id.write({'state' : 'cancel'})		
		self.cargo_sale_id._amount_all()