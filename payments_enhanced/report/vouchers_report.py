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


class VouchersReports(models.TransientModel):
    _name = 'vouchers.reports'

    form = fields.Date(string='From')
    to = fields.Date(string='To')
    file = fields.Binary('Download Report')
    name = fields.Char()

    payment_type = fields.Selection([
        ('all', 'All'),
        ('inbound', 'Receipt Vouchers'),
        ('outnbound', 'Payment Vouchers'),
    ], string='Payment Type')

    # @api.multi
    def report_for__xls(self):
        data = {
            'ids': self.ids,
            'model': self._name
        }
        return self.env.ref('payments_enhanced.voucher_report_id').report_action(self, data=data)
