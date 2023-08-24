# #-*- coding:utf-8 -*-

import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import api, models, fields
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
import string
import sys

class GenerateInvoiceLedgerbassami(models.TransientModel):
	_name = "invoice.ledger.bassami"


	partner_ids = fields.Many2one('res.partner',string="Customer")
	customer_ids = fields.Many2many('res.partner',string="Invoice To")
	date_from = fields.Date("Date From", required=True, default=time.strftime('%Y-01-01'))
	date_to = fields.Date("Date To", required=True)
	all_invoices = fields.Boolean(string="All Invoices")
	has_invoice = fields.Boolean(string="Has Invoice")


	@api.onchange('partner_ids')
	def onchange_invoice_to(self):
		if self.partner_ids:
			return {'domain': {
			'customer_ids': [('id', 'in', self.partner_ids.child_ids.ids)],
			}}

	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['partner_ids','date_from','date_to','customer_ids'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['partner_ids','date_from','date_to','customer_ids'])[0])
		return self.env.ref('bassami_statement_of_invoices.report_for_invoice_ledger').report_action(self, data=data)

	