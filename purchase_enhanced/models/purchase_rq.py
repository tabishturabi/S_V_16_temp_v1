# -*- coding: utf-8 -*-
from odoo import api, fields, models, _,tools
from datetime import datetime
from pytz import timezone, UTC
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProductCategory(models.Model):
    _inherit = "product.category"

    assgined_user_ids = fields.Many2many('res.users',index=True)

class PurchaseRequisition(models.Model):
    _inherit = 'stock.location'

    def _get_branch(self):
        return self.env.user.user_branch_id

    branche_id = fields.Many2one("bsg_branches.bsg_branches", string="Branch", default=_get_branch,
                                 track_visibility='always')
    is_default_for_branch = fields.Boolean(track_visibility='always')

    #@api.constrains('is_default_for_branch')
    #@api.one
    #def check_default_for_branch(self):
    #    branch_default = self.sudo().search([('branche_id','=',self.branche_id.id),('is_default_for_branch','=',True),('id','!=',self.id)])
    #    if branch_default:
    #        raise UserError(_("You Can't Assign Multi Location As Default For this branch !"))
    
                                 


class resuser(models.Model):
    _inherit = 'res.users'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', '|', '|', ('name', operator, name), ('login', operator, name),
                      ('email', operator, name),
                      ('partner_id.email', operator, name), ('partner_id.ref', operator, name)]
        user = self.search(domain + args, limit=limit)
        return user.name_get()

    # @api.multi
    @api.depends('name')
    def name_get(self):
        res = []
        for bsg in self:
            current = bsg
            if (current.id):
                name = '%s' % (current.partner_id.name)

                res.append((bsg.id, name))
        return res


class PurchaseRequisition(models.Model):
    _name = 'purchase.req'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Purchase Req"
    _order = 'date_pr desc'

    @api.model
    def default_get(self, fields):
        result = super(PurchaseRequisition, self).default_get(fields)
        if self.env.user.has_group('purchase_enhanced.pr_for_stock'):
            result['request_type'] = 'stock'
        if self.env.user.has_group('purchase_enhanced.pr_for_workshop'):
            result['request_type'] = 'workshop'
        if self.env.user.has_group('purchase_enhanced.pr_for_branch'):
            result['request_type'] = 'branch'
        return result

    def _get_request_oprions(self):
        options = []
        if self.env.user.has_group('purchase_enhanced.pr_for_stock'):
            options +=[('stock', _('For Stock'))]
        if self.env.user.has_group('purchase_enhanced.pr_for_workshop'):
            options +=[('workshop', _('For Workshop'))]
        if self.env.user.has_group('purchase_enhanced.pr_for_branch'):
            options +=[('branch', _('For Branch'))]
        return  options

    def _get_brwise(self):
        branch_id = self.env['hr.employee'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                company_id=self.env.user.company_id.id).search(
            [('user_id', '=', self.env.user.id)], limit=1).branch_id.id
        if branch_id:    
            return branch_id
        else:
            return self.env.user.user_branch_id.id    

    def _get_brwise_no(self):
        branch_id = self.env['hr.employee'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                company_id=self.env.user.company_id.id).search(
            [('user_id', '=', self.env.user.id)], limit=1).branch_id
        if branch_id:    
            return branch_id.branch_no
        else:
            return self.env.user.user_branch_id.branch_no

    def _getpartner(self):
        partner_id = self.env.user.partner_id
        return partner_id

    def _get_user_analytic(self):
        analytic_id = self.env['hr.contract'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                  company_id=self.env.user.company_id.id).search(
            [('employee_id.user_id', '=', self.env.user.id)], limit=1).analytic_account_id
        return analytic_id

    def _get_default_manager(self):
        manager_id = self.env['hr.employee'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                           company_id=self.env.user.company_id.id).search(
            [('user_id', '=', self.env.user.id)], limit=1).parent_id
        return [manager_id.user_id] + manager_id.alternative_employee_id.user_id   

    def _get_reciepts_domain(self):
        partner_ids = self.env.ref('purchase_enhanced.recieve_inventory_purchase_request').users.ids
        return [('id', 'in', partner_ids)]

    def _get_manager_domain(self):
        partner_ids = self.env.ref('purchase_enhanced.approve').users.ids
        return [('id', 'in', partner_ids)]

    def _get_address_to(self):
        branch_id = self.env['hr.employee'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                company_id=self.env.user.company_id.id).search(
            [('user_id', '=', self.env.user.id)], limit=1).branch_id
        if not branch_id:
           branch_id = self.env.user.user_branch_id     
        location_id = self.env['stock.location'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                     company_id=self.env.user.company_id.id).search(
            [('branche_id', '=', branch_id.id)])
        if location_id:    
            if len(location_id) > 1: 
                location_def_id = location_id.filtered(lambda rec: rec.is_default_for_branch)  
                if location_def_id:
                   return location_def_id[0].id
                else:
                    return location_id[0].id  
            else: return location_id.id


    def _get_edit_address_to(self):
        if self.env.user.has_group('purchase_enhanced.purchase_req_deliver_address'):
           return True
        else:
            return False

    def _get_edit_analytic_account(self):
        if self.env.user.has_group('purchase_enhanced.purchase_req_analytic_account'):
           return True
        else:
            return False       

    def get_current_tz_time(self):
        tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        return UTC.localize(fields.Datetime.now()).astimezone(tz).replace(tzinfo=None)

    def _default_currency_id(self):
        company_id = self.env.context.get('force_company') or self.env.context.get('company_id') or self.env.user.company_id.id
        return self.env['res.company'].browse(company_id).currency_id


    partner_id = fields.Many2one('res.partner', string='Requester Name', default=_getpartner, track_visibility='always')
    requester_id = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user,
                                   track_visibility='always')
    assign_user_ids = fields.Many2many('res.users', string='Assign To User', track_visibility='always')
    department_id = fields.Many2one('hr.department', string="Department",
                                    default=lambda self: self.env['hr.employee'].search(
                                        [('user_id', '=', self.env.user.id)], limit=1).department_id,
                                    track_visibility='always')
    preq_line = fields.One2many('purchase.req.line', 'preq', string="Purchase Request Line", track_visibility='always',copy=True)
    branches = fields.Many2one("bsg_branches.bsg_branches", string="Branch", default=_get_brwise,
                               track_visibility='always')
    branch_no = fields.Char('Branch Number', default=_get_brwise_no, track_visibility='always')
    note = fields.Text('Terms and conditions', track_visibility='always')
    request_type = fields.Selection(_get_request_oprions,
                                    required=True, track_visibility='always')
    has_two_type_group = fields.Boolean()
    user_analytic_account = fields.Many2one('account.analytic.account', default=_get_user_analytic, index=True)
    name = fields.Char(track_visibility='always', default='/')
    date_pr = fields.Datetime("Date", default=fields.Datetime.now, track_visibility='always')
    state = fields.Selection([
        ('tsub', 'To Submit'),
        ('tapprove', 'To Approve'),
        ('approve', 'Approved'),
        ('open', 'Open'), ('close', 'Close'),
        ('reject', 'Reject'), ('cancel', 'Cancel'),
        ('done', 'Done')], string='States', default='tsub', track_visibility='always')
    reject_reason = fields.Text(string="Reject Reason", track_visibility='always')
    purchase_order_ids = fields.One2many('purchase.order', 'purchase_transfer', track_visibility='always', index=True)

    purchase_picking_count = fields.Integer(compute='_compute_picking', string='Picking count', default=0, store=True)
    purchase_order_picking_ids = fields.Many2many('stock.picking', compute='_compute_picking', string='Receptions', copy=False, store=True)


    purchase_recieve_ids = fields.One2many('purchase.req.rec', 'purchase_transfer', track_visibility='always',
                                           index=True)
    purchase_transfer_ids = fields.One2many('purchase.transfer', 'purchase_transfer', track_visibility='always',
                                            index=True)
    set_to_close = fields.Boolean("Can Close It", compute="compute_to_close", default=False, store=True,
                                  track_visibility='always')

    manager_ids = fields.Many2many('res.users', 'purchase_requset_manager_users', 'purchase_id', 'user_id',
                                   default=_get_default_manager, domain=_get_manager_domain, index=True)
    reciepts_ids = fields.Many2many('res.users', 'purchase_requset_stock_users', 'purchase_id', 'user_id',
                                    domain=_get_reciepts_domain, index=True)
    message_managger_text = fields.Html("Manager Message")
    message_reciepts_text = fields.Html("Reciepts Message")
    manager_format = fields.Char(compute='_compute_manager_format', store=True)
    reciepts_format = fields.Char(compute='_compute_reciepts_format', store=True)
    transfer_number = fields.Char(track_visibility='always')
    address_to = fields.Many2one('stock.location', 'Deliver Address', default=_get_address_to)
    can_edit_address_to = fields.Boolean(compute='_get_address_to_edit',default=_get_edit_address_to)
    can_edit_analytic_account = fields.Boolean(compute='_get_address_to_edit',default=_get_edit_analytic_account)

    po_count = fields.Integer(string='Rfq Count  ', compute='_pocount')
    sp_count = fields.Integer(string='Rfq Count', compute='_spcount')
    it_count = fields.Integer(string='Internal Transfer Count', compute='_itcount')
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    company_id = fields.Many2one('res.company', 'Company', index=True,default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', 'Currency',default=_default_currency_id)
    is_recieved = fields.Boolean(track_visibility='always',copy=False)
    can_recieve = fields.Boolean(compute='is_can_recieve')
    transfer_picking_ids = fields.One2many('stock.picking', 'purchase_req_id', string='Transfer Pickings')
    

    def is_can_recieve(self):
        for rec in self:
            rec.can_recieve = False
            if rec.request_type == 'branch':
                if any(rec.preq_line.filtered(lambda s:s.iss_qty)):
                    rec.can_recieve = True 
                #if any(rec.preq_line.filtered(lambda s:s.qty_received and s.transfer_deliver_to.id == rec.address_to.id)):   
                #    rec.can_recieve = True 
                if len(rec.preq_line.filtered(lambda s:s.product_id.type == 'service')) > 0:
                    rec.can_recieve = True 


    def _get_address_to_edit(self):
        for rec in self:
            if rec.env.user.has_group('purchase_enhanced.purchase_req_deliver_address'):
                rec.can_edit_address_to = True
            else:
                rec.can_edit_address_to = False
            if rec.env.user.has_group('purchase_enhanced.purchase_req_analytic_account'):
                rec.can_edit_analytic_account = True
            else:
                rec.can_edit_analytic_account = False



    @api.depends('purchase_order_ids.order_line.move_ids.returned_move_ids',
                 'purchase_order_ids.order_line.move_ids.state',
                 'purchase_order_ids.order_line.move_ids.picking_id')
    def _compute_picking(self):
        for order in self:
            order.purchase_order_picking_ids = order.purchase_order_ids.mapped('picking_ids')
            order.purchase_picking_count = len(order.purchase_order_ids.mapped('picking_ids'))

    # @api.multi
    def set_recieve(self):
        for rec in self:
            rec.is_recieved = True
            
    # @api.multi
    def open_attach_wizard(self):
        view_id = self.env.ref('purchase_enhanced.view_attachment_form_purchase_req').id
        return {
            'name': _('Attachments'),
            'res_model': 'ir.attachment',
            'view_type': 'form',
            'context': "{'default_res_model': '%s','default_res_id': %d,'default_purchase_req_id': %d,'default_type': 'binary'}" % (
                self._name, self.id, self.id),
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }

    # @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('purchase_enhanced.action_attachment')
        return res

    # @api.multi
    def _compute_attachment_number(self):
        for rec in self:
            rec.attachment_number = self.env['ir.attachment'].search_count(
                [('res_model', '=', 'purchase.req'), ('res_id', '=', rec.id)])

    @api.model
    def create(self, vals):
        if 'preq_line' not in vals:
            raise UserError(_("Please at least add one line to save record."))
        result = super(PurchaseRequisition, self).create(vals)
        result.name = '*' + str(result.id)
        return result

    # @api.multi
    def write(self, values):
        res = super(PurchaseRequisition, self).write(values)
        for rec in self:
            if not rec.preq_line:
                raise UserError(_("Please at least add one line to save record"))
        return

    # @api.multi
    def unlink(self):
        for s in self:
            if (s.state != 'tsub'):
                raise UserError(_("You cannot delete a purchase request that is already done or approved."))
        return super(PurchaseRequisition, self).unlink()

    @api.depends('manager_ids')
    def _compute_manager_format(self):
        list_ids = []
        for rec in self:
            for manag in rec.manager_ids.mapped('partner_id'):
                list_ids.append(str(manag.id))
            rec.manager_format = ','.join(list_ids)

    @api.depends('reciepts_ids')
    def _compute_reciepts_format(self):
        list_ids = []
        for rec in self:
            for res in rec.reciepts_ids.mapped('partner_id'):
                list_ids.append(str(res.id))
            for rec in self.preq_line.mapped('assgined_user_ids.partner_id'):   
                list_ids.append(str(rec.id))
            rec.reciepts_format = ','.join(list_ids)

    @api.depends('preq_line.qty', 'preq_line.qty_po', 'preq_line.qty_received')
    def compute_to_close(self):
        for rec in self:
            if all(s.qty_received == s.qty_po and s.qty_po != 0 for s in rec.preq_line):
                rec.set_to_close = True
            else:
                rec.set_to_close = False

    def set_to_done(self):
        for rec in self:
            if all(s.state != 'cancel' and s.product_id.type == 'service' and s.qty <= s.qty_po for s in rec.preq_line):
                rec.purchase_transfer_ids.write({'state': 'done'})
                rec.purchase_recieve_ids.write({'state': 'done'})
                rec.write({'state': 'done'})
            if rec.request_type == 'stock':
                for line in rec.preq_line.filtered(lambda s:s.state != 'cancel'):
                    if line.qty <= line.qty_received or (line.product_id.type == 'service' and line.qty <= line.qty_po):
                        line.transfer_line_ids.write({'state':'done'})
                        line.purchase_rec_line_ids.write({'state':'done'})
                        line.write({'state':'done'})
                    else:
                        line.transfer_line_ids.write({'state':'open'})
                        line.purchase_rec_line_ids.write({'state':'open'})
                        line.write({'state':'open'})

                if all(s.product_id.type != 'service' and s.qty <= s.qty_received and s.qty != 0 for s in
                       rec.preq_line):
                    rec.purchase_transfer_ids.write({'state': 'done'})
                    rec.purchase_recieve_ids.write({'state': 'done'})
                    rec.write({'state': 'done'})
            if rec.request_type in ['workshop','manufacture']:
                for line in rec.preq_line.filtered(lambda s:s.state != 'cancel'):
                    if line.qty <= line.iss_qty or (line.product_id.type == 'service' and line.qty <= line.qty_po):
                        line.transfer_line_ids.write({'state':'done'})
                        line.purchase_rec_line_ids.write({'state':'done'})
                        line.write({'state':'done'})
                    else:
                        line.transfer_line_ids.write({'state':'open'})
                        line.purchase_rec_line_ids.write({'state':'open'})
                        line.write({'state':'open'})    
                if all(s.product_id.type != 'service' and s.qty <= s.iss_qty and s.qty != 0 for s in rec.preq_line):
                    rec.purchase_transfer_ids.write({'state': 'done'})
                    rec.purchase_recieve_ids.write({'state': 'done'})
                    rec.write({'state': 'done'})
            if rec.request_type == 'branch':
                for line in rec.preq_line.filtered(lambda s:s.state != 'cancel'):
                    if (line.qty <= line.iss_qty) or (line.product_id.type == 'service' and line.qty <= line.qty_po) or (line.qty <= line.qty_received and line.purchase_rec_line_ids and line.purchase_rec_line_ids[0].deliver_to.default_location_dest_id.id == rec.address_to.id):
                        line.transfer_line_ids.write({'state':'done'})
                        line.purchase_rec_line_ids.write({'state':'done'})
                        line.write({'state':'done'})
                    else:
                        line.transfer_line_ids.write({'state':'open'})
                        line.purchase_rec_line_ids.write({'state':'open'})
                        line.write({'state':'open'})    
                if all((
                               s.product_id.type != 'service' and s.qty <= s.qty_received and s.purchase_rec_line_ids and s.purchase_rec_line_ids[0].deliver_to.default_location_dest_id.id == rec.address_to.id) or
                       (
                               s.product_id.type != 'service' and s.qty <= s.iss_qty and s.transfer_deliver_to.id != rec.address_to.id)
                       for s in rec.preq_line):
                    rec.purchase_transfer_ids.write({'state': 'done'})
                    rec.purchase_recieve_ids.write({'state': 'done'})
                    rec.write({'state': 'done'})

    # @api.multi
    def order_close(self):
        for rec in self:
            rec.set_to_done()
            rec.purchase_recieve_ids.write({'state': 'close'})
            rec.purchase_recieve_ids.mapped('preq_rec_line').filtered(lambda line: line.state != 'done').write({'state': 'close'})
            rec.purchase_transfer_ids.write({'state': 'close'})
            rec.purchase_transfer_ids.mapped('purchase_line').filtered(lambda line: line.state != 'done').write({'state': 'close'})
            rec.preq_line.filtered(lambda line: line.state != 'done').write({'state': 'close'})
            rec.write({'state': 'close'})

    # @api.multi
    def action_reject(self):
        self.state = 'reject'

    # @api.multi
    def action_cancel(self):
        for rec in self:
            if any(st == 'purchase' for st in rec.preq_line.mapped('purchase_order_line_ids.order_id.state')) or any(st == 'done' for st in rec.preq_line.mapped('move_ids.picking_id.state')): 
                raise UserError(_("Sorry,Can't Cancel P.R it has confirmed PO Or Validated Stock Move"))
            else:
                rec.preq_line.mapped('purchase_order_line_ids.order_id').button_cancel()
                rec.preq_line.mapped('move_ids.picking_id').action_cancel()
                if not rec.preq_line.mapped('purchase_order_line_ids') and not rec.preq_line.mapped('move_ids'):
                    rec.purchase_recieve_ids.mapped('preq_rec_line').sudo().unlink()
                    rec.purchase_recieve_ids.sudo().unlink()
                    rec.purchase_transfer_ids.mapped('purchase_line').sudo().unlink()
                    rec.purchase_transfer_ids.sudo().unlink()
                else:    
                    rec.purchase_recieve_ids.write({'state': 'cancel'})
                    rec.purchase_transfer_ids.write({'state': 'cancel'})
                rec.write({'state': 'cancel'})
                rec.preq_line.write({'state': 'cancel'})

    # @api.multi
    def action_set_to_draft(self):
        for rec in self:
            rec.write({'state': 'tsub'})  
            rec.preq_line.write({'state': 'tsub'})          


    # @api.multi
    def get_form_view(self):
        if self.env.user.has_group('purchase_enhanced.all_access'):
            purchase_action = self.env.ref('purchase_enhanced.action_purchase_advisor')
            action = purchase_action.read()[0]
            action['views'] = [(self.env.ref('purchase_enhanced.view_purchase_req_advisor_form').id, 'form')]
        elif self.env.user.id in self.assign_user_ids.ids:
            purchase_action = self.env.ref('purchase_enhanced.action_purchase_approve')
            action = purchase_action.read()[0]
            action['views'] = [(self.env.ref('purchase_enhanced.view_purchase_req_form_approved').id, 'form')]
        elif self.env.user.id == self.requester_id.id:
            purchase_action = self.env.ref('purchase_enhanced.action_purchase_req')
            action = purchase_action.read()[0]
            action['views'] = [(self.env.ref('purchase_enhanced.view_purchase_req_form').id, 'form')]
        else:
            purchase_action = self.env.ref('purchase_enhanced.action_purchase_approve')
            action = purchase_action.read()[0]
            action['views'] = [(self.env.ref('purchase_enhanced.view_purchase_req_form_approved').id, 'form')]
        action['view_mode'] = 'form'
        action['res_id'] = self.id
        return action

    def submission(self):
        if not self.preq_line:
            raise UserError(_("Please Add Lines To Submit"))
        if not self.manager_ids:
            raise UserError(_("Please Add Manager"))
        if self.state == 'tsub':
            branch_number = self.branch_no
            if self.name == '/' or str(self.name).__contains__('*'):
                sequence = self.env.ref('purchase_enhanced.ir_sequence_purchasecollection').next_by_id()
                if branch_number:
                    self.name = "PR/%s%s" % (branch_number, sequence)
                else:
                    self.name = "PR/%s" % (sequence)
            self.write({'state': 'tapprove'})
            self.preq_line.write({'state': 'tsub'})  
        template_id = self.env.ref('purchase_enhanced.email_template_for_purchase_requset_manager')
        template_id.send_mail(self.id, force_send=True, raise_exception=True)
        self.message_post(subject=_('Requset Send To Approve'),
                          body='Requset Sent To : %s' % (self.manager_ids.mapped('name')))
        self.assign_user_ids = self.manager_ids

    def approved(self):
        if self.state == 'cancel':
            raise UserError(_("Sorry , This Request is already has been canceled"))
        if self.request_type != 'stock' and not all(s.product_id.type in ['service','consu'] for s in self.preq_line) and not self.reciepts_ids and not self.preq_line.mapped('assgined_user_ids'):
            raise UserError(_("Please Add Receipts"))
        if self.purchase_transfer_ids.filtered(lambda s:s.state != 'cancel'):
            raise UserError(_("Sorry , This Request is already has been sent to proceed"))
        for line in self.preq_line:
                stock = self.env['stock.quant'].sudo().search(
                    [('product_id', '=', line.product_id.id), ('location_id.usage', '=', 'internal'),
                    ('location_id', 'child_of', line.user_warehouse_id.view_location_id.id),
                    ('location_id.company_id', '=', line.user_warehouse_id.view_location_id.company_id.id)])
                line.onhand_on_approve = sum(stock.mapped('quantity'))
        if self.request_type == 'workshop':
            res_id = self.create_purchase_transfer()
            res_id.reciepts_ids = self.reciepts_ids + self.preq_line.mapped('assgined_user_ids')
            res_id.message_subscribe(res_id.reciepts_ids.mapped('partner_id.id'))
            self.preq_line.write({'state': 'open'})
            self.write({'state': 'approve', 'transfer_number': res_id.name})
            template_id = self.env.ref('purchase_enhanced.email_template_for_purchase_requset_stock')
            template_id.send_mail(self.purchase_transfer_ids.filtered(lambda s: s.state in ['approve', 'open'])[0].id,
                                  force_send=True, raise_exception=True)
            self.message_post(subject=_('Requset Send To Stock'),
                              body='Requset Sent To : %s' % (res_id.reciepts_ids.mapped('name')))

        elif self.request_type == 'manufacture':
            res_id = self.create_purchase_transfer_manufacture()
            res_id.reciepts_ids = self.reciepts_ids + self.preq_line.mapped('assgined_user_ids')
            res_id.message_subscribe(res_id.reciepts_ids.mapped('partner_id.id'))
            self.preq_line.write({'state': 'open'})
            self.write({'state': 'approve', 'transfer_number': res_id.name})
            template_id = self.env.ref('purchase_enhanced.email_template_for_purchase_requset_stock')
            template_id.send_mail(self.purchase_transfer_ids.filtered(lambda s: s.state in ['approve', 'open'])[0].id,
                                  force_send=True, raise_exception=True)
            self.message_post(subject=_('Requset Send To Stock'),
                              body='Requset Sent To : %s' % (res_id.reciepts_ids.mapped('name')))

        elif self.request_type == 'stock' or all(s.product_id.type in ['service', 'consu'] for s in self.preq_line):
            self.create_purchase()
        else:
            res_id = self.create_purchase_transfer()
            res_id.reciepts_ids = self.reciepts_ids + self.preq_line.mapped('assgined_user_ids')
            res_id.message_subscribe(res_id.reciepts_ids.mapped('partner_id.id'))
            self.preq_line.write({'state': 'open'})
            self.write({'state': 'approve', 'transfer_number': res_id.name})
            template_id = self.env.ref('purchase_enhanced.email_template_for_purchase_requset_stock')
            if len(self.purchase_transfer_ids.filtered(lambda s:s.state in ['approve','open'])) > 0:
                template_id.send_mail(self.purchase_transfer_ids.filtered(lambda s:s.state in ['approve','open'])[0].id, force_send=True, raise_exception=True)
            self.message_post(subject=_('Requset Send To Stock'),
                              body='Requset Sent To : %s' % (res_id.reciepts_ids.mapped('name')))

    def approved_redirect(self):
        if not self.reciepts_ids:
            raise UserError(_("Please Add Receipts"))
        for rec in self.purchase_transfer_ids:
            rec.reciepts_ids = self.reciepts_ids
        self.purchase_transfer_ids.message_subscribe(self.reciepts_ids.mapped('partner_id.id'))
        template_id = self.env.ref('purchase_enhanced.email_template_for_purchase_requset_stock')
        template_id.send_mail(self.purchase_transfer_ids.filtered(lambda s:s.state in ['approve','open'])[0].id, force_send=True, raise_exception=True)
        self.message_post(subject=_('Requset Send To Stock'),
                          body='Requset Sent To :%s' % (self.reciepts_ids.mapped('name')))

    def create_purchase_transfer_manufacture(self):
        list_1 = []
        for s in self.preq_line:
            list_1.append({
                'product_id': s.product_id.id,
                'ord_qty': s.qty,
                'name': s.name,
                'purchase_req_line_id': s.id,
                'purchase_req_id': self.id,
                'analytic_account_id': s.analytic_account_id.id,
                'deliver_to': s.deliver_to.id,
                'sequence': s.sequence,
            })
        res_id = self.env['purchase.transfer'].create({
            'name': self.name,
            'date_pr': self.date_pr,
            'manufacturing_order_id': self.manufacturing_order_id.id,
            'state': 'approve',
            'purchase_line': [(0, 0, s) for s in list_1],
            'purchase_transfer': self.id,
            'request_type': self.request_type,

        })
        return res_id


    def create_purchase_transfer(self):
        list_1 = []
        for s in self.preq_line:
            fleet_ref = False
            if s.fleet_id_ref:
                if str(s.fleet_id_ref).__contains__('fleet_trailer'):
                    fleet_ref = str("bsg_fleet_trailer_config") + "," + str(s.fleet_id_ref.id)
                if str(s.fleet_id_ref).__contains__('fleet.vehicle'):
                    fleet_ref = str("fleet.vehicle") + "," + str(s.fleet_id_ref.id)
            list_1.append({
                'product_id': s.product_id.id,
                # 'onhand':s.onhand,
                'ord_qty': s.qty,
                'name': s.name,
                'purchase_req_line_id': s.id,
                'work_order_id': s.work_order_id,
                'fleet_id_ref': fleet_ref,
                'purchase_req_id': self.id,
                'analytic_account_id': s.analytic_account_id.id,
                'deliver_to': s.deliver_to.id,
                'sequence' : s.sequence,
            })
        res_id = self.env['purchase.transfer'].create({
            'name': self.name,
            'date_pr': self.date_pr,
            'state': 'approve',
            'partner_id': self.partner_id.id,
            'department_id': self.department_id.id,
            'branches': self.branches.id,
            'purchase_line': [(0, 0, s) for s in list_1],
            'purchase_transfer': self.id,
            'request_type': self.request_type,
            'address_to': self.address_to.id,
            'company_id': self.company_id.id,

        })
        return res_id

    def create_purchase(self):
        if self.state == 'cancel':
            raise UserError(_("Sorry , This Request is already has been canceled"))
        purchase_ids = self.env['purchase.req.rec'].sudo().search([('purchase_transfer', '=', self.id),('state','!=','cancel')])
        if purchase_ids:
            raise UserError(_("Sorry , This Request is already has been sent to proceed")) 
        list_1 = []
        for s in self.preq_line:
            fleet_ref = False
            if s.fleet_id_ref:
                if str(s.fleet_id_ref).__contains__('fleet_trailer'):
                    fleet_ref = str("bsg_fleet_trailer_config") + "," + str(s.fleet_id_ref.id)
                if str(s.fleet_id_ref).__contains__('fleet.vehicle'):
                    fleet_ref = str("fleet.vehicle") + "," + str(s.fleet_id_ref.id)
            if not s.deliver_to and s.product_id.type not in ['service','consu']:
                raise UserError(_("Please Specify Deliver To Picking For Line!!"))
            list_1.append({
                'product_id': s.product_id.id,
                'qty': s.qty,
                'onhand': s.onhand,
                'name': s.name,
                'purchase_req_line_id': s.id,
                'work_order_id': s.work_order_id,
                'fleet_id_ref': fleet_ref,
                'purchase_req_id': self.id,
                'deliver_to': s.deliver_to.id,
                'analytic_account_id': s.analytic_account_id.id,
                'sequence' : s.sequence,
                'company_id':self.company_id.id
            })

        if (list_1):
            self.env['purchase.req.rec'].sudo().create({
                'name': self.name,
                'date_pr': self.date_pr,
                'request_type': self.request_type,
                'state': 'open',
                'partner_id': self.partner_id.id,
                'department_id': self.department_id.id,
                'branches': self.branches.id,
                'preq_rec_line': [(0, 0, s) for s in list_1],
                'purchase_transfer': self.id,
                'address_to': self.address_to.id,
                'company_id': self.company_id.id
            })
            self.write({'state': 'open'})
            self.preq_line.write({'state': 'open'})

    @api.constrains('preq_line')
    # @api.one
    def check_prodcut_line(self):
        if self.request_type == 'stock':
            product_list = []
            for data in self.preq_line:
                if not data.product_id in product_list:
                    product_list.append(data.product_id)
                else:
                    raise UserError(_("Duplicate products in Requst line not allowed !"))

    @api.constrains('request_type')
    def constrains_request_type(self):
        for rec in self:
            if not rec.request_type:
                raise UserError(_("Please Enter Request Type"))

    # Quick Access###################
    # @api.multi
    def _pocount(self):
        po_count = self.env['purchase.order'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('purchase_transfer','=',self.id),('is_copy','=',True)])
        self.update({
            'po_count': len(set(po_count))
        })

    # @api.multi
    def _spcount(self):
        for rec in self:
            rec.sp_count = 0
            pt_count = rec.env['purchase.transfer'].sudo().with_context(force_company=rec.env.user.company_id.id,
                                                                         company_id=rec.env.user.company_id.id).search(
                [('purchase_transfer', '=', rec.id)])
            for pt in pt_count:
                sp_count = rec.env['stock.picking'].sudo().with_context(force_company=rec.env.user.company_id.id,
                                                                         company_id=rec.env.user.company_id.id).search(
                    [('origin', '=', pt.name)])

                rec.sp_count = len(set(sp_count))

                # self.update({
                #     'sp_count': len(set(sp_count))
                # })

    # @api.multi
    def _itcount(self):
        pass
        itcount = self.env['purchase.transfer'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                    company_id=self.env.user.company_id.id).search(
            [('purchase_transfer', '=', self.id)])
        self.update({
            'it_count': len(set(itcount))
        })

    def action_view_po(self):
        po = self.env['purchase.order'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('purchase_transfer','=',self.id),('is_copied','=',True)])
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        if len(po) > 1:
            action['domain'] = [('id', 'in', po.ids)]
        elif len(po) == 1:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = po.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_sp(self):
        pt_count = self.env['purchase.transfer'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                     company_id=self.env.user.company_id.id).search(
            [('purchase_transfer', '=', self.id)])
        po = self.env['stock.picking'].with_context(force_company=self.env.user.company_id.id,
                                                           company_id=self.env.user.company_id.id).search(
            [('origin', '=', pt_count.name)])
        if len(po) == 1:
            views = [(self.env.ref('purchase_enhanced.view_view_picking_form_receipts_in_po').id, 'form'),(self.env.ref('purchase_enhanced.vpicktree_purchase_order').id, 'tree')] 
            return {
                'name': _('Transfers'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'view_id': False,
                'views': views,
                'res_id': po.id,
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', po.ids)],
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
            'domain': [('id', 'in', po.ids)],
        }    

    def action_view_it(self):
        it = self.env['purchase.transfer'].search([('purchase_transfer', '=', self.id)])
        action = self.env.ref('purchase_enhanced.action_purchase_transfer').read()[0]
        if len(it) > 1:
            action['domain'] = [('id', 'in', it.ids)]
        elif len(it) == 1:
            action['views'] = [(self.env.ref('purchase_enhanced.view_purchase_transfer_form').id, 'form')]
            action['res_id'] = it.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def compute_message_note(self,message_managger_text):
        body = tools.html_sanitize(message_managger_text)
        message_note = self.env['mail.template']._render_template(body, 'purchase.req', self.id)
        return message_note


    # @api.multi
    def action_view_picking(self):
        """ This function returns an action that display existing picking orders of given purchase order ids. When only one found, show the picking immediately.
        """
        pick_ids = self.mapped('purchase_order_picking_ids')
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
    _name = 'purchase.req.line'
    _description = "Purchase Req Line"
    _order = 'date_pr desc'

    preq = fields.Many2one('purchase.req', string="Purchase Request")
    product_id = fields.Many2one('product.product', string='Requested Product',domain=[('purchase_ok', '=', True)], required=True)
    product_type = fields.Selection([('consu', 'Consumable'), ('service', 'Service'),
                                     ('product', 'Storeable')], string='Product Type', related='product_id.type',
                                    store=True)

    product_categ = fields.Many2one('product.category', string='Product Category', required=True)
    qty = fields.Float('Requested Qty')
    name = fields.Text(string='Description', required=True)
    onhand = fields.Float("On Hand")
    work_order_id = fields.Char(string='Work Order')
    move_ids = fields.One2many('stock.move', 'purchase_req_line_id', string='Stock Move', readonly=True,
                               ondelete='set null', copy=False)
    purchase_order_line_ids = fields.One2many('purchase.order.line', 'purchase_req_line_id',
                                              string='Purchase Order Line', readonly=True, ondelete='set null',
                                              copy=False)
    qty_po = fields.Float(compute='_compute_line_qty', string="PO Qty", store=True, compute_sudo=True)
    qty_rfq = fields.Float(compute='_compute_line_qty', string="Rfq Qty", store=True, compute_sudo=True)
    qty_received = fields.Float(compute='_compute_line_qty', string="Received Qty", store=True, compute_sudo=True)
    qty_returned = fields.Float(compute='_compute_line_qty', string="Returned Qty", store=True, compute_sudo=True)
    qty_net_received = fields.Float(compute='_compute_line_qty', string="Net Received Qty", store=True,
                                    compute_sudo=True)
    iss_qty = fields.Float(string="ISS Qty", compute='_compute_iss_qty',store=True,compute_sudo=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Acount")

    partner_id = fields.Many2one('res.partner', related='preq.partner_id', store=True, string='Requester Name',
                                 track_visibility='always')
    requester_id = fields.Many2one('res.users', 'Current User', related='preq.requester_id', store=True,
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
        ('done', 'Done')], string='States', track_visibility='always',default='tsub')
    request_type = fields.Selection([('stock', 'For Stock'), ('workshop', 'For Workshop'), ('branch', 'For Branch')],
                                    related='preq.request_type', store=True, track_visibility='always')

    fleet_id = fields.Many2one('trailer.vehicle.connect.view', ondelete="set null")
    fleet_id_ref = fields.Reference(string='Fleet Ref',
                                    selection=[('fleet.vehicle', 'Vehicle'), ('bsg_fleet_trailer_config', 'Trailer')])
    fleet_num = fields.Char(string="Fleet", compute='_compute_fleet_ref_tag', store=True, track_visibility=True)
    onhand_on_approve = fields.Float("Onhand On Approve")
    deliver_to = fields.Many2one('stock.picking.type')
    transfer_line_ids = fields.One2many('purchase.transfer.line', 'purchase_req_line_id')
    purchase_rec_line_ids = fields.One2many('purchase.req.rec.line', 'purchase_req_line_id')
    transfer_deliver_to = fields.Many2one('stock.location',
                                          related='transfer_line_ids.deliver_to.default_location_dest_id', store=True)
    sequence = fields.Integer('No#',compute='_compute_line_sequence',
                                       store=True)
    assgined_user_ids = fields.Many2many('res.users','purchase_req_line_user_rel','req_line_id','user_id',related='product_categ.assgined_user_ids',index=True,store=True)                                   
    company_id = fields.Many2one('res.company', related='preq.company_id', string='Company', store=True, readonly=True)
    currency_id = fields.Many2one(related='preq.currency_id', store=True, string='Currency', readonly=True)

    #Purchase Field:
    price_unit = fields.Float(compute='_compute_amount',string='Unit Price',store=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    discount_percent = fields.Float(compute='_compute_amount',string='Discount (%)') 
    discount_amount = fields.Float(compute='_compute_amount',string='Discount Amount')
    qty_received_price = fields.Monetary(compute='_compute_qty_recieved_amount', string='Qty Received Price', store=True)                                           
    partner_ids = fields.Many2many('res.partner',compute='_compute_purchase_vendor',store=True, string='Vendors', track_visibility='always')
    
    #Invoice Field:
    qty_invoiced = fields.Float(compute='_compute_invoice_qty', string="Qty",store=True)
    invoice_price_unit = fields.Float(compute='_compute_invoice_amount',string='Unit Price',store=True)
    invoice_price_subtotal = fields.Monetary(string='Amount (without Taxes)',
        store=True, readonly=True, compute='_compute_invoice_amount', help="Total amount without taxes")
    invoice_tax_price = fields.Monetary(compute='_compute_invoice_amount',string='Tax Price',store=True) 
    invoice_total_price = fields.Monetary(compute='_compute_invoice_amount',string='Total Price',store=True)
    invoice_discount = fields.Float(string='Discount (%)',compute='_compute_invoice_amount',store=True)
    is_recieved = fields.Boolean()

    _sql_constraints = [('request_product_uniq', 'unique(preq,product_id,fleet_id_ref)',
                         'Duplicate products in Request line not allowed !')]

    @api.onchange('product_categ')
    def _onchange_product_categ(self):
        if self.product_categ:
            return {'domain': {'product_id': [('categ_id', '=', self.product_categ.id)]}}
        else:
            return {'domain': {'product_id': []}}

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_categ = self.product_id.categ_id.id

    @api.onchange('fleet_id')
    def _onchange_fleet_id(self):
        if self.fleet_id:
            self.fleet_id_ref = str(self.fleet_id.res_model) + "," + str(self.fleet_id.res_id)
            self.fleet_num = self.fleet_id.taq_number
            if self.fleet_id.res_model == 'fleet.vehicle':
                if self.fleet_id_ref.vehicle_type.analytic_account_id:
                    self.analytic_account_id = self.fleet_id_ref.vehicle_type.analytic_account_id.id
            else:
                self.analytic_account_id = self.preq.user_analytic_account.id
        else:
            self.analytic_account_id = self.preq.user_analytic_account.id

    @api.depends('fleet_id_ref')
    def _compute_fleet_ref_tag(self):
        for rec in self:
            if rec.fleet_id_ref:
                if str(rec.fleet_id_ref).__contains__('fleet_trailer'):
                    rec.fleet_num = rec.fleet_id_ref.trailer_taq_no
                if str(rec.fleet_id_ref).__contains__('fleet.vehicle'):
                    rec.fleet_num = rec.fleet_id_ref.taq_number

    @api.depends('purchase_order_line_ids.order_id.state', 'move_ids.picking_id.state', 'move_ids.quantity_done',
                 'purchase_order_line_ids.product_qty', 'purchase_order_line_ids.qty_received')
    def _compute_line_qty(self):
        for rec in self:
            # rec.qty_received = self.env['stock.move'].search([('purchase_req_line_id','=',rec.id),('picking_id.state','=','done')],limit=1).quantity_done
            # purchase_line_id = self.env['purchase.order.line'].search([('purchase_req_line_id','=',rec.id),('order_id.state','in',['purchase','done'])])
            # if purchase_line_id:
            rec.qty_po = sum(rec.purchase_order_line_ids.filtered(
                lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('product_qty'))
            rec.qty_rfq = sum(rec.purchase_order_line_ids.filtered(
                lambda m: m.order_id.state == 'draft' or (m.order_id.state == 'done' and m.order_id.is_copy)).mapped(
                'product_qty'))
            rec.qty_received = sum(rec.move_ids.filtered(
                lambda m: m.picking_id.state == 'done' and m.picking_type_id.code == 'incoming' and (m.purchase_line_id or m.created_purchase_line_id)).mapped(
                'quantity_done'))
            rec.qty_returned = sum(rec.move_ids.filtered(
                lambda m: m.picking_id.state == 'done' and m.picking_type_id.code == 'outgoing' and (m.purchase_line_id or m.created_purchase_line_id) ).mapped(
                'quantity_done'))
            rec.qty_net_received = rec.qty_received - rec.qty_returned

    @api.depends('purchase_order_line_ids.order_id.state', 'purchase_order_line_ids.product_qty', 'purchase_order_line_ids.price_total')
    def _compute_amount(self):
        for rec in self:
            rec.price_unit = sum(rec.purchase_order_line_ids.filtered(
                    lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('price_unit'))
            rec.price_subtotal = sum(rec.purchase_order_line_ids.filtered(
                    lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('price_subtotal'))
            rec.price_tax = sum(rec.purchase_order_line_ids.filtered(
                    lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('price_tax'))
            rec.discount_percent = sum(rec.purchase_order_line_ids.filtered(
                    lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('discount_percent'))
            rec.discount_amount = sum(rec.purchase_order_line_ids.filtered(
                    lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('discount_amount'))                
            rec.price_total = sum(rec.purchase_order_line_ids.filtered(
                    lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('price_total'))

    @api.depends('purchase_order_line_ids.order_id.state','purchase_order_line_ids.qty_invoiced')
    def _compute_invoice_qty(self):
        for rec in self:
            rec.qty_invoiced = sum(rec.purchase_order_line_ids.filtered(
                    lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('qty_invoiced'))  

    @api.depends('purchase_order_line_ids.order_id.state','purchase_order_line_ids.partner_id')
    def _compute_purchase_vendor(self):
        for rec in self:
            rec.partner_ids += rec.purchase_order_line_ids.filtered(
                    lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('partner_id')

    # Migration Note
    # @api.depends('purchase_order_line_ids.order_id.state','purchase_order_line_ids.invoice_lines.invoice_id.state','purchase_order_line_ids.invoice_lines.price_total')
    @api.depends('purchase_order_line_ids.order_id.state','purchase_order_line_ids.invoice_lines.move_id.state','purchase_order_line_ids.invoice_lines.price_total')
    def _compute_invoice_amount(self):
        for rec in self: 
            rec.invoice_price_unit = sum(rec.purchase_order_line_ids.filtered(
                    lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('invoice_lines').filtered(lambda s:s.invoice_id.state == 'open').mapped('price_unit')) 
            rec.invoice_discount = sum(rec.purchase_order_line_ids.filtered(
                    lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('invoice_lines').filtered(lambda s:s.invoice_id.state == 'open').mapped('discount'))            
            rec.invoice_price_subtotal = sum(rec.purchase_order_line_ids.filtered(
                    lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('invoice_lines').filtered(lambda s:s.invoice_id.state == 'open').mapped('price_subtotal'))
            rec.invoice_total_price = sum(rec.purchase_order_line_ids.filtered(
                    lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('invoice_lines').filtered(lambda s:s.invoice_id.state == 'open').mapped('price_total'))                                                                           
            rec.invoice_tax_price = rec.invoice_total_price - rec.invoice_price_subtotal
    
    @api.depends('purchase_order_line_ids.qty_received_price','purchase_order_line_ids.order_id.state',)
    def _compute_qty_recieved_amount(self):
        for rec in self:
            rec.qty_received_price = sum(rec.purchase_order_line_ids.filtered(
                            lambda m: m.order_id.state in ('purchase', 'done') and not m.order_id.is_copy).mapped('qty_received_price'))
                    
    # @api.multi
    @api.depends('preq.transfer_picking_ids','preq.transfer_picking_ids.state','preq.transfer_picking_ids.move_line_ids','preq.transfer_picking_ids.move_line_ids.qty_done'\
        ,'preq.transfer_picking_ids.move_line_ids.state','preq.transfer_picking_ids.move_line_ids.move_id.is_return')
    def _compute_iss_qty(self):
        for line in self:
            reciev_total = 0.0
            return_total = 0.0
            if line.preq.transfer_picking_ids and line.preq.transfer_picking_ids.filtered(lambda s:s.state != 'cancel'):
                for pick in line.preq.transfer_picking_ids.filtered(lambda s:s.state != 'cancel'):
                    reciev_total += sum(pick.move_line_ids.filtered(lambda m: m.product_id == line.product_id and m.state == 'done' and not m.mapped('move_id').is_return).mapped('qty_done'))
                    return_total += sum(pick.move_line_ids.filtered(lambda m: m.product_id == line.product_id and m.state == 'done' and m.mapped('move_id').is_return).mapped('qty_done'))
            line.iss_qty = reciev_total - return_total

    # @api.multi
    def remove_fleet_id(self):
        for rec in self:
            rec.fleet_id_ref = False

    @api.constrains('qty')
    def _code_constrains(self):
        for data in self:
            if data.qty <= 0:
                raise UserError(_("Requested Quantity Should be greater Than 0"))

    @api.onchange('qty')
    def check_qty(self):
        if (self.qty <= 0) and self.product_id:
            raise UserError(_("Requested Quantity Should be greater Than 0"))

    '''@api.onchange('product_id')
    def get_qtyonhand(self):
        for rec in self:
            if rec.product_id:
                rec.onhand = rec.product_id.qty_available'''

    # @api.multi
    @api.depends('name')
    def name_get(self):
        res = []
        for bsg in self:
            current = bsg
            if (current.id):
                name = '%s' % (current.preq.name)
                res.append((bsg.id, name))
        return res

    @api.model
    def create(self, vals):
        if vals.get('fleet_id'):
            vals.pop('fleet_id')
        result = super(PurchaseRequisitionLine, self).create(vals)
        return result

    # @api.multi
    def write(self, values):
        if 'fleet_id' in values:
            values.pop('fleet_id')
        return super(PurchaseRequisitionLine, self).write(values)

    # @api.multi
    @api.depends('preq.preq_line')
    def _compute_line_sequence(self):
        for rec in self:
            rec.sequence = (
                max(rec.preq.mapped('preq_line.sequence') or [0]) + 1)


class StockPicking(models.Model):
    _inherit = 'stock.picking.type'

    not_in_pr = fields.Boolean('Not Use In P.R')