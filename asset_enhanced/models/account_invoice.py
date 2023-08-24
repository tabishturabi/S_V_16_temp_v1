# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'


    # @api.one
    def asset_create(self):
        if self.asset_category_id:
            vals = {
                'name': self.name,
                'code': self.invoice_id.number or False,
                'category_id': self.asset_category_id.id,
                'value': self.price_subtotal_signed,
                'partner_id': self.invoice_id.partner_id.id,
                'company_id': self.invoice_id.company_id.id,
                'currency_id': self.invoice_id.company_currency_id.id,
                'date': self.invoice_id.date_invoice,
                'invoice_id': self.invoice_id.id,
                'account_analytic_id': self.account_analytic_id and self.account_analytic_id.id or False,
                'bsg_branches_id': self.branch_id and self.branch_id.id or False,
                'department_id': self.department_id and self.department_id.id or False,
                'fleet_vehicle_id': self.fleet_id and self.fleet_id.id or False,
                'analytic_tag_ids': self.analytic_tag_ids and self.analytic_tag_ids.ids or False,
            }
            if self.asset_category_id.open_asset and self.asset_category_id.date_first_depreciation == 'manual':
                # the asset will auto-confirm, so we need to set its date
                # since in this case the date will be readonly
                vals['first_depreciation_manual_date'] = self.invoice_id.date_invoice
            changed_vals = self.env['account.asset'].onchange_category_id_values_on_create(vals)
            vals.update(changed_vals['value'])
            asset = self.env['account.asset'].create(vals)
            if self.asset_category_id.open_asset:
                asset.validate()
        return True
