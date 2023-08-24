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
from werkzeug.urls import url_encode
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import Warning, ValidationError
from odoo.tools import config
import base64
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta


class UpgradeRequest(models.Model):
    _name = 'upgrade.request'
    _inherit = ['mail.thread']
    _description = "Sim Card Upgrade"
    _rec_name = "name"

    name = fields.Char(string='Name', readonly=True)
    employee_id = fields.Many2one('hr.employee', required=True, track_visibility=True)
    manager_id = fields.Many2one('hr.employee', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=False, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Sim Card")

    sim_type = fields.Selection(string="Sim Card Type", selection=[('voice', 'Voice'),
                                                                   ('data', 'Data'), ], default='voice', required=True,
                                track_visibility=True)
    is_cost = fields.Selection(string="Bear The Cost", selection=[('company', 'Company'),
                                                                  ('employee', 'Employee'), ], default='company')
    description = fields.Text(string="Description", track_visibility=True)
    branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Branch Name', readonly=True)
    department_id = fields.Many2one('hr.department', string="Department", readonly=True)
    job_id = fields.Many2one('hr.job', string="Job Position", readonly=True)
    date = fields.Datetime(string='Request Date', default=lambda self: fields.datetime.now(), track_visibility=True)

    state = fields.Selection(string="Sim Card Type", selection=[('draft', 'Draft'), ('submitted', 'Submitted'),
                                                                ('approve', 'MNG APPROVE'), ('reject', 'MNG REJECT'),
                                                                ('fin_approve', 'FIN APPROVE'),
                                                                ('fin_reject', 'FIN Reject'),
                                                                ('done', 'Done'), ('cancel', 'Cancel')],
                             default='draft', track_visibility=True)
    transaction_type = fields.Selection(string="Transaction type", selection=[('upgrade', 'Upgrade')],
                                        default='upgrade', required=True, track_visibility=True)
    attachment_ids = fields.Many2many('ir.attachment')
    mble_no = fields.Many2one('sim.card.define', string='Mobile Number', track_visibility=True)
    pkg_id = fields.Many2one('package.type', string=" Package Type Name", track_visibility=True, readonly=True)
    new_pkg_id = fields.Many2one('package.type', string="New Package Type Name",
                                 domain="[('service_id','=', service_id)]", track_visibility=True)
    pkg_type = fields.Char(string="Current Package Type")
    service_id = fields.Many2one('service.provider', string='Service provider', track_visibility=True)
    access_token = fields.Char('Security Token', copy=False)
    user_id = fields.Many2one('res.user', string="User")
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    active = fields.Boolean(string="Active", default=True, track_visibility=True)
    employee_code = fields.Char(string='Employee ID', readonly=True)
    bsg_empiqama = fields.Many2one('hr.iqama', string='Employee Iqama ID', readonly=True)
    bsg_national_id = fields.Many2one('hr.nationality', string='Employee National ID', readonly=True)
    date1 = fields.Date(string='Delivery Date1', compute='_compute_date1_count', store=True)

    @api.depends('date')
    def _compute_date1_count(self):
        for rec in self:
            if rec.date:
                rec.date1 = rec.date.date()

    
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'upgrade.request'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for upgrade_no in self:
            upgrade_no.attachment_number = attachment.get(upgrade_no.id, 0)

    
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('sim_card.action_attachment_upgrade_request')
        return res

    
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
            data = self.env['sim.card.define'].search(
                [('job_id', '=', self.job_id.id) and ('branch_id', '=', self.branch_id.id)
                 and ('department_id', '=', self.department_id.id) and ('employee', '=', self.employee_id.id)])
            d_list = []
            for rec in data:
                if rec.state.action_type == 'delivery':
                    d_list.append(rec.id)
            return {'domain': {'mble_no': [('id', 'in', data.ids)]}}

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        list = []
        employees = self.env['sim.card.define'].search([('employee', '!=', False)])
        for em in employees:
            list.append(em.employee.id)
        return {'domain': {'employee_id': [('id', 'in', list)]}}

    @api.onchange('mble_no')
    def onchange_mobile_number(self):
        if self.mble_no:
            pkg_list = []
            data = self.env['sim.card.define'].search([('id', '=', self.mble_no.id)])
            for d in data:
                pkg_list.append(d.pkg_id.id)
            return {'domain': {'pkg_id': [('id', 'in', pkg_list)]}}

    
    @api.onchange('mble_no')
    def get_mble_no_data(self):
        if self.mble_no:
            self.pkg_id = self.mble_no.pkg_id
            self.service_id = self.mble_no.service_id

    
    def approve_mng(self):
        return self.write({'state': 'approve'})

    
    def reject_mng(self):
        return self.write({'state': 'reject'})

    
    def finance_approve(self):
        return self.write({'state': 'fin_approve'})

    
    def finance_reject(self):
        return self.write({'state': 'fin_reject'})

    
    def cancel(self):
        return self.write({'state': 'cancel'})

    @api.model
    def create(self, vals):
        res = super(UpgradeRequest, self).create(vals)
        if self.env.user.user_branch_id.branch_no:
            res.name = 'SURQ' + self.env.user.user_branch_id.branch_no + self.env['ir.sequence'].next_by_code(
                'upgrade.request')
        else:
            res.name = 'SURQ' + self.env['ir.sequence'].next_by_code('upgrade.request')
        return res

    
    def action_done(self):
        define = self.env['sim.card.define'].search([('id', '=', self.mble_no.id)], limit=1)
        for re in define:
            re.pkg_id = self.new_pkg_id
        return self.write({'state': 'done'})

    
    def action_submit(self):
        self.state = 'submitted'
        MailTemplate = self.env.ref('sim_card.mail_sim_card_upgrade_tmpl', False)
        for rec in self.employee_id:
            if rec.partner_id.email:
                print('Upgrade request From to', rec.partner_id.email)
                print('Upgrade request Send to', self.manager_id.partner_id.email)
                MailTemplate.sudo().write(
                    {'email_to': str(self.manager_id.partner_id.email), 'email_from': str(rec.partner_id.email)})
                MailTemplate.sudo().send_mail(self.id, force_send=True)
        msg_id = self.env['mail.message'].search([('model', '=', 'upgrade.request'), ('res_id', '=', self.id)])
        msg_id.unlink()
        return True

    
    def approve_mng(self):
        self.state = 'approve'
        MailTemplate = self.env.ref('sim_card.mail_sim_card_finance_upgrade_tmpl', False)
        for rec in self.employee_id:
            if rec.partner_id.email:
                print('Upgrade Request From to', self.manager_id.partner_id.email)
                print('Upgrade request Send to', self.manager_id.partner_id.email)
                MailTemplate.sudo().write(
                    {'email_to': str(self.manager_id.partner_id.email),
                     'email_from': str(self.manager_id.partner_id.email)})
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

    def action_send_mail(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = self.env.ref('sim_card.sim_card_upgrade_email_template', False)
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
            'default_model': 'upgrade.request',
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
        return self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,company_id=self.env.user.company_id.id).get_param('web.base.url')

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
        if pid:
            params['pid'] = pid
            params['hash'] = self._sign_token(pid)
        if signup_partner and hasattr(self, 'employee_id.partner_id') and self.employee_id.partner_id:
            params.update(self.employee_id.partner_id.signup_get_auth_param()[self.employee_id.partner_id.id])

        return '%s?%s' % ('/mail/view' if redirect else self.access_url, url_encode(params))
