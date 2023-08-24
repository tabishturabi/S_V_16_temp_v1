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

class SalesRevenueReportBassami(models.TransientModel):
	_name = "sales.revenue.report"

	form = fields.Datetime(string="From",required=True)
	to = fields.Datetime(string="To",required=True)
	partner_types = fields.Many2one("partner.type",string="Partner Type", domain="['|',('is_custoemer','=',True),('is_dealer','=',True)]",required=True)
	service_type = fields.Many2many('product.template', string="Service Name")
	service_filter = fields.Selection(string="Service Filter",default="all", selection=[
		('all','All Service'),    
		('specific','Specific Service'), 
	],required=True)
	branch_from = fields.Many2many(string="Branch From", comodel_name="bsg_branches.bsg_branches")
	branch_filter = fields.Selection(string="Branch From Filter",default="all", selection=[
		('all','All Branches'),    
		('specific','Specific Branches'), 
	],required=True)
	user_branch = fields.Many2one(string="User Branch", comodel_name="bsg_branches.bsg_branches")
	user_filter = fields.Selection(string="User Branch Filter",default="all", selection=[
		('all','All Branches'),    
		('specific','Specific Branches'), 
	],required=True)

	
	# @api.multi
	def generate_report(self):
		self.ensure_one()
		[data] = self.read()
		# data['emp'] = self.env.context.get('active_ids', [])
		# employees = self.env['hr.employee'].browse(data['emp'])
		datas = {
			'ids': [],
			'model': 'sales.revenue.report',
			'form': data,
			'_name':'sales.revenue.report'
		}
		return self.env.ref('bassami_sales_revenue_report.report_for_sales_revenue_id').report_action(self,data=datas)
		# data = {}
		# data['form'] = self.read(['form','to','partner_types','service_type','branch_from','user_branch'])[0]
		# return self._print_report(data)

	# def _print_report(self, data):
	# 	data['form'].update(self.read(['form','to','partner_types','service_type','branch_from','user_branch'])[0])
	# 	print('...............data.............',data)
	# 	print('...............data.............',type(data))
	# 	return self.env.ref('bassami_sales_revenue_report.report_for_sales_revenue_id').report_action(self, data=data)
	