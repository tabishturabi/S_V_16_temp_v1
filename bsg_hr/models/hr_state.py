# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class BsghrSate(models.Model):
    _name = 'bsg.hr.state'
    _description = 'Hr State Configuration'
    _rec_name = 'employee_state'
    
    employee_state = fields.Char('Employee State', translate=True)
    suspend_salary = fields.Boolean(string="Suspend Salary")
