# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class FleetVehicleState(models.Model):
    _inherit = 'fleet.vehicle.state'

    code = fields.Char(string='Reference')
