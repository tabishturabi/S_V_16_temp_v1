# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
import json

class AccountJournal(models.Model):
    _inherit = "account.journal" 
    
    is_budget_recon = fields.Boolean('Is A Budget Reconciliation', copy=False)

class account_payment(models.Model):
    _inherit = "account.payment" 
    
    total_amount = fields.Float(string='Total Amount', copy=False)
    tamara_charges = fields.Float(string='Tamara Charges', copy=False)
    is_internal = fields.Boolean('Is Internal', copy=False)
    is_budget_recon = fields.Boolean('Budget Reconciliation', copy=False)
    receipt_voucher = fields.Char('Receipt Voucher')
    
    
    def button_related_voucher(self):
        return {
            'name': _('Receipt Vouchers'),
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id':False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', json.loads(self.receipt_voucher))],
        }
    
    def action_move_to_internal(self, old_move=None):
        config = self.env.user.company_id
        if config.sequnce_id:
            if not self.is_sequnce and self.journal_id.id != self.cancel_jounral_id.id:
                if self.branch_ids and self.branch_ids.branch_no:
                    self.name = str(self.branch_ids.branch_no) + config.sequnce_id.next_by_id()
                    self.is_sequnce = True 
                else:
                    self.name = config.sequnce_id.next_by_id()
                    self.is_sequnce = True
        trip_id = self.env['account.fuel.trip.configuration'].search([])
#         self.communication = self.budget_number +' -#'+ str(self.date)
        if self.budget_number:
            self.communication = self.budget_number +'-#'+ str(self.date)
        if old_move:
            for m in old_move.line_ids:
                m.name = self.name
        if trip_id.tax_account_id and trip_id.bank_charge_account_id:
            MoveObj = self.env['account.move']
            vals = {
                'ref':self.name,
                'journal_id':self.destination_journal_id.id,
                'date':self.date
            }
            move = MoveObj.create(vals)
            move_lines = []
            if self.tamara_charges > 0:
                if not trip_id.tamara_charges_account_id:
                    raise ValidationError(
                        _("Pls setup account for tamara charges on add rewards and fuel configuration"))
                move_lines.append({
                    'account_id':trip_id.tamara_charges_account_id.id,
                    'name':'#TAMARA CHARGE',
                    'debit':self.tamara_charges,
                    'credit':0.0,
                    'payment_id':self.id,
                    'move_id':move.id
                })
            if self.tax_amount > 0:
                move_lines.append({
                    'account_id':trip_id.tax_account_id.id,
                    'name':'#TAX CHARGE',
                    'debit':self.tax_amount,
                    'credit':0.0,
                    'payment_id':self.id,
                    'move_id':move.id
                })
            if self.bank_charges > 0:
                move_lines.append({
                    'account_id':trip_id.bank_charge_account_id.id,
                    'name':'#BANK CHARGE',
                    'debit':self.bank_charges,
                    'credit':0.0,
                    'payment_id':self.id,
                    'move_id':move.id
                })
            move_lines.append({
                'account_id':self.destination_journal_id.default_account_id.id,
                'name':self.communication,
                'debit': self.amount - (self.tax_amount + self.bank_charges + self.tamara_charges),
                'credit':0.0,
                'payment_id':self.id,
                'move_id':move.id
            })
            move_lines.append({
                'account_id':self.company_id.transfer_account_id.id,
                'name':self.communication,
                'debit': 0.0,
                'credit':self.total_amount if self.total_amount else self.amount,
                'payment_id':self.id,
                'move_id':move.id
            })
            lines = [(0, 0, line_move) for line_move in move_lines]
            move.write({'line_ids':lines})
            move.action_post()
            self.write({'state' : 'posted'})
              #  (transfer_credit_aml + transfer_debit_aml).reconcile()
            move_ids = self.env['account.move.line'].search([('id','in',self.move_line_ids.ids),('account_id','=',self.company_id.transfer_account_id.id)])
            if move_ids:
                move_ids.reconcile()
        else :
            raise UserError(_("Configure Bank Charges Account and Tax Account First"))

    def post_state(self):
        for res in self:
            
            if res.is_internal or res.bank_charges > 0:
                move = res.post_for_internal()
                res.action_move_to_internal(move)
            else:
                return super(account_payment,self).post_state()

    
    def post_for_internal(self):
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
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.date).next_by_code(sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = self.total_amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)
            rec.write({'move_name': move.name})
            return move

class AccountConfiguration(models.Model):
    _inherit = 'account.fuel.trip.configuration'
    _description = "Account Fuel Trip Configuration"
    
    
    bank_charge_account_id = fields.Many2one(comodel_name="account.account",string="Bank Charges Account") 
    tax_account_id = fields.Many2one(comodel_name="account.account", string="Tax Account")
    tamara_charges_account_id = fields.Many2one(comodel_name="account.account", string="Tamara Charges Account")

