# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ChangeFleetState(models.TransientModel):

	_name = "cange_fleet_trip_line_state"
	_description = "Change Fleet Trip State"

	trip_id = fields.Many2one('fleet.vehicle.trip',string="Trip ID")
	trip_state = fields.Selection(related="trip_id.state")
	trip_new_state = fields.Selection(selection=[
		('draft', 'Draft'),
		('on_transit', 'On Transit'),
		('confirmed', 'Confirmed'),
		('progress', 'In Operation'),
		('done', 'Done'),
		('finished', 'Finished'),
		('cancelled', 'Cancelled')])

	
	def update_state(self):
		return self.trip_id.write({'state' : self.trip_new_state})