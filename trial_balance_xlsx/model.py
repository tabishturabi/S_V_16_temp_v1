import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import models, fields, api
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class XlsxReportTrialBalance(models.TransientModel):
	_name = 'trial.balance.xlsx'
	_inherit = 'report.report_xlsx.abstract'

   
	date_from = fields.Date("Date From", required=True,default=date.today())
	date_to = fields.Date("Date To", required=True,default=date.today())
	analytic_account_ids = fields.Many2many("account.analytic.account",string="Analytic Account")
	target_moves = fields.Selection([
		('all', 'All Enteries'),
		('all_posted', 'All Posted Enteries')], string='Target Moves', required=True,default="all")
	levels = fields.Selection([
		('1', 'Level 1'),
		('2', 'Level 2'),
		('3', 'Level 3'),
		('4', 'Level 4'),
		('5', 'Level 5'),
		('6', 'Level 6')], string='Levels',required=True,default='1')
	with_movement = fields.Boolean("With Movement")


	#@api.multi
	def print_report(self):

		
		all_acts = self.env['account.account'].search([])

		if all_acts:
			self.ensure_one()
			[data] = self.read()
			datas = {
				'ids': [],
				'model': 'account.account',
				'form': data,
			}
			
			report = self.env['ir.actions.report']. \
				_get_report_from_name('trial_balance_xlsx.report_trial_balance_xlsx')

			report.report_file = self._get_report_base_filename()
			report = self.env.ref('trial_balance_xlsx.action_trial_balance_xls_report').report_action(all_acts, data=datas)
			
			return report
		else:
			raise UserError(_('There is no record in given date'))

	#@api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "Trial Balance"
		return name
	   


	