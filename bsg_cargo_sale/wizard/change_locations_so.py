# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

class ChangeSOLocations(models.TransientModel):

	_name = "change_so_locations"
	_description = "Change Retrun Location"

	msg = fields.Char(string='Message')
	return_loc_to = fields.Boolean(string="To")
	new_ret_loc_to = fields.Many2one(string="To", comodel_name="bsg_route_waypoints")
	loc_to_id = fields.Many2one('bsg_route_waypoints', 'current loc to')
	sale_line_ids = fields.Many2many('bsg_vehicle_cargo_sale_line', string='Sale Order lines')

	@api.onchange('loc_to_id')
	def set_new_ret_loc_to_domain(self):
		if self.loc_to_id:
			return {'domain': {'new_ret_loc_to': [('id', 'in', self.loc_to_id.allowed_return_waypoint_ids.ids),
								('branch_type','in',['pickup','both']),('id','!=',self.loc_to_id.id)]
			}}

	
	def update_locations(self):
		if not self.sale_line_ids:
			raise ValidationError(_("You must select at least one Sale Line.")) 
		search_id = self.env['bsg_vehicle_cargo_sale'].search([('id','=',self._context.get('sale_id'))])
		if self.new_ret_loc_to:
			search_id.write({'return_loc_to' : self.new_ret_loc_to.id,})
		return search_id.with_context({'new_ret_loc_to': self.new_ret_loc_to.id, 'sale_line_ids': self.sale_line_ids.ids}).start_return_process()
