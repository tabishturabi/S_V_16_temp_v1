# -*- coding: utf-8 -*-

from odoo import fields,models,api,_

class FreightForward(models.Model):
    _name= 'freight.forward'
    _description = 'Custom Freight Forward'
    _rec_name = 'name'
    
    name = fields.Char('Name')
    state = fields.Selection([('draft','Draft'),('done','Done')],string='State',default='draft')
    s_no = fields.Selection([('import','Import'),('export','Export')],string='SR No Type')
    s_supplier = fields.Many2one('res.partner',string='Shipping Line') 
    customer = fields.Many2one('res.partner', string='Customer')
    eta = fields.Date('ETA')
    etd = fields.Date('ETD')
    customer_site = fields.Many2one('bsg_route_waypoints',string='Site')
    book_date = fields.Date('Booking Date') 
    form = fields.Many2one('bsg_route_waypoints',string='Country of Origin')
    to = fields.Many2one('bsg_route_waypoints',string='Destination')
    cro = fields.Integer('CRO')
    cro_date = fields.Date('CRO Date')
    # acct_link = fields.Many2one('account.move', string='Invoice')
    
    freight = fields.Boolean('Freight Forwarding')
    store = fields.Boolean('Storage')
    trans = fields.Boolean('Transportation')
    custm = fields.Boolean('Custom Clearance')
    
    status_name = fields.Many2one('import.status',string='Status')
    
    freight_line = fields.One2many('freight.tree','freight_id',string='Freight Line')
    
    @api.model
    def create(self,vals):
        res = super(FreightForward, self).create(vals)
        res.name = 'SBX'+ str(res.customer_site.branch_no) + self.env['ir.sequence'].next_by_code('freight.forward') or _('New')
        return res
    
    # @api.multi
    def action_create_transport(self):
        for rec in self:
            rec.state = 'done'

    
    
class FreightTree(models.Model):
    _name = 'freight.tree'
    _description = 'Import Freight Tree'
    
    freight_id = fields.Many2one('freight.forward',string='Fright id')
    cont_no = fields.Char('Container No')
    cont_size = fields.Selection([('20ft','20ft'),('40ft','40ft')],string='Container Size')
    store_charge = fields.Float('Storage Charges')
    freight_chrg  = fields.Float('Freight Charges')
    stor_supp = fields.Many2one('res.partner',string='Storage Supplier')
    
class FreightStatus(models.Model):
    _name = 'freight.status'
    _description = 'Freight Forward Status'
    
    name = fields.Char('Status Name')