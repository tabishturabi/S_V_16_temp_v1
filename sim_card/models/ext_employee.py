# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, _



class ExtEmployee(models.Model):
    _inherit = 'hr.employee'

    sim_count = fields.Integer(string='SIM Card')
    employee_d_id = fields.Many2one('sim.card.define', string="employee delivered ID")
    employee_delivery_count = fields.Integer('employee of Delivery', compute='_compute_employee_delivery_id_count')

    def _compute_employee_delivery_id_count(self):
        for rec in self:
            rec.employee_delivery_count = self.env['sim.card.define'].search_count([('employee.id', '=', rec.id)])

    def compute_employee_delivery_count(self):
        return {
            'name': 'Employee Sim Delivery',
            'domain': [('employee', '=', self.id)],
            'res_model': 'sim.card.define',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            "views": [[self.env.ref('sim_card.sim_card_define_tree_vieww1').id, "tree"],
                      [self.env.ref('sim_card.sim_card_define_form_view').id, "form"]],
        }




