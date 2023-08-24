# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from lxml import etree

from odoo import api, fields, models, _
# from odoo.osv.orm import setup_modifiers


class AssetModify(models.TransientModel):
    _inherit = 'asset.modify'

    method_period_label = fields.Selection([('1', 'Months'), ('12', 'Years')], string='Number of Months in a Period',
                                           default='12', help="The amount of time between two depreciations")
    is_expense = fields.Boolean("Is Deferred Expense")

    @api.model
    def default_get(self, fields):
        res = super(AssetModify, self).default_get(fields)
        asset_id = self.env.context.get('active_id')
        asset = self.env['account.asset.asset'].browse(asset_id)
        print("===============", asset)
        print("===============type: ", asset.type)
        if asset.type == "expense":
            res.update({'is_expense': True})
        return res

    @api.onchange('method_period_label')
    def onchange_method_period_label(self):
        if self.method_period_label:
            self.method_period = int(self.method_period_label)