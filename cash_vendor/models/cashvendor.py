from odoo import api, fields, models, _


class Employees(models.Model):
    _inherit = "hr.employee"
    
    pur_rep = fields.Boolean('Purchase Representative')
    

class VendorTypes(models.Model):
    _name = "vendor.types"
    _description = "Vendor Type"

    name = fields.Char('Name')
#     code = fields.Char('code')


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    vt = fields.Selection([('char','Cash'),('credit','Credit')],string="Vendor Types")#fields.Many2one("vendor.types", string='Vendor Types')
    emp = fields.Many2one("hr.employee" , string='Purchase Representative')
    

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    partner_idid = fields.Integer() #should be invisible
    emp = fields.Many2one("hr.employee" , string='Employee')
    vendor_type = fields.Selection(related="partner_id.vt",store=True)#fields.Many2one("vendor.types", string='Vendor Types')

    #@api.multi
    @api.onchange('partner_id')
    def getemp(self):
        if(self.partner_id):
            self.emp = self.partner_id.emp
            pass
        