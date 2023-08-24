# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class bsg_car_classification(models.Model):
	_name = 'bsg_car_classfication'
	_inherit = ['mail.thread']
	_description = "Car Classfication"
	_rec_name = "car_class_name"

	car_class_name = fields.Char()
	active = fields.Boolean(string="Active", tracking=True, default=True)

	_sql_constraints = [
	('value_bsg_car_classfication_car_class_name_uniq', 'unique(car_class_name)', 'This record already exists !')
	]

	# 
	# def unlink(self):
	# 	cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line'].search([('car_classfication','=',self.id)])
	# 	bsg_price_line = self.env['bsg_price_line'].search([('car_classfication','=',self.id)])
	# 	bsg_car_model = self.env['bsg_car_line'].search([('car_classfication','=',self.id)])
	# 	if cargo_sale_line:
	# 		raise UserError(
	# 			_('Sorry you cant delete this record as it is already in used by some other records'),
	# 			)	
