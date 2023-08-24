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
from odoo.exceptions import Warning, ValidationError
from odoo.tools import config
import base64
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta


class SimCardDefine(models.Model):
    _name = 'sim.card.define'
    _inherit = ['mail.thread']
    _description = "Sim Card define"
    _rec_name = 'mble_no'

    pkg_id = fields.Many2one('package.type', string=" Package Type Name", required=True, track_visibility=True)
    mble_no = fields.Char(string='Mobile Number', required=True, track_visibility=True, ondelete='cascade', index=True)
    service_id = fields.Many2one('service.provider', string='Service provider', required=True, track_visibility=True)
    owner_id = fields.Many2one('sim.owner', string='Sim Card Owner', required=True, track_visibility=True)
    branch_id = fields.Many2many('bsg_branches.bsg_branches', string='Branch', track_visibility=True)
    department_id = fields.Many2many('hr.department', string="Department", track_visibility=True)
    job_id = fields.Many2many('hr.job', string="Job Position", track_visibility=True)
    company_id = fields.Many2one('res.company', string='Company', required=False, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Sim Card")
    date = fields.Datetime(string=' Activation Date', track_visibility=True, default=lambda self: fields.datetime.now())
    is_cost = fields.Selection(string="Bear The Cost", selection=[('company', 'Company'),
                                                                  ('employee', 'Employee'), ], default='company',
                               track_visibility=True)
    employee = fields.Many2one('hr.employee', string="Current Employee", readonly=True, track_visibility=True)
    last_delivery_seq_id = fields.Many2one('sim.card.delivery', string="Last Delivery Seq No", readonly=True,
                                           track_visibility=True)
    last_receipt_seq_id = fields.Many2one('sim.card.receipt', string="Last Receipt Seq", readonly=True,
                                          track_visibility=True)
    notes = fields.Text(string="Internal Notes", track_visibility=True)
    sim_type = fields.Selection(string="Sim Type", selection=[('voice', 'Voice'),
                                                              ('data', 'Data'), ], default='voice', required=True,
                                track_visibility=True)
    contract_no = fields.Char(string='Contract Number:',related='service_id.contract_no', readonly=True, track_visibility=True)
    imis_no = fields.Integer(string='IMIS NO', track_visibility=True)
    msisdn = fields.Integer(string='MSISDN', track_visibility=True)
    id_no = fields.Integer(string='Id No', track_visibility=True)
    delivery_seq_id = fields.Many2one('sim.card.delivery', string="current Delivery Seq No", readonly=True,
                                      track_visibility=True)
    description = fields.Text(string="Description", track_visibility=True, translate=True)
    check = fields.Boolean(string='Check', default=False)
    active = fields.Boolean(string="Active", default=True, track_visibility=True)

    @api.onchange('state')
    def _onchange_state(self):
        for rec in self:
            if not self.check and rec.state.action_type == 'delivery':
                raise ValidationError('You can Not Change this state')

    
    def write(self, values):
        if not "check" in values:
            if 'state' in values and self.state.action_type == 'delivery':
                raise ValidationError(_("You can Not Change this stage !"))
        values['check'] = False
        return super(SimCardDefine, self).write(values)

    @api.constrains('mble_no')
    def _check_name(self):
        for record in self:
            if self.env[self._name].search([('id', '!=', record.id), ('mble_no', '=', record.mble_no)]):
                raise ValidationError('Mobile Number with %s already exist.' % record.mble_no)

    
    def unlink(self):
        if self.state.action_type != 'cancelled':
            raise UserError(_('You Can Not Delete Record State in Receipt and Delivery'))
        return super(SimCardDefine, self).unlink()

    def _get_default_state_id(self):
        state = self.env.ref('sim.status', raise_if_not_found=False)
        return state if state and state.id else False

    def _default_state(self):
        return self.env['sim.status'].search([('action_type', '=', 'receipt')], limit=1).id

    @api.model
    def _read_group_stage_id(self, stages, domain, order):
        return self.env['sim.status'].search([], order=order)

    state = fields.Many2one('sim.status', 'State', track_visibility="onchange", ondelete="set null",
                            group_expand='_read_group_stage_id',
                            default=_default_state, )
    attachment_ids = fields.Many2many('ir.attachment', track_visibility=True)
    property_account_income_id = fields.Many2one('account.account', track_visibility=True, company_dependent=True,
                                                 string="Income Account", oldname="property_account_income",
                                                 domain=[('deprecated', '=', False)],
                                                 help="Keep this field empty to use the default value from the product category.")
    property_account_expense_id = fields.Many2one('account.account', company_dependent=True, track_visibility=True,
                                                  string="Expense Account", oldname="property_account_expense",
                                                  domain=[('deprecated', '=', False)],
                                                  help="Keep this field empty to use the default value from the product category. If anglo-saxon accounting with automated valuation method is configured, the expense account on the product category will be used.")
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    request_count = fields.Integer(string='Request')
    delivered_id = fields.Many2one('sim.card.delivery', string="delivered ID")
    delivered_count = fields.Integer(string='delivered')
    receipt_id = fields.Many2one('sim.card.receipt', string="Receipt ID")
    receipt_count = fields.Integer(string='Receipt')

    def compute_receipt_count_view(self):
        return {
            'name': 'delivery receipt',
            'domain': [('id', '=', self.receipt_id.id)],
            'res_model': 'sim.card.receipt',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            "views": [[self.env.ref('sim_card.sim_card_receipt_tree_vieww1').id, "tree"],
                      [self.env.ref('sim_card.sim_card_receipt_form_view').id, "form"]],
        }

    def compute_delivered_count_view(self):
        return {
            'name': 'delivery',
            'domain': [('id', '=', self.delivered_id.id)],
            'res_model': 'sim.card.delivery',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            "views": [[self.env.ref('sim_card.sim_card_delivery_tree_vieww1').id, "tree"],
                      [self.env.ref('sim_card.sim_card_delivery_form_view').id, "form"]],
        }

    def run_first(self):
        data = self.env['sim.card.define'].search([])
        for d in data:
            d.get_service_id_data()

    
    def sale_count(self):
        count_list = self.env['sim.card.define'].search([('state', '=', 'delivered')])
        count = len(count_list)
        self.state = count

    
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'sim.card.define'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for card_no in self:
            card_no.attachment_number = attachment.get(card_no.id, 0)

    
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('sim_card.action_attachment_sim_card_define')
        return res
