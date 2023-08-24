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



class HouseMovement(models.TransientModel):
    _name = 'house.movement'

    report_mode = fields.Selection([
        ('house_movement', 'House Movement Report'),
        ('house_movement_transaction_type', 'House Movement Report Grouping By Transaction Type'),
        ('house_movement_employee_type', 'House Movement Report Grouping By Employee Type'),
        ('house_movement_period', 'House Movement Report Grouping By Period'),
        ('house_movement_house_location', 'House Movement Report Grouping By House Location'),
    ], string='Report Mode',default="house_movement",required=False)

    house_location = fields.Many2many('bsg_branches.bsg_branches', string='House Location', help="Branch related to this Housing")

    company_id = fields.Many2many('res.company', string='Company', help="Company related to this Housing")
    job_id = fields.Many2many('hr.job', string="Job Position")
    department_id = fields.Many2many('hr.department', string="Department")
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    sticker_no = fields.Char(string='Sticker No', readonly=True)
    vehicle_type_id = fields.Many2many('bsg.vehicle.type.table', string='Vehicle Type')

    active = fields.Boolean(string="Still In The Housing..?", default=False)
    created_id = fields.Many2many('hr.employee', string="Created By")
    vehicle_id = fields.Many2many('fleet.vehicle',string="Sticker No")

    name = fields.Char(string='Name', readonly=False)
    date = fields.Datetime(string='Entry Date', default=lambda self: fields.datetime.now(), track_visibility=True,
                           readonly=False)

    is_still_house = fields.Char('Is Still At After House')
    interval_type = fields.Selection([('days', 'Day(s)'),
                                      ('weeks', 'Weeks(s)'),
                                      ('months', 'Months(s)'),
                                      ('months_last_day', 'Month(s) Last Day(s)'),
                                      ('year', 'Year(s)'), ], string='Interval Unit')

    
    @api.onchange('active')
    def get_setting_data(self):
        rec = self.env['permission_settings'].search([], limit=1)
        if not self.active:
            self.is_still_house = False
            self.interval_type = False
        if self.active:
            self.is_still_house = rec.days_schedule
            self.interval_type = rec.interval_type



    day_condition = fields.Selection([
        ('is equal to', 'is equal to'),
        ('is not equal to', 'is not equal to'),
        ('is after', 'is after'),
        ('is before', 'is before'),
        ('is after or equal to', 'is after or equal to'),
        ('is before or equal to', 'is before or equal to'),
        ('is between', 'is between'),
        ('is set', 'is set'),
        ('is not set', 'is not set'),
    ], string='Movement Date Condition')

    period_group = fields.Selection([
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('Quarter', 'Quarter'),
        ('year', 'Year'),
    ], string='Period Grouping By')

    transaction_type = fields.Selection([
        ('all', 'All'),
        ('entry_housing', 'Entry Housing'),
        ('exit_housing', 'Exit Housing'),
    ], string='Transaction Type',default="all")

    branch_id = fields.Many2many('bsg_branches.bsg_branches', 'bsg_branches_house_rel', column1='house_movement_id', column2='bsg_branch_id', string='Branch')

    
    def print_report(self):
        data = {
            'ids': self.ids,
            'model': self._name
        }
        return self.env.ref('housing.house_movement_report_id').report_action(self, data=data)

    
    def get_notification(self):
        data = self.read()
        report = self.env['ir.actions.report']. \
            _get_report_from_name('housing.house_movement_report_temp_xlsx')
        xlsx_ = report.render_xlsx(self.ids, data)
        excel_file = base64.encodestring(xlsx_[0])
        attachment_id = self.env['ir.attachment'].create({
            'name': 'House_movement.xlsx',
            'datas': excel_file,
            'store_fname': 'House_movement.xlsx',
            'type': 'binary'
        })
        return attachment_id






