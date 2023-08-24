# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class TrucksDedicatingArea(models.Model):
    _name = 'trucks.dedicating.area'
    _description = 'Trucks Dedicating Area'

    name = fields.Char('Name',required=True)
