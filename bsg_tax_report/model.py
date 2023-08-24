import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import models, fields, api,_
from odoo.exceptions import Warning,ValidationError, UserError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class XlsxReportBsgTax(models.TransientModel):
	_name = 'bsg.tax.report'
	_inherit = 'report.report_xlsx.abstract'

   
	form = fields.Date(string="From",required=True)
	to = fields.Date(string="To",required=True)
	payment_method_ids = fields.Many2many('cargo_payment_method', string="Payment Methods")
	filters = fields.Selection(string="Filter",default="detail", selection=[
		('detail','Detail'),    
		('summary','Summary'),
	],required=True)
	

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
				_get_report_from_name('bsg_tax_report.bsg_tax_report_xlsx')

			report.report_file = self._get_report_base_filename()
			report = self.env.ref('bsg_tax_report.action_bsg_tax_report').report_action(all_recs, data=datas)
			return report
		else:
			raise UserError(_('There is no record in given date'))

	# @api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "Tax Report"
		return name
	   


	