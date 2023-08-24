# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class bsg_vehicle_color(models.Model):
	_name = 'bsg_vehicle_color'
	_description = "Vehicle Color"
	_inherit = ['mail.thread']
	_rec_name = "vehicle_color_name"

	vehicle_color_name = fields.Char()
	vehicle_color_name_en = fields.Char()
	active = fields.Boolean(string="Active", tracking=True, default=True)

	_sql_constraints = [
	('value_vehicle_color_name_uniq', 'unique (vehicle_color_name)', 'This Car Color already exists !')
	]

	
	def unlink(self):
		cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line'].search([('car_color','=',self.id)])
		if cargo_sale_line:
			raise UserError(
				_('Sorry you cant delete this record as it is already in used by some other records'),
				)	
		result = super(bsg_vehicle_color, self).unlink()
		return result