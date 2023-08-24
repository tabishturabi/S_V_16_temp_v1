# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class BsgHrBanks(models.Model):
    _inherit = 'hr.banks'
   
    bsg_emp_code = fields.Char(related='bsg_employee_id.employee_code',string='Employee ID')
    bsg_emp_id = fields.Char(related='bsg_employee_id.driver_code',string='Driver Code')
