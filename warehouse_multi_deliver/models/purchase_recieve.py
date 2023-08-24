# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
class PurchaseRequisitionReceived(models.Model):
    _inherit = 'purchase.req.rec'



    # @api.multi
    def purchase_order(self,requisition_id=False):
        #To Add Deliver To Line 
        list_2 = []
        vendors = []
        for rec in self:
            if len(rec.rfq_ref) > 1:
                raise UserError(_("RFQ Already Created"))
            if rec.is_multiple_vendor and not rec.vendor_ids:
                    raise UserError(_("You Select Multi Vendor ,Please Add Vendors"))
            elif not rec.is_multiple_vendor and not self.vendor_id:
                    raise UserError(_("Please Select Vendor First"))            
            else:
                if rec.is_multiple_vendor and rec.vendor_ids:
                    vendors = rec.vendor_ids.ids
                elif  rec.vendor_id:
                    vendors.append(rec.vendor_id.id)
                if rec.preq_rec_line:
                    for v in vendors:
                        res = self.env['purchase.order'].create({
                                'partner_id':v,
                                'origin':rec.name,
                                'requisition_id' : requisition_id,
                                'request_id':rec.id,
                                'purchase_transfer':rec.purchase_transfer.id,
                                #'multi_deliver':True,
                                'request_type' : rec.request_type,
                            })
                        for s in rec.preq_rec_line:
                            fleet_ref = False
                            if s.fleet_id_ref:
                                if str(s.fleet_id_ref).__contains__('fleet_trailer'):
                                    fleet_ref = str("bsg_fleet_trailer_config")+","+str(s.fleet_id_ref.id)
                                if str(s.fleet_id_ref).__contains__('fleet.vehicle'):
                                    fleet_ref = str("fleet.vehicle")+","+str(s.fleet_id_ref.id)
                            if s.product_id.type  != 'service':
                                res.order_line.create({
                                        'order_id':res.id,
                                        'product_id':s.product_id.id,
                                        'product_qty':s.qty,
                                        'name':s.name + "/" + s.product_id.name,
                                        'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                        'product_uom':s.product_id.uom_id.id,
                                        'product_uom_qty':s.qty,
                                        'onhand':s.onhand,
                                        'price_unit':s.product_id.list_price,
                                        'pr_origin':s.purchase_req_id.id,
                                        'purchase_req_line_id': s.purchase_req_line_id.id,
                                        'account_analytic_id':s.analytic_account_id.id,
                                        'work_order_id': s.work_order_id,
                                        'fleet_id_ref' : fleet_ref,
                                        'department_id': s.department_id.id,
                                        'branches': s.branches.id,
                                        'deliver_line_ids':[(0, 0, {
                                                'name':s.name + "/" + s.product_id.name,
                                                'product_id':s.product_id.id,
                                                'requsted_qty':s.qty,
                                                'picking_type_id':s.deliver_to.id,
                                                'order_id':res.id,
                                                'purchase_req_line_id': s.purchase_req_line_id.id,
                                                'analytic_account_id':s.analytic_account_id.id,
                                                'work_order_id': s.work_order_id,
                                                'fleet_id_ref' : fleet_ref,
                                                'department_id':rec.department_id.id,
                                                'branch_id': rec.branches.id,
                                                'purchase_req_id': s.purchase_req_id.id,
                                                })],
                                        })     
                            elif s.product_id.type  == 'service':
                                res.order_line.create({
                                        'order_id':res.id,
                                        'product_id':s.product_id.id,
                                        'product_qty':s.qty,
                                        'name':s.name + "/" + s.product_id.name,
                                        'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                        'product_uom':s.product_id.uom_id.id,
                                        'product_uom_qty':s.qty,
                                        'onhand':s.onhand,
                                        'price_unit':s.product_id.list_price,
                                        'pr_origin':s.purchase_req_id.id,
                                        'purchase_req_line_id': s.purchase_req_line_id.id,
                                        'account_analytic_id':s.analytic_account_id.id,
                                        'work_order_id': s.work_order_id,
                                        'fleet_id_ref': fleet_ref,
                                        'department_id': s.department_id.id,
                                        'branches': s.branches.id,
                                        })     
                                             

class PurchaseRequisitionReceivedLine(models.Model):
    _inherit = 'purchase.req.rec.line'

    added_to_rfq = fields.Boolean()


