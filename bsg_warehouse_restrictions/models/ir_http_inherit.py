# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        res = super(IrHttp, self).session_info()
        res['warehouse-id'] = user.stock_warehouse_id.id if request.session.uid else None
        res['user_warehouse'] = {'current_warehouse': (user.stock_warehouse_id.id, user.stock_warehouse_id.name), 'allowed_warehouse': [(warehouse.id, warehouse.name) for warehouse in user.stock_warehouse_ids]},
        return res
