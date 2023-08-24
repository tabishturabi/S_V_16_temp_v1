# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# Account Payment
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('account_id', 'display_type')
    def _check_payable_receivable(self):
        for line in self:
            account_type = line.account_id.account_type
            if not self.env.context.get('is_trip'):
                if line.move_id.is_sale_document(include_receipts=True):
                    if (line.display_type == 'payment_term') ^ (account_type == 'asset_receivable'):
                        raise UserError(_("Any journal item on a receivable account must have a due date and vice versa."))
                if line.move_id.is_purchase_document(include_receipts=True):
                    if (line.display_type == 'payment_term') ^ (account_type == 'liability_payable'):
                        raise UserError(_("Any journal item on a payable account must have a due date and vice versa."))

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    is_fleet_operation = fields.Boolean(seting="Is Fleet Operation")

    @api.model
    def _get_refund_copy_fields(self):
        result = super(AccountInvoice, self)._get_refund_copy_fields()
        trip_coll_copy_fields = ['is_fleet_operation']
        return result + trip_coll_copy_fields
    
    #overide to allow for vendor bill
    @api.onchange('invoice_cash_rounding_id', 'invoice_line_ids', 'tax_line_ids')
    def _onchange_cash_rounding(self):
        # Drop previous cash rounding lines
        lines_to_remove = self.invoice_line_ids.filtered(lambda l: l.sequence == 9999)#as removed added line when removed
        if lines_to_remove:
            self.invoice_line_ids -= lines_to_remove

        # Clear previous rounded amounts
        for tax_line in self.invoice_line_ids.tax_ids:
            if tax_line.amount != 0.0:
              tax_line.amount = 0.0

        if self.invoice_cash_rounding_id and self.move_type:# in ('out_invoice', 'out_refund') -> removed as need on vendor bill
            rounding_amount = self.invoice_cash_rounding_id.compute_difference(self.currency_id, self.amount_total)
            if not self.currency_id.is_zero(rounding_amount) or self.is_fleet_operation:
                if self.invoice_cash_rounding_id.strategy == 'biggest_tax':
                    # Search for the biggest tax line and add the rounding amount to it.
                    # If no tax found, an error will be raised by the _check_cash_rounding method.
                    if not self.tax_line_ids:
                        return
                    biggest_tax_line = None
                    for tax_line in self.tax_line_ids:
                        if not biggest_tax_line or tax_line.amount > biggest_tax_line.amount:
                            biggest_tax_line = tax_line
                    biggest_tax_line.amount_rounding += rounding_amount
                elif self.invoice_cash_rounding_id.strategy == 'add_invoice_line' and not self.currency_id.is_zero(rounding_amount):
                    # Create a new invoice line to perform the rounding

                    # zero check added as per nabil
                    if rounding_amount > 0:
                        rounding_line = self.env['account.move.line'].new({
                            'name': self.invoice_cash_rounding_id.name,
                            'invoice_id': self.id,
                            'account_id': self.invoice_cash_rounding_id.account_id.id,
                            'price_unit': rounding_amount,
                            'account_analytic_id': self._context.get('analytic_id', False),
                            'fleet_id' : self._context.get('fleet_id', False),
                            'quantity': 1,
                            'is_rounding_line': True,
                            'branch_id' : self.env.user.user_branch_id.id,
                            'sequence': 9999  # always last line
                        })
                        # To be able to call this onchange manually from the tests,
                        # ensure the inverse field is updated on account.invoice.
                        if not rounding_line in self.invoice_line_ids:
                            self.invoice_line_ids += rounding_line
