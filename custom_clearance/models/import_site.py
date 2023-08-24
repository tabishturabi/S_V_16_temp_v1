# -*- coding: utf-8 -*-

from odoo import fields,models,api,_

class ImportSite(models.Model):
    _name= 'import.site'
    _description = 'Import Custom Site'
    
    site_id = fields.Many2one('export.custom',string='Site Line')
    city = fields.Char('City')
    name= fields.Char('Site Name')
    address = fields.Char('Address')
    contact = fields.Char('Contact No')    
