# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone, UTC



class PurchaseRequisitionReceived(models.Model):
    _name = 'purchase.req.rec'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Purchase Req Rec"
    _order = 'date_pr desc'

    name = fields.Char(track_visibility='always')
    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.user.company_id.id)
    date_pr = fields.Datetime("Date",default=fields.Datetime.now,track_visibility='always')
    purchase_transfer = fields.Many2one('purchase.req',string="Purchase Request",track_visibility='always')
    purchase_stock_tran = fields.Many2one('purchase.transfer',string="Purchase Transfer",track_visibility='always')
    partner_id = fields.Many2one('res.partner', string='Requester Name',default=lambda self: self.env.user.partner_id,track_visibility='always')
    department_id = fields.Many2one('hr.department',string="Department",default=lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id,track_visibility='always')
    preq_rec_line = fields.One2many('purchase.req.rec.line','preq_rec',string="Purchase Request Received Line",track_visibility='always')
    branches = fields.Many2one("bsg_branches.bsg_branches",string="Branch",track_visibility='always')
    note = fields.Text('Terms and conditions',track_visibility='always')   
    rfq_ref = fields.One2many('purchase.order','request_id',string="Request For Quotation")
    agreement_id = fields.One2many('purchase.requisition','request_id','Purchase Agreement')
    vendor_id = fields.Many2one('res.partner', string='Vendor',domain=[('supplier_rank','>',0)],track_visibility='always')
    is_multiple_vendor = fields.Boolean(string="IS Multi Vendor",track_visibility='always') 
    vendor_ids = fields.Many2many('res.partner',domain=[('supplier_rank','>',0)], string='Vendors',track_visibility='always')
    to_close = fields.Boolean('To Close',compute="compute_to_close")
    state = fields.Selection([
        ('tsub', 'To Submit'),
        ('tapprove', 'To Approve'),
        ('approve', 'Approved'),
         ('open', 'Open'),('close', 'Close'),
        ('reject' , 'Reject'), ('cancel', 'Cancel'),
        ('done', 'Done')],  string='States', default='approve',track_visibility='always')
    
    request_type = fields.Selection([('stock','For Stock'),('workshop','For Workshop'),('branch','For Branch')],required=True,track_visibility='always')    
    po_count =  fields.Integer(string='PO',compute='_pocount',store=True)
    rfq_count = fields.Integer(string="RFQ",compute='_rfqcount',store=True) 
    address_to = fields.Many2one('stock.location','Deliver Address')
    pr_count =  fields.Integer(string='PR',compute='_prcount')
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')

    def get_current_tz_time(self):
        tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        return UTC.localize(fields.Datetime.now()).astimezone(tz).replace(tzinfo=None)

    # @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('purchase_enhanced.action_attachment')
        return res

    # @api.multi
    def _compute_attachment_number(self):
        for rec in self:
            rec.attachment_number = self.env['ir.attachment'].search_count(
                [('res_model', '=', 'purchase.req'), ('purchase_req_id', '=', rec.purchase_transfer.id)])
    # @api.multi
    @api.depends('purchase_transfer')
    def _prcount(self):
        for rec in self:
            rec.pr_count = len(rec.purchase_transfer)

    def order_close(self):
        self.write({'state':'close'})
        
    def compute_to_close(self):
        for rec in self:
            rec.to_close = False
            if all(s.qty_received == s.qty_po for s in rec.preq_rec_line):
                rec.to_close = True

    # @api.multi
    def purchase_order(self,requisition_id=False):
        list_2 = []
        vendors = []
        for rec in self:
            if len(rec.rfq_ref) >= 1:
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
                for s in rec.preq_rec_line:
                    fleet_ref = False
                    if s.fleet_id_ref:
                        if str(s.fleet_id_ref).__contains__('fleet_trailer'):
                            fleet_ref = str("bsg_fleet_trailer_config")+","+str(s.fleet_id_ref.id)
                        if str(s.fleet_id_ref).__contains__('fleet.vehicle'):
                            fleet_ref = str("fleet.vehicle")+","+str(s.fleet_id_ref.id)
                    list_2.append({'product_id':s.product_id.id,
                            'product_qty':s.qty,
                            'name':s.name,
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
                                })
            if(len(list_2) > 0):
                    for v in vendors:
                        res = self.env['purchase.order'].create({
                                'partner_id':v,
                                'origin':rec.name,
                                'requisition_id' : requisition_id,
                                'request_id':rec.id,
                                'purchase_transfer':self.purchase_transfer.id,
                                'order_line':[(0, 0, s)for s in list_2],
                                'request_type' : rec.request_type,
                            })                 

    # @api.multi
    def purchase_requisition_order(self):
        list_2 = []
        for rec in self:
            if len(rec.agreement_id) > 1:
                raise UserError(_("Agreement Already Created")) 
            if rec.is_multiple_vendor and not rec.vendor_ids:
                    raise UserError(_("You Select Multi Vendor ,Please Add Vendors"))
            elif not rec.is_multiple_vendor and not self.vendor_id:
                    raise UserError(_("Please Select Vendor First"))            
        else:
            for s in rec.preq_rec_line:
                list_2.append({
                        'product_id':s.product_id.id,
                        'product_qty':s.qty,
                        'product_uom':s.product_id.uom_id.id,
                        'price_unit':s.product_id.list_price,
                        'account_analytic_id':s.analytic_account_id.id,
                        'scheduled_date':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                            })
        if(len(list_2) > 0):
                res = self.env['purchase.requisition'].create({
                        'origin':rec.name,
                        'request_id':rec.id,
                        #'picking_type_id': self.deliver_to.id,
                        'line_ids':[(0, 0, s)for s in list_2],
                    })
                rec.purchase_order(res.id)


    # @api.multi
    @api.depends('rfq_ref','rfq_ref.state')
    def _pocount(self):
        for rec in self:
            rec.po_count = len(rec.rfq_ref.filtered(lambda s:s.state != 'draft' and not s.is_copy))
    
    # @api.multi
    @api.depends('rfq_ref','rfq_ref.state')
    def _rfqcount(self):
        for rec in self:
            rec.rfq_count = len(rec.rfq_ref.filtered(lambda s:s.state == 'draft' or s.is_copy))

    def action_view_rfq(self):
        orders = self.rfq_ref.filtered(lambda s:s.state == 'draft' or s.is_copy).ids
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders)]
        elif len(orders) == 1:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = orders[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


    def action_view_po(self):
        orders = self.rfq_ref.filtered(lambda s:s.state != 'draft' and not s.is_copy).ids
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders)]
        elif len(orders) == 1:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = orders[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action    

    def action_view_pr(self):
        orders = self.purchase_transfer.ids
        action = self.env.ref('purchase_enhanced.action_purchase_advisor').read()[0]
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders)]
        elif len(orders) == 1:
            action['views'] = [(self.env.ref('purchase_enhanced.view_purchase_req_advisor_form').id, 'form')]
            action['res_id'] = orders[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action 

    # @api.multi
    def set_to_cancel(self):
        for rec in self:
            rec.preq_rec_line.set_to_cancel()
            rec.write({'state':'cancel'})

    # @api.multi
    def set_to_open(self):
        for rec in self:
            if rec.state != 'cancel':
                raise UserError(_("Sorry,This Order must be in Canceled state"))
            rec.preq_rec_line.set_to_open()
            rec.write({'state':'open'})        

class PurchaseRequisitionLineRec(models.Model):
    _name = 'purchase.req.rec.line'
    _description = "Purchase Req Rec Line"
    _order = 'date_pr desc'

    preq_rec = fields.Many2one('purchase.req.rec',string="Purchase Request")
    product_id = fields.Many2one('product.product', string='Requested Product')
    product_type = fields.Selection([('consu', 'Consumable'),('service', 'Service'),
    ('product','Storeable')], string='Product Type', related='product_id.type', store=True)
    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.user.company_id.id)
    qty = fields.Float('Requested Qty')
    name = fields.Text(string='Description', required=True)
    onhand = fields.Float("Qty Onhand")
    qtmr = fields.Float("Qty to make rfq")
    purchase_req_id = fields.Many2one('purchase.req',string="P.R")
    purchase_req_line_id = fields.Many2one('purchase.req.line')
    purchase_transfer_line = fields.Many2one('purchase.transfer.line')
    work_order_id = fields.Char(string='Work Order')
    fleet_id_ref = fields.Reference(string='Fleet Ref',
     selection=[('fleet.vehicle','Vehicle'),('bsg_fleet_trailer_config','Trailer')])
    analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    qty_po = fields.Float(related='purchase_req_line_id.qty_po', string="PO Qty",store=True)
    qty_rfq = fields.Float(related='purchase_req_line_id.qty_rfq', string="Rfq Qty",store=True)
    qty_received = fields.Float(related='purchase_req_line_id.qty_received', string="Received Qty",store=True)
    qty_returned = fields.Float(related='purchase_req_line_id.qty_returned',string="Returned Qty",store=True)
    qty_net_received = fields.Float(related='purchase_req_line_id.qty_net_received',string="Net Received Qty",store=True)
    deliver_to = fields.Many2one('stock.picking.type')
    iss_qty = fields.Float(string="ISS Qty",related='purchase_req_line_id.iss_qty',store=True)
    analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Acount")

    partner_id = fields.Many2one('res.partner',related='preq_rec.partner_id',store=True,string='Requester Name',track_visibility='always')
    requester_id = fields.Many2one('res.users','User',related='purchase_req_line_id.requester_id',store=True,track_visibility='always')
    department_id = fields.Many2one('hr.department',string="Department",related='preq_rec.department_id',store=True,track_visibility='always')
    branches = fields.Many2one("bsg_branches.bsg_branches",string="Branch",related='preq_rec.branches',store=True,track_visibility='always')
    date_pr = fields.Datetime("Date",related='preq_rec.date_pr',store=True,track_visibility='always')
    state = fields.Selection([
        ('tsub', 'To Submit'),
        ('tapprove', 'To Approve'),
        ('approve', 'Approved'),
            ('open', 'Open'),('close', 'Close'),('cancel', 'Cancel'),
        ('reject' , 'Reject'),
        ('done', 'Done')],  string='States',default='open',track_visibility='always')
    request_type = fields.Selection([('stock','For Stock'),('workshop','For Workshop'),('branch','For Branch')],related='preq_rec.request_type',store=True,track_visibility='always')
    fleet_num = fields.Char(string="Fleet",compute='_compute_fleet_ref_tag',store=True, track_visibility=True) 
    sequence = fields.Integer('No#')

    @api.depends('fleet_id_ref')
    def _compute_fleet_ref_tag(self):
        for rec in self:
            if rec.fleet_id_ref:
                if str(rec.fleet_id_ref).__contains__('fleet_trailer'):
                    rec.fleet_num = rec.fleet_id_ref.trailer_taq_no
                if str(rec.fleet_id_ref).__contains__('fleet.vehicle'):
                    rec.fleet_num = rec.fleet_id_ref.taq_number


    # @api.multi
    def _compute_iss_qty(self):
        for line in self:
            reciev_total = 0.0
            return_total = 0.0
            stock_picking = self.env['stock.picking'].search([('purchase_req_id','=',line.purchase_req_id.id),('state','!=','cancel')])
            if stock_picking:
                for pick in stock_picking:
                    reciev_total += sum(pick.move_ids_without_package.filtered(lambda m: m.product_id == line.product_id and m.state == 'done' and not m.is_return).mapped('quantity_done'))
                    return_total += sum(pick.move_ids_without_package.filtered(lambda m: m.product_id == line.product_id and m.state == 'done' and m.is_return).mapped('quantity_done'))
            line.iss_qty = reciev_total - return_total
    # @api.multi
    def set_to_cancel(self):
        for rec in self:
            if rec.qty_rfq > 0:
                raise UserError(_("Sorry,You Can't Close Line Has Rfq , cancel the rfq first"))
            rec.purchase_req_line_id.filtered(lambda s: not s.iss_qty and s.state !='done').write({'state':'cancel'})
            rec.purchase_req_line_id.transfer_line_ids.filtered(lambda s: not s.iss_qty and s.state !='done').write({'state':'cancel'})
            rec.write({'state':'cancel'})

    # @api.multi
    def set_to_open(self):
        for rec in self:
            if rec.state != 'cancel':
                raise UserError(_("Sorry,This Order Not Canceled"))
            rec.purchase_req_line_id.filtered(lambda s:s.state == 'cancel').write({'state':'open'})
            rec.purchase_req_line_id.transfer_line_ids.filtered(lambda s: s.state == 'cancel').write({'state':'open'})
            rec.write({'state':'open'})        


            
