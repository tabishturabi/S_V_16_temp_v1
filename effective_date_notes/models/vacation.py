import uuid
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ReturnVaction(models.Model):
    _name = 'return.vacation'
    _inherit = ['mail.thread']
    _description = "Effective date Notes"
    _rec_name = "name"

    name = fields.Char(string='Reference No', readonly=False)
    created_date = fields.Datetime(string='Created Date', default=lambda self: fields.datetime.now(), track_visibility=True, readonly=True)

    @api.model
    def _default_my_employee_id(self):
        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        return self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])

    employee_id = fields.Many2one('hr.employee', default=_default_my_employee_id, required=True, track_visibility=True)
    manager_id = fields.Many2one('hr.employee', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Effective Date")
    mobile_phone = fields.Char(string='Mobile Number', required=False, track_visibility=True)
    employee_code = fields.Char(string='Employee ID', readonly=True)
    bsg_empiqama = fields.Many2one('hr.iqama', string='Employee Iqama ID', readonly=True)
    bsg_national_id = fields.Many2one('hr.nationality', string='Employee National ID', readonly=True)

    period = fields.Date(string='Period', track_visibility=True, readonly=True)
    date_from = fields.Date(string='From', track_visibility=True, readonly=True)
    date_to = fields.Date(string='To', track_visibility=True, readonly=True)

    return_date = fields.Date(string='Returning Date', default=lambda self: fields.date.today(), track_visibility=True, readonly=False, required=True)
    description = fields.Text(string="description", track_visibility=True, translate=True)
    reason = fields.Text(string="Reason For Delay", track_visibility=True, translate=True, readonly=False)
    reason_active = fields.Boolean(string="Reason Active", compute='_compute_hide')

    reason_approve = fields.Boolean(string="Reason Approve")

    is_driver = fields.Boolean(string="Is Driver")
    is_settlement = fields.Boolean(string="Is Including settlement ")

    
    @api.onchange('is_driver')
    def get_decision_is_driver(self):
        if self.is_driver == True:
            self.reason_approve = False
        else:
            self.reason_approve = True

    branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Branch Name', readonly=True)
    department_id = fields.Many2one('hr.department', string="Department", readonly=True)
    job_id = fields.Many2one('hr.job', string="Job Position", readonly=True)
    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('submitted', 'Submitted'),
                                                        ('tech_manager_approve', 'Technical Support Approve'),
                                                        ('approve', 'MNG APPROVE'),
                                                        # ('reject', 'MNG REFUSE'),
                                                        ('fin_approve', 'HR Super Approve'),
                                                        # ('fin_reject', 'HR Super Reject'),
                                                        ('hr_manager_approve', 'HR MNG Approve'),
                                                        # ('hr_manager_reject', 'HR MNG Reject'),
                                                        ('done', 'Done'), ('cancel', 'Cancelled')], default='draft',
                             track_visibility=True)

    active = fields.Boolean(string="Active", default=True, track_visibility=True)
    duration = fields.Char(string='Duration', readonly=True)
    days_delayed = fields.Char(string='Delayed (If Any)', compute='_compute_days', readonly=True)

    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    other_employee = fields.Boolean(string='Other Employee')

    @api.constrains('payslip_payroll_date', 'working_payroll_date')
    def _check_date(self):
        for date in self:
            if date.working_payroll_date and date.working_payroll_date < date.payslip_payroll_date:
                raise ValidationError(_('Can Not Be Start Payroll Date less then the Starting Working Date'))


    @api.constrains('start_payroll_date', 'return_date')
    def _check_payroll_date(self):
        for date in self:
            if date.start_payroll_date and date.start_payroll_date < date.return_date:
                raise ValidationError(_('Start Payroll Date Must be Greater and equal than Returning Date'))

    
    def attach_document(self):
        view_id = self.env.ref('effective_date_notes.view_attachment_return_vacation_form').id
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
            [('res_model', '=', 'return.vacation'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for upgrade_no in self:
            upgrade_no.attachment_number = attachment.get(upgrade_no.id, 0)

    
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('effective_date_notes.action_attachment_return_vacation')
        return res


    @api.depends('return_date', 'date_to')
    def _compute_days(self):
        for rec in self:
            rec.reason_active = False
            if rec.return_date and rec.date_to:
                delta = rec.return_date - rec.date_to
                if delta.days < 0:
                    raise ValidationError("days delayed can not be less than Zero: %s" % delta.days)
                if delta.days > 0:
                    rec.reason_active = True
                else:
                    rec.reason_active = False
                rec.days_delayed = str(delta.days) + ' days '

    @api.depends('reason_active')
    def _compute_hide(self):
        if str(self.days_delayed) > 0:
            self.reason = True
        else:
            self.reason = False

    
    @api.onchange('leave_type_id')
    def get_employee_leave_data(self):
        if not self.leave_type_id:
            self.date_from = False
            self.date_to = False
            self.duration = False
        if self.leave_type_id:
            self.date_from = self.leave_type_id.request_date_from
            self.date_to = self.leave_type_id.request_date_to
            self.duration = self.leave_type_id.number_of_days_display


    leave_type_id = fields.Many2one('hr.leave', string='Leave Type',  track_visibility=True, domain="[('employee_id','=', employee_id)]", required=True)
    is_annual = fields.Boolean(string="Is annual")

    sick_leave_type = fields.Many2one('hr.leave.type',string='Employee Joined the work after ', related="leave_type_id.holiday_status_id", required=False, track_visibility=True, readonly=True)
    emp_description = fields.Text(string="Description", track_visibility=True, translate=True)
    approve_debt_date = fields.Datetime(string='Approve Employee Dept. Date', track_visibility=True, readonly=True)
    emp_manager = fields.Many2one('hr.employee', string='Employee Dept. Manager', track_visibility=True, readonly=True)

    analytic_account = fields.Many2one('account.analytic.account', string='Analytic Account', readonly=True)
    salary_structure = fields.Many2one('hr.payroll.structure', store=True, string='Salary Structure', track_visibility=True, readonly=True)
    payroll_effect = fields.Selection(string="Payroll Effective Date",
                                      selection=[('start_first_time',
                                                  'The Employee Start Working in the same date & he will include in the payslip on the'),
                                                 ('start_after_transport',
                                                  'The employee start working date, day and he will include in the payroll payslip on the date')], default='start_first_time',
                                      track_visibility=True)

    
    @api.onchange('payroll_effect')
    def get_decision_payroll_effect_null(self):
        if self.payroll_effect == 'start_first_time':
            self.working_payroll_date = False
            self.payslip_payroll_date = False
        if self.payroll_effect == 'start_after_transport':
            self.start_payroll_date = False

    hr_description = fields.Text(string="Description", track_visibility=True, translate=True)
    hr_approve_date = fields.Datetime(string='Hr Supervisor Approve Date', track_visibility=True, readonly=True)
    hr_supervisor = fields.Many2one('hr.employee', string='Hr Supervisor Name', track_visibility=True, readonly=True)
    hr_manager_approve_date = fields.Datetime(string='Hr Manager Approve Date', track_visibility=True, readonly=True)
    hr_manager = fields.Many2one('hr.employee', string='Hr Manager Name', track_visibility=True, readonly=True)
    manager_description = fields.Text(string="Description", track_visibility=True, translate=True)
    salary_description = fields.Text(string="Description", track_visibility=True, translate=True)
    start_payroll_date = fields.Date(string='Start Payroll Date', track_visibility=True, readonly=False)
    working_payroll_date = fields.Date(string='Employee Start Working Date', track_visibility=True, readonly=False)
    payslip_payroll_date = fields.Date(string='Payroll Payslip Date', track_visibility=True, readonly=False)
    hr_salary_approve_date = fields.Datetime(string='Hr Salary Approve Date', track_visibility=True, readonly=True)
    hr_salary = fields.Many2one('hr.employee', string='Hr Salary Name', track_visibility=True, readonly=True)
    assignment_vehicle = fields.Selection(string="Assignment Vehicle",
                                      selection=[('assign_vehicle',
                                                  'Driver is assign to vehicle'),
                                                 ('not_assign_vehicle',
                                                  'Employee has not yet assign vehicle, because vehicle vehicle is not currently available') ], track_visibility=True)

    
    @api.onchange('is_driver')
    def get_assignment_vehicle_data(self):
        if self.is_driver == True:
            self.assignment_vehicle = 'assign_vehicle'
        else:
            self.assignment_vehicle = False

    assign_date = fields.Datetime(string='Assign Date', track_visibility=True, readonly=True)
    sticker_no = fields.Char(string='Sticker No', required=False, track_visibility=False, readonly=True)
    assignment_no = fields.Many2one('driver.assign', string='Assignment No',domain="[('assign_driver_id','=', employee_id)]", track_visibility=True, readonly=False)
    reason_not_assign = fields.Text(string="Notes", track_visibility=True, translate=True)
    assign_description = fields.Text(string="Description", track_visibility=True, translate=True)
    leave_type_idddd = fields.Many2one('hr.leave.type', string='Leave Typeeeee', track_visibility=True)

    
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
            self.is_driver = self.employee_id.is_driver
            self.leave_type_id = False
            data = self.env['hr.leave'].search([('employee_id', '=', self.employee_id.id)], limit=1)
            self.is_annual = data.holiday_status_id.is_annual

    @api.onchange('assignment_vehicle')
    def get_decision_number_data_null(self):
        if self.assignment_vehicle == 'assign_vehicle':
            self.reason_not_assign = False
        if self.assignment_vehicle == 'not_assign_vehicle':
            self.assignment_no = False
            self.assign_date = False
            self.sticker_no = False

    
    @api.onchange('assignment_no')
    def get_emp_assignment_no_data(self):
        if self.assignment_no:
            record = self.env['driver.assign'].search([('assign_driver_id', '=', self.employee_id.id)], limit=1)
            self.assign_date = record.assign_date
            self.sticker_no = record.fleet_vehicle_id.taq_number
        if not self.assignment_no:
            self.assign_date = False
            self.sticker_no = False

    
    def action_validate(self):
        self.state = 'submitted'

        MailTemplate = self.env.ref('effective_date_notes.vacation_mail_employee_manager_temp', False)
        for rec in self.employee_id:
            if rec.partner_id.email:
                MailTemplate.sudo().write(
                    {'email_to': str(self.manager_id.partner_id.email), 'email_from': str(rec.partner_id.email)})
                MailTemplate.sudo().send_mail(self.id, force_send=True)
        msg_id = self.env['mail.message'].search([('model', '=', 'return.vacation'), ('res_id', '=', self.id)])
        msg_id.unlink()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Your vacation Date Request Submitted To Manager ',
                'type': 'rainbow_man',
            }
        }

    
    def mng_approve(self):
        self.state = 'approve'

        MailTemplate = self.env.ref('effective_date_notes.vacation_mail_employee_manager_temp', False)

        email = self.env['res.users'].search([])
        notification_email = []
        for em in email:
            if em.has_group('effective_date_notes.vacation_reporting_hr_supervisor_group'):
                if self.manager_id.partner_id.email != em.email:
                    notification_email.append(em.email)

        for email_select in notification_email:
            print('email_to', email_select)
            print('email_from', self.manager_id.partner_id.email)
            MailTemplate.sudo().write(
                {'email_to': str(email_select), 'email_from': str(self.manager_id.partner_id.email)})
            MailTemplate.sudo().send_mail(self.id, force_send=True)
        msg_id = self.env['mail.message'].search([('model', '=', 'return.vacation'), ('res_id', '=', self.id)])
        msg_id.unlink()

        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        self.emp_manager = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
        self.approve_debt_date = fields.datetime.now()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'vacation Date Request Submitted To HR Supervisor For Approval',
                'type': 'rainbow_man',
            }
        }



    
    def mng_reject(self):
        self.state = 'draft'

    
    def finance_approve(self):
        self.state = 'fin_approve'

        MailTemplate = self.env.ref('effective_date_notes.vacation_mail_employee_manager_temp', False)

        email = self.env['res.users'].search([])
        notification_email = []
        for em in email:
            if em.has_group('effective_date_notes.vacation_reporting_hr_manager_group'):
                if self.manager_id.partner_id.email != em.email:
                    notification_email.append(em.email)

        for email_select in notification_email:
            print('email_to', email_select)
            print('email_from', self.manager_id.partner_id.email)
            MailTemplate.sudo().write(
                {'email_to': str(email_select), 'email_from': str(self.manager_id.partner_id.email)})
            MailTemplate.sudo().send_mail(self.id, force_send=True)
        msg_id = self.env['mail.message'].search([('model', '=', 'return.vacation'), ('res_id', '=', self.id)])
        msg_id.unlink()

        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        self.hr_supervisor = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
        self.hr_approve_date = fields.datetime.now()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'vacation Date Request Submitted To HR Manager For Approval',
                'type': 'rainbow_man',
            }
        }

    
    def finance_reject(self):
        self.state = 'submitted'
        self.start_payroll_date = False
        self.working_payroll_date = False
        self.payslip_payroll_date = False

    
    def tech_manager_approve(self):
        self.state = 'tech_manager_approve'

        MailTemplate = self.env.ref('effective_date_notes.vacation_mail_employee_manager_temp', False)

        email = self.env['res.users'].search([])
        notification_email = []
        for em in email:
            if em.has_group('effective_date_notes.vacation_reporting_employee_manager_group'):
                if self.manager_id.partner_id.email != em.email:
                    notification_email.append(em.email)

        for email_select in notification_email:
            print('email_to', email_select)
            print('email_from', self.manager_id.partner_id.email)
            MailTemplate.sudo().write(
                {'email_to': str(email_select), 'email_from': str(self.manager_id.partner_id.email)})
            MailTemplate.sudo().send_mail(self.id, force_send=True)
        msg_id = self.env['mail.message'].search([('model', '=', 'return.vacation'), ('res_id', '=', self.id)])
        msg_id.unlink()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'vacation Date Request Submitted To Manager For Approval',
                'type': 'rainbow_man',
            }
        }

    
    def mng_approve1(self):
        self.state = 'approve'

        MailTemplate = self.env.ref('effective_date_notes.vacation_mail_employee_manager_temp', False)

        email = self.env['res.users'].search([])
        notification_email = []
        for em in email:
            if em.has_group('effective_date_notes.vacation_reporting_hr_supervisor_group'):
                if self.manager_id.partner_id.email != em.email:
                    notification_email.append(em.email)

        for email_select in notification_email:
            print('email_to', email_select)
            print('email_from', self.manager_id.partner_id.email)
            MailTemplate.sudo().write(
                {'email_to': str(email_select), 'email_from': str(self.manager_id.partner_id.email)})
            MailTemplate.sudo().send_mail(self.id, force_send=True)
        msg_id = self.env['mail.message'].search([('model', '=', 'return.vacation'), ('res_id', '=', self.id)])
        msg_id.unlink()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'vacation Date Request Submitted to HR Supervisor for Approval',
                'type': 'rainbow_man',
            }
        }

    
    def mng_reject1(self):
        self.state = 'draft'

    
    def tech_manager_reject(self):
        self.state = 'draft'
        self.reason_not_assign = False

    
    def hr_manager_approve(self):
        self.state = 'hr_manager_approve'
        MailTemplate = self.env.ref('effective_date_notes.vacation_mail_employee_manager_temp', False)
        email = self.env['res.users'].search([])
        notification_email = []
        for em in email:
            if em.has_group('effective_date_notes.vacation_reporting_hr_salary_group'):
                if self.manager_id.partner_id.email != em.email:
                    notification_email.append(em.email)

        for email_select in notification_email:
            print('email_to', email_select)
            print('email_from', self.manager_id.partner_id.email)
            MailTemplate.sudo().write(
                {'email_to': str(email_select), 'email_from': str(self.manager_id.partner_id.email)})
            MailTemplate.sudo().send_mail(self.id, force_send=True)
        msg_id = self.env['mail.message'].search([('model', '=', 'return.vacation'), ('res_id', '=', self.id)])
        msg_id.unlink()

        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        self.hr_manager = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
        self.hr_manager_approve_date = fields.datetime.now()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'vacation Date Request Submitted To HR Salary For Approval',
                'type': 'rainbow_man',
            }
        }

    
    def hr_manager_reject(self):
        self.state = 'hr_manager_reject'

    return_count = fields.Integer('Number return vacation Date Request')

    def _compute_return_count_count(self):
        for record in self:
            record.return_count = self.env['return.vacation'].search_count(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'done')])

    
    def hr_salary_approve(self):
        self.state = 'done'
        self._compute_return_count_count()
        return_vaction = self.env['hr.employee'].search([('id', '=', self.employee_id.id)], limit=1)
        for rec in return_vaction:
            self.employee_id.return_count = self.return_count
            self.employee_id.suspend_salary = False
            self.employee_id.employee_state = 'on_job'
            if self.leave_type_id.holiday_status_id.is_annual and self.is_settlement  == True :
                self.employee_id.last_return_date = self.start_payroll_date if self.start_payroll_date else self.payslip_payroll_date

        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        self.hr_salary = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
        self.hr_salary_approve_date = fields.datetime.now()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'vacation Date Request Has Bean approved',
                'type': 'rainbow_man',
            }
        }

    
    def hr_salary_reject(self):
        self.state = 'fin_approve'

    @api.model
    def create(self, vals):
        res = super(ReturnVaction, self).create(vals)
        if self.env.user.user_branch_id.branch_no:
            res.name = 'RFVN' + self.env.user.user_branch_id.branch_no + self.env['ir.sequence'].next_by_code(
                'return.vacation')
        else:
            res.name = 'RFVN' + self.env['ir.sequence'].next_by_code('return.vacation')
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
