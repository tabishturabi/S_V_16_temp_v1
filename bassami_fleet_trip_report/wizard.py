# #-*- coding:utf-8 -*-

import os
import xlsxwriter
from datetime import date, datetime
from datetime import date, timedelta
import time
from odoo import api, models, fields,_
from odoo.exceptions import Warning,ValidationError,UserError
from odoo.tools import config
import base64
import string
import sys

class FleetTripbassami(models.TransientModel):
	_name = "fleet.trip.report"
	_inherit = 'report.report_xlsx.abstract'

	# form = fields.Datetime(string="From")
	# to = fields.Datetime(string="To")
	vehicle_type = fields.Many2many('bsg.vehicle.type.table',string="Vehicle Type")
	fleet_id = fields.Many2many('fleet.vehicle',string="Fleets")
	driver_code = fields.Many2many('hr.employee',string="Driver")
	branch_from = fields.Many2many('bsg_route_waypoints','trip_report_branch_from_rel','from_id','trip_report_id',string="From Branch")
	branch_to = fields.Many2many('bsg_route_waypoints','trip_report_branch_to_rel','to_id','trip_report_id',string="To Branch")

	trip_type = fields.Selection([
		('auto','تخطيط تلقائي'),
		('manual','تخطيط يدوي'),
		('local','خدمي')
		], string="Trip Type")
	filter_type = fields.Selection(string="Filter",default="all", selection=[
		('all','All'),  
		('specific','Specific'),       
	])
	report_type = fields.Selection(string="Report Type",default="trip", selection=[
		('trip','Trip Wise'),    
		('fleet','Fleet Wise'), 
	],required=True)
	filter_date_by = fields.Selection(string="Filter Date By", selection=[
		('scheduled_start_date', 'Scheduled Start Date'),
		('scheduled_end_date', 'Scheduled End Date'),
		('actual_start_date', 'Actual Start Date'),
		('actual_end_date', 'Actual End Date'),
	])
	sa_date_condition = fields.Selection(
		[('all', 'All'), ('is_equal_to', 'is equal to '), ('is_not_equal_to', 'is not equal to'),
		 ('is_after', 'is after'), ('is_before', 'is before'),
		 ('is_after_or_equal_to', 'is after or equal to'),
		 ('is_before_or_equal_to', 'is before or equal to'), ('is_between', 'is between'),
		 ('is_set', 'is set'), ('is_not_set', 'is not set')], required=True, string='SA Date Condittion', default='all')
	form = fields.Datetime(string='From')
	to = fields.Datetime(string='To')
	date = fields.Datetime(string='Date')
	print_date = fields.Date(string='Date',default=fields.date.today())
	trip_status = fields.Selection(string="Trip Status", selection=[
		('draft', 'Draft'),
		('on_transit', 'On Transit'),
		('confirmed', 'Confirmed'),
		('progress', 'In Operation'),
		('done', 'Done'),
		('finished', 'Finished'),
		('cancelled', 'Cancelled')
	])
	truck_load = fields.Selection([
		('full', 'Full Load'),
		('empty', 'Empty Load')
	], string="Truck Load")
	car_load = fields.Selection([
		('full', 'Full Load'),
		('empty', 'Empty Load')
	], string="Car Load")
	vehicle_group_id = fields.Many2one('bsg.vehicle.group', string="Vehicle Group Name")
	fuel_expense_type_id = fields.Many2one('bsg.fuel.expense.method', string="Fuel Expense Type")
	user_id = fields.Many2one('res.users',string="User")
	group_by = fields.Selection(string="Group By", selection=[
		('all', 'All'),
		('vehicle_sticker_no', 'Vehicle Sticker NO'),
		('driver_code', 'Driver Code'),
		('vehicle_type', 'Vehicle Type'),
		('vehicle_group_name', 'Vehicle Group Name'),
		('fuel_expense_type', 'Fuel Expense Type'),
		('start_branch', 'Start Branch'),
		('end_branch', 'End Branch'),
		('schedule_start_date', 'Scheduled Start Date'),
		('schedule_end_date', 'Scheduled End Date'),
		('truck_load', 'Truck Load'),
		('trip_status', 'Trip Status'),
		('user', 'User'),
		('trip_type', 'Trip Type')
	],default="all",required=True)
	trailer_sticker_no = fields.Many2one('bsg_fleet_trailer_config',string="Trailer Sticker No")
	license_plate_no = fields.Char(string="License Plate NO")
	driver_link = fields.Selection([
		('all', 'All'),
		('linked', 'Linked'),
		('unlinked', 'Unlinked')
	], string="Driver Link",default="all",required=True)
	vehicle_state_id = fields.Many2one('fleet.vehicle.state', string="Vehicle State")

	@api.onchange('report_type')
	def onchange_report_type(self):
		if self.report_type:
			if self.report_type == 'trip':
				self.filter_type = 'all'



	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['form','to','fleet_id','report_type'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['form','to','fleet_id','report_type'])[0])
		return self.env.ref('bassami_fleet_trip_report.report_for_fleet_trip').report_action(self, data=data)

	# @api.multi
	def print_report_xlsx(self):
		
		all_recs = self.env['fleet.vehicle.trip'].search([],limit=1)

		if all_recs:
			self.ensure_one()
			[data] = self.read()
			datas = {
				'ids': [],
				'model': 'fleet.vehicle.trip',
				'form': data,
				'wiz_obj':self
			}
			report = self.env['ir.actions.report']. \
				_get_report_from_name('bassami_fleet_trip_report.fleet_trip_report_xlsx')

			report.report_file = self._get_report_base_filename()
			report = self.env.ref('bassami_fleet_trip_report.action_report_for_fleet_trip').report_action(all_recs, data=datas)
			return report
		else:
			raise UserError(_('There is no record in given date'))

	# @api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "Fleet Trip Report"
		return name

class SoWiseRevenue(models.TransientModel):
	_name = "so.wise.revenue"
	_inherit = 'report.report_xlsx.abstract'

	form = fields.Date(string="From")
	to = fields.Date(string="To")
	vehicle_type = fields.Many2many('bsg.vehicle.type.table',string="Vehicle Type")
	fleet_id = fields.Many2many('fleet.vehicle',string="Fleets")
	driver_code = fields.Many2many('hr.employee',string="Driver")


	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['form','to','fleet_id'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['form','to','fleet_id'])[0])
		return self.env.ref('bassami_fleet_trip_report.report_for_fleet_trip').report_action(self, data=data)

	# @api.multi
	def print_report_xlsx(self):
		
		# all_recs = self.env['fleet.vehicle.trip'].search([],limit=1)

		self.ensure_one()
		[data] = self.read()
		datas = {
			'ids': self.ids,
			'model': self._name,
			'form': data,
		}
		
		report = self.env['ir.actions.report']. \
			_get_report_from_name('bassami_fleet_trip_report.so_wise_revenue_report_xlsx')

		report.report_file = self._get_report_base_filename()
		report = self.env.ref('bassami_fleet_trip_report.action_so_wise_revenue_report').report_action(self, data=datas)
		return report
	# @api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "Sale Line Revenue"
		return name

	