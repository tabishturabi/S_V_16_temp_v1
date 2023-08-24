# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BudgetReconciliationInternalTransfer(models.TransientModel):
    _name = 'budget_reconciliation_internal_transfer'
    _description = "Budget Reconciliation Internal Transfer"
    
    
    
    def _check_valid_status(self,single=False):
        active_ids = self.env.context.get('active_ids')
        payment_id = self.env['account.payment'].search([('id','=',active_ids[0])])
        PaymentIds = self.env['account.payment'].search([('id','in',active_ids),('payment_method_id.name','=','Electronic'),('budget_number','=',payment_id.budget_number),('branch_ids','=',payment_id.branch_ids.id)])
        if len(active_ids) == len(PaymentIds):
            if single:
                return payment_id
            else:
                return PaymentIds
    
    def _get_payment_journal_id(self):
        validated_id = self._check_valid_status(single=True)
        if validated_id:
            return validated_id.journal_id.id
        else:
            return False
    
    def _get_payment_branch_id(self):
        validated_id = self._check_valid_status(single=True)
        if validated_id:
            return validated_id.branch_ids.id
        else:
            return False
    
    def _get_payment_amount(self):
        validated_ids = self._check_valid_status()
        if validated_ids:
            return sum(validated_id.amount for validated_id in validated_ids)
        else:
            return False
    
    payment_journal_id = fields.Many2one('account.journal',string="Payment Journal" ,readonly=True, domain=[('type', 'in', ('bank', 'cash'))],default=_get_payment_journal_id)
    tax_amount = fields.Float(string="Tax Amount")
    bank_charges = fields.Float(string="Bank Charges")
    destination_journal_id = fields.Many2one('account.journal',string="Transfer To",domain=[('type', '=', 'bank')],)
    payment_amount = fields.Float(string="Payment Amount", default=_get_payment_amount,readonly=True)
    payment_date = fields.Date("Payment Date",default=fields.Date.context_today, required=True, copy=False)
    payment_method_id = fields.Many2one('account.payment.method',string="Payment Method")
    budget_number = fields.Char('Budget Number')
    branch_ids = fields.Many2one('bsg_branches.bsg_branches',string='Branch',default=_get_payment_branch_id)
    
    def action_add_budget_reconciliation(self):
        if self.payment_amount and self.payment_journal_id:
            payment_id = self.env['account.payment']
            payment_method_id = self.env['account.payment.method'].search([('name','=','Electronic')])
            vals = {
                'payment_type':'transfer',
                'amount':self.payment_amount,
                'journal_id':self.payment_journal_id.id,
                'destination_journal_id':self.destination_journal_id.id,
                'payment_date':self.payment_date,
                'tax_amount':self.tax_amount,
                'bank_charges':self.bank_charges,
                'payment_method_id':payment_method_id.id,
                'branch_ids':self.branch_ids.id
                }
            csl_id = payment_id.create(vals)
        else:
            raise UserError(_("Some Value Are Not Match."))