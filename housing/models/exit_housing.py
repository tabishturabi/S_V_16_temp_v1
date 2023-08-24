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



class ExitHousing(models.Model):
	_name = 'exit.housing'
	_inherit = ['mail.thread']
	_description = "Exit Housing"
	_rec_name = "name"

	name = fields.Char(string='Name', readonly=False)

	date = fields.Datetime(string='Exiting Date', default=lambda self: fields.datetime.now(), track_visibility=True,
						   readonly=True)
	entry_date = fields.Datetime(string='Entering date', track_visibility=True, readonly=True)

	exit_id = fields.Many2one('entry.housing', string='Permission Entry Housing seq No',required=False, track_visibility=True , readonly=True)
	validate_date = fields.Datetime(string='Validate Date', default=lambda self: fields.datetime.now(), track_visibility=True, readonly=True)
	employee_id = fields.Many2one('hr.employee', required=True, track_visibility=True)
	manager_id = fields.Many2one('hr.employee', readonly=True)

	company_id = fields.Many2one('res.company', string='Company', readonly=True, index=True,
								 default=lambda self: self.env.user.company_id,
								 help="Company related to this Housing")

	house_location = fields.Many2one('bsg_branches.bsg_branches', string='House Location', readonly=True, index=True,
								 default=lambda self: self.env.user.user_branch_id,
								 help="Branch related to this Housing")

	@api.model
	def _default_created_id(self):
		user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
															company_id=self.env.user.company_id.id).search(
			[('id', '=', self.env.uid)])
		return self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])

	created_id = fields.Many2one('hr.employee', default=_default_created_id, required=False, track_visibility=True)
	mobile_phone = fields.Char(string='Mobile Number', required=False, track_visibility=True , readonly=True)
	sticker_no = fields.Char(string='Sticker No', readonly=True)
	vehicle_name = fields.Many2one('fleet.vehicle.model', string="Vehicle Name", track_visibility=True, readonly=True)
	vehicle_type_id = fields.Many2one('bsg.vehicle.type.table', string='Vehicle Type Name', readonly=True)
	branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Branch Name', readonly=True)
	department_id = fields.Many2one('hr.department', string="Department", readonly=True)
	job_id = fields.Many2one('hr.job', string="Job Position", readonly=True)
	house_seq = fields.Char(string='Exiting House seq', readonly=True)
	reason_id = fields.Many2one('reason.entry', string='Entry Reason Type', readonly=True)
	description = fields.Text(string="Description", track_visibility=True, translate=True)
	analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", readonly=True)
	analytic_tag_ids = fields.Many2many('account.analytic.tag', string="Analytic Tags", track_visibility='always', readonly=True)
	active = fields.Boolean(string="Active", default=True, track_visibility=True)
	state = fields.Selection(string="state", selection=[('draft', 'Draft'), ('done', 'Done')],
							 default='draft', track_visibility=True)
	employee_code = fields.Char(string='Employee ID', readonly=True)
	bsg_empiqama = fields.Many2one('hr.iqama', string='Employee Iqama ID', readonly=True)
	bsg_national_id = fields.Many2one('hr.nationality', string='Employee National ID', readonly=True)

	days_count = fields.Char(string='Days', readonly=True)
	date1 = fields.Date(string='Exit', compute='_compute_date1_count', store=True)

	@api.depends('entry_date')
	def _compute_date1_count(self):
		for rec in self:
			if rec.entry_date:
				rec.date1 = rec.date.date()

	@api.onchange('employee_id')
	def onchange_employee_id(self):
		list = []
		employees = self.env['entry.housing'].search([('employee_id', '!=', False),('house_seq', '=', False)])
		for em in employees:
			list.append(em.employee_id.id)
		return {'domain': {'employee_id': [('id', 'in', list)]}}

	
	def unlink(self):
		if self.state != 'draft':
			raise UserError(_('You Can Delete Record Only In Draft State'))
		return super(ExitHousing, self).unlink()

	
	@api.onchange('employee_id')
	def get_employee_data(self):
		if self.employee_id:
			self.exit_id = self.env['entry.housing'].search([('employee_id', '=', self.employee_id.id),('house_seq', '=', False)],limit=1).id

	
	@api.onchange('exit_id')
	def get_exit_id_data(self):
		if self.exit_id:
			self.company_id = self.exit_id.company_id
			self.branch_id = self.exit_id.branch_id
			self.department_id = self.exit_id.department_id
			self.job_id = self.exit_id.job_id.id
			self.mobile_phone = self.exit_id.mobile_phone
			self.employee_code = self.exit_id.employee_code
			self.bsg_empiqama = self.exit_id.bsg_empiqama
			self.bsg_national_id = self.exit_id.bsg_national_id
			self.analytic_account_id = self.exit_id.analytic_account_id
			self.sticker_no = self.exit_id.sticker_no
			self.reason_id = self.exit_id.reason_id
			self.entry_date = self.exit_id.date
			self.vehicle_name = self.exit_id.vehicle_name
			self.vehicle_type_id = self.exit_id.vehicle_type_id
			self.days_count = self.exit_id.days_count

	
	def action_validate(self):

		house = self.env['entry.housing'].search([('employee_id', '=', self.employee_id.id),('id', '=', self.exit_id.id)], limit=1)
		house.write({
			'house_seq': self.id,
			'exit_date': self.date,
		})
		return self.write({'state': 'done', 'validate_date': datetime.now()})

	@api.model
	def create(self, vals):
		res = super(ExitHousing, self).create(vals)
		if self.env.user.user_branch_id.branch_no:
			res.name = 'EXTH' + self.env.user.user_branch_id.branch_no + self.env['ir.sequence'].next_by_code(
				'exit.housing')
		else:
			res.name = 'EXTH' + self.env['ir.sequence'].next_by_code('exit.housing')

		Obj = self.env['entry.housing'].search([('id', '=', res.exit_id.id)], limit=1)
		Obj.update({
			'house_seq': res.id,
			'exit_date': res.date,
		})
		return res










