# -*- coding: utf-8 -*-
import re
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class bsg_car_year(models.Model):
	_name = 'bsg.car.year'
	_description = "Car Year"
	_inherit = ['mail.thread']
	_rec_name = "car_year_name"

	car_year_name = fields.Char()
	active = fields.Boolean(string="Active", tracking=True, default=True)
	_sql_constraints = [
	('value_car_year_name_uniq', 'unique (car_year_name)', 'This Car Year already exists !')
	]

	
	@api.constrains('car_year_name')
	def _check_car_year_name(self):
		match = re.match(r'[1-2][0-9]{3}', self.car_year_name)
		if match is None or len(self.car_year_name) != 4:
			raise UserError(
				_('Car Year must be valid and it must be of 4 digits and non negative!'),
			)

	
	def unlink(self):
		cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line'].search([('year','=',self.id)])
		if cargo_sale_line:
			raise UserError(
				_('Sorry you cant delete this record as it is already in used by some other records'),
				)	
		result = super(bsg_car_year, self).unlink()
		return result