from odoo import models, fields
class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    is_home_pickup = fields.Boolean(string="Is Home Pickup")
    is_home_delivery = fields.Boolean(string="Is Home Delivery")
    is_small_box = fields.Boolean(string="Is Small Box")
    is_medium_box = fields.Boolean(string="Is Medium Box")
    is_large_box = fields.Boolean(string="Is Large Box")