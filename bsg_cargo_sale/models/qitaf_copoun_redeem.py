# -*- coding: utf-8 -*-

from odoo import models, fields, api

class QitafCopounRedeem(models.Model):
    _name = 'qitaf.copoun.redeem'

    name = fields.Char('Copoun Code',readonly=True)
    discount_type = fields.Selection([('fixed', 'Fixed'), ('percent', 'Percent')], readonly=True)
    discount_amount = fields.Float('Copoun Discount', readonly=True)
    sale_order_id = fields.Many2one('bsg_vehicle_cargo_sale', 'Sale Order', readonly=True)
    sale_total_amount = fields.Float('Sale order Total', readonly=True)
    sale_discounted_amount = fields.Float('Discounted Amount', readonly=True)
    total_after_discount = fields.Float('Total After Discount', readonly=True)

