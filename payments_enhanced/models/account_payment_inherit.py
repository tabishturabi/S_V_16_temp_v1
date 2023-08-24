# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo import Command
from odoo.tools import float_compare
import datetime
from odoo.osv import expression
from lxml import etree
# Migration Note
# from odoo.osv.orm import setup_modifiers
from itertools import groupby
from odoo.addons import decimal_precision as dp
from num2words import num2words
import json

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': -1,
    'in_invoice': -1,
    'out_refund': 1,
}


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _seek_for_lines(self):
        ''' Helper used to dispatch the journal items between:
        - The lines using the temporary liquidity account.
        - The lines using the counterpart account.
        - The lines being the write-off lines.
        :return: (liquidity_lines, counterpart_lines, writeoff_lines)
        '''
        self.ensure_one()

        liquidity_lines = self.env['account.move.line']
        counterpart_lines = self.env['account.move.line']
        writeoff_lines = self.env['account.move.line']

        for line in self.move_id.line_ids:
            if line.account_id in self._get_valid_liquidity_accounts():
                liquidity_lines += line

            elif line.account_id.account_type in ('income_other','income','expense','expense_direct_cost','asset_receivable', 'liability_payable') or line.account_id == self.company_id.transfer_account_id:
                counterpart_lines += line
            else:
                writeoff_lines += line

        return liquidity_lines, counterpart_lines, writeoff_lines

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(AccountPayment, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        if self.env.context.get('from_payment_voucher') and view_type == 'form' and self.env.user.has_group(
                'payments_enhanced.group_payment_voucher_read_only'):
            doc = etree.XML(result['arch'])
            for t in doc.xpath("//form"):
                t.set('edit', "false")
                t.set('create', "false")
            result['arch'] = etree.tostring(doc)
            method_nodes = doc.xpath("//field")
            for node in method_nodes:
                node.set('readonly', "1")
                # Migration Note
                # setup_modifiers(node, result['fields'][node.get('name', False)])
            result['arch'] = etree.tostring(doc)
        return result

    # CONSTRAIS METHOD
    # Amount vlaue should not be 0

    # @api.constrains('amount')
    # def _check_amount(self):
    #     if not self.amount:
    #         raise UserError(_('Voucher Amount must be greater than 0...!'))

    # Overiding Unlink method to disallow user to delete voucher when sequnce was created
    # @api.multi
    def unlink(self):
        for payment in self:
            if payment.is_sequnce:
                raise UserError(
                    _('You can not delete a Voucher if sequnce is created...!'),
                )
        return super(AccountPayment, self).unlink()

    @api.model
    def update_cargo_sale_id(self):
        for data in self.search(
                [('state', '!=', 'draft'), ('payment_type', '=', 'inbound'), ('cargo_sale_order_id', '=', False)]):
            if data.communication:
                cargo_sale_number = data.communication.split('-')
                if cargo_sale_number:
                    search_cargo_id = self.env['bsg_vehicle_cargo_sale'].search([('name', '=', cargo_sale_number[0])])
                    if search_cargo_id:
                        data.write({'cargo_sale_order_id': search_cargo_id.id})

    # @api.multi
    def get_arabic_total_word(self, amount):
        word = num2words(float("%.2f" % amount), lang='ar')
        word = word.title()
        warr = str(("%.2f" % amount)).split('.')
        if self.currency_id.name == 'SAR':
            ar = ' ريال' if str(warr[1]) == '00' else ' هلله'
            rword = str(word).replace(',', ' ريال و ') + ar
            # rword = str(rword).replace('ريال و ', 'فاصلة')
        elif self.currency_id.name == 'AED':
            ar = ' درهم' if str(warr[1]) == '00' else ' فلس'
            rword = str(word).replace(',', ' درهم و ') + ar
            # rword = str(rword).replace('ريال و ', 'فاصلة')
        elif self.currency_id.name == 'JOD':
            ar = ' دينار' if str(warr[1]) == '00' else ' فلس'
            rword = str(word).replace(',', ' دينار و ') + ar
            # rword = str(rword).replace('ريال و ', 'فاصلة')
        elif self.currency_id.name == 'OMR':
            ar = ' ريال' if str(warr[1]) == '00' else ' بيسة'
            rword = str(word).replace(',', ' ريال و ') + ar
            # rword = str(rword).replace('ريال و ', 'فاصلة')
        else:
            ar = ' ريال' if str(warr[1]) == '00' else ' هلله'
            rword = str(word).replace(',', ' ريال و ') + ar
            # rword = str(rword).replace('ريال و ', 'فاصلة')
        return rword

    # @api.multi
    def write(self, vals):
        if vals.get('state') == 'cancelled' or vals.get('state') == 'reversal_entry':
            if self.receipt_voucher:
                for data in self.search([('id', 'in', json.loads(self.receipt_voucher))]):
                    data.update({'is_budget_recon': False})
        if vals.get('invoice_ids'):
            self.update({'state': 'posted'})
        res = super(AccountPayment, self).write(vals)
        return res

    # @api.model
    # def create(self, vals):
    #     if self._context.get('pass_sale_order_id'):
    #         vals['cargo_sale_order_id'] = self._context.get('pass_sale_order_id')
    #     if self._context.get('default_partner_id'):
    #         vals['partner_id'] = self._context.get('default_partner_id')
    #     res = super(AccountPayment, self).create(vals)
    #     # res.cargo_sale_line_order_ids = res.invoice_ids.cargo_sale_id.order_line_ids
    #     # res._onchange_cargo_sale_line_order_ids()
    #     res.show_invoice_amount = False
    #     if not res.cargo_sale_order_id and res.communication:
    #         search_cargo_id = self.env['bsg_vehicle_cargo_sale'].search([('name', '=', res.communication)])
    #         if search_cargo_id:
    #             res.cargo_sale_order_id = search_cargo_id.id
    #     if res.cargo_sale_order_id.payment_method.payment_type == 'pod':
    #         res.branch_ids = self.env.user.user_branch_id.id
    #     else:
    #         if not res.branch_ids:
    #             if res.cargo_sale_order_id:
    #                 if res.cargo_sale_order_id.loc_from.loc_branch_id.id in res.journal_id.branches.ids:
    #                     res.branch_ids = res.cargo_sale_order_id.loc_from.loc_branch_id.id
    #                 # if not res.branch_ids:
    #                 #     if res.cargo_sale_order_id.loc_to.loc_branch_id.id in res.journal_id.branches.ids:
    #                 #         res.branch_ids = res.cargo_sale_order_id.loc_from.loc_branch_id.id
    #             if not res.branch_ids:
    #                 brnch_list = []
    #                 for data in self.env['bsg_branches.bsg_branches'].search(
    #                         [('member_ids.user_id', '=', self.env.user.id)]):
    #                     for branch_data in res.journal_id.branches:
    #                         if branch_data.id == data.id:
    #                             res.branch_ids = data.id
    #     if not res.branch_ids:
    #         res.branch_ids = self.env.user.user_branch_id.id
    #     res.name = "*" + str(res.id)
    #     return res

    # @api.onchange('is_more_amount')
    # def _onchange_more_amoutn(self):
    #     if self.is_more_amount:
    #         self.is_more_amount = True
    #         raise Warning(_("You cannot Pay More than Amount "))

    # 
    # def _get_access_val(self):
    #     if self.env.user.has_group('payments_enhanced.group_confirming_voucher') or self.env.user.has_group('payments_enhanced.group_posting_voucher') or self.env.user.has_group('base.group_erp_manager'):
    #         self.have_access = True
    #     else:
    #         self.have_access = False

    @api.depends('show_invoice_amount', 'is_patrtially_payment')
    def _get_total_invoice_amount(self):
        if self._context.get('pass_sale_order_id'):
            amount_total = 0
            due_amount = 0
            if self.show_invoice_amount or self.is_patrtially_payment:
                for invoice in self.env['account.move'].search(
                        [('cargo_sale_id', '=', self._context.get('pass_sale_order_id'))]):
                    amount_total += invoice.amount_total
                    due_amount += invoice.residual
                self.total_invoice_amount = amount_total
                self.due_invoice_amount = due_amount

    # @api.multi
    def cancel_payment(self):
        # no need to these sequnce for now 
        # if self.is_sequnce:
        #     if self.payment_type == 'inbound':
        #         if self.journal_id.receipt_sequnce_id:
        #             if self.journal_id.receipt_sequnce_id.date_range_ids:
        #                 for data in self.journal_id.receipt_sequnce_id.date_range_ids:
        #                     data.write({'number_next_actual' : (data.number_next_actual - 1)})
        #             else:
        #                 self.journal_id.receipt_sequnce_id.write({'number_next_actual' : (self.journal_id.receipt_sequnce_id.number_next_actual - 1)})                
        #     elif self.payment_type == 'outbound':
        #         if self.journal_id.payment_sequnce_id:
        #             if self.journal_id.payment_sequnce_id.date_range_ids:
        #                 for data in self.journal_id.payment_sequnce_id.date_range_ids:
        #                     data.write({'number_next_actual' : (data.number_next_actual - 1)})
        #             else:
        #                 self.journal_id.payment_sequnce_id.write({'number_next_actual' : (self.journal_id.receipt_sequnce_id.number_next_actual - 1)})                

        #     elif self.is_internal_transfer: 
        #         config = self.env.ref('payments_enhanced.res_config_sequnce_data', False)
        #         if config.sequnce_id:
        #                 if config.sequnce_id.date_range_ids:
        #                     for data in config.sequnce_id.date_range_ids:
        #                         data.write({'number_next_actual' : (data.number_next_actual - 1)})
        #                 else:
        #                    config.sequnce_id.write({'number_next_actual' : (config.sequnce_id.number_next_actual - 1)})                
        # # match_invoice_id = (self.move_line_ids.mapped('matched_debit_ids.debit_move_id.invoice_id') |
        #                                     self.move_line_ids.mapped('matched_credit_ids.credit_move_id.invoice_id'))

        # if self.reconciled_invoice_ids.cargo_sale_id: 
        #     self.reconciled_invoice_ids.cargo_sale_id.write({'state' : 'pod'})
        for rec in self:
            if not self.env.user.has_group("payments_enhanced.group_cancel_voucher"):
                if not self.env.user.has_group("payments_enhanced.group_cancel_internal_transfer"):
                    raise ValidationError('This user is not allowed to cancel this transaction')
                elif rec.payment_type != 'transfer':
                    raise ValidationError('This user is not allowed to cancel this transaction')
        '''for data in self.reconciled_invoice_ids:
            if data.cargo_sale_id: 
                data.cargo_sale_id.write({'state' : 'pod'})
        if self.state == 'voucher':
            search_cargo_id = self.env['bsg_vehicle_cargo_sale'].search([('name','=',self.communication)])
            if search_cargo_id:
                search_cargo_id.write({'state' : 'pod'})'''
        # for data in self.move_line_ids:
        #     data.remove_move_reconcile()
        self.cancel_jounral_id = self.journal_id.id
        for rec in self:
            for move in rec.invoice_line_ids.mapped('move_id'):
                if rec.invoice_ids:
                    move.line_ids.remove_move_reconcile()
                move.button_cancel()
                move.unlink()
        self.state = 'cancelled'

        # if match_invoice_id:
        #     self.env.cr.execute("UPDATE account_invoice set state='open' WHERE id=%s",(match_invoice_id.id,))
        #     if match_invoice_id.cargo_sale_id:
        #         match_invoice_id.cargo_sale_id.write({'state' : 'pod'})
        # self.state = 'cancelled'

    @api.depends('budget_number')
    def _get_budget_check(self):
        for rec in self:
            rec.is_budget_number = False
            if rec.budget_number:
                rec.is_budget_number = True

    def _get_group_update_trip(self):
        if self.env.user.has_group('payments_enhanced.group_update_trip'):
            self.is_group_update_trip = True
        else:
            self.is_group_update_trip = False

    def _get_access_change_memo(self):
        if self.env.user.has_group('payments_enhanced.group_change_memo'):
            if self.is_internal_transfer:
                self.is_access_change_memo = True
            else:
                self.is_access_change_memo = False
        else:
            self.is_access_change_memo = False

    def _get_group_so_voucher(self):
        if self.env.user.has_group('payments_enhanced.group_so_on_voucher'):
            self.is_group_so_on_voucher = True
        else:
            self.is_group_so_on_voucher = False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(AccountPayment, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        if self.env.context.get('from_payment_voucher') and view_type == 'form' and self.env.user.has_group(
                'payments_enhanced.group_payment_voucher_read_only'):
            doc = etree.XML(result['arch'])
            for t in doc.xpath("//form"):
                t.set('edit', "false")
                t.set('create', "false")
            result['arch'] = etree.tostring(doc)
            method_nodes = doc.xpath("//field")
            for node in method_nodes:
                node.set('readonly', "1")
                # Migration Note
                # setup_modifiers(node, result['fields'][node.get('name', False)])
            result['arch'] = etree.tostring(doc)
        return result

    # coll_ids = fields.Many2many('account.collection', string="Invoices ", copy=False, help="""Technical field containing the invoices for which the payment has been generated.
    #
    #                                                                                                                                                                    This does not especially correspond to the invoices reconciled with the payment,
    #                                                                                                                                                          as it can have been generated first, and reconciled later""")
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company.id,
                                 help='The default company for this user.')
    voucher_line_ids = fields.One2many('account.voucher.line.custom', 'payment_id', string="Voucher Line")
    collectionre = fields.Char("Collection Voucher ref")
    is_voucher_or_expense = fields.Boolean(string="Is Voucher/Expense")
    track_coll = fields.Boolean("Track_coll", default=False)
    branch_id = fields.Many2one('res.partner', string='Branch Customer')
    total_invoice_amount = fields.Float(string="Total Amount", compute="_get_total_invoice_amount")
    due_invoice_amount = fields.Float(string="Due Amount", compute="_get_total_invoice_amount")
    show_invoice_amount = fields.Boolean("Show Invoices Amount", copy=False)
    is_sequnce = fields.Boolean(string="Sequence", copy=False)
    state = fields.Selection(
        [('draft', 'Draft'), ('reversal_entry', 'Reversal Entry'), ('voucher', 'Voucher'), ('posted', 'Posted'),
         ('sent', 'Sent'), ('reconciled', 'Reconciled'), ('cancelled', 'Cancelled')], readonly=True, default='draft',
        copy=False, string="Status", track_visibility='always')
    description = fields.Text(string="Description")
    payment_method_name = fields.Char(related="payment_method_id.name", store=True)
    cheque_no = fields.Char(string="Cheaque No")
    is_more_amount = fields.Boolean(string="Is More Amount")
    communication = fields.Char(string='Memo', copy=False, track_visibility='always')
    is_access_change_memo = fields.Boolean(strig="Is access of Change Memo", compute="_get_access_change_memo")
    cancel_jounral_id = fields.Many2one('account.journal', string="Cancel Journal ID", copy=False)
    amount = fields.Monetary(string='Payment Amount', required=True, digits=dp.get_precision('Vouchers'),
                             track_visibility='always')
    have_access = fields.Boolean(string="Have Access")
    operation_number = fields.Char(string="Operation Number")
    budget_number = fields.Char(string="Budget Number", track_visibility='always')
    is_show_partial = fields.Boolean(string="IS Enable Partial Payment")
    is_patrtially_payment = fields.Boolean(string="Is Partially Payment")
    attachment_id = fields.Binary(string="Attachment")
    is_budget_number = fields.Boolean(string="IS Budget Number", compute="_get_budget_check", store=True)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))], track_visibility='always')
    tax_amount = fields.Float('Tax Amount')
    bank_charges = fields.Float('Bank Charges')
    is_group_update_trip = fields.Boolean(string="IS Update Group", compute="_get_group_update_trip")
    is_group_so_on_voucher = fields.Boolean(string="IS Group So Voucher", compute="_get_group_so_voucher")
    is_allow_pay_with_fc = fields.Boolean(string="Is Allowed Payment With FC")
    cargo_sale_order_id = fields.Many2one(string="Cargo Sale ID", comodel_name="bsg_vehicle_cargo_sale", copy=False)
    invoice_ids = fields.Many2many("account.move", string='Invoices', readonly=True,
                                   copy=False)
    # coll_ids1 = fields.Many2many('account.collection.vendor', string="Invoices", copy=False, readonly=True, help="""Technical field containing the invoices for which the payment has been generated.                                                                                                                                                               This does not especially correspond to the invoices reconciled with the payment,
    #                                                                                                                                                                        as it can have been generated first, and reconciled later""")
    collectionre = fields.Char("Collection Voucher ref")
    track_coll = fields.Boolean("Track_coll", default=False)
    branch_id = fields.Many2one('res.partner', string='Branch Customer')
    bsg_vehicle_cargo_sale_line_ids = fields.One2many('account.cargo.line.payment', 'account_payment_id',
                                                      string='So Line Payment')

    @api.constrains('date', 'journal_id')
    def _constrains_date_journal_id(self):
        for rec in self:
            if rec.journal_id and rec.journal_id.is_not_allowed_past_payment:
                if fields.Date.today() < rec.date:
                    raise ValidationError(_('You cannot create transaction in past date for selected journal!'))

    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        return {
            'date': self.date,
            'ref': self.ref or '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
            'collection': self.collectionre,
        }

    def _get_liquidity_move_line_vals(self, amount):
        name = self.collectionre or self.name
        if self.is_internal_transfer:
            name = _('Transfer to %s') % self.destination_journal_id.name
        vals = {
            'name': name,
            'account_id': self.payment_type in ('outbound') and self.is_internal_transfer and self.journal_id.default_account_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'branch_id': self.env.user.user_branch_id.id,
            'branch_name': self.env.user.user_branch_id.branch_name,
        }

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id._convert(amount, self.journal_id.currency_id, self.company_id,
                                               self.date or fields.Date.today())
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(
                date=self.date)._compute_amount_fields(amount, self.journal_id.currency_id,
                                                               self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals

    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        return {
            'partner_id': self.payment_type in ('inbound', 'outbound') and self.env[
                'res.partner']._find_accounting_partner(self.partner_id).id or False,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
            'payment_id': self.id,
            'journal_id': self.journal_id.id,
        }

    def _get_counterpart_move_line_vals(self, invoice=False):
        if self.is_internal_transfer:
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound':
                    name += _("Customer Payment")
                elif self.payment_type == 'outbound':
                    name += _("Customer Credit Note")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound':
                    name += _("Vendor Credit Note")
                elif self.payment_type == 'outbound':
                    name += _("Vendor Payment")
            # if invoice:
            #     name = self.coll_ids1.name
        return {
            'name': name,
            'branch_name': self.env.user.user_branch_id.branch_name,
            'account_id': self.destination_account_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

    def action_validate_invoice_payment(self):
        """ Posts a payment used to pay an invoice. This function only posts the
        payment by default but can be overridden to apply specific post or pre-processing.
        It is called by the "validate" button of the popup window
        triggered on invoice form by the "Register Payment" button.
        """
        total_amount1 = 0.0

        if any(len(record.invoice_ids) != 1 for record in self):
            pass
            # For multiple invoices, there is account.register.payments wizard
            #             raise UserError(_("This method should only be called to process a single invoice's payment."))
            # for invoices in self.coll_ids1.account_invoice:
            #     # Check all invoices are open
            #     if any(invoice.state != 'open' for invoice in invoices):
            #         raise UserError(_("You can only register payments for open invoices"))
            #     # Check all invoices have the same currency
            #     if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            #         raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))
            #
            #     # Look if we are mixin multiple commercial_partner or customer invoices with vendor bills
            #     multi = any(inv.commercial_partner_id != invoices[0].commercial_partner_id
            #                 or MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[
            #                     invoices[0].type]
            #                 or inv.account_id != invoices[0].account_id
            #                 or inv.partner_bank_id != invoices[0].partner_bank_id
            #                 for inv in invoices)
            #
            #     currency = invoices[0].currency_id
            #
            #     total_amount1 = total_amount1 + self._compute_payment_amount(invoices=invoices, currency=currency)
            #     if (self.name == False):
            #         sequence = self.env['ir.sequence'].next_by_code('account.payment.customer.invoice')
            #         self.update({'name': sequence})
            #     res = self.create({
            #         'amount': abs(total_amount1),
            #         'currency_id': currency.id,
            #         'payment_type': total_amount1 > 0 and 'inbound' or 'outbound',
            #         'partner_id': False if multi else invoices[0].commercial_partner_id.id,
            #         'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            #         'communication': ' '.join([ref for ref in invoices.mapped('reference') if ref]),
            #         'invoice_ids': [(6, 0, invoices.ids)],
            #         'multi': multi,
            #         'payment_method_id': self.payment_method_id.id,
            #         'journal_id': self.journal_id.id,
            #         'collectionre': self.collectionre,
            #         'branch_id': self.branch_id.id,
            #     })
            #     # if self._context.get('active_model') == 'account.collection.vendor':
            #     #     invoices.move_id.update({'collection': self.coll_ids1.name})
            #     #     res.update({'track_coll': True})
            #     res.post()
            # self.coll_ids1.update({'state': 'posted'})
        else:
            # if self._context.get('active_model') == 'account.collection.vendor':
            #     self.coll_ids1.account_invoice.move_id.update({'collection': self.coll_ids1.name})
            self.post()
            # self.coll_ids1.update({'state': 'posted'})
        self.update({'state': 'posted'})
        return

    # @api.model
    # def default_get(self, fields):
    #     rec = super(AccountPayment, self).default_get(fields)
    #     invoice_id = []
    #     for record in self.env.context.get('default_invoice_ids'):
    #         invoice_id.append(record[1])
    #     invoice_defaults = [self.env['account.move'].browse(invoice_id)]
    #     # invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
    #     if invoice_defaults and len(invoice_defaults) == 1:
    #         invoice = invoice_defaults[0]
    #         rec['communication'] = invoice['ref'] or invoice['name'] or invoice['number']
    #         rec['currency_id'] = invoice['currency_id'][0]
    #         rec['payment_type'] = invoice['move_type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
    #         rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['move_type']]
    #         rec['partner_id'] = invoice['partner_id'][0]
    #         rec['amount'] = invoice['amount_residual']
    #     return rec

    # @api.multi
    def _compute_payment_amount(self, invoices=None, currency=None):
        '''Compute the total amount for the payment wizard.

        :param invoices: If not specified, pick all the invoices.
        :param currency: If not specified, search a default currency on wizard/journal.
        :return: The total amount to pay the invoices.
        '''

        # Get the payment invoices
        if not invoices:
            invoice_id = []
            for record in self.env.context.get('default_invoice_ids'):
                invoice_id.append(record[1])
            invoice_defaults = self.env['account.move'].browse(invoice_id)
            invoices = invoice_defaults

        # Get the payment currency
        if not currency:
            currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id or invoices and \
                       invoices[0].currency_id

        # Avoid currency rounding issues by summing the amounts according to the company_currency_id before
        total = 0.0
        groups = groupby(invoices, lambda i: i.currency_id)
        for payment_currency, payment_invoices in groups:
            amount_total = sum(
                [MAP_INVOICE_TYPE_PAYMENT_SIGN[i.move_type] * i.amount_residual_signed for i in payment_invoices])
            if payment_currency == currency:
                total += amount_total
            else:
                total += payment_currency._convert(amount_total, currency, self.env.user.company_id,
                                                   self.date or fields.Date.today())
        return total

    # @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.is_internal_transfer:
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.date).next_by_code(
                    sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

        return True

    # def post_state(self):
    #     # Create the journal entry
    #     amount = self.amount * (self.payment_type in ('outbound') and self.is_internal_transfer and 1 or -1)
    #     move = self._create_payment_entry(amount)
    #
    #     # In case of a transfer, the first journal entry created debited the source liquidity account and credited
    #     # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
    #     if self.is_internal_transfer:
    #         transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == self.company_id.transfer_account_id)
    #         transfer_debit_aml = self._create_transfer_entry(amount)
    #         (transfer_credit_aml + transfer_debit_aml).reconcile()
    #
    #     # self.coll_ids1.update({'state': 'posted'})
    #     self.write({'state': 'posted', 'name': move.name})

    # Migration Note
    # class account_abstract_payment(models.AbstractModel):
    #     _inherit = "account.abstract.payment"
    #
    #     @api.model
    #     def default_get(self, fields):
    #         rec = super(account_abstract_payment, self).default_get(fields)
    #         active_ids = self._context.get('active_ids')
    #         active_model = self._context.get('active_model')
    #         total_amount1 = 0.0
    #         # Check for selected invoices ids
    #         if active_model == 'account.collection.vendor':
    #
    #
    #             collectionss = self.env['account.collection.vendor'].browse(active_ids)
    #             invoices = self.env['account.move'].browse(collectionss.account_invoice.ids)
    #             multi = any(inv.commercial_partner_id != invoices[0].commercial_partner_id
    #             or MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type]
    #             or inv.account_id != invoices[0].account_id
    #             or inv.partner_bank_id != invoices[0].partner_bank_id
    #             for inv in invoices)
    #
    #             currency = invoices[0].currency_id
    #
    #             total_amount = self._compute_payment_amount(invoices=invoices, currency=currency)
    #             if(self._context['active_model'] == 'account.collection.vendor' and (self.id == False)):
    #                 collection = self.env[self._context['active_model']].search([('id','=',self._context['active_id'])]).name
    #                 branch = self.env[self._context['active_model']].search([('id','=',self._context['active_id'])])
    #                 rec.update({
    # #                         'name':self.env['ir.sequence'].next_by_code('account.payment.customer.invoice'),
    #                     'amount': abs(total_amount),
    #                     'currency_id': currency.id,
    #                     'payment_type': total_amount > 0 and 'inbound' or 'outbound',
    #                     'partner_id': False if multi else invoices[0].commercial_partner_id.id,
    #                     'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
    #                     'communication': ' '.join([ref for ref in collectionss.account_invoice.mapped('reference') if ref]),
    #                     'invoice_ids': [(6, 0, collectionss.account_invoice.ids)],
    #                     'multi': multi,
    #                     'collectionre':collection,
    #                     'branch_id':branch.id,
    #
    #                 })
    #             else:
    #                 rec.update({
    #                     'amount': abs(total_amount1),
    #                     'currency_id': currency.id,
    #                     'payment_type': total_amount1 > 0 and 'inbound' or 'outbound',
    #                     'partner_id': False if multi else invoices[0].commercial_partner_id.id,
    #                     'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
    #                     'communication': ' '.join([ref for ref in collectionss.account_invoice.mapped('reference') if ref]),
    #                     'invoice_ids': [(6, 0, collectionss.account_invoice.ids)],
    #                     'multi': multi,
    #
    #                 })
    #         return rec
    # Migration Note
    #             for invoices in collectionss.account_invoice:
    #             # Check all invoices are open
    #                 if any(invoice.state != 'open' for invoice in invoices):
    #                     continue
    #                 # Check all invoices have the same currency
    #                 if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
    #                     raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))
    #
    #                 # Look if we are mixin multiple commercial_partner or customer invoices with vendor bills
    #                 multi = any(inv.commercial_partner_id != invoices[0].commercial_partner_id
    #                     or MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type]
    #                     or inv.account_id != invoices[0].account_id
    #                     or inv.partner_bank_id != invoices[0].partner_bank_id
    #                     for inv in invoices)
    #
    #                 currency = invoices[0].currency_id
    #
    #                 total_amount1 = total_amount1+ self._compute_payment_amount(invoices=invoices, currency=currency)
    #                 if(self._context['active_model'] == 'account.collection.vendor' and (self.id == False)):
    #                     collection = self.env[self._context['active_model']].search([('id','=',self._context['active_id'])]).name
    #                     rec.update({
    # #                         'name':self.env['ir.sequence'].next_by_code('account.payment.customer.invoice'),
    #                         'amount': abs(total_amount1),
    #                         'currency_id': currency.id,
    #                         'payment_type': total_amount1 > 0 and 'inbound' or 'outbound',
    #                         'partner_id': False if multi else invoices[0].commercial_partner_id.id,
    #                         'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
    #                         'communication': ' '.join([ref for ref in collectionss.account_invoice.mapped('reference') if ref]),
    #                         'invoice_ids': [(6, 0, collectionss.account_invoice.ids)],
    #                         'multi': multi,
    #                         'collectionre':collection
    #                     })
    #                 else:
    #                     rec.update({
    #                         'amount': abs(total_amount1),
    #                         'currency_id': currency.id,
    #                         'payment_type': total_amount1 > 0 and 'inbound' or 'outbound',
    #                         'partner_id': False if multi else invoices[0].commercial_partner_id.id,
    #                         'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
    #                         'communication': ' '.join([ref for ref in collectionss.account_invoice.mapped('reference') if ref]),
    #                         'invoice_ids': [(6, 0, collectionss.account_invoice.ids)],
    #                         'multi': multi,
    #
    #                     })
    #         return rec

    @api.onchange('journal_id', 'destination_journal_id')
    def _oncahnge_journal_destination(self):
        electronic_pay = self.env['account.payment.method'].search([('code', '=', 'electronic')])
        if self.journal_id:
            if len(self.journal_id.branches) == 1:
                self.branch_ids = self.journal_id.branches.id

            if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
                return {'domain': {
                    'destination_journal_id': [('id', '!=', self.journal_id.id), ('type', 'in', ['cash', 'bank']),
                                               ('inbound_payment_method_line_ids', 'not in', electronic_pay.ids)]}}
            elif self.env.user.has_group('payments_enhanced.group_create_internal_voucher'):
                return {'domain': {
                    'destination_journal_id': ['|', ('is_internal', '=', True),
                                               ('transfer_branch_ids', 'in', self.env.user.user_branch_id.id),
                                               ('id', '!=', self.journal_id.id),
                                               ('inbound_payment_method_line_ids', 'not in', electronic_pay.ids)]}}
            else:
                if self.env.user.has_group('payments_enhanced.group_create_internal_voucher'):
                    if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
                        return {'domain': {
                            'destination_journal_id': ['|', ('is_internal', '=', True),
                                                       ('id', '!=', self.journal_id.id),
                                                       ('type', 'in', ['cash', 'bank']), (
                                                       'inbound_payment_method_line_ids', 'not in',
                                                       electronic_pay.ids)]}}
                    else:
                        search_ids = self.env['account.journal'].search(
                            [('id', '!=', self.journal_id.id), ('branches', 'in', self.env.user.user_branch_id.id),
                             ('type', 'in', ['cash', 'bank']),
                             ('inbound_payment_method_line_ids', 'not in', electronic_pay.ids)])
                        return {'domain': {
                            'destination_journal_id': ['|', ('is_internal', '=', True), ('id', 'in', search_ids.ids)],
                            'branch_ids': [('id', 'in', self.journal_id.branches.ids)]}}
                else:
                    return {'domain': {
                        'destination_journal_id': [('id', '!=', self.journal_id.id),
                                                   ('branches', 'in', self.env.user.user_branch_id.id),
                                                   ('type', 'in', ['cash', 'bank']),
                                                   ('inbound_payment_method_line_ids', 'not in', electronic_pay.ids)],
                        'branch_ids': [('id', 'in', self.journal_id.branches.ids)]}}
        if self.destination_journal_id:
            if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
                return {'domain': {
                    'journal_id': [('id', '!=', self.destination_journal_id.id), ('type', 'in', ['cash', 'bank'])]}}
            else:
                return {'domain': {
                    'journal_id': [('id', '!=', self.destination_journal_id.id),
                                   ('branches', 'in', self.env.user.user_branch_id.id),
                                   ('type', 'in', ['cash', 'bank'])]}}

    @api.onchange('currency_id')
    def _onchange_currency(self):
        self.amount = abs(self._compute_payment_amount())
        if self.cargo_sale_order_id and not self.is_for_refund:
            if not self.cargo_sale_order_id.is_old_order:
                self.bsg_vehicle_cargo_sale_line_ids.compute_currency_amount()
                self.amount = sum(self.bsg_vehicle_cargo_sale_line_ids.mapped('currency_amount'))

        # Set by default the first liquidity journal having this currency if exists.
        if not self._context.get('active_model') == 'bsg_vehicle_cargo_sale':
            if self.journal_id:
                return
            if self.is_internal_transfer:
                journal = self.env['account.journal'].search(
                    [('type', '=', 'cash'), ('branches', 'in', self.env.user.user_branch_id.id)], limit=1)
            else:
                journal = self.env['account.journal'].search(
                    [('type', 'in', ('bank', 'cash')), ('currency_id', '=', self.currency_id.id)], limit=1)
            if journal:
                return {'value': {'journal_id': journal.id}}

    @api.onchange('amount', 'currency_id')
    def _onchange_amount(self):
        # jrnl_filters = self._compute_journal_domain_and_types()
        # journal_types = jrnl_filters['journal_types']
        # domain_on_types = [('type', 'in', list(journal_types))]
        brnch_list = []
        if self.amount <= 0 and self.show_invoice_amount:
            self.is_more_amount = True
        # if self.amount > self.due_invoice_amount and self.show_invoice_amount:
        #     self.is_more_amount = True
        # if self.is_more_amount:
        #     raise Warning(_("You cannot Pay More than Amount "))
        # return {'type': 'ir.actions.act_window_close'}
        # raise Warning(_("You cannot Pay More than Amount "))
        # for data in self.env['bsg_branches.bsg_branches'].search([('member_ids.user_id','=',self.env.user.id)]):
        #     brnch_list.append(data.id)
        # if self.journal_id.type not in journal_types:
        #     self.journal_id = self.env['account.journal'].search(domain_on_types, limit=1)
        if self.is_more_amount:
            raise Warning(_("You cannot Pay More than Amount "))
        if self.partner_type == 'customer':
            if self._context.get('active_model') == 'transport.management':
                self.journal_id = False
                if self.payment_type == 'inbound':
                    return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id)]}}
                else:
                    return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id)]}}
            else:
                if self._context.get('context_sequnce_cash'):
                    if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
                        if self.payment_type == 'inbound':
                            return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Receipt', 'All'])]}}
                        else:
                            return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Payment', 'All'])]}}
                    else:
                        cargo_search_id = self.env['bsg_vehicle_cargo_sale'].browse(self._context.get('active_id'))
                        if self.payment_type == 'inbound':
                            cargo_sale_journal = self.env['account.journal'].search(
                                [('branches', 'in', cargo_search_id.loc_from.loc_branch_id.id),
                                 ('type', 'in', ['cash']), ('sub_type', 'in', ['Receipt', 'All'])], limit=1)
                            if cargo_sale_journal:
                                self.journal_id = cargo_sale_journal.id
                            else:
                                self.journal_id = False
                            # return {'domain': {'journal_id': ['|',('branches','in',brnch_list),('branches','in',cargo_search_id.loc_from.loc_branch_id.id),('type','in',['cash','bank']),('sub_type','in',['Receipt','All'])]}}
                            return {'domain': {
                                'journal_id': [('branches', 'in', cargo_search_id.loc_from.loc_branch_id.id),
                                               ('type', 'in', ['cash', 'bank']),
                                               ('sub_type', 'in', ['Receipt', 'All'])]}}
                        else:
                            cargo_sale_journal = self.env['account.journal'].search(
                                [('branches', 'in', cargo_search_id.loc_from.loc_branch_id.id),
                                 ('type', 'in', ['cash']), ('sub_type', 'in', ['Payment', 'All'])], limit=1)
                            if cargo_sale_journal:
                                self.journal_id = cargo_sale_journal.id
                            else:
                                self.journal_id = False
                            # return {'domain': {'journal_id': ['|',('branches','in',brnch_list),('branches','in',cargo_search_id.loc_from.loc_branch_id.id),('type','in',['cash','bank']),('sub_type','in',['Receipt','All'])]}}
                            return {'domain': {
                                'journal_id': [('branches', 'in', cargo_search_id.loc_from.loc_branch_id.id),
                                               ('type', 'in', ['cash', 'bank']),
                                               ('sub_type', 'in', ['Payment', 'All'])]}}
                elif self._context.get('default_show_invoice_amount'):
                    if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
                        if self.payment_type == 'inbound':
                            return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Receipt', 'All'])]}}
                        else:
                            return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Payment', 'All'])]}}
                    else:
                        cargo_sale_journal = False
                        cargo_search_id = self.env['bsg_vehicle_cargo_sale'].browse(self._context.get('active_id'))
                        user_id = self.env['res.users'].search([('id', '=', self._context.get('uid'))])
                        if self.payment_type == 'inbound':
                            if user_id.user_branch_id.id == cargo_search_id.loc_from.loc_branch_id.id or user_id.user_branch_id.id == cargo_search_id.loc_to.loc_branch_id.id:
                                # cargo_sale_journal = self.env['account.journal'].search(['|',('branches','in',cargo_search_id.loc_from.loc_branch_id.id),('branches','in',cargo_search_id.loc_to.loc_branch_id.id),('type','in',['cash']),('sub_type','in',['Receipt'])],limit=1)
                                cargo_sale_journal = self.env['account.journal'].search(
                                    [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash']),
                                     ('sub_type', 'in', ['Receipt'])], limit=1)
                            if cargo_sale_journal:
                                self.journal_id = cargo_sale_journal.id
                            else:
                                self.journal_id = False
                            # return {'domain': {'journal_id': ['|','|',('branches','in',cargo_search_id.loc_from.loc_branch_id.id),('branches','in',cargo_search_id.loc_to.loc_branch_id.id),('branches','in',brnch_list),('type','in',['cash','bank']),('sub_type','in',['Receipt','All'])]}}

                            return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id),
                                                              ('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Receipt', 'All'])]}}
                        else:
                            if user_id.user_branch_id.id == cargo_search_id.loc_from.loc_branch_id.id or user_id.user_branch_id.id == cargo_search_id.loc_to.loc_branch_id.id:
                                # cargo_sale_journal = self.env['account.journal'].search(['|',('branches','in',cargo_search_id.loc_from.loc_branch_id.id),('branches','in',cargo_search_id.loc_to.loc_branch_id.id),('type','in',['cash']),('sub_type','in',['Receipt'])],limit=1)
                                cargo_sale_journal = self.env['account.journal'].search(
                                    [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash']),
                                     ('sub_type', 'in', ['Payment'])], limit=1)
                            if cargo_sale_journal:
                                self.journal_id = cargo_sale_journal.id
                            else:
                                self.journal_id = False
                            # return {'domain': {'journal_id': ['|','|',('branches','in',cargo_search_id.loc_from.loc_branch_id.id),('branches','in',cargo_search_id.loc_to.loc_branch_id.id),('branches','in',brnch_list),('type','in',['cash','bank']),('sub_type','in',['Receipt','All'])]}}

                            return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id),
                                                              ('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Payment', 'All'])]}}
                else:
                    if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
                        if self.payment_type == 'inbound':
                            return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Receipt', 'All'])]}}
                        else:
                            return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Payment', 'All'])]}}
                    else:
                        if self.payment_type == 'inbound':
                            jounal_id = self.env['account.journal'].search(
                                [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash', 'bank']),
                                 ('sub_type', 'in', ['Receipt', 'All'])], limit=1)
                            if jounal_id:
                                self.journal_id = jounal_id.id
                            else:
                                self.journal_id = False
                            return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id),
                                                              ('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Receipt', 'All'])]}}
                        else:
                            jounal_id = self.env['account.journal'].search(
                                [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash', 'bank']),
                                 ('sub_type', 'in', ['Payment', 'All'])], limit=1)
                            if jounal_id:
                                self.journal_id = jounal_id.id
                            else:
                                self.journal_id = False
                            return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id),
                                                              ('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Payment', 'All'])]}}

        elif self.partner_type == 'supplier':
            if self._context.get('active_model') == 'transport.management':
                self.journal_id = False
                if self.payment_type == 'inbound':
                    return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id)]}}
                else:
                    return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id)]}}
            else:
                if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
                    if self.payment_type == 'inbound':
                        return {'domain': {'journal_id': [('sub_type', 'in', ['Receipt', 'All'])]}}
                    else:
                        return {'domain': {'journal_id': [('sub_type', 'in', ['Payment', 'All'])]}}
                else:
                    if self.payment_type == 'inbound':
                        jounal_id = self.env['account.journal'].search(
                            [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash', 'bank']),
                             ('sub_type', 'in', ['Receipt', 'All'])], limit=1)
                        if jounal_id:
                            self.journal_id = jounal_id.id
                        else:
                            self.journal_id = False
                        return {'domain': {'journal_id': [('sub_type', 'in', ['Receipt', 'All']),
                                                          ('branches', 'in', self.env.user.user_branch_id.id)]}}
                    else:
                        jounal_id = self.env['account.journal'].search(
                            [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash', 'bank']),
                             ('sub_type', 'in', ['Payment', 'All'])], limit=1)
                        if jounal_id:
                            self.journal_id = jounal_id.id
                        else:
                            self.journal_id = False
                        return {'domain': {'journal_id': [('sub_type', 'in', ['Payment', 'All']),
                                                          ('branches', 'in', self.env.user.user_branch_id.id)]}}
        else:
            if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
                if self.payment_type == 'inbound':
                    return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank'])]}}
                if self.payment_type == 'outbound':
                    return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank'])]}}
                if self.is_internal_transfer:
                    return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank'])]}}
            else:
                if self.payment_type == 'inbound':
                    return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank']),
                                                      ('branches', 'in', self.env.user.user_branch_id.id)]}}
                if self.payment_type == 'outbound':
                    return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank']),
                                                      ('branches', 'in', self.env.user.user_branch_id.id)]}}
                if self.is_internal_transfer:
                    return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank']),
                                                      ('branches', 'in', self.env.user.user_branch_id.id)]}}

    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        return {
            'date': self.date,
            'ref': self.communication or '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
            'collection': self.collectionre,
        }

    def _get_liquidity_move_line_vals(self, amount):
        name = self.collectionre or self.name
        # vals = {'currency_id':self.currency_id.id}
        if self.is_internal_transfer:
            name = _('Transfer to %s') % self.destination_journal_id.name
        vals = {
            'name': name,
            'account_id': self.payment_type in ('outbound') and self.is_internal_transfer and self.journal_id.default_account_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'branch_id': self.env.user.user_branch_id.id,
            'branch_name': self.env.user.user_branch_id.branch_name,
        }

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id._convert(amount, self.journal_id.currency_id, self.company_id,
                                               self.date or fields.Date.today())
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(
                date=self.date)._compute_amount_fields(amount, self.journal_id.currency_id,
                                                               self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })
        if not vals.get('currency_id'):
            vals.update({'currency_id':self.currency_id.id})
        if not vals.get('account_id'):
            vals.update({'account_id':self.journal_id.default_account_id.id})
        return vals

    def _get_counterpart_move_line_vals(self, invoice=False):
        if self.is_internal_transfer:
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound':
                    name += _("Customer Payment")
                elif self.payment_type == 'outbound':
                    name += _("Customer Credit Note")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound':
                    name += _("Vendor Credit Note")
                elif self.payment_type == 'outbound':
                    name += _("Vendor Payment")
            # if invoice:
            #     name = self.coll_ids.name
        return {
            'name': name,
            'branch_name': self.env.user.user_branch_id.branch_name,
            'account_id': self.destination_account_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

    # for internal transfer post payment
    def post_internal_transfer(self):
        for data in self:
            if data.is_internal_transfer:
                if self.env.user.has_group('payments_enhanced.group_posted_internal_transfer'):
                    data.post_state()
                    data.post_payment()
                else:
                    raise UserError(_("You Have no Right's to post payment please contact to Administrator"))
            else:
                raise UserError(_("You can do only for internal Transfer"))

    # for internal transfer post payment
    def post_internal_transfer(self):
        for data in self:
            if data.is_internal_transfer:
                if self.env.user.has_group('payments_enhanced.group_posted_internal_transfer'):
                    data.post_state()
                    data.post_payment()
                else:
                    raise UserError(_("You Have no Right's to post payment please contact to Administrator"))
            else:
                raise UserError(_("You can do only for internal Transfer"))

    def action_validate_invoice_payment(self):
        """ Posts a payment used to pay an invoice. This function only posts the
        payment by default but can be overridden to apply specific post or pre-processing.
        It is called by the "validate" button of the popup window
        triggered on invoice form by the "Register Payment" button.
        """
        if self._context.get('pass_sale_order_id'):
            cargo_id = self.env['bsg_vehicle_cargo_sale'].search([('id', '=', self._context.get('pass_sale_order_id'))])
            if cargo_id:
                if self.amount >= sum(self.invoice_ids.mapped('residual')):
                    cargo_id.write({'state': 'done'})

        '''if self.amount == self.due_invoice_amount :
            cargo_id = self.env['bsg_vehicle_cargo_sale'].search([('id','=',self._context.get('pass_sale_order_id'))])
            cargo_id.write({'state' : 'done'})

        cargo_id = self.env['bsg_vehicle_cargo_sale'].search([('id','=',self._context.get('active_id'))])        
        if not cargo_id:
            if self.cargo_sale_order_id.payment_method.payment_type != 'pod':
                self.cargo_sale_order_id.write({'state' : 'done'})
        if cargo_id.payment_method.payment_type != 'pod': 
            if not self.is_patrtially_payment:
                cargo_id.write({'state' : 'done'})
            if self.is_patrtially_payment:
                if self.amount == self.cargo_sale_order_id.invoice_ids.residual:
                    cargo_id.write({'state' : 'done'})'''
        # if self.amount > self.due_invoice_amount and self.show_invoice_amount: 
        #     raise Warning(_("You cannot Pay More than Amount "))

        total_amount1 = 0.0

        if any(len(record.invoice_ids) != 1 for record in self):
            pass
            # For multiple invoices, there is account.register.payments wizard
            #             raise UserError(_("This method should only be called to process a single invoice's payment."))
            # for invoices in self.coll_ids.account_invoice:
            #     # Check all invoices are open
            #     if any(invoice.state != 'open' for invoice in invoices):
            #         raise UserError(_("You can only register payments for open invoices"))
            #     # Check all invoices have the same currency
            #     if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            #         raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))
            #
            #     # Look if we are mixin multiple commercial_partner or customer invoices with vendor bills
            #     multi = any(inv.commercial_partner_id != invoices[0].commercial_partner_id
            #                 or MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[
            #                     invoices[0].type]
            #                 or inv.account_id != invoices[0].account_id
            #                 or inv.partner_bank_id != invoices[0].partner_bank_id
            #                 for inv in invoices)
            #
            #     currency = invoices[0].currency_id
            #
            #     total_amount1 = total_amount1 + self._compute_payment_amount(invoices=invoices, currency=currency)
            #     if (self.name == False):
            #         sequence = self.env['ir.sequence'].next_by_code('account.payment.customer.invoice')
            #         self.update({'name': sequence})
            #     res = self.create({
            #         'amount': abs(total_amount1),
            #         'currency_id': currency.id,
            #         'payment_type': total_amount1 > 0 and 'inbound' or 'outbound',
            #         'partner_id': False if multi else invoices[0].commercial_partner_id.id,
            #         'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            #         'communication': ' '.join([ref for ref in invoices.mapped('reference') if ref]),
            #         'invoice_ids': [(6, 0, invoices.ids)],
            #         'multi': multi,
            #         'payment_method_id': self.payment_method_id.id,
            #         'journal_id': self.journal_id.id,
            #         'collectionre': self.collectionre,
            #         'branch_id': self.branch_id.id,
            #     })
            #     # if self._context.get('active_model') == 'account.collection':
            #     #     invoices.move_id.update({'collection': self.coll_ids.name})
            #     #     res.update({'track_coll': True})
            #     res.post()
            # self.coll_ids.update({'state': 'posted'})

            # if self._context.get('active_model') == 'bsg_vehicle_cargo_sale':
            #     if self._context.get('default_amount_return_cargo_invoice'):
            #         cargo_id.cancel_so_agreement()
        else:
            # if self._context.get('active_model') == 'account.collection':
            #     self.coll_ids.account_invoice.move_id.update({'collection': self.coll_ids.name})
            # self.post_state()
            self.post()
            # if self._context.get('active_model') == 'bsg_vehicle_cargo_sale':
            #     if self._context.get('default_amount_return_cargo_invoice'):
            #         cargo_id.cancel_so_agreement()
            # self.coll_ids.update({'state': 'posted'})
        #         self.update({'state':'posted'})
        if self.bsg_vehicle_cargo_sale_line_ids:
            for so_line in self.bsg_vehicle_cargo_sale_line_ids.mapped('cargo_sale_line_id').filtered(
                    lambda x: x.is_paid and x.state == 'draft'):
                so_line.write({'state': 'confirm'})
        return

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        brnch_list = []
        jounal_id = False
        invoice_id = []
        if self.env.context.get('default_invoice_ids'):
            for record in self.env.context.get('default_invoice_ids'):
                invoice_id.append(record[1])

        invoice_defaults = [self.env['account.move'].browse(invoice_id)]
        if len(invoice_id) == 0:
            inv_list = self.env['account.move'].browse(self._context.get('active_ids'))
            invoice_defaults = [inv_list]
            rec['invoice_ids'] = inv_list
        # invoice_defaults = self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        cargo_search_id = False
        cargo_sale_journal = False
        if invoice_defaults:
            if self._context.get('active_model') == 'bsg_vehicle_cargo_sale' and self._context.get(
                    'context_sequnce_cash'):
                cargo_search_id = self.env['bsg_vehicle_cargo_sale'].browse(self._context.get('active_id'))
                cargo_sale_journal = self.env['account.journal'].search(
                    [('branches', 'in', cargo_search_id.loc_from.loc_branch_id.id), ('type', 'in', ['cash']),
                     ('sub_type', 'in', ['Receipt', 'All'])], limit=1)
            elif self._context.get('active_model') == 'bsg_vehicle_cargo_sale' and self._context.get(
                    'default_show_invoice_amount'):
                cargo_search_id = self.env['bsg_vehicle_cargo_sale'].browse(self._context.get('active_id'))
                user_id = self.env['res.users'].search([('id', '=', self._context.get('uid'))])
                if user_id.user_branch_id.id == cargo_search_id.loc_from.loc_branch_id.id or user_id.user_branch_id.id == cargo_search_id.loc_to.loc_branch_id.id:
                    # cargo_sale_journal = self.env['account.journal'].search(['|',('branches','in',cargo_search_id.loc_from.loc_branch_id.id),('branches','in',cargo_search_id.loc_to.loc_branch_id.id),('type','in',['cash']),('sub_type','in',['Receipt'])],limit=1)
                    cargo_sale_journal = self.env['account.journal'].search(
                        [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash']),
                         ('sub_type', 'in', ['Receipt', 'All'])], limit=1)
            communication_name = False
            if rec.get('partner_type') == 'customer':
                if self._context.get('default_invoice_ids'):
                    for data in self.env['account.move'].search(
                            [('id', '=', self._context.get('default_invoice_ids')[0][1])]):
                        communication_name = " , ".join((data.name for data in (data.invoice_line_ids)))
            if invoice_defaults and len(invoice_defaults) == 1 and cargo_sale_journal:
                invoice = invoice_defaults[0]
                rec[
                    'communication'] = communication_name if communication_name else cargo_search_id.name  # invoice['reference'] or invoice['name'] or invoice['number']
                rec['currency_id'] = invoice['currency_id'][0]
                rec['payment_type'] = invoice['move_type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
                rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['move_type']]
                rec['partner_id'] = invoice['partner_id'][0]
                rec['amount'] = invoice['amount_residual']
                rec['journal_id'] = cargo_sale_journal.id if cargo_sale_journal else False
            elif cargo_search_id:
                invoice = invoice_defaults[0]
                rec[
                    'communication'] = communication_name if communication_name else cargo_search_id.name  # invoice['reference'] or invoice['name'] or invoice['number']
                rec['currency_id'] = invoice['currency_id'][0]
                rec['payment_type'] = invoice['move_type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
                rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['move_type']]
                rec['partner_id'] = invoice['partner_id'][0]
                rec['amount'] = invoice['amount_residual']
                rec['journal_id'] = cargo_sale_journal.id if cargo_sale_journal else False
            elif invoice_defaults and len(invoice_defaults) == 1:
                invoice = invoice_defaults[0]
                if invoice.exists():
                    # rec['ref'] = communication_name if communication_name else invoice['ref'] or invoice['name']
                    rec['currency_id'] = invoice['currency_id'][0]
                    rec['payment_type'] = invoice['move_type'] in (
                    'out_invoice', 'in_refund') and 'inbound' or 'outbound'
                    rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['move_type']]
                    rec['partner_id'] = invoice['partner_id'][0]
                    rec['amount'] = invoice['amount_residual']
                    rec['journal_id'] = jounal_id.id if jounal_id else False

            if self._context.get('active_model') == 'transport.management':
                transport_id = self.env['transport.management'].browse(self._context.get('active_id'))
                rec.update({'communication': transport_id.transportation_no})
            if self._context.get('active_model') == 'bsg_vehicle_cargo_sale':
                cargo_search_id = self.env['bsg_vehicle_cargo_sale'].browse(self._context.get('active_id'))
                if cargo_search_id.cargo_sale_type == 'international':
                    if self.env.user.has_group('payments_enhanced.group_allowed_pay_with_fc'):
                        rec['is_allow_pay_with_fc'] = True
                    else:
                        rec['currency_id'] = self.env.user.company_id.currency_id.id
            if self._context.get('active_model') == 'account.move':
                account_search_id = self.env['account.move'].browse(self._context.get('active_ids'))
                if account_search_id.cargo_sale_id.cargo_sale_type == 'international':
                    if self.env.user.has_group('payments_enhanced.group_allowed_pay_with_fc'):
                        rec['is_allow_pay_with_fc'] = True
                    else:
                        rec['currency_id'] = self.env.user.company_id.currency_id.id
        return rec

    @api.depends('partner_id', 'journal_id', 'destination_journal_id')
    def _compute_is_internal_transfer(self):
        for payment in self:
            if self.env.context.get('default_is_internal_transfer'):
                payment.is_internal_transfer = True
            else:
                payment.is_internal_transfer = payment.partner_id \
                                               and payment.partner_id == payment.journal_id.company_id.partner_id \
                                               and payment.destination_journal_id
    # @api.multi
    def _compute_payment_amount(self, invoices=None, currency=None):
        '''Compute the total amount for the payment wizard.

        :param invoices: If not specified, pick all the invoices.
        :param currency: If not specified, search a default currency on wizard/journal.
        :return: The total amount to pay the invoices.
        '''

        # Get the payment invoices
        if not invoices:
            invoices = self.invoice_ids

        # Get the payment currency
        if not currency:
            currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id or invoices and \
                       invoices[0].currency_id

        # Avoid currency rounding issues by summing the amounts according to the company_currency_id before
        total = 0.0
        groups = groupby(invoices, lambda i: i.currency_id)
        for payment_currency, payment_invoices in groups:
            amount_total = sum([MAP_INVOICE_TYPE_PAYMENT_SIGN[i.type] * i.residual_signed for i in payment_invoices])
            if payment_currency == currency:
                total += amount_total
            else:
                total += payment_currency._convert(amount_total, currency, self.env.user.company_id,
                                                   self.date or fields.Date.today())
        return total

    # @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.is_internal_transfer:
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.date).next_by_code(
                    sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
        # if not self.move_line_ids:
        self.post_state()
        self.post_payment()
        return True

        # def action_post(self):
        #     counterpart_aml = False
        #     if self.payment_type == 'inbound':
        #         for data in self.invoice_line_ids:
        #             if data.credit != 0:
        #                 counterpart_aml = data
        #     elif self.payment_type == 'outbound':
        #         for data in self.invoice_line_ids:
        #             if data.debit != 0:
        #                 counterpart_aml = data
        #     # if self.invoice_ids:
        #     #     self.invoice_ids.register_payment(counterpart_aml)
        #     # for data in self.invoice_line_ids:
        #     #     data.move_id.action_post()

        # self.state = 'posted'

    def post_payment(self):
        for data in self:
            if data.state not in ['draft', 'posted']:
                raise UserError(_("Only a voucher payment can be Posted."))
            # if not self.env.user.has_group('bsg_cargo_sale.group_register_payment_on_agreement') or not self.env.user.has_group('payments_enhanced.group_confirming_voucher') or not self.env.user.has_group('payments_enhanced.group_posting_voucher') or not self.env.user.has_group('base.group_erp_manager'):
            #     raise UserError(_("You have not Access to Post the Payment"))            
            if self.env.user.has_group('bsg_cargo_sale.group_register_payment_on_agreement') or self.env.user.has_group(
                    'payments_enhanced.group_confirming_voucher') or self.env.user.has_group(
                    'payments_enhanced.group_posting_voucher') or self.env.user.has_group('base.group_erp_manager'):
                data.sudo().with_context(force_company=self.env.user.company_id.id,
                                         company_id=self.env.user.company_id.id).action_post()
            else:
                raise UserError(_("You have not Access to Post the Payment"))

    def confirm_post(self):
        for data in self:
            if data.state not in ['draft']:
                raise UserError(_("Only a draft payment can be Confirmed."))
            # if not self.env.user.has_group('bsg_cargo_sale.group_register_payment_on_agreement') or not self.env.user.has_group('payments_enhanced.group_confirming_voucher') or not self.env.user.has_group('payments_enhanced.group_confirming_voucher') or not self.env.user.has_group('payments_enhanced.group_posting_voucher') or not self.env.user.has_group('base.group_erp_manager'):
            #     raise UserError(_("You have not Access to confirm the Payment"))
            if self.env.user.has_group('bsg_cargo_sale.group_register_payment_on_agreement') or self.env.user.has_group(
                    'payments_enhanced.group_confirming_voucher') or self.env.user.has_group(
                    'payments_enhanced.group_confirming_voucher') or self.env.user.has_group(
                    'payments_enhanced.group_posting_voucher') or self.env.user.has_group('base.group_erp_manager'):
                data.sudo().with_context(force_company=self.env.user.company_id.id,
                                         company_id=self.env.user.company_id.id).post_state()
            else:
                raise UserError(_("You have not Access to confirm the Payment"))
            # data.action_post()

    def post_state(self):

        # for Disallow user to Post A Negative Entry ...!
        for rec in self:
            if rec.payment_type == 'outbound' and rec.journal_id and not rec.journal_id.is_allow_negative_transaction:
                if rec.journal_id.default_account_id.balance <= rec.amount:
                    raise UserError(_("You Are not Allowed to Post Negative Transaction...!!!!"))

        # Create the journal entry
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be Confirmed."))
        self.action_post()
        # for data in self:
        #     amount = data.amount * (data.payment_type in ('outbound', 'transfer') and 1 or -1)
        #     move = data.move_id
        #
        #     # In case of a transfer, the first journal entry created debited the source liquidity account and credited
        #     # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
        #     if data.is_internal_transfer:
        #         transfer_credit_aml = move.line_ids.filtered(
        #             lambda r: r.account_id == data.company_id.transfer_account_id)
        #         move.action_post()
        #         transfer_debit_aml = data._create_paired_internal_transfer_payment()
        #         (transfer_credit_aml + transfer_debit_aml).reconcile()
        #
        #     if not data.is_internal_transfer:
        #         jounral_search_id = data.journal_id
        #         if jounral_search_id.sub_type == 'Receipt' or jounral_search_id.sub_type == 'All' and data.partner_type == 'customer':
        #             if data.payment_type == 'inbound':
        #                 if jounral_search_id.receipt_sequnce_id:
        #                     if data.journal_id.id != data.cancel_jounral_id.id:
        #                         data.name = jounral_search_id.receipt_sequnce_id.next_by_id()
        #                         data.is_sequnce = True
        #             elif data.payment_type == 'outbound':
        #                 if jounral_search_id.payment_sequnce_id:
        #                     if data.journal_id.id != data.cancel_jounral_id.id:
        #                         data.name = jounral_search_id.payment_sequnce_id.next_by_id()
        #                         data.is_sequnce = True
        #         if jounral_search_id.sub_type == 'Payment' or jounral_search_id.sub_type == 'All' and data.partner_type == 'supplier':
        #             # if jounral_search_id.payment_sequnce_id:
        #             #    if self.journal_id.id != self.cancel_jounral_id.id:
        #             #        data.name = jounral_search_id.payment_sequnce_id.next_by_id()
        #             #        data.is_sequnce = True
        #             if data.payment_type == 'inbound':
        #                 if jounral_search_id.receipt_sequnce_id:
        #                     if data.journal_id.id != data.cancel_jounral_id.id:
        #                         data.name = jounral_search_id.receipt_sequnce_id.next_by_id()
        #                         data.is_sequnce = True
        #             elif data.payment_type == 'outbound':
        #                 if jounral_search_id.payment_sequnce_id:
        #                     if data.journal_id.id != data.cancel_jounral_id.id:
        #                         data.name = jounral_search_id.payment_sequnce_id.next_by_id()
        #                         data.is_sequnce = True
        #     elif data.is_internal_transfer:
        #         config = self.env.user.company_id
        #         if config.sequnce_id:
        #             if not data.is_sequnce and data.journal_id.id != data.cancel_jounral_id.id:
        #                 if data.branch_ids and data.branch_ids.branch_no:
        #                     data.name = str(data.branch_ids.branch_no) + config.sequnce_id.next_by_id()
        #                     data.is_sequnce = True
        #                 else:
        #                     data.name = config.sequnce_id.next_by_id()
        #                     data.is_sequnce = True
        #     # data.coll_ids.update({'state': 'posted'})
        #     # data.write({'name': move.name})
        #     for data_line in data.invoice_line_ids:
        #         if data.communication:
        #             data_line.write({'name': str(data.name) + "-" + str(data.communication)})
        #         else:
        #             data_line.write({'name': data.name})
        self.write({'state': 'posted'})

    # override method to unpost entrt instead of post enter and make entry creable when create account.payment
    # data.coll_ids.update({'state':'posted'})
    # data.write({'state': 'posted', 'move_name': move.name})
    # if not self.journal_id.post_at_bank_rec:
    # move.post()
    # def _create_payment_entry(self, amount):
    #     """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
    #         Return the journal entry.
    #     """
    #     self.move_id.action_post()
    #     # Migration Note
    #     # aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
    #     # amount_currency = False
    #     # currency_id = False
    #     # date = self.env.context.get('date') or fields.Date.today()
    #     # company = self.env.context.get('company_id')
    #     # if self.currency_id and self.currency_id != self.company_id.currency_id:
    #     #     amount_currency = amount
    #     #     amount = self.currency_id._convert(amount, self.currency_id, self.company_id.currency_id, date)
    #     #     currency_id = self.currency_id.id
    #     # debit = amount > 0 and amount or 0.0
    #     # credit = amount < 0 and -amount or 0.0
    #     # debit, credit, amount_currency, currency_id = debit, credit, amount_currency, currency_id
    #     # move = self.env['account.move'].create(self._get_move_vals())
    #     #
    #     # # Write line corresponding to invoice payment
    #     # counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
    #     # counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
    #     # counterpart_aml_dict.update({'currency_id': self.currency_id.id})
    #     # counterpart_aml = aml_obj.create(counterpart_aml_dict)
    #     # Reconcile with the invoices
    #     # if self.payment_difference_handling == 'reconcile' and self.payment_difference:
    #     #     writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
    #     #     debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(
    #     #         date=self.date)._compute_amount_fields(self.payment_difference, self.currency_id,
    #     #                                                        self.company_id.currency_id)
    #     #     writeoff_line['name'] = self.writeoff_label
    #     #     writeoff_line['account_id'] = self.writeoff_account_id.id
    #     #     writeoff_line['debit'] = debit_wo
    #     #     writeoff_line['credit'] = credit_wo
    #     #     writeoff_line['amount_currency'] = amount_currency_wo
    #     #     writeoff_line['currency_id'] = currency_id
    #     #     writeoff_line = aml_obj.create(writeoff_line)
    #     #     if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
    #     #         counterpart_aml['debit'] += credit_wo - debit_wo
    #     #     if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
    #     #         counterpart_aml['credit'] += debit_wo - credit_wo
    #     #     counterpart_aml['amount_currency'] -= amount_currency_wo
    #
    #     # Write counterpart lines
    #     # if not self.currency_id.is_zero(self.amount):
    #     #     if not self.currency_id != self.company_id.currency_id:
    #     #         amount_currency = 0
    #     #     liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
    #     #     liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
    #     #     aml_obj.create(liquidity_aml_dict)
    #
    #     # # validate the payment
    #     # if not self.journal_id.post_at_bank_rec:
    #     #     move.post()
    #     # move.action_post()
    #
    #     # reconcile the invoice receivable/payable line(s) with the payment
    #     # if self.invoice_ids:
    #     #     self.invoice_ids.register_payment(counterpart_aml)
    #     return True

    # override to remove post automatically user will do post manually
    def _create_paired_internal_transfer_payment(self):
        """ Create the journal entry corresponding to the 'incoming money' part of an internal transfer, return the reconcilable move line
        """
        super(AccountPayment, self)._create_paired_internal_transfer_payment()

        # aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        # custom_vals = self._get_move_vals(self.destination_journal_id)
        #
        # dst_move = self.env['account.move'].create(custom_vals)
        #
        # dst_liquidity_aml_dict = self._get_shared_move_line_vals(22, 0, 148, dst_move.id)
        # dst_liquidity_aml_dict.update({
        #     'name': _('Transfer from %s') % self.journal_id.name,
        #     'account_id': self.destination_journal_id.default_account_id.id,
        #     'currency_id': self.destination_journal_id.currency_id.id,
        #     'journal_id': self.destination_journal_id.id})
        # aml_obj.create(dst_liquidity_aml_dict)
        #
        # transfer_debit_aml_dict = self._get_shared_move_line_vals(0, -22, 148, dst_move.id)
        # transfer_debit_aml_dict.update({
        #     'name': self.name,
        #     'account_id': self.company_id.transfer_account_id.id,
        #     'journal_id': self.destination_journal_id.id})
        # if self.currency_id != self.company_id.currency_id:
        #     transfer_debit_aml_dict.update({
        #         'currency_id': self.currency_id.id,
        #         'amount_currency': -self.amount,
        #     })
        # transfer_debit_aml = aml_obj.create(transfer_debit_aml_dict)
        # if not self.destination_journal_id.post_at_bank_rec:
        #     dst_move.post()
        # return transfer_debit_aml

    @api.constrains('date', 'journal_id')
    def _constrains_date_journal_id(self):
        for rec in self:
            if rec.journal_id and rec.journal_id.is_not_allowed_past_payment:
                if fields.Date.today() > rec.date:
                    raise ValidationError(_('You cannot create transaction in past date for selected journal!'))


class AccountVoucherLine(models.Model):
    _name = 'account.voucher.line.custom'
    _description = "Account Voucher Line"

    payment_id = fields.Many2one('account.payment', string="Payment",required=True)
    account_id = fields.Many2one('account.account', string="Account")
    analytic_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    collectionre = fields.Char("Collection Voucher ref")
    track_coll = fields.Boolean("Track_coll", default=False)
    payment_type = fields.Selection([
        ('all', 'All'),
        ('inbound', 'Receipt Vouchers'),
        ('outnbound', 'Payment Vouchers'),
    ], string='Payment Type')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('posted', 'Posted'),
                              ('cancelled', 'Cancelled')], default='draft', string="Status")
    cargo_sale_order_id = fields.Many2one(string="Cargo Sale ID", comodel_name="bsg_vehicle_cargo_sale", copy=False)

    def write(self, vals):
        print("asdsadfsadasdasdasd")
        payment = self.payment_id
        if payment.payment_type == 'inbound' and self.payment_id.move_id.state == 'draft' and vals.get('account_id') and not vals.get('invoice_id'):
            self.payment_id.move_id.line_ids.filtered(lambda s: s.credit > 0).write({'account_id':vals.get('account_id')})
        elif payment.payment_type == 'outbound' and self.payment_id.move_id.state == 'draft' and vals.get('account_id') and not vals.get('invoice_id'):
            self.payment_id.move_id.line_ids.filtered(lambda s: s.debit > 0).write({'account_id':vals.get('account_id')})
        #
        # if payment.payment_type == 'inbound':
        #     if vals.get('credit') != 0.0 and not vals.get('invoice_id'):
        #         if len(payment.voucher_line_ids) != 0:
        #             vals['account_id'] = payment.voucher_line_ids[0].account_id.id
        #             vals['analytic_distribution'] = {payment.voucher_line_ids[0].analytic_id.id: 100}
        #     if vals.get('debit') != 0.0 and not vals.get('invoice_id'):
        #         if len(payment.voucher_line_ids) != 0:
        #             vals['account_id'] = payment.journal_id.default_debit_account_id.id
        # if vals.get('payment_id'):
        #     payment = self.env['account.payment'].search([('id','=',vals.get('payment_id'))])
        #     if payment.payment_type == 'outbound':
        #         if vals.get('credit') != 0.0 and not vals.get('invoice_id'):
        #             if len(payment.voucher_line_ids) != 0:
        #                 vals['account_id'] = payment.journal_id.default_credit_account_id.id
        #         if vals.get('debit') != 0.0 and not vals.get('invoice_id'):
        #             if len(payment.voucher_line_ids) != 0:
        #                 vals['account_id'] = payment.voucher_line_ids[0].account_id.id
        #                 vals['analytic_distribution'] = {payment.voucher_line_ids[0].analytic_id.id: 100}
        res = super(AccountVoucherLine, self).write(vals)
        return res

class account_cargo_line_payment(models.Model):
    _inherit = "account.cargo.line.payment"

    is_patrtially_payment = fields.Boolean(related='account_payment_id.is_patrtially_payment', store=True)
