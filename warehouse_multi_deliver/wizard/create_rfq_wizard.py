# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class CreateRfqWizard(models.TransientModel):
    _name = 'create.rfq.wizard'
    _description = 'Create Rfq Wizard'

    @api.model
    def _get_purchase_request_id(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        if active_model == 'purchase.req.rec':
            purchase_request_id = self.env['purchase.req.rec'].browse(int(active_id))
            if purchase_request_id.state == 'cancel':
                raise UserError(_('This Order Is Canceled'))
            # if any(line.state != 'cancel' and  line.product_id.type != 'service' and not line.deliver_to for line in purchase_request_id.preq_rec_line):
            #     raise UserError(_("Please Add Deliver To For Lines"))
            return active_id
        else:
            raise UserError(_('This Wizar Must Be Called From Purchase Recieve Model'))

    # @api.multi
    def _get_purchase_request_ids(self):
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        prr_ids = []
        if active_model == 'purchase.req.rec':
            purchase_request_id = self.env['purchase.req.rec'].search([('id', 'in', active_ids)])
            for purchase in purchase_request_id:
                if purchase.state == 'cancel':
                    raise UserError(_('This Order Is Canceled'))
                # if any(line.state != 'cancel' and line.product_id.type != 'service' and not line.deliver_to for line in
                #        purchase.preq_rec_line):
                #     raise UserError(_("Please Add Deliver To For Lines"))
                prr_ids.append(purchase.id)
            return prr_ids
        else:
            raise UserError(_('This Wizar Must Be Called From Purchase Recieve Model'))
    purchase_request_id = fields.Many2one('purchase.req.rec',default=_get_purchase_request_id)   
    purchase_request_line_ids = fields.Many2many('purchase.req.rec.line','create_rfq_purchase_line_rel','create_rfq_id','rec_line_id')
    vendor_id = fields.Many2one('res.partner', string='Vendor',domain=[('supplier_rank','>',0)],track_visibility='always')
    is_multiple_vendor = fields.Boolean(string="IS Multi Vendor",track_visibility='always') 
    vendor_ids = fields.Many2many('res.partner',domain=[('supplier_rank','>',0)], string='Vendors',track_visibility='always')
    purchase_request_ids = fields.Many2many('purchase.req.rec', default=_get_purchase_request_ids)

    def purchase_order(self):
        #To Add Deliver To Line   
        list_2 = []
        vendors = []
        for rec in self:
            if not rec.purchase_request_line_ids:
                raise UserError(_("Please At Least Choose One Line"))
            if any(line.state != 'cancel' and line.product_id.type != 'service' and not line.deliver_to for line in rec.purchase_request_line_ids):
                raise UserError(_("Please Add Deliver To For Lines"))   
            if any(rec.purchase_request_line_ids.mapped('added_to_rfq')):
                raise UserError(_("Already Purchase Qty For Lines"))
            if sum(rec.purchase_request_line_ids.mapped('qtmr')) <=0:
                raise UserError(_("Sorry, At Least One Line Must Have Qty More Than 0"))
            if rec.is_multiple_vendor and not rec.vendor_ids:
                    raise UserError(_("You Select Multi Vendor ,Please Add Vendors"))
            elif not rec.is_multiple_vendor and not self.vendor_id:
                    raise UserError(_("Please Select Vendor First"))            
            else:
                if rec.is_multiple_vendor and rec.vendor_ids:
                    vendors = rec.vendor_ids.ids
                elif  rec.vendor_id:
                    vendors.append(rec.vendor_id.id)
                if rec.purchase_request_line_ids:
                    for v in vendors:
                        res = self.env['purchase.order'].create({
                                'partner_id':v,
                                'origin':rec.purchase_request_id.name,
                                #'requisition_id' : requisition_id,
                                'request_id':rec.purchase_request_id.id,
                                'purchase_transfer':rec.purchase_request_id.purchase_transfer.id,
                                'request_type' : rec.purchase_request_id.request_type,
                            })  
                        for s in rec.purchase_request_line_ids:
                            fleet_ref = False
                            if s.fleet_id_ref:
                                if str(s.fleet_id_ref).__contains__('fleet_trailer'):
                                    fleet_ref = str("bsg_fleet_trailer_config")+","+str(s.fleet_id_ref.id)
                                if str(s.fleet_id_ref).__contains__('fleet.vehicle'):
                                    fleet_ref = str("fleet.vehicle")+","+str(s.fleet_id_ref.id)
                            if s.qtmr <=0:
                                continue
                            if s.product_id.type  != 'service':
                                res.order_line.create({
                                        'order_id':res.id,
                                        'purchase_req_rec_line_id':s.id,
                                        'product_id':s.product_id.id,
                                        'product_qty':s.qtmr,
                                        'name':s.name + "/" + s.product_id.name,
                                        'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                        'product_uom':s.product_id.uom_id.id,
                                        'product_uom_qty':s.qtmr,
                                        'onhand':s.onhand,
                                        'price_unit':s.product_id.list_price,
                                        'pr_origin':s.purchase_req_id.id,
                                        'purchase_req_line_id': s.purchase_req_line_id.id,
                                        'analytic_distribution': {s.analytic_account_id.id: 100},
                                        'work_order_id': s.work_order_id,
                                        'fleet_id_ref' : fleet_ref,
                                        'department_id': s.department_id.id,
                                        'branches': s.branches.id,
                                        'deliver_line_ids':[(0, 0, {
                                                'name':s.name + "/" + s.product_id.name,
                                                'product_id':s.product_id.id,
                                                'requsted_qty':s.qtmr,
                                                'picking_type_id':s.deliver_to.id,
                                                'order_id':res.id,
                                                'purchase_req_line_id': s.purchase_req_line_id.id,
                                                'analytic_account_id':s.analytic_account_id.id,
                                                'work_order_id': s.work_order_id,
                                                'fleet_id_ref' : fleet_ref,
                                                'department_id':s.department_id.id,
                                                'branch_id': s.branches.id,
                                                'purchase_req_id': s.purchase_req_id.id,
                                                'purchase_req_rec_line_id':s.id,
                                                })],
                                        })     
                            elif s.product_id.type  == 'service':
                                res.order_line.create({
                                        'order_id':res.id,
                                        'purchase_req_rec_line_id':s.id,
                                        'product_id':s.product_id.id,
                                        'product_qty':s.qtmr,
                                        'name':s.name + "/" + s.product_id.name,
                                        'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                        'product_uom':s.product_id.uom_id.id,
                                        'product_uom_qty':s.qtmr,
                                        'onhand':s.onhand,
                                        'price_unit':s.product_id.list_price,
                                        'pr_origin':s.purchase_req_id.id,
                                        'purchase_req_line_id': s.purchase_req_line_id.id,
                                        'analytic_distribution': {s.analytic_account_id.id: 100},
                                        'work_order_id': s.work_order_id,
                                        'fleet_id_ref' : fleet_ref,
                                        'department_id': s.department_id.id,
                                        'branches': s.branches.id,
                                        })
                    #New Requirement Can Create Rfq More Than One Time For Line So Commit Next Line          
                    #rec.purchase_request_line_ids.write({'added_to_rfq':True})
                    rec.purchase_request_line_ids.write({'qtmr':0})       
                    



                                             
