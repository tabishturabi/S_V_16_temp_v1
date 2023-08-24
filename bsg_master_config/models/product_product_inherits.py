# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductProduct(models.Model):
	_inherit = 'product.template'

	is_international = fields.Boolean("Is International")
	is_demurrage = fields.Boolean("Is Demurrage")