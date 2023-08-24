# -*- coding: utf-8 -*-
# Part of Odoo. See ICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
    _description = 'Return Picking'

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = super(ReturnPicking,self)._prepare_move_default_values(return_line, new_picking)
        if return_line.move_id.purchase_req_line_id.transfer_line_ids and (new_picking.location_id.id != return_line.move_id.purchase_req_line_id.transfer_line_ids[0].trans_picking_type_id.default_location_src_id.id):
            vals['is_return'] = True
        else:vals['is_return'] = False  
        return vals       

