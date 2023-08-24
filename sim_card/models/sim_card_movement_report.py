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



class SimCardReport(models.TransientModel):
    _name = 'sim.card.report'


    report_mode = fields.Selection([
        ('sim_card_delivery', 'SIM Card Movement Report by Delivery'),
        ('sim_card_receipt', 'SIM Card Movement Report by Receipts'),
        ('sim_card_upgrade', 'SIM Card Movement Report by Upgrade '),
        ('sim_card_lost', 'Replacement for Lost  SIM Request'),
    ], string='Report Mode',required=False)
    service_id = fields.Many2many('service.provider', string='Service provider')
    mble_no = fields.Many2many('sim.card.define', string='Sim Card')
    job_id = fields.Many2many('hr.job', string="Job Position")
    department_id = fields.Many2many('hr.department', string="Department")
    sim_type = fields.Selection(string="Sim Type", selection=[('voice', 'Voice'),
                                                              ('data', 'Data'), ],)
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
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

    pkg_id = fields.Many2many('package.type', string=" Package Type Name")
    branch_id = fields.Many2many('bsg_branches.bsg_branches', string='Branch')
    is_cost = fields.Selection(string="Bear The Cost", selection=[('company', 'Company'),
                                                                  ('employee', 'Employee')])
    
    def print_report(self):
        data = {
            'ids': self.ids,
            'model': self._name
        }
        return self.env.ref('sim_card.sim_card_report_id').report_action(self, data=data)






