# #-*- coding:utf-8 -*-

import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import api, models, fields
from odoo.exceptions import Warning,ValidationError,UserError
from odoo.tools import config
import base64
import string
import sys

class GeneratePartnerLedgerbassami(models.TransientModel):
	_name = "partner.ledger.bassami"



	def _get_default_access(self):
		if self.env.user.has_group('bassami_statement_of_accounts.statement_of_account_drivers_SOA'):
			return False
		else:
			return True

	def _get_wsv_default_access(self):
		if self.env.user.has_group('bassami_statement_of_accounts.statement_of_account_vendor_SOA'):
			return False
		else:
			return True

	def _get_default_type(self):
		if self.env.user.has_group('bassami_statement_of_accounts.statement_of_account_drivers_SOA'):
			return 'others'
		elif self.env.user.has_group('bassami_statement_of_accounts.statement_of_account_vendor_SOA'):
			return 'pay'
		else:
			return 'receive'

	form = fields.Date(string="From", default=date.today(),required=True)
	to = fields.Date(string="To",default=date.today(),required=True)
	entry_type = fields.Selection([
		('posted', 'Posted Ledger'),
		('all', 'All Ledger'),
		],default='all',string="Target Moves",required=True)
	partner_ids = fields.Many2many('res.partner',string="Partner")
	account_ids = fields.Many2many('account.account',string="Accounts")
	partner_types = fields.Many2one('partner.type',string="Partner Types")
	branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="Branches")
	customer_type = fields.Selection(string="Customer Filter", selection=[
		('all','All'),    
		('specific','Specific'),     
	],required=True,default='all')
	account_type = fields.Selection(string="Account Type", selection=[
		('receive','Receivable Accounts'),    
		('pay','Payable Accounts'),    
		('others','Others Accounts'),    
	],required=True,default=_get_default_type)
	with_details = fields.Boolean(string="With Details")
	for_emp = fields.Boolean(string="For Emp",default=False)
	one_page = fields.Boolean(string="Report In One Sheet")
	sort_details = fields.Boolean(string="Sort By Account")
	allowed_to_change = fields.Boolean('Allwed To Change',default=_get_default_access)
	with_inactive_partner = fields.Boolean(string="With Inactive Partner")
	with_soa_vendor = fields.Boolean(string='With SOA Vendor',default=_get_wsv_default_access)


	@api.onchange('partner_types')
	def get_customer_ids(self):
		if self.partner_types:
			partner_types_ids = []
			for p in self.partner_types:
				partner_types_ids.append(p.id)
			cust_data = self.env['res.partner'].search([('partner_types.id','in',partner_types_ids)]).ids

			domain = {'partner_ids': [('id', 'in', cust_data)]}
			return {'domain': domain, 'value': {'partner_ids': []}}

	@api.onchange('with_inactive_partner')
	def get_inactive_partner(self):
		if self.with_inactive_partner:
			return {'domain': {'partner_ids':['|',('active','=',True),('active','=',False)]}}
		else:
			return {'domain': {'partner_ids': [('active','=', True)]}}



	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['form','to','entry_type','partner_ids','customer_type','partner_types'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['form','to','entry_type','partner_ids','customer_type','partner_types'])[0])
		return self.env.ref('bassami_statement_of_accounts.report_for_partner_ledger').report_action(self, data=data)


	# @api.multi
	def print_report_xlsx(self):
		
		all_recs = self.env['res.partner'].search([],limit=1)

		if all_recs:
			self.ensure_one()
			[data] = self.read()
			datas = {
				'ids': [],
				'model': 'res.partner',
				'form': data,
			}
			
			report = self.env['ir.actions.report']. \
				_get_report_from_name('bassami_statement_of_accounts.stat_of_accounts_xlsx')

			report.report_file = self._get_report_base_filename()
			report = self.env.ref('bassami_statement_of_accounts.action_report_for_soa_xlsx').report_action(all_recs, data=datas)
			return report
		else:
			raise UserError('There is no record in given date')

	# @api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "Statement Of  Account  Report"
		return name

	
