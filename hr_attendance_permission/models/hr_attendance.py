# -*- coding: utf-8 -*-


from odoo import api, fields, models, exceptions, _


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    # permission
    permission_id = fields.Many2one("hr.permission.request", compute="compute_permission_id", store=True)
    permission_duration = fields.Integer("Permission Minutes", related="permission_id.duration_display", store=True)
    permission_type = fields.Selection(string="Permission Type", related="permission_id.permission_period", store=True)

    @api.depends("employee_id", "day")
    def compute_permission_id(self):
        for rec in self:
            domain = [("employee_id", "=", rec.employee_id.id), ("request_date", "=", rec.day)]
            rec.permission_id = self.env["hr.permission.request"].search(domain, limit=1)
            print("===========", rec.permission_id)
