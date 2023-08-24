from odoo import models, fields, api, _


class Services(models.Model):
    _name = "service.name"

    name = fields.Char(string="Service Name", track_visibility=True, translate=True)
    workshop = fields.Many2one('workshop.name', string='Workshops', track_visibility=True)
