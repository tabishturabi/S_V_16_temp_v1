# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ChangeSoLine(models.TransientModel):

	_name = "cange_so_line_state"
	_description = "Change Sale Order Line State"

	cargo_sale_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line',string="Cargo Sale Line")
	sms_sent = fields.Boolean(related="cargo_sale_line_id.sms_sent")
	cargo_sale_state = fields.Selection(related="cargo_sale_line_id.state")
	cargo_sale_new_state = fields.Selection([('draft', 'Draft'),
			('confirm', 'Confirm'),
			('awaiting', 'Awaiting Return'),
			('shipped', 'Shipped'),
			('on_transit', 'On Transit'),
			('Delivered', 'Delivered On Branch'),
			('done', 'Done'),
			('released', 'Released'),
			('cancel', 'Declined')])
	is_show_pick = fields.Boolean(string="IS Show Pickup Location..?")
	pickup_loc = fields.Many2one(string="Pickup Location", comodel_name="bsg_route_waypoints",track_visibility=True,)
	drop_loc = fields.Many2one(string="Drop", comodel_name="bsg_route_waypoints", track_visibility=True,)
	delivery_date = fields.Datetime(string='Delivery Date')
	send_sms = fields.Boolean('Send SMS?')

	@api.onchange('cargo_sale_new_state')
	def onchange_cargo_sale_state(self):
		if self.cargo_sale_new_state and self.cargo_sale_new_state == 'on_transit':
			self.is_show_pick = True

	
	def update_state(self):
		if self.cargo_sale_new_state == 'on_transit':
			self.env['bsg.sale.line.trip.history'].create({'cargo_sale_line_id' : self.cargo_sale_line_id.id,
															'fleet_trip_id' : self.cargo_sale_line_id.fleet_trip_id.id})
			return self.cargo_sale_line_id.write({'state' : self.cargo_sale_new_state,
												  'pickup_loc' : self.pickup_loc.id,
												  'drop_loc' : self.drop_loc.id,
												  'fleet_trip_id' : False,
												  'added_to_trip' : False})
		elif self.cargo_sale_new_state == 'Delivered':
			self.cargo_sale_line_id.write({'state' : self.cargo_sale_new_state,
												  'delivery_date' :  self.delivery_date,
													})
			self.cargo_sale_line_id.calculating_demurrage_cost()
			if self.send_sms and not self.sms_sent:
				self.cargo_sale_line_id.send_delivery_sms()
			else:
				#so sms won't be sent by cron_send_sms()  
				self.cargo_sale_line_id.sms_sent = True
			return True
		else:
			return self.cargo_sale_line_id.write({'state' : self.cargo_sale_new_state,
												  'delivery_date' :  self.delivery_date,
													})
