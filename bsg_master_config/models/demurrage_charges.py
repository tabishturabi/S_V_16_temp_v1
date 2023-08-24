# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class DemurrageChargesConfig(models.Model):
	_name = 'demurrage_charges_config'
	_inherit = ['mail.thread']
	_description = "Demurrage Charges"
	_rec_name = "chares"

	
	def _get_total_day(self):
		for rec in self:
			rec.total_day = (rec.ending_day_no - rec.starting_day_no) + 1

	car_size_ids = fields.Many2many('bsg_car_size', string='Car Size')
	starting_day_no = fields.Integer(string="Starting Day", required=True)
	ending_day_no = fields.Integer(string="Ending Day", required=True)
	total_day = fields.Integer(string="Total Day", compute="_get_total_day")
	chares = fields.Float(string="Charge")
	currency_id = fields.Many2one('res.currency',string="Currency",default=lambda self: self.env.user.company_id.currency_id.id)

	# _sql_constraints = [
	# ('no_of_days_demurage_uniq', 'unique (starting_day_no, ending_day_no, chares)', 'This record already exists !')
	# ]

	
	@api.constrains('starting_day_no','ending_day_no','chares')
	def _check_negative_values(self):
		if self.starting_day_no <= 0:
			raise UserError(_('Starting day no must be non-negative.'))
		
		if self.ending_day_no <= 0:
			raise UserError(_('Ending day no must be non-negative.'))

		if self.chares < 0:
			raise UserError(_('Charges must be non-negative.'))

		if self.starting_day_no > self.ending_day_no:
			raise UserError(_('Starting Day should be less then Ending day.'))