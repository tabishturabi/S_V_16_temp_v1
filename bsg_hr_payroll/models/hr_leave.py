
from odoo import api, fields, models



class HRLeave(models.Model):
    _inherit = "hr.leave"

    last_return_date = fields.Date(related="employee_id.last_return_date")
