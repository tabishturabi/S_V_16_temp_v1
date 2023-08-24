# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class accountMoveLine(models.Model):
	_inherit = 'account.move.line'

	ext_department = fields.Many2one('account.analytic.account',string="Branch")

	@api.model
	def create(self, vals):
		invoice = self._context.get('invoice')
		if invoice and invoice.analytic_distribution:
			vals.update({
				'analytic_distribution':invoice.analytic_distribution.id,
				# setting ext_department here and removing compute method
				'ext_department':invoice.account_analytic_id.parent_id.id 
				})
		return super(accountMoveLine, self).create(vals)
