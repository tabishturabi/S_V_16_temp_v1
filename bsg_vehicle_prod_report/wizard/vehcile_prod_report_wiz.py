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

class VehcileProdReport(models.TransientModel):
	_name = "vehicle.prod.report"

	report_mode= fields.Selection([('vehicle_prod_report_summary','Vehcile Productivity Reprot Summary')], 'Report Mode', default="vehicle_prod_report_summary")
	period_grouby = fields.Selection([
		('day', 'Day'),
		('week', 'Week'),
		('month', 'Month'),
		('quarter', 'Quarter'),
		('year', 'Year')
	], 'Period Group By')
	date_condition = fields.Selection([
		('=', 'Is Equal To'),
		('!=', 'Is Not Equal To'),
		('>', 'Is After'),
		('<', 'Is Before'),
		('>=', 'Is After or Equal To'),
		('<=', 'Is Before or Equal To'),
		('in', 'Is In between'),
		('is_set', 'Is Set'),
		('is_not_set', 'Is Not Set')
	], 'Date condition', default="in")
	form = fields.Date(string="From",required=True)
	to = fields.Date(string="To",required=True)
	from_location_ids = fields.Many2many('bsg_route_waypoints', string='Branches From')
	to_location_ids = fields.Many2many(comodel_name='bsg_route_waypoints', relation="m2m_vehicle_prod_report_to_loc_rel", 
									   column1="vehicle_prod_report", column2="waypoint", string='Branches To')
	vehicle_type_ids = fields.Many2many('bsg.vehicle.type.table', string='Vehicle Types')
	vehicle_ids = fields.Many2many('fleet.vehicle', string='Vehicles')
	driver_ids = fields.Many2many('hr.employee', string='Drivers')
	
	
	# @api.multi
	def print_report(self):

		self.ensure_one()
		[data] = self.read()
		datas = {
			'ids': [],
			'model': 'fleet.vehicle.trip',
			'form': data,
		}
		report = self.env['ir.actions.report']. \
			_get_report_from_name('bsg_vehicle_prod_report.vehicle_prod_reports_temp')

		report.report_file = self._get_report_base_filename()
		report = self.env.ref('bsg_vehicle_prod_report.vehicle_prod_report').report_action(self,  data=datas )
	
		return report

	# @api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "Vehicle Productivity Report"
		return name

	# @api.multi
	# def generate_report(self):
	# 	data = {}
	# 	data['form'] = self.read(list(self._fields))[0]
	# 	return self._print_report(data)

	# def _print_report(self, data):
	# 	# data['form'].update(self.read(['form','to','driver_id','filters','report_type'])[0])
	# 	return self.env.ref('bsg_vehicle_prod_report.vehicle_prod_report').report_action(self, data=data)

	