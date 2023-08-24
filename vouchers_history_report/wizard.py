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

class VoucherHistorybassami(models.TransientModel):
	_name = "voucher.history.report"

	form = fields.Date(string="From",required=True)
	to = fields.Date(string="To",required=True)
	branch_ids = fields.Many2many('bsg_branches.bsg_branches',string="Branch",required=True)
	report_type = fields.Selection(string="Report Type",default="all", selection=[
		('all','All'),  
		('rec','Receipts'),    
		('pay','Payments'),    
		('trans','Transfers'),  
	],required=True)
	branch_filter = fields.Selection(string="Branch Filter",default="all", selection=[
		('all','All'),  
		('specific','Specific'),      
	],required=True)
	
	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['form','to','branch_ids','report_type','branch_filter'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['form','to','branch_ids','report_type','branch_filter'])[0])
		return self.env.ref('vouchers_history_report.report_for_vouchers_history').report_action(self, data=data)

	