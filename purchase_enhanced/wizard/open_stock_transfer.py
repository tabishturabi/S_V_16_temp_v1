# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CloseStockTransfer(models.TransientModel):
    _name = 'colse.stock.transfer'
    _description = 'Close Stock Transfer'


    @api.model
    def default_get(self, fields):
        result = super(CloseStockTransfer, self).default_get(fields)
        purchase_id = self.env.context.get('active_id',False)
        result['purchase_transfer_id'] = purchase_id
        return result

    purchase_transfer_id = fields.Many2one('purchase.transfer',required=True)

    # @api.multi
    def action_close_transfer(self):
        if self.purchase_transfer_id:
            self.purchase_transfer_id.purchase_transfer.order_close()  
        
