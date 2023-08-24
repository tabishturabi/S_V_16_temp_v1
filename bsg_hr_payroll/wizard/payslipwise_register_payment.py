# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class HrPayslipRegisterPaymentWizard(models.TransientModel):
    _name = "hr.payslip.register.payment.wizard"
    _description = "Expense Report Register Payment wizard"

    @api.model
    def _default_amount(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        payslip_ids = self.env['hr.payslip'].browse(active_ids)
        payslip_states = set(payslip_ids.mapped('state'))
        payslip_batch_ids = list(set(payslip_ids.mapped('payslip_run_id')))
        if not all(state == 'done' for state in payslip_states):
            raise ValidationError('You can only register payment for payslips in state Done.')
        if not all(batch == batch[0] for batch in payslip_batch_ids):
            raise ValidationError('You can only register payment for payslips that are of the same batch')
        total_net = sum(payslip_ids.mapped('total_net'))
        return total_net


    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True, required=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', required=True)
    amount = fields.Monetary(string='Payment Amount', required=True, default = _default_amount)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True)
    communication = fields.Char(string='Memo')
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")


    
    @api.constrains('amount')
    def _check_amount(self):
        if not self.amount > 0.0:
            raise ValidationError(_('The payment amount must be strictly positive.'))

    
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
            payment_methods = self.journal_id.available_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            return {'domain': {'payment_method_id': [('payment_type', '=', 'outbound'), ('id', 'in', payment_methods.ids)]}}
        return {}

    
    def expense_post_payment(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        payslip_ids = self.env['hr.payslip'].browse(active_ids)
        name = _('Payslip payment')
        payment_journal_id = self.journal_id
        date = self.date
        currency = self.currency_id
        move_dict = {
            'narration': name,
            'ref': payslip_ids[0].payslip_run_id.name,
            'journal_id': payment_journal_id.id,
            'date': date,
        }
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        commission_amount = 0.0
        commission_tax_amount = 0.0
        for slip in payslip_ids:
            slip_debit = 0
            slip_credit = 0
            for line in slip.details_by_salary_rule_category:
                amount = currency.round(slip.credit_note and -line.total or line.total)
                if currency.is_zero(amount):
                    continue
                debit_account_id =line.salary_rule_id.account_credit.id
                debit_account_type = line.salary_rule_id.account_credit and line.salary_rule_id.account_credit or False
                credit_account_id = line.salary_rule_id.account_debit.id
                credit_account_type = line.salary_rule_id.account_debit and line.salary_rule_id.account_debit or False


                if debit_account_id and debit_account_type == 'payable':
                    if payslip_ids.type == 'holiday':
                        if line.salary_rule_id.is_get_from_leave:
                            debit_account_id = line.salary_rule_id.leave_debit_account_id.id
                        else:
                            debit_account_id = line.salary_rule_id.account_debit.id
                    debit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(credit_account=False),
                        'account_id': debit_account_id,
                        'journal_id': payment_journal_id.id,
                        'date': date,
                        'debit': amount > 0.0 and amount or 0.0,
                        'credit': amount < 0.0 and -amount or 0.0,
                        'tax_line_id': line.salary_rule_id.account_tax_id.id

                    })
                    line_ids.append(debit_line)
                    slip_debit += debit_line[2]['debit'] - debit_line[2]['credit']
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

                if credit_account_id and credit_account_type == 'payable':
                    if payslip_ids.type == 'holiday':
                        if line.salary_rule_id.is_get_from_leave:
                            credit_account_id = line.salary_rule_id.leave_credit_account_id.id
                        else:
                            credit_account_id = line.salary_rule_id.account_credit.id
                    credit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(credit_account=True),
                        'account_id': credit_account_id,
                        'journal_id': payment_journal_id.id,
                        'date': date,
                        'debit': amount < 0.0 and -amount or 0.0,
                        'credit': amount > 0.0 and amount or 0.0,
                        'tax_line_id': line.salary_rule_id.account_tax_id.id,
                    })
                    line_ids.append(credit_line)
                    slip_credit += credit_line[2]['credit'] - credit_line[2]['debit']
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
            employee_swift_code = slip.employee_id.bsg_bank_id and slip.employee_id.bsg_bank_id.bsg_bank_name or False
            if employee_swift_code and payment_journal_id.swift_code:
                if employee_swift_code != payment_journal_id.swift_code and payment_journal_id.commission_type and payment_journal_id.commission_value > 0:
                    debit_amount = currency.round(slip_credit - slip_debit)
                    comm_amount = payment_journal_id.commission_type == 'amount' and payment_journal_id.commission_value or \
                        (debit_amount /100) * payment_journal_id.commission_value
                    commission_amount +=comm_amount
                    commission_tax_amount += payment_journal_id.commission_tax_type == 'amount' and payment_journal_id.commission_tax_value or \
                        (comm_amount /100) * payment_journal_id.commission_tax_value
        
        if currency.compare_amounts(credit_sum, debit_sum) == -1:
            acc_id = payment_journal_id.default_account_id.id
            if not acc_id:
                raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (slip.journal_id.name))
            adjust_credit = (0, 0, {
                'name': self.communication,
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': payment_journal_id.id,
                'date': date,
                'debit': 0.0,
                'credit': currency.round(debit_sum - credit_sum),
            })
            line_ids.append(adjust_credit)
        
        elif currency.compare_amounts(debit_sum, credit_sum) == -1:
            acc_id = payment_journal_id.default_account_id.id
            if not acc_id:
                raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (slip.journal_id.name))
            adjust_debit = (0, 0, {
                'name':self.communication ,
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': payment_journal_id.id,
                'date': date,
                'debit': currency.round(credit_sum - debit_sum),
                'credit': 0.0,
            })
            line_ids.append(adjust_debit)
        if commission_amount > 0:
            credit_line = (0, 0, {
                        'name': "عمولة تحويل الرواتب",
                        'partner_id': False,
                        'account_id': payment_journal_id.commission_account_id.id,
                        'journal_id': payment_journal_id.id,
                        'date': date,
                        'debit': commission_amount,
                        'credit': 0.0,
                    })
            line_ids.append(credit_line)
        if commission_tax_amount > 0:
            credit_line = (0, 0, {
                'name': "ضريبة القيمة المضافة على عمولة تحويل الرواتب",
                'partner_id': False,
                'account_id': payment_journal_id.commission_tax_account_id.id,
                'journal_id': payment_journal_id.id,
                'date': date,
                'debit': commission_tax_amount,
                'credit': 0.0,
            })
            line_ids.append(credit_line)
        if commission_amount > 0 or commission_tax_amount > 0:
            acc_id = payment_journal_id.default_account_id.id
            if not acc_id:
                raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (slip.journal_id.name))
            adjust_credit = (0, 0, {
                'name': 'قيمة عمولات تحويل الرواتب بالقيمة المضافة',
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': payment_journal_id.id,
                'date': date,
                'debit': 0.0,
                'credit': currency.round(commission_amount + commission_tax_amount),
            })
            line_ids.append(adjust_credit)
            
        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        move.post()
        #Reconcile the payment, i.e. lookup on the payable account move lines
        account_move_lines_to_reconcile = self.env['account.move.line']
        slip_move_ids = payslip_ids.mapped('move_id')
        slip_move_line_ids = self.env['account.move.line'].search([('move_id', 'in', [mv.id for mv in slip_move_ids])])
        for line in move.line_ids + slip_move_line_ids:
            if line.account_id.internal_type == 'payable':
                account_move_lines_to_reconcile |= line
        account_move_lines_to_reconcile.reconcile()
        for payslip_id in payslip_ids:
            payslip_id.payment_move_id = move.id
            payslip_id.set_to_paid()

        return {'type': 'ir.actions.act_window_close'}

        