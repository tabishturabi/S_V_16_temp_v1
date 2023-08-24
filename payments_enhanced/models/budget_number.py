# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BudgetNumber(models.TransientModel):
	_name = 'budget_voucher_number'
	_description = "Budget Voucher Number"

	name = fields.Char(string="Budget Number")

	# @api.multi
	def add_budget_number(self):
		for data in self._context.get('active_ids'):
			payment_id = self.env['account.payment'].browse(data)
			if payment_id.partner_type == 'customer':
				payment_id.write({'budget_number' : self.name})
			else:
				raise UserError(_('Only Receipt Vouchers Have Budget Number'))
