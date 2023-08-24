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

class Reconciliationbassami(models.TransientModel):
	_name = "budget.reconciliation.report"

	form = fields.Date(string="From",required=True)
	to = fields.Date(string="To",required=True)
	branch_ids = fields.Many2many('bsg_branches.bsg_branches',string="Branch",required=True)
	report_type = fields.Selection(string="Report Type",default="all", selection=[
		('all','All'),  
		('specific','Specific'),     
	],required=True)
	with_budget = fields.Boolean(string="With Budget Created")
	without_budget = fields.Boolean(string="Without Budget Created")
	
	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['form','to','branch_ids','report_type','with_budget','without_budget'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['form','to','branch_ids','report_type','with_budget','without_budget'])[0])
		return self.env.ref('budget_reconciliation_report.report_for_budget_reconciliation').report_action(self, data=data)

	