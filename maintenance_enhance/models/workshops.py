from odoo import models, fields, api, _


class WorkshopName(models.Model):
    _name = "workshop.name"

    name = fields.Char(string="Workshop Name", track_visibility=True, translate=True)
