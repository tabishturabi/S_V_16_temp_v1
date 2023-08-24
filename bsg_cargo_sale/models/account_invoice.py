# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command
from collections import defaultdict

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}

TYPE_REVERSE_MAP = {
    'entry': 'entry',
    'out_invoice': 'out_refund',
    'out_refund': 'entry',
    'in_invoice': 'in_refund',
    'in_refund': 'entry',
    'out_receipt': 'out_refund',
    'in_receipt': 'in_refund',
}


# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',  # Customer Invoice
    'in_invoice': 'in_refund',  # Vendor Bill
    'out_refund': 'out_invoice',  # Customer Credit Note
    'in_refund': 'in_invoice',  # Vendor Credit Note
}

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    cargo_sale_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line', string="Cargo Sale Line")
    is_other_service_line = fields.Boolean(string='Is Other Service')
    is_demurrage_line = fields.Boolean(string='Is Demurrage')
    payment_ids = fields.One2many('account.cargo.line.payment', 'account_invoice_line_id', string='Payments')
    paid_amount = fields.Float(compute="_compute_paid_data", store=True)
    is_paid = fields.Boolean(compute="_compute_paid_data", store=True)
    is_refund = fields.Boolean('Is Refund', compute="_compute_is_refund")
    is_deduct = fields.Boolean()

    @api.depends('move_id.type_name')
    def _compute_is_refund(self):
        for rec in self:
            rec.is_refund = False
            if rec.cargo_sale_line_id:
                if rec.move_id.move_type in ('out_refund', 'in_refund'):
                    rec.is_refund = True

    @api.depends('payment_ids', 'payment_ids.state', 'move_id.state', 'move_id.reversal_move_id',
                 'move_id.reversal_move_id.state')
    def _compute_paid_data(self):
        for rec in self:
            rec.paid_amount = 0
            rec.is_paid = False
            if rec.move_id.state == 'paid':
                rec.is_paid = True
                rec.paid_amount = rec.price_total
            elif rec.payment_ids.filtered(lambda s: s.state == 'posted') or rec.move_id.reversal_move_id.filtered(
                    lambda s: s.state == 'paid' and not s.payment_ids):
                payment_amount = sum(rec.payment_ids.filtered(lambda s: s.state == 'posted').mapped(
                    'amount')) >= rec.price_total and rec.price_total or sum(
                    rec.payment_ids.filtered(lambda s: s.state == 'posted').mapped('amount'))
                refund_invoice_amount = sum(
                    rec.move_id.reversal_move_id.filtered(lambda s: s.state == 'paid' and not s.payment_ids).mapped(
                        'invoice_line_ids').filtered(
                        lambda s: s.cargo_sale_line_id.id == rec.cargo_sale_line_id.id).mapped(
                        'paid_amount')) >= rec.price_total and \
                                        rec.price_total or sum(
                    rec.move_id.reversal_move_id.filtered(lambda s: s.state == 'paid' and not s.payment_ids).mapped(
                        'invoice_line_ids').filtered(
                        lambda s: s.cargo_sale_line_id.id == rec.cargo_sale_line_id.id).mapped('paid_amount'))
                rec.paid_amount = payment_amount + refund_invoice_amount
                rec.is_paid = True and rec.paid_amount >= rec.price_total or False
            else:
                rec.is_paid = False
                rec.paid_amount = 0


class bsg_inherit_account_invoice(models.Model):
    _inherit = 'account.move'

    invoice_date = fields.Date('Date', default=fields.Date.context_today, readonly=True)
    cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale', string="Cargo Sale", copy=False)
    cargo_sale_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line', string="Cargo Sale Line")
    parent_customer_id = fields.Many2one('res.partner', string="Parent")
    shipment_type = fields.Selection(string="Shipment Type", related="cargo_sale_id.shipment_type", store=True)
    single_trip_reason = fields.Many2one('single.trip.cancel', 'One Way Reason')
    round_trip_reason = fields.Many2one('round.trip.cancel', 'Round Trip Vehicale')
    loc_from = fields.Many2one(string="From", related="cargo_sale_id.loc_from", store=True)
    loc_from_branch_id = fields.Many2one(related="loc_from.loc_branch_id", store=True)
    loc_to = fields.Many2one(string="To", related="cargo_sale_id.loc_to", store=True)
    payment_method = fields.Many2one('cargo_payment_method', string="Payment Method",
                                     related="cargo_sale_id.payment_method", store=True)
    payment_method_name = fields.Selection(related="payment_method.payment_type")
    wizard_cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale', string="Wizard Refund Cargo Sale")
    is_other_service_invoice = fields.Boolean(string="Other Service Invoice")
    is_demurrage_invoice = fields.Boolean(string="Demurrage Invoice")
    is_international_so_invoice = fields.Boolean(string="International SO Invoice")
    other_service_line_id = fields.Many2one('other_service_items', string="Other Service Line")
    is_so_invoice = fields.Boolean(string="IS SO Invoice", default=False)

    def _reverse_moves(self, default_values_list=None, cancel=False):
        ''' Reverse a recordset of account.move.
        If cancel parameter is true, the reconcilable or liquidity lines
        of each original move will be reconciled with its reverse's.
        :param default_values_list: A list of default values to consider per move.
                                    ('type' & 'reversed_entry_id' are computed in the method).
        :return:                    An account.move recordset, reverse of the current self.
        '''
        if not default_values_list:
            default_values_list = [{} for move in self]

        if cancel:
            lines = self.mapped('line_ids')
            # Avoid maximum recursion depth.
            if lines:
                lines.remove_move_reconcile()

        reverse_moves = self.env['account.move']
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'move_type': TYPE_REVERSE_MAP[move.move_type],
                'reversed_entry_id': move.id,
                'partner_id': move.partner_id.id,
            })
            reverse_moves += move.with_context(
                move_reverse_cancel=cancel,
                include_business_fields=True,
                skip_invoice_sync=move.move_type == 'entry',
            ).copy(default_values)

        reverse_moves.with_context(skip_invoice_sync=cancel).write({'line_ids': [
            Command.update(line.id, {
                'balance': -line.balance,
                'amount_currency': -line.amount_currency,
            })
            for line in reverse_moves.line_ids
            if line.move_id.move_type == 'entry' or line.display_type == 'cogs'
        ]})

        # Reconcile moves together to cancel the previous one.
        if cancel:
            if self.env.context.get('cancel_cargo_sale_line_ids'):
                reverse_moves.invoice_line_ids.filtered(lambda l: l.cargo_sale_line_id.id not in self.env.context.get('cancel_cargo_sale_line_ids')).unlink()
            reverse_moves.with_context(move_reverse_cancel=cancel)._post(soft=False)
            for move, reverse_move in zip(self, reverse_moves):
                group = defaultdict(list)
                for line in (move.line_ids + reverse_move.line_ids).filtered(lambda l: not l.reconciled):
                    group[(line.account_id, line.currency_id)].append(line.id)
                for (account, dummy), line_ids in group.items():
                    if account.reconcile or account.account_type in ('asset_cash', 'liability_credit_card'):
                        self.env['account.move.line'].browse(line_ids).with_context(move_reverse_cancel=cancel).reconcile()

        return reverse_moves


    @api.depends('amount_residual', 'move_type', 'state', 'company_id')
    def _compute_payment_state(self):
        stored_ids = tuple(self.ids)
        if stored_ids:
            self.env['account.partial.reconcile'].flush_model()
            self.env['account.payment'].flush_model(['is_matched'])

            queries = []
            for source_field, counterpart_field in (('debit', 'credit'), ('credit', 'debit')):
                queries.append(f'''
	                SELECT
	                    source_line.id AS source_line_id,
	                    source_line.move_id AS source_move_id,
	                    account.account_type AS source_line_account_type,
	                    ARRAY_AGG(counterpart_move.move_type) AS counterpart_move_types,
	                    COALESCE(BOOL_AND(COALESCE(pay.is_matched, FALSE))
	                        FILTER (WHERE counterpart_move.payment_id IS NOT NULL), TRUE) AS all_payments_matched,
	                    BOOL_OR(COALESCE(BOOL(pay.id), FALSE)) as has_payment,
	                    BOOL_OR(COALESCE(BOOL(counterpart_move.statement_line_id), FALSE)) as has_st_line
	                FROM account_partial_reconcile part
	                JOIN account_move_line source_line ON source_line.id = part.{source_field}_move_id
	                JOIN account_account account ON account.id = source_line.account_id
	                JOIN account_move_line counterpart_line ON counterpart_line.id = part.{counterpart_field}_move_id
	                JOIN account_move counterpart_move ON counterpart_move.id = counterpart_line.move_id
	                LEFT JOIN account_payment pay ON pay.id = counterpart_move.payment_id
	                WHERE source_line.move_id IN %s AND counterpart_line.move_id != source_line.move_id
	                GROUP BY source_line_id, source_move_id, source_line_account_type
	            ''')

            self._cr.execute(' UNION ALL '.join(queries), [stored_ids, stored_ids])

            payment_data = defaultdict(lambda: [])
            for row in self._cr.dictfetchall():
                payment_data[row['source_move_id']].append(row)
        else:
            payment_data = {}

        for invoice in self:
            if invoice.payment_state == 'invoicing_legacy':
                # invoicing_legacy state is set via SQL when setting setting field
                # invoicing_switch_threshold (defined in account_accountant).
                # The only way of going out of this state is through this setting,
                # so we don't recompute it here.
                continue

            currencies = invoice._get_lines_onchange_currency().currency_id
            currency = currencies if len(currencies) == 1 else invoice.company_id.currency_id
            reconciliation_vals = payment_data.get(invoice.id, [])
            payment_state_matters = invoice.is_invoice(True)

            # Restrict on 'receivable'/'payable' lines for invoices/expense entries.
            if payment_state_matters:
                reconciliation_vals = [x for x in reconciliation_vals if
                                       x['source_line_account_type'] in ('asset_receivable', 'liability_payable')]

            new_pmt_state = 'not_paid'
            if invoice.state == 'posted':

                # Posted invoice/expense entry.
                if payment_state_matters:

                    if currency.is_zero(invoice.amount_residual):
                        if any(x['has_payment'] or x['has_st_line'] for x in reconciliation_vals):

                            # Check if the invoice/expense entry is fully paid or 'in_payment'.
                            if all(x['all_payments_matched'] for x in reconciliation_vals):
                                new_pmt_state = 'paid'
                            else:
                                new_pmt_state = invoice._get_invoice_in_payment_state()

                        else:
                            new_pmt_state = 'paid'

                            reverse_move_types = set()
                            for x in reconciliation_vals:
                                for move_type in x['counterpart_move_types']:
                                    reverse_move_types.add(move_type)

                            in_reverse = (invoice.move_type in ('in_invoice', 'in_receipt')
                                          and (reverse_move_types == {'in_refund'} or reverse_move_types == {
                                        'in_refund', 'entry'}))
                            out_reverse = (invoice.move_type in ('out_invoice', 'out_receipt')
                                           and (reverse_move_types == {'out_refund'} or reverse_move_types == {
                                        'out_refund', 'entry'}))
                            misc_reverse = (invoice.move_type in ('entry', 'out_refund', 'in_refund')
                                            and reverse_move_types == {'entry'})
                            if in_reverse or out_reverse or misc_reverse:
                                new_pmt_state = 'reversed'

                    elif reconciliation_vals:
                        new_pmt_state = 'partial'

            invoice.payment_state = new_pmt_state
            if invoice.payment_state == 'paid' and invoice.is_so_invoice:
                if invoice.cargo_sale_id and invoice.cargo_sale_id.state != 'done':
                    invoice.cargo_sale_id.write({'state': 'done'})
            if invoice.payment_state == 'not_paid' and invoice.is_so_invoice:
                if invoice.cargo_sale_id.payment_method.payment_type == 'pod':
                    invoice.cargo_sale_id.write({'state': 'pod'})
                elif invoice.cargo_sale_id.payment_method.payment_type == 'cash':
                    invoice.cargo_sale_id.write({'state': 'confirm'})

    def js_remove_outstanding_partial(self, partial_id):
        ''' Called by the 'payment' widget to remove a reconciled entry to the present invoice.

        :param partial_id: The id of an existing partial reconciled with the current invoice.
        '''
        self.ensure_one()
        if self.env.context.get('invoice_id'):
            current_invoice = self.env['account.move'].browse(self.env.context['invoice_id'])
            for account_move_line in self:
                for payment in account_move_line.payment_id:
                    payment.bsg_vehicle_cargo_sale_line_ids.filtered(
                        lambda s: s.account_invoice_line_id.id in current_invoice.invoice_line_ids.ids).unlink()
        else:
            for account_move_line in self:
                for payment in account_move_line.payment_id:
                    payment.bsg_vehicle_cargo_sale_line_ids.unlink()
        partial = self.env['account.partial.reconcile'].browse(partial_id)
        return partial.unlink()

    def js_assign_outstanding_line(self, credit_aml_id):
        self.ensure_one()
        credit_aml = self.env['account.move.line'].browse(credit_aml_id)
        if credit_aml.payment_id:
            # credit_aml.payment_id.bsg_vehicle_cargo_sale_line_ids.unlink()
            for line in self.invoice_line_ids:
                if line.cargo_sale_line_id:
                    # todo migration note changing amount_residual to amount
                    if not line.is_paid and credit_aml.payment_id.amount > 0:
                        amount = credit_aml.payment_id.currency_id._convert(
                            credit_aml.payment_id.amount_total, line.move_id.currency_id, self.env.user.company_id,
                            credit_aml.payment_id.date or fields.Date.today())
                        credit_aml.payment_id.bsg_vehicle_cargo_sale_line_ids.with_context(
                            {'without_check_amount': True}).create({
                            'cargo_sale_line_id': line.cargo_sale_line_id.id,
                            'account_invoice_line_id': line.id,
                            'amount': amount <= (line.price_total - line.paid_amount) and amount or (
                                        line.price_total - line.paid_amount),
                            'residual': line.price_total - line.paid_amount,
                            'account_payment_id': credit_aml.payment_id.id,
                        })
                        if line.cargo_sale_line_id.is_paid and line.cargo_sale_line_id.state == 'draft':
                            line.cargo_sale_line_id.write({'state': 'confirm'})

        return super(bsg_inherit_account_invoice, self).js_assign_outstanding_line(credit_aml_id)

        # @api.model
        # def _refund_cleanup_lines(self, lines):
        """ Convert records to dict of values suitable for one2many line creation

            :param recordset lines: records to convert
            :return: list of command tuple for one2many line creation [(0, 0, dict of valueis), ...]
        """

        """print("In Clean Up>>>>>>>>>>>>>>>>>>>>>",self._context.get('cargo_sale_line_ids',False))
        if not self.cargo_sale_line_ids:
            return super(AccountInvoiceRefund, self)._refund_cleanup_lines()
        result = []
        for line in lines.filtered(lambda l: l.cargo_sale_line_id.id in self.cargo_sale_line_ids.ids):
            values = {}
            for name, field in line._fields.items():
                if name in MAGIC_COLUMNS:
                    continue
                elif field.type == 'many2one':
                    values[name] = line[name].id
                elif field.type not in ['many2many', 'one2many']:
                    values[name] = line[name]
                elif name == 'invoice_line_tax_ids':
                    values[name] = [(6, 0, line[name].ids)]
                elif name == 'analytic_tag_ids':
                    values[name] = [(6, 0, line[name].ids)]
            result.append((0, 0, values))
        return result"""

    @api.model
    def _prepare_refund(self, invoice, invoice_date=None, date=None, description=None, journal_id=None):
        """ Prepare the dict of values to create the new credit note from the invoice.
            This method may be overridden to implement custom
            credit note generation (making sure to call super() to establish
            a clean extension chain).

            :param record invoice: invoice as credit note
            :param string invoice_date: credit note creation date from the wizard
            :param integer date: force date from the wizard
            :param string description: description of the credit note from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the credit note
        """
        values = {}
        for field in self._get_refund_copy_fields():
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False
        if self._context.get('cargo_sale_line_ids', False):
            values['invoice_line_ids'] = self._refund_cleanup_lines(invoice.invoice_line_ids.filtered(
                lambda l: l.cargo_sale_line_id.id in self._context.get('cargo_sale_line_ids', False).ids))
        else:
            values['invoice_line_ids'] = self._refund_cleanup_lines(invoice.invoice_line_ids)

            tax_lines = invoice.tax_line_ids
            taxes_to_change = {
                line.tax_id.id: line.tax_id.refund_account_id.id
                for line in tax_lines.filtered(lambda l: l.tax_id.refund_account_id != l.tax_id.account_id)
            }
            cleaned_tax_lines = self._refund_cleanup_lines(tax_lines)
            values['tax_line_ids'] = self._refund_tax_lines_account_change(cleaned_tax_lines, taxes_to_change)

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif invoice['type'] == 'in_invoice':
            journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        else:
            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        values['journal_id'] = journal.id

        values['type'] = TYPE2REFUND[invoice['move_type']]
        values['invoice_date'] = invoice_date or fields.Date.context_today(invoice)
        values['date_due'] = values['invoice_date']
        values['state'] = 'draft'
        values['number'] = False
        values['invoice_origin'] = invoice.number
        values['reversed_entry_id'] = invoice.id
        values['reference'] = False

        if values['type'] == 'in_refund':
            values['invoice_payment_term_id'] = invoice.partner_id.property_supplier_payment_term_id.id
            partner_bank_result = self._get_partner_bank_id(values['company_id'])
            if partner_bank_result:
                values['partner_bank_id'] = partner_bank_result.id
        else:
            values['invoice_payment_term_id'] = invoice.partner_id.property_payment_term_id.id

        if date:
            values['date'] = date
        if description:
            values['name'] = description
        return values

    @api.onchange('parent_customer_id')
    def onchange_customer_type(self):
        if self.parent_customer_id:
            return {'domain': {
                'partner_id': [('id', 'in', self.parent_customer_id.child_ids.ids)],
            }}

    @api.model
    def _get_refund_copy_fields(self):
        result = super(bsg_inherit_account_invoice, self)._get_refund_copy_fields()
        bsg_copy_fields = ['parent_customer_id', 'shipment_type',
                           'single_trip_reason', 'round_trip_reason', 'loc_from', 'loc_from_branch_id', 'loc_to',
                           'payment_method',
                           'payment_method_name', 'wizard_cargo_sale_id', 'is_other_service_invoice',
                           'is_demurrage_invoice',
                           'is_international_so_invoice', 'other_service_line_id']
        return result + bsg_copy_fields


class AccountPayment(models.Model):
    _inherit = "account.payment"

    total_invoice_amount = fields.Float(string="Total Amount", compute="_get_total_invoice_amount")
    due_invoice_amount = fields.Float(string="Due Amount", compute="_get_total_invoice_amount")
    show_invoice_amount = fields.Boolean("Show Invoices Amount")

    # 
    @api.depends('show_invoice_amount')
    def _get_total_invoice_amount(self):
        amount_total = 0
        due_amount = 0
        for invoice in self.env['account.move'].search(
                [('cargo_sale_id', '=', self._context.get('pass_sale_order_id'))]):
            amount_total += invoice.amount_total
            due_amount += invoice.amount_residual
        self.total_invoice_amount = amount_total
        self.due_invoice_amount = due_amount


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def remove_move_reconcile(self):
        """ Undo a reconciliation """
        if self.env.context.get('invoice_id'):
            current_invoice = self.env['account.move'].browse(self.env.context['invoice_id'])
            for account_move_line in self:
                for payment in account_move_line.payment_id:
                    payment.bsg_vehicle_cargo_sale_line_ids.filtered(
                        lambda s: s.account_invoice_line_id.id in current_invoice.invoice_line_ids.ids).unlink()
        else:
            for account_move_line in self:
                for payment in account_move_line.payment_id:
                    payment.bsg_vehicle_cargo_sale_line_ids.unlink()
        return super(AccountMoveLine, self).remove_move_reconcile()
