# -*- coding: utf-8 -*-

from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, _


class ExtEmployee(models.Model):
    _inherit = 'hr.employee'

    effective_id = fields.Many2one('effect.request', string="Employee Effective")
    effective_count = fields.Integer(string='effective')
    return_count = fields.Integer(string='Return')
    last_move_date = fields.Date(string='Last Move Date', track_visibility=True, readonly=True)
    effectivee_count = fields.Integer(string='House')


    def employee_effective(self):
        return {
            'name': 'Employee Effective Request',
            'domain': [('employee_id', '=', self.id),('state', '=', 'done')],
            'res_model': 'effect.request',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            "views": [[self.env.ref('effective_date_notes.effect_request_tree_view').id, "tree"],
                      [self.env.ref('effective_date_notes.effect_request_form_view').id, "form"]],
        }


    def employee_return_vaction(self):
        return {
            'name': 'Employee Return vacation',
            'domain': [('employee_id', '=', self.id),('state', '=', 'done')],
            'res_model': 'return.vacation',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            "views": [[self.env.ref('effective_date_notes.vacation_request_tree_view').id, "tree"],
                      [self.env.ref('effective_date_notes.vacation_request_form_view').id, "form"]],
        }



# class ExtHrLeave(models.Model):
#     _inherit = 'hr.leave'
#
#     
#     def name_get(self):
#         res = []
#         if self._context.get('format_leave_type'):
#
#             for leave in self:
#                 res.append((leave.id, leave.holiday_status_id.name))
#
#         else:
#             res = super(ExtHrLeave, self).name_get()

        return res