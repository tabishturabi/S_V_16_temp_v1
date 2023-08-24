# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class AccountMoveReportWizard(models.TransientModel):
    _name = 'account.move.report.wizard'

    date_from = fields.Date(string='From',required=True)
    date_to = fields.Date(string='To',required=True)
    account_ids = fields.Many2many('account.account', string='Account',required=True)
    is_partner = fields.Boolean(string='Group By Partner')
    print_date = fields.Date(string='Today Date',default=fields.date.today())



    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_account_move_report.account_move_report_xlsx_id').report_action(self,data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_account_move_report.sales_revenue_report_pdf_id').report_action(self,data=data)










