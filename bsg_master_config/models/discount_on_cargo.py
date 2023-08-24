# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DiscountOnCargo(models.Model):
    _name = 'discount.cargo'
    _inherit = ['mail.thread']
    _description = "Discount On Cargo"

    name = fields.Char(string="Name", required=True)
    discount = fields.Float(string="Discount %",default=0.0)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id)
