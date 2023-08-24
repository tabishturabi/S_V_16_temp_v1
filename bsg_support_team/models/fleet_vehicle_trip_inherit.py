# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import _, api, fields, models


# fleet.vehicle.trip
class FleetVehicrleTrip(models.Model):
	_inherit = 'fleet.vehicle.trip'

	
	def change_state(self):
		data = {'default_trip_id' : self.id}
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'cange_fleet_trip_line_state',
			'view_id'   :  self.env.ref('bsg_support_team.cange_fleet_trip_line_state_form').id,
			'view_mode': 'form',
			# 'view_type': 'form',
			'context' : data,
			'target': 'new',
		}
