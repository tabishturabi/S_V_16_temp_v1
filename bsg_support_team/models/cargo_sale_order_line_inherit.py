# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import _, api, fields, models


# Cargo Sale Order Line
class bsg_vehicle_cargo_sale_line(models.Model):
	_inherit = 'bsg_vehicle_cargo_sale_line'

	def _get_user_access(self):	
		if self.env.user.has_group('bsg_support_team.group_update_so_line'):
			self.is_support_team = True
		else:
			self.is_support_team = False

	is_support_team = fields.Boolean(string="Is Support Team", compute="_get_user_access")

	
	def change_state(self):
		data = {'default_cargo_sale_line_id' : self.id}
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'cange_so_line_state',
			'view_id'   :  self.env.ref('bsg_support_team.cange_so_line_state_form').id,
			'view_mode': 'form',
			# 'view_type': 'form',
			'context' : data,
			'target': 'new',
		}

	
	def update_so_line_related_fields(self):
		for line in self:
			line.loc_from = line.bsg_cargo_sale_id.loc_from
			line.loc_to =  line.bsg_cargo_sale_id.loc_to
			line.customer_id = line.bsg_cargo_sale_id.customer
			line.order_date = line.bsg_cargo_sale_id.order_date
		cargo_sale_id = self[0].bsg_cargo_sale_id
		cargo_sale_id._amount_all()
		cargo_sale_id._amount_so_all()
		if 	cargo_sale_id.state != 'draft' and cargo_sale_id.name.__contains__('*'):
			name = str(cargo_sale_id.loc_from.loc_branch_id.branch_no) + \
			self.env['ir.sequence'].with_context(force_company=self.env.user.company_id.id).next_by_code('bsg_vehicle_cargo_sale')
			if cargo_sale_id.is_return_so:
				cargo_sale_id.name = 'R'+name
				cargo_sale_id._reset_sequence()
			else:
				cargo_sale_id.name = name
				cargo_sale_id._reset_sequence()
