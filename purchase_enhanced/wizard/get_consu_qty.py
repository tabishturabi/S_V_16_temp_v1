# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class GetConsuProductQty(models.TransientModel):
    _name = 'get.consumable.product.qty'
    _description = 'Get Consumable Product Qty'


    @api.model
    def default_get(self, fields):
        result = super(GetConsuProductQty, self).default_get(fields)
        line_id = self.env.context.get('line_id',False)
        result['purchase_transfer_line_id'] = line_id
        return result


    purchase_transfer_line_id = fields.Many2one('purchase.transfer.line',required=True)
    product_id = fields.Many2one('product.product',related='purchase_transfer_line_id.product_id',string='Requested Product')
    location_id = fields.Many2one('stock.location',required=True)

    # @api.multi
    def action_get_qty(self):
        for rec in self:
            rec.purchase_transfer_line_id.searched_loc_id = rec.location_id.id
        return True
