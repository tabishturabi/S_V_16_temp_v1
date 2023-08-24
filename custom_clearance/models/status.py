# -*- coding: utf-8 -*-

from odoo import fields,models,api,_

class ImportStatus(models.Model):
    _name = 'import.status'
    _description = 'Import Status'
    
    
    name = fields.Char('Status Name')