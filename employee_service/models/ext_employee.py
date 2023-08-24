# -*- coding: utf-8 -*-

from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, _


class ExtEmployee(models.Model):
    _inherit = 'hr.employee'

    service_id = fields.Many2one('employee.service', string="Employee Service")
    service_count = fields.Integer(string='Service')

    def employee_service(self):
        return {
            'name': 'Employee Service',
            'domain': [('employee_id', '=', self.id),('state', '=', 'done')],
            'res_model': 'employee.service',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            "views": [[self.env.ref('employee_service.employee_service_entry_tree_view').id, "tree"],
                      [self.env.ref('employee_service.employee_service_form_view').id, "form"]],
        }



