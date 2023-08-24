from datetime import datetime, date, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ExitAndReturn(models.Model):
    _name = 'hr.exit.return'
    _description = "Exit And Return"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    @api.model
    def default_get(self, fields_list):
        defaults = super(ExitAndReturn, self).default_get(fields_list)
        defaults['note'] = 'عبارة عن قيمة الخروج والعودة لـ'
        defaults['employee_id'] = self.env['hr.employee'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).search(
            [('user_id', '=', self.env.user.id)], limit=1).id
        hr_exit_account_data = self.env.ref('employee_human_resource.hr_exit_account_data')
        if not hr_exit_account_data.account_id or not hr_exit_account_data.journal_id:
            raise ValidationError(_("Please Set Account/Journal in Configuration First"))
        exit_account_id_debit = hr_exit_account_data.account_id or False
        exit_journal_id = hr_exit_account_data.journal_id or False
        defaults['account_debit_id'] = exit_account_id_debit.id
        defaults['account_journal_id'] = exit_journal_id.id
        return defaults

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Exit and Return")
    name = fields.Char(string='Name')
    activity_summary = fields.Char(string='Next Activity Summary')
    border_no = fields.Char(string='Work Permit No')
    display_name = fields.Char(string='Display Name')
    entry_visa_no = fields.Char(string='Visa No')
    visa_no = fields.Char(string='Visa No')

    from_hr = fields.Boolean('From Hr')
    on_employee_fair = fields.Boolean('On Employee Fair')
    without_leave = fields.Boolean('Without Leave')
    have_ticket = fields.Boolean('Have Ticket',compute="compute_have_booleans")
    have_clearance = fields.Boolean('Have Clearance',compute="compute_have_booleans")

    arrival_before_date = fields.Date(string='Arrival Before Date', track_visibility=True)
    first_date = fields.Date(string='First Date', track_visibility=True)
    travel_before_date = fields.Date(string='Travel Before Date', track_visibility=True)

    cost = fields.Float(string="Company Cost")
    visa_duration = fields.Float(string="Visa Duration")
    bsg_empiqama = fields.Many2one('hr.iqama', string="Iqama Number", track_visibility='always',related="employee_id.bsg_empiqama")
    bsg_issuedate_iqama = fields.Date("Iqama Issue date", track_visibility='always',related="employee_id.bsg_empiqama.bsg_issuedate")
    bsg_expirydate_iqama = fields.Date("Iqama Expiry date", track_visibility='always',related="employee_id.bsg_empiqama.bsg_expirydate")

    bsg_passport = fields.Many2one('hr.passport', string="Passport", track_visibility='always',related="employee_id.bsg_passport")
    bsg_issuedate_passport = fields.Date("Passport Issue date", track_visibility='always',related="employee_id.bsg_passport.bsg_issuedate")
    bsg_expirydate_passport = fields.Date("Passport Expiry date", track_visibility='always',related="employee_id.bsg_passport.bsg_expirydate")

    account_debit_id = fields.Many2one('account.account', string="Account Debit", track_visibility=True)
    account_journal_id = fields.Many2one('account.journal', string="Account Journal", track_visibility=True)
    account_move_id = fields.Many2one('account.move', string="Account Move", track_visibility=True)
    department_id = fields.Many2one('hr.department', string="Department", track_visibility=True,
                                    related='employee_id.department_id', readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", track_visibility=True,
                                  domain=[('employee_type', '=', 'foreign')])
    contract_id = fields.Many2one('hr.contract', string="Current Contract", track_visibility=True,
                                  related='employee_id.contract_id', readonly=True)
    job_id = fields.Many2one('hr.job', string="Job Position", track_visibility=True, related='employee_id.job_id',
                             readonly=True)
    leave_request_id = fields.Many2one('hr.leave', string="Leave Request", track_visibility=True,readonly=True)
    nationality_id = fields.Many2one('hr.nationality', string="Nationality (Country)", track_visibility=True,
                                     related='employee_id.bsg_national_id', readonly=True)

    contract_duration = fields.Selection([('12', '12 Month'), ('24', '24 Month')], string="Contract Duration",
                                         track_visibility=True)
    exit_return_type = fields.Selection([('one', 'One Travel'), ('multi', 'Multi Travel'), ('final', 'Final Exit')],
                                        string="Exit Return Type", track_visibility=True)
    request_for = fields.Selection(
        [('employee', 'For Employee Only'), ('family', 'For Family Only'), ('all', 'For Employee and Family')],
        string="Request For", track_visibility=True)
    state = fields.Selection([('draft', 'Draft'), ('waiting_finance', 'Waiting Finance'), ('done', 'Done')],
                             string="State", default='draft', track_visibility=True)
    note = fields.Text(string="Note", track_visibility=True)
    vacation_start_date = fields.Datetime(string="Vacation Start Date", related='leave_request_id.date_from',
                                          readonly=True)
    vacation_end_date = fields.Datetime(string="Vacation End Date", related='leave_request_id.date_to', readonly=True)
    vacation_duration = fields.Float(string="Vacation Duration", related='leave_request_id.number_of_days',
                                     readonly=True)
    last_ex_return_date = fields.Date(string="Effective Date",related="employee_id.last_return_date")
    hr_termination_id = fields.Many2one('hr.termination')
    deputation_id = fields.Many2one('hr.deputations')
    employee_cost = fields.Float("Employee Cost")
    total_cost = fields.Float("Total Cost",compute="compute_total_cost")
    loan_id = fields.Many2one('loan.application', string='Loan',copy=False)
    loan_count = fields.Integer(string="Loan", default=1)

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

    def action_create_loan(self):
        loan_obj = self.env['loan.application']
        payment_obj = self.env['account.payment']
        if self.employee_cost > 0:
            loan_id = loan_obj.create({
                "employee_id": self.employee_id.id or self.family_id.employee_id.id,
                "loan_policy": self.employee_id.loan_policy.id or self.env['loan.policies'].search([], limit=1).id,
                "loan_type_id": self.env['loan.type'].search([], limit=1).id,
                "application_date": datetime.today(),
                "approve_date": datetime.today(),
                "requested_loan_amt": self.employee_cost,
                "approved_loan_amt": self.employee_cost,
                "loan_compute_type": "fixed",
                "no_of_installment": 1,
                "loan_purpose": _("{} - Exit and return cost".format(self.employee_id.name)),
                "company_id": self.company_id.id,
                "state": "paid",
            })
            if loan_id:
                self.loan_id = loan_id.id
                loan_id.compute_payments_by_installment()
                payment_method = self.env.ref('account.account_payment_method_manual_out')
                payment_id = payment_obj.create({
                    "payment_method_id": payment_method.id,
                    'payment_type': 'outbound',
                    "partner_id": self.employee_id.partner_id.id,
                    "amount": self.employee_cost,
                    "journal_id": loan_id.account_journal_id.id,
                    "account_id": loan_id.emp_loan_acc_id.id,
                    "date": fields.Date.today(),
                    "communication": _("{} - Exit and return cost".format(self.employee_id.name)),
                })
                if payment_id:
                    loan_id.payment_id = payment_id.id
                    payment_obj.post_state()



    @api.depends('hr_termination_id', 'leave_request_id')
    def compute_have_booleans(self):
        for rec in self:
            rec.have_ticket = False
            rec.have_clearance = False
            if rec.leave_request_id:
                if rec.leave_request_id.is_has_ticket:
                    rec.have_ticket = True
                if rec.leave_request_id.hr_clearance_id.state == 'done':
                    rec.have_clearance = True
            elif rec.hr_termination_id:
                rec.have_ticket = True
                if rec.hr_termination_id.hr_clearance_count > 0:
                    if self.env['hr.clearance'].search([('termination_id','=',rec.hr_termination_id.id)],limit=1).state == 'done':
                        rec.have_clearance = True

    @api.depends('employee_cost', 'cost')
    def compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.cost + rec.employee_cost

    @api.onchange('exit_return_type')
    def onchnage_exit_return_type(self):
        if self.exit_return_type:
            if self.exit_return_type == 'final':
                self.note = 'عبارة عن قيمة الخروج النهائي لـ'
            else:
                self.note = 'عبارة عن قيمة الخروج والعودة لـ'

    
    def action_confirm(self):
        self.write({'state': 'waiting_finance'})

    
    def action_approve(self):
        for rec in self:
            if not self.account_journal_id or not self.account_debit_id or self.cost <= 0:
                raise ValidationError(
                    _("Please Set Account/Journal in Configuration First also cost must be greater than zero"))

            hr_exit_account_data = self.env.ref('employee_human_resource.hr_exit_account_data')

            exit_account_id_debit = hr_exit_account_data.account_id or False
            exit_journal_id = hr_exit_account_data.journal_id or False
            amount = rec.cost
            move_id = self.env['account.move'].with_context(check_move_validity=False).create({
                'ref': rec.employee_id.name + self.note,
                'date': datetime.today(),
                'journal_id': exit_journal_id.id,
                'state': 'draft',
                'line_ids': [(0, 6, {'name': rec.employee_id.name + _('/Exit re-entry'),
                                     'due_date': datetime.today(),
                                     'bsg_branches_id': self.employee_id.branch_id.id,
                                     'department_id': self.employee_id.department_id.id,
                                     'account_id': exit_journal_id.default_account_id.id,
                                     'debit': 0.0,
                                     'credit': amount,
                                     }),
                             (0, 6, {'name': rec.employee_id.name + _('/Exit re-entry'),
                                     'due_date': datetime.today(),
                                     'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id,
                                     'bsg_branches_id': self.employee_id.branch_id.id,
                                     'department_id': self.employee_id.department_id.id,
                                     'account_id': exit_account_id_debit.id,
                                     'debit': amount,
                                     'credit': 0.0,
                                     })]})
            # rec.employee_id.write({'ex_return_date':rec.to_date})
            rec.write({'account_move_id': move_id.id})
            move_id.action_post()
            rec.state = 'done'
            rec.action_create_loan()

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.exit.return.seq') or _('New')
        return super(ExitAndReturn, self).create(vals)

    @api.constrains('total_cost')
    def _total_cost_constrains(self):
        for data in self:
            if data.total_cost <= 0:
                raise UserError(_("Total Cost Should be greater Than 0"))