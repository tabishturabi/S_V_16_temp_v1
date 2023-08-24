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

class VoucherBranchesbassami(models.TransientModel):
	_name = "branchesvouchers.report.bassami"
	_inherit = 'report.report_xlsx.abstract'

	form = fields.Date(string="From",required=True)
	to = fields.Date(string="To",required=True)
	branch_ids = fields.Many2many('bsg_branches.bsg_branches',string="Branch",required=True)
	report_type = fields.Selection(string="Report Type",default="all", selection=[
		('all','All'),  
		('rec','Receipts'),    
		('pay','Payments'),    
		('trans','Transfers'),  
	],required=True)
	
	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['form','to','branch_ids','report_type'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['form','to','branch_ids','report_type'])[0])
		return self.env.ref('bassami_branches_vouchers_report.report_for_branches_voucher_records').report_action(self, data=data)

	# @api.multi
	def print_report_xlsx(self):
		
		all_recs = self.env['account.payment'].search([],limit=1)

		if all_recs:
			self.ensure_one()
			[data] = self.read()
			datas = {
				'ids': [],
				'model': 'account.payment',
				'form': data,
			}
			
			report = self.env['ir.actions.report']. \
				_get_report_from_name('bassami_branches_vouchers_report.voucher_report_xlsx')

			report.report_file = self._get_report_base_filename()
			report = self.env.ref('bassami_branches_vouchers_report.action_branches_voucher_report').report_action(all_recs, data=datas)
			return report
		else:
			raise UserError(_('There is no record in given date'))

	# @api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "Branches Voucher Report"
		return name