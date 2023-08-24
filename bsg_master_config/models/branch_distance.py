# -*- coding: utf-8 -*-

from odoo import fields,models,api,_
from odoo.exceptions import ValidationError,UserError

class BranchDistance(models.Model):
    _name = 'branch.distance'
    _inherit = ['mail.thread']
    _description = 'Branch To Branch Distance'
    _rec_name = 'name'
    
    name = fields.Char(string='Name',compute='_get_name')
    branch_from = fields.Many2one(comodel_name='bsg_route_waypoints',string='Branch From', tracking=True)
    branch_to = fields.Many2one(comodel_name='bsg_route_waypoints',string='Branch To', tracking=True)
    distance = fields.Float(string='Distance', tracking=True)
    active = fields.Boolean(string='Active', tracking=True, default=True)
    
    
    @api.constrains('distance')
    def _distance_constrains(self):
        if self.distance <= 0:
            raise ValidationError(_("Distance Should be greater Than 0"))
        
    
    @api.constrains('branch_from','branch_to')
    def _branch_constrains(self):
        if self.branch_from and self.branch_to:
            rec_id = self.env['branch.distance'].search([('branch_from','=',self.branch_from.id),('branch_to','=',self.branch_to.id),('id','!=',self.id)])
            if rec_id:
                raise UserError(_("That Value Already Taken By another User(Branch From,Branch To)"))
            
    @api.onchange('branch_from')
    def _oncahnge_branch_from(self):
        if self.branch_from:
            domain = [('id', '!=', self.branch_from.id)]
            return {'domain': {'branch_to': domain}}

    @api.onchange('branch_to')
    def _oncahnge_branch_to(self):
        if self.branch_to:
            domain = [('id', '!=', self.branch_to.id)]
            return {'domain': {'branch_from': domain}}
    
    
    @api.depends('branch_from','branch_from')
    def _get_name(self):
        if self.branch_from and self.branch_to:
            self.name = str(self.branch_from.route_waypoint_name) +" to "+ str(self.branch_to.route_waypoint_name)