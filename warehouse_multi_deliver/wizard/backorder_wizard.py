# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process_cancel_backorder(self):
        self._process(cancel_backorder=True)
        for pick_id in self.pick_ids:
            for r in pick_id.move_lines:
                if r.purchase_req_rec_line_id and all(s.state=='cancel' for s in r.picking_id.backorder_ids):
                    if r.purchase_req_rec_line_id.qty_received < r.purchase_req_rec_line_id.qty:
                        r.purchase_req_rec_line_id.write({'added_to_rfq':False})