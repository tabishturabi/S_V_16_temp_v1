import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
import pandas as pd
import numpy as np
import psycopg2 as pg
import pandas.io.sql as psql
import getpass
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class XlsxReportBxproductivity(models.TransientModel):
	_name = 'bx.productivity.reports'
	_inherit = 'report.report_xlsx.abstract'

	form = fields.Date(string='From')
	to = fields.Date(string='To')
	branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="From Branches")
	branch_ids_to = fields.Many2many('bsg_route_waypoints', string="To Branches")
	users = fields.Many2many('res.users', string="Created By")
	customer_ids = fields.Many2many('res.partner', string="Customers Name")
	from_bx = fields.Many2one('transport.management', string="From Bx No.")
	to_bx = fields.Many2one('transport.management', string="To Bx No.")
	truck_load = fields.Selection([
		('full', 'Full'),
		('empty', 'Empty'),
	], string='Truck Load')

	period_group = fields.Selection([
		('day', 'Day'),
		('weekly', 'Weekly'),
		('month', 'Month'),
		('quarterly', 'Quarterly'),
		('year', 'Year'),
	], string='Period Grouping By')

	fleet_type_transport = fields.Many2many('bsg.vehicle.type.table', string="Fleet Type")
	state = fields.Many2many('bsg.fleet.asset.status', string="Vehicle State")
	# employee_state = fields.Many2one('hr.employee', string="Employee State")


	employee_state = fields.Selection([
		('on_job', 'On Job'),
		('on_leave', 'On leave'),
		('return_from_holiday', 'Return From Holiday'),
		('resignation', 'Resignation'),
		('suspended', 'Suspended'),
		('service_expired', 'Service Expired'),
		('contract_terminated', 'Contract Terminated'),
		('ending_contract_during_trial_period', 'Ending Contract During Trial Period')
	], string='Employee State')

	date = fields.Date(string='Date')


	date_type = fields.Selection([
		('is equal to', 'is equal to'),
		('is not equal to', 'is not equal to'),
		('is after', 'is after'),
		('is before', 'is before'),
		('is after or equal to', 'is after or equal to'),
		('is before or equal to', 'is before or equal to'),
		('is between', 'is between'),
		('is set', 'is set'),
		('is not set', 'is not set'),
	], string='Order Date Condition')

	report_mode = fields.Selection([
		('Bx Vehicle productivity Detail Report', 'Bx Vehicle Productivity Detail Report'),
		('Bx Vehicle Type Summary Report', 'Bx Vehicle Type Productivity Summary Report'),
		('Bx Driver Summary Report','Bx Driver Productivity Summary Report'),
		('Bx User Summary Report', 'Bx User Productivity Summary Report'),
		('Bx Productivity Summary Loading Date Report', 'Bx Productivity Summary Loading Date Report'),
		('Bx Productivity Summary Arrival Date Report', 'Bx Productivity Summary Arrival Date Report'),
	], string='Report Mode',default="Bx Productivity Summary Loading Date Report")
	#
	is_between = fields.Boolean()
	others = fields.Boolean()


	@api.onchange('date_type')
	def onchange_date_type(self):
		if self.date_type:
			if self.date_type == "is between":
				self.is_between = True
				self.others = False

			if self.date_type != "is between":
				if self.date_type == "is set" or self.date_type == "is not set":
					self.is_between = False
					self.others = False
				else:
					self.is_between = False
					self.others = True

	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['form', 'to'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['form', 'to'])[0])
		return self.env.ref('bx_productivity_reports.report_transport_management').report_action(self, data=data)


	# @api.multi
	def print_report(self):

		all_recs = self.env['transport.management'].sudo().search([], limit=1)

		if 1:
			self.ensure_one()
			[data] = self.read()
			datas = {
				'ids': [],
				'model': 'transport.management',
				'form': data,
			}

			report = self.env['ir.actions.report']. \
				_get_report_from_name('bx_productivity_reports.bx_productivity_reports_xlsx')

			report.report_file = self._get_report_base_filename()
			report = self.env.ref('bx_productivity_reports.action_bx_productivity_reports').report_action(all_recs, data=datas)
			return report
		# else:
		# 	raise UserError(_('There is no record in given date'))

	# @api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "Bx Productivity Report"
		return name
	   


	
