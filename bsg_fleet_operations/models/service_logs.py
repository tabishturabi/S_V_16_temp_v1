# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class TrailerServiceLog(models.Model):
	_name = 'trailer.service.log'
	_description = 'Trailer Service Log'
	_order = 'date desc, trailer_id asc'
	_inherit = ['mail.thread']


	@api.model
	def default_get(self, default_fields):
		res = super(TrailerServiceLog, self).default_get(default_fields)
		service = self.env.ref('fleet.type_service_service_8', raise_if_not_found=False)
		res.update({
			'date': fields.Date.context_today(self),
			'cost_subtype_id': service and service.id or False,
			'cost_type': 'services'
		})
		return res

	state = fields.Selection([
		('draft', 'Draft'),
		('maintenance', 'Maintenance'),
		('done', 'Done'),
		('cancel', 'Cancel'),
		], 'State', default="draft", track_visibility=True)

	trailer_id = fields.Many2one(
		'bsg_fleet_trailer_config',
		string='Trailer', track_visibility=True
	)
	name = fields.Char(related='trailer_id.trailer_config_name', string='Name', store=True, readonly=False, track_visibility=True)
	cost_subtype_id = fields.Many2one('fleet.service.type', 'Type', help='Cost type purchased with this cost', track_visibility=True)
	amount = fields.Float('Total Price')
	cost_type = fields.Selection([
		('contract', 'Contract'),
		('services', 'Services'),
		('fuel', 'Fuel'),
		('other', 'Other')
		], 'Category of the cost', default="other", help='For internal purpose only', required=True, track_visibility=True)
	# Migration Note
	# cost_ids = fields.One2many('fleet.vehicle.cost', 'parent_id', 'Included Services', copy=True, track_visibility=True)
	# cost_ids = fields.One2many('fleet.vehicle.cost.report', 'parent_id', 'Included Services', copy=True, track_visibility=True)
	date = fields.Date(help='Date when the cost has been executed', track_visibility=True)
	description = fields.Char("Cost Description", track_visibility=True)
	purchaser_id = fields.Many2one('res.partner', 'Purchaser', domain="['|',('customer_rank','>',0),('employee','=',True)]", track_visibility=True)
	inv_ref = fields.Char('Invoice Reference', track_visibility=True)
	vendor_id = fields.Many2one('res.partner', 'Vendor', domain="[('supplier_rank','>', 0)]", track_visibility=True)
	# we need to keep this field as a related with store=True because the graph view doesn't support
	# (1) to address fields from inherited table and (2) fields that aren't stored in database
	notes = fields.Text(track_visibility=True)

	# @api.multi
	def draft_btn(self):
		return self.write({'state': 'draft'})

	# @api.multi
	def maintenance_btn(self):
		if self.trailer_id:
			self.trailer_id.maintenance_btn()
		return self.write({'state': 'maintenance'})

	# @api.multi
	def done_btn(self):
		if self.trailer_id:
			self.trailer_id.unlinked_btn()
		return self.write({'state': 'done'})

	# @api.multi
	def cancel_btn(self):
		return self.write({'state': 'cancel'})

# Migration Note For cost_ids in trailer.service.log
# class FleetReportInherit(models.Model):
# 	_inherit = "fleet.vehicle.cost.report"
#
#
# 	parent_id = fields.Many2one('fleet.vehicle.cost.report',string='Parent', help='Parent cost to this current cost')

