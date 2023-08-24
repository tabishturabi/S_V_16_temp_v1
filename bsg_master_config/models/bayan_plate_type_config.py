# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions,_


class BayanConfig(models.Model):
    _name = 'bayan.plate.type.config'
    _description = 'Bayan Plate Type Config'

    bayan_id = fields.Integer("Bayan ID",tracking=True)
    name = fields.Char("Plate Type Name",tracking=True,translate=True)