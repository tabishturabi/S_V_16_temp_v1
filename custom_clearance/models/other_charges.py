# -*- coding: utf-8 -*-

from odoo import fields,models,api,_

class ChargesDes(models.Model):
    _name= 'charges.des'
    _description = 'Import Charges Des'
    
    name = fields.Char(string='Other Charges Description')