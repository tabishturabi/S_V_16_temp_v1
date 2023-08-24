# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class HrTerminationType(models.Model):
    _name = 'hr.termination.type'
    _rec_name = 'name'
    _description = 'Termination Type'


    name = fields.Char(string="Name", required=True, )
    allowance_ids = fields.Many2many('hr.salary.rule',string="Allowances")
    allowance_id = fields.Many2one('hr.salary.rule',string="Allowance")
    clearance = fields.Boolean(string='Clearance')
    holiday = fields.Boolean(string='Holiday Allowance?')
    apply_in_resignation = fields.Boolean(string='Apply In Resignation')
    can_request_by_employee = fields.Boolean(string='Can Request By Employee')
    holiday_allowance = fields.Many2one('hr.salary.rule', string="Holiday Allowance")
    holiday_deduction = fields.Many2one('hr.salary.rule', string="Holiday Deduction")
    factor = fields.Float(string="Factor")
    reason_type = fields.Selection([('termination', 'Termination'), ('resign','Resignation'), ('end', 'End of Contract')], required=True)
    termination_duration_ids = fields.Many2many('hr.termination.duration',string='Termination Duration')

class HrTerminationDuration(models.Model):
    _name = 'hr.termination.duration'
    _description = 'Termination Duration'

    name = fields.Char(string='Name',required=True)
    date_from = fields.Float(string="Day From")
    date_to = fields.Float(string="Day To")
    factor = fields.Float(string="Duration In Days")
    amount = fields.Float(string="Amount",digits=(16, 5))
    hr_termination_type = fields.Many2one('hr.termination.type',string="HR Termination Type")

    # @api.depends('date_from','date_to')
    # def compute_factor(self):
    #     for rec in self:
    #         rec.factor = (rec.date_to - (rec.date_from-1))

