# #-*- coding:utf-8 -*-

import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import api, models, fields,_
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
import string
import sys

class vehicleRevenuereport(models.TransientModel):
	_name = "vehicle.revenue.report"

	form = fields.Date(string="From",required=True)
	to = fields.Date(string="To",required=True)
	vehicle_id = fields.Many2many('fleet.vehicle',string="Vehicle")
	vehicle_type = fields.Many2many('bsg.vehicle.type.table',string="Vehicle Type")
	driver_id = fields.Many2many('hr.employee',string="Driver")
	trip_type = fields.Selection([
		('auto','تخطيط تلقائي'),
		('manual','تخطيط يدوي'),
		('local', 'خدمي')
		], string="Trip Type")
	report_type = fields.Selection([
		('summary','Summary'),
		('detail','Detail'),
		], string="Report Type",required=True,default='summary')
	fuel_expense_method_ids = fields.Many2many('bsg.fuel.expense.method', string="Fuel Expenses Method")
	route_type = fields.Selection([
		('km', 'Domestic'),
		('local', 'خدمي'),
		('route', 'International'),
		('port', 'Port'),
		('hybrid', 'Hybrid Route')], string="Route Type",
		help='This is to determine if the route is international/domestic or between ports'
	)


	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['form','to','vehicle_id','driver_id','trip_type','vehicle_type','report_type'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		domain = [('expected_start_date', '>=', self.form), ('expected_start_date', '<=', self.to),
				  ('state', 'not in', ['draft', 'cancel']),('vehicle_id.state_id', 'not in', [1, 7])]
		if self.fuel_expense_method_ids:
			domain.append(('display_expense_mthod_id', 'in', self.fuel_expense_method_ids.ids))
		if self.vehicle_id:
			domain.append(('vehicle_id.id', 'in', self.vehicle_id.ids))
		if self.vehicle_type:
			domain.append(('vehicle_id.vehicle_type.id', 'in', self.vehicle_type.ids))
		if self.driver_id:
			domain.append(('driver_id.id', 'in', self.driver_id.ids))
		if self.trip_type:
			domain.append(('trip_type', '=', self.trip_type))
		all_trips = self.env['fleet.vehicle.trip'].search(domain, order="vehicle_id", limit=1)
		if not all_trips:
			raise ValidationError(_("NO records found"))
		data['form'].update(self.read(['form','to','vehicle_id','driver_id','trip_type','vehicle_type','report_type'])[0])
		return self.env.ref('vehicle_revenue_report.report_for_vehicle_revenue_report').report_action(self, data=data)

	# @api.multi
	def generate_report_xlsx(self):
		data = {}
		data['form'] = self.read(['form', 'to', 'vehicle_id', 'driver_id', 'trip_type', 'vehicle_type', 'report_type'])[
			0]
		print('..............data...........', data)
		return self._print_report_xlsx(data)

	def _print_report_xlsx(self, data):
		domain = [('expected_start_date', '>=', self.form), ('expected_start_date', '<=', self.to),
				  ('state', 'not in', ['draft', 'cancel']), ('vehicle_id.state_id', 'not in', [1, 7])]
		if self.fuel_expense_method_ids:
			domain.append(('display_expense_mthod_id', 'in', self.fuel_expense_method_ids.ids))
		if self.vehicle_id:
			domain.append(('vehicle_id.id', 'in', self.vehicle_id.ids))
		if self.vehicle_type:
			domain.append(('vehicle_id.vehicle_type.id', 'in', self.vehicle_type.ids))
		if self.driver_id:
			domain.append(('driver_id.id', 'in', self.driver_id.ids))
		if self.trip_type:
			domain.append(('trip_type', '=', self.trip_type))
		all_trips = self.env['fleet.vehicle.trip'].search(domain, order="vehicle_id", limit=1)
		if not all_trips:
			raise ValidationError(_("NO records found"))
		data['form'].update(
			self.read(['form', 'to', 'vehicle_id', 'driver_id', 'trip_type', 'vehicle_type', 'report_type'])[0])
		return self.env.ref('vehicle_revenue_report.vehicle_revenue_xlsx_report').report_action(self, data=data)
	

class vehicleTruckRevenuereport(models.TransientModel):
	_name = "vehicle.truck.revenue.report"

	form = fields.Date(string="From",required=True)
	to = fields.Date(string="To",required=True)
	vehicle_id = fields.Many2many('fleet.vehicle',string="Vehicle")
	# vehicle_type = fields.Many2many('bsg.vehicle.type.table',string="Vehicle Type")
	driver_id = fields.Many2many('hr.employee',string="Driver")
	trip_type = fields.Selection([
		('auto','تخطيط تلقائي'),
		('manual','تخطيط يدوي'),
		('local','خدمي')
		], string="Trip Type")
	report_type = fields.Selection([
		('summary','Summary'),
		('detail','Detail'),
		], string="Trip Type",required=True,default='summary')


	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['form','to','vehicle_id','driver_id','trip_type','report_type'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['form','to','vehicle_id','driver_id','trip_type','report_type'])[0])
		return self.env.ref('vehicle_revenue_report.report_for_vehicle_truck_revenue_report').report_action(self, data=data)