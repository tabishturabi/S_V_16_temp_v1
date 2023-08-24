from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import datetime
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from pytz import timezone, UTC


class Department(models.Model):
    _inherit = 'hr.department'

    warehouse = fields.Many2one('stock.warehouse', string="Ware house")
    location_id = fields.Many2one('stock.location', string="Location", domain=[('usage', '=', 'internal')])


class PurchaseRequisition(models.Model):
    _name = 'purchase.transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Purchase Transfer"
    _order = 'date_pr desc'

    name = fields.Char(track_visibility='always')
    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.user.company_id.id)
    date_pr = fields.Datetime("Date", default=fields.Datetime.now, track_visibility='always')
    state = fields.Selection([
        ('tsub', 'To Submit'),
        ('approve', 'Approved'),
        ('rep', 'Reported'), ('open', 'Open'), ('close', 'Close'), ('cancel', 'Cancel'),
        ('done', 'Done'),

    ], string='States', default='approve', track_visibility='always')
    partner_id = fields.Many2one('res.partner', string='Requester Name', track_visibility='always')
    department_id = fields.Many2one('hr.department', string="Department", track_visibility='always')
    purchase_line = fields.One2many('purchase.transfer.line', 'preq', string="Purchase Request Line",
                                    track_visibility='always')
    branches = fields.Many2one("bsg_branches.bsg_branches", string="Branch", track_visibility='always')
    note = fields.Text('Terms and conditions', track_visibility='always')
    purchase_transfer = fields.Many2one('purchase.req', string="Purchase Request", track_visibility='always')
    is_has_line_for_purchase = fields.Boolean("Has Purchase Line", compute="_compute_line_status")
    is_has_line_for_stock = fields.Boolean("Has Stock Line", compute="_compute_line_status")
    request_type = fields.Selection([('stock', 'For Stock'), ('workshop', 'For Workshop'), ('branch', 'For Branch')],
                                    required=True, track_visibility='always')
    reciepts_ids = fields.Many2many('res.users', 'purchase_requset_transfer_users', 'transfer_id', 'user_id')

    internal_trans_count = fields.Integer(string='Internal Transfer Count', compute='_itcount')
    deliver_trans_count = fields.Integer(string='Internal Transfer Count', compute='_itcount')
    purchase_count = fields.Integer(string='Purchase Count', compute='_itcount')
    purchase_open_count = fields.Integer(string='Purchase Open Count', compute='_itcount')
    address_to = fields.Many2one('stock.location', 'Deliver Address')
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    purchase_picking_count = fields.Integer(compute='_compute_picking', string='Picking count')


    # @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('purchase_enhanced.action_attachment')
        return res

    def _compute_picking(self):
        for order in self:
            if order.state != 'cancel':
                order.purchase_picking_count = len(order.purchase_transfer.mapped('purchase_order_picking_ids'))

    # @api.multi
    def _compute_attachment_number(self):
        for rec in self:
            rec.attachment_number = self.env['ir.attachment'].search_count(
                [('res_model', '=', 'purchase.req'), ('purchase_req_id', '=', rec.purchase_transfer.id)])

    def _compute_line_status(self):
        for rec in self:
            rec.is_has_line_for_purchase = False
            rec.is_has_line_for_stock = False
            if rec.request_type == 'stock':
                rec.is_has_line_for_purchase = True
            elif rec.request_type in ['workshop','manufacture']:
                for line in rec.purchase_line:
                    if line.onhand <= 0 or line.ord_qty > line.onhand:
                        rec.is_has_line_for_purchase = True
                    if (line.onhand > 0 or line.qty_net_received > 0) and line.iss_qty != line.ord_qty:
                        rec.is_has_line_for_stock = True
            elif rec.request_type == 'branch':
                for line in rec.purchase_line:
                    if line.onhand <= 0 or line.ord_qty > line.onhand:
                        rec.is_has_line_for_purchase = True
                    if ((line.onhand > 0 or line.qty_net_received > 0) and line.iss_qty != line.ord_qty) or (
                            (line.onhand > 0 or line.qty_net_received > 0) and line.deliver_to and line.deliver_to.default_location_dest_id.id != self.address_to.id):
                        rec.is_has_line_for_stock = True

    def dones(self):
        pass

    def get_current_tz_time(self):
        tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        return UTC.localize(fields.Datetime.now()).astimezone(tz).replace(tzinfo=None)

    def set_to_close(self):
        for rec in self:
            rec.purchase_transfer.write({'state':'close'})
            rec.state = 'close'

    def set_to_open(self):
        for rec in self:
            rec.purchase_transfer.write({'state': 'open'})
            rec.purchase_transfer.mapped('preq_line').filtered(lambda line: line.state != 'done').write({'state': 'open'})
            rec.purchase_line.filtered(lambda line: line.state != 'done').write({'state': 'open'})
            rec.write({'state': 'open'})

    # @api.multi
    def unlink(self):
        if (self.state == 'done'):
            raise UserError(_("You cannot delete a purchase request that is already done."))
        return super(PurchaseRequisition, self).unlink()

    def get_move_picking(self, picking_type_id):
        list_2 = []
        if picking_type_id.code == 'internal':
            for s in self.purchase_line.filtered(
                    lambda s: s.searched_loc_id.id == picking_type_id.default_location_src_id.id):
                fleet_ref = False
                if s.fleet_id_ref:
                    if str(s.fleet_id_ref).__contains__('fleet_trailer'):
                        fleet_ref = str("bsg_fleet_trailer_config") + "," + str(s.fleet_id_ref.id)
                    if str(s.fleet_id_ref).__contains__('fleet.vehicle'):
                        fleet_ref = str("fleet.vehicle") + "," + str(s.fleet_id_ref.id)
                if s.onhand > 0:
                    if (s.given == 0.0):
                        raise UserError(_("Enter Total Given Quantity For Lines"))
                    if (s.given > s.onhand):
                        raise UserError(_("Total Given Quantity For Lines Must Be Less Than On Hand Qty"))
                    list_2.append({
                        'name': '/',
                        'product_id': s.product_id.id,
                        'product_uom': s.product_id.uom_id.id,
                        'product_uom_qty': s.given,
                        # 'quantity_done' : s.given,
                        # 'reserved_availablitiy' : s.given,
                        'purchase_req_line_id': s.purchase_req_line_id.id,
                        'work_order_id': s.work_order_id,
                        'fleet_id_ref': fleet_ref,
                        'department_id': self.department_id.id,
                        'branch_id': self.branches.id,
                        'analytic_account_id': s.analytic_account_id.id,
                        'purchase_req_id': self.purchase_transfer.id,
                        'description': s.name,
                        'date_expected': fields.Datetime.now(),
                        'state': 'draft',
                    })
        else:
            for s in self.purchase_line:
                fleet_ref = False
                if s.fleet_id_ref:
                    if str(s.fleet_id_ref).__contains__('fleet_trailer'):
                        fleet_ref = str("bsg_fleet_trailer_config") + "," + str(s.fleet_id_ref.id)
                    if str(s.fleet_id_ref).__contains__('fleet.vehicle'):
                        fleet_ref = str("fleet.vehicle") + "," + str(s.fleet_id_ref.id)
                if s.onhand > 0:
                    if (s.given == 0.0):
                        raise UserError(_("Enter Total Given Quantity For Lines"))
                    if (s.given > s.onhand):
                        raise UserError(_("Total Given Quantity For Lines Must Be Less Than On Hand Qty"))
                    list_2.append({
                        'name': '/',
                        'product_id': s.product_id.id,
                        'product_uom': s.product_id.uom_id.id,
                        'product_uom_qty': s.given,
                        # 'quantity_done' : s.given,
                        # 'reserved_availablitiy' : s.given,
                        'purchase_req_line_id': s.purchase_req_line_id.id,
                        'work_order_id': s.work_order_id,
                        'fleet_id_ref': fleet_ref,
                        'department_id': self.department_id.id,
                        'branch_id': self.branches.id,
                        'analytic_account_id': s.analytic_account_id.id,
                        'purchase_req_id': self.purchase_transfer.id,
                        'description': s.name,
                        'date_expected': fields.Datetime.now(),
                        'state': 'draft',
                    })
        return list_2

    def create_delivery_picking(self, picking_type_id):
        for s in self.purchase_line:
            if s.onhand > 0:
                if (s.given == 0.0):
                    raise UserError(_("Enter Total Given Quantity For Lines"))
                if (s.given > s.onhand):
                    raise UserError(_("Total Given Quantity For Lines Must Be Less Than On Hand Qty"))
        context = {
            'default_origin': self.name,
            'default_scheduled_date': fields.Datetime.now(),
            'default_pur_tran': self.id,
            'default_purchase_req_id': self.purchase_transfer.id,
            'default_request_type': self.request_type,
            'default_show_operations': True,
        }
        stock_action = self.env.ref('purchase_enhanced.action_picking_tree_delivery')
        action = stock_action.read()[0]
        action['context'] = context
        action['views'] = [(self.env.ref('purchase_enhanced.view_view_picking_form_delivery').id, 'form')]
        return action

    def create_internal_picking(self, picking_type_id):
        for s in self.purchase_line.filtered(
                lambda s: s.searched_loc_id.id == picking_type_id.default_location_src_id.id):
            if s.onhand:
                if (s.given == 0.0):
                    raise UserError(_("Enter Total Given Quantity For Lines"))
                if (s.given > s.onhand):
                    raise UserError(_("Total Given Quantity For Lines Must Be Less Than On Hand Qty"))
        context = {
            'default_picking_type_id': picking_type_id.id,
            'default_origin': self.name,
            'default_scheduled_date': fields.Datetime.now(),
            'default_pur_tran': self.id,
            'default_purchase_req_id': self.purchase_transfer.id,
            'default_request_type': self.request_type,
            'default_show_operations': True,
        }
        stock_action = self.env.ref('purchase_enhanced.action_picking_tree_internal')
        action = stock_action.read()[0]
        action['context'] = context
        action['views'] = [(self.env.ref('purchase_enhanced.view_view_picking_form_internal').id, 'form')]
        return action

    def create_purchase(self):
        if self.state == 'cancel':
            raise UserError(_("Sorry , This Request is already has been canceled"))
        purchase_ids = self.env['purchase.req.rec'].sudo().search([('purchase_stock_tran', '=', self.id),('state','!=','cancel')])
        if purchase_ids:
            raise UserError(_("Sorry , This Request is already has been sent to proceed")) 
        list_1 = []
        for s in self.purchase_line:
            fleet_ref = False
            if s.fleet_id_ref:
                if str(s.fleet_id_ref).__contains__('fleet_trailer'):
                    fleet_ref = str("bsg_fleet_trailer_config") + "," + str(s.fleet_id_ref.id)
                if str(s.fleet_id_ref).__contains__('fleet.vehicle'):
                    fleet_ref = str("fleet.vehicle") + "," + str(s.fleet_id_ref.id)
            if s.onhand or s.iss_qty:
                if s.ord_qty > s.iss_qty:
                    if not s.deliver_to and s.product_id.type not in ['service','consu']:
                        raise UserError(_("Please Specify Deliver To Picking For Line!!"))
                    qty_diff = s.ord_qty - s.iss_qty
                    list_1.append({
                        'product_id': s.product_id.id,
                        'qty': qty_diff,
                        'onhand': s.onhand,
                        'name': s.name,
                        'purchase_req_line_id': s.purchase_req_line_id.id,
                        'purchase_transfer_line': s.id,
                        'work_order_id': s.work_order_id,
                        'fleet_id_ref': fleet_ref,
                        'purchase_req_id': self.purchase_transfer.id,
                        'deliver_to': s.deliver_to.id,
                        'analytic_account_id': s.analytic_account_id.id,
                        'sequence' : s.sequence,
                        'company_id': self.company_id.id,
                    })

            else:
                if not s.deliver_to and s.product_id.type not in ['service','consu']:
                    raise UserError(_("Please Specify Deliver To Picking For Line!!"))
                list_1.append({
                    'product_id': s.product_id.id,
                    'qty': s.ord_qty,
                    'onhand': s.onhand,
                    'name': s.name,
                    'purchase_req_line_id': s.purchase_req_line_id.id,
                    'purchase_transfer_line': s.id,
                    'work_order_id': s.work_order_id,
                    'fleet_id_ref': fleet_ref,
                    'purchase_req_id': self.purchase_transfer.id,
                    'deliver_to': s.deliver_to.id,
                    'analytic_account_id': s.analytic_account_id.id,
                    'sequence' : s.sequence,
                    'company_id': self.company_id.id,
                })

        if (list_1):
            self.env['purchase.req.rec'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create({
                'name': self.name,
                'date_pr': self.date_pr,
                'request_type': self.request_type,
                'state': 'open',
                'partner_id': self.partner_id.id,
                'department_id': self.department_id.id,
                'branches': self.branches.id,
                'preq_rec_line': [(0, 0, s) for s in list_1],
                'purchase_transfer': self.purchase_transfer.id,
                'purchase_stock_tran': self.id,
                'address_to': self.address_to.id,
                'company_id': self.company_id.id,
            })
            self.write({'state': 'open'})
            self.purchase_transfer.write({'state': 'open'})

    ###########Guick Access####################
    # @api.multi
    def _itcount(self):
        itcount = self.env['stock.picking'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                company_id=self.env.user.company_id.id).search(
            [('pur_tran', '=', self.id)])
        purchase_count = self.env['purchase.req.rec'].search([('purchase_stock_tran', '=', self.id)])
        purchase_open_count = self.env['purchase.req.rec'].search([('purchase_stock_tran', '=', self.id),('state','!=','cancel')])
        self.update({
            'internal_trans_count': len(set(itcount.filtered(lambda s:s.picking_type_id.code == 'internal'))),
            'deliver_trans_count': len(set(itcount.filtered(lambda s:s.picking_type_id.code == 'outgoing'))),
            'purchase_count': len(set(purchase_count)),
            'purchase_open_count': len(set(purchase_open_count))
        })

    def action_open_transfer(self):
        action = self.env.ref('purchase_enhanced.open_stock_transfer_action').read()[0]
        action['context'] = {'default_rec_type': self._context.get('default_rec_type')}
        return action

    def action_view_internal_picking(self):
        it = self.env['stock.picking'].search([('pur_tran', '=', self.id),('picking_type_id.code','=','internal')])
        action = self.env.ref('purchase_enhanced.action_picking_tree_internal').read()[0]
        if len(it) > 1:
            action['domain'] = [('id', 'in', it.ids)]
        elif len(it) == 1:
            action['views'] = [(self.env.ref('purchase_enhanced.view_view_picking_form_internal').id, 'form')]
            action['res_id'] = it.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_deliver_picking(self):
        it = self.env['stock.picking'].search([('pur_tran', '=', self.id),('picking_type_id.code','=','outgoing')])
        action = self.env.ref('purchase_enhanced.action_picking_tree_delivery').read()[0]
        if len(it) > 1:
            action['domain'] = [('id', 'in', it.ids)]
        elif len(it) == 1:
            action['views'] = [(self.env.ref('purchase_enhanced.view_view_picking_form_delivery').id, 'form')]
            action['res_id'] = it.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_purchase(self):
        purchase_ids = self.env['purchase.req.rec'].search([('purchase_stock_tran', '=', self.id)])
        action = self.env.ref('purchase_enhanced.action_purchase_req_rec').read()[0]
        if len(purchase_ids) > 1:
            action['domain'] = [('id', 'in', purchase_ids.ids)]
        elif len(purchase_ids) == 1:
            action['views'] = [(self.env.ref('purchase_enhanced.view_purchase_req_rec_form').id, 'form')]
            action['res_id'] = purchase_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # @api.multi
    def action_view_purchase_picking(self):
        """ This function returns an action that display existing picking orders of given purchase order ids. When only one found, show the picking immediately.
        """
        if self.state != 'cancel':
            pick_ids = self.purchase_transfer.mapped('purchase_order_picking_ids')
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

class PurchaseRequisitionLine(models.Model):
    _name = 'purchase.transfer.line'
    _description = "Purchase Transfer Line"
    _order = 'date_pr desc'

    preq = fields.Many2one('purchase.transfer', string="Purchase Request")
    product_id = fields.Many2one('product.product', string='Requested Product')
    product_type = fields.Selection([('consu', 'Consumable'), ('service', 'Service'),
                                     ('product', 'Storeable')], string='Product Type', related='product_id.type',
                                    store=True)
    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.user.company_id.id)
    ord_qty = fields.Float('Requested Quantity')
    name = fields.Text(string='Description', required=True)
    cons_onhand = fields.Float("Consumable Onhand")
    onhand = fields.Float("Onhand", compute='_compute_qty_on_hands', store=True)
    given = fields.Float("Total Given")
    work_order_id = fields.Char(string='Work Order')
    fleet_id_ref = fields.Reference(string='Fleet Ref',
                                    selection=[('fleet.vehicle', 'Vehicle'), ('bsg_fleet_trailer_config', 'Trailer')])
    purchase_req_id = fields.Many2one('purchase.req', string="P.R")
    purchase_req_line_id = fields.Many2one('purchase.req.line')
    qty_po = fields.Float(related='purchase_req_line_id.qty_po', string="PO Qty", store=True)
    qty_rfq = fields.Float(related='purchase_req_line_id.qty_rfq', string="Rfq Qty", store=True)
    qty_received = fields.Float(related='purchase_req_line_id.qty_received', string="Received Qty", store=True)
    qty_returned = fields.Float(related='purchase_req_line_id.qty_returned', string="Returned Qty", store=True)
    qty_net_received = fields.Float(related='purchase_req_line_id.qty_net_received', string="Net Received Qty",
                                    store=True)
    iss_qty = fields.Float(string="ISS Qty", related='purchase_req_line_id.iss_qty',store=True)
    deliver_to = fields.Many2one('stock.picking.type')
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Acount")

    partner_id = fields.Many2one('res.partner', related='preq.partner_id', store=True, string='Requester Name',
                                 track_visibility='always')
    requester_id = fields.Many2one('res.users', 'Current User', related='purchase_req_line_id.requester_id', store=True,
                                   track_visibility='always')
    department_id = fields.Many2one('hr.department', string="Department", related='preq.department_id', store=True,
                                    track_visibility='always')
    branches = fields.Many2one("bsg_branches.bsg_branches", string="Branch", related='preq.branches', store=True,
                               track_visibility='always')
    date_pr = fields.Datetime("Date", related='preq.date_pr', store=True, track_visibility='always')
    state = fields.Selection([
        ('tsub', 'To Submit'),
        ('tapprove', 'To Approve'),
        ('approve', 'Approved'),
        ('open', 'Open'), ('close', 'Close'),('cancel', 'Cancel'),
        ('reject', 'Reject'),
        ('done', 'Done')], string='States', default='open', track_visibility='always')
    request_type = fields.Selection([('stock', 'For Stock'), ('workshop', 'For Workshop'), ('branch', 'For Branch')],
                                    related='preq.request_type', store=True, track_visibility='always')
    reciepts_ids = fields.Many2many('res.users', 'purchase_requset_transfer_line_users', 'transfer_id', 'user_id',
                                    related='preq.reciepts_ids', store=True)
    fleet_num = fields.Char(string="Fleet", compute='_compute_fleet_ref_tag', store=True, track_visibility=True)
    searched_loc_id = fields.Many2one('stock.location', 'Searched Location')
    sequence = fields.Integer('No#')

    # @api.multi
    @api.depends('cons_onhand', 'product_id.qty_available')
    def _compute_qty_on_hands(self):
        for rec in self.sudo():
            if rec.product_id:
                if rec.product_type == 'consu' and rec.request_type == 'branch':
                    rec.onhand = rec.cons_onhand
                else:
                    rec.onhand = rec.product_id.qty_available
                rec.preq._compute_line_status()

    # @api.multi
    def _compute_iss_qty(self):
        for line in self:
            reciev_total = 0.0
            return_total = 0.0
            stock_picking = self.env['stock.picking'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                [('pur_tran', '=', line.preq.id), ('state', '!=', 'cancel')])
            if stock_picking:
                for pick in stock_picking:
                    reciev_total += sum(pick.move_ids_without_package.filtered(lambda m: m.product_id == line.product_id and m.state == 'done' and not m.is_return).mapped('quantity_done'))
                    return_total += sum(pick.move_ids_without_package.filtered(lambda m: m.product_id == line.product_id and m.state == 'done' and m.is_return).mapped('quantity_done'))
            line.iss_qty = reciev_total - return_total

    @api.depends('fleet_id_ref')
    def _compute_fleet_ref_tag(self):
        for rec in self:
            if rec.fleet_id_ref:
                if str(rec.fleet_id_ref).__contains__('fleet_trailer'):
                    rec.fleet_num = rec.fleet_id_ref.trailer_taq_no
                if str(rec.fleet_id_ref).__contains__('fleet.vehicle'):
                    rec.fleet_num = rec.fleet_id_ref.taq_number

    @api.onchange('given')
    def check_qty(self):
        if (self.given < 0):
            raise UserError(_("The given quantity should be greater than 0)"))
        if (self.given  > self.onhand and self.product_id.type == 'product') or (self.given  > self.qty_net_received and self.product_id.type != 'product'):
            raise UserError(_("The given quantity should be less than available quantity"))
        if ((self.given+ self.iss_qty) > self.ord_qty):
            raise UserError(_("Total Given Quantity Must Be Less Than Requested Qty"))


    #@api.constrains('given')
    #def constrains_request_given(self):
    #    for rec in self:
    #        if (rec.given  > rec.onhand and rec.product_id.type == 'product') or (rec.given  > rec.qty_net_received and rec.product_id.type != 'product'):
    #            raise UserError(_("The given quantity should be less than available quantity"))
    #        if ((rec.given + rec.iss_qty) > rec.ord_qty):
    #            raise UserError(_("Total Given Quantity Must Be Less Than Requested Qty"))
    
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_change_location(self):
        if self.env.user.has_group('purchase_enhanced.custom_group_stock_change_location'):
            return True
        else:
            return False

    pur_tran = fields.Many2one('purchase.transfer', string="Purchase Transfer Request")
    request_type = fields.Selection([('stock', 'For Stock'), ('workshop', 'For Workshop'), ('branch', 'For Branch'),('manufacture','For Manufacture')])
    purchase_req_id = fields.Many2one('purchase.req', string="P.R")
    change_location = fields.Boolean(default=_get_change_location)
    location_id = fields.Many2one('stock.location', "Source Location",
                                  default=lambda self: self.env['stock.picking.type'].browse(
                                      self._context.get('default_picking_type_id')).default_location_src_id,
                                  required=True)
    location_dest_id = fields.Many2one('stock.location', "Destination Location",
                                       default=lambda self: self.env['stock.picking.type'].browse(
                                           self._context.get('default_picking_type_id')).default_location_dest_id,
                                       required=True)
    accounting_date = fields.Date()

    @api.constrains('picking_type_id')
    def validateReceiptPicking(self):
        if self.company_id.po_required_in_receipt and self.picking_type_code in ['incoming'] and not self.purchase_id:
            raise ValidationError("You can't receipt picking without purchase order.")
    
                                

    @api.onchange('pur_tran')
    def _onchange_pur_tran(self):
        if self.pur_tran:
            #line_dict = self.pur_tran.get_move_picking(self.picking_type_id)
            #self.move_ids_without_package = line_dict
            if self.pur_tran.request_type == 'branch':
                self.location_dest_id = self.pur_tran.address_to.id

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if res.pur_tran:
            res.pur_tran.write({'state': 'open'})
        if res.purchase_req_id:
            res.purchase_req_id.write({'state': 'open'})
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_branch(self):
        branch_id = self.env['hr.employee'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                company_id=self.env.user.company_id.id).search(
            [('user_id', '=', self.env.user.id)], limit=1).branch_id.id
        return branch_id

    def _get_analytic(self):
        analytic_id = self.env['hr.employee'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                  company_id=self.env.user.company_id.id).search(
            [('user_id', '=', self.env.user.id)], limit=1).branch_id.account_analytic_id.id
        return analytic_id

    purchase_req_id = fields.Many2one('purchase.req', string="P.R")
    purchase_req_line_id = fields.Many2one('purchase.req.line')
    purchase_req_rec_line_id = fields.Many2one('purchase.req.rec.line')
    purchase_transfer_line_id = fields.Many2one('purchase.transfer.line')
    work_order_id = fields.Char(string='Work Order')
    fleet_id_ref = fields.Reference(string='Fleet Ref',
                                    selection=[('fleet.vehicle', 'Vehicle'), ('bsg_fleet_trailer_config', 'Trailer')])
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", default=_get_analytic)
    branch_id = fields.Many2one("bsg_branches.bsg_branches", string="Branch", default=_get_branch)
    department_id = fields.Many2one('hr.department', string="Department",
                                    default=lambda self: self.env['hr.employee'].search(
                                        [('user_id', '=', self.env.user.id)], limit=1).department_id)
    description = fields.Char()
    fleet_num = fields.Char(string="Fleet", compute='_compute_fleet_ref_tag', store=True, track_visibility=True)
    pur_tran = fields.Many2one('purchase.transfer', string="Purchase Transfer Request", related='picking_id.pur_tran',
                               store=True)
    request_type = fields.Selection([('stock', 'For Stock'), ('workshop', 'For Workshop'), ('branch', 'For Branch'),('manufacture','For Manufacture')],
                                    related='picking_id.request_type', store=True)
    sequence2 = fields.Integer('No#',compute='_compute_line_sequence',
                                       store=True)
    is_return = fields.Boolean()


    # Migration Note
    # @api.multi
    @api.depends('picking_id.move_ids')
    def _compute_line_sequence(self):
        for rec in self:
            rec.sequence2 = (
                max(rec.picking_id.mapped('move_ids.sequence2') or [0]) + 1)

    @api.depends('fleet_id_ref')
    def _compute_fleet_ref_tag(self):
        for rec in self:
            if rec.fleet_id_ref:
                if str(rec.fleet_id_ref).__contains__('fleet_trailer'):
                    rec.fleet_num = rec.fleet_id_ref.trailer_taq_no
                if str(rec.fleet_id_ref).__contains__('fleet.vehicle'):
                    rec.fleet_num = rec.fleet_id_ref.taq_number

    def _account_entry_move(self):
        """ Accounting Valuation Entries """
        self.ensure_one()
        if self.inventory_id.without_account_move:
            # no moves
            return False
        else:
            return super(StockMove, self)._account_entry_move()

    def _action_done(self,cancel_backorder=False):
        res = super(StockMove, self)._action_done()
        if not self.env.context.get('without_set_pr_to_done',False):
            for r in res:
                r.purchase_req_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).set_to_done()
        return res

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
        self.ensure_one()
        AccountMove = self.env['account.move']
        quantity = self.env.context.get('forced_quantity', self.product_qty)
        quantity = quantity if self._is_in() else -1 * quantity

        # Make an informative `ref` on the created account move to differentiate between classic
        # movements, vacuum and edition of past moves.
        ref = self.picking_id.name
        if self.env.context.get('force_valuation_amount'):
            if self.env.context.get('forced_quantity') == 0:
                ref = 'Revaluation of %s (negative inventory)' % ref
            elif self.env.context.get('forced_quantity') is not None:
                ref = 'Correction of %s (modification of past move)' % ref

        move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(quantity, abs(self.value),
                                                                                  credit_account_id, debit_account_id)
        if move_lines:
            if self._context.get('force_period_date'):
                date = self._context.get('force_period_date')
            elif self.picking_id.accounting_date:
                date = self.picking_id.accounting_date
            else:
                date = fields.Date.context_today(self)
            new_account_move = AccountMove.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': ref,
                'stock_move_id': self.id,
            })
            new_account_move.post()

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id,
                                       credit_account_id):
        # This method returns a dictonary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        rslt = super(StockMove, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value,
                                                                     debit_account_id, credit_account_id)
        location_from = self.location_id
        location_to = self.location_dest_id
        if (self._is_out() and (location_to and location_to.usage == 'customer')) or (
                self._is_in() and (location_from and location_from.usage == 'customer')):
            expence_type_id = self.env.ref('account.data_account_type_expenses').id
            cost_type_id = self.env.ref('account.data_account_type_direct_costs').id
            account_obj = self.env['account.account']
            debit_acc_id = account_obj.browse(debit_account_id)
            credit_acc_id = account_obj.browse(credit_account_id)
            if debit_acc_id.user_type_id.id in [expence_type_id, cost_type_id]:
                if self.fleet_id_ref:
                    if str(self.fleet_id_ref).__contains__('fleet_trailer'):
                        rslt['debit_line_vals']['trailer_id'] = self.fleet_id_ref.id
                    if str(self.fleet_id_ref).__contains__('fleet.vehicle'):
                        rslt['debit_line_vals']['fleet_vehicle_id'] = self.fleet_id_ref.id
                rslt['debit_line_vals']['bsg_branches_id'] = self.branch_id.id
                rslt['debit_line_vals']['department_id'] = self.department_id.id
                # rslt['debit_line_vals']['fleet_vehicle_id'] = self.fleet.id
                rslt['debit_line_vals']['analytic_account_id'] = self.analytic_account_id.id
            if credit_acc_id.user_type_id.id in [expence_type_id, cost_type_id]:
                if self.fleet_id_ref:
                    if str(self.fleet_id_ref).__contains__('fleet_trailer'):
                        rslt['credit_line_vals']['trailer_id'] = self.fleet_id_ref.id
                    if str(self.fleet_id_ref).__contains__('fleet.vehicle'):
                        rslt['credit_line_vals']['fleet_vehicle_id'] = self.fleet_id_ref.id
                rslt['credit_line_vals']['bsg_branches_id'] = self.branch_id.id
                rslt['credit_line_vals']['department_id'] = self.department_id.id
                # rslt['credit_line_vals']['fleet_vehicle_id'] = self.fleet.id
                rslt['credit_line_vals']['analytic_account_id'] = self.analytic_account_id.id
        rslt['debit_line_vals']['name'] = self.picking_id.origin
        rslt['credit_line_vals']['name'] = self.picking_id.origin
        return rslt

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        self.ensure_one()
        res = super(StockMove, self)._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
        # Add New Fields
        fleet_ref = False
        if self.fleet_id_ref:
            if str(self.fleet_id_ref).__contains__('fleet_trailer'):
                fleet_ref = str("bsg_fleet_trailer_config") + "," + str(self.fleet_id_ref.id)
            if str(self.fleet_id_ref).__contains__('fleet.vehicle'):
                fleet_ref = str("fleet.vehicle") + "," + str(self.fleet_id_ref.id)
        res['purchase_req_id'] = self.purchase_req_id and self.purchase_req_id.id or False
        res['purchase_req_line_id'] = self.purchase_req_line_id and self.purchase_req_line_id.id or False
        res['purchase_req_rec_line_id'] = self.purchase_req_rec_line_id and self.purchase_req_rec_line_id.id or False
        res['work_order_id'] = self.work_order_id
        res['fleet_id_ref'] = fleet_ref
        res['analytic_account_id'] = self.analytic_account_id and self.analytic_account_id.id or False
        res['branch_id'] = self.branch_id and self.branch_id.id or False
        res['department_id'] = self.department_id and self.department_id.id or False
        res['description'] = self.description
        res['fleet_num'] = self.fleet_num
        res['pur_tran'] = self.pur_tran and self.pur_tran.id or False
        res['request_type'] = self.request_type
        return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    purchase_req_id = fields.Many2one('purchase.req', string="P.R")
    purchase_req_line_id = fields.Many2one('purchase.req.line')
    purchase_req_rec_line_id = fields.Many2one('purchase.req.rec.line')
    work_order_id = fields.Char(string='Work Order')
    fleet_id_ref = fields.Reference(string='Fleet Ref',
                                    selection=[('fleet.vehicle', 'Vehicle'), ('bsg_fleet_trailer_config', 'Trailer')])
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    branch_id = fields.Many2one("bsg_branches.bsg_branches", string="Branch")
    department_id = fields.Many2one('hr.department', string="Department")
    description = fields.Char()
    fleet_num = fields.Char(string="Fleet", track_visibility=True)
    pur_tran = fields.Many2one('purchase.transfer', string="Purchase Transfer Request")
    request_type = fields.Selection([('stock', 'For Stock'), ('workshop', 'For Workshop'), ('branch', 'For Branch'),('manufacture','For Manufacture')])

# MIgration Note
# class Inventory(models.Model):
class StockQuant(models.Model):
    # _inherit = "stock.inventory"
    _inherit = "stock.quant"

    without_account_move = fields.Boolean()
