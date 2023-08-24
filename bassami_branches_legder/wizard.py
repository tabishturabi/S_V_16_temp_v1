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


class BranchesLedgerbassami(models.TransientModel):
	_name = "branches.ledger.bassami"

	def _currency_domain(self):
		return [('id','!=',self.env.user.company_id.currency_id.id)]

	date_to = fields.Datetime(string="Date Time To")
	date_form = fields.Datetime(string="Date Time From")
	print_by = fields.Boolean(string="Print By time")

	form = fields.Date(string="From")
	to = fields.Date(string="To")
	journal_id = fields.Many2one('account.journal',string="Journal",required=True)
	state = fields.Selection(string="State",default="all", selection=[
		('all','All'),  
		('draft','Draft'),       
		('posted','Posted'),  
	],required=True)
	user_id = fields.Many2many('res.users',string="User")
	user_type = fields.Selection(string="User Type",default="all", selection=[
		('all','All'),    
		('specific','Specific'), 
	],required=True)
	with_fc = fields.Boolean('with FC',default=False)
	currency_id = fields.Many2one('res.currency',domain=_currency_domain)


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

	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['date_form','date_to','form','to','journal_id','state','user_id','user_type','with_fc','currency_id'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['date_form','date_to','form','to','journal_id','state','user_id','user_type','with_fc','currency_id'])[0])
		return self.env.ref('bassami_branches_legder.report_for_branches_ledger').report_action(self, data=data)
	
