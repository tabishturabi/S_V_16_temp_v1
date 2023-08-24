# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class bsg_car_config(models.Model):
	_name = 'bsg_car_config'
	_description = "Car Model"
	_inherit = ['mail.thread']
	_rec_name="car_maker"

	car_maker = fields.Many2one(string="Car Maker", comodel_name="bsg_car_make")
	active = fields.Boolean(string="Active", tracking=True, default=True)
	visible_on_mobile_app = fields.Boolean('Visible On Mobile App')
	visible_for_subcontract_api = fields.Boolean('Visible On Contract App')
	car_line_ids = fields.One2many(string="car_line_ids", comodel_name="bsg_car_line", inverse_name="car_config_id")
	_sql_constraints = [
	('value_car_maker_uniq', 'unique (car_maker)', 'This Car Model already exists !')
	]

	# 
	# def unlink(self):
	# 	cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line'].search([('car_make','=',self.id)])
	# 	if cargo_sale_line:
	# 		raise UserError(
	# 			_('Sorry you cant delete this record as it is already in used by some other records'),
	# 			)
	# 	result = super(bsg_car_config, self).unlink()
	# 	return result
# car lines

class bsg_car_line(models.Model):
	_name = 'bsg_car_line'
	_description = "Car Lines"
	_inherit = ['mail.thread']

	active = fields.Boolean(string="Active", tracking=True, default=True)
	car_config_id = fields.Many2one(string="Car Config ", comodel_name="bsg_car_config")
	sequence = fields.Integer(string="Sr No")
	car_size = fields.Many2one(string="Car Size", comodel_name="bsg_car_size", required=True)
	car_model = fields.Many2one('bsg_car_model', string="Model", required=True)
	car_classfication = fields.Many2one('bsg_car_classfication', string="Classification", required=True)
	car_line_len = fields.Integer(string="Length")
	car_line_width = fields.Integer(string="Width")
	car_line_height = fields.Integer(string="Height")


	# _sql_constraints = [
	# ('value_bsg_car_line_unique', 'unique (car_size, car_classfication)', 'This record already exists !')
	# ]

	
	def unlink(self):
		search_id = self.env['bsg_vehicle_cargo_sale_line'].search([('car_size','=',self.car_size.id),('car_classfication','=',self.car_classfication.id),('car_model','=',self.car_model.id)])
		if search_id:
			raise UserError(_('You cannot Delete these Record is still Refrence'))
		result = super(bsg_car_line, self).unlink()
		return result




class bsg_car_model(models.Model):
	_name = 'bsg_car_model'
	_description = "Car Model"
	_inherit = ['mail.thread']
	_rec_name = 'car_model_name'

	car_model_name = fields.Char(string="Arabic Name")
	car_model_en_name = fields.Char('English Name')
	car_maker_id = fields.Many2one("bsg_car_make", string="Car Maker")
	car_model_old_sys_id = fields.Integer("Model Old Sys Id")
	active = fields.Boolean(string="Active", tracking=True, default=True)

	
	@api.constrains('car_model_name')
	def _check_car_model_name(self):
		if self.car_model_name:
			car_model = self.env['bsg_car_model'].search([('car_model_name','=',self.car_model_name),('car_maker_id','=',self.car_maker_id.id)])
			if len(car_model)>1:
				raise UserError(_('This record already exists !'))