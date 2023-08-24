import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import models, fields, api,_
from odoo.exceptions import Warning,ValidationError,UserError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class XlsxReportBxInfo(models.TransientModel):
	_name = 'bx.info.report'

	form = fields.Date(string='Order Date', default=fields.Date.context_today, required=True)
	to = fields.Date(string='Order Date', default=fields.Date.context_today, required=True)
	branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="Branches From")
	branch_ids_to = fields.Many2many('bsg_route_waypoints', string="Branches To")
	users = fields.Many2many('res.users', string="Created By")
	customer_ids = fields.Many2many('res.partner', string="Customers")
	vehicle_ids = fields.Many2many('fleet.vehicle', string="Vehicle Stricker No.")
	driver_ids = fields.Many2many('hr.employee', string="Driver Names")
	from_bx = fields.Many2one('transport.management', string="From Bx No.")
	to_bx = fields.Many2one('transport.management', string="To Bx No.")
	payment_method_ids = fields.Many2many('cargo_payment_method', string="Payment Methods")
	vehicle_type_ids = fields.Many2many('bsg.vehicle.type.table',string="Vehicle Type")
	vehicle_type_domain_ids = fields.Many2many('vehicle.type.domain',string="Domain Name")
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
	grouping_by = fields.Selection([
		('all', 'All'),
		('by_branch_from', 'Bx Information Report Group By Branch From'),
		('by_branch_to', 'Bx Information Report Group By Branch To'),
		('by_vehicle', 'Bx Information Report Group By Vehicle'),
		('by_customer', 'Bx Information Report Group By Customer'),
		('by_payment_method', 'Bx Information Report Group By Payment Method'),
		('by_created_by', 'Bx Information Report Group By Created By'),
		('by_driver_name', 'Bx Information Report Group By Driver Name'),
		('by_state', 'Bx Information Report Group By States'),
		('by_domain_name', 'Bx Information Report Group By Domain Name'),
		('by_vehicle_type', 'Bx Information Report Group By Vehicle Type'),
		('by_period', 'Bx Information Report Group By Period'),
	], default='all' ,required=True,string='Grouping By')
	period_grouping_by = fields.Selection(
		[('day', 'Day'), ('weekly', 'Weekly'), ('month', 'Month'), ('quarterly', 'Quarterly'), ('year', 'Year')],
		string='Period Grouping By')
	include_cancel = fields.Boolean(string="Include Cancel?")


	# @api.multi
	def print_report(self):

		# data = {
		# 	'ids': self.ids,
		# 	'model': self._name,
		# }
		# return self.env.ref('bx_information_report.action_bx_info_report').report_action(self, data=data)

		all_recs = self.env['transport.management'].search([], limit=1)

		if all_recs:
			self.ensure_one()
			[data] = self.read()
			datas = {
				'ids': [],
				'model': 'transport.management',
				'form': data,
			}

			report = self.env['ir.actions.report']. \
				_get_report_from_name('bx_information_report.bx_info_report_xlsx')

			report.report_file = self._get_report_base_filename()
			report = self.env.ref('bx_information_report.action_bx_info_report').report_action(self, data=datas)
			return report
		else:
			raise UserError(_('There is no record in given date'))

	# @api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "Bx Information Report"
		return name
	   


	