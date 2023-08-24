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


class ReasonEntry(models.Model):
    _name = 'reason.entry'
    # _inherit = ['mail.thread']
    _description = "Entry Reason"
    _rec_name = "description"

    # name = fields.Char(string='Name', readonly=False)

    description = fields.Text(string="Description", track_visibility=True, translate=True)
    active = fields.Boolean(string="Active", default=True, track_visibility=True)



class PermissionSettings(models.Model):
    _name = 'permission_settings'

    employee_sending = fields.Char(string="Sending From")
    employee_cc = fields.Char(string="Send Cc")

    employee_to = fields.Char(string="Send To")
    days_schedule = fields.Char(string="Days")
    interval_type = fields.Selection([('days', 'Day(s)'),
                                      ('weeks', 'Weeks(s)'),
                                      ('months', 'Months(s)'),
                                      ('months_last_day', 'Month(s) Last Day(s)'),
                                      ('year', 'Year(s)'), ], string='Interval Unit', default='days')

    
    def execute_settings(self):
        self.ensure_one()
        permission_config = self.env.ref('housing.permission_settings_data', False)
        permission_config.sudo().write({
            'employee_sending': self.employee_sending,
            'employee_cc': self.employee_cc,
            'employee_to': self.employee_to,
            'days_schedule': self.days_schedule,
            'interval_type': self.interval_type,
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def default_get(self, fields):
        res = super(PermissionSettings, self).default_get(fields)
        notification_permission = self.env.ref('housing.permission_settings_data', False)
        if notification_permission:
            res.update({
                'employee_sending': notification_permission.sudo().employee_sending,
                'employee_cc': notification_permission.sudo().employee_cc,
                'employee_to': notification_permission.sudo().employee_to,
                'days_schedule': notification_permission.sudo().days_schedule,
                'interval_type': notification_permission.sudo().interval_type,
            })
        return res
