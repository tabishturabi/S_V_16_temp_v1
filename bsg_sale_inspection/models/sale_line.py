# -*- coding: utf-8 -*-
import json
from lxml import etree
from lxml.builder import E

from odoo import api, fields, models, _


class InspectionLine(models.Model):
    _name = 'sale.inspection.line'

    INSP_TYPE = [
        ("manual", "Manual"),
        ("mobile", "From mobile"),
        ("check_point", "Check point"),
    ]

    sequence = fields.Integer(string='Sequence', default=1)
    sale_line_id = fields.Many2one("bsg_vehicle_cargo_sale_line", required=True)
    employee_id = fields.Many2one("hr.employee", string="Inspector Name",
                                  domain="[('branch_id', 'in', allowed_branched), ('is_driver','=',False)]")
    inspection_type = fields.Selection(INSP_TYPE, string="Inspection Type")
    branch_id = fields.Many2one('bsg_branches.bsg_branches', string="Branch")
    date = fields.Datetime("Date")
    user_id = fields.Many2one("res.users", string="User")
    pickup_loc = fields.Many2one('bsg_route_waypoints', related="sale_line_id.pickup_loc", string="Pickup Location")
    drop_loc = fields.Many2one('bsg_route_waypoints', related="sale_line_id.drop_loc", string="Drop Location")
    allowed_branched = fields.Many2many("bsg_branches.bsg_branches", compute="compute_allowed_branched")
    allowed_to_edit = fields.Boolean("User allowed to edit", compute="compute_allowed_to_edit")

    def compute_allowed_to_edit(self):
        for rec in self:
            if self.env.user.has_group("bsg_sale_inspection.group_sale_inspection_line_edit"):
                rec.allowed_to_edit = True
            else:
                rec.allowed_to_edit = False

    @api.depends("pickup_loc", "drop_loc")
    def compute_allowed_branched(self):
        for rec in self:
            branches = self.env["bsg_branches.bsg_branches"]
            if rec.pickup_loc:
                branches += rec.pickup_loc.loc_branch_id
            if rec.drop_loc:
                branches += rec.drop_loc.loc_branch_id
            rec.allowed_branched = branches
        # return {'domain': {'employee_id': [('branch_id', 'in', branches.ids)]}}

######################################################################


class bsg_vehicle_cargo_sale_line(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale_line'

    inspection_lines = fields.One2many("sale.inspection.line", "sale_line_id")
    is_inspected = fields.Boolean("Is inspected", index=True)

    
    def action_add_inspection(self):
        last_sequence = max(self.inspection_lines.mapped("sequence") or [0])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Inspection',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'add.inspection.wizard',
            'target': 'new',
            'context': {
                'default_sequence': last_sequence+1,
                'active_id': self.id,
                'active_ids': self.ids,
            }}
