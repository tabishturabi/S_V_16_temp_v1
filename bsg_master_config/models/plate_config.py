# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class bsg_plate_config(models.Model):
	_name = 'bsg_plate_config'
	_description = "Plate Config"
	_inherit = ['mail.thread']
	_rec_name = "plate_config_name"

	plate_config_name = fields.Char()
	plate_config_name_en = fields.Char()
	active = fields.Boolean(string="Active", tracking=True, default=True)
	
	_sql_constraints = [
	('value_plate_config_name_uniq', 'unique (plate_config_name)', 'This record already exists !')
	]


	
	def unlink(self):
		search_id = self.env['bsg_vehicle_cargo_sale_line'].search([('plate_type','=',self.id)])
		if search_id:
			raise UserError(_('You cannot Delete these Record is still Refrence'))
		result = super(bsg_plate_config, self).unlink()
		return result

