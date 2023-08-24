# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class BsgTruckAccident(models.Model):
    _name = 'truck.accident.attachment'

    name = fields.Char("Name")
    is_required = fields.Boolean('Is Required')

