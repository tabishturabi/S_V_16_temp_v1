# -*- coding: utf-8 -*-

from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, _


class ExtEmployee(models.Model):
    _inherit = 'hr.employee'

    house_id = fields.Many2one('entry.housing', string="Employee Housing")
    house_count = fields.Integer(string='House')

    e_house_count = fields.Integer(string='House')


    def employee_housing(self):
        return {
            'name': 'Employee Housing',
            'domain': [('employee_id', '=', self.id),('state', '=', 'done')],
            'res_model': 'entry.housing',
            # 'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            "views": [[self.env.ref('housing.employee_housing_entry_tree_view').id, "tree"],
                      [self.env.ref('housing.housing_entry_form_view').id, "form"]],
        }


class ExtFleetVehicle(models.Model):
    _inherit = 'fleet.vehicle.trip'

    @api.constrains('driver_id')
    def _vehicle_id(self):
        for record in self:
            curr_obj = self.env['entry.housing'].search([('employee_id', '=', record.driver_id.id),
                                                         ('house_seq', '=', False)])
            if  len(curr_obj) > 0:
                raise ValidationError(_('This diver has permission of entering the house no %s before make any trip go to make exit housing first' % curr_obj.name))
