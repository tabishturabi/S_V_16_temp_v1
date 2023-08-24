# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    bayan_plate_type_id = fields.Many2one('bayan.plate.type.config', track_visibility=True, string="Bayan Plate Type")
