# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import math
from odoo.exceptions import UserError
from datetime import datetime, timedelta, timezone


class IqamaRenewels(models.Model):
    _name = 'iqama.renewels'
    _inherit = 'mail.thread'
    _description = 'Iqama Renewel'
    _rec_name = 'sequence_number'



    sequence_number = fields.Char(string='Request NO',readonly=True,track_visibility='always')
    request_date = fields.Date(string='Request Date',default=fields.date.today(),track_visibility='always')
    employee_name= fields.Many2one('hr.employee',string='Employee Name',track_visibility='always')
    emp_department = fields.Many2one('hr.department',readonly=True,track_visibility='always',string='Department')
    employee_id = fields.Char(related='employee_name.driver_code',store=True,string='Employee ID',track_visibility='always')
    branch_name= fields.Many2one('bsg_branches.bsg_branches',readonly=True,string='Branch Name',track_visibility='always')
    partner_id = fields.Many2one('res.partner',readonly=True)
    nationality = fields.Many2one('res.country',readonly=True,string='Nationality',track_visibility='always')
    job_position= fields.Many2one('hr.job',readonly=True,string='Job Position',track_visibility='always')
    manager= fields.Many2one('hr.employee',readonly=True,string='Manager',required=True,track_visibility='always')
    iqama_no= fields.Many2one(related='employee_name.bsg_empiqama',store=True,string='Iqama NO',track_visibility='always')
    iqama_job_position= fields.Char(string='Job Position On Iqama',readonly=True,track_visibility='always')
    expiration_date= fields.Date(related='iqama_no.bsg_expirydate',store=True,string='Expiration Date',track_visibility='always')
    analytic_account = fields.Many2one('account.analytic.account',string='Analytic Account',readonly=True)
    state = fields.Selection([('draft','Draft'),('submitted_to_manager','Submitted to Manager'),
                              ('confirmed_by_manager','Confirmed By Manager'),('rejected_by_manager','Rejected By Manager'),
                              ('confirmed_by_hrmanager','Confirmed By HR Manager'),('rejected_by_hrmanager','Rejected By HR Manager'),
                              ('petty_cash_done','Petty Cash Done'),
                              ('done','Done'),('refused','Refused')],default='draft',track_visibility='always')
    emp_reject_comment= fields.Text(string='Employee Rejection Comment',track_visibility='always')
    manager_reject_comment = fields.Text(string='Manager Rejection Comment',track_visibility='always')
    hr_manager_reject_comment = fields.Text(string='Hr Manager Rejection Comment',track_visibility='always')
    renewel_duration = fields.Selection([('1','1 Year'),('2','2 Years'),('3','3 Years'),('4','4 Years'),
                                         ('5','5 Years')],default='1',track_visibility='always')
    user_id = fields.Many2one('res.users', string='Requester',track_visibility='always')
    refusal_reason = fields.Text(string='Reason', readonly=True,track_visibility='always')
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    expense_id = fields.Many2one('expense.accounting.petty',string='Expense ID',track_visibility='always')
    label=fields.Char(string='Label',store=True,compute='_get_label')
    truck = fields.Many2one('fleet.vehicle',store=True,string='Truck',compute='_get_vehicle_id')

    def set_expense_id(self,expense_id):
        if expense_id:
            self.write({'expense_id':expense_id,'state':'petty_cash_done'})

    @api.depends('employee_name','sequence_number')
    def _get_label(self):
        for rec in self:
            rec.label = 'تجديد اقامة الموظف'+'-'+str(rec.employee_name.name)+'-'+'رقم الاقامة'+'-'+str(rec.sequence_number)

    @api.depends('employee_name')
    def _get_vehicle_id(self):
        for rec in self:
            vehicle_id = rec.env['fleet.vehicle'].search([('taq_number','=',rec.employee_name.vehicle_sticker_no)],limit=1)
            rec.truck = vehicle_id.id
    # @api.multi
    # @api.depends('iqama_renewel_expense_line.amount','iqama_renewel_expense_line.taxes')
    # def _expenses_amount_all(self):
    #     for rec in self:
    #         expense_lines = rec.iqama_renewel_expense_line
    #         if expense_lines:
    #             expense_untaxed_amount = sum(expense_lines.mapped('amount'))
    #             expense_taxe_amount = sum(expense_lines.mapped('taxes'))
    #             rec.update({
    #                 'amount_untaxed': expense_untaxed_amount,
    #                 'amount_tax': expense_taxe_amount,
    #                 'amount_total': expense_untaxed_amount + expense_taxe_amount
    #             })
    #         else:
    #              rec.update({
    #                 'amount_untaxed': 0.0,
    #                 'amount_tax': 0.0,
    #                 'amount_total': 0.0
    #             })

    @api.onchange('employee_name')
    def onchange_employee_id(self):
        for rec in self:
            contract_id = rec.env['hr.contract'].search([('employee_id','=',rec.employee_name.id),('state','=','open')])
            rec.analytic_account=contract_id.analytic_account_id.id
            rec.emp_department = rec.employee_name.department_id.id
            rec.branch_name = rec.employee_name.branch_id.id
            rec.manager = rec.employee_name.parent_id.id
            rec.job_position = rec.employee_name.job_id.id
            rec.iqama_job_position = rec.iqama_no.bsg_job_pos
            rec.nationality = rec.employee_name.country_id.id
            rec.partner_id =  self.employee_name.partner_id.id

    # @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('bsg_iqama_renewels', 'action_attachment')
        return res

    # @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'iqama.renewels'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for iqama in self:
            iqama.attachment_number = attachment.get(iqama.id, 0)

    @api.model
    def create(self, vals):
        c_obj = self.env['ir.sequence'].search([('name', '=', 'code sequence')])
        ro_code = c_obj.code
        vals['sequence_number'] = self.env['ir.sequence'].next_by_code(ro_code)
        return super(IqamaRenewels, self).create(vals)

    def click_submit(self):
        if self.state == 'draft':
            self.state = 'submitted_to_manager'
    def confirm_manager(self):
        if self.state == 'submitted_to_manager':
            self.state = 'confirmed_by_manager'
    def reject_manager(self):
        if self.state == 'submitted_to_manager':
            if not self.manager_reject_comment:
                raise UserError(_('Please Give Rejection Reason'))
            else:
                self.state = 'rejected_by_manager'
    def confirm_hrmanager(self):
        if self.state == 'confirmed_by_manager':
            if not self.user_id:
                raise UserError(_('Requester is mandatory for further process'))
            else:
                self.state = 'confirmed_by_hrmanager'
    def reject_hrmanager(self):
        if self.state == 'confirmed_by_manager':
            if not self.hr_manager_reject_comment:
                raise UserError(_('Please Give Rejection Reason'))
            else:
                self.state = 'rejected_by_hrmanager'
    def expenses_issue(self):
        if self.state == 'confirmed_by_hrmanager':
            expence_action = self.env.ref('advance_petty_expense_mgmt.petty_expence_create_wizard_action')
            attach_ids = self.env['ir.attachment'].search([('res_model', '=', 'iqama.renewels'), ('res_id', 'in', self.ids)])
            action = expence_action.read()[0]
            action['context'] = "{'default_user_id':%d,\
                           'default_line_ref':'%s',\
                           'default_partner_id':%d,\
                           'default_analytic_account_id': %d,\
                           'default_branch_id': %d,\
                           'default_department_id': %d,\
                           'default_truck_id': %d,\
                           'default_label': '%s',\
                           'default_attach_files_ids': %s,\
                           }"%(self.user_id.id ,self.sequence_number,self.partner_id.id and self.partner_id.id or self.employee_name.partner_id.id,
                           self.analytic_account.id,self.branch_name and self.branch_name.id or self.employee_name.branch_id.id,
                           self.emp_department and self.emp_department.id or self.employee_name.department_id.id,self.truck.id,self.label,attach_ids.ids)
            return  action              
            # self.state = 'expenses_issue'
    # def click_pettycash(self):
    #     if self.state == 'expenses_issue':
    #         if not self.iqama_renewel_expense_line:
    #             raise UserError(_('Please Add Expenses Lines'))
    #         else:
    #             self.state = 'submitted_for_petty_cash_process'
    def click_done(self):
        if self.state == 'petty_cash_done':
            if not self.expiration_date:
                raise UserError(_('Expiration date of iqama is not given'))
            else:
                if self.renewel_duration:
                    iqama_id = self.env['hr.iqama'].search([('id','=',self.iqama_no.id)])
                    duration = self.renewel_duration
                    self.expiration_date += timedelta(days=duration * 365)
                    if iqama_id:
                        iqama_id.bsg_expirydate = self.expiration_date
                    self.state = 'done'


class EmployeeForCountryCOde(models.Model):
    _inherit = 'hr.employee'


    country_code = fields.Char(related='country_id.code',store=True,string='Country Code')










