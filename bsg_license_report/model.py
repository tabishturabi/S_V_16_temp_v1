import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError, UserError
from odoo.tools import config
import base64
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import xlwt
import base64
from io import BytesIO
from xlwt import *


class XlsxReportBranchLicense(models.TransientModel):
    _name = 'bsg.license.report'
    _inherit = 'report.report_xlsx.abstract'

    form = fields.Date(string='From')

    to = fields.Date(string='To')
    date = fields.Date(string='Date')
    branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="Branches")
    doc_type = fields.Many2many('bsg.branch.doc.type', string="Document Type")
    date_type = fields.Selection([
        ('is equal to', 'is equal to'),
        ('is not equal to', 'is not equal to'),
        ('is after', 'is after'),
        ('is before', 'is before'),
        ('is after or equal to', 'is after or equal to'),
        ('is before or equal to', 'is before or equal to'),
        ('is between', 'is between'),
        ('is set', 'is set'),
        ('is not set', 'is not set'),
    ], string='Date Condition')

    report_mode = fields.Selection([
        ('All Details', 'All Details'),
        ('Document Type', 'Document Type'),
    ], string='Report Mode', default="All Details")

    filter_type = fields.Selection([
        ('By Issue Date', 'By Issue Date'),
        ('By Expiry Date', 'By Expiry Date'),
        ('By Due To Renewal', 'By Due To Renewal'),
        ('By Latest Renewal Date', 'By Latest Renewal Date'),
    ], string='Filter By')

    is_between = fields.Boolean()
    others = fields.Boolean()
    report_file = fields.Binary('report file')

    @api.onchange('date_type')
    def onchange_date_type(self):
        if self.date_type:
            if self.date_type == "is between":
                self.is_between = True
                self.others = False

            if self.date_type != "is between":
                if self.date_type == "is set" or self.date_type == "is not set":
                    self.is_between = False
                    self.others = False
                else:
                    self.is_between = False
                    self.others = True

    # @api.multi
    def print_report(self):

        all_recs = self.env['bsg.license.info'].search([], limit=1)

        if all_recs:
            self.ensure_one()
            [data] = self.read()
            datas = {
                'ids': [],
                'model': 'bsg.license.info',
                'form': data,
            }

            report = self.env['ir.actions.report']. \
                _get_report_from_name('bsg_license_report.bsg_license_report_xlsx')

            # print(report, all_recs, datas, 1111111111111111111)
            print(report.render_xlsx([], datas))
            # report.report_file = self._get_report_base_filename()
            report = self.env.ref('bsg_license_report.action_bsg_license_report').report_action(all_recs, data=datas)
            return report
        else:
            raise UserError(_('There is no record in given date'))

    # @api.multi
    def get_notification(self):
        all_recs = self.env['bsg.license.info'].search([], limit=1)

        if all_recs:
            self.ensure_one()
            [data] = self.read()
            datas = {
                'ids': [],
                'model': 'bsg.license.info',
                'form': data,
            }
        report = self.env['ir.actions.report']. \
            _get_report_from_name('bsg_license_report.bsg_license_report_xlsx')
        xlsx_ = report.render_xlsx(all_recs, datas)

        excel_file = base64.encodestring(xlsx_[0])

        attachment_id = self.env['ir.attachment'].create({
            'name': 'license report.xlsx',
            'datas': excel_file,
            'store_fname': 'license report.xlsx',
            'type': 'binary'
        })
        return attachment_id
