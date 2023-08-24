from odoo import models, fields, api, _


class InspectionConfig(models.Model):
    _name = "inspection.config"

    name = fields.Char(string="Title", track_visibility=True,translate=True)
    type = fields.Selection(string="Type", selection=[('trailer', 'Trailer'), ('truck', 'Truck')], default='draft', track_visibility=True)


