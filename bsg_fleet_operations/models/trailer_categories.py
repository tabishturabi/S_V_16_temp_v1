# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BsgTrailerCategories(models.Model):
	_name = 'bsg.trailer.categories'
	_description = "Trailer Categories"
	_inherit = ['mail.thread']
	_rec_name = "trailer_cat_id"

	trailer_cat_id = fields.Char(string="Trailer Categories ID")
	active = fields.Boolean(string="Active", track_visibility=True, default=True)
	trailer_cat_ar_name = fields.Char(string="Trailer Cat Ar Name")
	trailer_cat_er_name = fields.Char(string="Trailer Cat Er Name")