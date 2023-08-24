# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp

class bsg_inherit_fleet_vehicle(models.Model):
	_inherit = 'fleet.vehicle'

	current_branch_id = fields.Many2one('bsg_branches.bsg_branches',string='Current Branch', track_visibility="onchange")

class SupportTeamFleetVehicle(models.Model):
	_name = 'support_team_fleet_vehicle_change_branch'
	_description = "Support Team Fleet Vehicle Change Branch"
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Many2one('fleet.vehicle',string="Vehicle ID", track_visibility="onchange")
	current_branch_id = fields.Many2one('bsg_branches.bsg_branches',string="Current Branch",  track_visibility="onchange")
	new_branch_id = fields.Many2one('bsg_branches.bsg_branches',string="New Branch", track_visibility="onchange")
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')], string='Status', track_visibility=True, default='draft')

	
	@api.onchange('name')
	def _onchange_parent_id(self):
		for data in self:
			data.current_branch_id = data.name.current_branch_id.id

	
	def cahnge_branch(self):
		self.name.write({'current_branch_id' : self.new_branch_id.id})
		self.state = 'confirmed'

	@api.model
	def create(self, vals):
		res = super(SupportTeamFleetVehicle, self).create(vals)
		res._onchange_parent_id()
		return res

	
	def write(self, vals):
		if vals.get('name'):
			vehicle_id = self.env['fleet.vehicle'].browse(vals.get('name'))
			vals['current_branch_id'] = vehicle_id.current_branch_id.id
		res = super(SupportTeamFleetVehicle, self).write(vals)
		return res