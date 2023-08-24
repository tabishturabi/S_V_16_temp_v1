# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AddInspectionWizard(models.TransientModel):
    _name = 'add.inspection.wizard'
    _description = "Add Inspection To Sale line"

    INSP_TYPE = [
        ("manual", "Manual"),
        ("mobile", "From mobile"),
        ("check_point", "Check point"),
    ]

    @api.model
    def default_get(self, fields_list):
        defaults = super(AddInspectionWizard, self).default_get(fields_list)
        sale_line_id = self.env.context.get('active_id')
        defaults.update({"sale_line_id": sale_line_id})
        sale_line = self.env["bsg_vehicle_cargo_sale_line"].browse([sale_line_id])
        last_sequence = max(sale_line.inspection_lines.mapped("sequence") or [0])
        defaults.update({"sequence": last_sequence+1})
        return defaults

    sequence = fields.Integer(string='Sequence', default=1)
    sale_line_id = fields.Many2one("bsg_vehicle_cargo_sale_line", required=True)
    pickup_loc = fields.Many2one('bsg_route_waypoints', related="sale_line_id.pickup_loc", string="Pickup Location")
    drop_loc = fields.Many2one('bsg_route_waypoints', related="sale_line_id.drop_loc", string="Drop Location")
    employee_id = fields.Many2one("hr.employee", string="Inspector Name")
    branch_id = fields.Many2one('bsg_branches.bsg_branches', string="Branch", related="employee_id.branch_id")
    inspection_type = fields.Selection(INSP_TYPE, string="Inspection Type", default="manual")
    date = fields.Datetime("Date", default=fields.datetime.now())
    user_id = fields.Many2one("res.users", string="User",  default=lambda self: self.env.user)

    # @api.onchange("employee_id")
    # def onchange_employee_id(self):
    #     self.branch_id = self.employee_id.branch_id

    @api.onchange("pickup_loc", "drop_loc")
    def onchange_locations(self):
        branches = self.env["bsg_branches.bsg_branches"]
        if self.pickup_loc:
            branches += self.pickup_loc.loc_branch_id
        if self.drop_loc:
            branches += self.drop_loc.loc_branch_id
        return {'domain': {'employee_id': [('branch_id', 'in', branches.ids), ('is_driver', '=', False)]}}

    def add_inspection(self):
        values = {
            "sale_line_id": self.sale_line_id.id,
            "sequence": self.sequence,
            "employee_id": self.employee_id.id,
            "branch_id": self.branch_id.id,
            "inspection_type": self.inspection_type,
            "date": self.date,
            "user_id": self.user_id.id,
        }
        inspection_line = self.env["sale.inspection.line"].create(values)
        # inspection_line.onchange_locations()
        self.sale_line_id.is_inspected = True
