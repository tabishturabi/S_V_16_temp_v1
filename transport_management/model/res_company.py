# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    fuel_analytic_account_id = fields.Many2one('account.analytic.account', string='Fuel Analytic Account')
    invoice_analytic_account_id = fields.Many2one('account.analytic.account', string='Invoice Analytic Account')
    reward_for_analytic_account_id = fields.Many2one('account.analytic.account',
                                                     string='Reward For Load Analytic Account')
    cash_rounding_id = fields.Many2one('account.cash.rounding', string='Cash Rounding Method')
    bx_customer_journal_id = fields.Many2one('account.journal', domain="[('type','=','sale')]",
                                             string='Default Bx Customer Invoice Journal')
    bx_vendor_journal_id = fields.Many2one('account.journal', domain="[('type','=','purchase')]",
                                           string='Default Bx Vendor Invoice Journal')

    fuel_product_id = fields.Many2one('product.product', string='Default Fuel Product')
    fuel_analytic_tag_ids = fields.Many2one('account.account.tag', string='Invoice Analytic Tage')
    fuel_supplier_id = fields.Many2one('res.partner', string='Default Fuel Supplier')
    invoice_analytic_tag_ids = fields.Many2one('account.account.tag', string='Invoice Analytic Tage')
    reward_for_load_id = fields.Many2one('product.product', string='Default Reward For Load')
    reward_for_analytic_tag_ids = fields.Many2one('account.account.tag',
                                                  string='Reward For Load Invoice Analytic Tage')
    product_category_ids = fields.Many2many('product.category', string='Default Product Categories')
    vehicle_type_domain_ids = fields.Many2many('vehicle.type.domain', string='Domain Name')
    bsg_car_size_ids = fields.Many2many('bsg_car_size', string='Fleet Size')
