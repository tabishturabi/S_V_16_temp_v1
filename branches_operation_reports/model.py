import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import models, fields, api , _
from odoo.exceptions import Warning,ValidationError ,UserError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class XlsxReportBranchOptReport(models.TransientModel):
	_name = 'bsg.opt.reports'
	_inherit = 'report.report_xlsx.abstract'

	
	branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="Branches")
	users = fields.Many2many('res.users', string="Employees")
	year = fields.Many2one('account.fiscal.year', string="Year",required=True)
	months = fields.Selection([
		('01', 'January'),
		('02', 'February'),
		('03', 'March'),
		('04', 'April'),
		('05', 'May'),
		('06', 'June'),
		('07', 'July'),
		('08', 'August'),
		('09', 'September'),
		('10', 'October'),
		('11', 'November'),
		('12', 'December'),
	], string='Months',required=True)
	details = fields.Boolean(string="With Details")
	


	# @api.multi
	def print_report(self):
		
		all_recs = self.env['bsg_vehicle_cargo_sale_line'].search([],limit=1)

		if all_recs:
			self.ensure_one()
			[data] = self.read()
			datas = {
				'ids': [],
				'model': 'bsg_vehicle_cargo_sale_line',
				'form': data,
			}
			
			report = self.env['ir.actions.report']. \
				_get_report_from_name('branches_operation_reports.bsg_operations_report_xlsx')

			report.report_file = self._get_report_base_filename()
			report = self.env.ref('branches_operation_reports.action_bsg_operations_report').report_action(all_recs, data=datas)
			return report
		else:
			raise UserError(_('There is no record in given date'))

	# @api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "Branches Operation Reports"
		return name
