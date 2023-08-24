import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import models, fields, api
from odoo.exceptions import Warning,ValidationError,UserError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class XlsxReportCompOperation(models.TransientModel):
	_name = 'comp.operatios.report'
	_inherit = 'report.report_xlsx.abstract'

   
	form = fields.Datetime(string="From",required=True)
	to = fields.Datetime(string="To",required=True)
	payment_method_ids = fields.Many2many('cargo_payment_method', string="Payment Methods")
	ship_loc = fields.Many2many('bsg_route_waypoints','from_bsg_route_waypoints_operatios_report_rel','wizard_id','from_id', string="Shipping Location")
	drop_loc = fields.Many2many('bsg_route_waypoints','to_bsg_route_waypoints_operatios_report_rel','wizard_id','to_id', string="Drop Location")
	users = fields.Many2many('res.users', string="Users")
	customer_ids = fields.Many2many('res.partner', string="Customers")
	state = fields.Selection(
		[
			('all', 'All'),
			('draft', 'Draft'),
			('confirm', 'Confirm'),
			('awaiting', 'Awaiting Return'),
			('shipped', 'Shipped'),
			('on_transit', 'On Transit'),
			('Delivered', 'Delivered On Branch'),
			('done', 'Done'),
			('released', 'Released'),
			('cancel', 'Declined')
		], default='all',)
	trip_type = fields.Selection([
		('all','All'),
		('auto','تخطيط تلقائي'),
		('manual','تخطيط يدوي'),
		('local','خدمي')
		], string="Trip Type",default="all")
	pay_case = fields.Selection([
		('both', 'All'),
		('paid', 'Paid'),
		('not_paid', 'Not Paid')], string='Payment State', required=True,default="both")
	cargo_sale_type = fields.Selection(string="Cargo Sale Type",default="all", selection=[
		('all', 'All'),
		('local', 'Local'),
		('international', 'International')])
	user_type = fields.Selection(string="User Type",default="all", selection=[
		('all','All'),    
		('specific','Specific'), 
	],required=True)
	branch_type = fields.Selection(string="Ship Location Filter",default="all", selection=[
		('all','All'),    
		('specific','Specific'),
	],required=True)
	branch_type_to = fields.Selection(string="Drop Location Filter",default="all", selection=[
		('all','All'),    
		('specific','Specific'),
	],required=True)
	payment_method_filter = fields.Selection(string="Pay Methods Filter",default="all", selection=[
		('all','All'),    
		('specific','Specific'),
	],required=True)
	customer_filter = fields.Selection(string="Customer Filter",default="all", selection=[
		('all','All'),    
		('specific','Specific'),
	],required=True)
	sale_order_state = fields.Selection(
		[('all', 'All'),
		 ('confirm', 'Confirm'),
		 ('pod', 'Delivery'),
		 ('done', 'Done'),
		 ('Delivered', 'Delivered'),
		 ],string='Sale Order State', default="all")
	invoicep_line_filter = fields.Selection(
		[('all', 'All'),
		 ('paid', 'Paid'),
		 ('unpaid', 'Unpaid'),
		 ],string='Invoice Paid/Unpaid', default="all")
	with_cc = fields.Boolean(string='With CC')
	with_summary = fields.Boolean(string='With Summary')
	so_line_state = fields.Selection(
		[('all', 'All'),
		 ('paid', 'Paid'),
		 ('unpaid', 'Unpaid'),
		 ], string='SO Line State', default="all")


	

	# @api.multi
	def print_report(self):
		
		all_recs = self.env['bsg_vehicle_cargo_sale_line'].search([('company_id','=',self.env.user.company_id.id)],limit=1)
		

		if all_recs:
			self.ensure_one()
			[data] = self.read()
			datas = {
				'ids': [],
				'model': 'bsg_vehicle_cargo_sale_line',
				'form': data,
			}
			
			report = self.env['ir.actions.report']. \
				_get_report_from_name('comprehensive_operations_report.comp_operat_report_xlsx')

			report.report_file = self._get_report_base_filename()
			report = self.env.ref('comprehensive_operations_report.action_comperhansive_operations_report').report_action(all_recs, data=datas)
			return report
		else:
			raise UserError('There is no record in given date')

	# @api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "Comprehensive Operations Report"
		return name
	   


	
