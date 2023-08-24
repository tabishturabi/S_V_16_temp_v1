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
from werkzeug.urls import url_encode
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class SimCardDelivery(models.Model):
	_name = 'sim.card.delivery'
	_inherit = ['mail.thread']
	_description = "Sim Card Delivery"
	_rec_name = "name"

	name = fields.Char(string='Name', readonly=True)
	name_id = fields.Many2one('sim.card.request', string='Request No.',required=False, track_visibility=True)
	employee_id = fields.Many2one('hr.employee', required=True, track_visibility=True, readonly=False)
	manager_id = fields.Many2one('hr.employee', readonly=True, track_visibility=True)
	company_id = fields.Many2one('res.company', string='Company', required=False, index=True,
								 default=lambda self: self.env.user.company_id,
								 help="Company related to this Sim Card")
	sim_type = fields.Selection(string="Sim Card Type", selection=[('voice', 'Voice'),
																   ('data', 'Data'), ], default='voice', required=True, track_visibility=True)
	transaction_type = fields.Selection(string="Transaction type", selection=[('delivery', 'Delivery')], default='delivery', required=True, track_visibility=True)
	mble_no = fields.Many2one('sim.card.define', string='Mobile Number',required=True, track_visibility=True)
	pkg_id = fields.Many2one('package.type', string=" Package Type Name", track_visibility=True)
	service_id = fields.Many2one('service.provider', string='Service provider')
	is_cost = fields.Selection(string="Bear The Cost", selection=[('company', 'Company'),
																  ('employee', 'Employee'), ], default='company', track_visibility=True)
	description = fields.Text(string="Description", track_visibility=True, translate=True)
	date = fields.Datetime(string='Delivery Date', track_visibility=True, default=lambda self: fields.datetime.now())
	date1 = fields.Date(string='Delivery Date1', compute='_compute_date1_count', store=True)
	branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Branch Name' ,readonly=True)
	department_id = fields.Many2one('hr.department', string="Department" ,readonly=True)
	job_id = fields.Many2one('hr.job', string="Job Position" ,readonly=True)
	user_id = fields.Many2one('res.user', string="User")
	active = fields.Boolean(string="Active", default=True, track_visibility=True)
	employee_code = fields.Char(string='Employee ID', readonly=True)
	bsg_empiqama = fields.Many2one('hr.iqama', string='Employee Iqama ID', readonly=True)
	bsg_national_id = fields.Many2one('hr.nationality', string='Employee National ID', readonly=True)

	def _default_state_action(self):
		return self.env['sim.status'].search([('action_type', '=', 'delivery')], limit=1).id
	mble_state = fields.Many2one('sim.status', string="Mobile State", track_visibility=True,
								 required=True, default=_default_state_action, index=True,
								 ondelete='cascade',domain="[('action_type','=', 'delivery')]" )
	state = fields.Selection(string="Sim Card Type", selection=[('draft', 'Draft'),('done', 'Done')], default='draft', track_visibility=True)
	attachment_ids = fields.Many2many('ir.attachment')
	attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')

	
	@api.onchange('mble_no')
	def get_mble_no_data(self):
		if self.mble_no:
			self.pkg_id = self.mble_no.pkg_id
			self.service_id = self.mble_no.service_id

	
	@api.onchange('name_id')
	def get_name_id_data(self):
		if not self.name_id:
			self.employee_id = False
		if self.name_id:
			self.employee_id = self.name_id.employee_id

	
	@api.onchange('employee_id', 'sim_type')
	def get_employee_id_data(self):
		if not self.employee_id:
			self.manager_id = False
			self.company_id = False
			self.branch_id = False
			self.department_id = False
			self.job_id = False
			self.employee_code = False
			self.bsg_empiqama = False
			self.bsg_national_id = False
		if self.employee_id:
			self.manager_id = self.employee_id.parent_id
			self.company_id = self.employee_id.company_id
			self.branch_id = self.employee_id.branch_id
			self.department_id = self.employee_id.department_id
			self.job_id = self.employee_id.job_id
			self.employee_code = self.employee_id.employee_code
			self.bsg_empiqama = self.employee_id.bsg_empiqama
			self.bsg_national_id = self.employee_id.bsg_national_id
			data = self.env['sim.card.define'].search(['|','|',('job_id', '=', self.job_id.id),
													   ('branch_id', '=', self.branch_id.id),
													   ('department_id', '=', self.department_id.id)])
			d_list = []
			for rec in data:

				if rec.state.action_type == 'receipt':
					if rec.sim_type == self.sim_type:
						d_list.append(rec.id)
			return {'domain': {'mble_no': [('id', 'in', d_list)]}}

	delivered_id = fields.Many2one('sim.card.define', string="delivered ID")
	delivered_count = fields.Integer('Number of Receipt', compute='_compute_delivered_count')
	delivery_id = fields.Many2one('sim.card.request', string="Delivery ID")
	delivery_count = fields.Integer('Number of Delivery', compute='_compute_delivery_count')

	@api.depends('name_id')
	def _compute_delivery_count(self):
		for rec in self:
			if rec.name_id:
				rec.delivery_count = len(rec.name_id)

	@api.depends('mble_no')
	def _compute_delivered_count(self):
		for rec in self:
			if rec.mble_no:
				rec.delivered_count = len(rec.mble_no)

	@api.depends('date')
	def _compute_date1_count(self):
		for rec in self:
			if rec.date:
				rec.date1 = rec.date.date()

	
	def action_validate(self):
		employee_delivery = self.env['hr.employee'].search([('id', '=', self.employee_id.id)], limit=1)
		delivery = self.env['sim.card.request'].search([('id', '=', self.name_id.id)], limit=1)
		define = self.env['sim.card.define'].search([('id', '=', self.mble_no.id)], limit=1)
		for rec in delivery:
			if self.name_id:
				rec.state = 'delivered'
				rec.is_cost = self.is_cost

				self.name_id.delivery_id = self.id
				self.name_id.delivery_count = self.delivery_count
		for i in self:
			if i.employee_id:
				abc = self.env['sim.card.request'].create({
					# 'name': self.id,
					'employee_id': i.employee_id.id,
					'manager_id': i.manager_id.id,
					'company_id': i.company_id.id,
					'branch_id': i.branch_id.id,
					'department_id': i.department_id.id,
					'job_id': i.job_id.id,
					'state': 'delivered',
					'is_cost': i.is_cost,
				})
				self.name_id = abc.id

		for re in define:
			re.employee = self.employee_id
			re.delivery_seq_id = self.id
			re.state = self.mble_state
			re.is_cost = self.is_cost
			re.pkg_id = self.pkg_id
		self.mble_no.delivered_id = self.id
		self.mble_no.delivered_count = self.delivered_count
		return self.write({'state': 'done'})

	
	def _compute_attachment_number(self):
		attachment_data = self.env['ir.attachment'].read_group(
			[('res_model', '=', 'sim.card.delivery'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
		attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
		for delivery_no in self:
			delivery_no.attachment_number = attachment.get(delivery_no.id, 0)

	
	def action_get_attachment_view(self):
		self.ensure_one()
		res = self.env['ir.actions.act_window'].for_xml_id('sim_card', 'action_attachment_sim_card_delivery')
		return res

	@api.model
	def create(self, vals):
		res = super(SimCardDelivery, self).create(vals)
		if self.env.user.user_branch_id.branch_no:
			res.name = 'SMD' + self.env.user.user_branch_id.branch_no + self.env['ir.sequence'].next_by_code(
				'sim.card.delivery')
		else:
			res.name = 'SMD' + self.env['ir.sequence'].next_by_code('sim.card.delivery')
		return res

	
	def unlink(self):
		if self.state != 'draft':
			raise UserError(_('You Can Delete Record Only In Draft State'))
		return super(SimCardDelivery, self).unlink()

	def action_send_mail(self):
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = self.env.ref('sim_card.sim_card_delivery_email_template', False)
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False

		partner_ids = [self.employee_id.partner_id.id]
		if self.manager_id.partner_id:
			partner_ids += self.manager_id.partner_id.ids

		ctx = {
			'default_model': 'sim.card.delivery',
			'default_res_id': self.id,
			'default_use_template': bool(template_id),
			'default_template_id': template_id and template_id.id or False,
			'default_composition_mode': 'comment',
			'mark_so_as_sent': True,
			'custom_layout': "mail.mail_notification_paynow",
			'proforma': self.env.context.get('proforma', False),
			'force_email': True,
			'default_partner_ids': partner_ids,
		}
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}

	
	def get_base_url(self):
		"""Get the base URL for the current model.

        Defined here to be overriden by website specific models.
        The method has to be public because it is called from mail templates.
        """
		self.ensure_one()
		return self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('web.base.url')

	def _get_share_url(self, redirect=False, signup_partner=False, pid=None):
		"""
        Build the url of the record  that will be sent by mail and adds additional parameters such as
        access_token to bypass the recipient's rights,
        signup_partner to allows the user to create easily an account,
        hash token to allow the user to be authenticated in the chatter of the record portal view, if applicable
        :param redirect : Send the redirect url instead of the direct portal share url
        :param signup_partner: allows the user to create an account with pre-filled fields.
        :param pid: = partner_id - when given, a hash is generated to allow the user to be authenticated
            in the portal chatter, if any in the target page,
            if the user is redirected to the portal instead of the backend.
        :return: the url of the record with access parameters, if any.
        """
		self.ensure_one()
		params = {
			'model': self._name,
			'res_id': self.id,
		}
		if hasattr(self, 'access_token'):
			params['access_token'] = self._portal_ensure_token()
		if pid:
			params['pid'] = pid
			params['hash'] = self._sign_token(pid)
		if signup_partner and hasattr(self, 'employee_id.partner_id') and self.employee_id.partner_id:
			params.update(self.employee_id.partner_id.signup_get_auth_param()[self.employee_id.partner_id.id])

		return '%s?%s' % ('/mail/view' if redirect else self.access_url, url_encode(params))












