# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    sub_type = fields.Selection([('Receipt', 'Receipt'), ('Payment', 'Payment'), ('All' ,'All')],string="Sub Type")
    receipt_sequnce_id = fields.Many2one('ir.sequence',string="Receipt Sequence")
    payment_sequnce_id = fields.Many2one('ir.sequence',string="Payment Sequence")
    # internal_sequnce_id = fields.Many2one('ir.sequence',string="Internal Sequence")
    is_allow_negative_transaction = fields.Boolean(string="Allowed Negative Transaction")
    is_not_allowed_past_payment = fields.Boolean(string="Is Not Allowed Past Payment")
    is_internal = fields.Boolean(string="IS Internal", default=False)
    transfer_branch_ids = fields.Many2many("bsg_branches.bsg_branches",'account_journal_transfer_branch_rel','journal_id','branch_id', string="Allowed Transferred Branch")