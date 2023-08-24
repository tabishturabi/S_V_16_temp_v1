# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.exceptions import UserError, ValidationError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    journal_id = fields.Many2one('account.journal', 'Salary Journal', default=lambda self: self.env['account.journal'].search([('code', '=', 'SALRY')], limit=1), domain=[('code','=', 'SALRY')])
    code = fields.Char('Code', readonly=True)
    work_nature_allowance = fields.Float('Work Nature')
    fixed_add_allowance = fields.Float('Fixed Addtional')
    food_allowance = fields.Float('Food')
    work_nature_active_date = fields.Date('Active Date')
    work_nature_expiry_date = fields.Date('Expiry Date')
    fixed_add_active_date = fields.Date('Active Date')
    fixed_add_expiry_date = fields.Date('Expiry Date')
    custom_gosi = fields.Boolean('Custom Social Insurance')
    employee_gosi = fields.Float('Employee GOSI')
    company_gosi = fields.Float('Company GOSI')
    annual_legal_leave = fields.Integer("Annual Legal Leave",required=True,default=30)
    marital = fields.Selection([('single', 'Single'), ('married','Married')], 'Marital Status')
    fixed_deduct_amount = fields.Float('Fixed Deduction')
    transportation_allowance = fields.Float('Transportation Allowance')
    housing_allowance = fields.Float('Housing Allowance')
    house_rent_allowance_metro_nonmetro = fields.Float(string='House Rent Allowance (%)', digits='Payroll',
        help='HRA is an allowance given by the employer to the employee for taking care of his rental or accommodation expenses for metro city it is 50% and for non metro 40%. \nHRA computed as percentage(%)')

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('hr.contract')
        return super(HrContract, self).create(vals)

    @api.constrains('work_nature_allowance','fixed_add_allowance', 'food_allowance')
    def check_allowance(self):
        if self.work_nature_allowance < 0.0:
            raise ValidationError(_("Work nature allowance value can not be less that 0.0!"))
        if self.fixed_add_allowance < 0.0:
            raise ValidationError(_("Fixed additional allowance value can not be less that 0.0!"))
        if self.food_allowance < 0.0:
            raise ValidationError(_("food allowance value can not be less that 0.0!"))
    
    @api.constrains('work_nature_active_date','work_nature_expiry_date', 'fixed_add_active_date', 'static_expiry_date')
    def check_allowance_dates(self):
        if self.work_nature_expiry_date and self.work_nature_active_date and self.work_nature_active_date > self.work_nature_expiry_date:
            raise ValidationError(_("Work nature allowance activation date can not be greater than it's expiry date!"))
        if self.fixed_add_active_date and self.fixed_add_expiry_date and self.fixed_add_active_date > self.fixed_add_expiry_date:
            raise ValidationError(_("Fixed additional allowance activation date can not be greater than it's expiry date!"))

