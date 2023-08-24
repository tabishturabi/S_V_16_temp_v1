# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class CancelSOLine(models.TransientModel):
	_name = "declined_petty_cash_request"
	_description = "Declined Petty Cash Request"

	petty_cash_id = fields.Many2one('petty.cash.expense.accounting',string="Cargo Sale")
	reject_reason = fields.Text(string="Reject Reason")

	#for Reject Petty Cash Request

	def reject_petty_cash_request(self):
		return self.petty_cash_id.write({'state' : 'declined',
										'reject_reason' : self.reject_reason,
										'is_reject' : True})			
