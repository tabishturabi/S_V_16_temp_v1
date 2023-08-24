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
import uuid
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class SimCardRequest(models.Model):
	_name = 'sim.card.request'
	_inherit = ['mail.thread']
	_description = "Sim Card Request"
	_rec_name = "name"

	name = fields.Char(string='Name', readonly=True)

	@api.constrains('employee_id')
	def _check_employee_contracr(self):
		if self.employee_id:
			emp_id = self.env['hr.contract'].search(
				[('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
			if not emp_id:
				raise ValidationError(_('%s does not has contract in running state' % self.employee_id.name))

	@api.model
	def _default_my_employee_id(self):
		user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,company_id=self.env.user.company_id.id).search([('id', '=', self.env.uid)])
		return self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])

	employee_readonly = fields.Boolean(string='Employee Readonly')
	employee_id = fields.Many2one('hr.employee',default=_default_my_employee_id, required=True , track_visibility=True)
	manager_id = fields.Many2one('hr.employee' ,readonly=True)
	company_id = fields.Many2one('res.company', string='Company', required=False, index=True,
								 default=lambda self: self.env.user.company_id,
								 help="Company related to this Sim Card")
	sim_type = fields.Selection(string="Sim Card Type", selection=[('voice', 'Voice'),
																   ('data', 'Data'), ], default='voice', required=True, track_visibility=True)
	is_cost = fields.Selection(string="Bear The Cost", selection=[('company', 'Company'),
																  ('employee', 'Employee'), ], default='company', track_visibility=True)
	description = fields.Text(string="Description", track_visibility=True, translate=True)
	branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Branch Name' ,readonly=True)
	department_id = fields.Many2one('hr.department', string="Department" ,readonly=True)
	job_id = fields.Many2one('hr.job', string="Job Position" ,readonly=True)
	date = fields.Datetime(string='Date' ,default=lambda self: fields.datetime.now(), track_visibility=True)
	date1 = fields.Date(string='Housing', compute='_compute_date1_count', store=True)
	clearance_in_leave = fields.Boolean(string="Clearance In Leave")

	@api.depends('date')
	def _compute_date1_count(self):
		for rec in self:
			if rec.date:
				rec.date1 = rec.date.date()

	state = fields.Selection(string="State", selection=[('draft', 'Draft'),('submitted', 'Submitted'),
																('approve', 'MNG APPROVE'),('reject', 'MNG REFUSE'),
																('fin_approve', 'FIN APPROVE'),('fin_reject', 'FIN REFUSE'),
														('delivered', 'Delivered'),('returned', 'Returned')], default='draft', track_visibility=True)
	generation = fields.Selection(string="Generation", selection=[('4G', '4G'),
																  ('5G', '5G'), ('6G', '6G')],required=True, track_visibility=True)

	attachment_ids = fields.Many2many('ir.attachment')
	attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
	delivery_id = fields.Many2one('sim.card.delivery', string="Delivery ID" ,readonly=True)
	delivery_count = fields.Integer('Number of Delivery')
	access_token = fields.Char('Security Token', copy=False)
	active = fields.Boolean(string="Active", default=True, track_visibility=True)
	employee_code = fields.Char(string='Employee ID',readonly=True)
	bsg_empiqama = fields.Many2one('hr.iqama', string='Employee Iqama ID',readonly=True)
	bsg_national_id = fields.Many2one('hr.nationality', string='Employee National ID',readonly=True)
	return_date = fields.Date(string='Return Date')
	assign_date = fields.Date(string='Assign Date')

	def action_return(self):
		self.return_date = fields.Date.today()
		self.state = 'returned'

	
	@api.onchange('employee_id')
	def get_employee_id_data(self):
		if self.employee_id:
			self.manager_id = self.employee_id.parent_id
			self.company_id = self.employee_id.company_id
			self.branch_id = self.employee_id.branch_id
			self.department_id = self.employee_id.department_id
			self.job_id = self.employee_id.job_id
			self.employee_code = self.employee_id.employee_code
			self.bsg_empiqama = self.employee_id.bsg_empiqama
			self.bsg_national_id = self.employee_id.bsg_national_id

	
	def _compute_attachment_number(self):
		attachment_data = self.env['ir.attachment'].read_group(
			[('res_model', '=', 'sim.card.request'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
		attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
		for request_no in self:
			request_no.attachment_number = attachment.get(request_no.id, 0)

	def compute_delivery_count_view(self):
		return {
			'name': 'delivery',
			'domain': [('id', '=', self.delivery_id.id)],
			'res_model': 'sim.card.delivery',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'type': 'ir.actions.act_window',
			"views": [[self.env.ref('sim_card.sim_card_delivery_tree_vieww1').id, "tree"],
					  [self.env.ref('sim_card.sim_card_delivery_form_view').id, "form"]],
		}

	
	def reject_mng(self):
		return self.write({'state': 'draft'})

	
	def finance_approve(self):
		self.assign_date = fields.Date.today()
		self.state= 'fin_approve'

	
	def finance_reject(self):
		return self.write({'state': 'submitted'})

	@api.model
	def create(self, vals):
		res = super(SimCardRequest, self).create(vals)
		if self.env.user.user_branch_id.branch_no:
			res.name = 'SRQ' + self.env.user.user_branch_id.branch_no + self.env['ir.sequence'].next_by_code(
				'sim.card.request')
		else:
			res.name = 'SRQ' + self.env['ir.sequence'].next_by_code('sim.card.request')
		return res

	
	def unlink(self):
		if self.state != 'draft':
			raise UserError(_('You Can Delete Record Only In Draft State'))
		return super(SimCardRequest, self).unlink()

	
	def approve_mng(self):
		self.state = 'approve'
		MailTemplate = self.env.ref('sim_card.mail_sim_card_tmplt', False)
		for rec in self.employee_id:
			if rec.partner_id.email:
				MailTemplate.sudo().write(
					{'email_to': str(self.manager_id.partner_id.email), 'email_from': str(self.manager_id.partner_id.email)})
				MailTemplate.sudo().send_mail(self.id, force_send=True)
		msg_id = self.env['mail.message'].search([('model', '=', 'sim.card.request'), ('res_id', '=', self.id)])
		msg_id.unlink()
		return True

	
	def action_submit(self):
		self.state = 'submitted'
		MailTemplate = self.env.ref('sim_card.mail_sim_card_tmpl', False)
		for rec in self.employee_id:
			if rec.partner_id.email:
				MailTemplate.sudo().write(
					{'email_to': str(self.manager_id.partner_id.email), 'email_from': str(rec.partner_id.email)})
				MailTemplate.sudo().send_mail(self.id, force_send=True)
		msg_id = self.env['mail.message'].search([('model', '=', 'sim.card.request'), ('res_id', '=', self.id)])
		msg_id.unlink()
		return True

	@api.model
	def base_url(self):
		base_url = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,company_id=self.env.user.company_id.id).get_param('web.base.url')
		return base_url

	@api.model
	def database_name(self):
		return self._cr.dbname

	
	def generate_access_token(self):
		if self.access_token:
			return self.access_token
		access_token = str(uuid.uuid4())
		self.write({'access_token': access_token})
		return access_token
