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
from odoo import models, fields, api,_
from odoo.exceptions import Warning,ValidationError, UserError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class XlsxReportBxSales(models.TransientModel):
	_name = 'bx.sales.report'
	_inherit = 'report.report_xlsx.abstract'

	form = fields.Date(string='From')
	to = fields.Date(string='To')
	date = fields.Date(string='Date')
	branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="Branches From")
	branch_ids_to = fields.Many2many('bsg_route_waypoints', string="Branches To")
	users = fields.Many2many('res.users', string="Created By")
	customer_ids = fields.Many2many('res.partner', string="Customers")
	from_bx = fields.Many2one('transport.management', string="From Bx No.")
	to_bx = fields.Many2one('transport.management', string="To Bx No.")
	payment_method_ids = fields.Many2many('cargo_payment_method', string="Payment Methods")
	state = fields.Selection([
		('draft', 'Draft'),
		('confirm', 'Confirmed Order'),
		('issue_bill', 'Issue Bill'),
		('vendor_trip', 'Vendor Trip Money'),
		('fuel_voucher', 'Fuel Voucher'),
		('receive_pod', 'Received POD'),
		('done', 'Invoiced'),
		('cancel', 'Cancel'),
	], string='State')

	period_group = fields.Selection([
		('day', 'Day'),
		('month', 'Month'),
		('year', 'Year'),
	], string='Period Grouping By')

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
	], string='Date Condition')

	report_mode = fields.Selection([
		('Bx Sales Detail Report', 'Bx Sales Detail Report'),
		('Bx Period Sales Summary Report', 'Bx Period Sales Summary Report'),
		('Bx Branch Sales Summary Report','Bx Branch Sales Summary Report'),
		('Bx User Sales Summary Report', 'Bx User Sales Summary Report'),
		('Bx Customer Sales Summary Report', 'Bx Customer Sales Summary Report'),
	], string='Report Mode',default="Bx Sales Detail Report")

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
	def print_report(self):
		
		all_recs = self.env['transport.management'].search([],limit=1)

		if all_recs:
			self.ensure_one()
			[data] = self.read()
			datas = {
				'ids': [],
				'model': 'transport.management',
				'form': data,
			}
			
			report = self.env['ir.actions.report']. \
				_get_report_from_name('bx_sales_report.bx_sales_report_xlsx')

			report.report_file = self._get_report_base_filename()
			report = self.env.ref('bx_sales_report.action_bx_sales_report').report_action(all_recs, data=datas)
			return report
		else:
			raise UserError(_('There is no record in given date'))

	# @api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "Bx Sales Report"
		return name
	   


	