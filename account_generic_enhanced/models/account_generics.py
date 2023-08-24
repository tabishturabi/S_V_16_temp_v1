from odoo import api, fields, models, _

class AccountGeneric(models.Model):
    _inherit = "account.account"
    
    levels = fields.Selection([
            ('l1','Level 1'),
            ('l2','Level 2'),
            ('l3','Level 3'),
            ('l4','Level 4'),
            ('l5','Level 5'),
            ('l6','Level 6'),
            ('l7','Level 7'),
            ('l8','Level 8'),
            ('l9','Level 9'),
            ('l10','Level 10'),
            
        ],string="Level")