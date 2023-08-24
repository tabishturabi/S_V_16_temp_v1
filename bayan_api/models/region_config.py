# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class RegionConfigurationExt(models.Model):
    _inherit = 'region.config'

    bayan_region_id = fields.Integer("Bayan Region ID", track_visibility='always')


class RegionConfigurationLineExt(models.Model):
    _inherit = 'region.config.line'

    bayan_city_id = fields.Integer("Bayan City ID", track_visibility='always')
