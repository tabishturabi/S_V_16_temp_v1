# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = 'account.journal'
  
    is_bx_cc_journal = fields.Boolean(string="IS BX CC JOURNAL", default=False)