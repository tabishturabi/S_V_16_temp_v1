# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class AccountConfiguration(models.Model):
	_name = 'cargo_sale_order_config'
	_description = "Cargo Sale Order Configuration"

	name = fields.Float(string=" Specific period to update SO state to cancel")
	ar_message = fields.Char('Arabic Message')
	en_message = fields.Char('English Message')
	show = fields.Boolean("Show",default=False)
