from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import uuid
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class EffectRequest(models.Model):
    _name = 'effect.request'
    _inherit = ['mail.thread']
    _description = "Effective date Notes"
    _rec_name = "name"

    name = fields.Char(string='Reference No', readonly=False)
    entry_date = fields.Datetime(string='Entry Date', default=lambda self: fields.datetime.now(), track_visibility=True,
                                 readonly=True)

    @api.model
    def _default_my_employee_id(self):
        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        return self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])

    from_hr = fields.Boolean(string='Another Employee', track_visibility=True, copy=False)
    employee_id = fields.Many2one('hr.employee', default=_default_my_employee_id, required=True, track_visibility=True,
                                  readonly=False)
    manager_id = fields.Many2one('hr.employee', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Effective Date")
    mobile_phone = fields.Char(string='Mobile Number',readonly=True, required=False, track_visibility=True)

    employee_code = fields.Char(string='Employee ID', readonly=True)
    bsg_empiqama = fields.Many2one('hr.iqama', string='Employee Iqama ID', readonly=True)
    bsg_national_id = fields.Many2one('hr.nationality', string='Employee National ID', readonly=True)

    working_date = fields.Date(string='Starting Working Date', default=fields.date.today(), track_visibility=True,
                               readonly=False, required=True)
    description = fields.Text(string="Description", track_visibility=True, translate=True)
    validate_date = fields.Datetime(string='Validate Date', track_visibility=True, readonly=True)
    branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Branch Name', readonly=True)
    department_id = fields.Many2one('hr.department', string="Department", readonly=True)
    job_id = fields.Many2one('hr.job', string="Job Position", readonly=True)
    state = fields.Selection(string="State",
                             selection=[('1', 'Draft'),
                                        ('2', 'Waiting Deputy Executive Director'),
                                        ('3', 'Branch Supervisor'),
                                        ('4', 'Direct Manager'),
                                        ('5', 'HR Salary Accountant'),
                                        ('6', 'HR Manager'),
                                        ('7', 'Finance Manager'),
                                        ('8', 'Done'),
                                        ('9', 'Cancelled'),
                                        ('11', 'Accountant'),
                                        ],
                             default='1',
                             track_visibility=True)
    loan_id = fields.Many2one('loan.application', string='Insurance Deficits')
    on_paid_leave = fields.Boolean(string="On Paid Leave",compute="compute_on_paid_leave")
    mark_done_check = fields.Boolean(string="On Paid Leave")
    refusal_reason = fields.Text(string="Refusal Reason",track_visibility=True)



    @api.constrains('return_date')
    def validate_return_date(self):
        if self.return_date and self.date_from:
            if self.return_date <= self.date_from:
                raise ValidationError('Return date must be greater than from date')




    @api.depends('return_date','date_to','notice_type','sick_leave_type')
    def compute_on_paid_leave(self):
        for rec in self:
            rec.on_paid_leave = False
            if rec.notice_type == 'start_after_vacation' and rec.sick_leave_type.leave_type == 'paid':
                if rec.return_date and rec.date_to:
                    if rec.return_date < rec.date_to:
                        rec.on_paid_leave = True

    
    def action_reset_to_draft(self):
        self.state = '1'

    
    def action_cancel(self):
        self.state = '9'

    
    def action_send_deputy_executive_director(self):
        if self.decision_date and self.working_date:
            if self.decision_date > self.working_date:
                raise ValidationError('Working date must be equal or greater than decision date')
        if self.notice_type == 'start_after_vacation' and self.employee_id.state != 'on_leave' and not self.by_hr:
            raise ValidationError('Employee status must be on leave')
        if self.notice_type == 'start_after_vacation' and self.sick_leave_type.leave_type == 'paid':
            self.state = '2'
        elif self.notice_type == 'start_after_vacation' and self.sick_leave_type.leave_type == 'unpaid':
            self.state = '2'
        elif self.notice_type in ('start_first_time', 'start_after_transport'):
            self.state = '2'
        else:
            self.state = '2'

    
    def action_submit_branch_supervisor(self):
        if self.decision_number.decision_type == 'transfer_employee':
            clearance_ids = self.env['hr.clearance'].search(
                [('decision_number', '=', self.decision_number.id), ('state', '!=', 'done')], limit=1)
            if clearance_ids:
                raise ValidationError("Request can't be submitted unless clearance is in done state.")
        if self.decision_date and self.working_date:
            if self.decision_date > self.working_date:
                raise ValidationError('Working date must be equal or greater than decision date')
        if self.notice_type == 'start_after_vacation' and self.employee_id.state != 'on_leave' and not self.by_hr:
            raise ValidationError('Employee status must be on leave')
        if self.notice_type == 'start_after_vacation' and self.sick_leave_type.leave_type == 'paid':
            self.state = '3'
        elif self.notice_type == 'start_after_vacation' and self.sick_leave_type.leave_type == 'unpaid':
            self.state = '3'
        elif self.notice_type in ('start_first_time', 'start_after_transport'):
            self.state = '3'
        else:
            self.state = '3'

    
    def action_submit_direct_manager(self):
        self.state = '4'

    
    def action_submit_dept_supervisor(self):
        if self.notice_type == 'start_after_vacation' and self.sick_leave_type.leave_type == 'paid':
            self.state = '4'
        elif self.notice_type == 'start_after_vacation' and self.sick_leave_type.leave_type == 'unpaid':
            self.state = '4'
        else:
            self.state = '4'

    
    def action_submit_hr_salary_accountant(self):
        if self.notice_type == 'start_after_vacation' and self.sick_leave_type.leave_type == 'paid':
            if self.return_date and self.date_to:
                date_diff = abs((self.return_date - self.date_to).days)
                self.check_days_delayed_by_type = False
                self.is_foreign = False
                if date_diff > 20:
                    self.check_days_delayed_by_type = True
                    contract_id = self.env['hr.contract'].search(
                        [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
                    amount = 0
                    if contract_id.line_ids:
                        rule_codes = contract_id.line_ids.mapped('code')
                        rule_id = self.env['hr.salary.rule'].search(
                            [('code', 'in', rule_codes), ('is_housing', '=', True)], limit=1)
                        if rule_id:
                            housing_rule_id = contract_id.line_ids.filtered(lambda l: l.code and l.code == rule_id.code)
                            amount = housing_rule_id.total
                    _logger.info('...employee_type ' + str(self.employee_id.employee_type))
                    if self.employee_id.employee_type == 'foreign':
                        self.is_foreign = True
                        self.iqama_license_cost = (self.employee_id.bsg_empiqama.yearly_iqama_cost / 360) * (
                                    date_diff - 20)
                        self.social_insurance_cost = (((contract_id.wage + amount) * .02) / 30) * (date_diff - 20)
                        self.total_cost = (self.social_insurance_cost + self.iqama_license_cost)
                        _logger.info('...foreign Processing draft records on date ' + str(self.iqama_license_cost))
                        _logger.info('...foreign Processing draft records on date ' + str(self.total_cost))
                    elif self.employee_id.employee_type == 'citizen':
                        self.is_foreign = False
                        self.gosi_cost = (contract_id.wage * 9.75) * (date_diff - 20)
                        self.social_insurance_cost = (((contract_id.wage + amount) * .02) / 30) * (date_diff - 20)
                        self.total_cost = (self.social_insurance_cost + self.gosi_cost)
                        _logger.info('...citizen gosi_cost ' + str(self.gosi_cost))
                        _logger.info('...citizen total_cost ' + str(self.total_cost))
            self.state = '5'
        elif self.notice_type == 'start_after_vacation' and self.sick_leave_type.leave_type == 'unpaid':
            self.state = '5'
        else:
            self.state = '5'

    
    def action_submit_hr_manager(self):
        self.mark_done_check = False
        if self.notice_type == 'start_after_vacation' and self.sick_leave_type.leave_type == 'paid':
            if self.return_date and self.date_to:
                date_diff = abs((self.return_date - self.date_to).days)
                if date_diff > 20:
                    self.mark_done_check = True
            self.state = '6'
        elif self.notice_type == 'start_after_vacation' and self.sick_leave_type.leave_type == 'unpaid':
            self.state = '6'
        else:
            self.state = '6'


    
    def action_submit_finance_manager(self):
        if self.notice_type == 'start_after_vacation' and self.sick_leave_type.leave_type == 'paid':
            if self.return_date and self.date_to:
                date_diff = abs((self.return_date - self.date_to).days)
                if date_diff > 20:
                    self.state = '7'
        elif self.notice_type == 'start_after_vacation' and self.sick_leave_type.leave_type == 'unpaid':
            self.employee_id.write(
                {'last_return_date': self.return_date, 'employee_state': 'on_job', 'state': 'on_job'})
            self.state = '8'
        else:
            self.state = '8'

    def action_submit_accountant(self):
        self.state = '11'


    def action_mark_done(self):
        self.env['hr.employee'].browse(self.decision_number.employee_name.id).write({
            'branch_id': self.decision_number.current_branch_name.id,
            'department_id': self.decision_number.current_emp_department.id,
            'job_id': self.decision_number.current_job_position.id,
            'parent_id': self.decision_number.current_manager.id,
            'company_id': self.decision_number.current_company.id,
            'bonus_classification_ids': [(6, 0, self.decision_number.current_bonus_cls_ids.ids)]
        })
        # contract_id = self.env['hr.contract'].search(
        #     [('employee_id', '=', self.employee_name.id), ('state', '=', 'open')])

        running_emp_contract = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
        if running_emp_contract:
            self.env['hr.contract'].browse(running_emp_contract.id).write({
                'analytic_account_id': self.decision_number.current_analytic_account.id
            })
            if self.decision_number.decision_type == 'transfer_employee':
                self.env['hr.contract'].browse(running_emp_contract.id).write({
                    'struct_id': self.decision_number.current_salary_structure.id,
                    'wage': self.decision_number.current_wage,
                    'work_nature_allowance': self.decision_number.current_work_nature,
                    'fixed_add_allowance': self.decision_number.current_fixed_additional,
                    'food_allowance': self.decision_number.current_food,
                    'fixed_deduct_amount': self.decision_number.current_fixed_deduction,
                })
        if self.decision_type  == 'appoint_employee':
            self.employee_id.write({'employee_state': 'on_job', 'bsgjoining_date': self.working_date})
        if self.notice_type == 'start_first_time':
            emp_contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'draft')], limit=1)
            if emp_contract:
                emp_contract._get_trail_date_end()
                emp_contract.write({'date_start': self.working_date,'state':'open'})
                self.employee_id.write({'state': 'trail_period', 'bsgjoining_date': self.working_date, 'last_return_date': self.working_date})
                holiday_status_id = self.env['hr.leave.type'].search([('is_annual','=',True),('leave_type','=','paid')],limit=1)
                allocation_request = self.env['hr.leave.allocation'].create({'name': "Allocation of Legal Leaves "+ self.employee_id.name,
                                                                             'employee_id': self.employee_id.id,
                                                                             'holiday_status_id': holiday_status_id.id,
                                                                             'holiday_type': 'employee',
                                                                             'state': 'draft',
                                                                             'nextcall': self.working_date
                                                                             })
                allocation_request.action_confirm()
                allocation_request.action_approve()
                self.state = '8'
            else:
                raise ValidationError(_('Pls make sure current employee has a draft contract'))
        elif self.notice_type == 'start_after_transport':
            if running_emp_contract and self.employee_id.state in ['on_job', 'trail_period']:
                self.employee_id.write({'last_move_date': self.working_date})
                self.state = '8'
            else:
                raise ValidationError(
                    _('Pls make sure current employee on job or trail period state and contract is running'))
        # else:
        #     self.employee_id.write({'last_move_date': self.working_date})
        # loan_obj = self.env['loan.application']
        # loan_id = loan_obj.create({
        #     "employee_id": self.employee_id.id,
        #     "loan_policy": self.employee_id.loan_policy.id or self.env['loan.policies'].search([], limit=1).id,
        #     "loan_type_id": self.env['loan.type'].search([], limit=1).id,
        #     "application_date": self.working_date,
        #     "approve_date": self.start_payroll_date,
        #     "requested_loan_amt": self.total_cost,
        #     "approved_loan_amt": self.total_cost,
        #     "loan_compute_type": "fixed",
        #     "no_of_installment": 1,
        #     "loan_purpose": _("{} - Insurance Difference Amount".format(self.employee_id.name)),
        #     "company_id": self.company_id.id,
        #     "state": "paid",
        # })
        # self.loan_id = loan_id.id
        elif self.notice_type == 'start_after_vacation' and self.sick_leave_type.leave_type == 'paid':
            self.employee_id.write({'last_return_date': self.return_date,'employee_state': 'on_job','state': 'on_job'})
            allocation_id = self.env['hr.leave.allocation'].search([('is_annual_allocation','=',True),('employee_id','=',self.employee_id.id)],limit=1)
            if allocation_id:
                allocation_id.write({'nextcall': self.return_date})
            self.state = '8'
        if self.notice_type == 'start_after_vacation' and self.by_hr:
            self.employee_id.write({'last_return_date': self.return_date,'employee_state': 'on_job','state': 'on_job'})
            allocation_id = self.env['hr.leave.allocation'].search([('is_annual_allocation','=',True),('employee_id','=',self.employee_id.id)],limit=1)
            if allocation_id:
                allocation_id.write({'nextcall': self.return_date})
            self.state = '8'
        # else:
        #     self.state = '8'
    # 
    # def action_mark_as_done(self):
    #     running_emp_contract = self.env['hr.contract'].search(
    #         [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
    #     if self.notice_type == 'start_first_time':
    #         emp_contract = self.env['hr.contract'].search(
    #             [('employee_id', '=', self.employee_id.id), ('state', '=', 'draft')], limit=1)
    #         if emp_contract:
    #             emp_contract.write({'date_start': self.working_date})
    #             self.employee_id.write({'state': 'trail_period', 'bsgjoining_date': self.working_date})
    #         else:
    #             raise ValidationError(_('Pls make sure current employee has a draft contract'))
    #     elif self.notice_type == 'start_after_transport':
    #         if running_emp_contract and self.employee_id.state in ['on_job', 'trail_period']:
    #             self.employee_id.write({'last_move_date': self.working_date})
    #         else:
    #             raise ValidationError(
    #                 _('Pls make sure current employee on job or trail period state and contract is running'))
    #     else:
    #         self.employee_id.write({'last_move_date': self.working_date})

    notice_type = fields.Selection(string="Effective Date Notice Type",
                                   selection=[('start_first_time', 'Started The Work For The First Time'),
                                              ('start_after_transport', 'Started The Work After Transport'),
                                              ('start_after_vacation', 'Started The Work After Vacation')],
                                   default='start_first_time', track_visibility=True)
    employee_company_housing = fields.Boolean(string='Employee Company Housing')
    active = fields.Boolean(string="Active", default=True, track_visibility=True)
    by_hr = fields.Boolean(string="By HR", default=False)
    number = fields.Char(string='number', required=False, readonly=False)
    decision_number = fields.Many2one('employees.appointment', string='Decision Number',
                                      domain="[('employee_name','=', employee_id),('state','=', 'approved')]",
                                      required=False, readonly=True)

    sequence_number = fields.Char(string='Decision  Number', readonly=False, track_visibility='always')

    
    @api.onchange('decision_number')
    def get_decision_number_data(self):
        if not self.decision_number:
            self.decision_date = False
        if self.decision_number:
            self.decision_date = self.decision_number.decision_date

    decision_type = fields.Selection([('appoint_employee', 'Decision to appoint an employee'),
                                      ('transfer_employee', 'Decision to transfer an employee'),
                                      ('assign_employee', 'Decision to assign an employee')],
                                     string='Decision Type')
    #
    # 
    # @api.onchange('notice_type')
    # def onchange_notice_type(self):
    #     if self.notice_type in ('start_first_time', 'start_after_transport'):

    
    @api.onchange('notice_type')
    def get_decision_number_data_null(self):
        if self.notice_type == 'start_after_transport':
            self.decision_number = False
        if self.notice_type == 'start_first_time':
            self.decision_number = False

    @api.onchange('notice_type', 'employee_id')
    def onchange_employee_id(self):
        list_appoint = []
        list_transfer = []
        employees_appoint = self.env['employees.appointment'].search([('employee_name', '=', self.employee_id.id),
                                                                      ('decision_type', '=', 'appoint_employee'),
                                                                      ('state', '=', 'approved')])
        employees_transfer = self.env['employees.appointment'].search([('employee_name', '=', self.employee_id.id),
                                                                       ('decision_type', '=', 'transfer_employee'),
                                                                       ('state', '=', 'approved')])
        for em in employees_appoint:
            list_appoint.append(em.id)
        for em in employees_transfer:
            list_transfer.append(em.id)
        if self.notice_type == 'start_first_time':
            return {'domain': {'decision_number': [('id', 'in', list_appoint)]}}
        elif self.notice_type == 'start_after_transport':
            return {'domain': {'decision_number': [('id', 'in', list_transfer)]}}

    decision_date = fields.Date(string='Decision Date', track_visibility=True, readonly=True)
    emp_description = fields.Text(string="Description", track_visibility=True, translate=True)
    approve_debt_date = fields.Datetime(string='Approve Employee Dept. Date', track_visibility=True, readonly=True)

    @api.model
    def _default_manager_id(self):
        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        return self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])

    emp_manager = fields.Many2one('hr.employee', string='Employee Dept. Manager', track_visibility=True, readonly=True)
    analytic_account = fields.Many2one('account.analytic.account', string='Analytic Account', readonly=True)
    salary_structure = fields.Many2one('hr.payroll.structure', store=True, string='Salary Structure',
                                       track_visibility=True, readonly=True)

    payroll_effect = fields.Selection(string="Payroll Effective Date",
                                      selection=[('start_first_time',
                                                  'The Employee Start Working in the same date & he will include in the payslip on the'),
                                                 ('start_after_transport',
                                                  'The employee start working date, day and he will include in the payroll payslip on the date')],
                                      default='start_first_time',
                                      track_visibility=True)

    
    @api.onchange('payroll_effect')
    def get_decision_payroll_effect_null(self):
        if self.payroll_effect == 'start_first_time':
            self.working_payroll_date = False
            self.payslip_payroll_date = False
        if self.payroll_effect == 'start_after_transport':
            self.start_payroll_date = False

    start_payroll_date = fields.Date(string='Start Payroll Date', track_visibility=True, readonly=False)
    working_payroll_date = fields.Date(string='Employee Start Working Date', track_visibility=True, readonly=False)
    payslip_payroll_date = fields.Date(string='Payroll Payslip Date', track_visibility=True, readonly=False)
    hr_description = fields.Text(string="Description", track_visibility=True, translate=True)

    hr_approve_date = fields.Datetime(string='Hr Supervisor Approve Date', track_visibility=True, readonly=True)
    hr_supervisor = fields.Many2one('hr.employee', string='Hr Supervisor Name', track_visibility=True, readonly=True)

    hr_manager_approve_date = fields.Datetime(string='Hr Manager Approve Date', track_visibility=True, readonly=True)
    hr_manager = fields.Many2one('hr.employee', string='Hr Manager Name', track_visibility=True, readonly=True)

    manager_description = fields.Text(string="Description", track_visibility=True, translate=True)
    salary_description = fields.Text(string="Description", track_visibility=True, translate=True)
    hr_salary_approve_date = fields.Datetime(string='Hr Salary Approve Date', track_visibility=True, readonly=True)
    hr_salary = fields.Many2one('hr.employee', string='Hr Salary Name', track_visibility=True, readonly=True)
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')

    @api.constrains('payslip_payroll_date', 'working_payroll_date')
    def _check_date(self):
        for date in self:
            if date.working_payroll_date and date.working_payroll_date < date.payslip_payroll_date:
                raise ValidationError(_('Can Not Be Start Payroll Date less then the Starting Working Date'))

    
    def attach_document(self):
        view_id = self.env.ref('effective_date_notes.view_attachment_effective_date_form').id
        return {
            'name': _('Attachments'),
            'res_model': 'ir.attachment',
            'view_type': 'form',
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id),
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }

    
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'effect.request'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for upgrade_no in self:
            upgrade_no.attachment_number = attachment.get(upgrade_no.id, 0)

    
    @api.onchange('employee_id')
    def get_employee_data(self):
        if self.employee_id:
            self.manager_id = self.employee_id.parent_id
            self.company_id = self.employee_id.company_id
            self.branch_id = self.employee_id.branch_id
            self.department_id = self.employee_id.department_id
            self.job_id = self.employee_id.job_id
            self.mobile_phone = self.employee_id.mobile_phone
            self.employee_code = self.employee_id.employee_code
            self.bsg_empiqama = self.employee_id.bsg_empiqama
            self.bsg_national_id = self.employee_id.bsg_national_id
            self.analytic_account = self.employee_id.contract_id.analytic_account_id
            self.salary_structure = self.employee_id.contract_id.struct_id

    
    @api.onchange('from_hr')
    def get_employee_domain(self):
        if self.from_hr:
            if self.env.user.has_group('bsg_hr.group_hr_specialist') or self.env.user.has_group(
                    'bsg_hr.group_hr_manager'):
                return {'domain': {'employee_id': []}}
            elif self.env.user.has_group('bsg_hr.group_department_manager'):
                return {'domain': {'employee_id': [('parent_id', 'in', self.env.user.employee_ids.ids)]}}
            else:
                self.employee_id = self.env.user.employee_ids
                return {'domain': {'employee_id': [('user_id', '=', self.env.user.id)]}}
        else:
            self.employee_id = self.env.user.employee_ids
            return {'domain': {'employee_id': [('user_id', '=', self.env.user.id)]}}

    
    def action_validate(self):
        if self.notice_type != 'start_after_vacation':
            if self.decision_date > self.working_date:
                raise ValidationError('Working date must be equal or greater than decision date')
        self.state = 'submitted'
        # MailTemplate = self.env.ref('effective_date_notes.effect_mail_employee_manager_temp', False)
        # for rec in self.employee_id:
        #     if rec.partner_id.email:
        #         MailTemplate.sudo().write(
        #             {'email_to': str(self.manager_id.partner_id.email), 'email_from': str(rec.partner_id.email)})
        #         MailTemplate.sudo().send_mail(self.id, force_send=True)
        # msg_id = self.env['mail.message'].search([('model', '=', 'effect.request'), ('res_id', '=', self.id)])
        # msg_id.unlink()
        #
        # return {
        #     'effect': {
        #         'fadeout': 'slow',
        #         'message': 'Your Effective Date Request Submitted To Manager ',
        #         'type': 'rainbow_man',
        #     }
        # }

    
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('effective_date_notes', 'action_attachment')
        return res

    
    def mng_approve(self):
        self.state = 'approve'
        MailTemplate = self.env.ref('effective_date_notes.effect_mail_manager_approve_temp', False)
        email = self.env['res.users'].search([])
        notification_email = []
        for em in email:
            if em.has_group('effective_date_notes.effective_reporting_supervisor_group'):
                if self.manager_id.partner_id.email != em.email:
                    notification_email.append(em.email)

        for email_select in notification_email:
            print('email_to', email_select)
            print('email_from', self.manager_id.partner_id.email)
            MailTemplate.sudo().write(
                {'email_to': str(email_select), 'email_from': str(self.manager_id.partner_id.email)})
            MailTemplate.sudo().send_mail(self.id, force_send=True)
        msg_id = self.env['mail.message'].search([('model', '=', 'effect.request'), ('res_id', '=', self.id)])
        msg_id.unlink()

        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        self.emp_manager = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
        self.approve_debt_date = fields.datetime.now()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Effective Date Request Submitted To HR Supervisor For Approval ',
                'type': 'rainbow_man',
            }
        }

    
    def mng_reject(self):
        self.state = '1'
        self.decision_number = False
        self.decision_date = False

    
    def finance_approve(self):
        self.state = 'fin_approve'

        MailTemplate = self.env.ref('effective_date_notes.effect_mail_manager_approve_temp', False)

        email = self.env['res.users'].search([])
        notification_email = []
        for em in email:
            if em.has_group('effective_date_notes.effective_reporting_hr_manager_group'):
                if self.manager_id.partner_id.email != em.email:
                    notification_email.append(em.email)

        for email_select in notification_email:
            print('email_to', email_select)
            print('email_from', self.manager_id.partner_id.email)
            MailTemplate.sudo().write(
                {'email_to': str(email_select), 'email_from': str(self.manager_id.partner_id.email)})
            MailTemplate.sudo().send_mail(self.id, force_send=True)
        msg_id = self.env['mail.message'].search([('model', '=', 'effect.request'), ('res_id', '=', self.id)])
        msg_id.unlink()

        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        self.hr_supervisor = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
        self.hr_approve_date = fields.datetime.now()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Effective Date Request Submitted To HR Manager For Approval ',
                'type': 'rainbow_man',
            }
        }

    
    def finance_reject(self):
        self.state = 'submitted'
        self.start_payroll_date = False
        self.working_payroll_date = False
        self.payslip_payroll_date = False

    
    def hr_manager_approve(self):
        self.state = 'hr_manager_approve'

        MailTemplate = self.env.ref('effective_date_notes.effect_mail_manager_approve_temp', False)
        email = self.env['res.users'].search([])
        notification_email = []
        for em in email:
            if em.has_group('effective_date_notes.effective_reporting_hr_salary_group'):
                if self.manager_id.partner_id.email != em.email:
                    notification_email.append(em.email)

        for email_select in notification_email:
            print('email_to', email_select)
            print('email_from', self.manager_id.partner_id.email)
            MailTemplate.sudo().write(
                {'email_to': str(email_select), 'email_from': str(self.manager_id.partner_id.email)})
            MailTemplate.sudo().send_mail(self.id, force_send=True)
        msg_id = self.env['mail.message'].search([('model', '=', 'effect.request'), ('res_id', '=', self.id)])
        msg_id.unlink()

        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        self.hr_manager = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
        self.hr_manager_approve_date = fields.datetime.now()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Effective Date Request Submitted To HR Salary Manager For Approval ',
                'type': 'rainbow_man',
            }
        }

    
    def hr_manager_reject(self):
        self.state = 'hr_manager_reject'

    effective_count = fields.Integer('Number Effective Date Request')

    def _compute_effective_count(self):
        for record in self:
            record.effective_count = self.env['effect.request'].search_count(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'done')])

    
    def hr_salary_approve(self):
        self.state = 'done'
        self._compute_effective_count()
        effective = self.env['hr.employee'].search([('id', '=', self.employee_id.id)], limit=1)
        for rec in effective:
            self.employee_id.effective_count = self.effective_count
            self.employee_id.suspend_salary = False
            self.employee_id.employee_state = 'on_job'

        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        self.hr_salary = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
        self.hr_salary_approve_date = fields.datetime.now()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Effective Date Request has Been Approved',
                'type': 'rainbow_man',
            }
        }

    
    def hr_salary_reject(self):
        self.state = 'fin_approve'

    @api.model
    def create(self, vals):
        res = super(EffectRequest, self).create(vals)
        if self.env.user.user_branch_id.branch_no:
            res.name = 'EDN' + self.env.user.user_branch_id.branch_no + self.env['ir.sequence'].next_by_code(
                'effect.request')
        else:
            res.name = 'EDN' + self.env['ir.sequence'].next_by_code('effect.request')
        return res

    @api.model
    def base_url(self):
        base_url = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                       company_id=self.env.user.company_id.id).get_param(
            'web.base.url')
        return base_url

    @api.model
    def database_name(self):
        return self._cr.dbname

    
    def generate_access_token(self):
        if self.access_token:
            return self.access_token
        access_token = str(uuid.uuid4())
        self.write({'access_token': access_token})
        return access_token

    reason = fields.Text(string="Reason For Delay", track_visibility=True, translate=True, readonly=False)
    reason_active = fields.Boolean(string="Reason Active", compute='_compute_days')

    reason_approve = fields.Boolean(string="Reason Approve")

    is_driver = fields.Boolean(string="Is Driver")
    is_settlement = fields.Boolean(string="Is Including settlement ")
    duration = fields.Float(string='Duration', related='leave_type_id.number_of_days_display')
    # medical_insurance_cost = fields.Float(string='Medical Insurance Cost', track_visibility=True, translate=True,
    #                                       readonly=False, copy=False, compute='_compute_all_costing')
    iqama_license_cost = fields.Float(string='Iqama And License Cost', track_visibility=True,readonly=False, copy=False)
    social_insurance_cost = fields.Float(string='Social Insurance Cost', track_visibility=True,readonly=False, copy=False)
    gosi_cost = fields.Float(string='Gosi Cost', track_visibility=True, readonly=False, copy=False)
    total_cost = fields.Float(string='Total Cost', track_visibility=True, readonly=False, copy=False)
    days_delayed = fields.Char(string='Delayed (If Any)', compute='_compute_days', readonly=True)

    leave_type_id = fields.Many2one('hr.leave', string='Leave', track_visibility=True)
    is_annual = fields.Boolean(string="Is annual")

    sick_leave_type = fields.Many2one('hr.leave.type', string='Leave Type',
                                      related="leave_type_id.holiday_status_id", required=False, track_visibility=True,
                                      readonly=True)
    return_date = fields.Date(string='Returning Date', default=lambda self: fields.date.today(), track_visibility=True,
                              readonly=False, required=True)
    date_from = fields.Date(string='From', track_visibility=True, related='leave_type_id.request_date_from')
    date_to = fields.Date(string='To', track_visibility=True, related='leave_type_id.request_date_to')
    check_days_delayed_by_type = fields.Boolean(string='Days Delayed Check')
    is_foreign = fields.Boolean(string='is_foreign')


    @api.onchange('leave_type_id','employee_id')
    def get_leave_type_domain(self):
        if self.employee_id:
            leave_type_ids = []
            request_ids = self.env['effect.request'].search(
                [('employee_id', '=', self.employee_id.id), ('state', 'not in', ["9"])])
            for request_id in request_ids:
                if request_id.leave_type_id:
                    leave_type_ids.append(request_id.leave_type_id.id)
            if leave_type_ids:
                return {'domain': {'leave_type_id': [('employee_id', '=',self.employee_id.id),('id', 'not in',leave_type_ids)]}}
            else:
                return {'domain': {'leave_type_id': [('employee_id', '=', self.employee_id.id)]}}



    @api.depends('return_date', 'date_to','working_date','decision_date','notice_type')
    def _compute_days(self):
        self.reason_active = False
        self.days_delayed = ''
        if self.notice_type == 'start_after_vacation':
            if self.return_date and self.date_to:
                delta = self.return_date - (self.date_to + relativedelta(days=1))
                if delta.days <= 0:
                    self.days_delayed = '0' + ' days '
                    # raise ValidationError("days delayed can not be less than Zero: %s" % delta.days)
                    self.reason_active = False
                else:
                    self.reason_active = True
                    self.days_delayed = str(delta.days) + ' days '


        elif self.notice_type == 'start_after_transport':
            if self.working_date and self.decision_date:
                if self.working_date > self.decision_date:
                    delta = self.working_date - self.decision_date
                    if delta.days <= 0:
                        self.days_delayed = '0' + ' days '
                        self.reason_active = False
                    else:
                        self.days_delayed = str(delta.days) + ' days '
                        self.reason_active = True
        else:
            if self.working_date and self.decision_date:
                if self.working_date > self.decision_date:
                    delta = self.working_date - self.decision_date
                    if delta.days <= 0:
                        # self.days_delayed = '0' + ' days '
                        # raise ValidationError("days delayed can not be less than Zero: %s" % delta.days)
                        self.reason_active = False
                    else:
                        self.reason_active = True
                        # self.days_del






    # @api.depends('employee_id', 'notice_type', 'leave_type_id')
    # def _compute_all_costing(self):
    #     for rec in self:
    #         if rec.date_to and rec.return_date:
    #             yearly_insurance_cost = self.env['hr.insurance'].search(
    #                 [('employee_insurance', '=', rec.employee_id.id), ('is_employee', '=', True)],
    #                 limit=1).yearly_insurance_cost
    #             date_diff = abs((rec.return_date - rec.date_to).days)
    #             print(yearly_insurance_cost)
    #             if date_diff > 20:
    #                 if rec.employee_id.employee_type == 'foreign':
    #                     rec.medical_insurance_cost = (yearly_insurance_cost / 360) * (date_diff - 20)
    #                     # rec.iqama_license_cost = (rec.employee_id.bsg_empiqama.yearly_iqama_cost / 360) * (
    #                     #             date_diff - 20)
    #                     # rec.total_cost = (rec.medical_insurance_cost + rec.iqama_license_cost)
    #                 else:
    #                     # rec.gosi_cost = (rec.employee_id.contract_id.wage * 9.75) * (date_diff - 20)
    #                     rec.medical_insurance_cost = (yearly_insurance_cost / 360) * (date_diff - 20)
    #                     # rec.total_cost = (rec.medical_insurance_cost + rec.gosi_cost)



    
    def action_submit_dept_manager(self):
        self.state = 'dept_approve'

    
    def action_submit_hr_emp_manager(self):
        self.state = 'hr_emp_approve'

    
    def action_submit_hr_supervisor(self):
        self.state = 'hr_super_approve'

    # 
    # def action_mark_as_done(self):
    #     running_emp_contract = self.env['hr.contract'].search(
    #         [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
    #     if self.notice_type == 'start_first_time':
    #         emp_contract = self.env['hr.contract'].search(
    #             [('employee_id', '=', self.employee_id.id), ('state', '=', 'draft')], limit=1)
    #         if emp_contract:
    #             emp_contract.write({'date_start': self.working_date})
    #             self.employee_id.write({'state': 'trail_period', 'bsgjoining_date': self.working_date})
    #             self.state = 'done'
    #         else:
    #             raise ValidationError(_('Pls make sure current employee has a draft contract'))
    #     elif self.notice_type == 'start_after_transport':
    #         if running_emp_contract and self.employee_id.state in ['on_job', 'trail_period']:
    #             self.employee_id.write({'last_move_date': self.working_date})
    #         else:
    #             raise ValidationError(
    #                 _('Pls make sure current employee on job or trail period state and contract is running'))
    #     else:
    #         self.employee_id.write({'last_move_date': self.working_date})
