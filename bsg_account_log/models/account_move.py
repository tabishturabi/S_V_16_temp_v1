# -*- coding: utf-8 -*-

import time
from datetime import date
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang, format_date
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp
from lxml import etree

class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move','mail.thread']
    

    # @api.multi
    def _get_default_journal(self):
        if self.env.context.get('default_journal_type'):
            return self.env['account.journal'].search([('company_id', '=', self.env.user.company_id.id), ('type', '=', self.env.context['default_journal_type'])], limit=1).id

    name = fields.Char(string='Number', required=True, copy=False, default='/', track_visibility=True)
    ref = fields.Char(string='Reference', copy=False, track_visibility=True)
    date = fields.Date(required=True, states={'posted': [('readonly', True)]}, index=True, default=fields.Date.context_today, track_visibility=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, states={'posted': [('readonly', True)]}, default=_get_default_journal, track_visibility=True)
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', store=True, string="Currency", track_visibility=True)
    state = fields.Selection([('draft', 'Unposted'), ('posted', 'Posted')], string='Status',
      required=True, readonly=True, copy=False, default='draft',
      help='All manually created new journal entries are usually in the status \'Unposted\', '
           'but you can set the option to skip that status on the related journal. '
           'In that case, they will behave as journal entries automatically created by the '
           'system on document validation (invoices, bank statements...) and will be created '
           'in \'Posted\' status.', track_visibility=True)
    line_ids = fields.One2many('account.move.line', 'move_id', string='Journal Items',
        states={'posted': [('readonly', True)]}, copy=True, track_visibility=True)
    partner_id = fields.Many2one('res.partner', compute='_compute_partner_id', string="Partner", store=True, readonly=True, track_visibility=True)
    # amount = fields.Monetary(compute='_amount_compute', store=True, track_visibility=True)
    narration = fields.Html(string='Internal Note', track_visibility=True)
    # company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', store=True, readonly=True, track_visibility=True)
    # matched_percentage = fields.Float('Percentage Matched', compute='_compute_matched_percentage', digits=0, store=True, readonly=True, help="Technical field used in cash basis method", track_visibility=True)
    # Dummy Account field to search on account.move by account_id
    dummy_account_id = fields.Many2one('account.account', related='line_ids.account_id', string='Account', store=False, readonly=True, track_visibility=True)
    tax_cash_basis_rec_id = fields.Many2one(
        'account.partial.reconcile',
        string='Tax Cash Basis Entry of',
        help="Technical field used to keep track of the tax cash basis reconciliation. "
        "This is needed when cancelling the source: it will post the inverse journal entry to cancel that part too.", track_visibility=True)
    auto_reverse = fields.Boolean(string='Reverse Automatically', default=False, help='If this checkbox is ticked, this entry will be automatically reversed at the reversal date you defined.', track_visibility=True)
    reverse_date = fields.Date(string='Reversal Date', help='Date of the reverse accounting entry.', track_visibility=True)
    reverse_entry_id = fields.Many2one('account.move', String="Reverse entry", store=True, readonly=True, track_visibility=True)
    tax_type_domain = fields.Char(store=False, help='Technical field used to have a dynamic taxes domain on the form view.', track_visibility=True)

    # @api.depends('line_ids.debit', 'line_ids.credit', 'line_ids.matched_debit_ids.amount','line_ids.matched_credit_ids.amount', 'line_ids.account_id.user_type_id.type')
    # @api.depends('line_ids.debit', 'line_ids.credit', 'line_ids.matched_debit_ids.amount','line_ids.matched_credit_ids.amount', 'line_ids.account_id.account_type')
    # def _compute_matched_percentage(self):
    #     """Compute the percentage to apply for cash basis method. This value is relevant only for moves that
    #     involve journal items on receivable or payable accounts.
    #     """
    #     pass
    #     # for move in self:
    #     #     total_amount = 0.0
    #     #     total_reconciled = 0.0
    #     #     for line in move.line_ids:
    #     #         # if line.account_id.user_type_id.type in ('receivable', 'payable'):
    #     #         if line.account_id.account_type in ('receivable', 'payable'):
    #     #             amount = abs(line.balance)
    #     #             total_amount += amount
    #     #     precision_currency = move.currency_id or move.company_id.currency_id

    #     #     if float_is_zero(total_amount, precision_rounding=precision_currency.rounding):
    #     #         move.matched_percentage = 1.0
    #     #     else:
    #     #         for line in move.line_ids:
    #     #             if line.account_id.user_type_id.type in ('receivable', 'payable'):
    #     #                 for partial_line in (line.matched_debit_ids + line.matched_credit_ids):
    #     #                     total_reconciled += partial_line.amount
    #     #         move.matched_percentage = precision_currency.round(total_reconciled) / precision_currency.round(
    #     #             total_amount)
