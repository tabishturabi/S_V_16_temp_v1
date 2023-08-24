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



class PackageType(models.Model):
	_name = 'package.type'
	_inherit = ['mail.thread']
	_description = " Package Type"
	_rec_name = 'name'

	name = fields.Char(string=" Package Type Name" , required=True, track_visibility=True)
	service_id = fields.Many2one('service.provider', string="Service provider", required=True, track_visibility=True)
	contract_no = fields.Char(string='Contract Number:', related='service_id.contract_no', readonly=True,
							  track_visibility=True)
	minutes = fields.Integer(string='Group Minutes', track_visibility=True)
	local_minutes = fields.Integer(string='Local Minutes', track_visibility=True)
	international_minutes = fields.Integer(string='International Minutes', track_visibility=True)
	local_sms = fields.Integer(string='Local SMS', track_visibility=True)
	device_discount = fields.Integer(string='Device Discount', track_visibility=True)
	no_slice = fields.Integer(string='No. Of Data Slice', track_visibility=True)
	pkg_cost = fields.Float(string='Package Cost', track_visibility=True)
	local_internet = fields.Integer(string='Local Internet', track_visibility=True)
	local_roaming = fields.Integer(string='Internet Roaming', track_visibility=True)
	minutes_roaming = fields.Integer(string='Minutes Roaming', track_visibility=True)
	active = fields.Boolean(string="Active", default=True, track_visibility=True)
	generation = fields.Selection(string="Generation", selection=[('4G', '4G'),
																  ('5G', '5G'),('6G', '6G') ], track_visibility=True)

	
	@api.constrains('minutes', 'local_minutes', 'international_minutes','local_sms','device_discount','no_slice','pkg_cost','local_internet','local_roaming','minutes_roaming')
	def _check_minutes(self):
		if self.minutes:
			if self.minutes < 0:
				raise UserError(_('minutes can not be less than zero '),)
		if self.local_minutes:
			if self.local_minutes < 0:
				raise UserError(_('local_minutes can not be less than zero '),)
		if self.international_minutes:
			if self.international_minutes < 0:
				raise UserError(_('international_minutes can not be less than zero '),)
		if self.local_sms:
			if self.local_sms < 0:
				raise UserError(_('local_sms can not be less than zero '),)
		if self.device_discount:
			if self.device_discount < 0:
				raise UserError(_('device_discount can not be less than zero '),)
		if self.no_slice:
			if self.no_slice < 0:
				raise UserError(_('no_slice can not be less than zero '),)
		if self.pkg_cost:
			if self.pkg_cost < 0:
				raise UserError(_('pkg_cost can not be less than zero '),)
		if self.local_internet:
			if self.local_internet < 0:
				raise UserError(_('local_internet can not be less than zero '),)
		if self.local_roaming:
			if self.local_roaming < 0:
				raise UserError(_('local_roaming can not be less than zero '),)
		if self.minutes_roaming:
			if self.minutes_roaming < 0:
				raise UserError(_('minutes_roaming can not be less than zero '),)

	
	@api.constrains('name')
	def check_license_line(self):
		if self.name:
			record_id = self.env['package.type'].search(
				[('name', '=', self.name), ('id', '!=', self.id), ('service_id', '=', self.service_id.id)])
			if record_id:
				raise UserError(_("Package Type Name and Service provider must Be Unique...!"))

	pkg_unit = fields.Selection([
		('monthly', 'Monthly'),
		('quarterly', 'Quarterly'),
		('yearly', 'Yearly')
	], 'Package Unit', default='monthly', track_visibility=True)







