# -*- coding: utf-8 -*- 
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        return {
            'date': self.date,
            'ref': self.ref or '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
            'collection':self.collectionre,
            'pety_cash_id' : self.petty_cash_id.id if self.petty_cash_id else False,
        }

class AccountMove(models.Model):
    _inherit = "account.move"

    is_petty_cash = fields.Boolean(string="Is Petty Cash")
    is_petty_expense = fields.Boolean(string="Is Petty Expenses")
    pety_cash_id = fields.Many2one('petty.cash.expense.accounting', string="Petty Cash Id")
    expense_id = fields.Many2one('expense.accounting.petty', string="Expense Id")
    # Migration Note
    # invoice_id = fields.Many2one('account.move',related='line_ids.invoice_id')
    invoice_id = fields.Many2one('account.move')
    # payment_id = fields.Many2one('account.payment',related='line_ids.payment_id')
    picking_id = fields.Many2one('stock.picking',related='stock_move_id.picking_id')

    #override to used pass refrence to jounral entry
    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if res.pety_cash_id:
            res.update({'ref' : res.pety_cash_id.name})
        return res


    # override write method

    def write(self, values):
        res = super(AccountMove, self).write(values)
        for rec in self:
            if ((rec.is_petty_expense and rec.expense_id) or (rec.is_petty_cash and rec.pety_cash_id)) and not self.env.context.get('from_petty'):
                raise UserError(_("Sorry! You Can't Edit Petty Cash Move"))
        return res



    def button_cancel(self):
        for rec in self:
            if ((rec.is_petty_expense and rec.expense_id) or (rec.is_petty_cash and rec.pety_cash_id)) and not self.env.context.get('from_petty'):
                raise UserError(_("Sorry! You Can't Edit Petty Cash Move"))
        return super(AccountMove, self).button_cancel()

    #overriden to restict if voucher cancel and re-draft it not allow to create new sequnce , #changes to sequnce as need by a.emera
    '''
    def post(self, invoice=False):
        self._post_validate()
        # Create the analytic lines in batch is faster as it leads to less cache invalidation.
        self.mapped('line_ids').create_analytic_lines()
        for move in self:
            if move.name == '/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.move_name and invoice.move_name != '/':
                    new_name = invoice.move_name
                else:
                    if journal.sequence_id:
                        # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
                        sequence = journal.sequence_id
                        if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
                            if not journal.refund_sequence_id:
                                raise UserError(_('Please define a sequence for the credit notes'))
                            sequence = journal.refund_sequence_id

                        search_move_line_id = self.env['account.move.line'].search([('move_id','=',move.id)],limit=1)
                        if search_move_line_id.payment_id and search_move_line_id.payment_id.move_name:
                            new_name = search_move_line_id.payment_id.move_name
                        else:
                            if move.expense_id:
                                new_name = str(move.expense_id.name) + '/' + str(move.expense_id.sequence)
                            else:
                                new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                    else:
                        raise UserError(_('Please define a sequence on the journal.'))

                if new_name:
                    move.name = new_name

            if move == move.company_id.account_opening_move_id and not move.company_id.account_bank_reconciliation_start:
                # For opening moves, we set the reconciliation date threshold
                # to the move's date if it wasn't already set (we don't want
                # to have to reconcile all the older payments -made before
                # installing Accounting- with bank statements)
                move.company_id.account_bank_reconciliation_start = move.date

        return self.write({'state': 'posted'})'''

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # getting petty cash id
     
    @api.depends('payment_id')
    def _get_petty_cash_id(self):
        if self.payment_id and self.payment_id.petty_cash_id:
            self.petty_cash_id = self.payment_id.petty_cash_id

    petty_cash_id = fields.Many2one('petty.cash.expense.accounting',compute="_get_petty_cash_id") 
    expense_accouting_petty_id = fields.Many2one('expense.accounting.petty.tree') 


    #override to used diablse pass branch on move line as need by a.emra
    @api.model
    def create(self, vals):
        res = super(AccountMoveLine, self).create(vals)
        if res.payment_id.petty_cash_id:
            res['bsg_branches_id'] = False
        return res    
    # #override to used voucher line accont and analytic account
    # @api.model
    # def create(self, vals):
    #     # if not vals.get('account_id'):
    #     #     raise UserError(_("Be sure you have Defined Account in Partner or Journal"))
    #     # payment = self.env['account.payment'].search([('id','=',vals.get('payment_id'))])
    #     # if payment.payment_type == 'outbound':
    #     #     if payment.petty_cash_id:
    #     #         # if vals.get('credit') != 0.0 and not vals.get('invoice_id'):
    #     #         #     vals['account_id'] = payment.journal_id.default_account_id.id
    #     #         # if vals.get('debit') != 0.0 and not vals.get('invoice_id'):
    #     #         #     vals['account_id'] = payment.debit_account_id.id
    #     #         move_id = self.env['account.move'].browse(vals.get('move_id'))
    #     #         move_id.write({'is_petty_cash' : True})
    #     res = super(AccountMoveLine, self).create(vals)
    #     if res.payment_id.petty_cash_id:
    #         res.update({'name' : str(res.payment_id.name) + ' - ' + res.payment_id.petty_cash_id.descripiton})
    #     return res

