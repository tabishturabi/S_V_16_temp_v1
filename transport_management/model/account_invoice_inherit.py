# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.move"
    
    #for checking trasport state done or not
    # @api.multi
    def write(self,vals):
        for invoice in self:
            if invoice.move_type == 'in_refund' and invoice.return_vendor_tranport_id and vals.get('state') == 'paid':
                invoice.return_vendor_tranport_id.write({'state' : 'cancel'})
            if invoice.move_type == 'out_refund' and invoice.return_customer_tranport_id and vals.get('state') == 'paid':
                invoice.return_customer_tranport_id.write({'state' : 'cancel'})
        res = super(AccountInvoice, self).write(vals)
        return res

    return_vendor_tranport_id = fields.Many2one('transport.management')
    return_customer_tranport_id = fields.Many2one('transport.management')

    transport_cus_inv_id = fields.Many2one('transport.management', string='Transport Customer Inv')
    transport_management_ids = fields.One2many('transport.management','invoice_id','Transport Management Ids')
