from odoo import api, fields, models


class HolidaysLeaveType(models.Model):
    _inherit = "hr.leave.type"

    is_annual = fields.Boolean(string="Is Annual")
