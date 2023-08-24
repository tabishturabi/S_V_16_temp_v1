from odoo import models, fields

class ResCountry(models.Model):
    _inherit = 'res.country'

    visible_on_mobile_app = fields.Boolean('Visible On Mobile App')