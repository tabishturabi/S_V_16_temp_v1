# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError



class HRContract(models.Model):
    _inherit = 'hr.contract'

    CONTRACT_PERIOD = [
        ('12', '12 Months'),
        ('24', '24 Months'),
        ('36', '36 Months'),
        ('without_period', 'Without Period'),
        ('other', 'Other')]

    contract_period = fields.Selection(CONTRACT_PERIOD, default='12', string='Contract Period')
    gosi_percentage = fields.Float(string='GOSI Percentage')
    contract_documentation = fields.Boolean(string='Contract Documentation')
    last_ticket_date = fields.Date(string='Last Ticket Date')
    contract_end_date = fields.Date(string='Contract End Date')
    date_end = fields.Date('End Date', compute='_get_date_end', store=True,
                           help="End date of the contract (if it's a fixed-term contract).")
    struct_id = fields.Many2one('hr.payroll.structure', string="Regular Pay Structure",related="structure_type_id.default_struct_id",store=True)


    
    def contract_trial_end_date(self):
        yesterday = fields.date.today() - relativedelta(days=1)
        contract_ids = self.env['hr.contract'].search([('state', '=', 'open'),('trial_date_end','=',yesterday)])
        for contract_id in contract_ids:
            contract_id.employee_id.state = 'on_job'

    # @api.multi
    def get_all_structures(self):
        """
        @return: the structures linked to the given contracts, ordered by hierachy (parent=False first,
                 then first level children and so on) and without duplicata
        """
        structures = self.mapped('struct_id')
        if not structures:
            return []
        # YTI TODO return browse records
        return list(set(structures._get_parent_structure().ids))


    @api.onchange('date_start')
    
    def _get_trail_date_end(self):
        for rec in self:
            # rec.employee_id.bsgjoining_date = rec.date_start
            rec.trial_date_end = rec.date_start + relativedelta(months=3)

    
    def write(self, values):
        res = super(HRContract, self).write(values)
        for rec in self:
            if rec.employee_id:
                rec.employee_id.write({'bsgjoining_date': rec.date_start})
        return res

    @api.model
    def create(self, vals):
        res = super(HRContract, self).create(vals)
        for rec in res:
            if rec:
                if rec.employee_id:
                    rec.employee_id.write({'bsgjoining_date': rec.date_start})
        return res

    @api.depends('contract_period', 'date_start', 'contract_end_date')
    def _get_date_end(self):
        for rec in self:
            rec.date_end = False
            # rec.employee_id.bsgjoining_date = rec.date_start
            # rec.trial_date_end = rec.date_start + relativedelta(months=3)
            if rec.contract_period == '12':
                rec.date_end = rec.date_start + relativedelta(years=1)
            elif rec.contract_period == '24':
                rec.date_end = rec.date_start + relativedelta(years=2)
            elif rec.contract_period == '36':
                rec.date_end = rec.date_start + relativedelta(years=3)
            elif rec.contract_period == 'without_period':
                rec.date_end = False
            else:
                rec.date_end = rec.contract_end_date


class ExtendTrialPeriod(models.Model):
    _name = 'extend.trial.period'

    _description = "Extend Trial Period"
    _rec_name = "employee_id"

    employee_id = fields.Many2one("hr.employee", string="Employee", domain=[('state', '=', 'trail_period')],
                                  required=True)
    employee_no = fields.Char(related="employee_id.driver_code", string="Driver Code")
    branch_id = fields.Many2one("bsg_branches.bsg_branches", related="employee_id.bsg_branch_id", string="Branch")
    department_id = fields.Many2one("hr.department", related="employee_id.department_id", string="Department")
    job_id = fields.Many2one("hr.job", related="employee_id.job_id", string="Job")
    manager_id = fields.Many2one("hr.employee", related="employee_id.parent_id", string="Manager")
    date_start = fields.Date(string='Start Date', readonly=True)
    trail_date_end = fields.Date(string='Trial Date End', readonly=True)
    new_trail_date_end = fields.Date(string='New Trial Date End', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'),
                              ('cancel', 'Cancelled')], default='draft', track_visibility='always')

    @api.onchange('employee_id')
    def get_current_contract(self):
        for rec in self:
            contract_id = rec.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
            if contract_id:
                rec.date_start = contract_id.date_start
                rec.trail_date_end = contract_id.trial_date_end

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('driver_code', operator, name)] + args, limit=limit)
        return recs.name_get()

    def action_submit_manager(self):
        for rec in self:
            rec.state = 'submitted'

    def action_approve(self):
        for rec in self:
            if not rec.trail_date_end:
                raise ValidationError(_("Employee contract has no trial end date."))
            rec.new_trail_date_end = rec.trail_date_end + relativedelta(months=3)
            contract_id = rec.env['hr.contract'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1)
            if contract_id:
                contract_id.trial_date_end = rec.new_trail_date_end
                decision_data = {
                    'employee_name':rec.employee_id.id,
                    'old_manager': rec.employee_id.parent_id.id,
                    'old_branch_name': rec.employee_id.branch_id.id,
                    'old_emp_department': rec.employee_id.department_id.id,
                    'old_job_position': rec.employee_id.job_id.id,
                    'old_company': rec.employee_id.company_id.id,
                    'old_salary_structure': contract_id.structure_type_id.default_struct_id.id,
                    'old_analytic_account': contract_id.analytic_account_id.id,
                    'old_wage': contract_id.wage,
                    'old_work_nature': contract_id.work_nature_allowance,
                    'old_fixed_additional': contract_id.fixed_add_allowance,
                    'old_food': contract_id.food_allowance,
                    'old_fixed_deduction': contract_id.fixed_deduct_amount,
                    'old_bonus_cls_ids': rec.employee_id.bonus_classification_ids,
                    'current_company': rec.employee_id.company_id.id,
                    'current_salary_structure': contract_id.structure_type_id.default_struct_id.id,
                    'current_wage': contract_id.wage,
                    'current_work_nature': contract_id.work_nature_allowance,
                    'current_fixed_additional': contract_id.fixed_add_allowance,
                    'current_food': contract_id.food_allowance,
                    'current_fixed_deduction': contract_id.fixed_deduct_amount,
                    'decision_type':'extend'
                }
                rec.env["employees.appointment"].create(decision_data)
            rec.state = 'approved'

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
