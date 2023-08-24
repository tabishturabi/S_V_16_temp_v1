# -*- coding: utf-8 -*-
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrClearance(models.Model):
    """"""
    _name = 'hr.clearance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'
    _description = "Clearance"



    def get_default_employee(self):
        employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
        return employee_id

    from_hr_department = fields.Boolean(string="Other Employee")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    employee_id = fields.Many2one('hr.employee',string="Employee Name",default=get_default_employee)
    department_id = fields.Many2one("hr.department", related="employee_id.department_id", string="Department")
    job_id = fields.Many2one("hr.job", related="employee_id.job_id", string="Job Position")
    leave_request_id = fields.Many2one('hr.leave', string="Leave Request")
    start_of_vacation = fields.Date(related="leave_request_id.request_date_from", string="Start Of Vacation")
    end_of_vacation = fields.Date(related="leave_request_id.request_date_to", string="End Of Vacation")
    date = fields.Date(string="Request Date",readonly=True, default=fields.Date.today(),required=True)
    date_deliver_work = fields.Date(string="Delivering Work Date",required=True,default=fields.Date.today())
    work_delivered = fields.Text(string="Reason Of Clearance")
    clearance_type = fields.Selection([('vacation','Vacation Clearance'),('transfer','Transfer Clearance'),('final','Final Clearance')],default='vacation')
    # state = fields.Selection([('draft','Draft'),('department_manager','Department Manager'),('technical_support','Technical Support'),('replacement_approval',' Replacement Approval'),
    #                           ('internal_auditor','Internal Auditor'),('finance_manager','Finance Manager'),
    #                           ('hr_salary_accountant','HR Salary Accountant'),('done','Done'),('cancel','Cancelled')],string='State',required=True,default='draft',track_visibility='onchange')
    state = fields.Selection(
        [('draft', 'Draft'), ('branch_supervisor', 'Branch Supervisor'), ('direct_manager', 'Direct Manager'),
         ('done', 'Done')], string='State',
        required=True, default='draft', track_visibility='onchange')
    bank_attachment_id = fields.Many2many('ir.attachment', string='Bank Attach')
    bank_comments = fields.Text(string="Bank Reasons")
    refuse_reason = fields.Text(string="Refuse Reasons",track_visibility='onchange')
    cancel_reason = fields.Text(string="Cancel Reasons",track_visibility='onchange')
    termination_id = fields.Many2one('hr.termination',string="Termination")
    replace_by_user_check = fields.Boolean(string="Replace By User",compute="compute_replace_by_user")
    manager_login_check = fields.Boolean(string="Is Manager?",compute="compute_manager_user")
    decision_number = fields.Many2one('employees.appointment',string='Decision Number',readonly=True)
    submit_check = fields.Boolean(string="Submit Check",compute="get_submit_check")
    custody_count = fields.Integer(string="Custodies", compute="_get_custody_count")

    # @api.multi
    @api.onchange('termination_id')
    def onchange_termination_id(self):
        if self.termination_id and self.termination_id.employee_id:
            self.employee_id = self.termination_id.employee_id.id
        hr_clearance_termination_ids = self.env['hr.clearance'].search([('termination_id','!=',False)]).mapped('termination_id')
        if len(hr_clearance_termination_ids) > 0:
            domain = [('id', 'not in', hr_clearance_termination_ids.ids)]
        else:
            domain = [(1, '=', 1)]
        return {'domain': {'termination_id': domain}}

    def _get_custody_count(self):

        """"""
        for rec in self:
            rec.custody_count = self.env["custody.request"].search_count([('employee_id', '=', rec.employee_id.id),
                                                                          ('state', '=', "assign")])

    def action_get_custody(self):
        # This function is action to view employee custodies
        custodies = self.env["custody.request"].search([('employee_id', '=', self.employee_id.id),
                                                        ('state', '=', "assign")])
        return {
            'name': '{} Custodies'.format(self.employee_id.name),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'custody.request',
            'domain': [('employee_id', 'in', custodies.mapped('employee_id.id'))]
        }

    def get_submit_check(self):
        for rec in self:
            if rec.create_uid.id == rec.env.user.id or rec.env.user.has_group('bsg_hr.group_branch_supervisor') or rec.env.user.has_group('bsg_hr.group_department_manager'):
                rec.submit_check = True
            else:
                rec.submit_check = False

    # @api.multi
    @api.onchange('from_hr_department')
    def get_employee_domain(self):
        if self.from_hr_department:
            if self.env.user.has_group('bsg_hr.group_hr_specialist') or self.env.user.has_group('bsg_hr.group_hr_manager'):
                return {'domain': {'employee_id': [('state', 'in', ['on_job', 'trail_period']), ('employee_state', 'in', ['on_job'])]}}
            elif self.env.user.has_group('bsg_hr.group_department_manager'):
                return {'domain': {'employee_id': [('parent_id', 'in', self.env.user.employee_ids.ids),
                                                   ('state', 'in', ['on_job', 'trail_period']),
                                                   ('employee_state', 'in', ['on_job'])]}}
            else:
                self.employee_id = self.env.user.employee_ids
                return {'domain': {
                    'employee_id': [('user_id', '=', self.env.user.id), ('state', 'in', ['on_job', 'trail_period']),
                                    ('employee_state', 'in', ['on_job'])]}}
        else:
            self.employee_id = self.env.user.employee_ids
            return {'domain': {'employee_id': [('user_id', '=', self.env.user.id)]}}


    @api.depends('employee_id')
    def compute_manager_user(self):
        for rec in self:
            if rec.employee_id.parent_id.user_id == rec.env.user:
                rec.manager_login_check = True
            else:
                rec.manager_login_check = False



    @api.model
    def create(self, vals):
        res = super(HrClearance, self).create(vals)
        if res.clearance_type:
            if not res.decision_number and res.clearance_type == 'transfer':
                raise ValidationError(_("You can't create clearance with transfer clearance type."))
        if res.leave_request_id:
            if res.state not in ['draft','cancel']:
                res.leave_request_id.have_clearance = True
            else:
                res.leave_request_id.have_clearance = False
        if res.termination_id:
            if res.state not in ['draft', 'cancel']:
                res.termination_id.have_termination = True
            else:
                res.termination_id.have_termination = False
        return res
    #
    # @api.multi
    def write(self, values):
        res = super(HrClearance, self).write(values)
        if self.leave_request_id:
            if self.state not in ['draft', 'cancel']:
                self.leave_request_id.have_clearance = True
            else:
                self.leave_request_id.have_clearance = False
        if self.termination_id:
            if self.state not in ['draft', 'cancel']:
                self.termination_id.have_termination = True
            else:
                self.termination_id.have_termination = False
        return res



    def compute_replace_by_user(self):
        for rec in self:
            rec.replace_by_user_check = False
            if rec.leave_request_id.replace_by:
                if rec.leave_request_id.replace_by.user_id == rec.env.user:
                    rec.replace_by_user_check = True



    def submit(self):
        for rec in self:
            custody_request_ids = rec.env['custody.request'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'assign')], limit=1)
            if custody_request_ids:
                if not rec.employee_id.branch_id.is_hq_branch:
                    rec.state = 'branch_supervisor'
                else:
                    rec.state = 'direct_manager'
            else:
                rec.state = 'done'

            # if rec.clearance_type == 'vacation':
            #     custody_request_ids = rec.env['custody.request'].search(
            #         [('employee_id', '=', rec.employee_id.id),('state', '=', 'assign'),('clearance_in_leave','=',True)],limit=1)
            #     sim_card_request_ids = rec.env['sim.card.request'].search(
            #         [('employee_id', '=', rec.employee_id.id),('state', '=', 'delivered'),('clearance_in_leave','=',True)],limit=1)
            #     if custody_request_ids or sim_card_request_ids:
            #         raise ValidationError("Please return your custodies first and try again.")
        #     rec.state = 'department_manager'
        # else:
        #     rec.state = 'department_manager'

    def branch_supervisor_approve(self):
        for rec in self:
            if rec.clearance_type == 'vacation':
                custody_request_ids = rec.env['custody.request'].search(
                    [('employee_id', '=', rec.employee_id.id),('state', '=', 'assign'),('clearance_in_leave','=',True)],limit=1)
                sim_card_request_ids = rec.env['sim.card.request'].search(
                    [('employee_id', '=', rec.employee_id.id),('state', '=', 'delivered'),('clearance_in_leave','=',True)],limit=1)
                if custody_request_ids or sim_card_request_ids:
                    raise ValidationError("Please return your custodies first and try again.")
            elif rec.clearance_type == 'final':
                custody_request_ids = rec.env['custody.request'].search(
                    [('employee_id', '=', rec.employee_id.id), ('state', '=', 'assign')], limit=1)
                sim_card_request_ids = rec.env['sim.card.request'].search(
                    [('employee_id', '=', rec.employee_id.id), ('state', '=', 'delivered')], limit=1)
                if custody_request_ids or sim_card_request_ids:
                    raise ValidationError("Please return your custodies first and try again.")
            else:
                rec.state = 'done'


    def direct_manager_approve(self):
        for rec in self:
            if rec.clearance_type == 'vacation':
                custody_request_ids = rec.env['custody.request'].search(
                    [('employee_id', '=', rec.employee_id.id),('state', '=', 'assign'),('clearance_in_leave','=',True)],limit=1)
                sim_card_request_ids = rec.env['sim.card.request'].search(
                    [('employee_id', '=', rec.employee_id.id),('state', '=', 'delivered'),('clearance_in_leave','=',True)],limit=1)
                if custody_request_ids or sim_card_request_ids:
                    raise ValidationError("Please return your custodies first and try again.")
            elif rec.clearance_type == 'final':
                custody_request_ids = rec.env['custody.request'].search(
                    [('employee_id', '=', rec.employee_id.id), ('state', '=', 'assign')], limit=1)
                sim_card_request_ids = rec.env['sim.card.request'].search(
                    [('employee_id', '=', rec.employee_id.id), ('state', '=', 'delivered')], limit=1)
                if custody_request_ids or sim_card_request_ids:
                    raise ValidationError("Please return your custodies first and try again.")
            else:
                rec.state = 'done'


    # def dept_manager_approve(self):
    #     for rec in self:
    #         custody_request_ids = rec.env['custody.request'].search(
    #             [('employee_id', '=', rec.employee_id.id), ('state', '=', 'assign')],limit=1)
    #         if custody_request_ids:
    #             raise ValidationError("You can't approve unless employee return all custodies.")
    #         if rec.employee_id.job_id.is_driver:
    #             rec.state = 'technical_support'
    #         elif not rec.replace_by_user_check:
    #             rec.state = 'internal_auditor'
    #         else:
    #             rec.state = 'replacement_approval'
    #
    # def tech_aupport_approve(self):
    #     for rec in self:
    #         if not rec.replace_by_user_check:
    #             rec.state = 'internal_auditor'
    #         else:
    #             rec.state = 'replacement_approval'
    #
    # def replacement_approve(self):
    #     for rec in self:
    #         rec.state = 'internal_auditor'
    #
    #
    # def internal_audit_approve(self):
    #     for rec in self:
    #         rec.state = 'finance_manager'
    #
    # def finance_manager(self):
    #     for rec in self:
    #         if not rec.bank_attachment_id:
    #             raise ValidationError("You can't approve unless bank attachment is attached.")
    #         rec.state = 'hr_salary_accountant'
    #
    # def hr_salary_accountant(self):
    #     for rec in self:
    #         if not rec.bank_comments:
    #             raise ValidationError("You can't approve unless bank comments are given.")
    #         rec.state='done'

    def draft(self):
        for rec in self:
            rec.state = 'draft'


class HrLeaveInherit(models.Model):
    _inherit = 'hr.leave'

    have_clearance = fields.Boolean(string='Have Clearance?')

    def compute_have_clearance(self):
        for rec in self:
            clearance_ids = rec.env['hr.clearance'].search([('leave_request_id','=',rec.id),('state','not in',['draft','cancel'])])
            if clearance_ids:
                rec.have_clearance = True
            else:
                rec.have_clearance = False

class HrLeaveInheritClearance(models.Model):
    _inherit = "hr.leave"

    # @api.multi
    def action_hr_clearance(self):
        res = self.env['ir.actions.act_window']._for_xml_id('hr_clearence.hr_clearance_action')
        res['domain'] = [('leave_request_id', 'in', self.ids)]
        return res

    clearance_count = fields.Integer('HR Clearance', compute='_compute_hr_clearance_count',
                                        track_visibility='onchange')

    # @api.multi
    def _compute_hr_clearance_count(self):
        for clearance in self:
            clearance.clearance_count = self.env['hr.clearance'].search_count(
                [('leave_request_id', '=', clearance.id)])




