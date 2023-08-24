import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
import pandas as pd
import numpy as np
import psycopg2 as pg
import pandas.io.sql as psql
import getpass
import uuid
from odoo import models, fields, api, _
from num2words import num2words

from odoo.exceptions import UserError
from odoo.exceptions import Warning, ValidationError
from odoo.tools import config
import base64
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from ummalqura.hijri_date import HijriDate



def get_date(days_count, years, months, days):
    if days_count <= 0:
        return years, months, days
    elif days_count >= 365:
        years += 1
        days_count = days_count - 365
        return get_date(days_count, years, months, days)
    elif days_count >= 30:
        months += 1
        days_count = days_count - 30
        return get_date(days_count, years, months, days)
    else:
        days = days + days_count
        days_count = days_count - days
        return get_date(days_count, years, months, days)


class EmployeeService(models.Model):
    _name = 'employee.service'
    _inherit = ['mail.thread']
    _description = "Employee Service"
    _rec_name = "name"

    name = fields.Char(string='Name', readonly=False)
    date = fields.Date(string='Entry Date', default=fields.Date.context_today, track_visibility=True,
                           readonly=True)
    exit_date = fields.Datetime(string='Exiting Date', track_visibility=True, readonly=True)
    validate_date = fields.Datetime(string='Validate Date', track_visibility=True, readonly=True)
    line_ids = fields.One2many('service.line', 'line_id',track_visibility='always')

    def get_default_employee(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        return employee_id

    other_employee = fields.Boolean(string="Other Employee")
    employee_id = fields.Many2one('hr.employee', default=get_default_employee, required=True, track_visibility=True)
    manager_id = fields.Many2one('hr.employee', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Housing")
    mobile_phone = fields.Char(string='Mobile Number', required=False, track_visibility=True, readonly=True)
    branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Branch Name', readonly=True)
    department_id = fields.Many2one('hr.department', string="Department", readonly=True)
    job_id = fields.Many2one('hr.job', string="Job Position", readonly=True)
    description = fields.Text(string="Description", track_visibility=True, translate=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", readonly=True)
    analytic_tag_ids = fields.Many2many('account.account.tag', string="Analytic Tags", track_visibility='always',
                                        readonly=True)
    active = fields.Boolean(string="Active", default=True, track_visibility=True)
    state = fields.Selection(string="State", selection=[('draft', 'Draft'),
                                                        ('direct_manager', 'Direct Manager'),
                                                        ('hr_specialist', 'HR Specialist'),
                                                        ('hr_supervisor', 'HR Supervisor'),
                                                        ('top_management_secretary', 'Top Management Secretary'),
                                                        ('waiting_finance', 'Waiting Finance'),
                                                        ('done', 'Done'),
                                                        ('cancel', 'Cancelled')], default='draft',
                             track_visibility=True)
    employee_readonly = fields.Boolean(string='Employee Readonly')
    employee_code = fields.Char(string='Employee ID', readonly=True)
    bsg_empiqama = fields.Many2one('hr.iqama', string='Employee Iqama ID', readonly=True)
    bsg_national_id = fields.Many2one('hr.nationality', string='Employee National ID', readonly=True)
    bsg_totalyears = fields.Char(string='Total Years/Days	', readonly=True)
    bsg_job_pos = fields.Char(string='Iqama Job Position', readonly=True)
    date1 = fields.Date(string='Housing', compute='_compute_date1_count', store=True)
    service_type = fields.Many2one('service.type', string='Service Type', readonly=False, required=True)
    service_name = fields.Selection([('salary_intro_letter', 'Salary Introduction Letter'), ('letter_of_authority', 'Letter of Authority'), ('salary_transfer_letter', 'Salary Transfer Letter'), ('experience_certificate', 'Experience Certificate'), ('other', 'Other')],related="service_type.service_name",string="Service Name")
    service_to = fields.Char(string='Service To', readonly=False)
    # account_no = fields.Char(string='Account No', readonly=False)
    reason = fields.Text(string="Reason", track_visibility=True, translate=True, required=True)
    cancel_reason = fields.Text(string="Cancel Reason", track_visibility=True)
    refusal_reason = fields.Text(string="Refusal Reason", track_visibility=True)
    certification = fields.Boolean(string="Certification From The Chamber of Commerce", track_visibility=True)
    performance = fields.Selection(string="Employee Performance Appraisal", selection=[
        ('excellent', 'Excellent'),
        ('v_good', 'Very Good'),
        ('good', 'Good'),
        ('pathological', 'Pathological'),
        ('week', 'Week')], track_visibility=True)
    emp_description = fields.Text(string="Description", track_visibility=True, translate=True)
    approve_debt_date = fields.Datetime(string='Approve Employee Dept. Date', track_visibility=True, readonly=True)
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
    start_payroll_date = fields.Date(string='Start Payroll Date', track_visibility=True, readonly=False)
    working_payroll_date = fields.Date(string='Employee Start Working Date', track_visibility=True, readonly=False)
    payslip_payroll_date = fields.Date(string='Payroll Payslip Date', track_visibility=True, readonly=False)
    hr_description = fields.Text(string="Description", track_visibility=True, translate=True)
    hr_approve_date = fields.Datetime(string='Hr Supervisor Approve Date', track_visibility=True, readonly=True)
    hr_supervisor = fields.Many2one('hr.employee', string='Hr Supervisor Name', track_visibility=True, readonly=True)
    manager_description = fields.Text(string="Description", track_visibility=True, translate=True)
    hr_manager_approve_date = fields.Datetime(string='Hr Manager Approve Date', track_visibility=True, readonly=True)
    hr_manager = fields.Many2one('hr.employee', string='Hr Manager Name', track_visibility=True, readonly=True)
    salary_description = fields.Text(string="Description", track_visibility=True, translate=True)
    hr_salary_approve_date = fields.Datetime(string='Hr Salary Approve Date', track_visibility=True, readonly=True)
    hr_salary = fields.Many2one('hr.employee', string='Hr Salary Name', track_visibility=True, readonly=True)
    is_ceo = fields.Boolean(string="CEO Approval", default=False, track_visibility=True)
    is_deputy = fields.Boolean(string="Deputy CEO Approval", default=False, track_visibility=True)
    bsgjoining_date = fields.Date(string='Joining Date', readonly=True)
    nationality_id = fields.Many2one('res.country', string='Nationality', track_visibility=True, readonly=True)


    days_count = fields.Char(string='Days', compute='_compute_days')
    letter_language = fields.Selection( [('arabic', 'Arabic'), ('english', 'English')],default='arabic',string="Letter Language",required=True)
    cost = fields.Float(string="Cost")
    account_debit_id = fields.Many2one('account.account', string="Account Debit", track_visibility=True,readonly=True)
    account_journal_id = fields.Many2one('account.journal', string="Account Journal", track_visibility=True,readonly=True)
    account_move_id = fields.Many2one('account.move', string="Account Move", track_visibility=True,readonly=True)

    
    def print_service_request_report(self):
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'employee.service',
            'form': data,
        }
        report = self.env.ref('employee_service.employee_service_report').report_action(self,data=datas)
        return report


    def _get_hijri_date(self,service_date):
        service_hijri_date = HijriDate.get_hijri_date(service_date)
        return service_hijri_date

    def _get_leaving_date(self,service_id):
        leaving_day = ""
        termination_id = self.env["hr.termination"].search([('employee_id','=',service_id.employee_id.id),('state','=','10')],limit=1)
        if termination_id:
            leaving_day = termination_id.final_work_date
        return leaving_day

    def get_user_lang(self):
        lang_id = 0
        user_id = self.env['res.users'].search([('id', '=', self._uid)])
        if user_id.lang == 'en_US':
            lang_id = 1
        return lang_id

    def _get_deductions_rules(self):
        deductions_rules=[]
        rule_ids = self.env['hr.salary.rule'].search([('category_id.code','=','DED')])
        for rule_id in rule_ids:
            deductions_rules.append(rule_id.code)
        return deductions_rules
    def _compute_days(self):
        for rec in self:
            rec.days_count = ""
            if rec.date and rec.bsgjoining_date:
                delta = rec.date - rec.bsgjoining_date
                year, month, day = get_date(int(delta.days), 0, 0, 0)
                rec.days_count = "{0} Year {1} Months {2} Days".format(year,month,day)

    
    @api.onchange('service_type')
    def get_service_type_data(self):
        if self.service_type:
            self.is_ceo = self.service_type.is_ceo
            self.is_deputy = self.service_type.is_deputy

    ceo_description = fields.Text(string="Description", track_visibility=True, translate=True)
    ceo_approve_date = fields.Datetime(string='CEO Approval Date	', track_visibility=True, readonly=True)
    ceo = fields.Many2one('hr.employee', string='CEO Approval Name', track_visibility=True, readonly=True)
    deputy_description = fields.Text(string="Description", track_visibility=True, translate=True)
    deputy_approve_date = fields.Datetime(string='Deputy CEO Approval Date', track_visibility=True, readonly=True)
    deputy = fields.Many2one('hr.employee', string='Deputy CEO Approval Name', track_visibility=True, readonly=True)

    admin_group = fields.Boolean(string="Admin Group", default=False, track_visibility=True, store=False, compute='_compute_readonly')
    user_create_check = fields.Boolean(string="User Create Check",compute="_get_user_create_check")


    def _get_user_create_check(self):
        for rec in self:
            if rec.create_uid.id == rec.env.user.id:
                rec.user_create_check = True
            else:
                rec.user_create_check = False
                
    def _get_hijri_date(self,service_date):
        service_hijri_date = HijriDate.get_hijri_date(service_date)
        return service_hijri_date

    def get_user_lang(self):
        lang_id = 0
        user_id = self.env['res.users'].search([('id', '=', self._uid)])
        if user_id.lang == 'en_US':
            lang_id = 1
        return lang_id

    # 
    # def print_service_request_report(self):
    #     [data] = self.read()
    #     datas = {
    #         'ids': [],
    #         'model': 'employee.service',
    #         'form': data,
    #     }
    #     report = self.env.ref('employee_service.employee_service_report').report_action(self, data=datas)
    #     return report
    
    def _get_leaving_date(self,service_id):
        leaving_day = ""
        termination_id = self.env["hr.termination"].search([('employee_id','=',service_id.employee_id.id),('state','=','10')],limit=1)
        if termination_id:
            leaving_day = termination_id.final_work_date
        return leaving_day


    @api.depends('manager_id')
    def _compute_readonly(self):
        for rec in self:
            rec.admin_group = False
            if rec.manager_id:
                if rec.manager_id.partner_id:
                    user = rec.env['res.users'].search([('partner_id','=',rec.manager_id.partner_id.id)])
                    if len(user) == 1:
                        if user.has_group('employee_service.employee_manager_service_group') and rec.env.user.has_group('employee_service.employee_manager_service_group'):
                            if user.id == rec.env.user.id:
                                rec.admin_group = True

    
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('You Can Delete Record Only In Draft State'))
        return super(EmployeeService, self).unlink()



    
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
            self.nationality_id = self.employee_id.country_id
            self.bsgjoining_date = self.employee_id.bsgjoining_date
            iqama = self.env['hr.iqama'].search([('bsg_employee', '=', self.employee_id.id)], limit=1)
            for iq in iqama:
                self.bsg_job_pos = iq.bsg_job_pos
            self.analytic_account = self.employee_id.contract_id.analytic_account_id
            self.salary_structure = self.employee_id.contract_id.struct_id
            data = self.employee_id.line_ids
            salary_list = []
            for rec in data:
                salary_list.append(self.line_ids.create({
                    'name': rec.name,
                    'total': rec.total,
                }).id)

            self.line_ids = [(6, 0, salary_list)]

    
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('employee_service.action_attachment')
        return res

    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')

    
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'employee.service'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for upgrade_no in self:
            upgrade_no.attachment_number = attachment.get(upgrade_no.id, 0)


    
    def action_validate(self):
        for rec in self:
            if rec.state == 'top_management_secretary':
                employee_service_account_data = self.env.ref('employee_service.employee_service_account_data')
                if not employee_service_account_data.account_id or not employee_service_account_data.journal_id:
                    raise ValidationError(_("Please Set Account/Journal in Configuration First"))
                service_account_id_debit = employee_service_account_data.account_id or False
                service_journal_id = employee_service_account_data.journal_id or False
                rec.account_debit_id = service_account_id_debit
                rec.account_journal_id = service_journal_id
            if rec.state == 'waiting_finance':
                if not rec.account_journal_id or not rec.account_debit_id or rec.cost <= 0:
                    raise ValidationError(
                        _("Please Set Account/Journal in Configuration First also cost must be greater than zero"))
                amount = rec.cost
                move_id = self.env['account.move'].with_context(check_move_validity=False).create({
                    'ref': rec.employee_id.name,
                    'date': datetime.today(),
                    'journal_id': rec.account_journal_id.id,
                    'state': 'draft',
                    'line_ids': [(0, 6, {'name': rec.employee_id.name + _('/Service re-entry'),
                                         'due_date': datetime.today(),
                                         'bsg_branches_id': self.employee_id.branch_id.id,
                                         'department_id': self.employee_id.department_id.id,
                                         'account_id': rec.account_journal_id.default_account_id.id,
                                         'debit': 0.0,
                                         'credit': amount,
                                         }),
                                 (0, 6, {'name': rec.employee_id.name + _('/Service re-entry'),
                                         'due_date': datetime.today(),
                                         'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id,
                                         'bsg_branches_id': self.employee_id.branch_id.id,
                                         'department_id': self.employee_id.department_id.id,
                                         'account_id': rec.account_debit_id.id,
                                         'debit': amount,
                                         'credit': 0.0,
                                         })]})
                # rec.employee_id.write({'ex_return_date':rec.to_date})
                rec.write({'account_move_id': move_id.id})
                move_id.action_post()
            if rec.service_type.service_name == 'salary_intro_letter':
                if rec.certification:
                    if rec.state == 'draft':
                        rec.state = 'hr_specialist'
                    elif rec.state == 'hr_specialist':
                        rec.state = 'top_management_secretary'
                    elif rec.state == 'top_management_secretary':
                        rec.state = 'waiting_finance'
                    elif rec.state == 'waiting_finance':
                        rec.state = 'done'
                else:
                    if rec.state == 'draft':
                        rec.state = 'hr_specialist'
                    elif rec.state == 'hr_specialist':
                        rec.state = 'done'
            elif rec.service_type.service_name == 'letter_of_authority':
                if rec.certification:
                    if rec.state == 'draft':
                        rec.state = 'direct_manager'
                    elif rec.state == 'direct_manager':
                        rec.state = 'hr_specialist'
                    elif rec.state == 'hr_specialist':
                        rec.state = 'hr_supervisor'
                    elif rec.state == 'hr_supervisor':
                        rec.state = 'top_management_secretary'
                    elif rec.state == 'top_management_secretary':
                        rec.state = 'waiting_finance'
                    elif rec.state == 'waiting_finance':
                        rec.state = 'done'
                else:
                    if rec.state == 'draft':
                        rec.state = 'direct_manager'
                    elif rec.state == 'direct_manager':
                        rec.state = 'hr_specialist'
                    elif rec.state == 'hr_specialist':
                        rec.state = 'hr_supervisor'
                    elif rec.state == 'hr_supervisor':
                        rec.state = 'done'
            elif rec.service_type.service_name == 'salary_transfer_letter':
                if rec.state == 'draft':
                    rec.state = 'hr_specialist'
                elif rec.state == 'hr_specialist':
                    rec.state = 'hr_supervisor'
                elif rec.state == 'hr_supervisor':
                    rec.state = 'done'
            elif rec.service_type.service_name == 'experience_certificate':
                if rec.state == 'draft':
                    rec.state = 'direct_manager'
                elif rec.state == 'direct_manager':
                    rec.state = 'hr_specialist'
                elif rec.state == 'hr_specialist':
                    rec.state = 'done'
            elif rec.service_type.service_name == 'other':
                if rec.certification:
                    if rec.state == 'draft':
                        rec.state = 'direct_manager'
                    elif rec.state == 'direct_manager':
                        rec.state = 'hr_specialist'
                    elif rec.state == 'hr_specialist':
                        rec.state = 'top_management_secretary'
                    elif rec.state == 'top_management_secretary':
                        rec.state = 'waiting_finance'
                    elif rec.state == 'waiting_finance':
                        rec.state = 'done'
                else:
                    if rec.state == 'draft':
                        rec.state = 'direct_manager'
                    elif rec.state == 'direct_manager':
                        rec.state = 'hr_specialist'
                    elif rec.state == 'hr_specialist':
                        rec.state = 'done'

        # MailTemplate = self.env.ref('employee_service.submit_service_mail_manager_approve_temp', False)
        # for rec in self.employee_id:
        #     if rec.partner_id.email:
        #         MailTemplate.sudo().write(
        #             {'email_to': str(self.manager_id.partner_id.email), 'email_from': str(rec.partner_id.email)})
        #         MailTemplate.sudo().send_mail(self.id, force_send=True)
        # msg_id = self.env['mail.message'].search([('model', '=', 'employee.service'), ('res_id', '=', self.id)])
        # msg_id.unlink()
        #
        # return {
        #     'effect': {
        #         'fadeout': 'slow',
        #         'message': 'Employee Service Request Submitted To Direct Manager ',
        #         'type': 'rainbow_man',
        #     }
        # }

    # 
    # def mng_approve(self):
    #     self.state = 'approve'
    #     MailTemplate = self.env.ref('employee_service.mng_service_mail_manager_approve_temp', False)
    #     email = self.env['res.users'].search([])
    #     notification_email = []
    #     for em in email:
    #         if em.has_group('employee_service.employee_hr_supervisor_service_group'):
    #             if self.manager_id.partner_id.email != em.email:
    #                 notification_email.append(em.email)
    #     for email_select in notification_email:
    #         print('email_to', email_select)
    #         print('email_from', self.manager_id.partner_id.email)
    #         MailTemplate.sudo().write(
    #             {'email_to': str(email_select), 'email_from': str(self.manager_id.partner_id.email)})
    #         MailTemplate.sudo().send_mail(self.id, force_send=True)
    #     msg_id = self.env['mail.message'].search([('model', '=', 'employee.service'), ('res_id', '=', self.id)])
    #     msg_id.unlink()
    #     user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
    #                                                         company_id=self.env.user.company_id.id).search(
    #         [('id', '=', self.env.uid)])
    #     self.emp_manager = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
    #     self.approve_debt_date = fields.datetime.now()
    #
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Employee Service Approved By Employee Manager ',
    #             'type': 'rainbow_man',
    #         }
    #     }
    #
    # 
    # def mng_reject(self):
    #     self.state = 'draft'
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Employee Service Rejected By Employee Manager ',
    #             'type': 'rainbow_man',
    #         }
    #     }

    # 
    # def mng_approve1(self):
    #     self.state = 'approve'
    #     MailTemplate = self.env.ref('employee_service.mng_service_mail_manager_approve_temp', False)
    #     email = self.env['res.users'].search([])
    #     notification_email = []
    #     for em in email:
    #         if em.has_group('employee_service.employee_hr_supervisor_service_group'):
    #             if self.manager_id.partner_id.email != em.email:
    #                 notification_email.append(em.email)
    #     for email_select in notification_email:
    #         print('email_to', email_select)
    #         print('email_from', self.manager_id.partner_id.email)
    #         MailTemplate.sudo().write(
    #             {'email_to': str(email_select), 'email_from': str(self.manager_id.partner_id.email)})
    #         MailTemplate.sudo().send_mail(self.id, force_send=True)
    #     msg_id = self.env['mail.message'].search([('model', '=', 'employee.service'), ('res_id', '=', self.id)])
    #     msg_id.unlink()
    #     user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
    #                                                         company_id=self.env.user.company_id.id).search(
    #         [('id', '=', self.env.uid)])
    #     self.emp_manager = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
    #     self.approve_debt_date = fields.datetime.now()
    #
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Employee Service Approved By Employee Manager ',
    #             'type': 'rainbow_man',
    #         }
    #     }
    #
    # 
    # def mng_reject1(self):
    #     self.state = 'draft'
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Employee Service Rejected By Employee Manager ',
    #             'type': 'rainbow_man',
    #         }
    #     }
    #
    # 
    # def finance_approve(self):
    #     self.state = 'fin_approve'
    #     MailTemplate = self.env.ref('employee_service.finance_service_mail_manager_approve_temp', False)
    #     email = self.env['res.users'].search([])
    #     notification_email = []
    #     for em in email:
    #         if em.has_group('employee_service.employee_hr_manager_service_group'):
    #             if self.manager_id.partner_id.email != em.email:
    #                 notification_email.append(em.email)
    #
    #     for email_select in notification_email:
    #         print('email_to', email_select)
    #         print('email_from', self.manager_id.partner_id.email)
    #         MailTemplate.sudo().write(
    #             {'email_to': str(email_select), 'email_from': str(self.manager_id.partner_id.email)})
    #         MailTemplate.sudo().send_mail(self.id, force_send=True)
    #     msg_id = self.env['mail.message'].search([('model', '=', 'employee.service'), ('res_id', '=', self.id)])
    #     msg_id.unlink()
    #
    #     user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
    #                                                         company_id=self.env.user.company_id.id).search(
    #         [('id', '=', self.env.uid)])
    #     self.hr_supervisor = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
    #     self.hr_approve_date = fields.datetime.now()
    #
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Employee Service Approved By Employee HR Supervisor ',
    #             'type': 'rainbow_man',
    #         }
    #     }
    #
    # 
    # def finance_reject(self):
    #     self.state = 'submitted'
    #     self.start_payroll_date = False
    #     self.working_payroll_date = False
    #     self.payslip_payroll_date = False
    #
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Employee Service Rejected By Employee HR Supervisor ',
    #             'type': 'rainbow_man',
    #         }
    #     }
    #
    # 
    # def hr_manager_approve(self):
    #     if self.is_deputy == True:
    #         self.state = 'hr_manager_approve'
    #         MailTemplate = self.env.ref('employee_service.hr_manager1_service_mail_manager_approve_temp', False)
    #         email = self.env['res.users'].search([])
    #         notification_email = []
    #         for em in email:
    #             if em.has_group('employee_service.employee_hr_deputy_ceo_approve_group'):
    #                 if self.manager_id.partner_id.email != em.email:
    #                     notification_email.append(em.email)
    #
    #         for email_select in notification_email:
    #             print('email_to', email_select)
    #             print('email_from', self.manager_id.partner_id.email)
    #             MailTemplate.sudo().write(
    #                 {'email_to': str(email_select), 'email_from': str(self.manager_id.partner_id.email)})
    #             MailTemplate.sudo().send_mail(self.id, force_send=True)
    #         msg_id = self.env['mail.message'].search([('model', '=', 'employee.service'), ('res_id', '=', self.id)])
    #         msg_id.unlink()
    #
    #     if self.is_ceo == True:
    #         self.state = 'deputy'
    #         MailTemplate = self.env.ref('employee_service.hr_manager_service_mail_manager_approve_temp', False)
    #         email = self.env['res.users'].search([])
    #         notification_email = []
    #         for em in email:
    #             if em.has_group('employee_service.employee_hr_ceo_approve_group'):
    #                 if self.manager_id.partner_id.email != em.email:
    #                     notification_email.append(em.email)
    #
    #         for email_select in notification_email:
    #             print('email_to', email_select)
    #             print('email_from', self.manager_id.partner_id.email)
    #             MailTemplate.sudo().write(
    #                 {'email_to': str(email_select), 'email_from': str(self.manager_id.partner_id.email)})
    #             MailTemplate.sudo().send_mail(self.id, force_send=True)
    #         msg_id = self.env['mail.message'].search([('model', '=', 'employee.service'), ('res_id', '=', self.id)])
    #         msg_id.unlink()
    #
    #     if self.is_deputy and self.is_ceo == True:
    #         self.state = 'hr_manager_approve'
    #
    #     user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
    #                                                         company_id=self.env.user.company_id.id).search(
    #         [('id', '=', self.env.uid)])
    #     self.hr_manager = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
    #     self.hr_manager_approve_date = fields.datetime.now()
    #
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Employee Service Approved By Employee HR Manager ',
    #             'type': 'rainbow_man',
    #         }
    #     }
    #
    # 
    # def hr_manager_reject(self):
    #     self.state = 'approve'
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Employee Service Rejected By Employee HR Manager ',
    #             'type': 'rainbow_man',
    #         }
    #     }
    #
    # 
    # def deputy_approve(self):
    #     self.state = 'done'
    #
    #     self._compute_service_count()
    #     service = self.env['hr.employee'].search([('id', '=', self.employee_id.id)], limit=1)
    #     for rec in service:
    #         rec.service_count = self.service_count
    #
    #
    #     user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
    #                                                         company_id=self.env.user.company_id.id).search(
    #         [('id', '=', self.env.uid)])
    #     self.deputy = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
    #     self.deputy_approve_date = fields.datetime.now()
    #
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Employee Service Approved By Deputy CEO ',
    #             'type': 'rainbow_man',
    #         }
    #     }
    #
    # 
    # def deputy_reject(self):
    #     self.state = 'deputy'
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Employee Service Reject By Deputy CEO ',
    #             'type': 'rainbow_man',
    #         }
    #     }

    service_count = fields.Integer('Number Service Request')

    def _compute_service_count(self):
        for record in self:
            record.service_count = self.env['employee.service'].search_count([('employee_id', '=', self.employee_id.id), ('state', '=', 'done')])
    #
    # 
    # def ceo_approve(self):
    #     self.state = 'done'
    #
    #     self._compute_service_count()
    #     service = self.env['hr.employee'].search([('id', '=', self.employee_id.id)], limit=1)
    #     for rec in service:
    #         rec.service_count = self.service_count
    #
    #     user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
    #                                                         company_id=self.env.user.company_id.id).search(
    #         [('id', '=', self.env.uid)])
    #     self.ceo = self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])
    #     self.ceo_approve_date = fields.datetime.now()
    #
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Employee Service Approved By CEO ',
    #             'type': 'rainbow_man',
    #         }
    #     }
    #
    # 
    # def ceo_reject(self):
    #     self.state = 'draft'
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Employee Service Reject By CEO ',
    #             'type': 'rainbow_man',
    #         }
    #     }

    @api.model
    def create(self, vals):
        res = super(EmployeeService, self).create(vals)
        if self.env.user.user_branch_id.branch_no:
            res.name = 'ESR' + self.env.user.user_branch_id.branch_no + self.env['ir.sequence'].next_by_code(
                'employee.service')
        else:
            res.name = 'ESR' + self.env['ir.sequence'].next_by_code('employee.service')
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


class EmployeeServiceLine(models.Model):
    _name = 'service.line'

    line_id = fields.Many2one('employee.service', required=False, track_visibility=True)
    total = fields.Float(string='Total')
    name = fields.Char(string='Name')

    
    def get_arabic_total_word(self, total):
        word = num2words(float("%.2f" % total), lang='ar')
        word = word.title()
        warr = str(("%.2f" % total)).split('.')
        ar = ' ريال' if str(warr[1]) == '00' else ' هلله'
        rword = str(word).replace(',', ' ريال و ') + ar
        rword = str(rword).replace('ريال و ', 'فاصلة')
        return rword

# class HrLeaveServiceInherit(models.Model):
#     _inherit = 'hr.leave'
#
#     leave_req_action = fields.Boolean(string='Leave Request Action?')

class ResCompanyInherit(models.Model):
    """"""
    _inherit = 'res.company'

    chairman_id = fields.Many2one("hr.employee", string="Chairman Of Board")
