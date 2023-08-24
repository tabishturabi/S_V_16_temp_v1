# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp

class SupportTeamLinkDriver(models.Model):
	_name = 'support_team_fleet_change_driver'
	_description = "Support Team Link Driver"
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Many2one('fleet.vehicle',string="Vehicle ID", track_visibility="onchange")
	bsg_driver = fields.Many2one(string="Current Vehicle Driver", comodel_name="hr.employee", track_visibility="onchange")
	new_bsg_driver = fields.Many2one(string="New Vehicle Driver", comodel_name="hr.employee", track_visibility="onchange")
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')], string='Status', track_visibility=True, default='draft')

	
	@api.onchange('name')
	def _onchange_parent_id(self):
		for data in self:
			data.bsg_driver = data.name.bsg_driver.id

	
	def cahnge_driver(self):
		self.name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).write({'bsg_driver' : self.new_bsg_driver.id})
		self.name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).link_driver()
		self.state = 'confirmed'

	@api.model
	def create(self, vals):
		res = super(SupportTeamLinkDriver, self).create(vals)
		res._onchange_parent_id()
		return res

	
	def write(self, vals):
		if vals.get('name'):
			vehicle_id = self.env['fleet.vehicle'].browse(vals.get('name'))
			vals['bsg_driver'] = vehicle_id.bsg_driver.id
		res = super(SupportTeamLinkDriver, self).write(vals)
		return res