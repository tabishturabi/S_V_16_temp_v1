# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
# from werkzeug import url_encode
import logging

_logger = logging.getLogger(__name__)

class HrDeputationRegisterPaymentWizard(models.TransientModel):
    _name = "deputation.register.payment.wizard"
    _description = "Deputation Register Payment Wizard"



    @api.model
    def default_get(self, fields):
        res = super(HrDeputationRegisterPaymentWizard, self).default_get(fields)
        deputation_vals = self.env['hr.deputations'].browse(self.env.context.get('active_id'))
        rec_name = deputation_vals.name
        # emp_name = deputation_vals.employee_id.name
        communication = "{} :بدل انتداب للإنتداب رقم".format(rec_name)
        Config = self.env.user.company_id
        res.update({
               'emp_deputation_acc_id': Config.account_id.id,
               'communication': communication,
            })
        return res


    @api.model
    def _default_amount(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        deputation_ids = self.env['hr.deputations'].browse(active_ids)
        deputation_states = set(deputation_ids.mapped('state'))
        if not all(state == 'accountant' for state in deputation_states):
            raise ValidationError('You can only register payment on accountant state.')
        total_net = sum(deputation_ids.mapped('total_amount'))
        return total_net


    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True)
    emp_deputation_acc_id = fields.Many2one('account.account', string="Employee Deputation Account", required=True)
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True, required=True)
    # Migration NOTE
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', required=True)
    # payment_method_id = fields.Many2one('account.payment.method.line', string='Payment Type', required=True)
    amount = fields.Monetary(string='Payment Amount', required=True, default = _default_amount)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True)
    communication = fields.Char(string='Memo')
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")
    deputation_id = fields.Many2one('hr.deputations',string="Deputation")

    @api.constrains('amount')
    def _check_amount(self):
        if not self.amount > 0.0:
            raise ValidationError(_('The payment amount must be Strictly positive.'))


    @api.depends('journal_id')
    def _compute_hide_payment_method(self):
        if not self.journal_id:
            self.hide_payment_method = True
            return
        journal_payment_methods = self.journal_id.available_payment_method_ids
        self.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.journal_id.available_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            return {'domain': {'payment_method_id': [('payment_type', '=', 'outbound'), ('id', 'in', payment_methods.ids)]}}
        return {}

    def _get_payment_vals(self,rec):
        """ Hook for extension """
        return {
            'name':'/',
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'partner_id': rec.employee_id.partner_id.id,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'payment_method_id': self.payment_method_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'date': self.payment_date,
            'ref': self.communication,
            #'destination_account_id' :,
            'voucher_line_ids': [(0, 0, {
                'account_id':self.emp_deputation_acc_id.id})],
        }

    def deputation_post_payment(self):
        
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        deputation_ids = self.env['hr.deputations'].browse(active_ids)

        # Create payment and post it
        for rec in deputation_ids:
            if not rec.employee_id.partner_id:
                raise ValidationError(_('Please Set Partner For Employee {}'.format(str(rec.employee_id))))
            print(rec)
            print(self._get_payment_vals(rec))
            payment = self.env['account.payment'].sudo().create(self._get_payment_vals(rec))
            payment.post_state()
            # Log the payment in the chatter
            # body = (_("A payment of %s %s with the reference <a href='/mail/view?%s'>%s</a> related to your Deputation %s has been made.") % (payment.amount, payment.currency_id.symbol, url_encode({'model': 'account.payment', 'res_id': payment.id}), payment.name, rec.loan_id))
            # rec.message_post(body=body)

            # Reconcile the payment and the overtime, i.e. lookup on the payable account move lines
            #account_move_lines_to_reconcile = self.env['account.move.line']
            #for line in payment.move_line_ids + rec.move_id.line_ids.filtered(lambda m: m.partner_id.id == rec.employee_name.partner_id.id):
            #    if line.account_id.internal_type == 'payable' and not line.reconciled:
            #        account_move_lines_to_reconcile |= line
            #account_move_lines_to_reconcile.reconcile()
            rec.write({'state':'done'})

        return {'type': 'ir.actions.act_window_close'}