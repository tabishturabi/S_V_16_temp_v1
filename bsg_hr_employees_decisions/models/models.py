# -*- coding: utf-8 -*-

import uuid
import hashlib
import hmac
import base64
from werkzeug.urls import url_encode
from odoo import api, exceptions, fields, models, tools, _
from odoo.exceptions import UserError,ValidationError
from datetime import date


class EmployeesDescions(models.Model):
    _name = 'employees.appointment'
    _inherit = 'mail.thread'
    _description='Employee Decisions'
    _rec_name ='employee_name'

    
    def name_get(self):
        result = []
        for appointment in self:
            sequence_number = appointment.employee_name.name + " - " + (appointment.sequence_number or " ")
            result.append((appointment.id, sequence_number))
        return result

    sequence_number = fields.Char(string='Sequence NO',readonly=True,track_visibility='always')
    employee_name = fields.Many2one('hr.employee', string='Employee Name', required=True, track_visibility='always')
    employee_id = fields.Char(related='employee_name.driver_code',store=True,string='Employee ID',track_visibility='always')
    old_manager = fields.Many2one('hr.employee',store=True, string='Manager',readonly=True,track_visibility='always')
    old_company = fields.Many2one('res.company',string='Company',store=True,readonly=True,track_visibility='always')
    old_branch_name = fields.Many2one('bsg_branches.bsg_branches',store=True,readonly=True, string='Branch Name',track_visibility='always')
    old_emp_department = fields.Many2one('hr.department',store=True,readonly=True, string='Department',track_visibility='always')
    old_job_position = fields.Many2one('hr.job',store=True, string='Job Position',readonly=True,track_visibility='always')
    old_analytic_account = fields.Many2one('account.analytic.account',store=True,string='Analytic Account',readonly=True,track_visibility='always')
    old_salary_structure = fields.Many2one('hr.payroll.structure',store=True,string='Sallary Structure',readonly=True,track_visibility='always')
    old_wage = fields.Monetary(string='Wage',readonly=True,track_visibility='always')
    old_work_nature = fields.Monetary(string='Work Nature',readonly=True,track_visibility='always')
    old_fixed_additional =fields.Monetary(string='Fixed Additional',readonly=True,track_visibility='always')
    old_food = fields.Monetary(string='Food',readonly=True,track_visibility='always')
    old_fixed_deduction = fields.Monetary(string='Fixed Deduction',readonly=True,track_visibility='always')
    decision_date = fields.Date(string='Decision Date',default=fields.Date.today(),track_visibility='always',required=True)
    decision_type=fields.Selection([('appoint_employee','Decision to appoint an employee'),
                                    ('transfer_employee','Decision to transfer an employee'),
                                    ('assign_employee','Decision to assign an employee'),
                                    ('extend', 'Employee Decision (Extend Trail Period)'),
                                    ('change', 'Employee Decision (Change Employee Data)')],
                                   string='Decision Type', track_visibility='always',default='appoint_employee',required=True)
    decision_action_type = fields.Selection([('employee_action', 'Employee Action'),
                                      ('decision_action', 'Decision Action')],
                                     string='Decision Action Type')
    current_company = fields.Many2one('res.company', string='Company',track_visibility='always',readonly=True)
    current_branch_name = fields.Many2one('bsg_branches.bsg_branches', string='Branch Name',track_visibility='always')
    current_emp_department = fields.Many2one('hr.department', string='Department',track_visibility='always')
    current_job_position = fields.Many2one('hr.job', string='Job Position',track_visibility='always')
    current_manager = fields.Many2one(related='current_emp_department.manager_id',readonly=True, string='Manager',track_visibility='always')
    current_analytic_account = fields.Many2one('account.analytic.account',string='Analytic Account',track_visibility='always')
    current_salary_structure = fields.Many2one('hr.payroll.structure', string='Sallary Structure',track_visibility='always')
    current_wage = fields.Monetary(string='Wage', track_visibility='always')
    current_work_nature = fields.Monetary(string='Work Nature', track_visibility='always')
    current_fixed_additional = fields.Monetary(string='Fixed Additional', track_visibility='always')
    current_food = fields.Monetary(string='Food', track_visibility='always')
    current_fixed_deduction = fields.Monetary(string='Fixed Deduction', track_visibility='always')
    from_date = fields.Date(string='From',track_visibility='always',default=fields.date.today())
    to_date = fields.Date(string='To',track_visibility='always')
    currency_id = fields.Many2one('res.currency', string='Currency',readonly=True,
                                  default=lambda self:self.env['res.currency'].search([('name','=','SR')]))
    attach_docs = fields.Many2many('ir.attachment', attachment=True, string='ATTACH DOCUMENT')
    description = fields.Text(string='Description',track_visibility='always')
    decision_report_comments = fields.Many2one('decisions.report.comments',string='Decision Report Comments',track_visibility='always')
    refusal_reason=fields.Text(string='Reason',readonly=True,track_visibility='always')
    print_date = fields.Date(string='Print Date', readonly=True, default=fields.date.today())
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'),
                               ('refused', 'Refused')], default='draft',track_visibility='always')
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    partner_id = fields.Many2one(related='employee_name.partner_id',string='Partner')
    active = fields.Boolean(string="Active", default=True, track_visibility=True)

    user_id = fields.Many2one('res.users',string='Users')
    access_url = fields.Char(
        'Portal Access URL', compute='_compute_access_url',
        help='Customer Portal URL')
    access_token = fields.Char('Security Token', copy=False)
    parent_current_dept = fields.Char(string='parent current department',compute='_get_parent_dept')
    parent_old_dept = fields.Char(string='parent old department',compute='_get_parent_dept')
    old_bonus_cls_ids = fields.Many2many('employee.bonus.classification','old_decision_bonus_rel','old_decision_id','old_bonus_id',string='Bonus Classification',readonly=True)
    current_bonus_cls_ids = fields.Many2many('employee.bonus.classification','current_decision_bonus_rel','current_decision_id','current_bonus_id',string='Bonus Classification')

    # to display the warning from specific model
    access_warning = fields.Text("Access warning", compute="_compute_access_warning")
    effective_request_number = fields.Integer(string='Effective Requests',compute='compute_effective_number')
    clearance_number = fields.Integer(string='Clearances',compute='compute_clearance_number')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


    @api.constrains('current_wage')
    def _validate_current_wage(self):
        for rec in self:
            if rec.decision_type == 'transfer_employee':
                if rec.current_wage <= 0.00:
                    raise ValidationError(_('Wage must be more than zero.'))

    def action_get_effective_request_view(self):
        return {
            'name': 'Effective Date Request',
            'domain': [('decision_number', '=', self.id)],
            'res_model': 'effect.request',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    @api.model
    def update_employee_decisions(self):
        ''' This method is called from a cron job. '''
        decision_ids = self.env['employees.appointment'].search([('decision_type','=','change'),('state','=','approved'),('decision_date','=',date.today())])
        if decision_ids:
            for decision_id in decision_ids:
                if decision_id:
                    self.env['hr.employee'].browse(decision_id.employee_name.id).write({
                        'branch_id': decision_id.current_branch_name.id,
                        'department_id': decision_id.current_emp_department.id,
                        'job_id': decision_id.current_job_position.id,
                        'parent_id': decision_id.current_manager.id,
                        'company_id': decision_id.current_company.id,
                        'bonus_classification_ids': [(6, 0, decision_id.current_bonus_cls_ids.ids)]
                    })
                    running_emp_contract = self.env['hr.contract'].search(
                        [('employee_id', '=', decision_id.employee_name.id), ('state', '=', 'open')], limit=1)
                    if running_emp_contract:
                        self.env['hr.contract'].browse(running_emp_contract.id).write({
                            'analytic_account_id': decision_id.current_analytic_account.id,
                            'struct_id': decision_id.current_salary_structure.id,
                            'wage': decision_id.current_wage,
                            'work_nature_allowance': decision_id.current_work_nature,
                            'fixed_add_allowance': decision_id.current_fixed_additional,
                            'food_allowance': decision_id.current_food,
                            'fixed_deduct_amount': decision_id.current_fixed_deduction,
                        })



    
    def compute_effective_number(self):
        for rec in self:
            count = rec.env['effect.request'].search_count([('decision_number', '=', rec.id)])
            rec.effective_request_number = count

    
    def compute_clearance_number(self):
        for rec in self:
            count = rec.env['hr.clearance'].search_count([('decision_number', '=', rec.id)])
            rec.clearance_number = count

    def action_get_clearance_view(self):
        return {
            'name': 'Employee Clearance',
            'domain': [('decision_number', '=', self.id)],
            'res_model': 'hr.clearance',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }


    @api.onchange('decision_type')
    def get_decision_report_comments(self):
        comments_id = self.env['decisions.report.comments'].search([('decision_type','=',self.decision_type)],limit=1)
        if comments_id:
            self.decision_report_comments = comments_id.id
        self.employee_name=False
        if self.decision_type == 'appoint_employee':
            return {'domain': {'employee_name': [('state', 'in', ['complete_data'])]}}
        else:
            return {'domain': {'employee_name': [('state', 'in', ['trail_period','on_job'])]}}


    @api.constrains('from_date')
    def validate_from_date(self):
        if self.decision_type == 'assign_employee' and self.from_date < self.decision_date:
            raise ValidationError('From Date must be greater than or equal to decision date')



    @api.onchange('current_emp_department')
    def onchange_department(self):
        self.current_job_position = False




    @api.depends('old_emp_department','current_emp_department')
    def _get_parent_dept(self):
        for rec in self:
            rec.parent_current_dept = False
            rec.parent_old_dept = False
            if rec.current_emp_department:
                current_dept = rec.current_emp_department.complete_name
                current_dept_split = current_dept.split('/')
                rec.parent_current_dept =current_dept_split[0]
            if rec.old_emp_department:
                old_dept = rec.old_emp_department.complete_name
                old_dept_split = old_dept.split('/')
                rec.parent_old_dept = old_dept_split[0]
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('code')
        user = self.env['res.users'].sudo().search([('id', '=', self.env.user.id)])
        branch_number = user.user_branch_id.branch_no
        vals['sequence_number'] = "DE%s%s" % (branch_number, seq)
        return super(EmployeesDescions, self).create(vals)

    @api.onchange('employee_name')
    def get_employee_info(self):
        if self.employee_name:
            if self.decision_type == 'appoint_employee':
                appoint_contract_id = self.env['hr.contract'].search([('employee_id', '=', self.employee_name.id)],
                                                                     order='date_start desc', limit=1)
                if appoint_contract_id:
                    self.update({
                        'old_manager': self.employee_name.parent_id,
                        'old_branch_name': self.employee_name.branch_id,
                        'old_emp_department': self.employee_name.department_id,
                        'old_job_position': self.employee_name.job_id,
                        'old_company': self.employee_name.company_id,
                        'old_salary_structure': appoint_contract_id.structure_type_id.default_struct_id.id,
                        'old_analytic_account': appoint_contract_id.analytic_account_id.id,
                        'old_wage': appoint_contract_id.wage,
                        'old_work_nature': appoint_contract_id.work_nature_allowance,
                        'old_fixed_additional': appoint_contract_id.fixed_add_allowance,
                        'old_food': appoint_contract_id.food_allowance,
                        'old_fixed_deduction': appoint_contract_id.fixed_deduct_amount,
                        'old_bonus_cls_ids': self.employee_name.bonus_classification_ids,
                        'current_branch_name': self.employee_name.branch_id,
                        'current_emp_department': self.employee_name.department_id,
                        'current_job_position': self.employee_name.job_id,
                        'current_company': self.employee_name.company_id,
                        'current_analytic_account': appoint_contract_id.analytic_account_id.id
                    })
                else:
                    raise UserError(_('This employee has no contract'))

            else:
                contract_id = self.env['hr.contract'].search(
                    [('employee_id', '=', self.employee_name.id), ('state', '=', 'open')])
                if contract_id:
                    self.update({
                        'old_manager': self.employee_name.parent_id,
                        'old_branch_name': self.employee_name.branch_id,
                        'old_emp_department': self.employee_name.department_id,
                        'old_job_position': self.employee_name.job_id,
                        'old_company': self.employee_name.company_id,
                        'old_salary_structure': contract_id.structure_type_id.default_struct_id.id,
                        'old_analytic_account': contract_id.analytic_account_id.id,
                        'old_wage': contract_id.wage,
                        'old_work_nature': contract_id.work_nature_allowance,
                        'old_fixed_additional': contract_id.fixed_add_allowance,
                        'old_food': contract_id.food_allowance,
                        'old_fixed_deduction': contract_id.fixed_deduct_amount,
                        'old_bonus_cls_ids': self.employee_name.bonus_classification_ids,
                        'current_company': self.employee_name.company_id,
                        'current_salary_structure': contract_id.structure_type_id.default_struct_id.id,
                        'current_wage': contract_id.wage,
                        'current_work_nature': contract_id.work_nature_allowance,
                        'current_fixed_additional': contract_id.fixed_add_allowance,
                        'current_food': contract_id.food_allowance,
                        'current_fixed_deduction': contract_id.fixed_deduct_amount,
                    })
                else:
                    raise UserError(_('This employee has no contract in running state'))

    
    def action_submit_manager(self):
        self.state = 'submitted'
        MailTemplate = self.env.ref('bsg_hr_employees_decisions.mail_employees_decisions_temp', False)
        for rec in self.employee_name:
            if rec.partner_id.email:
                MailTemplate.sudo().write(
                    {'email_to': str(self.old_manager.partner_id.email), 'email_from': str(rec.partner_id.email)})
                MailTemplate.sudo().send_mail(self.id, force_send=True)
        msg_id = self.env['mail.message'].search([('model', '=', 'employees.appointment'), ('res_id', '=', self.id)])
        msg_id.unlink()
        return True

    
    def action_approve(self):
        if self.state == 'submitted':
            contract_id = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_name.id), ('state', '=', 'open')])
            if self.decision_type=='appoint_employee':
                # if contract_id:
                #     self.env['hr.contract'].browse(contract_id.id).write({
                #         'date_start': self.decision_date
                #     })
                # self.env['hr.employee'].browse(self.employee_name.id).write({
                #     'bsgjoining_date': self.decision_date,
                # })
                self.env['effect.request'].create({
                    'from_hr': True,
                    'employee_id': self.employee_name.id,
                    'manager_id':self.current_manager.id,
                    'company_id':self.current_company.id,
                    'branch_id':self.current_branch_name.id,
                    'department_id':self.current_emp_department.id,
                    'job_id':self.current_job_position.id,
                    'mobile_phone':self.employee_name.mobile_phone,
                    'employee_code':self.employee_name.employee_code,
                    'bsg_empiqama':self.employee_name.bsg_empiqama.id,
                    'bsg_national_id':self.employee_name.bsg_national_id.id,
                    'analytic_account':self.employee_name.contract_id.analytic_account_id.id,
                    'salary_structure':self.employee_name.contract_id.struct_id.id,
                    'notice_type': 'start_first_time',
                    'decision_number': self.id,
                    'decision_date': self.decision_date,
                    'working_date': self.decision_date
                })
            elif self.decision_type == 'transfer_employee':
                # if contract_id:
                #     self.env['hr.contract'].browse(contract_id.id).write({
                #         'struct_id': self.current_salary_structure.id,
                #         'wage': self.current_wage,
                #         'work_nature_allowance': self.current_work_nature,
                #         'fixed_add_allowance': self.current_fixed_additional,
                #         'food_allowance': self.current_food,
                #         'fixed_deduct_amount': self.current_fixed_deduction,
                #     })
                self.env['effect.request'].create({
                    'from_hr': True,
                   'employee_id': self.employee_name.id,
                    'manager_id':self.current_manager.id,
                    'company_id':self.current_company.id,
                    'branch_id':self.current_branch_name.id,
                    'department_id':self.current_emp_department.id,
                    'job_id':self.current_job_position.id,
                   'mobile_phone': self.employee_name.mobile_phone,
                   'employee_code': self.employee_name.employee_code,
                   'bsg_empiqama': self.employee_name.bsg_empiqama.id,
                   'bsg_national_id': self.employee_name.bsg_national_id.id,
                   'analytic_account': self.employee_name.contract_id.analytic_account_id.id,
                   'salary_structure': self.employee_name.contract_id.structure_type_id.default_struct_id.id,
                   'notice_type': 'start_after_transport',
                   'decision_number': self.id,
                   'decision_date': self.decision_date,
                   'working_date': self.decision_date
                })

                self.env['hr.clearance'].create({
                    'employee_id': self.employee_name.id,
                    'company_id': self.old_company.id,
                    'department_id': self.old_emp_department.id,
                    'job_id': self.old_job_position.id,
                    'decision_number': self.id,
                    'clearance_type': 'transfer',
                })

            self.state = 'approved'
    def action_reset_draft(self):
        if self.state == 'submitted':
            self.state = 'draft'

    def action_send_mail(self):
        # template_id = self.env.ref('bsg_hr_employees_decisions.employee_decisions_email_template').id
        # self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = self.env.ref('bsg_hr_employees_decisions.employee_decisions_email_template', False)
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        # self.env['ir.attachment'].browse(self.id).write({
        #     'report_doc':True
        # })
        # self.action_generate_attachment()
        ctx = {
            'default_model': 'employees.appointment',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id and template_id.id or False,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def _compute_access_warning(self):
        for mixin in self:
            mixin.access_warning = ''

    
    def _compute_access_url(self):
        for record in self:
            record.access_url = '#'

    def _portal_ensure_token(self):
        """ Get the current record access token """
        if not self.access_token:
            # we use a `write` to force the cache clearing otherwise `return self.access_token` will return False
            self.sudo().write({'access_token': str(uuid.uuid4())})
        return self.access_token


    
    def get_base_url(self):
        """Get the base URL for the current model.

        Defined here to be overriden by website specific models.
        The method has to be public because it is called from mail templates.
        """
        self.ensure_one()
        return self.env['ir.config_parameter'].sudo().get_param('web.base.url')

    def _get_share_url(self, redirect=False, signup_partner=False, pid=None):
        """
        Build the url of the record  that will be sent by mail and adds additional parameters such as
        access_token to bypass the recipient's rights,
        signup_partner to allows the user to create easily an account,
        hash token to allow the user to be authenticated in the chatter of the record portal view, if applicable
        :param redirect : Send the redirect url instead of the direct portal share url
        :param signup_partner: allows the user to create an account with pre-filled fields.
        :param pid: = partner_id - when given, a hash is generated to allow the user to be authenticated
            in the portal chatter, if any in the target page,
            if the user is redirected to the portal instead of the backend.
        :return: the url of the record with access parameters, if any.
        """
        self.ensure_one()
        params = {
            'model': self._name,
            'res_id': self.id,
        }
        if hasattr(self, 'access_token'):
            params['access_token'] = self._portal_ensure_token()
        if pid:
            params['pid'] = pid
            params['hash'] = self._sign_token(pid)
        if signup_partner and hasattr(self, 'employee_name.partner_id') and self.employee_name.partner_id:
            params.update(self.employee_name.partner_id.signup_get_auth_param()[self.employee_name.partner_id.id])

        return '%s?%s' % ('/mail/view' if redirect else self.access_url, url_encode(params))

    
    def _notify_get_groups(self, message, groups):
        access_token = self._portal_ensure_token()
        customer = self.employee_name.partner_id

        if access_token and customer:
            additional_params = {
                'access_token': self.access_token,
            }
            additional_params.update(customer.signup_get_auth_param()[customer.id])
            access_link = self._notify_get_action_link('view', **additional_params)

            new_group = [
                ('portal_customer', lambda pdata: pdata['id'] == customer.id, {
                    'has_button_access': False,
                    'button_access': {
                        'url': access_link,
                        'title': _('View %s') % self.env['ir.model']._get(message.model).display_name,
                    },
                })
            ]
        else:
            new_group = []
        return super(EmployeesDescions, self)._notify_get_groups(message, new_group + groups)

    
    def get_access_action(self, access_uid=None):
        """ Instead of the classic form view, redirect to the online document for
        portal users or if force_website=True in the context. """
        self.ensure_one()

        user, record = self.env.user, self
        if access_uid:
            try:
                record.check_access_rights('read')
                record.check_access_rule("read")
            except exceptions.AccessError:
                return super(EmployeesDescions, self).get_access_action(access_uid)
            user = self.env['res.users'].sudo().browse(access_uid)
            record = self.sudo(user)
        if user.share or self.env.context.get('force_website'):
            try:
                record.check_access_rights('read')
                record.check_access_rule('read')
            except exceptions.AccessError:
                if self.env.context.get('force_website'):
                    return {
                        'type': 'ir.actions.act_url',
                        'url': record.access_url,
                        'target': 'self',
                        'res_id': record.id,
                    }
                else:
                    pass
            else:
                return {
                    'type': 'ir.actions.act_url',
                    'url': record._get_share_url(),
                    'target': 'self',
                    'res_id': record.id,
                }
        return super(EmployeesDescions, self).get_access_action(access_uid)

    @api.model
    def action_share(self):
        action = self.env.ref('portal.portal_share_action').read()[0]
        action['context'] = {'active_id': self.env.context['active_id'],
                             'active_model': self.env.context['active_model']}
        return action

    
    def _sign_token(self, pid):
        """Generate a secure hash for this record with the email of the recipient with whom the record have been shared.

        This is used to determine who is opening the link
        to be able for the recipient to post messages on the document's portal view.

        :param str email:
            Email of the recipient that opened the link.
        """
        self.ensure_one()
        secret = self.env["ir.config_parameter"].sudo().get_param(
            "database.secret")
        token = (self.env.cr.dbname, self.access_token, pid)
        return hmac.new(secret.encode('utf-8'), repr(token).encode('utf-8'), hashlib.sha256).hexdigest()

    
    def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        """
            Get a portal url for this model, including access_token.
            The associated route must handle the flags for them to have any effect.
            - suffix: string to append to the url, before the query string
            - report_type: report_type query string, often one of: html, pdf, text
            - download: set the download query string to true
            - query_string: additional query string
            - anchor: string to append after the anchor #
        """
        self.ensure_one()
        url = self.access_url + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self._portal_ensure_token(),
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url


    # 
    # def action_print_report(self):
    #     return self.env.ref('bsg_hr_employees_decisions.employee_decisions_report_pdf_id').report_action(self)

    
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_hr_employees_decisions.action_attachment')
        return res

    
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'employees.appointment'), ('res_id', 'in', self.ids),('name','!=','Employee Decision_Report.pdf')], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for decision in self:
            decision.attachment_number = attachment.get(decision.id, 0)


class MailComposeInhert(models.TransientModel):
    _inherit = 'mail.compose.message'

    
    def send_mail(self, auto_commit=False):
        context = self._context
        # TODO TDE: clean that brole one day
        res = super(MailComposeInhert, self).send_mail(auto_commit=auto_commit)
        if self.model == 'employees.appointment' and context.get('active_ids'):
           rec_names = self.partner_ids.mapped('name')
           names = ','.join(rec_names)
           attachments = self.attachment_ids.ids
           msg = _(
               """<div class="o_thread_message_content">
                   <p>Employee Decision Email</p>
                   <ul class="o_mail_thread_message_tracking">
                   <li>Subject : <span>{subject}</span></li>
                   <li>Recipients : <span>{names}</span></li>
                   <li>Body : <span>{body}</span></li>
                   </ul>
                   </div>
                   """.format(
                   subject=self.subject,
                   names=names,
                   body = self.body
               )
           )
           self.env['employees.appointment'].browse(self.res_id).message_post(body=msg)
        return res


















