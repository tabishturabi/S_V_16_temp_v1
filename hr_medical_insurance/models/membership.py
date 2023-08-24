# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, _


class InsuranceMembership(models.Model):
    """"""
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'insurance.membership'
    _rec_name = 'employee_id'
    _description = "Insurance Membership"

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('approve', 'Approved'), ('expire', 'Expired')],
                             default='draft', string='State')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id, store=True)
    membership_type = fields.Selection([('employee', 'Employee'), ('family_member', 'Family Member')],
                                       string='Membership Type', default='employee')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    agent_employee_id = fields.Many2one('hr.employee', string='Agent')
    family_id = fields.Many2one('hr.iqama.family', string='Agent',copy=False)
    membership_date = fields.Date(string="Joining Date", default=fields.Date.today())
    cost_to_employee = fields.Boolean(string="Cost To The Employee", default=False,copy=False)
    policy_id = fields.Many2one('insurance.policy', string='Policy')
    insurance_company_id = fields.Many2one("res.partner", related="policy_id.insurance_company_id")
    start_date = fields.Date(string="Start Date", related="policy_id.start_date")
    end_date = fields.Date(string="End Date", related="policy_id.end_date")
    allowed_class_id = fields.Many2one("insurance.class", string="Allowed Class")
    allowed_class_amount = fields.Float(string="Allowed Class Amount")
    selected_class_id = fields.Many2one("insurance.class", string="Selected Class")
    selected_class_amount = fields.Float(string="Selected Class Amount")
    amount_difference = fields.Monetary(string='Amount Difference', compute="_get_amount_difference")
    currency_id = fields.Many2one('res.currency', string='Currency', related="policy_id.currency_id")
    loan_count = fields.Integer(string="Loan", default=1)
    loan_id = fields.Many2one('loan.application', string='Insurance Deficits',copy=False)
    need_loan = fields.Boolean(string="Need Loan", default=False,copy=False)
    service_expired = fields.Boolean(string="Service Expired", default=False)

    @api.onchange("employee_id")
    def _onchange_employee(self):
        self.family_id = False
        self.agent_employee_id = self.employee_id.id

    @api.onchange('policy_id', 'state')
    def _get_confirmed_policy(self):
        for rec in self:
            policies = self.env['insurance.policy'].search([('state', '=', 'bill')]).mapped('id')
            return {'domain': {'policy_id': [('id', 'in', policies)]}}

    @api.onchange('policy_id', 'state')
    def _get_allowed_class(self):
        for rec in self:
            class_ids = rec.policy_id.policy_class_ids.mapped('class_id.id')
            return {'domain': {'allowed_class_id': [('id', 'in', class_ids)]},
                    'value': {'allowed_class_id': class_ids[0] if len(class_ids) > 0 else None}}

    @api.onchange('policy_id', 'state')
    def _get_selected_class(self):
        for rec in self:
            class_ids = rec.policy_id.policy_class_ids.mapped('class_id.id')
            return {'domain': {'selected_class_id': [('id', 'in', class_ids)]},
                    'value': {'selected_class_id': class_ids[0] if len(class_ids) > 0 else None}}

    def _get_amount_difference(self):
        for rec in self:
            rec.amount_difference = rec.selected_class_amount - rec.allowed_class_amount
            rec._check_need_loan()

    def action_confirm(self):
        self.state = 'confirm'
        self._check_need_loan()

    def action_approve(self):
        self.state = 'approve'
        self._check_need_loan()

    @api.onchange('cost_to_employee')
    def _check_need_loan(self):
        # Function to check if membership should pay loan

        for rec in self:
            rec.need_loan = False
            if rec.state == 'approve':
                if rec.cost_to_employee or rec.amount_difference > 0.0:
                    rec.need_loan = True

    def action_create_loan(self):
        loan_obj = self.env['loan.application']
        payment_obj = self.env['account.payment']
        loan_amount = 0.0
        if self.cost_to_employee:
            loan_amount = self.selected_class_amount
        elif self.amount_difference > 0.0:
            loan_amount = self.amount_difference

        if loan_amount > 0:
            loan_id = loan_obj.create({
                "employee_id": self.employee_id.id or self.family_id.employee_id.id,
                "loan_policy": self.employee_id.loan_policy.id or self.env['loan.policies'].search([], limit=1).id,
                "loan_type_id": self.env['loan.type'].search([], limit=1).id,
                "application_date": datetime.today(),
                "approve_date": datetime.today(),
                "requested_loan_amt": loan_amount,
                "approved_loan_amt": loan_amount,
                "loan_compute_type": "fixed",
                "no_of_installment": 1,
                "loan_purpose": _("{} - Insurance Difference Amount".format(self.employee_id.name)),
                "company_id": self.company_id.id,
                "currency_id": self.currency_id.id,
                "state": "paid",
            })
            if loan_id:
                self.loan_id = loan_id.id
                loan_id.compute_payments_by_installment()
                self.need_loan = False

                payment_method = self.env.ref('account.account_payment_method_manual_out')

                payment_id = payment_obj.create({
                    "payment_method_id": payment_method.id,
                    'payment_type': 'outbound',
                    "partner_id": self.employee_id.partner_id.id,
                    "amount": loan_amount,
                    "currency_id": self.currency_id.id,
                    "journal_id": loan_id.account_journal_id.id,
                    "account_id": loan_id.emp_loan_acc_id.id,
                    "payment_date": fields.Date.today(),
                    "communication": _("{} - Insurance Difference Amount".format(self.employee_id.name)),
                })
                if payment_id:
                    loan_id.payment_id = payment_id.id
                    payment_obj.post_state()

    def action_draft(self):
        self._check_need_loan()
        self.need_loan = False
        self.state = 'draft'


    def action_view_loan(self):
        loan_obj = self.env.ref('loan.loan_application_form')
        return {'name': _("{} Membership Difference").format(self.employee_id.name or self.family_id.employee_id.name),
                'view_mode': 'form',
                'res_model': 'loan.application',
                'view_id': loan_obj.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': self.loan_id.id,
                'context': {}}
