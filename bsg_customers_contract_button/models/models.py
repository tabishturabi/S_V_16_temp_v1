# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class CustomersConfig(models.Model):
    _inherit = 'res.partner'
    _description = 'Customer form Configuration'

    customer_contracts_number = fields.Integer(string='Contracts',compute='compute_contracts_number')

    def action_contracts(self):
        return {
            'name': 'Customers Contracts',
            'domain': [('cont_customer.name', '=', self.name)],
            'res_model': 'bsg_customer_contract',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }
    # @api.multi
    def compute_contracts_number(self):
        count = self.env['bsg_customer_contract'].search_count([('cont_customer.name', '=', self.name)])
        self.customer_contracts_number = count



