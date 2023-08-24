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
from odoo.exceptions import Warning, ValidationError
from odoo.tools import config
import base64
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta


def get_date(days_count, years, months, days):
    if days_count <= 0:
        return years, months, days
    elif days_count >= 365:
        years += 1
        days_count = days_count - 365
        return get_date(days_count, years, months, days)
    elif days_count >= 30:
        months += 1
        days_count = days_count - 30
        return get_date(days_count, years, months, days)
    else:
        days = days + days_count
        days_count = days_count - days
        return get_date(days_count, years, months, days)


class EntryHousing(models.Model):
    _name = 'entry.housing'
    _inherit = ['mail.thread']
    _description = "Entry Housing"
    _rec_name = "name"

    name = fields.Char(string='Name', readonly=False)
    date = fields.Datetime(string='Entry Date', default=lambda self: fields.datetime.now(), track_visibility=True,
                           readonly=True)
    exit_date = fields.Datetime(string='Exiting Date', track_visibility=True, readonly=True)
    validate_date = fields.Datetime(string='Validate Date', track_visibility=True, readonly=True)
    employee_id = fields.Many2one('hr.employee', required=True, track_visibility=True)
    manager_id = fields.Many2one('hr.employee', readonly=True)

    @api.model
    def _default_created_id(self):
        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        return self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])

    created_id = fields.Many2one('hr.employee', default=_default_created_id, required=False, track_visibility=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Housing")

    housing_location = fields.Many2one('res.company', string='Company', readonly=True, index=True,
                                       default=lambda self: self.env.user.company_id,
                                       help="Company related to this Housing")

    house_location = fields.Many2one('bsg_branches.bsg_branches', string='House Location', readonly=True, index=True,
                                     default=lambda self: self.env.user.user_branch_id,
                                     help="Branch related to this Housing")
    mobile_phone = fields.Char(string='Mobile Number', required=False, track_visibility=True)
    sticker_no = fields.Char(string='Sticker No', readonly=True)
    vehicle_name = fields.Many2one('fleet.vehicle.model', string="Vehicle Name", track_visibility=True, readonly=True)
    vehicle_type_id = fields.Many2one('bsg.vehicle.type.table', string='Vehicle Type Name', readonly=True)
    branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Branch Name', readonly=True)
    department_id = fields.Many2one('hr.department', string="Department", readonly=True)
    job_id = fields.Many2one('hr.job', string="Job Position", readonly=True)
    house_seq = fields.Many2one('exit.housing', string='Exiting House seq', readonly=True)
    reason_id = fields.Many2one('reason.entry', string='Entry Reason Type', required=True)
    description = fields.Text(string="Description", track_visibility=True, translate=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", readonly=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string="Analytic Tags", track_visibility='always',
                                        readonly=True)
    active = fields.Boolean(string="Active", default=True, track_visibility=True)
    state = fields.Selection(string="state", selection=[('draft', 'Draft'), ('done', 'Done')],
                             default='draft', track_visibility=True)
    employee_code = fields.Char(string='Employee ID', readonly=True)
    bsg_empiqama = fields.Many2one('hr.iqama', string='Employee Iqama ID', readonly=True)
    bsg_national_id = fields.Many2one('hr.nationality', string='Employee National ID', readonly=True)
    date1 = fields.Date(string='Housing', compute='_compute_date1_count', store=True)

    @api.depends('date')
    def _compute_date1_count(self):
        for rec in self:
            if rec.date:
                rec.date1 = rec.date.date()

    days_count = fields.Char(string='Days', compute='_compute_days')

    @api.constrains('employee_id')
    def _check_name(self):
        for record in self:
            curr_obj = self.env[self._name].search(
                [('id', '!=', record.id), ('employee_id', '=', record.employee_id.id), ('house_seq', '=', False)])
            if curr_obj:
                raise ValidationError(
                    _('This Employer Has Previous Permission To Entry The Housing %s' % curr_obj.name))

    def _compute_days(self):
        for rec in self:
            if rec.date and rec.exit_date:
                delta = rec.exit_date - rec.date
                year, month, day = get_date(int(delta.days), 0, 0, 0)
                rec.days_count = "{0} Year {1} Months {2} Days".format(year,month,day)
            else:
                if not rec.exit_date:
                    delta = rec.date.date() - fields.date.today()
                    temp_days = delta.days
                    if int(temp_days) < 0:
                        temp_days = abs(int(delta.days))
                    year, month, day = get_date(int(temp_days), 0, 0, 0)
                    year = -year
                    month = -month
                    day = -day
                    rec.days_count = "{0} Year {1} Months {2} Days".format(year, month, day)


    
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('You Can Delete Record Only In Draft State'))
        return super(EntryHousing, self).unlink()

    
    @api.onchange('employee_id')
    def get_employee_data(self):
        if self.employee_id:
            self.manager_id = self.employee_id.parent_id
            self.company_id = self.employee_id.company_id
            self.branch_id = self.employee_id.branch_id
            self.department_id = self.employee_id.department_id
            self.job_id = self.employee_id.job_id
            self.mobile_phone = self.employee_id.mobile_phone
            self.employee_code = self.employee_id.employee_code
            self.bsg_empiqama = self.employee_id.bsg_empiqama
            self.bsg_national_id = self.employee_id.bsg_national_id
            self.analytic_account_id = self.employee_id.contract_id.analytic_account_id
            data = self.env['fleet.vehicle'].search([('bsg_driver', '=', self.employee_id.id)], limit=1)
            self.sticker_no = data.taq_number
            self.vehicle_type_id = data.vehicle_type
            self.vehicle_name = data.model_id

    house_count = fields.Integer('Number of House')

    def _compute_house_count(self):
        for record in self:
            record.house_count = self.env['entry.housing'].search_count([('employee_id', '=', self.employee_id.id)])

    
    def action_validate(self):
        self._compute_house_count()
        house = self.env['hr.employee'].search([('id', '=', self.employee_id.id)], limit=1)
        for rec in house:
            self.employee_id.house_count = self.house_count
        return self.write({'state': 'done', 'validate_date': datetime.now()})

    @api.model
    def create(self, vals):
        res = super(EntryHousing, self).create(vals)
        if self.env.user.user_branch_id.branch_no:
            res.name = 'ENTH' + self.env.user.user_branch_id.branch_no + self.env['ir.sequence'].next_by_code(
                'entry.housing')
        else:
            res.name = 'ENTH' + self.env['ir.sequence'].next_by_code('entry.housing')
        return res
