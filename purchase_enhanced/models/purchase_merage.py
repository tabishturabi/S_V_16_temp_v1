# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseRequisitionMerge(models.TransientModel):
    _name = 'purchase.req.merge'
    _inherit = 'purchase.req'
    _description = "Merge RFQ"

    test = fields.Boolean()
    
    partner_id = fields.Many2one('res.partner', string='Vendor')
    
    @api.model
    def default_get(self, fields):
        rec = super(PurchaseRequisitionMerge, self).default_get(fields)
        
        partner_list = []
        for data in self.env[self._context['active_model']].search([('id','in',self._context['active_ids'])]):
            partner_list.append(data.vendor_id.id)
        partner_list = list(set(partner_list))
        if len(partner_list) == 1:
            rec['partner_id'] = partner_list[0]
        return rec

    def merge_rfq(self):
        #request rfq
        partner_list = []
        state = []
        origin_char = ''
        for data in self.env[self._context['active_model']].search([('id','in',self._context['active_ids'])]):
            if data.vendor_id:
                partner_list.append(data.vendor_id.id)
            origin_char =   str(data.name) + ',' + str(origin_char) 
            state.append(data.state)
        partner_list = list(set(partner_list))

        if len(partner_list) == 0:
            partner_list.append(self.partner_id.id)

        if 'done' in state:
            raise UserError(_("Be Sure Request not Done..!"))
        if len(partner_list) == 1:
            purchase_order = self.env['purchase.order'].create({'partner_id' : partner_list[0],'origin' : origin_char[0:-1]})
            for data in self.env[self._context['active_model']].search([('id','in',self._context['active_ids'])]):
                for inner_data in data.preq_rec_line:
                    search_id = self.env['purchase.order.line'].search([('product_id','=',inner_data.product_id.id),('order_id','=',purchase_order.id)])
                    if search_id:
                        search_id.write({'product_uom_qty': search_id.product_uom_qty + inner_data.qty,'product_qty' : search_id.product_qty + inner_data.qty})
                    else:
                        stock =  self.env['stock.quant'].search([('product_id','=',inner_data.product_id.id),('location_id.usage','=','internal')],limit=1)
                        self.env['purchase.order.line'].create({'product_id':inner_data.product_id.id,
                                   'product_qty':inner_data.qty,
                                   'name':inner_data.product_id.name,
                                   'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                   'product_uom':inner_data.product_id.uom_id.id,
                                   'product_uom_qty':inner_data.qty,
                                   'onhand':stock.quantity,
                                   'price_unit':inner_data.product_id.list_price,
                                   'pr_origin':origin_char[0:-1],
                                   'order_id' : purchase_order.id,
                                   })                                
                data.write({'rfq_ref' : purchase_order.id,'state':'done'})
        else:
            raise UserError(_("Be Sure that Merger Request Have Same vendor..!"))

        # self.with_context(context)
   
