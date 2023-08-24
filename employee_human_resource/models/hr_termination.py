# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class HrTermination(models.Model):
    _name = 'hr.termination'
    _rec_name = 'name'
    _description = 'Termination'
    _order = 'name asc, id desc'
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", related='employee_id.name', required=False)
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Termination")
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",related="employee_id.department_id")
    job_id = fields.Many2one(comodel_name="hr.job", string="Job Title",related="employee_id.job_id")
    reject_reason = fields.Text(string="Rejection Reason", track_visibility='always')
    state = fields.Selection(string="State", selection=[('1', 'Draft'),
                                                        ('2', 'Direct Manager'),
                                                        ('3', ' HR Salary Accountant'),
                                                        ('4', 'Legal Department Manager'),
                                                        ('5', 'HR Manager'),
                                                        ('6', 'Accountant'),
                                                        ('7', ' Internal Audit'),
                                                        ('8', 'Finance Manager'),
                                                        ('9', 'Accountant'),
                                                        ('10', 'Done'), ('11', 'Cancel')], default='1', required=False,
                             track_visibility='onchange')


    
    def action_reset(self):
        return self.write({'state': '1'})

    
    def action_cancel(self):
        return self.write({'state': '11'})

    
    def action_done(self):
        return self.write({'state': '10'})

    
    def action_accountant_before_done(self):
        return self.write({'state': '9'})

    
    def action_finance_manager(self):
        return self.write({'state': '8'})

    
    def action_internal_audit(self):
        return self.write({'state': '7'})

    
    def action_accountant_before_audit(self):
        vals_for_clearance = {
            'clearance_type': 'final',
            'employee_id': self.employee_id.id,
            'date_deliver_work': fields.date.today(),
            'termination_id': self.id,
            'work_delivered': "End of Service"
        }
        clearance_id = self.env['hr.clearance'].search([('termination_id', '=', self.id)], limit=1)
        if not clearance_id:
            hr_have_clearance = self.env['hr.clearance'].create(vals_for_clearance)
        return self.write({'state': '6'})

    
    def action_hr_manager(self):
        return self.write({'state': '5'})

    
    def action_legal_department_manager(self):
        if self.total_eos_net == 0 and not self.eos_payslip_id:
            raise ValidationError(_("Pls make sure compute the sheet first before confirming order"))
        if self.eos_by_employee_service:
            return self.write({'state': '5'})
        else:
            return self.write({'state': '4'})

    
    def action_hr_salary_accountant(self):
        return self.write({'state': '3'})

    
    def action_direct_manager(self):
        return self.write({'state': '2'})

    
    def action_terminate_employee(self):
        self.employee_id.write({'state': 'service_expired','employee_state': 'service_expired','suspend_salary':True})

    request_date = fields.Date(string="Request Date", required=False, default=fields.Date.today())
    approve_date = fields.Date(string="Approve Date", required=False, )
    termination_date = fields.Date(string="Termination Date", required=False, default=fields.Date.today())
    reason = fields.Text(string="Reason", required=False, )
    turnover_reason = fields.Many2one(comodel_name="hr.termination.type", string="Reason", required=True)
    end_incentive = fields.Float(string="End of Service Incentive", required=False, )
    end_incentive_month = fields.Float(string="End of Service Months",
                                       default=lambda self: self.env["ir.config_parameter"].sudo().get_param(
                                           "end_service_incentive"))
    is_incentive_calc = fields.Boolean(string="Is Incentive Calc",
                                       default=lambda self: self.env["ir.config_parameter"].sudo().get_param(
                                           "is_calculated"))
    final_work_date = fields.Date(required=True)
    salary_payslip_id = fields.Many2one('hr.payslip', string='Salary', readonly=False,copy=False)
    salary_payslip_line_id = fields.One2many(related='salary_payslip_id.line_ids')
    salary_start_date = fields.Date(related='salary_payslip_id.date_from')
    salary_end_date = fields.Date(related='salary_payslip_id.date_to')
    salary_move = fields.Many2one(related='salary_payslip_id.move_id')
    # salary_payslip_line_ids = fields.One2many(related='salary_payslip_id.line_ids')
    # eos_payslip_line_ids = fields.One2many(related='eos_payslip_id.line_ids')

    eos_payslip_id = fields.Many2one('hr.payslip', string='EOS payslip', readonly=False,copy=False)
    eos_payslip_line_id = fields.One2many(related='eos_payslip_id.line_ids')
    eos_start_date = fields.Date(related='eos_payslip_id.date_from')
    payslip_state_eos = fields.Selection(related='eos_payslip_id.state')
    payslip_state_monthly = fields.Selection(related='salary_payslip_id.state')
    eos_end_date = fields.Date(related='eos_payslip_id.date_to')
    eos_move = fields.Many2one(related='eos_payslip_id.move_id')
    employee_start_date = fields.Date('Employment Date', related='employee_id.bsgjoining_date', readonly=1, store=True)
    service_days = fields.Integer(string='Service Days', compute="compute_service_years")
    service_months = fields.Integer(string='Service Months', compute="compute_service_years")
    service_years = fields.Integer(string='Service Years', compute="compute_service_years")
    vacation_balance = fields.Float(related="employee_id.remaining_leaves")
    notice_period_vacation_balance = fields.Float(string="Notice Period Vacation Balance",compute="get_vacation_balance")
    total_vacation_balance = fields.Float(string="Total Vacation Balance",compute="get_vacation_balance")
    vacation_amount = fields.Float(store=True)
    have_termination = fields.Boolean(string='Have Termination?')
    eos_by_employee_service = fields.Boolean(string='EOS By Employee',default=False)
    hr_termination_duration_id = fields.Many2one(comodel_name="hr.termination.duration",string="Hr Termination Duration")
    eos_options = fields.Selection(string="EOS Type", selection=[('final_exit', 'Final Exit'), ('iqama_transfer', 'Iqama Trasnfer')], track_visibility='onchange')
    employee_type = fields.Selection(related="employee_id.employee_type")
    total_eos_amount = fields.Monetary(string='Total EOS Amount', compute='_get_total_eos_amount')
    total_salary_net = fields.Monetary(string='Total Net Salary', compute='_get_total_eos_amount')
    total_eos_net = fields.Monetary(string='Total', compute='_get_total_eos_amount')
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    is_ticket_created = fields.Boolean(string="Is Ticket Created ", default=False)

    # @api.onchange('turnover_reason','eos_by_employee_service')
    # def _get_turnover_reason(self):
    #     turnover_list = []
    #     hr_termination_type = self.env['hr.termination.type'].search([('can_request_by_employee', '=', True)])
    #     if hr_termination_type:
    #         for termination in hr_termination_type:
    #             turnover_list.append(termination.id)
    #     return {'domain': {'turnover_reason': [('id', 'in', turnover_list)]}}

    @api.depends('employee_id', 'final_work_date', 'vacation_balance')
    def get_vacation_balance(self):
        today = fields.Date.from_string(fields.Date.today())
        for rec in self:
            rec.total_vacation_balance = 0
            rec.notice_period_vacation_balance = 0
            number_of_days_display = 0
            if rec.final_work_date:
                number_of_days_display = (rec.final_work_date - today).days
            if number_of_days_display > 0:
                contract_id = rec.employee_id.contract_id
                if contract_id and contract_id.state == 'open':
                    contract_annual_legal_leave = contract_id.annual_legal_leave
                    if rec.employee_id.country_id.code == 'SA':
                        if contract_annual_legal_leave > 30:
                            days_to_give = contract_annual_legal_leave / 12
                            balance_per_day = days_to_give / 30
                            rec.notice_period_vacation_balance = balance_per_day * number_of_days_display
                        else:
                            days_to_give = 30 / 12
                            balance_per_day = days_to_give / 30
                            rec.notice_period_vacation_balance = balance_per_day * number_of_days_display
                    else:
                        if contract_annual_legal_leave > 21:
                            days_to_give = contract_annual_legal_leave / 12
                            balance_per_day = days_to_give / 30
                            rec.notice_period_vacation_balance = balance_per_day * number_of_days_display
                        else:
                            day_from = fields.Datetime.from_string(contract_id.date_start)
                            day_to = fields.Datetime.from_string(today)
                            date_diff = relativedelta(day_to, day_from)
                            if date_diff.years >= 5:
                                days_to_give = 30 / 12
                                balance_per_day = days_to_give / 30
                                rec.notice_period_vacation_balance = balance_per_day * number_of_days_display
                            else:
                                days_to_give = 21 / 12
                                balance_per_day = days_to_give / 30
                                rec.notice_period_vacation_balance = balance_per_day * number_of_days_display
            rec.total_vacation_balance = rec.notice_period_vacation_balance + rec.vacation_balance

    @api.depends('salary_payslip_line_id', 'eos_payslip_line_id')
    def _get_total_eos_amount(self):
        for rec in self:
            rec.total_eos_amount = sum(rec.eos_payslip_line_id.mapped('total'))
            rec.total_salary_net = rec.salary_payslip_line_id.filtered(lambda l: l.code == 'NET').total
            rec.total_eos_net = rec.total_salary_net + rec.total_eos_amount

    # @api.depends('turnover_reason', 'employee_start_date', 'final_work_date', 'request_date', 'termination_date')
    # def compute_hr_termination_duration(self):
    #     for rec in self:
    #         rec.hr_termination_duration_id = False
    #         if rec.turnover_reason and len(rec.turnover_reason.termination_duration_ids) > 0:
    #             month_diff = rec.employee_start_date.month - rec.final_work_date.month + 12 * (
    #                     rec.employee_start_date.year - rec.final_work_date.year)
    #             vals = rec.turnover_reason.termination_duration_ids.filtered(
    #                 lambda s: s.amount > 0 and s.date_from <= abs(month_diff) <= s.date_to)
    #             rec.hr_termination_duration_id = vals.id

    @api.onchange('department_id')
    def change_job_id(self):
        self.job_id = False

    # def compute_have_termination(self):
    #     for rec in self:
    #         termination_ids = rec.env['hr.clearance'].search(
    #             [('termination_id', '=', rec.id), ('state', 'not in', ['draft', 'cancel'])])
    #         if termination_ids:
    #             rec.have_termination = True
    #         else:
    #             rec.have_termination = False
    # @api.depends('employee_id')
    # def _compute_remain_day(self):
    #     for rec in self:
    #         rec.vacation_balance = rec.employee_id.leagal_leave_allow_ids and sum(rec.employee_id.leagal_leave_allow_ids.mapped('remain_paid_day')) or 0.0

    @api.depends('employee_id', 'employee_start_date', 'final_work_date')
    def compute_service_years(self):
        for rec in self:
            if rec.employee_start_date and rec.final_work_date:
                rec.service_years, rec.service_months, rec.service_days = rec.employee_id.compute_service_years_from_dates(
                    rec.employee_start_date, rec.final_work_date)
            else:
                rec.service_years = rec.service_months = rec.service_days = 0

    # @api.model
    # def create(self,vals):
    #     vals['name'] = self.env['ir.sequence'].next_by_code('hr.termination')
    #     return super(HrTermination, self).create(vals)

    
    def confirm(self):
        for rec in self:
            rec.write({'state': 'dir_mng_approve'})

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.update({'department_id': self.employee_id.department_id.id, 'job_id': self.employee_id.job_id.id})

    
    def action_cancel(self):
        return self.write({'state': '11'})

    
    def action_approved(self):
        self.employee_id.state = 'terminated'
        self.employee_id.end_date = self.final_work_date

        # cancel all employee's contracts
        if self.employee_id.contract_id:
            self.employee_id.contract_id.date_end = self.final_work_date
            self.employee_id.contract_id.end_incentive = self.end_incentive

        if self.salary_payslip_id:
            self.salary_payslip_id.action_payslip_done()
        if self.allowance_payslip_id:
            self.allowance_payslip_id.action_payslip_done()

        for contract in self.employee_id.contract_ids:
            if contract.state != 'cancel':
                contract.write({'date_end': self.final_work_date})
                contract.write({'state': 'end_service'})
                contract.write({'end_service_type': 'terminated'})
        legal_leve_obj = self.env['legal.leave.allow']
        employee_legal = legal_leve_obj.search([('employee_id', '=', self.employee_id.id)])
        employee_legal.write(
            {'taken_days': employee_legal.remain_day, 'paid_taken_days': employee_legal.remain_paid_day})
        self.write({'state': 'done', 'approve_date': fields.Date.today()})

    def direct_mng_approve(self):
        for rec in self:
            for contract in rec.employee_id.contract_ids:
                contract.write({'end_service_type': 'terminated'})
            rec.state = 'hr_mng_approve'

    def hr_mng_approve(self):
        for rec in self:
            rec.state = 'acc_mng_approve'

    def acc_mng_approve(self):
        for rec in self:
            rec.state = 'exc_mng_approve'

    
    def salary_compute(self):
        for rec in self:
            if rec.salary_payslip_id:
                rec.salary_start_date = str(fields.Date.from_string(rec.final_work_date) + relativedelta(day=1))
                rec.salary_end_date = str(fields.Date.from_string(rec.final_work_date))
                rec.salary_payslip_id.date_to = rec.salary_end_date
                rec.salary_payslip_id.date_from = rec.salary_start_date
                rec.salary_payslip_id.sudo().onchange_employee_hr_leave()
                rec.salary_payslip_id.compute_sheet()
                net = rec.salary_payslip_id.line_ids and rec.salary_payslip_id.line_ids.filtered(lambda line: line.code == 'NET').total or 0.0
                rec.salary_payslip_id.total_net = net
                return True

            slip_data = self.env['hr.payslip'].with_context(contract=True). \
                onchange_employee_id(str(fields.Date.from_string(rec.final_work_date) + relativedelta(day=1)),
                                     str(fields.Date.from_string(rec.final_work_date)),
                                     rec.employee_id.id, contract_id=rec.employee_id.contract_id.id)
            rule = self.env['hr.salary.rule'].search([('in_holiday', '=', True)])
            res = {
                'employee_id': rec.employee_id.id,
                'hr_termination_id': self.id,
                'name': 'Salary Slip For/' + rec.employee_id.name,
                'struct_id': slip_data['value'].get('struct_id'),
                'salary_payment_method': rec.employee_id.salary_payment_method,
                'contract_id': rec.employee_id.contract_id.id,
                'type': 'eos',
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': str(fields.Date.from_string(rec.final_work_date) + relativedelta(day=1)),
                'date_to': str(fields.Date.from_string(rec.final_work_date)),
            }
            allowance = self.env['hr.payslip'].create(res)
            allowance.with_context(tracking_disable=True).compute_sheet()

            self.write({'salary_payslip_id': allowance.id, 'salary_start_date': allowance.date_from,
                        'salary_end_date': allowance.date_to})
        return True

    
    def compute_sheet_allowance(self):
        for rec in self:
            if rec.eos_payslip_id:
                rec.eos_start_date = str(fields.Date.from_string(rec.employee_start_date))
                rec.eos_end_date = str(fields.Date.from_string(rec.final_work_date))
                rec.eos_payslip_id.date_to = rec.eos_end_date
                rec.eos_payslip_id.date_from = rec.eos_start_date
                eos_vacation_id = self.env.ref('employee_human_resource.employee_eos_vacation_rule').id
                eos_vacation_rule = self.env['hr.salary.rule'].search([('id', '=', eos_vacation_id)])
                eos_vacation_rule.amount_fix = 0.0
                employee_eos_id = self.env.ref('employee_human_resource.employee_eos_rule').id
                employee_eos_rule = self.env['hr.salary.rule'].search([('id', '=', employee_eos_id)])
                employee_eos_rule.amount_fix = 0.0
                if rec.employee_id.line_ids:
                    rule_codes = rec.employee_id.line_ids.filtered(lambda l: l.code not in ['GROSS', 'NET']).mapped(
                        'code')
                    leave_rule_id = self.env['hr.salary.rule'].search(
                        [('code', 'in', rule_codes), ('in_holiday', '=', True)])
                    if leave_rule_id:
                        leave_rules = rec.employee_id.line_ids.filtered(
                            lambda l: l.code and l.code in leave_rule_id.mapped('code'))
                eos_vacation_rule.amount_fix = (sum(leave_rules.mapped('total')) / 30) * rec.total_vacation_balance
                temp_codes = rec.turnover_reason.allowance_ids.mapped('code')
                employee_gross_salary_per_day = sum(
                    rec.employee_id.line_ids.filtered(lambda l: l.code in temp_codes).mapped('total')) / 30
                if rec.employee_id.contract_id.transportation_allowance > 0 or rec.employee_id.contract_id.housing_allowance > 0:
                    employee_gross_salary_per_day += (
                                                                 rec.employee_id.contract_id.transportation_allowance + rec.employee_id.contract_id.housing_allowance) / 30
                amount = 0
                total_days = (rec.service_years * 360) + (rec.service_months * 30) + (rec.service_days)
                turnover_data = self.env['hr.termination.type'].search([('apply_in_resignation', '=', True)], limit=1)
                if rec.turnover_reason.reason_type == 'resign' and total_days > 3600:
                    turnover_reason = turnover_data
                else:
                    turnover_reason = rec.turnover_reason
                if turnover_reason:
                    for record in turnover_reason.termination_duration_ids:
                        if record.date_from <= total_days <= record.date_to:
                            if total_days < record.factor and total_days > 0:
                                amount += (total_days / 12) * (record.amount * employee_gross_salary_per_day)
                                total_days = 0
                            elif total_days == record.factor:
                                amount += (record.factor / 12) * (record.amount * employee_gross_salary_per_day)
                                total_days = 0
                            elif total_days > record.factor and total_days > 0:
                                amount += (record.factor / 12) * (record.amount * employee_gross_salary_per_day)
                                total_days = total_days - record.factor
                    employee_eos_rule.amount_fix = amount
                rec.eos_payslip_id.sudo().onchange_employee_hr_leave()
                rec.eos_payslip_id.sudo().with_context(tracking_disable=True,eos_hr_termination=True).compute_sheet()
                return True
            eos_vacation_id = self.env.ref('employee_human_resource.employee_eos_vacation_rule').id
            eos_vacation_rule = self.env['hr.salary.rule'].search([('id', '=', eos_vacation_id)])
            eos_vacation_rule.amount_fix = 0.0
            employee_eos_id = self.env.ref('employee_human_resource.employee_eos_rule').id
            employee_eos_rule = self.env['hr.salary.rule'].search([('id', '=', employee_eos_id)])
            employee_eos_rule.amount_fix = 0.0
            if rec.employee_id.line_ids:
                rule_codes = rec.employee_id.line_ids.filtered(lambda l: l.code not in ['GROSS', 'NET']).mapped('code')
                leave_rule_id = self.env['hr.salary.rule'].search(
                    [('code', 'in', rule_codes), ('in_holiday', '=', True)])
                if leave_rule_id:
                    leave_rules = rec.employee_id.line_ids.filtered(
                        lambda l: l.code and l.code in leave_rule_id.mapped('code'))
            eos_vacation_rule.amount_fix = (sum(leave_rules.mapped('total')) / 30) * rec.total_vacation_balance
            temp_codes = rec.turnover_reason.allowance_ids.mapped('code')
            employee_gross_salary_per_day = sum(
                rec.employee_id.line_ids.filtered(lambda l: l.code in temp_codes).mapped('total')) / 30
            if rec.employee_id.contract_id.transportation_allowance > 0 or rec.employee_id.contract_id.housing_allowance > 0:
                employee_gross_salary_per_day += (rec.employee_id.contract_id.transportation_allowance + rec.employee_id.contract_id.housing_allowance) / 30
            amount = 0
            total_days = (rec.service_years * 360) + (rec.service_months * 30) + (rec.service_days)
            turnover_data = self.env['hr.termination.type'].search([('apply_in_resignation', '=', True)], limit=1)
            if rec.turnover_reason.reason_type == 'resign' and total_days > 3600:
                turnover_reason = turnover_data
            else:
                turnover_reason = rec.turnover_reason
            if turnover_reason:
                for record in turnover_reason.termination_duration_ids:
                    if record.date_from <= total_days <= record.date_to:
                        if total_days < record.factor and total_days > 0:
                            amount += (total_days / 12) * (record.amount * employee_gross_salary_per_day)
                            total_days = 0
                        elif total_days == record.factor:
                            amount += (record.factor / 12) * (record.amount * employee_gross_salary_per_day)
                            total_days = 0
                        elif total_days > record.factor and total_days > 0:
                            amount += (record.factor / 12) * (record.amount * employee_gross_salary_per_day)
                            total_days = total_days - record.factor
                employee_eos_rule.amount_fix = amount
                slip_data = self.env['hr.payslip'].with_context(contract=True). \
                    onchange_employee_id(str(fields.Date.from_string(rec.employee_start_date)),
                                         str(fields.Date.from_string(rec.final_work_date)),
                                         rec.employee_id.id, contract_id=rec.employee_id.contract_id.id)
                net_salary_rule_id = self.env['hr.salary.rule'].search(
                    [('code', '=', "NET"), ('company_id', '=', self.env.user.company_id.id)], limit=1)
                res = {
                    'employee_id': rec.employee_id.id,
                    'hr_termination_id': self.id,
                    'name': 'EOS Slip For/' + rec.employee_id.name,
                    'struct_id': slip_data['value'].get('struct_id'),
                    'salary_payment_method': rec.employee_id.salary_payment_method,
                    'contract_id': rec.employee_id.contract_id.id,
                    'type': 'eos',
                    'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                    'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                    'date_from': str(fields.Date.from_string(rec.employee_start_date)),
                    'date_to': str(fields.Date.from_string(rec.final_work_date)),
                    'eos_rule_ids': [(6, 0, eos_vacation_rule.ids + employee_eos_rule.ids + net_salary_rule_id.ids)],

                }
                allowance = self.env['hr.payslip'].create(res)
                allowance.with_context(tracking_disable=True,eos_hr_termination=True).compute_sheet()
                self.write({'eos_payslip_id': allowance.id, 'eos_start_date': allowance.date_from,
                            'eos_end_date': allowance.date_to})
                allowance._compute_total_net()
        return True

