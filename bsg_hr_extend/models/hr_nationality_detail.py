# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions,_

class BsgHrNationalId(models.Model):
    _inherit = 'hr.nationality'

    bsg_emp_code = fields.Char(related='bsg_employee.employee_code',string='Employee ID')
    bsg_emp_id = fields.Char(related='bsg_employee.driver_code',string='Driver Code')
