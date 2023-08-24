# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountConfiguration(models.Model):
	_name = 'account.fuel.trip.configuration'
	_description = "Account Fuel Trip Configuration"

	name = fields.Char(string="Name")
	fuel_expense_account_id = fields.Many2one(comodel_name="account.account", string="Fuel Account")
	fuel_expense_analytical_account_id = fields.Many2one(comodel_name="account.analytic.account", string="Fuel Analytic Account")
	trip_account = fields.Many2one(comodel_name="account.account", string="Trip Account")
	trip_analytical_account_id = fields.Many2one(comodel_name="account.analytic.account", string="Fuel Analytic Account")