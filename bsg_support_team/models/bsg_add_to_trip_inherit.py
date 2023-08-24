# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class CargoSaleLineAddTrip(models.TransientModel):
	_inherit = 'cargo_sale_line_add_trip'

	#need to override for support team support
	@api.onchange('fleet_type')
	def _onchange_parent_id(self):
		id_list = []
		if self.fleet_type == 'from_to':
			search = self.env[self._context['active_model']].search([('id', 'in', self._context['active_ids'])],
																	limit=1)
			for data in self.env['fleet.trip.arrival'].search(
					[('waypoint_from', '=', search.loc_from.id), ('waypoint_to', '=', search.loc_to.id)]):
				id_list.append(data.trip_id.id)
			if self.env.user.has_group('bsg_trip_mgmt.group_create_trip_with_all_route_view'):
				return {
						'domain': {'fleet_trip_id': [('id', 'in', id_list), ('state', 'in', ['draft', 'on_transit', 'confirmed'])]}
						}
			elif self.env.user.has_group('bsg_support_team.group_add_so_line_to_a_trip'):
				return {
						'domain': {'fleet_trip_id': [('state', 'in', ['draft', 'progress', 'confirmed','finished'])]}#,('route_id.waypoint_from.loc_branch_id','=',self.env.user.user_branch_id.id),('create_uid','=',self.env.user.id)
						}
			else:
				return {
						'domain': {'fleet_trip_id': ['|',('route_id.waypoint_to_ids.waypoint.loc_branch_id','=',self.env.user.user_branch_id.id),('route_id.waypoint_from.loc_branch_id','=',self.env.user.user_branch_id.id),('state', 'in', ['draft', 'on_transit', 'confirmed']),('id', 'in', id_list)]}#('id', 'in', id_list),('route_id.waypoint_from.loc_branch_id','=',self.env.user.user_branch_id.id),('create_uid','=',self.env.user.id), 
						}				
		if self.fleet_type == 'all':
			search = self.env['fleet.vehicle.trip'].search([('state', 'in', ['draft', 'on_transit', 'confirmed'])])
			if self.env.user.has_group('bsg_trip_mgmt.group_create_trip_with_all_route_view'):
				return {
						'domain': {'fleet_trip_id': [('id', 'in', search.ids)]}
						}
			elif self.env.user.has_group('bsg_support_team.group_add_so_line_to_a_trip'):
				return {
						'domain': {'fleet_trip_id': [('state', 'in', ['draft', 'progress', 'confirmed','finished'])]}#,('route_id.waypoint_from.loc_branch_id','=',self.env.user.user_branch_id.id),('create_uid','=',self.env.user.id)
						}
			else:
				return {
						'domain': {'fleet_trip_id': ['|',('route_id.waypoint_to_ids.waypoint.loc_branch_id','=',self.env.user.user_branch_id.id),('route_id.waypoint_from.loc_branch_id','=',self.env.user.user_branch_id.id),('id', 'in', search.ids)]}#,('route_id.waypoint_from.loc_branch_id','=',self.env.user.user_branch_id.id),('create_uid','=',self.env.user.id)
						}