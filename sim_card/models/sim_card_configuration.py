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


class SimCardConfig(models.Model):
	_name = 'service.provider'
	_inherit = ['mail.thread']
	_description = "Sim Card configuration"
	_rec_name = "name"

	name = fields.Char(string='Service provider	', required=True, track_visibility=True)
	partner_id = fields.Many2one('res.partner', 'Partner', track_visibility=True)
	contract_no = fields.Char(string='Contract Number', track_visibility=True)
	active = fields.Boolean(string="Active", default=True, track_visibility=True)

	@api.constrains('name')
	def _check_name(self):
		for record in self:
			if self.env[self._name].search([('id', '!=', record.id), ('name', '=', record.name)]):
				raise ValidationError('Service provider with %s already exist.' % record.name)


class SimStatus(models.Model):
	_name = 'sim.status'
	_order = 'sequence asc'
	_rec_name = 'name'
	_description = "Sim Card Status"

	name = fields.Char(required=True, translate=True)
	sequence = fields.Integer(help="Used to order the note stages")
	active = fields.Boolean(string="Active", default=True, track_visibility=True)
	_sql_constraints = [('fleet_state_name_unique', 'unique(name)', 'State name already exists')]

	action_type = fields.Selection([
		('delivery', 'Delivery'),
		('receipt', 'Receipt'),
		('cancelled', 'Cancelled')
	], 'Action Type', default='delivery')


class SimCardOwner(models.Model):
	_name = 'sim.owner'
	_inherit = ['mail.thread']
	_description = "Sim Card Owner"
	_rec_name = "name"

	name = fields.Char(string='Owner Name', required=True, track_visibility=True, translate=True)
	partner_id = fields.Many2one('res.partner', 'Partner', track_visibility=True)
	contract_no = fields.Char(string='Contract Number', track_visibility=True)
	active = fields.Boolean(string="Active", default=True, track_visibility=True)
