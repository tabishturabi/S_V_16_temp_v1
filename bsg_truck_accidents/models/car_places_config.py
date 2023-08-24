# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class CarPlacesConfig(models.Model):
    _name = 'car.places.config'

    name = fields.Char("Place Name")