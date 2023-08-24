# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.exceptions import UserError, ValidationError
import re
from lxml import etree
# from odoo.osv.orm import setup_modifiers




class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # "Has Loan ?"

    #
    "Loan from"
    judicial_character = fields.Char(string="Judicial Character",track_visibility='always')
    judicial_body = fields.Char(string="judicial Body",track_visibility='always')
    has_loan = fields.Boolean("Has Loan?",track_visibility='always')
    loan_from = fields.Char("Loan From",track_visibility='always')
    social_security_no = fields.Char("Social Security Membership No.",track_visibility='always')
    suspend_salary = fields.Boolean('Suspend Salary',track_visibility='always')
    employee_code = fields.Char('Employee Code', readonly=True, track_visibility='always')
    last_return_date = fields.Date('Effective Date',track_visibility='always')
    has_done_payslip = fields.Boolean(readonly=True, compute='_compute_has_done_payslip',track_visibility='always')
    branch_id = fields.Many2one('bsg_branches.bsg_branches', string="Branch",track_visibility='always',required=True)
    is_inspection_employee = fields.Boolean('Is Inspection Employee',track_visibility='always')
    has_open_contract = fields.Boolean('has Running contract', readonly=True, compute="_compute_has_open_contract",store=True,track_visibility='always')
    # salary_payment_method = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')], string = "Salary Payment Method", default='bank',track_visibility='always')
    state = fields.Selection([
        ('complete_data', 'Completed Data'),
        ('trail_period', 'Trail Period'),
        ('on_job', 'On Job'),
        ('on_leave', 'On Leave'),
        ('service_expired', 'Service Expired'),
    ], string='Employee State',  default='complete_data',track_visibility='always')
    last_emp_state = fields.Selection([
        ('complete_data', 'Completed Data'),
        ('trail_period', 'Trail Period'),
        ('on_job', 'On Job'),
        ('on_leave', 'On Leave'),
        ('service_expired', 'Service Expired'),
    ], string='Employee State',track_visibility='always')
    employee_state = fields.Selection([
        ('on_job', 'On Job'),
        ('on_leave', 'On leave'),
        ('return_from_holiday', 'Return From Holiday'),
        ('resignation', 'Resignation'),
        ('suspended', 'Suspended'),
        ('service_expired','Service Expired'),
        ('contract_terminated', 'Contract Terminated'),
        ('ending_contract_during_trial_period','Ending Contract During Trial Period'),
        ('deceased', 'Deceased'),
        ('suspended_case', 'Suspended for Case'),

    ], string='Employee State',  default='on_job',track_visibility='always')
    category_id = fields.Many2one(
        'hr.employee.category',
        string='Tag',track_visibility='always')
    state_id = fields.Many2one("bsg.hr.state", index=True,track_visibility='always')
    suspend_salary = fields.Boolean('Suspend Salary',track_visibility='always')
    check_suspend_salary = fields.Boolean(string="Suspend Salary", compute="get_check_suspend_salary",track_visibility='always')
    work_location = fields.Char(track_visibility='always')


    def change_to_on_job(self):
        for rec in self:
            rec.state = 'on_job'
            rec.employee_state = 'on_job'

    def get_check_suspend_salary(self):
        for rec in self:
            if rec.env.user.has_group("bsg_hr_payroll.group_suspend_salary_access"):
                rec.check_suspend_salary = True
            else:
                rec.check_suspend_salary = False

    @api.onchange("employee_state")
    def onchange_state_id(self):
        if self.employee_state:
            if self.employee_state != 'on_job':
                self.suspend_salary = True
            else:
                self.suspend_salary = False

    
    
    @api.depends('contract_ids.state')
    def _compute_has_open_contract(self):
        for rec in self:
            rec.has_open_contract = rec.contract_ids.filtered(lambda con:con.state == 'open') and True or False



    def get_next_sequence(self):
        seq = "NA"
        if self.country_id and self.country_id.code:
            if self.driver_code:
                num_code =  int(re.findall(r'\d+', self.driver_code)[0])
                if num_code <= self.country_id.employee_count:
                    seq = self.country_id.code + str(num_code+100000)[1:]
                else:
                    seq = self.country_id.code + str(self.country_id.employee_count + 1 +100000)[1:]
                    self.country_id.employee_count += 1
            else:
                seq = self.country_id.code + str(self.country_id.employee_count + 1 +100000)[1:]
                self.country_id.employee_count += 1
        return seq

    
    @api.depends('slip_ids')
    def _compute_has_done_payslip(self):
        sudo_self = self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id)
        payslip_states = sudo_self.slip_ids and sudo_self.slip_ids.mapped('state') or []
        self.has_done_payslip = 'done' in payslip_states and True or False

    @api.model
    def create(self, vals):
        rec = super(HrEmployee, self).create(vals)
        rec.employee_code = rec.get_next_sequence()
        if rec.partner_id:
                rec.partner_id.ref = rec.driver_code
        return rec
    
    def deactivate_user(self):
        for rec in self:
            if rec.employee_state in [
            "resignation", "suspended", "service_expired", "contract_terminated",
            "ending_contract_during_trial_period", "deceased", "suspended_case"] and rec.user_id:
                rec.user_id.toggle_active()

    
    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        if vals.get('country_id', False):
            self.employee_code = self.get_next_sequence()
            if self.partner_id:
                self.partner_id.ref = self.employee_code
        if vals.get('employee_state', False):
            self.deactivate_user()
        return res


    #FOR TECHNICAL USE
    
    def emp_complete_data(self):
        self.write({'state':'complete_data','last_emp_state':self.state})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    
    def last_state(self):
        self.write({'state':self.last_emp_state})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    
    def generate_employee_seq(self):
        employee_ids = self.search([])
        for rec in employee_ids:
            rec.employee_code = rec.get_next_sequence()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(HrEmployee, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and self.env.context.get('params'):
            doc = etree.XML(result['arch'])
            method_nodes = doc.xpath("//field")
            for node in method_nodes:
                emp_state = self.env['hr.employee'].browse(self.env.context.get('params').get('id'))
                if emp_state and emp_state.state != 'complete_data':
                    node.set('readonly', "1")
                    # setup_modifiers(node, result['fields'][node.get('name', False)])
            result['arch'] = etree.tostring(doc)
        return result
