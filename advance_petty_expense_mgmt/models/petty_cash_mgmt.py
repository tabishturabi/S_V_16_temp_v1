# -*- coding: utf-8 -*- 
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class AccountPayment(models.Model):
    _inherit =  "account.payment"

    petty_cash_id = fields.Many2one('petty.cash.expense.accounting',string="Petty cash ID") 
    debit_account_id = fields.Many2one('account.account',string="Debit Account")

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    analytical_ids = fields.Many2many('account.analytic.account',string="Related BU/ Dept.")
    is_payment_journal = fields.Boolean('Pettycash Payment Journal')
 
#for managing PettyCash & Expenses
class PettyCashExpense(models.Model):
    _name = "petty.cash.expense.accounting"
    _description = "Petty Cash Expenses Accouting"
    _inherit = ['mail.thread','mail.activity.mixin']

    # #for getting default jounral from petty_cash_user_rules
    # @api.model
    # def default_get(self, fields):
    #     result = super(PettyCashExpense, self).default_get(fields)
    #     search_cash_user_rule_id = self.env['petty_cash_user_rules'].search([('user_id','=',self.env.user.id)],limit=1)
    #     if search_cash_user_rule_id:
    #         result['petty_cash_user_rules_id'] = search_cash_user_rule_id.id
    #     return result

    # #getting default balance
    # @api.model
    # def _default_balance(self):
    #     return self.journal.default_debit_account_id.balance

    #getting default currency
    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    #getting default department id
    @api.model
    def _default_department_id(self):
        search_employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)],limit=1)
        return search_employee_id.department_id


    def unlink(self):
        for data in self:
            if data.state != 'draft':
                raise UserError(_('You can only delete a record if its in draft state..!'))
        return super(PettyCashExpense, self).unlink()

    # employee_id = fields.Many2one('hr.employee', string="Employee")
    user_id = fields.Many2one('res.users',string="Requested User", default=lambda self: self.env.user)
    date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    journal = fields.Many2one('account.journal')
    payment_jounal_id = fields.Many2one('account.journal',string="Payment Journal")
    name = fields.Char(string="Sequence", required=False,default='/')
    department_id = fields.Many2one('hr.department',string="Department Id",default=_default_department_id)
    analytical_id = fields.Many2one('account.analytic.account',string="Analytic Accounts")
    # petty_cash_line_ids = fields.One2many('petty.cash.expense.accounting.tree', 'petty_cash_id')
    total_request = fields.Float(string="Total Requested",  required=False,  compute='_compute_amount')   
    total = fields.Float(string="Total",  required=False,  compute='_compute_amount')
    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('to_submit', 'Submitted'),
    ('approved', 'Approved By Finance Manager'),('declined', 'Declined'),('done', 'Done') ], default='draft',track_visibility='always')
    tax_amount = fields.Float(string="Total Vat",compute='_compute_amount')
    # total_without_vat = fields.Float(string="Total Without Vat",compute='_compute_amount')
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_default_currency, track_visibility='always')
    payment_id = fields.Many2one('account.payment')
    descripiton = fields.Text(string="Description")
    amount_request = fields.Float(string="Amount Requested")
    amount_approval = fields.Float(string="Amount Approved")
    amount_approved = fields.Float(string="Approved By", compute='_compute_amount')
    ir_attachment_ids = fields.Many2many('ir.attachment',string='Attachments')
    net_balacne = fields.Float(string="Net Balance")    #, default=_default_balance
    petty_cash_user_rule_id = fields.Many2one('petty_cash_user_rules',string="Petty Cash User Rule")
    petty_cash_journal_id = fields.Many2one(related="petty_cash_user_rule_id.journal_id")
    account_id = fields.Many2one('account.account', string="Account")
    reject_reason = fields.Text(string="Reject Reason")
    is_reject = fields.Boolean(string="IS Reject")
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Documents")

    def _compute_attached_docs_count(self):
        for petty in self:
            petty.doc_count = self.env['ir.attachment'].search_count([
            '&',
            ('res_model', '=', 'petty.cash.expense.accounting'),
            ('res_id', '=', petty.id)
        ])



    # override write method

    def write(self, values):
        res = super(PettyCashExpense, self).write(values)
        for rec in self:
            if rec.ir_attachment_ids:
                rec.ir_attachment_ids.write({'res_id':rec.id})
        return res



    def attachment_tree_view(self):
        res = self.env['ir.actions.act_window']._for_xml_id('advance_petty_expense_mgmt.action_attachment_petty_cash_expense_accounting')
        return res 

    #make attchment mendetory
    @api.constrains('ir_attachment_ids')
    def _check_attachment_id(self):
        for rec in self:
            if not rec.ir_attachment_ids:
                warning_obj=self.env['bsg.warning.error'].get_warning('0010')
                raise UserError(warning_obj)

    #for onchange to pass user journal to petty cash journal and getting journal balance as well
    @api.onchange('petty_cash_user_rule_id')
    def onchange_petty_cash_user_rule_id(self):
        # if not self.petty_cash_user_rule_id.journal_id.default_account_id and not self.petty_cash_user_rule_id.journal_id.default_account_id and self.petty_cash_user_rule_id.account_id:
        if not self.petty_cash_user_rule_id.journal_id.default_account_id and self.petty_cash_user_rule_id.account_id:
            self.account_id = self.petty_cash_user_rule_id.account_id.id
        if self.petty_cash_user_rule_id:
            self.journal = self.petty_cash_user_rule_id.journal_id.id
            # if self.petty_cash_user_rule_id.journal_id.default_account_id:
            if self.petty_cash_user_rule_id.journal_id.default_account_id:
                # self.opening_balacne = self.journal.default_debit_account_id.balance
                # self.account_id = self.petty_cash_user_rule_id.journal_id.default_account_id.id
                self.account_id = self.petty_cash_user_rule_id.journal_id.default_account_id.id

    #getting default balance from account if not select any journal
    @api.onchange('account_id')
    def _onchange_account_id(self):
        if self.account_id:
            balance = 0.0   
            if self.petty_cash_user_rule_id.account_id:     
                for aml in self.env['account.move.line'].search([('account_id','=',self.account_id.id),('move_id.state','=','posted'),('partner_id','=',self.petty_cash_user_rule_id.partner_id.id)]):
                    balance += aml.debit - aml.credit
            else:
                for aml in self.env['account.move.line'].search([('account_id','=',self.account_id.id),('move_id.state','=','posted')]):                
                    balance += aml.debit - aml.credit
            self.net_balacne = balance

    #for constrint for not allow 0 value on requested amount
    
    @api.constrains('amount_request')
    def _check_amount_request(self):
        if self.amount_request == 0:
            raise UserError(_('Amount Should not be 0 ...!'))

    #onchange for valiation amount use
    @api.onchange('amount_approval')
    def onchange_amount_approval(self):
        if self.amount_approval:
            if self.amount_approval > self.amount_request:
                raise UserError(_("Amount Should be less than Requested Amount"))
    
    #cahnge state to submit

    def to_submit(self):
        for rec in self:
            code = 'PCR' + self.env.user.user_branch_id.branch_no
            seq = self.env['ir.sequence'].next_by_code(code)
            if not bool(seq):
                _ = self.sudo().env['ir.sequence'].create({
                    'name': code,
                    'code': code,
                    'prefix': 'PCR' + self.env.user.user_branch_id.branch_no +  '%(y)s' + '%(month)s',
                    'padding': 4,
                })
                rec.name = self.env['ir.sequence'].next_by_code(code)
            else:
                rec.name = seq
            rec.state = 'to_submit'

    #cahnge state to declined

    def declined(self):
        data = {'default_id' : self.id, 'default_petty_cash_id' : self.id}
        return {
        'type': 'ir.actions.act_window',
        'res_model': 'declined_petty_cash_request',
        'view_id'   :  self.env.ref('advance_petty_expense_mgmt.declined_petty_cash_request_form').id,
        'view_mode': 'form',
        'view_type': 'form',
        'context' : data,
        'target': 'new',
        }
        # self.state = 'declined'
    
    #cahnge state to declined

    def action_by_manager(self):
        if self.amount_approval == 0.0:
            raise UserError(_("Please Enter some amount..."))
        else:
            self.state = 'approved'
    
    #for see the payment voucher

    def action_view_payment(self):
        return {
        'name': _('Payment Voucher'),
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'account.payment',
        'view_id': False,
        'type': 'ir.actions.act_window',
        'domain': [('id', '=', self.payment_id.id)],
        }

    #for see the journal entry

    def button_journal_entries(self):
        return {
        'name': _('Journal Entries'),
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'account.move.line',
        'view_id': False,
        'type': 'ir.actions.act_window',
        'domain': [('id', 'in', self.payment_id.move_line_ids.ids)],
        }

    #change state to declined

    def to_declined(self):
        self.state = 'declined'

    #confirming the petty cash

    def confirm_petty_cash(self):
        if self.total <= 0:
            raise UserError(_("Be Sure you have more than 0 amount ...!"))
        if not self.payment_jounal_id:
            raise UserError(_("Be Sure you have Payment Journal...!"))
        payment_method = self.env.ref('account.account_payment_method_manual_in')
        if not self.journal.default_account_id and not self.journal.default_account_id:
            payment_id = self.env['account.payment'].create({
             'name' : '/',
             'payment_type' : 'outbound','partner_type' : 'supplier',
             'partner_id' : self.petty_cash_user_rule_id.partner_id.id if self.petty_cash_user_rule_id.partner_id  else self.user_id.partner_id.id,'amount' : self.total,
             'petty_cash_id' : self.id,
             'ref' : self.descripiton,
             'journal_id' : self.payment_jounal_id.id,'date' : str(datetime.now()),
             'payment_method_id' : payment_method.id})
            payment_line_ids = self.env['account.voucher.line.custom'].create({'payment_id' : payment_id.id,
                                                                                'account_id' : self.petty_cash_user_rule_id.account_id.id})
            
            self.write({'payment_id' : payment_id.id,'state':'done'})
            #payment_id.with_context(from_petty=True).post()
        else:
            payment_id = self.env['account.payment'].create({'name' : '/',
             'is_internal_transfer' : True,
             'amount' : self.total,
             'payment_type' : 'outbound',
             'petty_cash_id' : self.id,
             'ref' : self.descripiton,
             'journal_id' : self.payment_jounal_id.id,
             'destination_journal_id' : self.journal.id,
             'date' : str(datetime.now()),
             'payment_method_id' : payment_method.id})
            self.write({'payment_id' : payment_id.id,'state':'done'})
            #payment_id.with_context(from_petty=True).post()
        payment_id.with_context(from_petty=True).post_state()
        # self.action_send_mail()

    #computing total 
    
    @api.depends('amount_request','amount_approval')
    def _compute_amount(self):
        self.total_request = self.amount_request
        self.total = self.amount_approval
        self.amount_approved = self.amount_approval

    #oveeride create method
    @api.model
    def create(self, vals):
        res = super(PettyCashExpense, self).create(vals)
        res.name = '*' + str(res.id)
        if res.ir_attachment_ids:
            res.ir_attachment_ids.write({'res_id':res.id})    
        return res

    #send mail 

    def action_send_mail(self):
        MailTemplate = self.env.ref('advance_petty_expense_mgmt.mail_petty_cash_expense_tmpl', False)
        for rec in self.user_id:
            if rec.partner_id.email:
                MailTemplate.write({'email_to': str(rec.partner_id.email),'email_from': str(self.env.user.email)})
                MailTemplate.send_mail(self.id, force_send=True)
        return True
