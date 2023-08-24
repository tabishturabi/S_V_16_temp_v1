# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions,_

class BsgHrInsurance(models.Model):
    _inherit = 'hr.insurance'

    bsg_emp_code = fields.Char(related='employee_insurance.employee_code',string='Employee ID')
    bsg_emp_id = fields.Char(related='employee_insurance.driver_code',string='Driver Code')
