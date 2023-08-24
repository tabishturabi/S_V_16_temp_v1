# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

class AccountInvoice(models.Model):
    _inherit = "account.move"

    #for checking cargo sale sate done if done than no need to update esle need to updatw
    # @api.multi
    # def write(self,vals):
    #     for invoice in self:
    #     #    if invoice.type == 'out_refund' and invoice.wizard_cargo_sale_id and vals.get('state') == 'paid':
    #     #        if invoice.wizard_cargo_sale_id.shipment_type != 'return':
    #     #            invoice.wizard_cargo_sale_id.write({'state' : 'cancel'})
    #         if vals.get('payment_state') == 'paid' and invoice.is_so_invoice:
    #            if invoice.cargo_sale_id and invoice.cargo_sale_id.state != 'done':
    #                 invoice.cargo_sale_id.write({'state' : 'done'})
    #         if vals.get('payment_state') == 'not_paid' and invoice.is_so_invoice:
    #             if invoice.cargo_sale_id.payment_method.payment_type == 'pod':
    #                 invoice.cargo_sale_id.write({'state': 'pod'})
    #             elif invoice.cargo_sale_id.payment_method.payment_type == 'cash':
    #                 invoice.cargo_sale_id.write({'state': 'confirm'})
    #     res = super(AccountInvoice, self).write(vals)
    #     return res
    # @api.model_create_multi
    # def create(self, vals_list):
    #     return 1/0
    
    def _get_payment(self):
        # if len(self.payment_ids) == 0:
        #     if self.state == 'paid' and self.payment_move_line_ids:
        #         self.payment = 1
        # else:
        #     self.payment = len(self.payment_ids.filtered(lambda r: r.state != 'reversal_entry'))
        #     self.patment_return = len(self.payment_ids.filtered(lambda r: r.state != 'reversal_entry'))
        self.payment = len(self.env['account.payment'].search([('invoice_ids','in',self.ids),('is_reconciled','=',True)]).filtered(lambda r: r.state != 'reversal_entry'))
        self.patment_return = len(self.env['account.payment'].search([('invoice_ids','in',self.ids),('is_reconciled','=',True)]).filtered(lambda r: r.state != 'reversal_entry'))

    # @api.multi
    def action_invoice_validate(self):
        for data in self.payment_ids:
            if data.state in ['draft','voucher']:
                raise UserError(_("Please Validate First Draft Voucher"))
    
    
    def _get_validate_payment(self):
        payment_list = []
        for rec in self:
            rec.is_validate = False
            if rec.payment_ids:
                for data in rec.payment_ids:
                    payment_list.append(data.state)
            if not rec.cargo_sale_line_id:
                if rec.payment_ids:
                    if 'draft' in payment_list or 'cancel' in payment_list:   #or 'voucher' in payment_list
                        rec.is_validate = True
                else:
                    rec.is_validate = False
            else:
                rec.is_validate = False
            
    # @api.multi
    def action_view_payment_voucher(self):
        """
        This function returns an action that display existing payments of given
        account invoices.
        When only one found, show the payment immediately.
        """
        
        action = self.env.ref('account.action_account_payments_payable')
        
        return {
        'name': 'Payment Voucher',
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'account.payment',
        'view_id': False,
        'type': 'ir.actions.act_window',
        'domain': [('id', 'in', self.payment_ids.filtered(lambda r: r.state != 'reversal_entry').ids)],
        'context' : {'create' : False}
        }

    
    def _get_paid_voucher_amount(self):
        total_discount = 0
        self.paid_voucher_amount = 0
        if self.move_type == 'out_refund':
            total_discount = self.amount_total
        else:
            for data in self.payment_ids:
                if data.invoice_id:
                    total_discount += data.invoice_id.amount_total
        self.invoice_discount = total_discount
        if self.payment_ids:
            self.paid_voucher_amount = self.amount_total - self.amount_residual - self.invoice_discount
                    
    # @api.multi
    def action_view_payment(self):
        """
        This function returns an action that display existing payments of given
        account invoices.
        When only one found, show the payment immediately.
        """
        action = self.env.ref('account.action_account_payments_payable')

        return {
        'name': 'Payment Voucher',
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'account.payment',
        'view_id': False,
        'type': 'ir.actions.act_window',
        'domain': [('id', 'in', self.env['account.payment'].search([('invoice_ids','in',self.ids),('is_reconciled','=',True)]).filtered(lambda r: r.state != 'reversal_entry').ids)],
        'context' : {'create' : False}
        }

        # result = action.read()[0]
        
        # # choose the view_mode accordingly
        # if len(self.payment_ids) != 1:
        #     if len(self.payment_ids) == 0:
        #         res = self.env.ref('account.view_account_payment_form', False)
        #         result['views'] = [(res and res.id or False, 'form')]
        #         result['res_id'] = self.payment_move_line_ids.payment_id.id
        #     else:
        #         result['domain'] = "[('id', 'in', " + str(
        #         self.payment_ids.ids) + ")]"
        # elif len(self.payment_ids) == 1:
        #     res = self.env.ref('account.view_account_payment_form', False)
        #     result['views'] = [(res and res.id or False, 'form')]
        #     result['res_id'] = self.payment_ids.id
        # return result

    seq_no = fields.Integer("Sequence No",compute='_seq_line_numbers',readonly=True, default=False)
    payment = fields.Integer("Payment",compute="_get_payment")
    patment_return = fields.Integer("Payment Vocuher", compute="_get_payment")
    is_validate = fields.Boolean(string="Is Payment", compute="_get_validate_payment")
    paid_voucher_amount = fields.Float(string="Paid Voucher Amount", compute="_get_paid_voucher_amount")
    invoice_discount = fields.Float(string="Invoice Discount", compute="_get_paid_voucher_amount")
    
    
    def _seq_line_numbers(self):
        line_num = 1    
        if self.ids:
            first_line_rec = self.browse(self.ids)

            for line_rec in first_line_rec:
                line_rec.seq_no = line_num
                line_num += 1

    # #Total Amount vlaue should not be 0 
    # 
    # @api.constrains('amount_total')
    # def _check_amount(self):
    #     if not self.amount_total:
    #         raise UserError(_('Invoice Total Amount must be greater than 0...!'))

