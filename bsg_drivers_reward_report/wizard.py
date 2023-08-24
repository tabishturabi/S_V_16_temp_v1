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

class DriversRewardReportBassami(models.TransientModel):
	_name = "drivers.reward.report"

	form = fields.Datetime(string="From",required=True)
	to = fields.Datetime(string="To",required=True)
	driver_id = fields.Many2many('hr.employee', string="Drivers")
	filters = fields.Selection(string="Filter",default="all", selection=[
		('all','All'),    
		('specific','Specific'), 
	],required=True)
	report_type = fields.Selection(string="Filter",default="summary", selection=[
		('detail','Detail'),    
		('summary','Summary'), 
	],required=True)
	trip_type = fields.Selection([
		('auto', 'تخطيط تلقائي'),
		('manual', 'تخطيط يدوي'),
		('local', 'خدمي')
	], string="Trip Type")
	fuel_expense_method_ids = fields.Many2many('bsg.fuel.expense.method',string="Fuel Expenses Method")
	
	
	# @api.multi
	def generate_report(self):
		print('...........self.read()............',self.read())
		[data] = self.read()
		datas = {
			'ids': [],
			'model': 'fleet.vehicle.trip',
			'form': data,
		}
		print('..........Generate report..........')
		print('..........Generate report..........')
		print('..........Generate report..........')
		print('..........Generate report..........')
		# return self.env.ref('bsg_drivers_reward_report.report_for_drivers_reward_id').report_action(self, data=datas)
		# data = {}
		# data['form'] = self.read(['form','to','driver_id','filters','report_type'])[0]
		# return self._print_report(data)

	def _print_report(self, data):
		# data['form'].update(self.read(['form','to','driver_id','filters','report_type'])[0])
		[data] = self.read()
		datas = {
			'ids': [],
			'model': 'fleet.vehicle.trip',
			'form': data,
		}
		return self.env.ref('bsg_drivers_reward_report.report_for_drivers_reward_id').report_action(self, data=data)

	# @api.multi
	def generate_xlsx_report(self):
		data = {
			'ids': self.ids,
			'model': self._name,
		}
		return self.env.ref('bsg_drivers_reward_report.driver_reward_report_xlsx').report_action(self, data=data)

class bsg_inherit_hr_employee_report(models.Model):
	_inherit = 'hr.employee'


	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
	    args = args or []
	    recs = self.search([('driver_code', operator, name)] + args, limit=limit)
	    if not recs.ids:
	        return super(bsg_inherit_hr_employee_report, self).name_search(name=name, args=args,operator=operator,limit=limit)
	        
	    return recs.name_get()
	