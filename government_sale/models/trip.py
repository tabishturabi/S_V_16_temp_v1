

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from lxml import etree
# from odoo.osv.orm import setup_modifiers


class VehicleTrip(models.Model):
    _inherit = 'fleet.vehicle.trip'

    sale_gov_id = fields.Many2one("transport.management", string="Gov Sale")
