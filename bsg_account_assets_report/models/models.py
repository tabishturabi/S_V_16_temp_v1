# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class AccountAssetReportWizard(models.TransientModel):
    _name = 'account.asset.report'

    date_from = fields.Date(string='From',required=True)
    date_to = fields.Date(string='To',required=True)
    with_details = fields.Boolean(string='With Details')
    assets_type = fields.Selection([("all", "All"), ("purchase", "Assets"), ("sale", "Deferred Revenue"),
                                    ("expense", "Deferred Expense")], default="purchase")
    print_date = fields.Date(string='Today Date', default=fields.date.today())

    @api.onchange('date_to')
    def onchange_to(self):
        if self.date_to < self.date_from:
            raise UserError('Date to must be greater than or equal to date from')



    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_account_assets_report.asset_report_xlsx_id').report_action(self,data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_account_assets_report.asset_report_pdf_id').report_action(self,data=data)












