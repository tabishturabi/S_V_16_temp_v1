# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
from dateutil import relativedelta
import math


class loan_payment(models.Model):
    _name = 'loan.payment'
    _description = 'Loan Payment'

    
    def paid_button(self):
        if self.loan_app_id.state != 'paid':
            raise ValidationError(_('Loan application is not approved.'))
        if self.state == 'draft':
            if not self.due_date:
                raise ValidationError(_('Please select the due date.'))
            payment_rec = self.search([('loan_app_id', '=', self.loan_app_id.id), ('state', '=', 'paid')])
            if len(payment_rec) + 1 == self.loan_app_id.no_of_installment:
                self.loan_app_id.write({'state': 'close'})
            self.write({'state': 'paid'})

    rate= fields.Float("Rate")
    due_date = fields.Date(string="Due Date")
    original_due_date = fields.Date(string="Original Due Date")
    principal = fields.Float("Principal")
    balance_amt = fields.Float("Balance")
    interest = fields.Float("Interest")
    total = fields.Float("Total",compute='_compute_total',store=True)
    extra = fields.Float("Pre-Payment")
    loan_app_id = fields.Many2one('loan.application', string="Loan Application")
    move_id = fields.Many2one('account.move', string="Account Move")
    employee_id = fields.Many2one('hr.employee', related='loan_app_id.employee_id', readonly=True, store=True)
    state = fields.Selection([
                              ('draft', 'Draft'),('delay','Delay'),
                              ('paid','Paid')], string="State", default='draft')
    payslip_id = fields.Many2one('hr.payslip', string="Payslip")

    @api.depends('principal','extra')
    def _compute_total(self):
        for rec in self:
            rec.total = abs(rec.principal-rec.extra) 

    
    
    def action_new_arah(self):
        for arch in self:
            loan_archive = self.search([('loan_app_id','=',arch.loan_app_id.id)],order='due_date desc', limit=1)
            date_start = loan_archive.due_date
            date_start = date_start + relativedelta.relativedelta(months=+1)
            self.create({
                        'loan_app_id':arch.loan_app_id.id,
                        'due_date': date_start,
                        'principal': arch.principal,
                        'interest': 0,
                        'interest_rate': 0,
                        'total': arch.total,
                        'balance_amt': arch.balance_amt,
                        })
        return True

    
    def action_delay(self):
        self.action_new_arah()
        self.write({'state': 'delay'})




class LoanDelay(models.Model):
    _name = "hr.loan.delay"
    _inherit = ['mail.thread']
    _description = "Delay Loans"

    name =  fields.Char("Name", readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,domain=[('loan_ids.state','=','paid')])
    loan_app_id = fields.Many2one('loan.application', string="Loan Application",required=True,readonly=True,
        states={'draft': [('readonly', False)]})
    start_date = fields.Date("Delay Start Date", required=True,readonly=True,
        states={'draft': [('readonly', False)]})
    end_date = fields.Date("Delay End Date", required=True,readonly=True,
        states={'draft': [('readonly', False)]})
    payment_ids = fields.Many2many('loan.payment', string='Installments',readonly=True,
        states={'draft': [('readonly', False)]},) 

    note = fields.Text("Notes",readonly=True,
        states={'draft': [('readonly', False)]},)
    state = fields.Selection([
        ('draft','Draft'),
        ('requested','Requested'),
        ('approved','Approved'),
        ('rejected','Rejected')
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')


    @api.model
    def create(self, vals):
        if not vals.get('name', False):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.loan.delay') or '/'
        return super(LoanDelay, self).create(vals)


    @api.onchange('start_date','end_date')
    def _onchange_dates(self):
        for rec in self:
            lines =[]
            for line in rec.payment_ids:
                if line.due_date >= rec.start_date and line.due_date <= rec.end_date:
                    lines.append(line.id)
            rec.payment_ids = [(6, 0,[x for x in lines])]

    
    def action_reject(self):
        self.write({'state':'rejected'})
    
    
    def action_draft(self):
        self.write({'state':'draft'})
        
    
    def action_approve(self):
        self.payment_ids.action_delay()
        self.write({'state': 'approved'})
        
        
    def action_request(self):
        if  not self.payment_ids:
            raise UserError(_('Please specify installment'))
        return self.write({'state':'requested'})        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: