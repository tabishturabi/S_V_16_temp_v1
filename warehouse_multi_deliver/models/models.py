# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare

from odoo.exceptions import UserError

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase


from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    multi_deliver = fields.Boolean(string="Separate Deliver Per Line")
    deliver_line_ids = fields.One2many('deliver.to.line','order_id',copy=True)



    # @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent','waiting_committee']:
                continue
            committees_list = order.committee_id.search([], order="limit_committee_amount desc")
            if len(committees_list) > 0 and committees_list[-1].limit_committee_amount !=0 and order.amount_total > committees_list[-1].limit_committee_amount:
                if order.amount_total >= self.env.user.company_id.currency_id._convert(
                        order.committee_id.limit_committee_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()):
                            if not order.committee_id:
                                order.set_commite_member()
                                continue
                            else:
                                if not order._check_committee_approve():
                                    raise UserError(_("You Must Wait Other Memeber's Decisions"))
            if not order.is_copied:   
               order._copy_origin_rfq() 
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id._convert(
                            order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                  
                    order.button_approve()
                    order.write({'approve_date':fields.Datetime.now()})
            else:
                order.write({'state': 'to approve'})
            for line in order.order_line:
                if line.purchase_req_rec_line_id:
                    if line.purchase_req_rec_line_id.qty_po >= line.purchase_req_rec_line_id.qty:
                        line.purchase_req_rec_line_id.write({'added_to_rfq':True})
            template_id = order.env.ref('warehouse_multi_deliver.email_template_for_purchase_order_approve')
            template_id.send_mail(order.id, force_send=True, raise_exception=True)
            order.message_post(subject=_('Notification Send To Requester'),
                          body='Approve Notification Send To Requester : %s' % (order.purchase_transfer.partner_id.name))            
        return True

    # @api.multi
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        if not self.multi_deliver:
            super(PurchaseOrder, self)._create_picking()
        else:
            for picking in self.deliver_line_ids.mapped('picking_type_id'):
                if any([ptype in ['product', 'consu'] for ptype in self.deliver_line_ids.filtered(lambda s: s.picking_type_id.id== picking.id).mapped('product_id.type')]):
                    res = self._prepare_to_multi_picking(picking)
                    created_picking = StockPicking.create(res)
                    for line in self.deliver_line_ids.filtered(lambda s: s.picking_type_id.id== picking.id):
                        moves = line._create_stock_moves(created_picking)
                        moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                        seq = 0
                        for move in sorted(moves, key=lambda move: move.date_expected):
                            seq += 5
                            move.sequence = seq
                        moves._action_assign()
                        created_picking.message_post_with_view('mail.message_origin_link',
                                                   values={'self': created_picking, 'origin': line.order_id},
                                                   subtype_id=self.env.ref('mail.mt_note').id)
        return True


    @api.model
    def _prepare_to_multi_picking(self,picking_type_id):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
        return {
            'picking_type_id': picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': picking_type_id.default_location_dest_id.id,
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
            'request_type':self.request_type,
        }

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
            for deliver_line in copied_order.deliver_line_ids:
                purchase_line = copied_order.order_line.filtered(lambda m: m.product_id.id == deliver_line.product_id.id)[0]
                deliver_line.purchase_order_line = purchase_line.id
            order.write({'origin': copied_order.name,
                        'origin_rfq': copied_order.id,
                         'is_copied': True,
                         'name': self.env['ir.sequence'].next_by_code('purchase.order') or '/',
                         })


class DeliverToLine(models.Model):
    _name = 'deliver.to.line'

    name = fields.Char()
    purchase_order_line = fields.Many2one('purchase.order.line',required=True)
    product_id = fields.Many2one('product.product',required=True,related='purchase_order_line.product_id')
    requsted_qty = fields.Integer(required=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To',required=True,domain="[('code','=','incoming')]")
    order_id = fields.Many2one('purchase.order', string='Order Reference', index=True, required=True, ondelete='cascade')
    state = fields.Selection(related='order_id.state', store=True, readonly=False)
    move_ids = fields.One2many('stock.move', 'deliver_to_id', string='Reservation', readonly=True, ondelete='set null', copy=False)
    orderpoint_id = fields.Many2one('stock.warehouse.orderpoint', 'Orderpoint')

    purchase_req_line_id = fields.Many2one('purchase.req.line')
    purchase_req_rec_line_id = fields.Many2one('purchase.req.rec.line')
    work_order_id = fields.Char(string='Work Order')
    fleet_id_ref = fields.Reference(string='Fleet Ref',
     selection=[('fleet.vehicle','Vehicle'),('bsg_fleet_trailer_config','Trailer')])
    analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    branch_id = fields.Many2one("bsg_branches.bsg_branches",string="Branch")
    department_id = fields.Many2one('hr.department',string="Department")
    purchase_req_id = fields.Many2one('purchase.req',string="P.R")
    qty_invoiced = fields.Float(compute='_compute_qty_invoiced', string="Billed Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)
    qty_received = fields.Float(string="Received Qty", digits=dp.get_precision('Product Unit of Measure'), copy=False)

    @api.onchange('purchase_order_line')
    def _onchange_purchase_order_line(self):
        self.requsted_qty = self.purchase_order_line.product_qty - self.purchase_order_line.deliver_to_qty
        self.name = self.purchase_order_line.name
        self.purchase_req_id = self.purchase_order_line.purchase_req_line_id.preq.id
        self.purchase_req_line_id = self.purchase_order_line.purchase_req_line_id.id
        self.analytic_account_id = self.purchase_order_line.purchase_req_line_id.analytic_account_id.id
        self.work_order_id = self.purchase_order_line.work_order_id
        self.fleet_id_ref = self.purchase_order_line.fleet_id_ref
        self.department_id = self.purchase_order_line.purchase_req_line_id.preq.department_id.id
        self.branch_id =  self.purchase_order_line.purchase_req_line_id.preq.branches.id


    @api.depends('purchase_order_line.invoice_lines','purchase_order_line.invoice_lines.move_id.state', 'purchase_order_line.invoice_lines.quantity')
    def _compute_qty_invoiced(self):
        for line in self:
            qty = 0.0
            for inv_line in line.purchase_order_line.invoice_lines:
                if inv_line.invoice_id.state not in ['cancel']:
                    if inv_line.invoice_id.type == 'in_invoice':
                        qty += inv_line.uom_id._compute_quantity(inv_line.quantity, line.purchase_order_line.product_uom)
                    elif inv_line.invoice_id.type == 'in_refund':
                        qty -= inv_line.uom_id._compute_quantity(inv_line.quantity, line.purchase_order_line.product_uom)
            line.qty_invoiced = qty


    # @api.multi
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        fleet_ref = False
        if self.fleet_id_ref:
            if str(self.fleet_id_ref).__contains__('fleet_trailer'):
                fleet_ref = str("bsg_fleet_trailer_config")+","+str(self.fleet_id_ref.id)
            if str(self.fleet_id_ref).__contains__('fleet.vehicle'):
                fleet_ref = str("fleet.vehicle")+","+str(self.fleet_id_ref.id)    
        qty = 0.0
        price_unit = self.purchase_order_line._get_stock_move_price_unit()
        for move in self.move_ids.filtered(lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.purchase_order_line.product_uom, rounding_method='HALF-UP')
        template = {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'product_uom': self.purchase_order_line.product_uom.id,
            'date': self.order_id.date_order,
            'date_expected': self.purchase_order_line.date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.picking_type_id.default_location_dest_id.id,
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            #'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.purchase_order_line.id,
            'deliver_to_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'route_ids': self.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.picking_type_id.warehouse_id.id,
            'purchase_req_line_id': self.purchase_req_line_id.id,
            'purchase_req_rec_line_id' : self.purchase_order_line.purchase_req_rec_line_id.id,
            'analytic_account_id':self.analytic_account_id.id,
            'work_order_id': self.work_order_id,
            'fleet_id_ref' : fleet_ref,
            'department_id':self.department_id.id,
            'branch_id': self.branch_id.id,
            'purchase_req_id': self.purchase_req_id.id,
            'description' : self.name or '',
        }
        diff_quantity = self.requsted_qty - qty
        if float_compare(diff_quantity, 0.0,  precision_rounding=self.purchase_order_line.product_uom.rounding) > 0:
            quant_uom = self.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param
            # Always call '_compute_quantity' to round the diff_quantity. Indeed, the PO quantity
            # is not rounded automatically following the UoM.
            if get_param('stock.propagate_uom') != '1':
                product_qty = self.purchase_order_line.product_uom._compute_quantity(diff_quantity, quant_uom, rounding_method='HALF-UP')
                template['product_uom'] = quant_uom.id
                template['product_uom_qty'] = product_qty
            else:
                template['product_uom_qty'] = self.purchase_order_line.product_uom._compute_quantity(diff_quantity, self.purchase_order_line.product_uom, rounding_method='HALF-UP')
            res.append(template)
        return res

    # @api.multi
    def _create_stock_moves(self, picking):
        values = []
        for line in self:
            for val in line._prepare_stock_moves(picking):
                values.append(val)   
        return self.env['stock.move'].create(values)

    def _update_received_qty(self):
        for line in self:
            total = 0.0
            # In case of a BOM in kit, the products delivered do not correspond to the products in
            # the PO. Therefore, we can skip them since they will be handled later on.
            for move in line.move_ids.filtered(lambda m: m.product_id == line.product_id \
                and line.picking_type_id.default_location_dest_id in [m.location_dest_id,m.location_id]):
                if move.state == 'done':
                    if move.location_dest_id.usage == "supplier":
                        if move.to_refund:
                            total -= move.product_uom._compute_quantity(move.product_uom_qty, line.purchase_order_line.product_uom)
                    elif move.origin_returned_move_id._is_dropshipped() and not move._is_dropshipped_returned():
                        # Edge case: the dropship is returned to the stock, no to the supplier.
                        # In this case, the received quantity on the PO is set although we didn't
                        # receive the product physically in our stock. To avoid counting the
                        # quantity twice, we do nothing.
                        pass
                    else:
                        total += move.product_uom._compute_quantity(move.product_uom_qty, line.purchase_order_line.product_uom)
            line.qty_received = total

    def _merge_in_existing_line(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        """ This function purpose is to be override with the purpose to forbide _run_buy  method
        to merge a new po line in an existing one.
        """
        return True



    # @api.multi
    def _create_or_update_picking(self):
        for line in self:
            if line.product_id.type in ('product', 'consu'):
                # Prevent decreasing below received quantity
                if float_compare(line.requsted_qty, line.qty_received, line.purchase_order_line.product_uom.rounding) < 0:
                    raise UserError(_('You cannot decrease the ordered quantity below the received quantity.\n'
                                      'Create a return first.'))

                if float_compare(line.requsted_qty, line.qty_invoiced, line.purchase_order_line.product_uom.rounding) == -1:
                    # If the quantity is now below the invoiced quantity, create an activity on the vendor bill
                    # inviting the user to create a refund.
                    activity = self.env['mail.activity'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create({
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'note': _('The quantities on your purchase order indicate less than billed. You should ask for a refund. '),
                        'res_id': line.purchase_order_line.invoice_lines[0].invoice_id.id,
                        'res_model_id': self.env.ref('account.model_account_invoice').id,
                    })
                    activity._onchange_activity_type_id()

                # If the user increased quantity of existing line or created a new line
                pickings = line.order_id.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel') and line.picking_type_id.default_location_dest_id == x.location_dest_id and x.location_dest_id.usage in ('internal', 'transit'))
                picking = pickings and pickings[0] or False
                if not picking:
                    res = line.order_id._prepare_to_multi_picking(line.picking_type_id)
                    picking = self.env['stock.picking'].create(res)
                move_vals = line._prepare_stock_moves(picking)
                for move_val in move_vals:
                    self.env['stock.move']\
                        .create(move_val)\
                        ._action_confirm()\
                        ._action_assign()

    @api.model
    def create(self, values):
        line = super(DeliverToLine, self).create(values)
        if line.order_id.state == 'purchase':
            line._create_or_update_picking()
        return line

    # @api.multi
    def write(self, values):
        result = super(DeliverToLine, self).write(values)
        # Update expected date of corresponding moves
        if 'requsted_qty' in values:
            self.filtered(lambda l: l.order_id.state == 'purchase')._create_or_update_picking()
        return result       

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    deliver_line_ids = fields.One2many('deliver.to.line', 'purchase_order_line', string='Deliver To Line',copy=False)
    deliver_to_qty = fields.Float(compute="_compute_deliver_to_qty",store=True,copy=False)

    @api.depends('deliver_line_ids.requsted_qty')
    def _compute_deliver_to_qty(self):
        for rec in self:
            rec.deliver_to_qty = sum(rec.deliver_line_ids.mapped('requsted_qty'))

    @api.constrains('deliver_to_qty')
    def _constrains_deliver_to_qty(self):
        if not self._context.get('is_copy',False):
            for rec in self:
                if rec.deliver_to_qty > rec.product_qty:
                    raise UserError(_("Total Deliver To Qty Can't Be More Than Line Qty %s") % rec.name)

    @api.model
    def create(self, values):
        line = super(PurchaseOrderLine, self).create(values)
        if line.order_id.state == 'purchase':
            if not line.order_id.multi_deliver:
                line._create_or_update_picking()
        return line

    # @api.multi
    def write(self, values):
        result = super(PurchaseOrderLine, self).write(values)
        # Update expected date of corresponding moves
        if 'date_planned' in values:
            self.env['stock.move'].search([
                ('purchase_line_id', 'in', self.ids), ('state', '!=', 'done')
            ]).write({'date_expected': values['date_planned']})
        if 'product_qty' in values:
            if not self.order_id.multi_deliver:
                self.filtered(lambda l: l.order_id.state == 'purchase')._create_or_update_picking()
            #elif self.deliver_line_ids and self.product_qty !=  sum(self.deliver_line_ids.mapped('requsted_qty')):
            #    raise UserError(_("Line Qty Must Equal Deliver To Qty %s") % sum(self.deliver_line_ids.mapped('requsted_qty')))
        return result


    # @api.multi
    def _create_or_update_picking(self):
        for line in self:
            if not line.order_id.multi_deliver:
                if line.product_id.type in ('product', 'consu'):
                    # Prevent decreasing below received quantity
                    if float_compare(line.product_qty, line.qty_received, line.product_uom.rounding) < 0:
                        raise UserError(_('You cannot decrease the ordered quantity below the received quantity.\n'
                                        'Create a return first.'))

                    if float_compare(line.product_qty, line.qty_invoiced, line.product_uom.rounding) == -1:
                        # If the quantity is now below the invoiced quantity, create an activity on the vendor bill
                        # inviting the user to create a refund.
                        activity = self.env['mail.activity'].sudo().create({
                            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                            'note': _('The quantities on your purchase order indicate less than billed. You should ask for a refund. '),
                            'res_id': line.invoice_lines[0].invoice_id.id,
                            'res_model_id': self.env.ref('account.model_account_invoice').id,
                        })
                        activity._onchange_activity_type_id()

                    # If the user increased quantity of existing line or created a new line
                    pickings = line.order_id.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel') and x.location_dest_id.usage in ('internal', 'transit', 'customer'))
                    picking = pickings and pickings[0] or False
                    if not picking:
                        res = line.order_id._prepare_picking()
                        picking = self.env['stock.picking'].create(res)
                    move_vals = line._prepare_stock_moves(picking)
                    for move_val in move_vals:
                        self.env['stock.move']\
                            .create(move_val)\
                            ._action_confirm()\
                            ._action_assign()
                        

class StockMove(models.Model):
    _inherit = 'stock.move'

    deliver_to_id = fields.Many2one('deliver.to.line')


    def _action_done(self,cancel_backorder=False):
        res = super(StockMove, self)._action_done()
        self.mapped('deliver_to_id').sudo()._update_received_qty()
        return res

    def write(self, vals):
        res = super(StockMove, self).write(vals)
        if 'product_uom_qty' in vals:
            self.filtered(lambda m: m.state == 'done' and m.deliver_to_id).mapped(
                'deliver_to_id').sudo()._update_received_qty()
        return res

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_multi_deliver = fields.Boolean(string='Multi Deliver To',default=False,default_model='purchase.order')    
