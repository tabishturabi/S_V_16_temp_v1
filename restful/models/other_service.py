from odoo import models, fields

class BsgBranch(models.Model):
    _inherit = 'bsg_branches.bsg_branches'
    
    contact_numbers = fields.Char('Contact Phones')

class OtherServiceItems(models.Model):
    _inherit = 'other_service_items'
    
    home_location = fields.Char('Home Location')
    pickup_location = fields.Char('Pickup Location')
