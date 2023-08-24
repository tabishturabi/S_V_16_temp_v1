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

class GeneralLedgerbassami(models.TransientModel):
	_name = "general.ledger.bassami"

	def _currency_domain(self):
		return [('id','!=',self.env.user.company_id.currency_id.id)]

	form = fields.Date(string="From",required=True)
	to = fields.Date(string="To",required=True)
	account_id = fields.Many2one('account.account',string="Account",required=True)
	state = fields.Selection(string="State",default="all", selection=[
		('all','All'),  
		('draft','Draft'),       
		('posted','Posted'),  
	],required=True)

	# branch_ids = fields.Many2many('bsg_branches.bsg_branches',string="Branch")
	# branch_type = fields.Selection(string="Branch Type",default="all", selection=[
	# 	('all','All'),    
	# 	('specific','Specific'), 
	# ])
	with_fc = fields.Boolean('with FC',default=False)
	currency_id = fields.Many2one('res.currency',domain=_currency_domain)

	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['form','to','account_id','state','with_fc','currency_id'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['form','to','account_id','state','with_fc','currency_id'])[0])
		return self.env.ref('bassami_general_legder.report_for_general_ledger').report_action(self, data=data)

	# @api.multi
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

	
