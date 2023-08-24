# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'


    swift_code = fields.Char('Swift Code')
    commission_type = fields.Selection([('amount','Amount'), ('percent','Percent')],' Commission Type')
    commission_value = fields.Float('Commission Value')
    commission_account_id = fields.Many2one('account.account', string='Commission Account')
    commission_tax_type = fields.Selection([('amount','Amount'), ('percent','Percent')],'Commission Tax Type')
    commission_tax_value = fields.Float('Commission Tax Value')
    commission_tax_account_id= fields.Many2one('account.account', string='Commission Tax Account')
    