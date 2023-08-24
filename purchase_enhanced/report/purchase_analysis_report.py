# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class PurchaseReport(models.Model):
    _inherit = "purchase.report"


    qty_received = fields.Float(string="Received Qty",readonly=True)
    qty_invoiced = fields.Float(string="Invoiced Qty",readonly=True)
    qty_received_price = fields.Float(string="Received Qty Price",readonly=True)
    qty_invoiced_price = fields.Float(string="Invoiced Qty Price",readonly=True)
    is_copy = fields.Boolean()
    def _select(self):
        return super(PurchaseReport, self)._select() + ", sum(l.qty_received/u.factor*u2.factor) as qty_received,sum(l.qty_invoiced/u.factor*u2.factor) as qty_invoiced,l.is_copy as is_copy,sum(l.price_unit / COALESCE(NULLIF(cr.rate, 0), 1.0) * l.qty_received)::decimal(16,2) as qty_received_price,sum(l.price_unit / COALESCE(NULLIF(cr.rate, 0), 1.0) * l.qty_invoiced)::decimal(16,2) as qty_invoiced_price"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", l.is_copy"
