# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class bsg_car_make(models.Model):
	_name = 'bsg_car_make'
	_description = "Car Make"
	_inherit = ['mail.thread']
	_rec_name ="car_make_ar_name"

	car_make_name = fields.Char()
	car_make_ar_name = fields.Char("Arabic Name")
	car_make_old_sys_id = fields.Integer("Maker Old Sys Id")
	active = fields.Boolean(string="Active", tracking=True, default=True)

	_sql_constraints = [
	('value_car_make_name_uniq', 'unique (car_make_name)', 'This Car Maker already exists !')
	]

	
	def unlink(self):
		bsg_car_config = self.env['bsg_car_config'].search([('car_maker','=',self.id)])
		if bsg_car_config:
			raise UserError(
				_('Sorry you cant delete this record as it is already in used by some other records'),
				)
		result = super(bsg_car_make, self).unlink()
		return result