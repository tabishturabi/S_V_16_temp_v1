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

class VoucherLedgerbassami(models.TransientModel):
	_name = "vouchers.report.bassami"

	form = fields.Date(string="From",required=True)
	to = fields.Date(string="To",required=True)
	# branch_ids = fields.Many2many('bsg_branches.bsg_branches',string="Branch")
	journal_id = fields.Many2one('account.journal',string="Journal")
	user_id = fields.Many2many('res.users',string="User")
	report_type = fields.Selection(string="Report Type",default="all", selection=[
		('all','All'),  
		('rec','Receipts'),    
		('pay','Payments'),    
		('trans','Transfers'),  
	],required=True)
	state = fields.Selection(string="State",default="all", selection=[
		('all','All'),  
		('draft','Draft'),    
		('voucher','Voucher'),    
		('posted','Posted'),  
	],required=True)

	user_type = fields.Selection(string="User Type",default="all", selection=[
		('all','All'),    
		('specific','Specific'), 
	])


	@api.onchange('form','to')
	def get_journal_ids(self):
		branches = []
		curr_users = self.env['res.users'].search([('id','=',self._uid)])
		for b in curr_users.user_branch_id:
			branches.append(b)

		journals = []
		for chk in branches:
			journal_data = self.env['account.journal'].search([])
			for j in journal_data:
				if chk in j.branches:
					journals.append(j.id)

			domain = {'journal_id': [('id', 'in', journals)]}
			return {'domain': domain, 'value': {'journal_id': []}}
			

	@api.onchange('user_type')
	def get_user_ids(self):
		branches = []
		curr_users = self.env['res.users'].search([('id','=',self._uid)])
		for b in curr_users.user_branch_id:
			branches.append(b)

		users = []
		for chk in branches:
			user_data = self.env['res.users'].search([])
			for u in user_data:
				if chk in u.user_branch_ids:
					users.append(u.id)

			domain = {'user_id': [('id', 'in', users)]}
			return {'domain': domain, 'value': {'user_id': []}}

	# @api.onchange('report_type')
	# def get_filter(self):
	# 	self.branch_type = 'all'

	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['form','to','branch_ids','report_type','branch_type','state'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['form','to','branch_ids','report_type','branch_type','state'])[0])
		return self.env.ref('bassami_vouchers_report.report_for_voucher_records').report_action(self, data=data)

	# 
	# def get_report(self):
		
	# 	data = {
	# 		'ids': self.ids,
	# 		'model': self._name,
	# 		'form': {
	# 			'form': self.form,
	# 			'to': self.to,
	# 			'entry_type': self.entry_type,
	# 			'partner_ids': self.partner_ids,
	# 			'customer_type': self.customer_type,
	# 		},
	# 	}

	
	# 	return self.env.ref('bassami_statement_of_accounts.report_for_partner_ledger').report_action(self, data=data)

	