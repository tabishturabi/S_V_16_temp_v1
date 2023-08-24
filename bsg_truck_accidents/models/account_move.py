# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class AccountMoveExt(models.Model):
    _inherit = 'account.move'

    bsg_truck_accident = fields.Many2one('bsg.truck.accident', string='Truck Accident', track_visibility=True)
