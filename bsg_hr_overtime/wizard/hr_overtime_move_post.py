# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
# from werkzeug import url_encode

class HrOvertimeMovePostWizard(models.TransientModel):

    _name = "hr.overtime.move.post.wizard"
    _description = "Overtime Move Post Wizard"


    @api.model
    def _default_amount(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        overtime_ids = self.env['hr.overtime'].browse(active_ids)
        for rec in overtime_ids:
            if rec.move_id:
                raise ValidationError(_('This Record Is Already Posted {}'.format(str(rec.sequence_number))))
            if rec.state != 'fin_approved':
                raise ValidationError(_(' You can only post move for overtimes in Financial Approved , Please Approve {}'.format(str(rec.sequence_number))))
            if not rec.employee_name.partner_id:
                raise ValidationError(_('Please Set Partner For Employee {}'.format(str(rec.employee_name.name))))
        total_net = sum(overtime_ids.mapped('total_overtime_amount'))
        return total_net

    @api.model
    def _default_analytic(self):
        if self.env.user.company_id.overtime_analytic_account_id:
            return self.env.user.company_id.overtime_analytic_account_id
        else:
            context = dict(self._context or {})
            active_ids = context.get('active_ids', [])
            if len(active_ids) == 1:
                overtime_ids = self.env['hr.overtime'].browse(active_ids)
                return overtime_ids.employee_name.contract_id.analytic_account_id
            
                              


    journal_id = fields.Many2one('account.journal', string='Overtime Journal', required=True,default=lambda self: self.env.user.company_id.overtime_journal_id )
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True, required=True)
    debit_account = fields.Many2one('account.account',string='Debit Account',required=True,default=lambda self: self.env.user.company_id.overtime_debit_account_id)
    credit_account = fields.Many2one('account.account', string='Credit Account',required=True,default=lambda self: self.env.user.company_id.overtime_credit_account_id)
    analytic_account = fields.Many2one('account.analytic.account', string='Analytic Account',default= _default_analytic)
    amount = fields.Monetary(string='Amount', required=True, default = _default_amount)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    post_date = fields.Date(string='Post Date', default=fields.Date.context_today, required=True)
    description = fields.Char(string='Description')
    
    # @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if not self.amount > 0.0:
            raise ValidationError(_('The amount must be Strictly positive.'))



    def action_post_overtime(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        overtime_ids = self.env['hr.overtime'].browse(active_ids)
        move_lines = []
        total_balance = 0
        for rec in overtime_ids:
            analytic_account = False
            if self.analytic_account:
                analytic_account = self.analytic_account.id
            elif rec.employee_name.contract_id.analytic_account_id:
                  analytic_account = rec.employee_name.contract_id.analytic_account_id.id  
            move_lines.append({
            'name': self.description,
            'account_id': self.debit_account.id,
            'credit': 0,
            'debit': round(rec.total_overtime_amount, 2),
            'analytic_account_id': analytic_account,
            'partner_id' : rec.employee_name.partner_id.id,
            'bsg_branches_id':rec.branch_name and rec.branch_name.id or rec.employee_name.branch_id.id,
            'department_id': rec.emp_department and rec.emp_department.id or rec.employee_name.department_id.id,
            #'fleet_vehicle_id':
            })
            move_lines.append(
                {
                'name': self.description,
                'account_id': self.credit_account.id,
                'credit': round(rec.total_overtime_amount, 2),
                'debit': 0,
                'partner_id' : rec.employee_name.partner_id.id,
                })
        if len(move_lines):
            move_id = self.env['account.move'].with_context(check_move_validity=False).create({
                'name': '/',
                'ref' : self.description,
                'date' : self.post_date ,
                'journal_id': self.journal_id.id,
                'line_ids': [(0, 0, x) for x in move_lines],
            })
            if move_id:
                move_id.post()
                for rec in overtime_ids:
                    rec.write({'state': 'posted', 'move_id': move_id.id,'journal_id':self.journal_id.id,'posted_date':self.post_date})                

        return {'type': 'ir.actions.act_window_close'}
