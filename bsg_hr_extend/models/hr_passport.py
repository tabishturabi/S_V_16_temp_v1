# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions,_

class BsgHrPassport(models.Model):
    _inherit = 'hr.passport'

    bsg_emp_code = fields.Char(related='bsg_employee_id.employee_code',string='Employee ID')
    bsg_emp_id = fields.Char(related='bsg_employee_id.driver_code',string='Driver Code')
