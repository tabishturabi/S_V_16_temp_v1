# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CloseWayBill(models.TransientModel):
    _name = "close.way.bill"

    @api.model
    def default_get(self, fields_list):
        defaults = super(CloseWayBill, self).default_get(fields_list)
        defaults['way_bill_id'] = self.env.context.get('bayan_way_bill_id')
        return defaults

    way_bill_id = fields.Char("Way Bill ID")
    actual_delivery_date = fields.Date("Actual Delivery Date")

    
    def action_close(self):
        print("adasd")