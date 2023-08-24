from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from pytz import timezone, UTC
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.addons import decimal_precision as dp
from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    Purchase.READONLY_STATES['waiting_committee'] = [('readonly', True)]

    @api.model
    def _default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return types[:1]


    pr_count =  fields.Integer(string='PR',compute='_prcount',store=True)
    rfq_count = fields.Integer(string="RFQ",compute='_get_rfqcount',store=True) 
    po_count =  fields.Integer(string='PO',compute='_get_pocount',store=True)
    disount = fields.Boolean("Discount",default=False)
    #purchase_foc = fields.One2many('purchase.foc','foc_id',string="FOC")
    #last_price = fields.Many2many('purchase.last.price','lst_id',string="Last Price",compute="_get_last_purchase_price")
    Discount = fields.Char("Discount by")
    request_id = fields.Many2one('purchase.req.rec')
    origin_rfq = fields.Many2one('purchase.order')
    purchase_transfer = fields.Many2one('purchase.req',string="Purchase Transfer")
    request_type = fields.Selection([('stock','For Stock'),('workshop','For Workshop'),('branch','For Branch'),('manufacture','For Manufacture')])
    purchase_representative = fields.Many2one('hr.employee',domain=[('pur_rep','=',True)],states=Purchase.READONLY_STATES)
    is_copy = fields.Boolean()
    is_copied = fields.Boolean()
    requisition_id = fields.Many2one('purchase.requisition', string='Purchase Agreement', copy=False,states=Purchase.READONLY_STATES)
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', states=Purchase.READONLY_STATES, default=_default_picking_type,
        help="This will determine operation type of incoming shipment")
    picking_count = fields.Integer(compute='_compute_picking', string='Picking count', default=0, store=True,compute_sudo=True)
    picking_ids = fields.Many2many('stock.picking', compute='_compute_picking', string='Receptions', copy=False, store=True,compute_sudo=True)
    is_shipped = fields.Boolean(compute="_compute_is_shipped",compute_sudo=True)
    total_amount = fields.Monetary(string='Total Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    total_discount = fields.Monetary(string='Discount Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    state = fields.Selection(selection_add=[('waiting_committee', 'Waiting Committee Approve')])
    committee_id = fields.Many2one('purchase.committee',copy=False)
    committee_line_ids = fields.One2many('purchase.order.committee','purchase_order_id')
    approve_date = fields.Datetime('Approve Date')
    member_format = fields.Char(compute='_compute_member_format', store=True)

    freight_cost_type = fields.Selection([("included", "Included"), ("excluded", "Excluded")], copy=False,
                                         default="included")
    freight_cost = fields.Float(string='Freight Cost', copy=False, compute='_compute_freight_cost')
    enclosures = fields.Text(
        string='Enclosures', copy=False
    )

    # @api.multi
    def _compute_freight_cost(self):
        for po in self:
            po.freight_cost = 0.0
            if po.freight_cost_type == 'excluded':
                purchase_landed_cost_ids = po.picking_ids.ids
                landed_cost_total = sum(
                    self.env['stock.landed.cost'].search([('picking_ids', 'in', purchase_landed_cost_ids)]).mapped(
                        'amount_total'))
                po.freight_cost = landed_cost_total

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = total_amount =total_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                total_discount += line.discount_amount
                total_amount += line.price_unit * line.product_qty
            order.update({
                'total_amount' : order.currency_id.round(total_amount), 
                'total_discount' : order.currency_id.round(total_discount),
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })
    # Cron Job to update picking
    @api.model
    def update_picking(self):
        ''' This method is called from a cron job. '''
        for rec in self.search([]):
            rec._compute_picking()

    # @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'waiting_committee']:
                continue
            if not order.is_copied:   
               order._copy_origin_rfq() 
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id._convert(
                            order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                #To Check Commite Approve
                if order.amount_total < self.env.user.company_id.currency_id._convert(
                            order.committee_id.limit_committee_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()):
                    order.button_approve()
                else:
                    committee_rec = order.committee_id.search([('is_default','=',True),('company_id','=',order.company_id.id)],limit=1)
                    if committee_rec and committee_rec.member_ids:
                        for member in committee_rec.member_ids:
                            order.committee_line_ids.sudo().create({
                                'member_id' : member.id,
                                'purchase_order_id':order.id,
                                'from_commite':True,
                            })
                        for other_member in committee_rec.other_member_ids:
                            order.committee_line_ids.sudo().create({
                                'member_id' : other_member.id,
                                'purchase_order_id':order.id,
                            })  
                        order.write({'committee_id': committee_rec.id})      
                            
                    order.write({'state': 'waiting_committee'})

            else:
                order.write({'state': 'to approve'})
        return True  

    def get_current_tz_time(self):
        tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        return UTC.localize(fields.Datetime.now()).astimezone(tz).replace(tzinfo=None)  

    def _check_committee_approve(self):
        if all(committe.decision == 'approve' for committe in self.committee_line_ids):
            return True
        elif  all(committe.decision == 'approve' for committe in self.committee_line_ids.filtered(lambda s:s.from_commite)) and \
            all(committe.decision == 'approve' or  committe.is_expired for committe in self.committee_line_ids.filtered(lambda s: not s.from_commite)) :
            return True
        else:
            return False    

    # @api.multi
    def set_commite_member(self):
        for order in self:
            if order.state not in ['draft', 'sent','waiting_committee']:
                raise UserError(_('Order Must Be RFQ To Set Committee'))
            committee_rec = order.committee_id.search([('is_default','=',True),('company_id','=',order.company_id.id)],limit=1)
            committees_list = order.committee_id.search([], order="limit_committee_amount desc")
            for rec in committees_list:
                if order.amount_total > rec.limit_committee_amount:
                    committee_rec = rec
                    break
            order.committee_id = committee_rec.id
            order.committee_line_ids.unlink()
            if committee_rec and committee_rec.member_ids:
                for member in committee_rec.member_ids:
                    order.committee_line_ids.sudo().create({
                        'member_id' : member.id,
                        'purchase_order_id':order.id,
                        'from_commite':True,
                    })
                for other_member in committee_rec.other_member_ids:
                        order.committee_line_ids.sudo().create({
                            'member_id' : other_member.id,
                            'purchase_order_id':order.id,
                        })    
                # if order.request_id and order.request_id.department_id and order.request_id.department_id.manager_id.user_id:
                #     order.committee_line_ids.sudo().create({
                #     'member_id' : order.request_id.department_id.manager_id.user_id.id,
                #     'purchase_order_id':order.id,
                #     'from_commite':True,
                #     })

            order.write({'state': 'waiting_committee'})
            order._compute_member_format()
            template_id = order.env.ref('purchase_enhanced.email_template_committe_approve')
            template_id.send_mail(order.id, force_send=True, raise_exception=True)
            order.message_post(subject=_('Requset Send To Committe Approve'),
                          body='Requset Sent Member\'s : %s' % (self.committee_line_ids.mapped('member_id.name')))


    @api.depends('committee_line_ids.member_id')
    def _compute_member_format(self):
        list_ids = []
        for rec in self:
            for member in rec.committee_line_ids.mapped('member_id.partner_id'):
                list_ids.append(str(member.id))
            rec.member_format = ','.join(list_ids)

    # @api.multi
    def _copy_origin_rfq(self):
        ctx = dict(self.env.context)
        ctx['is_copy'] = True
        for order in self:
            copied_order = order.with_context(ctx).copy()
            #Set Not Copied Fields
            copied_order.write({
                'name' : order.name,
                'origin' : order.origin,
                'partner_ref' : order.partner_ref,
                'date_order': order.date_order,
                'requisition_id': order.requisition_id.id,
                'invoice_status': 'no',
                'date_approve' : fields.Datetime.now(),
                'is_copy':True,
                'state':'done',   
            })
            order.write({'origin': copied_order.name,
                        'origin_rfq': copied_order.id,
                         'is_copied': True,
                         'name': self.env['ir.sequence'].next_by_code('purchase.order') or '/',
                         })

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New' and not self._context.get('is_copy',False):
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.rfq.order') or '/'
        return super(PurchaseOrder, self).create(vals)

    
    '''@api.one
    def _get_last_purchase_price(self):
        create_data_list = []
        for data in self.order_line:
            for line in self.env['purchase.order.line'].search([('id','!=',data.id),('product_id','=',data.product_id.id),('order_id.partner_id','=',self.partner_id.id)],order="name DESC",limit=1):
                if not self.last_price:
                    create_record = self.env['purchase.last.price'].create({
                                                        'product_id':line.product_id.id,
                                                        'price':line.price_unit,
                                                        'lst_id':self.id,
                                                    })
                    create_data_list.append(create_record.id)
                for last_data in self.last_price:
                    if last_data.product_id.id != line.product_id.id:
                        create_record = self.env['purchase.last.price'].create({
                                                        'product_id':line.product_id.id,
                                                        'price':line.price_unit,
                                                        'lst_id':self.id,
                                                    })
                        create_data_list.append(create_record.id)
        self.last_price = [(6,0, create_data_list)]'''
    # @api.multi
    @api.depends('purchase_transfer')
    def _prcount(self):
        for rec in self:
            rec.pr_count = len(rec.purchase_transfer)
    
    # @api.multi
    @api.depends('request_id','request_id.rfq_ref','request_id.rfq_ref.state')
    def _get_rfqcount(self):
        for rec in self:
            rec.rfq_count = len(rec.request_id.rfq_ref.filtered(lambda s:s.state == 'draft' or s.is_copy))
    
    # @api.multi
    @api.depends('request_id','request_id.rfq_ref','request_id.rfq_ref.state')
    def _get_pocount(self):
        for rec in self:
            rec.po_count = len(rec.request_id.rfq_ref.filtered(lambda s:s.state != 'draft' and not s.is_copy))
    
    def action_view_rfq(self):
        orders = self.request_id.rfq_ref.filtered(lambda s:s.state == 'draft' or s.is_copy).ids
        action = self.env.ref('purchase.purchase_rfq').read()[0]
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

    def action_view_po(self):
        orders = self.request_id.rfq_ref.filtered(lambda s:s.state != 'draft' and not s.is_copy).ids
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders)]
        elif len(orders) == 1:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = orders[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action     


    # @api.multi
    def action_view_picking(self):
        """ This function returns an action that display existing picking orders of given purchase order ids. When only one found, show the picking immediately.
        """
        pick_ids = self.mapped('picking_ids')
        if len(pick_ids) == 1:
            views = [(self.env.ref('purchase_enhanced.view_view_picking_form_receipts_in_po').id, 'form'),(self.env.ref('purchase_enhanced.vpicktree_purchase_order').id, 'tree')] 
            return {
                'name': _('Transfers'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'view_id': False,
                'views': views,
                'res_id': pick_ids.id,
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', pick_ids.ids)],
            }
        else:
            views = [(self.env.ref('purchase_enhanced.vpicktree_purchase_order').id, 'tree'), (self.env.ref('purchase_enhanced.view_view_picking_form_receipts_in_po').id, 'form')]
        return {
            'name': _('Transfers'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'view_id': False,
            'views': views,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', pick_ids.ids)],
        }

    # @api.multi
    def button_draft(self):
        self.write({'committee_id': False,'committee_line_ids':[(6, 0, [])]})
        return super(PurchaseOrder, self).button_draft()          

    # @api.multi
    def button_cancel(self):
        for order in self:
            #Check Invoices
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("Unable to cancel this purchase order. You must first cancel the related vendor bills."))
            #Stop Check Picking 
            #for pick in order.picking_ids:
            #    if pick.state == 'done':
            #        raise UserError(_('Unable to cancel purchase order %s as some receptions have already been done.') % (order.name))
            
            #Replace Check Picking By Check qty_received For Lines
            for order_line in order.order_line:
                if order_line.qty_received > 0:
                    raise UserError(_("Unable to cancel this purchase order. You must first Return All Receipt,Please Review Received Qty For Products."))
            
            # If the product is MTO, change the procure_method of the the closest move to purchase to MTS.
            # The purpose is to link the po that the user will manually generate to the existing moves's chain.
            if order.state in ('draft', 'sent', 'to approve'):
                for order_line in order.order_line:
                    if order_line.move_dest_ids:
                        move_dest_ids = order_line.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))
                        siblings_states = (move_dest_ids.mapped('move_orig_ids')).mapped('state')
                        if all(state in ('done', 'cancel') for state in siblings_states):
                            move_dest_ids.write({'procure_method': 'make_to_stock'})
                            move_dest_ids._recompute_state()

            for pick in order.picking_ids.filtered(lambda r: r.state not in ('cancel', 'done')):
                pick.action_cancel()

            order.order_line.write({'move_dest_ids':[(5,0,0)]})

        self.write({'state': 'cancel'})

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
              

    @api.depends('product_id')
    def _get_onhand_qty(self):
        for rec in self:
            rec.onhand = rec.product_id.qty_available

    onhand = fields.Float("On Hand",compute='_get_onhand_qty',store=True)
    #last_price_line = fields.One2many('purchase.last.price','lst_line_id',string="Last Price")
    pr_origin =fields.Many2one('purchase.req', string='P.R')
    purchase_req_line_id = fields.Many2one('purchase.req.line')
    purchase_req_rec_line_id = fields.Many2one('purchase.req.rec.line')
    work_order_id = fields.Char(string='Work Order')
    fleet_id_ref = fields.Reference(string='Fleet Ref',
     selection=[('fleet.vehicle','Vehicle'),('bsg_fleet_trailer_config','Trailer')])
    department_id = fields.Many2one('hr.department',string="Department",track_visibility='always')
    branches = fields.Many2one("bsg_branches.bsg_branches",string="Branch",track_visibility='always')
    fleet_num = fields.Char(string="Fleet",compute='_compute_fleet_ref_tag',store=True, track_visibility=True) 
    sequence2 = fields.Integer('No#',compute='_compute_line_sequence',
                                       store=True)
    discount_percent = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'),
        default=0.0) 
    discount_amount = fields.Float(string='Discount Amount', digits=dp.get_precision('Discount'),
        default=0.0) 
    free_qty_amount = fields.Float(string='Free Qty Amount', digits=dp.get_precision('Discount'),
        default=0.0)     
    qty_received_price = fields.Monetary(compute='_compute_qty_recieved_amount', string='Qty Received Price', store=True)                                          
    qty_invoiced_price = fields.Monetary(compute='_compute_qty_invoiced_amount', string='Qty Invoiced Price', store=True)

    is_copy = fields.Boolean(related='order_id.is_copy',store=True)
    is_copied = fields.Boolean(related='order_id.is_copied',store=True)
    free_qty = fields.Integer('Free Qty')

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
        }

    @api.depends('qty_received','price_unit', 'taxes_id','discount_percent')
    def _compute_qty_recieved_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            vals['price_unit'] = vals['price_unit'] * (1 - (line.discount_percent or 0.0) / 100.0)
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                line.qty_received,
                vals['product'],
                vals['partner'])
            line.update({
                'qty_received_price': taxes['total_included']
            })

    @api.depends('qty_invoiced','price_unit', 'taxes_id','discount_percent')
    def _compute_qty_invoiced_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            vals['price_unit'] = vals['price_unit'] * (1 - (line.discount_percent or 0.0) / 100.0)
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                line.qty_invoiced,
                vals['product'],
                vals['partner'])
            line.update({
                'qty_invoiced_price': taxes['total_included']
            })

    @api.depends('product_qty', 'price_unit', 'taxes_id','discount_percent')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            vals['price_unit'] = vals['price_unit'] * (1 - (line.discount_percent or 0.0) / 100.0)
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.onchange('price_unit','product_qty')
    def _onchange_product_price_unit(self):
        self._onchange_product_free_qty()
        self._onchange_fixed_discount()

    @api.onchange('free_qty')
    def _onchange_product_free_qty(self):
        if self.free_qty:
            if self.free_qty > self.product_qty:
                raise UserError(_('Free Qty should be less than Purchase Qty'))
            self.free_qty_amount = self.price_unit * self.free_qty
            self.discount_amount += self.free_qty_amount
            self._onchange_fixed_discount()

    @api.onchange('discount_percent')
    def _onchange_discount_percent(self):
        if self.discount_percent:
            if self.discount_percent > 100:
                raise UserError(_('Discount value should be less than 100'))
            self.discount_amount = (self.price_unit*self.product_qty) * (self.discount_percent / 100.0)
        elif self.discount_percent == 0.0:
            self.discount_amount = 0.0

    @api.onchange('discount_amount')
    def _onchange_fixed_discount(self):
        if self.discount_amount:
            if self.discount_amount > (self.price_unit*self.product_qty):
                raise UserError(_('Discount value should be less than Price'))
            self.discount_percent = (self.discount_amount / (self.price_unit*self.product_qty)) * 100


    # @api.multi
    @api.depends('order_id.order_line')
    def _compute_line_sequence(self):
        for rec in self:
            rec.sequence2 = (
                max(rec.order_id.mapped('order_line.sequence2') or [0]) + 1)  

    @api.depends('fleet_id_ref')
    def _compute_fleet_ref_tag(self):
        for rec in self:
            if rec.fleet_id_ref:
                if str(rec.fleet_id_ref).__contains__('fleet_trailer'):
                    rec.fleet_num = rec.fleet_id_ref.trailer_taq_no
                if str(rec.fleet_id_ref).__contains__('fleet.vehicle'):
                    rec.fleet_num = rec.fleet_id_ref.taq_number

 
class FOC(models.Model):
    _name = "purchase.foc"
    _description = "Purchase Foc"

    foc_id = fields.Many2one('purchase.order',string="Purchase Order")
    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float('Quantity')
    
    
class LP(models.Model):
    _name = "purchase.last.price"
    _description = "Purchase Last Price"

    lst_id = fields.Many2one('purchase.order',string="Purchase Order")
    lst_line_id = fields.Many2one('purchase.order.line',string="Purchase Order ")
    product_id = fields.Many2one('product.product', string='Product')
    name=fields.Char(related="product_id.name")
    price = fields.Float("Last Price")

class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition" 

    request_id = fields.Many2one('purchase.req.rec')   

class PurchaseCommittee(models.Model):
    _name = "purchase.committee"

    name = fields.Char(default='/',required=True)
    member_ids = fields.Many2many('res.users','res_users_committe_member_rel','committe_id','user_id','Members')
    other_member_ids = fields.Many2many('res.users','res_users_committe_other_member_rel','committe_id','user_id','Other Members')
    is_default = fields.Boolean()
    company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)
    limit_committee_amount = fields.Float(string='Purchase Committee Amount')

class PurchaseOrderCommittee(models.Model):
    _name = "purchase.order.committee"

    member_id = fields.Many2one('res.users',required=True)
    decision = fields.Selection([('approve','Approve'),('reject','Reject'),('not_set','Waiting')],default='not_set',required=True)
    comment = fields.Char('Reject Reason')
    purchase_order_id = fields.Many2one('purchase.order')
    is_member_current_user = fields.Boolean(compute='_check_current_user')
    from_commite = fields.Boolean(default=False)
    date_start = fields.Datetime('Start Date', default=fields.Datetime.now, required=True)
    duration = fields.Char('Duration', compute='_compute_duration')
    is_expired = fields.Boolean(compute='_compute_duration')
    decision_date = fields.Datetime('Decision Date')

    def _compute_duration(self):
        for rec in self:
            d1 = fields.Datetime.from_string(rec.date_start)
            d2 = fields.Datetime.from_string(fields.Datetime.now())
            if rec.purchase_order_id.state in ['purchase','done'] and rec.purchase_order_id.approve_date:
                d2 = fields.Datetime.from_string(rec.purchase_order_id.approve_date)
            diff = d2 - d1
            if round(diff.total_seconds() / 60.0, 2) > (60*24):
                rec.is_expired = True
            else:
                rec.is_expired = False    
            
            #if (blocktime.loss_type not in ('productive', 'performance')) and blocktime.workcenter_id.resource_calendar_id:
            #    r = blocktime.workcenter_id.get_work_days_data(d1, d2)['hours']
            #    blocktime.duration = round(r * 60, 2)
            #else:
            rec.duration = diff
            

    # @api.multi
    def _check_current_user(self):
        for rec in self:
            if rec.member_id.id == self.env.user.id:
                rec.is_member_current_user = True

    # @api.multi
    def accept(self):
        for rec in self:
            rec.sudo().decision = 'approve'
            rec.sudo().decision_date = fields.Datetime.now()
            rec.sudo().purchase_order_id.message_post(subject=_('Mebmer Approve Purchase Order '),
                                      body='Member %s Approve Purchase Order In %s' % (str(self.env.user.name),str(fields.Datetime.now())))
            #if rec.purchase_order_id._check_committee_approve():
            #    rec.purchase_order_id.button_confirm()
   
    # @api.multi
    def reject(self):
        for rec in self:
            rec.sudo().decision = 'reject' 
            rec.sudo().decision_date = fields.Datetime.now()    
            rec.sudo().purchase_order_id.message_post(subject=_('Mebmer Reject Purchase Order '),
                                      body='Member %s Reject Purchase Order In %s' % (str(self.env.user.name),str(fields.Datetime.now()))) 


    @api.model
    def create(self, vals):
        res = super(PurchaseOrderCommittee, self).create(vals)
        template_id = res.env.ref('purchase_enhanced.email_template_committe_approve')
        template_id.send_mail(res.purchase_order_id.id, force_send=True, raise_exception=True,email_values={'email_to': res.member_id.email})
        res.purchase_order_id.message_post(subject=_('Requset Send To Committe Approve'),
                        body='Requset Sent Member\'s : %s' % (res.member_id.name))
        return res

    # @api.multi
    def unlink(self):
        for line in self:
            if line.from_commite:
                raise UserError(_('You Can\'t Delete Main Member.'))
        return super(PurchaseOrderCommittee, self).unlink()

class ResCompany(models.Model):
    _inherit = 'res.company'

    limit_committee_amount = fields.Float(string='Purchase Committee Amount')
    po_required_in_receipt = fields.Boolean(string='PO Required In Receipt')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    limit_committee_amount = fields.Float(string='Purchase Committee Amount',related='company_id.limit_committee_amount',store=True,readonly=False)    
