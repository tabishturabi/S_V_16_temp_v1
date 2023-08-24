from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError,Warning
from datetime import datetime

class BsgVehicleCargoSaleInherit(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale'


    is_credit_customer = fields.Boolean(related="partner_types.is_credit_customer",string='is credit customer')
    is_customer_contract = fields.Boolean(string="is customer contract?",compute="_is_customer_contract")

    @api.depends('customer_contract')
    def _is_customer_contract(self):
        for rec in self:
            if rec.customer_contract:
                rec.is_customer_contract = True
            else:
                rec.is_customer_contract = False
    @api.onchange('partner_types','payment_method')
    def onchange_partner_payment(self):
        if self.partner_types.is_credit_customer == True and self.payment_method.payment_type in ['cash','pod']:
            self.is_to_other_customer = True
        else:
            self.is_to_other_customer = False
