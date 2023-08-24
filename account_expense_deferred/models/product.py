# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


# Migration Note
# account.asset.category does not exist in base
# class ProductTemplate(models.Model):
#     _inherit = 'product.template'
#
#     deferred_expense_category_id = fields.Many2one('account.asset.category', string='Deferred Exoene Type', company_dependent=True, ondelete="restrict")
#
#     # @api.multi
#     def _get_asset_accounts(self):
#         res = super(ProductTemplate, self)._get_asset_accounts()
#         if self.asset_category_id or self.deferred_expense_category_id:
#             res['stock_input'] = self.property_account_expense_id
#         if self.deferred_revenue_category_id:
#             res['stock_output'] = self.property_account_income_id
#         return res
