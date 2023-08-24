# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class RegionConfiguration(models.Model):
    _name = 'region.config'
    _description = "Region Configuration"
    _inherit = ['mail.thread']
    _rec_name = "bsg_region_name"

    bsg_region_name = fields.Char('Region English Name')
    bsg_region_name_ar = fields.Char('Region Arabic Name')
    bsg_region_code = fields.Char('Region Code')
    active = fields.Boolean(string="Active", tracking=True, default=True)
    bayan_region_id = fields.Integer("Bayan Region ID", tracking=True)
    bsg_region_name = fields.Char(track_visibility='always')
    bsg_region_code = fields.Char(track_visibility='always')
    region_arabic_name = fields.Char(string='Region Arabic Name', track_visibility='always')
    region_line = fields.One2many('region.config.line', 'region_id', string='Region Line')

    _sql_constraints = [
        ('bsg_region_code_uniq', 'unique (bsg_region_code)', _('The code must be unique !')),
    ]


class RegionConfigLine(models.Model):
    _name = 'region.config.line'
    _rec_name='city_name'

    region_id = fields.Many2one('region.config',string='Region ID')
    city_name = fields.Char(string='City Name' ,translate=True)
    city_code = fields.Char(string='City Code')
    bayan_city_id = fields.Integer("Bayan City ID", track_visibility='always')
