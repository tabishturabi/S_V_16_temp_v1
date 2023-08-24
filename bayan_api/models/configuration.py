# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions,_


class BayanConfig(models.Model):
    _name = 'bayan.plate.type.config'

    bayan_id = fields.Integer("Bayan ID",track_visibility='always')
    name = fields.Char("Plate Type Name",track_visibility='always',translate=True)

class BayanGoodType(models.Model):
    _name = 'bayan.good.type.config'

    good_id = fields.Integer("Goods ID",track_visibility='always')
    good_name =  fields.Char("Goods Name",track_visibility='always',translate=True)
    name =  fields.Char("Name",track_visibility='always',related='good_name')