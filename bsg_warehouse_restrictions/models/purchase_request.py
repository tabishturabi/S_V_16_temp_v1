# -*- coding: utf-8 -*-

from odoo import models, fields, api,_ 
from odoo.exceptions import UserError

class PurchaseRequest(models.Model):
    _inherit = 'purchase.req'

    def _get_default_manager(self): 
        manager_id = self.env['hr.employee'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('user_id','=',self.env.user.id)],limit=1).parent_id
        manager_id |= manager_id.alternative_employee_id
        return manager_id.filtered(lambda s: s.user_id.has_group('purchase_enhanced.approve')).mapped('user_id.id') 
    
    def _get_restruct_reciepts_domain(self):
        partner_ids = []
        users = self.env.ref('purchase_enhanced.recieve_inventory_purchase_request').users
        for user in users:
            #if any(stock.id == self.env.user.stock_warehouse_id.id for stock in user.stock_warehouse_ids):
            partner_ids.append(user.id)
        return [('id','in',partner_ids)]

    def _get_restruct_manager_domain(self):
        partner_ids = []
        users = self.env.ref('purchase_enhanced.approve').users
        for user in users:
            #if any(stock.id == self.env.user.stock_warehouse_id.id for stock in user.stock_warehouse_ids):
            partner_ids.append(user.id) 
        return [('id','in',partner_ids)]

    user_warehouse_id = fields.Many2one('stock.warehouse',string='Current User warehouse',default=lambda self: self.env.user.stock_warehouse_id)
    manager_ids = fields.Many2many('res.users','purchase_requset_manager_users','purchase_id','user_id',default=_get_default_manager,domain=_get_restruct_manager_domain,index=True)
    reciepts_ids = fields.Many2many('res.users','purchase_requset_stock_users','purchase_id','user_id',domain=_get_restruct_reciepts_domain,index=True)

    def create_purchase_transfer(self):    
        list_1 = []
        for s in self.preq_line:
            fleet_ref = False
            if s.fleet_id_ref:
                if str(s.fleet_id_ref).__contains__('fleet_trailer'):
                    fleet_ref = str("bsg_fleet_trailer_config")+","+str(s.fleet_id_ref.id)
                if str(s.fleet_id_ref).__contains__('fleet.vehicle'):
                    fleet_ref = str("fleet.vehicle")+","+str(s.fleet_id_ref.id)    
            list_1.append({
                        'company_id': self.company_id.id,
                        'product_id':s.product_id.id,
                        #'onhand':s.onhand,
                        'ord_qty':s.qty,
                        'name':s.name,
                        'purchase_req_line_id':s.id,
                        'work_order_id':s.work_order_id,
                        'fleet_id_ref':fleet_ref,
                        'purchase_req_id':self.id,
                        'analytic_account_id':s.analytic_account_id.id,
                        'deliver_to':s.deliver_to.id,
                        'trans_picking_type_id': s.product_id.type != 'product' and s.deliver_to.search([('default_location_src_id','=',s.deliver_to.default_location_dest_id.id)],limit=1).id or False,
                        'sequence' : s.sequence,
                        'user_warehouse_id': ((s.assgined_user_ids and self.request_type == 'branch') and s.assgined_user_ids[0].stock_warehouse_id.id) or ((self.reciepts_ids and self.request_type == 'branch') and self.reciepts_ids[0].stock_warehouse_id.id) or self.env.user.stock_warehouse_id.id,
                        })              
        res_id =self.env['purchase.transfer'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create({
                    'name':self.name,
                    'date_pr':self.date_pr,
                    'state':'approve',
                    'partner_id':self.partner_id.id,
                    'department_id':self.department_id.id,
                    'branches':self.branches.id,
                    'purchase_line':[(0, 0, s)for s in list_1],
                    'purchase_transfer':self.id,
                    'request_type':self.request_type,
                    'address_to':self.address_to.id,
                    'company_id': self.company_id.id,
                    'user_warehouse_id': (self.reciepts_ids and self.request_type == 'branch') and self.reciepts_ids[0].stock_warehouse_id.id or self.env.user.stock_warehouse_id.id,
                    
                })                
        return res_id

    def submission(self):
        if not self.preq_line:
            raise UserError(_("Please Add Lines To Submit"))
        if not all(line.product_id.without_approve for line in self.preq_line) and not self.manager_ids:
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
            if all(line.product_id.without_approve for line in self.preq_line):
                self.approved()
        template_id = self.env.ref('purchase_enhanced.email_template_for_purchase_requset_manager')
        template_id.send_mail(self.id, force_send=True, raise_exception=True)
        self.message_post(subject=_('Requset Send To Approve'),
                          body='Requset Sent To : %s' % (self.manager_ids.mapped('name')))
        self.assign_user_ids = self.manager_ids


class PurchaseRequestTransfer(models.Model):
    _inherit = 'purchase.transfer'

    user_warehouse_id = fields.Many2one('stock.warehouse',string='Created User warehouse',default=lambda self: self.env.user.stock_warehouse_id)

    def get_move_picking(self,picking_type_id):
        list_2 = []
        for s in self.purchase_line.filtered(lambda s:s.trans_picking_type_id.id == picking_type_id.id and s.iss_qty < s.ord_qty and s.given > 0 and (s.iss_qty+s.given) <= s.ord_qty and s.state in ['open','approve']):
                fleet_ref = False
                if s.fleet_id_ref:
                    if str(s.fleet_id_ref).__contains__('fleet_trailer'):
                        fleet_ref = str("bsg_fleet_trailer_config")+","+str(s.fleet_id_ref.id)
                    if str(s.fleet_id_ref).__contains__('fleet.vehicle'):
                        fleet_ref = str("fleet.vehicle")+","+str(s.fleet_id_ref.id)
                list_2.append([0,0,{
                                'name':'/',
                                'product_id':s.product_id.id,
                                'product_uom':s.product_id.uom_id.id,
                                'product_uom_qty':s.given,
                                #'quantity_done' : s.given,
                                #'reserved_availablitiy' : s.given,
                                'purchase_req_line_id' : s.purchase_req_line_id.id,
                                'purchase_transfer_line_id' : s.id,
                                'work_order_id' : s.work_order_id,
                                'fleet_id_ref' : fleet_ref,
                                'department_id':self.department_id.id,
                                'branch_id' : self.branches.id,
                                'analytic_account_id' : s.analytic_account_id.id ,
                                'purchase_req_id' : self.purchase_transfer.id,
                                'description' : s.name,
                                'date_expected':fields.Datetime.now(),
                                'state':'draft',
                            }]) 
        return  list_2                   

    def create_delivery_picking(self,picking_type_id):
        lines = []
        for s in self.purchase_line.filtered(lambda s:s.trans_picking_type_id.id == picking_type_id.id and s.given > 0 and  s.iss_qty < s.ord_qty and (s.iss_qty+s.given) <= s.ord_qty and s.state in ['open','approve']):
            onhand =0
            if s.product_id.type == 'product':
                onhand = s._compute_qty_on_hand_by_location(picking_type_id.default_location_src_id)
            else: 
                onhand = s.qty_net_received  
            if onhand > 0:
                if(s.given == 0.0):
                    raise UserError(_("Enter Total Given Quantity For Lines"))
                if(s.given > onhand):
                    if s.product_id.type == 'product':
                        raise UserError(_("Total Given Quantity For Lines Must Be Less Than On Hand Qty"))
                    else:   
                        raise UserError(_("Total Given Quantity For Lines Must Be Less Than Net Recieved Qty")) 
                if(s.given > s.ord_qty):
                    raise UserError(_("Total Given Quantity For Lines Must Be Less Than Requested Qty"))
                lines.append(s)        
        if len(lines) < 1:  
            raise UserError(_("Sorry No Lines Has On-Hand Location To Proceed"))   
        picking_lines = self.get_move_picking(picking_type_id)          
        order_dict = {
            'picking_type_id' :picking_type_id.id,
            'origin':self.name,
            'scheduled_date':fields.Datetime.now(),
            'partner_id': self.partner_id.id,
            'pur_tran':self.id,
            'purchase_req_id':self.purchase_transfer.id,
            'request_type':self.request_type,
            'show_operations': True,
            'move_ids_without_package':picking_lines,
            'location_id':picking_type_id.default_location_src_id.id,
            'location_dest_id':picking_type_id.default_location_dest_id.id
            }
        picking_id  = self.env['stock.picking'].create(order_dict)
        picking_id.onchange_picking_type()
        if picking_type_id.code == 'internal':
            picking_id._onchange_pur_tran()
        picking_id.action_confirm()
        picking_id.action_assign()
        for move in picking_id.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
        picking_id.with_context(without_set_pr_to_done=True).button_validate()
        return [picking_id]
    

    def create_internal_picking(self,picking_type_id):
        lines = []
        for s in self.purchase_line.filtered(lambda s:s.trans_picking_type_id.id == picking_type_id.id and s.given > 0 and  s.iss_qty < s.ord_qty and (s.iss_qty+s.given) <= s.ord_qty and s.state in ['open','approve']):
            onhand =0
            if s.product_id.type == 'product':
                onhand = s._compute_qty_on_hand_by_location(picking_type_id.default_location_src_id)
            else: 
                onhand = s.qty_net_received         
            if onhand > 0:
                if(s.given == 0.0):
                    raise UserError(_("Enter Total Given Quantity For Lines"))
                if(s.given > onhand):
                    if s.product_id.type == 'product':
                        raise UserError(_("Total Given Quantity For Lines Must Be Less Than On Hand Qty"))
                    else:   
                        raise UserError(_("Total Given Quantity For Lines Must Be Less Than Net Recieved Qty"))
                if(s.given > s.ord_qty):
                    raise UserError(_("Total Given Quantity For Lines Must Be Less Than Requested Qty"))
                lines.append(s)
        if len(lines) < 1:  
            raise UserError(_("Sorry No Lines Has On-Hand For Location To Proceed"))      
        context = {
            'default_picking_type_id' :picking_type_id.id, 
            'default_origin':self.name,
            'default_scheduled_date':fields.Datetime.now(),
            'default_pur_tran':self.id,
            'default_purchase_req_id':self.purchase_transfer.id,
            'default_request_type':self.request_type,
            'default_location_dest_id': self.address_to.id,
            'default_show_operations': True,
            }
        stock_action = self.env.ref('purchase_enhanced.action_picking_tree_internal')
        action = stock_action.read()[0]
        action['context'] = context
        action['views'] = [(self.env.ref('purchase_enhanced.view_view_picking_form_internal').id, 'form')]
        return action   



    def action_open_transfer(self):
        for rec in self:
            generated_picking = []
            operation = False
            if rec.state == 'cancel':
                raise UserError(_("Sorry , This Request is already has been canceled"))
            if all(line.given == 0.0 for line in rec.purchase_line):
                raise UserError(_("Enter Total Given Quantity For  Lines Has On-Hand"))
            if any((line.given > line.onhand and line.product_id.type == 'product') or (line.given > line.qty_net_received and line.product_id.type != 'product')  for line in rec.purchase_line):
                raise UserError(_("Total Given Quantity For Lines Must Be Less Than Available Qty"))
            if any(line.given > line.ord_qty  for line in rec.purchase_line):
                raise UserError(_("Total Given Quantity For Lines Must Be Less Than Requested Qty"))
            operation_type = self._context.get('rec_type',False)   
            if operation_type == 'deliver':         
                operation = rec.purchase_line.filtered(lambda s: s.given > 0 and s.iss_qty < s.ord_qty and s.trans_picking_type_id and s.trans_picking_type_id.code == 'outgoing' and (s.iss_qty+s.given) <= s.ord_qty and  s.state in ['open','approve']).mapped('trans_picking_type_id')
            elif operation_type == 'internal':         
                operation = rec.purchase_line.filtered(lambda s: s.given > 0 and s.iss_qty < s.ord_qty and s.trans_picking_type_id and s.trans_picking_type_id.code == 'internal' and (s.iss_qty+s.given) <= s.ord_qty and  s.state in ['open','approve']).mapped('trans_picking_type_id')
            if not operation:
                raise UserError(_("Sorry,No Lines Can be Proceed ,Check All Lines Operation,Status,Given Qty And Iss Qty"))
            for oper in operation:
                stock_picking = self.env['stock.picking'].sudo().search([('pur_tran','=',rec.id),
                          ('picking_type_id','=',oper.id),('state','not in',['cancel','done'])])
                if stock_picking:
                    raise UserError(_("Sorry,You Have Picking By This Operation Please Proceed It First"))
                generated_picking += self.create_delivery_picking(oper)
            #if generated_picking:
            #    generated_picking.button_validate()

            if not generated_picking:
                raise UserError(_("Sorry,Can't generate picking for this order"))
            if generated_picking :   
                rec.purchase_line.write({'given':0,'trans_picking_type_id':False})
                if all(picking.state == 'done' for picking in generated_picking): 
                    rec.purchase_transfer.set_to_done()  
                    if not all(line.state == 'done'  for line in rec.purchase_line):  
                        if not any(line.state == 'open' and line.purchase_req_line_id.purchase_rec_line_ids and line.qty_received == 0  for line in rec.purchase_line):  
                            action = self.env.ref('purchase_enhanced.close_stock_transfer_action').read()[0]
                            action['context'] = {'default_purchase_transfer_id': rec.id}    
                            return action 

            else:
                raise UserError(_("Picking Generated But We Can't Set all it to Done Please Proceed"))       
        return True

class PurchaseRequestReceived(models.Model):
    _inherit = 'purchase.req.rec'

    user_warehouse_id = fields.Many2one('stock.warehouse',string='Created User warehouse',default=lambda self: self.env.user.stock_warehouse_id)



class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.req.line'

    def _get_category_domain(self):
        category_ids = self.env['product.category'].search([('not_use_in_pr','=',False),('product_ids','!=',False)])
        return [('id','in',category_ids.ids)]

    onhand = fields.Float("On Hand",compute='_compute_qty_on_hand',store=True,compute_sudo=True)
    user_warehouse_id = fields.Many2one('stock.warehouse',string='Current User warehouse',default=lambda self: self.env.user.stock_warehouse_id)
    product_categ = fields.Many2one('product.category', string='Product Category', required=True,domain=_get_category_domain,index=True)
    part_number = fields.Char('Part Number',related='product_id.part_number',store=True)
    # Cron Job to update order line Onhand
    @api.model
    def update_order_onhand(self):
        ''' This method is called from a cron job. '''
        for rec in self.search([]):
            if rec.product_id and rec.user_warehouse_id.view_location_id:
                #rec.onhand = rec.product_id.qty_available
                stock = self.env['stock.quant'].sudo().search([('product_id','=',rec.product_id.id),('location_id.usage','=','internal'),
                ('location_id','child_of',rec.user_warehouse_id.view_location_id.id),('location_id.company_id','=',rec.user_warehouse_id.view_location_id.company_id.id)])
                rec.onhand = sum(stock.mapped('quantity'))
            
    @api.depends('user_warehouse_id','product_id','product_id.qty_available','state')
    def _compute_qty_on_hand(self):
        for rec in self:
            if rec.product_id and rec.user_warehouse_id.view_location_id:
                if rec.state in ['tsub','tapprove']:
                    #rec.onhand = rec.product_id.qty_available
                    stock = self.env['stock.quant'].sudo().search([('product_id','=',rec.product_id.id),('location_id.usage','=','internal'),
                    ('location_id','child_of',rec.user_warehouse_id.view_location_id.id),('location_id.company_id','=',rec.user_warehouse_id.view_location_id.company_id.id)])
                    rec.onhand = sum(stock.mapped('quantity'))
                else:
                    rec.onhand = rec.onhand_on_approve

    @api.onchange('product_categ')
    def _onchange_product_categ(self):
        domain = []
        vals = {}
        if self.product_categ:
            domain += [('categ_id','=',self.product_categ.id)]
        if self.preq.request_type == 'branch':
            domain += [('is_for_branch','=',True)]
        if self.product_id and self.product_categ:
            if self.product_id.categ_id != self.product_categ:
                vals['product_id'] = False
        return {'domain':{'product_id':domain},'value':vals }

class PurchaseTransferLine(models.Model):
    _inherit = 'purchase.transfer.line'  

    onhand = fields.Float("Onhand",compute='_compute_qty_on_hand',store=True,compute_sudo=True)  
    user_warehouse_id = fields.Many2one('stock.warehouse',string='Current User warehouse',default=lambda self: self.env.user.stock_warehouse_id)
    allow_picking_type_id = fields.Many2many('stock.picking.type',compute='_compute_allow_picking',store=True,compute_sudo=True)
    trans_picking_type_id = fields.Many2one('stock.picking.type')
    part_number = fields.Char('Part Number',related='product_id.part_number',store=True)


    @api.depends('user_warehouse_id','product_id.qty_available','deliver_to')
    def _compute_allow_picking(self):
        for rec in self:
            if rec.request_type != 'stock':
                if rec.product_id and rec.user_warehouse_id:
                    if rec.product_id.type == 'product':
                        location_ids = self.env['stock.quant'].sudo().search([('product_id','=',rec.product_id.id),('location_id.usage','=','internal'),
                                ('location_id','child_of',rec.user_warehouse_id.view_location_id.id),('location_id.company_id','=',self.env.context.get('company_id') or self.env.user.company_id.id)]).mapped('location_id')
                        if location_ids:
                            if rec.request_type == 'workshop':
                                rec.allow_picking_type_id = rec.trans_picking_type_id.search([('default_location_src_id','in',location_ids.ids),('code','=','outgoing'),('not_in_pr','!=',True)])
                            elif rec.request_type == 'branch':
                                rec.allow_picking_type_id = rec.trans_picking_type_id.search([('default_location_src_id','in',location_ids.ids),('code','!=','incoming'),('not_in_pr','!=',True)])
                            elif rec.request_type == 'manufacture':
                                rec.allow_picking_type_id = rec.trans_picking_type_id.search([('default_location_src_id','in',location_ids.ids),('code','!=','incoming'),('not_in_pr','!=',True)])
                    else:
                        if rec.request_type == 'workshop':
                            rec.allow_picking_type_id = rec.trans_picking_type_id.search([('default_location_src_id','=',rec.deliver_to.default_location_dest_id.id),('code','=','outgoing'),('not_in_pr','!=',True)])
                        elif rec.request_type == 'branch':
                            rec.allow_picking_type_id = rec.trans_picking_type_id.search([('default_location_src_id','=',rec.deliver_to.default_location_dest_id.id),('code','!=','incoming'),('not_in_pr','!=',True)])
                        elif rec.request_type == 'manufacture':
                            rec.allow_picking_type_id = rec.trans_picking_type_id.search([('default_location_src_id','=',rec.deliver_to.default_location_dest_id.id),('code','!=','incoming'),('not_in_pr','!=',True)])

    @api.model
    def update_order_onhand(self):
        ''' This method is called from a cron job. '''
        for rec in self.search([]):
            if rec.product_id and rec.user_warehouse_id.view_location_id:
                #rec.onhand = rec.product_id.qty_available
                stock = self.env['stock.quant'].sudo().search([('product_id','=',rec.product_id.id),('location_id.usage','=','internal'),
                ('location_id','child_of',rec.user_warehouse_id.view_location_id.id),('location_id.company_id','=',rec.user_warehouse_id.view_location_id.company_id.id)])
                rec.onhand = sum(stock.mapped('quantity'))
    
    @api.onchange('allow_picking_type_id')
    def _onchange_trans_picking_type_id(self):
        return {'domain':{'trans_picking_type_id':[('id','in',self.allow_picking_type_id.ids)]}}

        
    @api.depends('user_warehouse_id','trans_picking_type_id','product_id.qty_available','state','searched_loc_id','product_id.stock_move_ids')
    def _compute_qty_on_hand(self):
        move_line_obj = self.env['stock.move.line']
        for rec in self:
            if rec.product_id and rec.user_warehouse_id.view_location_id:
                if rec.product_type =='consu' and rec.searched_loc_id: 
                    in_qty = out_qty = 0
                    in_qty = sum(move_line_obj.search([('location_dest_id','child_of',rec.searched_loc_id.id),('product_id','=',rec.product_id.id)]).mapped('qty_done'))
                    out_qty = sum(move_line_obj.search([('location_id','child_of',rec.searched_loc_id.id),('product_id','=',rec.product_id.id)]).mapped('qty_done')) 
                    rec.onhand = in_qty-out_qty
                else:
                    #rec.onhand = rec.product_id.qty_available
                    if not rec.trans_picking_type_id:
                        stock = self.env['stock.quant'].sudo().search([('product_id','=',rec.product_id.id),('location_id.usage','=','internal'),
                        ('location_id','child_of',rec.user_warehouse_id.view_location_id.id),('location_id.company_id','=',rec.user_warehouse_id.view_location_id.company_id.id)])
                    else:
                        stock = self.env['stock.quant'].sudo().search([('product_id','=',rec.product_id.id),('location_id.usage','=','internal'),
                        ('location_id','=',rec.trans_picking_type_id.default_location_src_id.id)])
                       
                    rec.onhand = sum(stock.mapped('quantity'))
    
    def _compute_qty_on_hand_by_location(self,location_id):
        stock = self.env['stock.quant'].sudo().search([('product_id','=',self.product_id.id),('location_id.usage','=','internal'),
                    ('location_id','child_of',location_id.id),('location_id.company_id','=',location_id.company_id.id)])
        return sum(stock.mapped('quantity'))                

class PurchaseRequisitionLineRec(models.Model):
    _inherit = 'purchase.req.rec.line'

    onhand = fields.Float("On Hand",compute='_compute_qty_on_hand',store=True,compute_sudo=True)
    user_warehouse_id = fields.Many2one('stock.warehouse',string='Current User warehouse',default=lambda self: self.env.user.stock_warehouse_id)
    part_number = fields.Char('Part Number',related='product_id.part_number',store=True)
    
    # Cron Job to update order line Onhand
    @api.model
    def update_order_onhand(self):
        ''' This method is called from a cron job. '''
        for rec in self.search([]):
            if rec.product_id and rec.user_warehouse_id.view_location_id:
                #rec.onhand = rec.product_id.qty_available
                stock = self.env['stock.quant'].sudo().search([('product_id','=',rec.product_id.id),('location_id.usage','=','internal'),
                ('location_id.company_id','=',rec.user_warehouse_id.view_location_id.company_id.id)])
                rec.onhand = sum(stock.mapped('quantity'))
                
    @api.depends('product_id.qty_available','state')
    def _compute_qty_on_hand(self):
        for rec in self:
            if rec.product_id:
                #rec.onhand = rec.product_id.qty_available
                stock = self.env['stock.quant'].sudo().search([('product_id','=',rec.product_id.id),('location_id.usage','=','internal'),
                ('location_id.company_id','=',rec.user_warehouse_id.view_location_id.company_id.id)])
                rec.onhand = sum(stock.mapped('quantity'))
                
             

    # @api.multi
    def write(self, line_values):     
        res = super(PurchaseRequisitionLineRec, self).write(line_values)
        if line_values.get('deliver_to', False):
            for rec in self:
                rec.purchase_req_line_id.write({'deliver_to':rec.deliver_to.id})
                rec.purchase_transfer_line.write({'deliver_to':rec.deliver_to.id})
                if not rec.purchase_transfer_line.trans_picking_type_id and rec.product_id.type != 'product':
                    rec.purchase_transfer_line.write({'trans_picking_type_id': rec.deliver_to.search([('default_location_src_id','=',rec.deliver_to.default_location_dest_id.id)],limit=1).id}),
        return res



