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

class SimCardReceipt(models.Model):
	_name = 'sim.card.receipt'
	_inherit = ['mail.thread']
	_description = "Sim Card Receipt"
	_rec_name = 'name'

	name = fields.Char(string='Name', readonly=True)
	mble_no = fields.Many2one('sim.card.define', string='Mobile Number',required=True,
							  track_visibility=True, domain=[('state.action_type', '=', 'delivery')])
	employee_id = fields.Many2one('hr.employee', string="Employee", required=True, track_visibility=True, readonly=True)
	manager_id = fields.Many2one('hr.employee', string='Manager', readonly=True)
	company_id = fields.Many2one('res.company', string='Company', required=False, index=True,
								 default=lambda self: self.env.user.company_id,
								 help="Company related to this Sim Card")
	employee_code = fields.Char(string='Employee ID', readonly=True)
	bsg_empiqama = fields.Many2one('hr.iqama', string='Employee Iqama ID', readonly=True)
	bsg_national_id = fields.Many2one('hr.nationality', string='Employee National ID', readonly=True)
	description = fields.Text(string="Description", track_visibility=True, translate=True)
	date = fields.Datetime(string='Receipt Date',default=lambda self: fields.datetime.now(), track_visibility=True)
	branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Branch', readonly=True)
	department_id = fields.Many2one('hr.department', string="Department", readonly=True)
	job_id = fields.Many2one('hr.job', string="Job Position", readonly=True)
	state = fields.Selection(string="Sim Card Type", selection=[('draft', 'Draft'), ('done', 'Done')], default='draft', track_visibility=True)
	delivery_seq_id = fields.Many2one('sim.card.delivery', string="Delivery Seq No", track_visibility=True, readonly=True)
	user_id = fields.Many2one('res.user', string="User")
	active = fields.Boolean(string="Active", default=True, track_visibility=True)
	transaction_type = fields.Selection(string="Transaction type", selection=[('receipt', 'Receipt')], default='receipt', required=True, track_visibility=True)
	sim_type = fields.Selection(string="Sim Card Type", selection=[('voice', 'Voice'),
																   ('data', 'Data')], required=False,
								track_visibility=True)
	is_cost = fields.Selection(string="Bear The Cost", selection=[('company', 'Company'),
																  ('employee', 'Employee')],
							   track_visibility=True)
	pkg_id = fields.Many2one('package.type', string=" Package Type Name", required=False, track_visibility=True)

	def _default_state_action(self):
		return self.env['sim.status'].search([('action_type', '=', 'receipt')], limit=1).id

	mble_state = fields.Many2one('sim.status', string="Mobile State", track_visibility=True,
								 required=True, default=_default_state_action, index=True, ondelete='cascade',
								 domain="[('action_type','=', 'receipt')]" )
	attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
	receipt_id = fields.Many2one('sim.card.define', string="Receipt ID")
	receipt_count = fields.Integer('receipt of Delivery', compute='_compute_receipt_id_count')
	date1 = fields.Date(string='Delivery Date1', compute='_compute_date1_count', store=True)

	@api.depends('date')
	def _compute_date1_count(self):
		for rec in self:
			if rec.date:
				rec.date1 = rec.date.date()

	@api.depends('mble_no')
	def _compute_receipt_id_count(self):
		for rec in self:
			if rec.mble_no:
				rec.receipt_count = len(rec.mble_no)

	
	@api.onchange('mble_no')
	def get_delivery_mble_no_data(self):
		if not self.mble_no:
			self.employee_id = False
			self.delivery_seq_id = False
			self.sim_type = False
			self.is_cost = False
			self.pkg_id = False
		if self.mble_no:
			self.employee_id = self.mble_no.employee
			self.delivery_seq_id = self.mble_no.delivery_seq_id
			self.sim_type = self.mble_no.sim_type
			self.is_cost = self.mble_no.is_cost
			self.pkg_id = self.mble_no.pkg_id

	
	@api.onchange('employee_id')
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

			data = self.env['sim.card.define'].search(
				[('job_id', '=', self.job_id.id) and ('branch_id', '=', self.branch_id.id)
				 and ('department_id', '=', self.department_id.id)])
			return {'domain': {'mble_no': [('id', 'in', data.ids)]}}

	
	def unlink(self):
		if self.state != 'draft':
			raise UserError(_('You Can Delete Record Only In Draft State'))
		return super(SimCardReceipt, self).unlink()

	
	def validate(self):
		receipt = self.env['sim.card.define'].search([('id', '=', self.mble_no.id)], limit=1)
		for rec in receipt:
			rec.write({'employee.employee_delivery_count': -1,
					   'state': self.mble_state.id,
					   'employee': False,
					   'delivery_seq_id': False,
					   'last_delivery_seq_id': self.delivery_seq_id.id,
					   'last_receipt_seq_id': self.id,
					   'check': True,
					   })
		self.mble_no.receipt_id = self.id
		self.mble_no.receipt_count = self.receipt_count
		return self.write({'state': 'done'})

	
	def _compute_attachment_number(self):
		attachment_data = self.env['ir.attachment'].read_group(
			[('res_model', '=', 'sim.card.receipt'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
		attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
		for receipt_no in self:
			receipt_no.attachment_number = attachment.get(receipt_no.id, 0)

	@api.model
	def create(self, vals):
		res = super(SimCardReceipt, self).create(vals)
		if self.env.user.user_branch_id.branch_no:
			res.name = 'SMR' + self.env.user.user_branch_id.branch_no + self.env['ir.sequence'].next_by_code(
				'sim.card.receipt')
		else:
			res.name = 'SMR' + self.env['ir.sequence'].next_by_code('sim.card.receipt')
		return res

	def action_send_mail(self):
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = self.env.ref('sim_card.sim_card_receipt_email_template', False)
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
			'default_model': 'sim.card.receipt',
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

	def action_get_attachment_view(self):
		self.ensure_one()
		res = self.env['ir.actions.act_window'].for_xml_id('sim_card', 'action_attachment_sim_card_receipt')
		return res

