# -*- coding: utf-8 -*-

from odoo import fields,api,models

class AppConfig(models.Model):
    _name = 'app.config'
    _inherit = ['mail.thread']
    _description = 'All About Helpdesk App Configuration'
    _rec_name='name'
    
    name = fields.Char(string='Name')
    active = fields.Boolean(string="Active", tracking=True, default=True)