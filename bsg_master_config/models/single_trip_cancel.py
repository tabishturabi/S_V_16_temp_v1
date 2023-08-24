# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class SingleTripCancel(models.Model):
	_name = 'single.trip.cancel'
	_inherit = ['mail.thread']
	_description = "Single Trip Cancel"
	_rec_name = "stc_reason_name"

	active = fields.Boolean(string="Active", tracking=True, default=True)
	stc_reason_name = fields.Char()
	stc_reason_type = fields.Selection(string="Reason Type", selection=[
		('fixed','Fixed Amount'),
		('percentage','Percentage'),
		('na','N/A')
	], default="")
	stc_value = fields.Float(string='Value')
	stc_account_id = fields.Many2one('account.account',string='Account ID')
	is_cancel = fields.Boolean(string="Is Cancel")
	tax_ids = fields.Many2many('account.tax',
        string='Taxes', domain=[('type_tax_use','=','sale'), '|', ('active', '=', False), ('active', '=', True)])

