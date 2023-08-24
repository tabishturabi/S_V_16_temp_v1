# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    poptd = fields.Integer(string="PO PTD",compute="_get_poytdo")
    poytd_open = fields.Integer(string="PO YTD OPEN",compute="_get_poytdo")
    poytd_close = fields.Integer(string="PO YTD CLOSE",compute="_get_poytdo")
    prptd = fields.Integer(string="PR PTD",compute="_get_prytdc")
    prytd_open = fields.Integer(string="PR YTD OPEN",compute="_get_prytdc")
    prytd_close = fields.Integer(string="PR YTD CLOSE",compute="_get_prytdc")
    
    ############PO.Report#######################################
     
    @api.depends('product_id')
    def _get_poytdo(self):
        total_open = self.env['warehouse.po.year.open.report'].with_context({'product_id':self.product_id}).get_total_count()
        total_close = self.env['warehouse.po.year.close.report'].with_context({'product_id':self.product_id}).get_total_count()
        total_period = self.env['warehouse.po.period.report'].with_context({'product_id':self.product_id}).get_total_count()
        self.poytd_open = total_open
        self.poytd_close = total_close
        self.poptd = total_period


    
    def action_view_poytdo_open(self):
        if not self.product_id or not self.order_id:
            raise UserError(_("You Must Save Order First"))    
        self.env['warehouse.po.year.open.report'].with_context({'product_id':self.product_id}).set_mode_values()     
        return {
                'name': _('Purchase Order Open'),
                # 'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'warehouse.po.year.open.report',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('quantity', '!=', 0)],
                'target': 'new',
                'context' : {'create': False},
                }

    
    def action_view_poytdo_close(self):
        if not self.product_id or not self.order_id:
            raise UserError(_("You Must Save Order First"))           
        self.env['warehouse.po.year.close.report'].with_context({'product_id':self.product_id}).set_mode_values()     
        return {
                'name': _('Purchase Order Close'),
                # 'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'warehouse.po.year.close.report',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('quantity', '!=', 0)],
                'target': 'new',
                'context' : {'create': False},
                }

    
    def action_view_poytdo_period(self):
        if not self.product_id or not self.order_id:
            raise UserError(_("You Must Save Order First"))            
        self.env['warehouse.po.period.report'].with_context({'product_id':self.product_id}).set_mode_values()     
        return {
                'name': _('Purchase Order Period'),
                # 'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'warehouse.po.period.report',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('quantity', '!=', 0)],
                'target': 'new',
                'context' : {'create': False},
                }            

    
    def action_view_onhand(self):  
        if not self.product_id or not self.order_id:
            raise UserError(_("You Must Save Order First"))    
        self.env['warehouse.on.hand.report'].with_context({'product_id':self.product_id}).set_mode_values()
        return {
                'name': _('ON-HAND Quantity'),
                # 'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'warehouse.on.hand.report',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('quantity', '!=', 0)],
                'target': 'new',
                'context' : {'create': False},
                }            


    ####################PR.Report#######################################
     
    @api.depends('product_id')
    def _get_prytdc(self):
        total_open = self.env['warehouse.pr.year.open.report'].with_context({'product_id':self.product_id}).get_total_count()
        total_close = self.env['warehouse.pr.year.close.report'].with_context({'product_id':self.product_id}).get_total_count()
        total_period = self.env['warehouse.pr.period.report'].with_context({'product_id':self.product_id}).get_total_count()
        self.prytd_open = total_open
        self.prytd_close = total_close
        self.prptd = total_period

    
    def action_view_prytdo_open(self):
        if not self.product_id or not self.order_id:
            raise UserError(_("You Must Save Order First"))            
        self.env['warehouse.pr.year.open.report'].with_context({'product_id':self.product_id}).set_mode_values()     
        return {
                'name': _('Purchase Request Open'),
                # 'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'warehouse.pr.year.open.report',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('quantity', '!=', 0)],
                'target': 'new',
                'context' : {'create': False},
                }

    
    def action_view_prytdo_close(self):
        if not self.product_id or not self.order_id:
            raise UserError(_("You Must Save Order First"))            
        self.env['warehouse.pr.year.close.report'].with_context({'product_id':self.product_id}).set_mode_values()     
        return {
                'name': _('Purchase Request Close'),
                # 'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'warehouse.pr.year.close.report',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('quantity', '!=', 0)],
                'target': 'new',
                'context' : {'create': False},
                }

    
    def action_view_prytdo_period(self):
        if not self.product_id or not self.order_id:
            raise UserError(_("You Must Save Order First"))            
        self.env['warehouse.pr.period.report'].with_context({'product_id':self.product_id}).set_mode_values()     
        return {
                'name': _('Purchase Request Period'),
                # 'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'warehouse.pr.period.report',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('quantity', '!=', 0)],
                'target': 'new',
                'context' : {'create': False},
                }      