# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductProduct(models.Model):
	_inherit = 'product.template'

	is_fuel_expense = fields.Boolean("Is Fuel expense")
	is_driver_reward = fields.Boolean("Is Driver Rewards")