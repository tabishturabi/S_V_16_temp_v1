# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class loan_advance_payment(models.Model):
    _name = 'loan.advance.payment'
    _description = 'Loan Advance Payment'

    
    @api.depends('loan_app_id', 'amount')
    def preview_payments(self):
        final_list = []
        loan_payment = self.env['loan.payment']
        if self.amount and self.amount <= 0:
            raise ValidationError(_('Please enter the amount greater than zero'))
        if self.loan_app_id and self.amount:
            loan_payment_ids = loan_payment.search([('loan_app_id', '=', self.loan_app_id.id),
                                                        ('state', '=', 'draft')])
            loan_payment_paid_ids = loan_payment.search([('loan_app_id', '=', self.loan_app_id.id),
                                                                ('state', '=', 'paid')])
            balance_list = []
            for each in loan_payment_paid_ids:
                balance_list.append(each.balance_amt)
            if not balance_list:
                remain_balance = self.loan_app_id.amount
            if balance_list:
                remain_balance = balance_list[-1]
            bal = "%.2f" % (remain_balance)
            if self.amount and self.amount > float(bal):
                raise ValidationError(_('Please enter the amount less than %s' % (bal)))
            bal = "%.2f" % (remain_balance)
            if self.amount == float(bal):
                final_list = []
            else:
                if self.loan_app_id.loan_method == 'reducing':
                    principal = remain_balance - self.amount
                    months = len(loan_payment_ids)
                    rate = self.loan_app_id.loan_type_id.interest_rate / 100.00
                    per = np.arange(months) + 1
                    ipmt = np.ipmt(rate / 12, per, months, principal)
                    ppmt = np.ppmt(rate / 12, per, months, principal)
                    pmt = np.pmt(rate / 12, months, principal)
                    if self.loan_app_id.loan_type_id and self.loan_app_id.loan_type_id.interest_rate:
                        if np.allclose(ipmt + ppmt, pmt):
                            for payment in per:
                                index = payment - 1
                                principal = principal + ppmt[index]
                                date = datetime.date.today() + relativedelta(months=payment)
                                date = date.replace(day=1)
    #                             if self.loan_app_id.loan_type_id and self.loan_app_id.loan_type_id.interest_rate:
                                final_list.append((0, 0, {
                                    'due_date': date,
                                    'principal': (ppmt[index] * -1),
                                    'interest': (ipmt[index] * -1),
                                    'total': (ppmt[index] * -1) + (ipmt[index] * -1),
                                    'balance_amt': abs(principal),
                                }))
                    elif self.loan_app_id.loan_type_id and not self.loan_app_id.loan_type_id.interest_rate:
                        principal = remain_balance - self.amount
                        rate = self.loan_app_id.loan_type_id.interest_rate / 100 * principal
                        time = float(len(loan_payment_ids)) / 12
                        months = self.loan_app_id.term
                        per = np.arange(months) + 1
                        each_month_payment = balance = 0.00
                        if time:
                            balance = ((principal / time + rate) / 12) * self.loan_app_id.term
                            for each_term in per:
                                date = datetime.date.today() + relativedelta(months=each_term)
                                date = date.replace(day=1)
                                if self.loan_app_id.loan_type_id and self.loan_app_id.loan_method:
                                    interest = principal / time + rate
                                    each_month_payment = interest / 12
                                    total_pay_amount = each_month_payment * self.loan_app_id.term
                                    balance -= each_month_payment
                                    monthly_interest = rate * time / self.loan_app_id.term
                                    monthly_principal = principal / self.loan_app_id.term
                                    final_list.append((0, 0, {
                                                    'due_date': date,
                                                    'number': each_term,
                                                    'principal': monthly_principal,
                                                    'interest': monthly_interest,
                                                    'interest_rate': str("%.2f" % (self.loan_app_id.loan_type_id.interest_rate / 12)) + " %",
                                                    'total': monthly_interest + monthly_principal,
                                                    'balance_amt': abs(balance)
                                                    }))
                elif self.loan_app_id.loan_method == 'flat':
                    principal = remain_balance - self.amount
                    rate = self.loan_app_id.loan_type_id.interest_rate / 100 * principal
                    time = float(len(loan_payment_ids)) / 12
                    months = self.loan_app_id.term
                    per = np.arange(months) + 1
                    each_month_payment = balance = 0.00
                    if time:
                        balance = ((principal / time + rate) / 12) * self.loan_app_id.term
                        for each_term in per:
                            date = datetime.date.today() + relativedelta(months=each_term)
                            date = date.replace(day=1)
                            if self.loan_app_id.loan_type_id and self.loan_app_id.loan_method:
                                interest = principal / time + rate
                                each_month_payment = interest / 12
                                total_pay_amount = each_month_payment * self.loan_app_id.term
                                balance -= each_month_payment
                                monthly_interest = rate * time / self.loan_app_id.term
                                monthly_principal = principal / self.loan_app_id.term
                                final_list.append((0, 0, {
                                                'due_date': date,
                                                'number': each_term,
                                                'principal': monthly_principal,
                                                'interest': monthly_interest,
                                                'interest_rate': str("%.2f" % (self.loan_app_id.loan_type_id.interest_rate / 12)) + " %",
                                                'total': monthly_interest + monthly_principal,
                                                'balance_amt': abs(balance)
                                                }))
            self.lap_line_ids = final_list
            return final_list

    
    def new_payments(self,payment):
        loan_payment = self.env['loan.payment']
        amount = self.amount
        install_amount = 0
        while(amount > 0):
            install_amount = amount
            first_draft_install = loan_payment.search([('loan_app_id', '=', self.loan_app_id.id),
                                                        ('state', '=', 'draft')],order='due_date',limit=1)
            if amount >= first_draft_install.total:
                install_amount = first_draft_install.total
                first_draft_install.update({
                        'state': 'paid',
                        'extra': first_draft_install.extra + install_amount
                        })
            else:
                first_draft_install.update({
                        'extra': first_draft_install.extra + install_amount
                        })            
            amount -=  install_amount
        self.env['loan.prepayment'].create({
                                        'employee_id' : self.employee_id.id,
                                        'loan_app_id': self.loan_app_id.id,
                                        'date': self.date,
                                        'amount': self.amount,
                                        'journal_id': self.journal_id.id,
                                        'emp_loan_acc_id':self.emp_loan_acc_id.id,
                                        'state': 'done',
                                        'name': self.communication,
                                        'payment_id':payment.id,
                                    })
        template_id = self.env.ref('loan.email_template_for_new_loan_emi')
        self.loan_app_id.update({'advance_amt': self.amount})
        template_id.send_mail(self.loan_app_id.id)
        self.loan_app_id.employee_id.message_post(subject=_('New Loan EMI'),
                                                  body=_("Your new emi is calculated"))
        return {
            'res_id': self.loan_app_id.id,
            'view_mode': 'form',
            'res_model': 'loan.application',
            'type': 'ir.actions.act_window',
            'nodestroy' : False,
        }



    @api.model
    def default_get(self, fields):
        res = super(loan_advance_payment, self).default_get(fields)
        loan_setting_id = self.env['loan.setting'].sudo().search([], limit=1, order='id desc')
        res.update({
               'emp_loan_acc_id': loan_setting_id.emp_loan_acc_id.id,
               'journal_id': loan_setting_id.account_journal_id.id,
            })
        return res

    employee_id = fields.Many2one('hr.employee',required=True,domain=[('loan_ids.state','=','paid')])
    loan_app_id = fields.Many2one('loan.application', string="Loan Application", required=True)
    lap_line_ids = fields.One2many('loan.advance.payment.line', 'loan_advance_payment_id',
                                   string="Payment Lines",
                                   compute="preview_payments")
    create_entries = fields.Boolean('Create Entries', default=True)                               
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True)
    emp_loan_acc_id = fields.Many2one('account.account', string="Employee Loan Account",readonly=True,required=True)
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True, required=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', required=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True)
    total_remaining_amt = fields.Float('Remaining Amount', related='loan_app_id.total_remaining_amt')
    communication = fields.Char(string='Memo')
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")

    
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
            'name':self.communication,
            'partner_type': 'customer',
            'payment_type': 'inbound',
            'partner_id': rec.employee_id.partner_id.id,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'payment_method_id': self.payment_method_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'date': self.date,
            'communication': self.communication,
            #'destination_account_id' :,
            'voucher_line_ids': [(0, 0, {
                'account_id':self.emp_loan_acc_id.id})],
        }

    
    def loan_post_payment(self):
        if self.amount and self.amount <= 0:
            raise ValidationError(_('Please enter the amount greater than zero'))
        loan_ids = self.env['loan.application'].browse(self.loan_app_id.id)

        # Create payment and post it
        for rec in loan_ids:
            if self.amount > rec.total_remaining_amt:
                raise ValidationError(_('Amount Is Bigger Than Remanning Amount'))
            if not rec.employee_id.partner_id:
                raise ValidationError(_('Please Set Partner For Employee {}'.format(str(rec.employee_id))))
            payment = self.env['account.payment'].create(self._get_payment_vals(rec))
            payment.post()
            #self.new_payments(payment)
            # Log the payment in the chatter
            #body = (_("A payment of %s %s with the reference <a href='/mail/view?%s'>%s</a> related to your Loan %s has been made.") % (payment.amount, payment.currency_id.symbol, url_encode({'model': 'account.payment', 'res_id': payment.id}), payment.name, rec.loan_id))
            #rec.message_post(body=body)

            # Reconcile the payment and the overtime, i.e. lookup on the payable account move lines
            #account_move_lines_to_reconcile = self.env['account.move.line']
            #for line in payment.move_line_ids + rec.move_id.line_ids.filtered(lambda m: m.partner_id.id == rec.employee_name.partner_id.id):
            #    if line.account_id.internal_type == 'payable' and not line.reconciled:
            #        account_move_lines_to_reconcile |= line
            #account_move_lines_to_reconcile.reconcile()
            #rec.write({'payment_id':payment.id,'state':'paid','paid_date':self.date})

        return self.new_payments(payment)


class loan_advance_payment_line(models.Model):
    _name = 'loan.advance.payment.line'
    _description = 'Loan Advance Payment'

    due_date = fields.Date(string="Due Date")
    principal = fields.Float("Principal")
    balance_amt = fields.Float("Balance")
    interest = fields.Float("Interest")
    total = fields.Float("Total")
    loan_advance_payment_id = fields.Many2one('loan.advance.payment', string="Advance Payment")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: