from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
from odoo.tools.float_utils import float_round
from odoo.tools import html2plaintext, is_html_empty

_logger = logging.getLogger(__name__)

WORK_DAY_PER_MONTH = 30


class HrLeave(models.Model):
    _inherit = "hr.leave"


    # def action_hr_clearance(self):
    #     res = self.env['ir.actions.act_window'].for_xml_id('hr_clearence', 'hr_clearance_action')
    #     res['domain'] = [('leave_request_id', 'in', self.ids)]
    #     return res

    hr_clearance_count = fields.Integer('HR Clearance')
    is_create_user = fields.Boolean('Create User', compute="get_create_user")
    leave_req_action = fields.Boolean(string='Leave Request Action?')

    @api.depends('holiday_status_id')
    def _compute_state(self):
        for rec in self:
            rec.state = 'draft'

    def get_create_user(self):
        for rec in self:
            create_user_employee_id = rec.env['hr.employee'].search([('user_id','=',rec.create_uid.id)],limit=1)
            if rec.create_uid.id == rec.env.user.id or create_user_employee_id.branch_id.supervisor_id.user_id.id == rec.env.user.id or create_user_employee_id.parent_id.user_id.id == rec.env.user.id:
                rec.is_create_user = True
            else:
                rec.is_create_user = False

    # 
    # def _compute_hr_clearance_count(self):
    #     for clearance in self:
    #         clearance.hr_clearance_count = self.env['hr.clearance'].search_count(
    #             [('leave_request_id', '=', clearance.id)])

    
    def action_unpaid_leave(self):
        res = self.env['ir.actions.act_window']._for_xml_id('hr_holidays.hr_leave_action_my')
        res['domain'] = [('unpaid_leave_id', 'in', self.ids)]
        return res

    
    def action_hr_exit_return_view(self):
        res = self.env['ir.actions.act_window']._for_xml_id('employee_human_resource.action_menu_government_relations')
        res['domain'] = [('leave_request_id', 'in', self.ids)]
        return res

    hr_exit_return_count = fields.Integer('Number of Exit Return', compute='_compute_hr_exit_return_count',
                                          track_visibility='onchange')

    
    def _compute_hr_exit_return_count(self):
        for exit in self:
            exit.hr_exit_return_count = self.env['hr.exit.return'].search_count([('leave_request_id', '=', exit.id)])

    
    def action_update_employee_state(self):
        if self.employee_id:
            self.employee_id.write({'state': 'on_leave', 'employee_state': 'on_leave', 'suspend_salary': True})

    def action_hr_effect_request(self):
        res = self.env['ir.actions.act_window']._for_xml_id('effective_date_notes.effect_date_request_action')
        res['domain'] = [('leave_type_id', 'in', self.ids)]
        return res

    hr_effect_request_count = fields.Integer('HR Effective Request',
                                             compute='_compute_hr_effect_request_count', track_visibility='onchange')

    
    def _compute_hr_effect_request_count(self):
        for effect in self:
            effect.hr_effect_request_count = self.env['effect.request'].search_count(
                [('leave_type_id', '=', effect.id)])

    
    def action_hr_ticket(self):
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_hr_ksa_ticket.ticket_request_action')
        res['domain'] = [('leave_request_id', 'in', self.ids)]
        return res

    hr_ticket_count = fields.Integer('Leave Tickets', compute='_compute_hr_ticket_count',
                                     track_visibility='onchange')

    
    def _compute_hr_ticket_count(self):
        for ticket in self:
            ticket.hr_ticket_count = self.env['hr.ticket.request'].search_count(
                [('leave_request_id', '=', ticket.id)])

    @api.onchange('employee_id')
    def onchange_last_employee_contract(self):
        if self.holiday_type == 'employee':
            running_emp_contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
            if running_emp_contract:
                self.last_employee_contract = running_emp_contract.id

    @api.model
    def default_get(self, fields):
        result = super(HrLeave, self).default_get(fields)
        print(self.env.user.employee_ids)
        if len(self.env.user.employee_ids) > 0:
            running_emp_contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.env.user.employee_ids.id), ('state', '=', 'open')], limit=1)
            if running_emp_contract:
                result['last_employee_contract'] = running_emp_contract.id
        return result

    replace_by = fields.Many2one("hr.employee", string="Replace By")
    last_employee_contract = fields.Many2one("hr.contract", string="Current Contract")
    employee_type = fields.Selection(selection=[('foreign', 'Foreign'), ('citizen', 'Citizen')],
                                     related="employee_id.employee_type")

    delegate_acc = fields.Boolean("Delegate Permissions")
    successful_completion = fields.Boolean("Successful Completion")
    is_has_ticket = fields.Boolean(compute='get_ticket')
    is_ticket_created = fields.Boolean(string="Is Ticket Created ", default=False)
    is_send_confirmation = fields.Boolean(string="Accountant Confirmation ", default=False)

    is_exit_entry_created = fields.Boolean(string="is Exit Entry Created ", default=False)
    is_effective_created = fields.Boolean(string="Is Effective Created", default=False)
    is_remaining_leaves = fields.Boolean(compute='check_remaining_leaves')
    request_more_than_balance = fields.Boolean("Request More Than Balance")
    remaining_leaves = fields.Float(
        related='employee_id.remaining_leaves', string='Remaining Legal Leaves',
        help='Total number of legal leaves allocated to this employee, change this value to create allocation/leave request. '
             'Total based on all the leave types without overriding limit.')
    vacation_balance = fields.Float(compute='get_vacation_balance', string='Vacation Balance', store=True)

    last_ticket_date = fields.Date(string='Last Ticket Date', related='employee_id.contract_id.last_ticket_date')
    payslip_status = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('cancel', 'Rejected'),
    ], string='Payslip Status', related="holiday_salary_payslip_id.state")
    # state = fields.Selection(selection=[
    #     ('draft', 'Draft'),
    #     ('hr_specialist', 'Hr Specialist'),
    #     ('hr_manager', 'Hr Manager'),
    #     ('branch_supervisor', 'Branch Supervisor'),
    #     ('department_supervisor', 'Department Supervisor'),
    #     ('area_manager', 'Area Manager'),
    #     ('branches_department_manager', 'Branches Department Manager'),
    #     ('department_manager', 'Department Manager'),
    #     ('vice_em', 'vice Execution Manager'),
    #     ('finance_manager', 'Finance Manager'),
    #     ('validate', 'Approved'),
    #     ('confirm', 'Approved'),  # for old process
    #     ('refuse', 'Refused'),
    #     ('cancel', 'Cancelled'),
    #
    # ], default="draft")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'To Approve'),
        ('hr_specialist', 'Hr Specialist'),
        ('hr_manager', 'Hr Manager'),
        ('department_manager', 'Direct Manager'),
        ('vice_em', 'vice Execution Manager'),
        ('internal_audit_manager', 'Internal Audit Manager'),
        ('vice_em', 'vice Execution Manager'),
        ('finance_manager', 'Finance Manager'),
        ('accountant', 'Accountant'),
        ('validate', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Cancelled'),

    ], default="draft")
    need_clearance = fields.Boolean("With Clearance", compute='_compute_holiday_status_id_leave_configuration',
                                    store=True)
    is_external_leave = fields.Boolean("Is External Leave", default=False)
    need_clearance_check = fields.Boolean("With Clearance check", compute='get_clearance_check')
    cancel_reason = fields.Text("Cancel Reason")
    refuse_reason = fields.Text("Refuse Reason", )
    hr_leave_salary_rule_ids = fields.One2many(comodel_name="hr.payslip.line", inverse_name="hr_leave_request_id",
                                               string="Salary Payslip")
    allowance_payslip_line_id = fields.One2many(comodel_name="hr.payslip.line", inverse_name="hr_leave_request_id",
                                                string="Allowance Payslip")
    allowance_deduction_payslip_line_id = fields.One2many(comodel_name="hr.payslip.line",
                                                          inverse_name="hr_leave_request_id",
                                                          string="Allowance and Deduction")
    leave_type_type = fields.Selection(related="holiday_status_id.leave_type")
    attach_chick = fields.Boolean("Attach Chick", related="holiday_status_id.attach_chick")
    alternative_chick = fields.Boolean("Alternative Chick", related="holiday_status_id.alternative_chick")
    salary_start_date = fields.Date()
    salary_end_date = fields.Date()
    salary_payslip_id = fields.Many2one('hr.payslip', string='Salary', readonly=True)
    hr_exit_return_id = fields.Many2one('hr.exit.return', string='Hr Exit Return', track_visibility='always',
                                        readonly=True)
    hr_clearance_id = fields.Many2one('hr.clearance', string='Hr Clearance', track_visibility='always', readonly=True)
    hr_effect_request_id = fields.Many2one('effect.request', string='Hr Effective Request', track_visibility='always',
                                           readonly=True)
    hr_destination_id = fields.Many2one('hr.destination', string='Destination', track_visibility='always')

    salary_payslip_line_ids = fields.One2many(related='salary_payslip_id.line_ids')

    holiday_salary_start_date = fields.Date()
    holiday_salary_end_date = fields.Date()
    leave_date_to = fields.Date("Leave Date To")
    unpaid_leave_id = fields.Many2one('hr.leave', string='Unpaid Leave', readonly=True)
    holiday_salary_payslip_id = fields.Many2one('hr.payslip', string='Salary', readonly=True)
    holiday_salary_payslip_line_ids = fields.One2many(related='holiday_salary_payslip_id.line_ids')
    payslip_count = fields.Integer(string='Payslips', compute='compute_payslip_count')
    total_clearance_amount = fields.Monetary(string='Total Clearance Amount', compute='_get_total_clearance_amount')
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    is_direct_manager = fields.Boolean(string="is Direct Manager?", compute="get_direct_manager_check")
    issue_ticket_by_company = fields.Boolean(string="Issue Ticket By Company")
    is_allocation = fields.Boolean(string="Is Allocation Created")
    is_approved_by_hr_manager = fields.Boolean(string="Is Approved By Hr Manager")
    birth_delivery_expected_date = fields.Date(string="Birth Delivery Expected Date")
    reject_reason = fields.Text(string="Rejection Reason", track_visibility='always')
    unpaid_duration = fields.Float('Unpaid Duration', compute='_compute_paid_unpaid_duration', copy=False,
                                   readonly=True)
    total_duration = fields.Float('Total Duration', compute='_compute_paid_unpaid_duration', copy=False, readonly=True)
    request_for = fields.Selection(
        [('employee', 'For Employee Only'), ('family', 'For Family Only'), ('all', 'For Employee and Family')],
        string="Request For", track_visibility=True)

    
    def action_refuse(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if any(holiday.state not in ['confirm', 'validate', 'validate1'] for holiday in self):
            raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

        validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
        validated_holidays.write({'state': 'refuse', 'first_approver_id': current_employee.id})
        (self - validated_holidays).write({'state': 'refuse', 'second_approver_id': current_employee.id})
        # Delete the meeting
        self.mapped('meeting_id').unlink()
        # If a category that created several holidays, cancel all related
        linked_requests = self.mapped('linked_request_ids')
        if linked_requests:
            linked_requests.action_refuse()
        self._remove_resource_leave()
        self.activity_update()
        self.is_send_confirmation = False
        return True

    
    @api.depends('leave_date_to')
    def _compute_paid_unpaid_duration(self):
        for allocation in self:
            allocation.unpaid_duration = 0
            allocation.total_duration = 0
            if allocation.leave_date_to:
                delta = allocation.leave_date_to - allocation.request_date_to
                allocation.unpaid_duration = delta.days
                allocation.total_duration = allocation.unpaid_duration + allocation.number_of_days_display

    @api.depends('number_of_days_display', 'holiday_status_id', 'request_date_to', 'request_date_from')
    def get_vacation_balance(self):
        today = fields.Date.from_string(fields.Date.today())
        for rec in self:
            if rec.holiday_status_id.leave_type == 'paid':
                contract_id = rec.last_employee_contract
                if contract_id and contract_id.state == 'open':
                    contract_annual_legal_leave = contract_id.annual_legal_leave
                    if rec.sudo().employee_id.country_id.code == 'SA':
                        if contract_annual_legal_leave > 30:
                            days_to_give = contract_annual_legal_leave / 12
                            balance_per_day = days_to_give / 30
                            rec.vacation_balance = balance_per_day * rec.number_of_days_display
                        else:
                            days_to_give = 30 / 12
                            balance_per_day = days_to_give / 30
                            rec.vacation_balance = balance_per_day * rec.number_of_days_display
                    else:
                        if contract_annual_legal_leave > 21:
                            days_to_give = contract_annual_legal_leave / 12
                            balance_per_day = days_to_give / 30
                            rec.vacation_balance = balance_per_day * rec.number_of_days_display
                        else:
                            day_from = fields.Datetime.from_string(contract_id.date_start)
                            day_to = fields.Datetime.from_string(today)
                            date_diff = relativedelta(day_to, day_from)
                            if date_diff.years >= 5:
                                days_to_give = 30 / 12
                                balance_per_day = days_to_give / 30
                                rec.vacation_balance = balance_per_day * rec.number_of_days_display
                            else:
                                days_to_give = 21 / 12
                                balance_per_day = days_to_give / 30
                                rec.vacation_balance = balance_per_day * rec.number_of_days_display

    @api.depends('number_of_days_display')
    def get_clearance_check(self):
        for rec in self:
            leave_config_id = self.env['hr.leave.config'].search([], limit=1)
            rec.need_clearance_check = False
            if leave_config_id:
                if rec.number_of_days_display < leave_config_id.days_to_clearance:
                    rec.need_clearance_check = True

    @api.depends('employee_id')
    def get_direct_manager_check(self):
        for rec in self:
            if rec.employee_id.parent_id == rec.env.user or rec.env.user.has_group('bsg_hr.group_department_manager'):
                rec.is_direct_manager = True
            else:
                rec.is_direct_manager = False

    @api.depends('salary_payslip_line_ids', 'holiday_salary_payslip_line_ids')
    def _get_total_clearance_amount(self):
        for rec in self:
            rec.total_clearance_amount = rec.salary_payslip_line_ids.filtered(
                lambda l: l.code == 'NET').total + rec.holiday_salary_payslip_line_ids.filtered(
                lambda l: l.code == 'NET').total

    def action_payslips(self):
        payslip_ids = []
        payslip_ids.append(self.holiday_salary_payslip_id.id)
        payslip_ids.append(self.salary_payslip_id.id)
        return {
            'name': 'Payslips',
            'domain': [('leave_request_id', 'in', self.ids)],
            'res_model': 'hr.payslip',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    
    def compute_payslip_count(self):
        for rec in self:
            payslip_ids = []
            payslip_ids.append(rec.holiday_salary_payslip_id.id)
            payslip_ids.append(rec.salary_payslip_id.id)
            count = rec.env['hr.payslip'].search_count([('leave_request_id', '=', rec.id)])
            rec.payslip_count = count

    @api.onchange('request_more_than_balance')
    def onchange_request_more_than_balance(self):
        if self.request_more_than_balance and self.remaining_leaves:
            self.request_date_to = self.request_date_from + timedelta(days=int(self.remaining_leaves) - 1)
        else:
            self.request_date_to = False

    def _get_number_of_days_from_seconds(self, total_sec):
        total_sec = total_sec
        i = total_sec
        days_count = 0
        while total_sec > 0:
            if total_sec == 30600:
                days_count += 1
                total_sec = total_sec - 30600
            elif total_sec > 30600:
                days_count += 1
                total_sec = total_sec - 30600
                total_sec = total_sec - 55800
            else:
                days_count += 1
                total_sec = -1
        return days_count

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_leave_dates(self):
        # super()._compute_number_of_days
        if self.date_from and self.date_to:
            if self.holiday_status_id.include_weekend:
                self.number_of_days = self._get_number_of_days_from_seconds(
                    (self.date_to - self.date_from).total_seconds())
        else:
            self.number_of_days = 1

    @api.onchange('request_date_from')
    def onchange_period(self):
        if self.request_date_from:
            month_first_day = self.request_date_from.replace(day=1)
            one_day_before = self.request_date_from - timedelta(days=1)
            self.salary_start_date = month_first_day
            self.salary_end_date = one_day_before

    @api.depends('holiday_status_id', 'request_date_to', 'request_date_from')
    def _compute_holiday_status_id_leave_configuration(self):
        hr_leave_config = self.env['hr.leave.config'].search([], limit=1)
        for rec in self:
            rec.need_clearance = False
            if rec.holiday_status_id.leave_type == 'paid':
                if rec.number_of_days_display > hr_leave_config.days_to_clearance:
                    rec.need_clearance = True

    
    def action_confirm(self):
        if self.holiday_status_id.attach_chick:
            attachment_count = self.env['ir.attachment'].search_count(
                [('res_model', '=', 'hr.leave'), ('res_id', '=', self.id)])
            if attachment_count == 0:
                raise ValidationError(_("Atleast one attachment is required"))
        employee_id = self.employee_id.id
        if self.holiday_status_id.leave_type == 'sick':
            if self.state == 'draft':
                self.write({'state': 'hr_specialist'})
            elif self.state == 'hr_specialist':
                self.write({'state': 'validate'})
        elif self.holiday_status_id.leave_type == 'death':
            if self.state == 'draft':
                self.write({'state': 'hr_specialist'})
            elif self.state == 'hr_specialist':
                self.write({'state': 'validate'})
        elif self.holiday_status_id.leave_type == 'birth':
            if self.state == 'draft':
                self.write({'state': 'hr_specialist'})
            elif self.state == 'hr_specialist':
                self.write({'state': 'validate'})
        elif self.holiday_status_id.leave_type == 'marry':
            if self.state == 'draft':
                self.write({'state': 'hr_specialist'})
            elif self.state == 'hr_specialist':
                self.write({'state': 'validate'})
        elif self.holiday_status_id.leave_type == 'birthdelivery':
            if self.state == 'draft':
                if self.employee_id.gender != 'female':
                    raise ValidationError(_("Only female can request this type of leave."))
                elif self.birth_delivery_expected_date and (
                        self.birth_delivery_expected_date - fields.date.today()).days > 30:
                    raise ValidationError(_("You can't request this type of leave before mare than 30 days."))
                self.write({'state': 'hr_specialist'})
            elif self.state == 'hr_specialist':
                self.write({'state': 'validate'})
        elif self.holiday_status_id.leave_type == 'test':
            if self.state == 'draft':
                self.write({'state': 'hr_specialist'})
            elif self.state == 'hr_specialist':
                self.write({'state': 'validate'})
        elif self.holiday_status_id.leave_type == 'unpaid':
            # if self.is_department_manager(employee_id):
            if self.state == 'draft':
                self.write({'state': 'department_manager'})
            elif self.state == 'department_manager':
                self.write({'state': 'hr_specialist'})
            elif self.state == 'hr_specialist':
                self.write({'state': 'hr_manager'})
            elif self.state == 'hr_manager':
                self.write({'state': 'validate'})
            # elif self.is_other_department_employee(self.employee_id):
            #     if self.state == 'draft':
            #         self.write({'state': 'hr_specialist'})
            # elif self.state == 'department_supervisor':
            #     self.write({'state': 'department_manager'})
            # elif self.state == 'department_manager':
            #     self.write({'state': 'hr_specialist'})
            #     elif self.state == 'hr_specialist':
            #         self.write({'state': 'hr_manager'})
            #     elif self.state == 'hr_manager':
            #         self.write({'state': 'validate'})
            # else:
            #     if self.state == 'draft':
            #         self.write({'state': 'hr_specialist'})
            #     # elif self.state == 'branch_supervisor':
            #     #     self.write({'state': 'area_manager'})
            #     # elif self.state == 'area_manager':
            #     #     self.write({'state': 'branches_department_manager'})
            #     # elif self.state == 'branches_department_manager':
            #     #     self.write({'state': 'hr_specialist'})
            #     elif self.state == 'hr_specialist':
            #         self.write({'state': 'hr_manager'})
            #     elif self.state == 'hr_manager':
            #         self.write({'state': 'validate'})
        elif self.holiday_status_id.leave_type == 'paid' and self.need_clearance:
            if self.is_department_manager(employee_id):
                if self.state == 'draft':
                    self.write({'state': 'department_manager'})
                elif self.state == 'department_manager':
                    self.write({'state': 'hr_specialist'})
                elif self.state == 'hr_specialist':
                    if self.employee_type == 'foreign' and not self.issue_ticket_by_company and not self.is_ticket_created and self.is_has_ticket and self.need_clearance:
                        raise ValidationError(
                            _("Pls make sure the ticket amount added on the clearance before confirming order"))
                    if self.need_clearance == True and self.total_clearance_amount <= 0:
                        raise ValidationError(_("Pls make sure compute the sheet first before confirming order"))
                    self.write({'state': 'hr_manager'})
                elif self.state == 'hr_manager':
                    if self.is_external_leave and self.employee_type == 'foreign':
                        note = ' عبارة عن قيمة الخروج والعودة لـ '
                        if self.name:
                            note = ' عبارة عن قيمة الخروج والعودة لـ ' + self.name,
                        on_employee_fair = False
                        if not self.is_external_leave and not self.is_has_ticket:
                            on_employee_fair = True
                        res = {
                            'request_for': self.request_for,
                            'travel_before_date': fields.date.today(),
                            'exit_return_type': 'one',
                            'note': note,
                            'on_employee_fair': on_employee_fair,
                            'employee_id': self.employee_id.id,
                            'leave_request_id': self.id}
                        if not self.is_exit_entry_created:
                            hr_exit_return = self.env['hr.exit.return'].create(res)
                            self.hr_exit_return_id = hr_exit_return.id
                            self.is_exit_entry_created = True
                        vals_for_clearance = {
                            'clearance_type': 'vacation',
                            'employee_id': self.employee_id.id,
                            'date_deliver_work': fields.date.today(),
                            'leave_request_id': self.id,
                            'work_delivered': "Legal Leave"
                        }
                        if not self.hr_clearance_id and self.leave_type_type == 'paid':
                            hr_have_clearance = self.env['hr.clearance'].create(vals_for_clearance)
                            self.hr_clearance_id = hr_have_clearance.id
                        if self.request_more_than_balance and not self.unpaid_leave_id:
                            vals_for_unpaid_leave_request = {
                                'date_from': self.request_date_to + timedelta(days=1),
                                'date_to': self.leave_date_to,
                                'holiday_status_id': self.env.ref('hr_holidays.holiday_status_unpaid').id,
                                'employee_id': self.employee_id.id,
                                'request_date_from': self.request_date_to + timedelta(days=1),
                                'request_date_to': self.leave_date_to,
                                'state': 'validate'}
                            self._constrains_for_leave_date_to()
                            unpaid_leave_id = self.env['hr.leave'].create(vals_for_unpaid_leave_request)
                            unpaid_leave_id.unpaid_leave_id = self.id
                            unpaid_leave_id.sudo()._onchange_leave_dates()
                            unpaid_leave_id.sudo()._onchange_request_parameters
                    else:
                        vals_for_clearance = {
                            'clearance_type': 'vacation',
                            'employee_id': self.employee_id.id,
                            'date_deliver_work': fields.date.today(),
                            'leave_request_id': self.id,
                            'work_delivered': "Legal Leave"
                        }
                        if not self.hr_clearance_id and self.leave_type_type == 'paid':
                            hr_have_clearance = self.env['hr.clearance'].create(vals_for_clearance)
                            self.hr_clearance_id = hr_have_clearance.id
                        if self.request_more_than_balance and not self.unpaid_leave_id:
                            vals_for_unpaid_leave_request = {
                                'date_from': self.request_date_to + timedelta(days=1),
                                'date_to': self.leave_date_to,
                                'holiday_status_id': self.env.ref('hr_holidays.holiday_status_unpaid').id,
                                'employee_id': self.employee_id.id,
                                'request_date_from': self.request_date_to + timedelta(days=1),
                                'request_date_to': self.leave_date_to,
                                'state': 'validate'}
                            self._constrains_for_leave_date_to()
                            unpaid_leave_id = self.env['hr.leave'].create(vals_for_unpaid_leave_request)
                            unpaid_leave_id.unpaid_leave_id = self.id
                            unpaid_leave_id.sudo()._onchange_leave_dates()
                            unpaid_leave_id.sudo()._onchange_request_parameters
                    if self.need_clearance:
                        self.is_approved_by_hr_manager = True
                        self.write({'state': 'accountant'})
                        if not self.is_allocation:
                            allocation_request = self.env['hr.leave.allocation'].search(
                                [('is_annual_allocation', '=', True), ('employee_id', '=', self.employee_id.id),
                                 ('employee_id.active', '=', True), ('state', '=', 'validate'),
                                 ('holiday_type', '=', 'employee')], limit=1)
                            allocation_request.write({'number_of_days': allocation_request.number_of_days + float_round(
                                self.vacation_balance % 1, precision_digits=3)})
                            self.is_allocation = True
                    else:
                        self.write({'state': 'internal_audit_manager'})
                        if not self.is_allocation:
                            allocation_request = self.env['hr.leave.allocation'].search(
                                [('is_annual_allocation', '=', True), ('employee_id', '=', self.employee_id.id),
                                 ('employee_id.active', '=', True), ('state', '=', 'validate'),
                                 ('holiday_type', '=', 'employee')], limit=1)
                            allocation_request.write({'number_of_days': allocation_request.number_of_days + float_round(
                                self.vacation_balance % 1, precision_digits=3)})
                            self.is_allocation = True
                elif self.state == 'internal_audit_manager':
                    self.write({'state': 'finance_manager'})
                elif self.state == 'finance_manager':
                    self.write({'state': 'accountant'})
                elif self.state == 'accountant':
                    if self.need_clearance and not self.is_send_confirmation:
                        self.write({'state': 'internal_audit_manager', 'is_send_confirmation': True})
                    else:
                        self.write({'state': 'validate'})
                    vals = {
                        'employee_id': self.employee_id.id,
                        'return_date': self.request_date_to + timedelta(days=1),
                        'working_date': fields.date.today(),
                        'leave_type_id': self.id,
                        'notice_type': 'start_after_vacation',
                    }
                    if not self.is_effective_created and self.leave_type_type == 'paid':
                        hr_effect_request = self.env['effect.request'].create(vals)
                        hr_effect_request.get_employee_data()
                        self.hr_effect_request_id = hr_effect_request.id
                        self.is_effective_created = True
                    if self.request_date_from < fields.Date.today():
                        self.employee_id.write({'state': 'on_leave', 'employee_state': 'on_leave'})
            elif self.is_other_department_employee(self.employee_id):
                if self.state == 'draft':
                    self.write({'state': 'department_manager'})
                elif self.state == 'department_manager':
                    self.write({'state': 'hr_specialist'})
                elif self.state == 'hr_specialist':
                    if self.employee_type == 'foreign' and not self.issue_ticket_by_company and not self.is_ticket_created and self.is_has_ticket and self.need_clearance:
                        raise ValidationError(
                            _("Pls make sure the ticket amount added on the clearance before confirming order"))
                    if self.need_clearance == True and self.total_clearance_amount <= 0:
                        raise ValidationError(_("Pls make sure compute the sheet first before confirming order"))
                    self.write({'state': 'hr_manager'})
                elif self.state == 'hr_manager':
                    if self.is_external_leave and self.employee_type == 'foreign':
                        note = ' عبارة عن قيمة الخروج والعودة لـ '
                        if self.name:
                            note = ' عبارة عن قيمة الخروج والعودة لـ ' + self.name,
                        on_employee_fair = False
                        if not self.is_external_leave and not self.is_has_ticket:
                            on_employee_fair = True
                        res = {
                            'request_for': self.request_for,
                            'travel_before_date': fields.date.today(),
                            'exit_return_type': 'one',
                            'note': note,
                            'on_employee_fair': on_employee_fair,
                            'employee_id': self.employee_id.id,
                            'leave_request_id': self.id}
                        if not self.is_exit_entry_created:
                            hr_exit_return = self.env['hr.exit.return'].create(res)
                            self.hr_exit_return_id = hr_exit_return.id
                            self.is_exit_entry_created = True
                        vals_for_clearance = {
                            'clearance_type': 'vacation',
                            'employee_id': self.employee_id.id,
                            'date_deliver_work': fields.date.today(),
                            'leave_request_id': self.id,
                            'work_delivered': "Legal Leave"
                        }
                        if not self.hr_clearance_id and self.leave_type_type == 'paid':
                            hr_have_clearance = self.env['hr.clearance'].create(vals_for_clearance)
                            self.hr_clearance_id = hr_have_clearance.id
                        if self.request_more_than_balance and not self.unpaid_leave_id:
                            vals_for_unpaid_leave_request = {
                                'date_from': self.request_date_to + timedelta(days=1),
                                'date_to': self.leave_date_to,
                                'holiday_status_id': self.env.ref('hr_holidays.holiday_status_unpaid').id,
                                'employee_id': self.employee_id.id,
                                'request_date_from': self.request_date_to + timedelta(days=1),
                                'request_date_to': self.leave_date_to,
                                'state': 'validate'}
                            self._constrains_for_leave_date_to()
                            unpaid_leave_id = self.env['hr.leave'].create(vals_for_unpaid_leave_request)
                            unpaid_leave_id.unpaid_leave_id = self.id
                            unpaid_leave_id.sudo()._onchange_leave_dates()
                            unpaid_leave_id.sudo()._onchange_request_parameters
                    else:
                        vals_for_clearance = {
                            'clearance_type': 'vacation',
                            'employee_id': self.employee_id.id,
                            'date_deliver_work': fields.date.today(),
                            'leave_request_id': self.id,
                            'work_delivered': "Legal Leave"
                        }
                        if not self.hr_clearance_id and self.leave_type_type == 'paid':
                            hr_have_clearance = self.env['hr.clearance'].create(vals_for_clearance)
                            self.hr_clearance_id = hr_have_clearance.id
                        if self.request_more_than_balance and not self.unpaid_leave_id:
                            vals_for_unpaid_leave_request = {
                                'date_from': self.request_date_to + timedelta(days=1),
                                'date_to': self.leave_date_to,
                                'holiday_status_id': self.env.ref('hr_holidays.holiday_status_unpaid').id,
                                'employee_id': self.employee_id.id,
                                'request_date_from': self.request_date_to + timedelta(days=1),
                                'request_date_to': self.leave_date_to,
                                'state': 'validate'}
                            self._constrains_for_leave_date_to()
                            unpaid_leave_id = self.env['hr.leave'].create(vals_for_unpaid_leave_request)
                            unpaid_leave_id.unpaid_leave_id = self.id
                            unpaid_leave_id.sudo()._onchange_leave_dates()
                            unpaid_leave_id.sudo()._onchange_request_parameters
                    if self.need_clearance:
                        self.write({'state': 'accountant'})
                        if not self.is_allocation:
                            allocation_request = self.env['hr.leave.allocation'].search(
                                [('is_annual_allocation', '=', True), ('employee_id', '=', self.employee_id.id),
                                 ('employee_id.active', '=', True), ('state', '=', 'validate'),
                                 ('holiday_type', '=', 'employee')], limit=1)
                            allocation_request.write({'number_of_days': allocation_request.number_of_days + float_round(
                                self.vacation_balance % 1, precision_digits=3)})
                            self.is_allocation = True
                    else:
                        self.write({'state': 'internal_audit_manager'})
                        if not self.is_allocation:
                            allocation_request = self.env['hr.leave.allocation'].search(
                                [('is_annual_allocation', '=', True), ('employee_id', '=', self.employee_id.id),
                                 ('employee_id.active', '=', True), ('state', '=', 'validate'),
                                 ('holiday_type', '=', 'employee')], limit=1)
                            allocation_request.write({'number_of_days': allocation_request.number_of_days + float_round(
                                self.vacation_balance % 1, precision_digits=3)})
                            self.is_allocation = True
                elif self.state == 'internal_audit_manager':
                    self.write({'state': 'finance_manager'})
                elif self.state == 'finance_manager':
                    self.write({'state': 'accountant'})
                elif self.state == 'accountant':
                    if self.need_clearance and not self.is_send_confirmation:
                        self.write({'state': 'internal_audit_manager', 'is_send_confirmation': True})
                    else:
                        self.write({'state': 'validate'})
                    if self.request_date_from < fields.Date.today():
                        self.employee_id.write({'state': 'on_leave', 'employee_state': 'on_leave'})
            else:
                if self.state == 'draft':
                    self.write({'state': 'department_manager'})
                elif self.state == 'department_manager':
                    self.write({'state': 'hr_specialist'})
                elif self.state == 'hr_specialist':
                    if self.employee_type == 'foreign' and not self.issue_ticket_by_company and not self.is_ticket_created and self.is_has_ticket and self.need_clearance:
                        raise ValidationError(
                            _("Pls make sure the ticket amount added on the clearance before confirming order"))
                    if self.need_clearance == True and self.total_clearance_amount <= 0:
                        raise ValidationError(_("Pls make sure compute the sheet first before confirming order"))
                    self.write({'state': 'hr_manager'})
                elif self.state == 'hr_manager':
                    if self.is_external_leave and self.employee_type == 'foreign':
                        note = ' عبارة عن قيمة الخروج والعودة لـ '
                        if self.name:
                            note = ' عبارة عن قيمة الخروج والعودة لـ ' + self.name,
                        on_employee_fair = False
                        if not self.is_external_leave and not self.is_has_ticket:
                            on_employee_fair = True
                        res = {
                            'request_for': self.request_for,
                            'travel_before_date': fields.date.today(),
                            'exit_return_type': 'one',
                            'note': note,
                            'on_employee_fair': on_employee_fair,
                            'employee_id': self.employee_id.id,
                            'leave_request_id': self.id
                        }
                        if not self.is_exit_entry_created:
                            hr_exit_return = self.env['hr.exit.return'].create(res)
                            self.hr_exit_return_id = hr_exit_return.id
                            self.is_exit_entry_created = True
                        vals_for_clearance = {
                            'clearance_type': 'vacation',
                            'employee_id': self.employee_id.id,
                            'date_deliver_work': fields.date.today(),
                            'leave_request_id': self.id,
                            'work_delivered': "Legal Leave"
                        }
                        if not self.hr_clearance_id and self.leave_type_type == 'paid':
                            hr_have_clearance = self.env['hr.clearance'].create(vals_for_clearance)
                            self.hr_clearance_id = hr_have_clearance.id
                        if self.request_more_than_balance and not self.unpaid_leave_id:
                            vals_for_unpaid_leave_request = {
                                'date_from': self.request_date_to + timedelta(days=1),
                                'date_to': self.leave_date_to,
                                'holiday_status_id': self.env.ref('hr_holidays.holiday_status_unpaid').id,
                                'employee_id': self.employee_id.id,
                                'request_date_from': self.request_date_to + timedelta(days=1),
                                'request_date_to': self.leave_date_to,
                                'state': 'validate'}
                            self._constrains_for_leave_date_to()
                            unpaid_leave_id = self.env['hr.leave'].create(vals_for_unpaid_leave_request)
                            unpaid_leave_id.unpaid_leave_id = self.id
                            unpaid_leave_id.sudo()._onchange_leave_dates()
                            unpaid_leave_id.sudo()._onchange_request_parameters
                    else:
                        vals_for_clearance = {
                            'clearance_type': 'vacation',
                            'employee_id': self.employee_id.id,
                            'date_deliver_work': fields.date.today(),
                            'leave_request_id': self.id,
                            'work_delivered': "Legal Leave"
                        }
                        if not self.hr_clearance_id and self.leave_type_type == 'paid':
                            hr_have_clearance = self.env['hr.clearance'].create(vals_for_clearance)
                            self.hr_clearance_id = hr_have_clearance.id
                        if self.request_more_than_balance and not self.unpaid_leave_id:
                            vals_for_unpaid_leave_request = {
                                'date_from': self.request_date_to + timedelta(days=1),
                                'date_to': self.leave_date_to,
                                'holiday_status_id': self.env.ref('hr_holidays.holiday_status_unpaid').id,
                                'employee_id': self.employee_id.id,
                                'request_date_from': self.request_date_to + timedelta(days=1),
                                'request_date_to': self.leave_date_to,
                                'state': 'validate'}
                            self._constrains_for_leave_date_to()
                            unpaid_leave_id = self.env['hr.leave'].create(vals_for_unpaid_leave_request)
                            unpaid_leave_id.unpaid_leave_id = self.id
                            unpaid_leave_id.sudo()._onchange_leave_dates()
                            unpaid_leave_id.sudo()._onchange_request_parameters
                    if self.need_clearance:
                        self.write({'state': 'accountant'})
                        if not self.is_allocation:
                            allocation_request = self.env['hr.leave.allocation'].search(
                                [('is_annual_allocation', '=', True), ('employee_id', '=', self.employee_id.id),
                                 ('employee_id.active', '=', True), ('state', '=', 'validate'),
                                 ('holiday_type', '=', 'employee')], limit=1)
                            allocation_request.write({'number_of_days': allocation_request.number_of_days + float_round(
                                self.vacation_balance % 1, precision_digits=3)})
                            self.is_allocation = True
                    else:
                        self.write({'state': 'internal_audit_manager'})
                        if not self.is_allocation:
                            allocation_request = self.env['hr.leave.allocation'].search(
                                [('is_annual_allocation', '=', True), ('employee_id', '=', self.employee_id.id),
                                 ('employee_id.active', '=', True), ('state', '=', 'validate'),
                                 ('holiday_type', '=', 'employee')], limit=1)
                            allocation_request.write({'number_of_days': allocation_request.number_of_days + float_round(
                                self.vacation_balance % 1, precision_digits=3)})
                            self.is_allocation = True
                elif self.state == 'internal_audit_manager':
                    self.write({'state': 'finance_manager'})
                elif self.state == 'finance_manager':
                    self.write({'state': 'accountant'})
                elif self.state == 'accountant':
                    if self.need_clearance and not self.is_send_confirmation:
                        self.write({'state': 'internal_audit_manager', 'is_send_confirmation': True})
                    else:
                        self.write({'state': 'validate'})
                    if self.request_date_from < fields.Date.today():
                        self.employee_id.write({'state': 'on_leave', 'employee_state': 'on_leave', 'suspend_salary': True})
        elif self.holiday_status_id.leave_type == 'haj':
            if self.is_department_manager(employee_id):
                if self.state == 'draft':
                    self.write({'state': 'department_manager'})
                elif self.state == 'department_manager':
                    self.write({'state': 'hr_specialist'})
                elif self.state == 'hr_specialist':
                    self.write({'state': 'hr_manager'})
                elif self.state == 'hr_manager':
                    self.write({'state': 'validate'})
            elif self.is_other_department_employee(self.employee_id):
                if self.state == 'draft':
                    self.write({'state': 'department_manager'})
                elif self.state == 'department_manager':
                    self.write({'state': 'hr_specialist'})
                elif self.state == 'hr_specialist':
                    self.write({'state': 'hr_manager'})
                elif self.state == 'hr_manager':
                    self.write({'state': 'validate'})
            else:
                if self.state == 'draft':
                    self.write({'state': 'department_manager'})
                elif self.state == 'department_manager':
                    self.write({'state': 'hr_specialist'})
                elif self.state == 'hr_specialist':
                    self.write({'state': 'hr_manager'})
                elif self.state == 'hr_manager':
                    self.write({'state': 'validate'})
        elif self.holiday_status_id.leave_type == 'paid' and not self.need_clearance:
            if self.state == 'draft':
                self.write({'state': 'department_manager'})
            elif self.state == 'department_manager':
                self.write({'state': 'hr_specialist'})
            elif self.state == 'hr_specialist':
                self.write({'state': 'hr_manager'})
            elif self.state == 'hr_manager':
                if self.is_external_leave and self.employee_type == 'foreign':
                    note = ' عبارة عن قيمة الخروج والعودة لـ '
                    if self.name:
                        note = ' عبارة عن قيمة الخروج والعودة لـ ' + self.name,
                    on_employee_fair = False
                    if not self.is_external_leave and not self.is_has_ticket:
                        on_employee_fair = True
                    res = {
                        'request_for': self.request_for,
                        'travel_before_date': fields.date.today(),
                        'exit_return_type': 'one',
                        'note': note,
                        'on_employee_fair': on_employee_fair,
                        'employee_id': self.employee_id.id,
                        'leave_request_id': self.id
                    }
                    if not self.is_exit_entry_created:
                        hr_exit_return = self.env['hr.exit.return'].create(res)
                        self.hr_exit_return_id = hr_exit_return.id
                        self.is_exit_entry_created = True
                    vals_for_clearance = {
                        'clearance_type': 'vacation',
                        'employee_id': self.employee_id.id,
                        'date_deliver_work': fields.date.today(),
                        'leave_request_id': self.id,
                        'work_delivered': "Legal Leave"
                    }
                    if not self.hr_clearance_id and self.leave_type_type == 'paid':
                        hr_have_clearance = self.env['hr.clearance'].create(vals_for_clearance)
                        self.hr_clearance_id = hr_have_clearance.id

                self.write({'state': 'validate'})

        else:
            if self.is_department_manager(employee_id):
                if self.state == 'draft':
                    self.write({'state': 'vice_em'})
                elif self.state == 'vice_em':
                    self.write({'state': 'hr_specialist'})
                elif self.state == 'hr_specialist':
                    self.write({'state': 'hr_manager'})
                elif self.state == 'hr_manager':
                    self.write({'state': 'validate'})
            elif self.is_other_department_employee(self.employee_id):
                if self.state == 'draft':
                    self.write({'state': 'department_manager'})
                # elif self.state == 'department_supervisor':
                #     self.write({'state': 'department_manager'})
                elif self.state == 'department_manager':
                    self.write({'state': 'hr_specialist'})
                elif self.state == 'hr_specialist':
                    self.write({'state': 'hr_manager'})
                elif self.state == 'hr_manager':
                    self.write({'state': 'validate'})
            else:
                if self.state == 'draft':
                    self.write({'state': 'hr_specialist'})
                # elif self.state == 'branch_supervisor':
                #     self.write({'state': 'area_manager'})
                # elif self.state == 'area_manager':
                #     self.write({'state': 'branches_department_manager'})
                # elif self.state == 'branches_department_manager':
                #     self.write({'state': 'hr_specialist'})
                elif self.state == 'hr_specialist':
                    self.write({'state': 'hr_manager'})
                elif self.state == 'hr_manager':
                    self.write({'state': 'validate'})
        self.activity_update()
        self._create_resource_leave()
        return True

    def is_department_manager(self, employee_id):
        departments = self.env['hr.department'].search([("is_branch", "=", False)])
        for department in departments:
            if employee_id == department.manager_id.id:
                return True
        return False

    def is_other_department_employee(self, employee_id):
        return not employee_id.department_id.is_branch

    
    def compute_sheet(self):
        for rec in self:
            if rec.salary_payslip_id:
                rec.salary_start_date = str(fields.Date.from_string(rec.request_date_from) + relativedelta(day=1))
                rec.salary_end_date = str(fields.Date.from_string(rec.request_date_from) + relativedelta(days=-1))
                rec.salary_payslip_id.date_from = rec.salary_start_date
                rec.salary_payslip_id.date_to = rec.salary_end_date

                rec.salary_payslip_id.sudo().with_context(contract=True). \
                onchange_employee_id(str(fields.Date.from_string(rec.request_date_from) + relativedelta(day=1)),
                                     str(fields.Date.from_string(rec.request_date_from) + relativedelta(days=-1)),
                                     rec.employee_id.id, contract_id=rec.employee_id.contract_id.id)


                rec.salary_payslip_id.compute_sheet()
                return True

            slip_data = self.env['hr.payslip'].with_context(contract=True). \
                onchange_employee_id(str(fields.Date.from_string(rec.request_date_from) + relativedelta(day=1)),
                                     str(fields.Date.from_string(rec.request_date_from) + relativedelta(days=-1)),
                                     rec.employee_id.id, contract_id=rec.employee_id.contract_id.id)
            print('...........slip_data value............',slip_data['value'])
            for x in slip_data['value'].get('worked_days_line_ids'):
                print('.............x..........',x)
            res = {
                'employee_id': rec.employee_id.id,
                'leave_request_id': self.id,
                'name': 'Salary Slip For/' + rec.employee_id.name,
                'struct_id': slip_data['value'].get('struct_id'),
                'salary_payment_method': rec.employee_id.salary_payment_method,
                'contract_id': rec.employee_id.contract_id.id,
                'type': 'salary',
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': str(fields.Date.from_string(rec.request_date_from) + relativedelta(day=1)),
                'date_to': str(fields.Date.from_string(rec.request_date_from) + relativedelta(days=-1)),
            }
            allowance = self.env['hr.payslip'].create(res)
            allowance.compute_sheet()

            self.write({'salary_payslip_id': allowance.id, 'salary_start_date': allowance.date_from,
                        'salary_end_date': allowance.date_to})
        return True

    
    def salary_compute(self):
        for rec in self:
            # if rec.holiday_salary_payslip_id:
            #     rec.holiday_salary_payslip_id.unlink()
            rule = self.env['hr.salary.rule'].search([('in_holiday', '=', True)])
            slip_data = self.env['hr.payslip'].with_context(contract=True). \
                onchange_employee_id(str(fields.Date.from_string(rec.request_date_from)),
                                     str(fields.Date.from_string(rec.request_date_to)),
                                     rec.employee_id.id, contract_id=rec.employee_id.contract_id.id)
            allowance = False
            if not rec.holiday_salary_payslip_id:
                res = {
                    'employee_id': rec.employee_id.id,
                    'leave_request_id': self.id,
                    'name': 'Holiday/' + rec.employee_id.name,
                    'struct_id': slip_data['value'].get('struct_id'),
                    'salary_payment_method': rec.employee_id.salary_payment_method,
                    'contract_id': rec.employee_id.contract_id.id,
                    'type': 'holiday',
                    'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                    'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                    'date_from': str(fields.Date.from_string(rec.request_date_from)),
                    'date_to': str(
                        fields.Date.from_string(rec.request_date_to + timedelta(days=int(self.vacation_balance)))),
                    'bonus_ids': [(6, 0, rule.ids)],
                }
                allowance = self.env['hr.payslip'].create(res)
                allowance.sudo().with_context(contract=True). \
                onchange_employee_id(str(fields.Date.from_string(rec.request_date_from)),
                                     str(fields.Date.from_string(rec.request_date_to)),
                                     rec.employee_id.id, contract_id=rec.employee_id.contract_id.id)
            else:
                allowance = rec.holiday_salary_payslip_id
                pre_input_lines = allowance.input_line_ids
                rec.holiday_salary_start_date = str(fields.Date.from_string(rec.request_date_from))
                rec.holiday_salary_end_date = str(
                    fields.Date.from_string(rec.request_date_to + timedelta(days=int(self.vacation_balance))))
                allowance.date_from = rec.holiday_salary_start_date
                allowance.date_to = rec.holiday_salary_end_date
                allowance.sudo().with_context(contract=True). \
                onchange_employee_id(str(fields.Date.from_string(rec.request_date_from)),
                                     str(fields.Date.from_string(rec.request_date_to)),
                                     rec.employee_id.id, contract_id=rec.employee_id.contract_id.id)

            if allowance:
                allowance.sudo().onchange_employee_hr_leave()
                # allowance.compute_sheet()
                pre_input_lines = allowance.input_line_ids
                # allowance_lines = self.sudo().with_context({'leave_id': self.id})._get_payslip_lines(
                #     allowance.contract_id.ids, allowance.id,allowance.input_line_ids)
                allowance_lines = self.sudo().with_context({'leave_id': self.id})._get_payslip_lines(allowance)
                holiday_rules = rule.mapped('code')

                payslip_lines = []
                number = allowance.number or self.env['ir.sequence'].next_by_code('salary.slip')
                # for allowance_line in allowance_lines:
                #     if allowance_line['code'] in holiday_rules:
                #         payslip_lines.append(allowance_line)
                if allowance_lines:
                    allowance.line_ids.unlink()
                    lines = [(0, 0, line) for line in allowance_lines]
                    # _logger.info("pre_input_lines : " + str(pre_input_lines))
                    # _logger.info("pre_input_lines : " + str(pre_input_lines.ids))
                    allowance.write({'line_ids': lines, 'number': number})
                    # allowance.input_line_ids.unlink()
                    # allowance.input_line_ids = pre_input_lines.ids
                # if allowance.line_ids:
                #     filter_allowance_lines = allowance.line_ids.filtered(lambda l:l.code not in holiday_rules)
                #     if filter_allowance_lines:
                #         filter_allowance_lines.unlink()
                # allowance.compute_sheet()

                self.write({'holiday_salary_payslip_id': allowance.id, 'holiday_salary_start_date': allowance.date_from,
                            'holiday_salary_end_date': allowance.date_to})
                # allowance.action_payslip_done()
        return True

    def _get_payslip_lines(self,payslip):
        line_vals = []
        if payslip:
            if not payslip.contract_id:
                raise UserError(
                    _("There's no contract set on payslip %s for %s. Check that there is at least a contract set on the employee form.",
                      payslip.name, payslip.employee_id.name))

            localdict = self.env.context.get('force_payslip_localdict', None)
            if localdict is None:
                localdict = payslip._get_localdict()

            rules_dict = localdict['rules'].dict
            result_rules_dict = localdict['result_rules'].dict

            blacklisted_rule_ids = self.env.context.get('prevent_payslip_computation_line_ids', [])

            result = {}
            for rule in sorted(payslip.struct_id.rule_ids, key=lambda x: x.sequence):
                if rule.id in blacklisted_rule_ids:
                    continue
                localdict.update({
                    'result': None,
                    'result_qty': 1.0,
                    'result_rate': 100,
                    'result_name': False
                })
                if rule._satisfy_condition(localdict):
                    amount, qty, rate = rule._compute_rule(localdict)
                    # check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    # set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    result_rules_dict[rule.code] = {'total': tot_rule, 'amount': amount, 'quantity': qty}
                    rules_dict[rule.code] = rule
                    # sum the amount for its salary category
                    localdict = rule.category_id._sum_salary_rule_category(localdict, tot_rule - previous_amount)
                    # Retrieve the line name in the employee's lang
                    employee_lang = payslip.employee_id.sudo().address_home_id.lang
                    # This actually has an impact, don't remove this line
                    context = {'lang': employee_lang}
                    if localdict['result_name']:
                        rule_name = localdict['result_name']
                    elif rule.code in ['BASIC', 'GROSS', 'NET', 'DEDUCTION',
                                       'REIMBURSEMENT']:  # Generated by default_get (no xmlid)
                        if rule.code == 'BASIC':  # Note: Crappy way to code this, but _(foo) is forbidden. Make a method in master to be overridden, using the structure code
                            if rule.name == "Double Holiday Pay":
                                rule_name = _("Double Holiday Pay")
                            if rule.struct_id.name == "CP200: Employees 13th Month":
                                rule_name = _("Prorated end-of-year bonus")
                            else:
                                rule_name = _('Basic Salary')
                        elif rule.code == "GROSS":
                            rule_name = _('Gross')
                        elif rule.code == "DEDUCTION":
                            rule_name = _('Deduction')
                        elif rule.code == "REIMBURSEMENT":
                            rule_name = _('Reimbursement')
                        elif rule.code == 'NET':
                            rule_name = _('Net Salary')
                    else:
                        rule_name = rule.with_context(lang=employee_lang).name
                    # create/overwrite the rule in the temporary results
                    result[rule.code] = {
                        'sequence': rule.sequence,
                        'code': rule.code,
                        'name': rule_name,
                        'note': html2plaintext(rule.note) if not is_html_empty(rule.note) else '',
                        'salary_rule_id': rule.id,
                        'contract_id': localdict['contract'].id,
                        'employee_id': localdict['employee'].id,
                        'amount': amount,
                        'quantity': qty,
                        'rate': rate,
                        'slip_id': payslip.id,
                    }
            line_vals += list(result.values())
        return line_vals

    # @api.model
    # def _get_payslip_lines(self, contract_ids, payslip_id,input_line_ids):
    #
    #     def _sum_salary_rule_category(localdict, category, amount):
    #         if category.parent_id:
    #             localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
    #
    #         if category.code in localdict['categories'].dict:
    #             localdict['categories'].dict[category.code] += amount
    #         else:
    #             localdict['categories'].dict[category.code] = amount
    #
    #         return localdict
    #
    #     class BrowsableObject(object):
    #         def __init__(self, employee_id, dict, env):
    #             self.employee_id = employee_id
    #             self.dict = dict
    #             self.env = env
    #
    #         def __getattr__(self, attr):
    #             return attr in self.dict and self.dict.__getitem__(attr) or 0.0
    #
    #     class InputLine(BrowsableObject):
    #         """a class that will be used into the python code, mainly for usability purposes"""
    #
    #         def sum(self, code, from_date, to_date=None):
    #             if to_date is None:
    #                 to_date = fields.Date.today()
    #             self.env.cr.execute("""
    #                    SELECT sum(amount) as sum
    #                    FROM hr_payslip as hp, hr_payslip_input as pi
    #                    WHERE hp.employee_id = %s AND hp.state = 'done'
    #                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
    #                                 (self.employee_id, from_date, to_date, code))
    #             return self.env.cr.fetchone()[0] or 0.0
    #
    #     class WorkedDays(BrowsableObject):
    #         """a class that will be used into the python code, mainly for usability purposes"""
    #
    #         def _sum(self, code, from_date, to_date=None):
    #             if to_date is None:
    #                 to_date = fields.Date.today()
    #             self.env.cr.execute("""
    #                    SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
    #                    FROM hr_payslip as hp, hr_payslip_worked_days as pi
    #                    WHERE hp.employee_id = %s AND hp.state = 'done'
    #                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
    #                                 (self.employee_id, from_date, to_date, code))
    #             return self.env.cr.fetchone()
    #
    #         def sum(self, code, from_date, to_date=None):
    #             res = self._sum(code, from_date, to_date)
    #             return res and res[0] or 0.0
    #
    #         def sum_hours(self, code, from_date, to_date=None):
    #             res = self._sum(code, from_date, to_date)
    #             return res and res[1] or 0.0
    #
    #     class Payslips(BrowsableObject):
    #         """a class that will be used into the python code, mainly for usability purposes"""
    #
    #         def sum(self, code, from_date, to_date=None):
    #             if to_date is None:
    #                 to_date = fields.Date.today()
    #             self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
    #                            FROM hr_payslip as hp, hr_payslip_line as pl
    #                            WHERE hp.employee_id = %s AND hp.state = 'done'
    #                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
    #                                 (self.employee_id, from_date, to_date, code))
    #             res = self.env.cr.fetchone()
    #             return res and res[0] or 0.0
    #
    #     # we keep a dict with the result because a value can be overwritten by another rule with the same code
    #     result_dict = {}
    #     rules_dict = {}
    #     worked_days_dict = {}
    #     inputs_dict = {}
    #     blacklist = []
    #     payslip = self.env['hr.payslip'].browse(payslip_id)
    #     for worked_days_line in payslip.worked_days_line_ids:
    #         worked_days_dict[worked_days_line.code] = worked_days_line
    #     for input_line in input_line_ids:
    #         inputs_dict[input_line.code] = input_line
    #
    #     categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
    #     inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
    #     worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
    #     payslips = Payslips(payslip.employee_id.id, payslip, self.env)
    #     rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)
    #
    #     # _logger.info("BrowsableObject rules : " + str(rules))
    #
    #     baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days,
    #                      'inputs': inputs}
    #     # _logger.info("baselocaldict" + str(baselocaldict))
    #     # get the ids of the structures on the contracts and their parent id as well
    #     contracts = self.env['hr.contract'].browse(contract_ids)
    #     if len(contracts) == 1 and payslip.struct_id:
    #         structure_ids = list(set(payslip.struct_id._get_parent_structure().ids))
    #     else:
    #         structure_ids = contracts.get_all_structures()
    #     # get the rules of the structure and thier children
    #     rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
    #     # run the rules by sequence
    #     sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
    #     sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)
    #
    #     sorted_rules = sorted_rules.filtered(lambda l: l.in_holiday)
    #
    #     for contract in contracts:
    #         employee = contract.employee_id
    #         localdict = dict(baselocaldict, employee=employee, contract=contract)
    #         for rule in sorted_rules:
    #             key = rule.code + '-' + str(contract.id)
    #             localdict['result'] = None
    #             localdict['result_qty'] = 1.0
    #             localdict['result_rate'] = 100
    #             # check if the rule can be applied
    #             if rule._satisfy_condition(localdict) and rule.id not in blacklist:
    #                 # compute the amount of the rule
    #                 amount, qty, rate = rule._compute_rule(localdict)
    #                 # check if there is already a rule computed with that code
    #                 previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
    #                 if rule.per_day and worked_days.PAID100:
    #                     amount = (amount / WORK_DAY_PER_MONTH) * worked_days.PAID100.number_of_days
    #                 # set/overwrite the amount computed for this rule in the localdict
    #                 tot_rule = amount * qty * rate / 100.0
    #                 localdict[rule.code] = tot_rule
    #                 rules_dict[rule.code] = rule
    #                 # sum the amount for its salary category
    #                 localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
    #                 # create/overwrite the rule in the temporary results
    #                 result_dict[key] = {
    #                     'salary_rule_id': rule.id,
    #                     'contract_id': contract.id,
    #                     'name': rule.name,
    #                     'code': rule.code,
    #                     'category_id': rule.category_id.id,
    #                     'sequence': rule.sequence,
    #                     'appears_on_payslip': rule.appears_on_payslip,
    #                     'condition_select': rule.condition_select,
    #                     'condition_python': rule.condition_python,
    #                     'condition_range': rule.condition_range,
    #                     'condition_range_min': rule.condition_range_min,
    #                     'condition_range_max': rule.condition_range_max,
    #                     'amount_select': rule.amount_select,
    #                     'amount_fix': rule.amount_fix,
    #                     'amount_python_compute': rule.amount_python_compute,
    #                     'amount_percentage': rule.amount_percentage,
    #                     'amount_percentage_base': rule.amount_percentage_base,
    #                     'register_id': rule.register_id.id,
    #                     'amount': amount,
    #                     'employee_id': contract.employee_id.id,
    #                     'quantity': qty,
    #                     'rate': rate,
    #                 }
    #             else:
    #                 # blacklist this rule and its children
    #                 blacklist += [id for id, seq in rule._recursive_search_of_rules()]
    #
    #     return list(result_dict.values())

    #########################End Constraints Check######################################################################
    
    def action_create_ticket(self):
        if self.is_ticket_created:
            raise ValidationError(_("Sorry Ticket Already Created"))
        hr_ticket_request_type = self.env['hr.ticket.request.type'].search([('ticket_check', '=', True)], limit=1)
        vals = {
            'request_date': fields.date.today(),
            'employee_id': self.employee_id.id,
            'leave_request_id': self.id,
            'destination_id': self.hr_destination_id.id,
            'request_type': hr_ticket_request_type.id,
            'ticket_cost': hr_ticket_request_type.id,
            'ticket_date': fields.date.today(),
            'mission_check': False,
        }
        self.env['hr.ticket.request'].create(vals)
        self.write({'is_ticket_created': True})

    
    def get_ticket(self):
        for rec in self:
            rec.is_has_ticket = False
            diff_days = 0
            diff_month = 0
            if rec.holiday_status_id.leave_type == 'paid' and self.employee_type == 'foreign':
                tickets_date = rec.employee_id.contract_id.last_ticket_date or rec.employee_id.contract_id.date_start
                holiday_start = fields.Date.from_string(rec.request_date_from)
                ticket_date = fields.Date.from_string(tickets_date)
                if diff_days and diff_month:
                    diff_days = holiday_start - ticket_date
                    diff_month = (holiday_start.year - ticket_date.year) * 12 + holiday_start.month - ticket_date.month
                    if rec.employee_id.contract_id.contract_period == '12':
                        if int(diff_month) >= 11:
                            rec.is_has_ticket = True
                    elif rec.employee_id.contract_id.contract_period == '24':
                        if int(diff_month) >= 22:
                            rec.is_has_ticket = True
                    elif rec.employee_id.contract_id.contract_period == '36':
                        if int(diff_month) >= 33:
                            rec.is_has_ticket = True

    @api.depends('request_more_than_balance', 'request_date_to', 'request_date_from', 'holiday_status_id')
    def check_remaining_leaves(self):
        for rec in self:
            rec.is_remaining_leaves = False
            if rec.number_of_days_display > rec.remaining_leaves or rec.number_of_days_display > 0:
                rec.is_remaining_leaves = True

    @api.constrains('employee_id')
    def _constrains_for_employee_state(self):
        if self.employee_id.state not in ('on_job', 'trail_period') or self.employee_id.employee_state != 'on_job':
            raise UserError('You cannot create leave request if you are not on Job !')

    @api.constrains('leave_date_to', 'request_date_to')
    def _constrains_for_leave_date_to(self):
        if self.leave_date_to and self.leave_date_to <= self.request_date_to:
            raise ValidationError(_("New request end date must be greater than leave end date"))

    def _check_approval_update(self, state):
        pass
        # """ Check if target state is achievable. """
        # current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        # is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        #
        # for holiday in self:
        #     val_type = holiday.holiday_status_id.validation_type
        #     if state == 'confirm':
        #         continue
        # if state == 'draft':
        #     if holiday.employee_id != current_employee and not is_manager:
        #         raise UserError(_('Only a Leave Manager can reset other people leaves.'))
        #     continue

        # if not is_officer:
        #     raise UserError(_('Only a Leave Officer or Manager can approve or refuse leave requests.'))

        # if is_officer:
        # use ir.rule based first access check: department, members, ... (see security.xml)
        # holiday.check_access_rule('write')

        # if holiday.employee_id == current_employee and not is_manager:
        #     raise UserError(_('Only a Leave Manager can approve its own requests.'))

        # if (state == 'validate1' and val_type == 'both') or (state == 'validate' and val_type == 'manager'):
        #     manager = holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
        #     if (manager and manager != current_employee) and not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
        #         raise UserError(_('You must be either %s\'s manager or Leave manager to approve this leave') % (holiday.employee_id.name))
        #
        # if state == 'validate' and val_type == 'both':
        #     if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
        #         raise UserError(_('Only an Leave Manager can apply the second approval on leave requests.'))


class BsgInheritHrLeaveReport(models.Model):
    _inherit = 'hr.leave.report'
    holiday_status_id = fields.Many2one("hr.leave.type", string="Leave Type", readonly=True)
    state = fields.Selection(
        selection_add=[('hr_specialist', 'Hr Specialist'), ('hr_specialist', 'Hr Specialist'),
                       ('hr_manager', 'Hr Manager'),
                       ('branch_supervisor', 'Branch Supervisor'), ('department_supervisor', 'Department Supervisor'),
                       ('area_manager', 'Area Manager'), ('branches_department_manager', 'Branches Department Manager'),
                       ('department_manager', 'Department Manager'), ('vice_em', 'vice Execution Manager'),
                       ('internal_audit_manager', 'Internal Audit Manager'), ('accountant', 'Accountant'),
                       ('finance_manager', 'Finance Manager')])
