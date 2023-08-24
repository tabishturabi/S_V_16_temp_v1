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

class ServiceType(models.Model):
    _name = 'service.type'
    _inherit = ['mail.thread']
    _description = "Employee Service Type"
    _rec_name = "service_name"

    service_name = fields.Selection([('salary_intro_letter', 'Salary Introduction Letter'), ('letter_of_authority', 'Letter of Authority'), ('salary_transfer_letter', 'Salary Transfer Letter'), ('experience_certificate', 'Experience Certificate'), ('other', 'Other')],string="Service Name",required=True)
    active = fields.Boolean(string="Active", default=True, track_visibility=True)

    is_ceo = fields.Boolean(string="CEO Approval", default=False, track_visibility=True)

    is_deputy = fields.Boolean(string="Deputy CEO Approval", default=False, track_visibility=True)

    mail_template = fields.Many2one('mail.template', string='Mail Template', readonly=False, domain="[('model', '=', 'employee.service')]")

    # template_id = fields.Many2one('mail.template', string='Email Template',
    #                               domain="[('model','=','employee.service')]",
    #                               default=lambda self: self.env.ref('employee_service.submit_service_mail_manager_approve_temp'),
    #                               required=True)

    def name_get(self):
        res = []
        for rec in self:
            if rec.service_name == 'salary_intro_letter':
                name = "Salary Introduction Letter"
                res.append((rec.id, name))
            elif rec.service_name == 'letter_of_authority':
                name = "Letter of Authority"
                res.append((rec.id, name))
            elif rec.service_name == 'salary_transfer_letter':
                name = "Salary Transfer Letter"
                res.append((rec.id, name))
            elif rec.service_name == 'experience_certificate':
                name = "Experience Certificate"
                res.append((rec.id, name))
            else:
                name = "other"
                res.append((rec.id, name))
        return res

    @api.constrains('service_name')
    def _check_name(self):
        for rec in self:
            if self.env['service.type'].search([('id', '!=', rec.id), ('service_name', '=', rec.service_name)]):
                raise ValidationError(_("Can't create more than one service types with same service name."))



