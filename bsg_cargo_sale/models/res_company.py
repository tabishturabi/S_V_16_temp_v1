# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompanyExt(models.Model):
    _inherit = 'res.company'

    tax_ids = fields.Many2many('account.tax', string="Tax")
    satah_account_id = fields.Many2one('account.account', string="Satah Account")
    inv_line_account_id = fields.Many2one('account.account', string="Default Invoice Line Account")
    cargo_service_id = fields.Many2one('product.template', string="Cargo Service")
    international_cargo_service_id = fields.Many2one('product.template', string="Cargo Service")
