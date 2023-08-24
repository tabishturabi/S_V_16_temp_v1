# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BsgHrInsurance(models.Model):
    _name = 'hr.insurance'
    _description = "Insurance"
    _rec_name = "bsg_insurance_member1"

    employee_insurance = fields.Many2one('hr.employee',string="Employee")
    yearly_insurance_cost = fields.Float('Yearly Insurance Cost', copy=False, track_visibility='always')
    bsg_insurance_company = fields.Char("Insurance Company name")
    bsg_insurance_member1 = fields.Char( string="Member name")
    bsg_insurance_member =fields.Many2one('hr.employee',string="Member name") #automatically gets emp name if insurance is emp only
    bsg_startdate = fields.Date("Start date")
    bsg_enddate = fields.Date("End date")
    is_employee = fields.Boolean("Is a Employee")
    bsg_premium = fields.Float("Premium")
    bsg_insurancerelation = fields.Selection([('wife','Wife'),
                                              ('son', 'Son'),
                                              ('daug', 'Daughter'),
                                              ('emp', 'Employee'),

                                              ],string="Insurance Relation")
    bsg_class = fields.Char("Class")
    bsg_cardcode = fields.Char("Card Code")
    bsg_gender = fields.Selection([('M','Male'),('F','Female')],string="Gender")
    # bsg_placeofbirth = fields.Char("Place of Birth")
    bsg_emp_code = fields.Char(related='employee_insurance.employee_code', string='Employee ID')
    bsg_emp_id = fields.Char(related='employee_insurance.driver_code', string='Driver Code')

    @api.constrains('bsg_startdate', 'bsg_enddate')
    def check_start_end_date(self):
        for rec in self:
            employee_id = rec.bsg_insurance_member or rec.employee_insurance
            if employee_id and employee_id.contract_id:
                contract_start = employee_id.contract_id.date_start
                if not (rec.bsg_startdate >= contract_start and rec.bsg_enddate > contract_start):
                    raise UserError(_("Insurance Start date must be greater or equal to %s and end date must be greater than %s")%(str(contract_start), str(contract_start)))

    @api.onchange('is_employee')
    def check_boolean(self):
        if (self.is_employee):
            self.bsg_insurance_member = self._context.get('default_bsg_insurance_member')
        else:
            self.bsg_insurance_member = ''