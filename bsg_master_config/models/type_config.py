# -*- coding: utf-8 -*-

from odoo import fields,api,models

class TypeConfig(models.Model):
    _name = 'type.config'
    _inherit = ['mail.thread']
    _description = 'All About Helpdesk Type Configuration'
    _rec_name='name'
    
    name = fields.Char(string='Name')
    active = fields.Boolean(string="Active", tracking=True, default=True)