# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    local_trip_revenue = fields.Float(string='Local Trip Revenue', default=0)
    cash_rounding_id = fields.Many2one('account.cash.rounding', string="Cash Rounding Method")
    rented_vehicle_service = fields.Many2one('product.template',string='Default Rented Vehicle Service Product')								   
