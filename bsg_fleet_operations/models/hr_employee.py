# -*- coding: utf-8 -*-

import re
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class bsg_inherit_hr_employee(models.Model):
	_inherit = 'hr.employee'

	is_driver = fields.Boolean(string="Is Driver ?")
	is_technician = fields.Boolean(string="Is Technician ?")
	driver_code = fields.Char(
		string='Employee ID',
	)
	vehicle_sticker_no = fields.Char(
		 string='Vehicle Sticker No',
	 )
	
	@api.constrains('driver_code')
	def check_driver_code(self):
		if self.driver_code:
		    driver_id = self.env['hr.employee'].search([('driver_code','=',self.driver_code),('id','!=',self.id)])
		    if driver_id:
		        raise UserError(_("Your Entered Employee ID is already taken by another user"))
	
	# Validate the identification no or iqama 2 means non-saudi as regex is checking 
	# 
	@api.constrains('identification_id')
	def _validate_identification_id(self):
		if self.identification_id:
			match = re.match(r'2[0-9]{9}', self.identification_id)
			if match is None or len(str(self.identification_id)) != 10:
				raise UserError(
					_('Iqama ID no must be start from 2 and must have 10 digits.'),
				)