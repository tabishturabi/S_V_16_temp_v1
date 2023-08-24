# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, ValidationError


class BsgMrpProduction(models.Model):
    """ Manufacturing Orders """
    _name = 'bsg.mrp.production'
    _description = 'BSG Production Order'
    _date_name = 'date_planned_start'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_planned_start asc,id'

    @api.model
    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            (
                'warehouse_id.company_id', 'in',
                [self.env.context.get('company_id', self.env.user.company_id.id), False])],
            limit=1).id

    @api.model
    def _get_default_location_src_id(self):
        location = False
        if self._context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(
                self.env.context['default_picking_type_id']).default_location_src_id
        if not location:
            location = self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            (
                'warehouse_id.company_id', 'in',
                [self.env.context.get('company_id', self.env.user.company_id.id), False])],
            limit=1).default_location_src_id.id
            
        return location and location.id or False

    @api.model
    def _get_default_location_dest_id(self):
        location = False
        if self._context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(
                self.env.context['default_picking_type_id']).default_location_dest_id
        if not location:
            location = self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            (
                'warehouse_id.company_id', 'in',
                [self.env.context.get('company_id', self.env.user.company_id.id), False])],
            limit=1).default_location_dest_id
        return location and location.id or False

    name = fields.Char(
        'Reference', copy=False, readonly=True, default=lambda x: _('New'))
    origin = fields.Char(
        'Source', copy=False,
        help="Reference of the document that generated this production order request.")

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('type', 'in', ['product', 'consu'])])
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id',
                                      readonly=True)
    product_qty = fields.Float(
        'Quantity To Produce',
        default=1.0, digits=dp.get_precision('Product Unit of Measure'),
        readonly=True, track_visibility='onchange',
        states={'confirmed': [('readonly', False)]})
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure', readonly=True, related='product_id.uom_id')
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        default=_get_default_picking_type)
    location_src_id = fields.Many2one(
        'stock.location', 'Raw Materials Location',
        default=_get_default_location_src_id,
        readonly=True, help="Location where the system will look for components.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Finished Products Location',
        default=_get_default_location_dest_id,
        readonly=True,
        help="Location where the system will stock the finished products.")
    date_planned_start = fields.Datetime(
        'Deadline Start', copy=False, default=fields.Datetime.now,
        index=True, required=True)
    date_planned_finished = fields.Datetime(
        'Deadline End', copy=False, default=fields.Datetime.now,
        index=True)

    state = fields.Selection([
        ('1', 'Draft'),
        ('2', 'Preparation Cutting/ Drilling'),
        ('3', 'Assembly & Tack Welding'),
        ('4', 'Finishing / Grinding'),
        ('5', 'Welding Inspection (Visual/MPI/UT)'),
        ('6', 'Blasting/Painting'),
        ('7', 'Done')], string='State',
        copy=False, default='1', track_visibility='onchange')

    routing_id = fields.Many2one(
        'mrp.routing', 'Routing', store=True,
        help="The list of operations (list of work centers) to produce the finished product. The routing "
             "is mainly used to compute work center costs during operations and to plan future loads on "
             "work centers based on production planning.")
    project_id = fields.Many2one('bsg.mrp.project', 'Project')
    quality_control_id = fields.Many2one('bsg.quality.check', 'Quality Control')
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account",
                                          related='project_id.analytic_account_id', readonly=True)
    project_type = fields.Many2one('bsg.mrp.project.type', 'Project Type Name', related='project_id.project_type',
                                   readonly=True)
    production_line_ids = fields.One2many(
        'bsg.mrp.production.line', 'bsg_production_id', 'Raw Materials', copy=False)
    technician_line_ids = fields.One2many(
        'bsg.mrp.technician.line', 'bsg_production_id', 'Technician Lines', copy=False)
    is_send_to_qc = fields.Boolean('Is Send To QC')
    is_check_create_pr = fields.Boolean('Is ALL PR Created', compute="_compute_is_check_create_pr",
                                        search='_search_status')
    pr_count = fields.Integer('PR', compute='_compute_pr_number')
    qc_count = fields.Integer('PR', compute='_compute_qc_number')
    manager_ids = fields.Many2many('res.users', index=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    final_picking = fields.Many2one('stock.picking')
   
    # @api.multi
    def _compute_pr_number(self):
        for rec in self:
            rec.pr_count = self.env['purchase.req'].search_count([('manufacturing_order_id', '=', rec.id)])

    # @api.multi
    def _compute_qc_number(self):
        for rec in self:
            rec.qc_count = self.env['bsg.quality.check'].search_count([('manufacturing_order_id', '=', rec.id)])

    # @api.multi
    def action_get_pr_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('purchase_enhanced.action_purchase_req')
        res['domain'] = [('manufacturing_order_id', 'in', self.ids)]
        return res

    # @api.multi
    def action_get_qc_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('manufacturing_enhance.quality_check_manufacture_order')
        res['domain'] = [('manufacturing_order_id', 'in', self.ids)]
        return res

    # @api.multi
    def _search_status(self, operator, value):
        res = []
        recs = self.search([]).filtered(lambda x: x.is_check_create_pr)
        if recs:
            return [('id', 'in', [x.id for x in recs])]
        return res

    # @api.multi
    def _compute_is_check_create_pr(self):
        for rec in self:
            if len(rec.production_line_ids.filtered(
                    lambda s: not s.is_pr_create and s.requested_from == 'pr' and s.product_id)) > 0:
                rec.is_check_create_pr = True
            else:
                rec.is_check_create_pr = False

    # @api.multi
    def btn_confirm(self):
        if self.state == '1' and self.name == "New":
            self.write({'state': '2', 'name': self.env['ir.sequence'].next_by_code('bsg.mrp.production.seq')})
        else:
            if not self.is_send_to_qc:
                raise ValidationError(_("You can not move to next state if you do not pass the QC"))
            if self.quality_control_id and self.quality_control_id.production_state == self.state:
                if self.is_send_to_qc and self.quality_control_id.quality_state != 'pass':
                    raise ValidationError(_("You can not move to next state if you do not pass the QC"))
            state_seq = int(self.state)
            state_seq += 1
            self.write({'state': str(state_seq), 'is_send_to_qc': False})
            if self.state == '7':
                self.final_picking = self.create_final_picking()

    # @api.multi
    def create_final_picking(self):
        for rec in self:        
            if not rec.picking_type_id:  
                raise UserError(_("Please Choose Picking Operation"))   
            picking_lines = self.get_move_picking(rec.picking_type_id)          
            order_dict = {
                'picking_type_id' :rec.picking_type_id.id,
                'origin':self.name,
                'scheduled_date':fields.Datetime.now(),
                #'partner_id': self.partner_id.id,
                #'pur_tran':self.id,
                #'purchase_req_id':self.purchase_transfer.id,
                #'request_type':self.request_type,
                'show_operations': True,
                'move_ids_without_package':picking_lines,
                'location_id':rec.picking_type_id.default_location_src_id.id,
                'location_dest_id':rec.picking_type_id.default_location_dest_id.id
                }
            picking_id  = self.env['stock.picking'].create(order_dict)
            picking_id.onchange_picking_type()
            picking_id.action_confirm()
            picking_id.action_assign()
            for move in picking_id.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                    for move_line in move.move_line_ids:
                        move_line.qty_done = move_line.product_uom_qty
            picking_id.with_context(without_set_pr_to_done=True).button_validate()
            return picking_id

    def get_move_picking(self,picking_type_id):
        purchase_transfer_ids = self.env['purchase.req'].search([('manufacturing_order_id', '=', self.id)]).mapped('purchase_transfer_ids')
        if not purchase_transfer_ids:
            raise UserError(_("No P.R"))  
        picking_ids = self.env['stock.picking'].search([('pur_tran', 'in', purchase_transfer_ids.ids),('picking_type_id.code','=','outgoing')])
        if not picking_ids:
            raise UserError(_("No Picking In Purchase Request")) 
        if not picking_ids.mapped('move_ids_without_package.account_move_ids'):
            raise UserError(_("No Accounting Move For Picking In Purchase Request"))     
        final_total_price = sum(picking_ids.mapped('move_ids_without_package.account_move_ids.line_ids.debit'))
        price_unit = final_total_price / self.product_qty
        move_list = [([0,0,{
                        'name':'/',
                        'product_id':self.product_id.id,
                        'product_uom':self.product_id.uom_id.id,
                        'product_uom_qty':self.product_qty,
                        #'purchase_req_line_id' : s.purchase_req_line_id.id,
                        #'purchase_transfer_line_id' : s.id,
                        #'work_order_id' : s.work_order_id,
                        #'fleet_id_ref' : fleet_ref,
                        #'department_id':self.department_id.id,
                        #'branch_id' : self.branches.id,
                        'analytic_account_id' : self.analytic_account_id.id ,
                        #'purchase_req_id' : self.purchase_transfer.id,
                        'description' : self.name,
                        'date_expected':fields.Datetime.now(),
                        'state':'draft',
                        'warehouse_id': self.picking_type_id.warehouse_id.id,
                        'company_id': self.company_id.id,
                        'price_unit': price_unit,
                    }])]
        return  move_list  


        
    # @api.multi
    def btn_reject(self):
        if self.state == '2':
            state_seq = int(self.state)
            state_seq -= 1
            self.write({'state': str(state_seq), 'is_send_to_qc': True})
        else:
            state_seq = int(self.state)
            state_seq -= 1
            self.write({'state': str(state_seq)})

    # @api.multi
    def btn_send_to_qc(self):
        self.env['bsg.quality.check'].create(
            {'title': self._fields['state'].selection[int(self.state) - 1][1],
             'project_id': self.project_id.id,
             'manufacturing_order_id': self.id, 'production_state': self.state})

    # @api.multi
    def btn_material_takeoff(self):
        production_lines = []
        if not self.manager_ids:
            raise ValidationError(_("Please Add Manager First"))
        if self.production_line_ids:
            for rec in self.production_line_ids:
                if not rec.is_pr_create and rec.requested_from == 'pr':
                    production_lines.append(
                        {'product_id': rec.product_id.id, 'product_categ': rec.product_id.categ_id.id,
                         'qty': int(rec.qty_to_consume), 'name': rec.note,
                         'manufacturing_order_id': self.id,
                         'analytic_account_id': self.project_id.analytic_account_id.id})

        if production_lines:
            pr_id = self.env['purchase.req'].create(
                {'manager_ids': [(6, 0, self.manager_ids.ids)], 'manufacturing_order_id': self.id,
                 'entry_date': fields.Date.today(),
                 'request_type': 'manufacture',
                 'preq_line': [(0, 0, x) for x in production_lines]})
            for pr_line in pr_id.preq_line:
                pr_line._onchange_fleet_id()
            for line in self.production_line_ids:
                if not line.is_pr_create and line.product_id and line.requested_from == 'pr':
                    line.update({'is_pr_create': True})
            pr_id.sudo().submission_manufacturing()
            #if pr_id.state != 'approve':
            #    pr_id.sudo().approved()
        else:
            raise ValidationError(_("You can not create PR"))


class BsgMrpProductionLine(models.Model):
    _name = 'bsg.mrp.production.line'
    _description = 'BSG Production Order Line'

    qty_reserved = fields.Float('Reserved', digits=dp.get_precision('Product Unit of Measure'))
    qty_done = fields.Float('Consumed', digits=dp.get_precision('Product Unit of Measure'))
    qty_to_consume = fields.Float('To Consume', digits=dp.get_precision('Product Unit of Measure'))
    product_id = fields.Many2one('product.product', 'Product')
    bsg_production_id = fields.Many2one('bsg.mrp.production', 'Production Order')
    note = fields.Char(string="Note", track_visibility=True)
    requested_from = fields.Selection(string="Requested From", selection=[('scrap', 'Scrap'), ('pr', 'PR')],
                                      track_visibility=True)
    is_pr_create = fields.Boolean(string="Is PR Created", readonly=True)
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure')
    state = fields.Selection([
        ('1', 'Draft'),
        ('2', 'Preparation Cutting/ Drilling'),
        ('3', 'Assembly & Tack Welding'),
        ('4', 'Finishing / Grinding'),
        ('5', 'Welding Inspection (Visual/MPI/UT)'),
        ('6', 'Blasting/Painting'),
        ('7', 'Done')], string='State',
        copy=False, track_visibility='onchange',related='bsg_production_id.state')

    # @api.multi
    @api.onchange('product_id')
    def get_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id


class TechnicianLine(models.Model):
    _name = 'bsg.mrp.technician.line'
    _description = 'BSG Production Technician Line'

    bsg_production_id = fields.Many2one('bsg.mrp.production', 'Production Order')
    employee_id = fields.Many2one('hr.employee', string='Technician Name', track_visibility=True)
    driver_code = fields.Char(related='employee_id.driver_code', string='Technician Code', track_visibility=True,readonly=True)
    state = fields.Selection([
        ('1', 'Draft'),
        ('2', 'Preparation Cutting/ Drilling'),
        ('3', 'Assembly & Tack Welding'),
        ('4', 'Finishing / Grinding'),
        ('5', 'Welding Inspection (Visual/MPI/UT)'),
        ('6', 'Blasting/Painting'),
        ('7', 'Done')], string='State',
        copy=False, track_visibility='onchange',related='bsg_production_id.state')