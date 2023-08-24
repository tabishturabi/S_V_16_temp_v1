# -*- coding: utf-8 -*-
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ViolationType(models.Model):
    """"""
    _name = 'employee.violation.type'
    _description = "Violation Type"

    name = fields.Char(string="Name", translate=True)
    penalty_ids = fields.One2many( comodel_name="penalty", inverse_name="violation_id" , string="penalties")


class Penalty(models.Model):
    """"""
    _name = 'penalty'
    _description = "Penalty"

    PENALTY_TYPES = [
        ("warning", "Warning"),
        ("deduction", "Deduction"),
        ("suspend", "Suspend"),
        ("stop_upgrade", "Stop Upgrade"),
        ("stop_bonus", "Stop Bonus"),
        ("termination", "Termination")
    ]

    DEDUCTION_TYPES = [
        ("percentage", "Percentage"),
        ("hour", "Hours"),
        ("day", "Days")
    ]

    name = fields.Char(string="Name", translate=True)
    violation_id = fields.Many2one("employee.violation.type", string="Violation")
    sequence = fields.Integer(string="Sequence", default=1)
    penalty_period = fields.Integer(string="Penalty Period / Day", default=180)
    penalty_type = fields.Selection(PENALTY_TYPES, string="Penalty Type", default="warning")
    deduction_type = fields.Selection(DEDUCTION_TYPES, string="Deduction Type", default="day")
    deduction_percentage = fields.Float(string="Percentage Amount")
    deduction_period_hour = fields.Float(string="Deduction Period / Hours")
    deduction_period_day = fields.Float(string="Deduction Period / Days", default=5)
    suspend_period = fields.Integer(string="Suspend Period / Day", default=5)

    @api.constrains('sequence')
    def _check_sequence(self):
        for rec in self:
            if self.env['penalty'].search([('id', '!=', rec.id), ('sequence', '=', rec.sequence)]):
                raise ValidationError(_("Sequence must be unique per violation"))


class EmployeePenalty(models.Model):
    """"""
    _name = 'employee.penalty'
    _inherit = 'mail.thread'
    _rec_name = 'employee_id'
    _description = "Employee Penalty"

    STATE = [
        ('draft', 'Draft'),
        ('hr_supervisor', 'Hr Supervisor'),
        ('branch_supervisor', 'Branch Supervisor'),
        ('direct_manager', 'Direct Manager'),
        ('hr_salary_accountant', 'HR Salary Accountant'),
        ('applied', 'Applied')
    ]

    state = fields.Selection(STATE, default='draft', string='State', tracking=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", tracking=True)
    department_id = fields.Many2one("hr.department", related="employee_id.department_id", string="Department")
    manager_id = fields.Many2one("hr.employee", related="employee_id.parent_id", string="Manager")
    employee_job = fields.Many2one("hr.job", related="employee_id.job_id", string="Job Position")
    employee_no = fields.Char(related="employee_id.pin", string="Employee No")
    violation_date = fields.Date(string="Violation Date", default=fields.Date.today(), tracking=True)
    applied_date = fields.Date(string="Applied Date")
    violation_id = fields.Many2one("employee.violation.type", string="Violation Type", tracking=True)
    penalty_id = fields.Many2one("penalty", string="Penalty", copy=False)
    reason = fields.Text(string="Reason")
    employee_salary = fields.Float(string="Employee Salary")
    deduction_amount = fields.Float(string="Deduction Amount", compute="_get_deduction_amount")
    payslip_id = fields.Many2one("hr.payslip", string="Deducted in Payslip")
    refuse_reason = fields.Text(string="Refuse Reasons", track_visibility='onchange')
    cancel_reason = fields.Text(string="Cancel Reasons", track_visibility='onchange')
    branch_supervisor_check = fields.Boolean(string="Branch Supervisor Check",compute="get_branch_supervisor_check")
    direct_manager_check = fields.Boolean(string="Direct Manager Check",compute="get_direct_manager_check")
    salary_per_day = fields.Float(string="Salalry Per Day",compute="compute_employee_salary")
    salary_per_hour = fields.Float(string="Salalry Per Hour",compute="compute_employee_salary")

    def compute_employee_salary(self):
        for rec in self:
            employee_contract = self.env["hr.contract"].search([('employee_id', '=', rec.employee_id.id),
                                                                ('state', '=', 'open')], limit=1)
            if employee_contract:
                # day_wage = (rec.employee_id.line_ids.filtered(lambda l: l.code == 'GROSS').total / 30)
                day_wage = (employee_contract.wage/ 30)
                hour_wage = day_wage/8
                rec.salary_per_day = day_wage
                rec.salary_per_hour = hour_wage



    def get_branch_supervisor_check(self):
        for rec in self:
            if rec.env.user.id == rec.employee_id.branch_id.supervisor_id.user_id.id:
                rec.branch_supervisor_check = True
            else:
                rec.branch_supervisor_check = False

    def get_direct_manager_check(self):
        for rec in self:
            if rec.env.user.id == rec.employee_id.parent_id.user_id.id:
                rec.direct_manager_check = True
            else:
                rec.direct_manager_check = False


    @api.onchange('employee_id')
    def _get_employee_salary(self):
        for rec in self:
            print('..................._get_employee_salary.............')
            print('...................rec.employee_id.line_ids.............',rec.employee_id.line_ids)
            # rec.employee_salary = self.env["hr.contract"].search([('employee_id', '=', rec.employee_id.id),
            #                                                       ('state', '=', 'open')], limit=1).wage
            contract_id = rec.env['hr.contract'].search([('employee_id','=',rec.employee_id.id),('state','=','open')],limit=1)
            # rec.employee_salary = rec.employee_id.line_ids.filtered(lambda l:l.code=='GROSS').total
            print('...................rec.employee_id.contract_id.............', contract_id)
            rec.employee_salary = contract_id.wage

    @api.depends('employee_id', 'penalty_id')
    def _get_deduction_amount(self):
        for rec in self:
            employee_contract = self.env["hr.contract"].search([('employee_id', '=', rec.employee_id.id),
                                                                ('state', '=', 'open')], limit=1)
            rec.deduction_amount = 0.0

            if rec.penalty_id and rec.penalty_id.penalty_type in ('deduction', 'suspend'):
                if employee_contract:
                    # day_wage = (rec.employee_id.line_ids.filtered(lambda l:l.code=='GROSS').total/30)
                    day_wage = employee_contract.wage
                    hour_wage = day_wage/8

                    if rec.penalty_id.deduction_type == "percentage":
                        rec.deduction_amount = (day_wage * (rec.penalty_id.deduction_percentage / 100))
                    elif rec.penalty_id.deduction_type == "hour":
                        rec.deduction_amount = (rec.penalty_id.deduction_period_hour * hour_wage)
                    else:
                        rec.deduction_amount = (rec.penalty_id.deduction_period_day * day_wage)
                else:
                    raise ValidationError(_("Employee {} haven't running contract..."))

    @api.onchange('employee_id', 'violation_date', 'violation_id')
    def _get_penalty(self):
        # A function to get employee penalty depend on violation and last penalty
        for rec in self:
            penalties = self.env['penalty'].search([('violation_id', '=', rec.violation_id.id)], order="sequence DESC")
            last_penalty = self.env['employee.penalty'].search([('employee_id', '=', rec.employee_id.id),
                                                                ('violation_id', '=', rec.violation_id.id),
                                                                ('applied_date', '!=', False)
                                                                ],
                                                               order="id DESC", limit=1)
            if penalties:
                if last_penalty:
                    if (rec.violation_date - last_penalty.applied_date).days > last_penalty.penalty_id.penalty_period:
                        rec.penalty_id = penalties[-1].id
                    else:
                        for penalty in penalties:
                            if penalty.sequence > last_penalty.penalty_id.sequence:
                                rec.penalty_id = penalty.id
                    rec._all_penalties()
                else:
                    rec.penalty_id = penalties[-1].id

    def _all_penalties(self):
        if not self.penalty_id:
            raise ValidationError(_("All penalties for this violation are applied!"))

    def action_submit(self):

        body = ('<strong>You have new penalty<br/>click here to view it: </strong>')
        body += '<a href=# data-oe-model=employee.penalty data-oe-id=%d>%s</a>' % (self.id, self.employee_id.name)
        if self.employee_id.address_home_id:
            mail_details = {
                'subject': "{} Penalty".format(self.employee_id.name),
                'body': body,
                'partner_ids': [self.employee_id.address_home_id.id],
                'message_type': 'email',
                'email_to': self.employee_id.work_email
            }
            self.message_post(**mail_details)
        self.state = 'hr_supervisor'
        self._check_bonus_upgrade()


    def action_hr_specialist_approve(self):
        for rec in self:
            if rec.state == 'hr_supervisor':
                if not rec.employee_id.branch_id.is_hq_branch:
                    rec.state = 'branch_supervisor'
                else:
                    rec.state = 'direct_manager'

    def action_branch_supervisor_approve(self):
        for rec in self:
            if rec.state == 'branch_supervisor':
                rec.state = 'hr_salary_accountant'

    def action_direct_manager_approve(self):
        for rec in self:
            if rec.state == 'direct_manager':
                rec.state = 'hr_salary_accountant'

    def action_hr_salary_accountant_approve(self):
        for rec in self:
            if rec.state == 'hr_salary_accountant':
                first_day = date(month=rec.violation_date.month, year=rec.violation_date.year, day=1)
                last_day = date(month=rec.violation_date.month, year=rec.violation_date.year, day=1
                                ) + relativedelta(months=1, days=-1)

                employee_contract = self.env["hr.contract"].search([('employee_id', '=', rec.employee_id.id),
                                                                    ('state', '=', 'open')], limit=1)
                # hour_wage = (employee_contract.wage / (employee_contract.full_time_required_hours * 4))
                # day_wage = (hour_wage * employee_contract.resource_calendar_id.hours_per_day)

                day_wage = (rec.employee_id.line_ids.filtered(lambda l: l.code == 'GROSS').total / 30)
                hour_wage = day_wage/8

                suspend_days = self.env['employee.penalty'].search([('penalty_id.penalty_type', '=', 'suspend'),
                                                                    ('employee_id', '=', rec.employee_id.id),
                                                                    ('state', '=', 'applied'),
                                                                    ('applied_date', '>=', first_day),
                                                                    ('applied_date', '<=', last_day)])
                suspend_days = sum(days.penalty_id.suspend_period for days in suspend_days)

                deducted_month_days = self.env['employee.penalty'].search([('employee_id', '=', rec.employee_id.id),
                                                                           ('state', '=', 'applied'),
                                                                           ('applied_date', '>=', first_day),
                                                                           ('applied_date', '<=', last_day)])

                deducted_month_days = sum(days.deduction_amount for days in deducted_month_days)

                if (suspend_days + rec.penalty_id.suspend_period) > 5:
                    raise ValidationError(_("A suspend of more than 5 days in month can't be applied!"))

                if (deducted_month_days + rec.deduction_amount) > (day_wage * 5):
                    raise ValidationError(_("A deduction of more than 5 days in month can't be applied!"))

                if rec.deduction_amount > 0.0:
                    if rec.deduction_amount > (day_wage * 5):
                        raise ValidationError(_("A deduction of more than 5 days salary can't be applied!"))

                if (fields.date.today() - rec.violation_date).days > 30:
                    raise ValidationError(
                        _("This penalty has been exposed for more than 30 days, and it can't be applied!"))
                else:
                    rec.applied_date = fields.date.today()
                    rec._check_bonus_upgrade()
                    rec.state = 'applied'


    # def action_approve(self):
    #     first_day = date(month=self.violation_date.month, year=self.violation_date.year, day=1)
    #     last_day = date(month=self.violation_date.month, year=self.violation_date.year, day=1
    #                     ) + relativedelta(months=1, days=-1)
    #
    #     employee_contract = self.env["hr.contract"].search([('employee_id', '=', self.employee_id.id),
    #                                                         ('state', '=', 'open')], limit=1)
    #     hour_wage = (employee_contract.wage / (employee_contract.full_time_required_hours * 4))
    #     day_wage = (hour_wage * employee_contract.resource_calendar_id.hours_per_day)
    #
    #     suspend_days = self.env['employee.penalty'].search([('penalty_id.penalty_type', '=', 'suspend'),
    #                                                         ('employee_id', '=', self.employee_id.id),
    #                                                         ('state', '=', 'approve'),
    #                                                         ('applied_date', '>=', first_day),
    #                                                         ('applied_date', '<=', last_day)])
    #     suspend_days = sum(days.penalty_id.suspend_period for days in suspend_days)
    #
    #     deducted_month_days = self.env['employee.penalty'].search([('employee_id', '=', self.employee_id.id),
    #                                                                ('state', '=', 'approve'),
    #                                                                ('applied_date', '>=', first_day),
    #                                                                ('applied_date', '<=', last_day)])
    #
    #     deducted_month_days = sum(days.deduction_amount for days in deducted_month_days)
    #
    #     if (suspend_days + self.penalty_id.suspend_period) > 5:
    #         raise ValidationError(_("A suspend of more than 5 days in month can't be applied!"))
    #
    #     if (deducted_month_days + self.deduction_amount) > (day_wage * 5):
    #         raise ValidationError(_("A deduction of more than 5 days in month can't be applied!"))
    #
    #     if self.deduction_amount > 0.0:
    #         if self.deduction_amount > (day_wage * 5):
    #             raise ValidationError(_("A deduction of more than 5 days salary can't be applied!"))
    #
    #     if (fields.date.today() - self.violation_date).days > 30:
    #         raise ValidationError(_("This penalty has been exposed for more than 30 days, and it can't be applied!"))
    #     else:
    #         self.applied_date = fields.date.today()
    #         self.state = 'approve'
    #         self._check_bonus_upgrade()

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        return super(EmployeePenalty, self.with_context(
            mail_post_autofollow=self.env.context.get('mail_post_autofollow', True))).message_post(**kwargs)

    def action_cancel(self):
        self.state = 'cancel'
        self._check_bonus_upgrade()

    def action_refuse(self):
        self.state = 'refuse'
        self._check_bonus_upgrade()

    # def action_new(self):
    #     self.applied_date = False
    #     self.state = 'new'
    #     self._check_bonus_upgrade()

    def _check_bonus_upgrade(self):
        employee_contract = self.env["hr.contract"].search([('employee_id', '=', self.employee_id.id),
                                                            ('state', '=', 'open')], limit=1)
        if self.state == 'applied':
            if self.penalty_id.penalty_type == 'stop_upgrade':
                employee_contract.stop_upgrade = True
            elif self.penalty_id.penalty_type == 'stop_bonus':
                employee_contract.stop_bonus = True
        else:
            employee_contract.stop_upgrade = False
            employee_contract.stop_bonus = False


class HRPayslip(models.Model):
    """"""
    _inherit = 'hr.payslip'

    # def compute_sheet(self):
    #     res = super(HRPayslip, self).compute_sheet()
    #     for record in self:  # resolve singleton Error
    #         penalty_id = self.env.ref('hr_employee_penalty.employee_penalty_rule').id
    #         penalty_rule = self.env['hr.salary.rule'].search([('id', '=', penalty_id)])
    #         penalty_rule.amount_fix = 0.0
    #
    #         employee_penalty = self.env['employee.penalty'].search([('employee_id', '=', record.employee_id.id),
    #                                                                 ('state', '=', 'applied'),
    #                                                                 ('applied_date', '>=', record.date_from),
    #                                                                 ('applied_date', '<=', record.date_to),
    #                                                                 ('payslip_id', '=', False)])
    #
    #         for penalty in employee_penalty:
    #             penalty_rule.amount_fix = penalty_rule.amount_fix + penalty.deduction_amount
    #             penalty.payslip_id = self.id
    #     return res
    def get_employee_penality(self,payslip):
        employee_penalty_total = 0
        if payslip.dict.type == 'eos' and self.env.context.get('eos_hr_termination'):
            employee_penalty = self.env['employee.penalty'].search([('employee_id', '=', payslip.dict.employee_id.id),
                                                                    ('state', '=', 'applied'),
                                                                    ('applied_date', '>=', payslip.dict.date_from),
                                                                    ('applied_date', '<=', payslip.dict.date_to),
                                                                    ('payslip_id', '=', False)])
            ep_obj = self.env['employee.penalty'].search([('payslip_id', '=', payslip.dict.id)])
            if ep_obj:
                employee_penalty_total = employee_penalty_total + ep_obj.deduction_amount
            elif employee_penalty:
                for penalty in employee_penalty:
                    employee_penalty_total = employee_penalty_total + penalty.deduction_amount
                    penalty.payslip_id = payslip.dict.id
        elif payslip.dict.type == 'salary':
            employee_penalty = self.env['employee.penalty'].search([('employee_id', '=', payslip.dict.employee_id.id),
                                                                    ('state', '=', 'applied'),
                                                                    ('applied_date', '>=', payslip.dict.date_from),
                                                                    ('applied_date', '<=', payslip.dict.date_to),
                                                                    ('payslip_id', '=', False)])
            ep_obj = self.env['employee.penalty'].search([('payslip_id', '=', payslip.dict.id)])
            if ep_obj:
                employee_penalty_total = employee_penalty_total + ep_obj.deduction_amount
            elif employee_penalty:
                for penalty in employee_penalty:
                    employee_penalty_total = employee_penalty_total + penalty.deduction_amount
                    penalty.payslip_id = payslip.dict.id
        elif payslip.dict.type == 'holiday':
            employee_penalty = self.env['employee.penalty'].search([('employee_id', '=', payslip.dict.employee_id.id),
                                                                    ('state', '=', 'applied'),
                                                                    ('applied_date', '>=', payslip.dict.date_from),
                                                                    ('applied_date', '<=', payslip.dict.date_to),
                                                                    ('payslip_id', '=', False)])
            ep_obj = self.env['employee.penalty'].search([('payslip_id', '=', payslip.dict.id)])
            if ep_obj:
                employee_penalty_total = employee_penalty_total + ep_obj.deduction_amount
            elif employee_penalty:
                for penalty in employee_penalty:
                    employee_penalty_total = employee_penalty_total + penalty.deduction_amount
                    penalty.payslip_id = payslip.dict.id
        return employee_penalty_total


    # def action_payslip_done(self):
    #     res = super(HRPayslip, self).action_payslip_done()
    #     employee_penalty = self.env['employee.penalty'].search([('employee_id', '=', self.employee_id.id),
    #                                                             ('penalty_id.penalty_type', 'in', ('deduction', 'suspend')),
    #                                                             ('state', '=', 'approve'),
    #                                                             ('applied_date', '>=', self.date_from),
    #                                                             ('applied_date', '<=', self.date_to),
    #                                                             ('payslip_id', '=', False)])
    #     for rec in employee_penalty:
    #         rec.payslip_id = self.id
    #     return res

    def action_payslip_cancel(self):
        res = super(HRPayslip, self).action_payslip_cancel()
        employee_penalty = self.env['employee.penalty'].search([('payslip_id', '=', self.id)])
        for rec in employee_penalty:
            rec.payslip_id = False
        return res


class HrContract(models.Model):
    """"""
    _inherit = 'hr.contract'

    stop_upgrade = fields.Boolean(string="Stop Upgrade", default=False)
    stop_bonus = fields.Boolean(string="Stop Bonus", default=False)


class HrEmployee(models.Model):
    """"""
    _inherit = 'hr.employee'

    penalty_count = fields.Integer(string="Penalties", compute="_get_penalty_count")

    def _get_penalty_count(self):
        for rec in self:
            rec.penalty_count = self.env["employee.penalty"].search_count([('employee_id', '=', rec.id)])

    def action_get_penalties(self):
        # This function is action to view employee penalties

        penalties = self.env["employee.penalty"].search([('employee_id', '=', self.id)])
        return {
            'name': '{} Penalties'.format(self.name),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'employee.penalty',
            'domain': [('employee_id', 'in', penalties.mapped('employee_id.id'))]
        }
