# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class CancelSOLine(models.TransientModel):

	_name = "cancel_so_line_record"
	_description = "Cancel So Line"

	cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale',string="Cargo Sale")
	shipment_type = fields.Selection(string="Shipment Type", related="cargo_sale_id.shipment_type")
	single_trip_reason = fields.Many2one('single.trip.cancel', 'One Way Reason')
	round_trip_reason = fields.Many2one('round.trip.cancel', 'Round Trip Vehicale')

	#for canceling so line
	
	def cancel_so_line(self):
		search_id = self.env['bsg_vehicle_cargo_sale_line'].search([('id','=',self._context.get('default_id'))])
		if self.single_trip_reason:
			search_id.write({'single_trip_reason' : self.single_trip_reason.id})
		if self.round_trip_reason:
			search_id.write({'round_trip_reason' : self.round_trip_reason.id})			
		return search_id.cancel_so_line_state_from_wizard()