# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class ClaimsAccountConfig(models.Model):
    _name = 'claims_account_config'

    name = fields.Char("Name")
    claim_account_id = fields.Many2one('account.account', string='Claim Account')
    cars_account_id = fields.Many2one('account.account', string='Cars Account')
    claim_product_id = fields.Many2one('product.template', string='Product')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    journal_id = fields.Many2one('account.journal', string='Journal')
    driver_mistake_account_id = fields.Many2one('account.account', string='Driver Mistake Account')
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Claims Account Config")
    vendor_tax_id = fields.Many2one('account.tax',string="Vendor Taxes")
    customer_tax_id = fields.Many2one('account.tax',string="Customer Taxes")
