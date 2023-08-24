# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EmployeeDecisionsButton(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee Decisions Button'

    employee_decisions_number = fields.Integer(string='Decisions', compute='compute_decisions_number')

    def action_decisions(self):
        return {
            'name': 'Employee Decisions',
            'domain': [('employee_name', '=', self.id)],
            'res_model': 'employees.appointment',
            # 'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            "views": [[self.env.ref('bsg_hr_employees_decisions.employee_appointment_tree_view_button').id, "tree"],
                      [self.env.ref('bsg_hr_employees_decisions.employee_appointment_form_view_button').id, "form"]],
        }

    # @api.multi
    def compute_decisions_number(self):
        for rec in self:
            count = rec.env['employees.appointment'].search_count([('employee_name', '=', rec.id)])
            rec.employee_decisions_number = count
