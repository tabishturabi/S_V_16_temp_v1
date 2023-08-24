# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError,ValidationError

class bsg_car_size(models.Model):
	_name = 'bsg_car_size'
	_inherit = ['mail.thread']
	_description = "Car Size"
	_rec_name = "car_size_name"

	car_size_name = fields.Char()
	car_size_len = fields.Integer(string="Length")
	car_size_width = fields.Integer(string="Width")
	car_size_height = fields.Integer(string="Height")
	trailer_capcity = fields.Integer(string="Aquiring Capacity", help="This is the capacity that this size will aquire on trailer", required=True, default="1")
	car_size_old_id = fields.Integer(
		string='Car Old Id',
	)
	weight = fields.Integer("Weight", required=True)
	capacity_per_load = fields.Float(string='Capacity %')
	active = fields.Boolean(string="Active", tracking=True, default=True)

	_sql_constraints = [
	('value_car_size_name_uniq', 'unique (car_size_name)', 'This Car Size already exists !')
	]
	
	
	@api.constrains('capacity_per_load')
	def _check_value(self):
		warning_obj=self.env['bsg.warning.error'].get_warning('0001')
		if self.capacity_per_load > 100 or self.capacity_per_load < 0:
			raise UserError(warning_obj %(self.capacity_per_load))

		
	
	@api.constrains('trailer_capcity')
	def _check_trailer_capcity(self):
		warning_obj=self.env['bsg.warning.error'].get_warning('0002')
		for order in self:
			if order.trailer_capcity <= 0:
				raise UserError(warning_obj %(order.trailer_capcity ))

	
	@api.constrains('car_size_len','car_size_width','car_size_height')
	def _check_negative_values(self):
		if (self.car_size_len or self.car_size_width or self.car_size_height) < 0:
			raise UserError(_('Values must be greater then 0.'))

	
	def unlink(self):
		# cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line'].search([('car_size','=',self.id)])
		bsg_car_model = self.env['bsg_car_line'].search([('car_size','=',self.id)])
		if bsg_car_model:
			raise UserError(
				_('Sorry you cant delete this record as it is already in used by some other records'),
				)
		result = super(bsg_car_size, self).unlink()
		return result
