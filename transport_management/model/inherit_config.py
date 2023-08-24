# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class ResTransportConfig(models.Model):
    _name = 'res.transport.config.data'
    _description = "Res Transport Product "

    product_category_ids = fields.Many2many('product.category', string='Default Product Categories')
    vehicle_type_domain_ids = fields.Many2many('vehicle.type.domain', string='Domain Name')
    bsg_car_size_ids = fields.Many2many('bsg_car_size', string='Fleet Size')


class TransportMgmtConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fuel_product_id = fields.Many2one('product.product', string='Default Fuel Product',
                                      config_parameter='transport_management.default_fuel_product_id',readonly=False)
    fuel_analytic_account_id = fields.Many2one('account.analytic.account', string='Fuel Analytic Account',
                                               related="company_id.fuel_analytic_account_id", readonly=False)

    fuel_analytic_tag_ids = fields.Many2one('account.account.tag', string='Invoice Analytic Tage',
                                            related="company_id.fuel_analytic_tag_ids",readonly=False)
    fuel_supplier_id = fields.Many2one('res.partner', string='Default Fuel Supplier',
                                       related="company_id.fuel_supplier_id",readonly=False)

    invoice_analytic_account_id = fields.Many2one('account.analytic.account', string='Invoice Analytic Account',
                                                  related="company_id.invoice_analytic_account_id", readonly=False)
    invoice_analytic_tag_ids = fields.Many2one('account.account.tag', string='Invoice Analytic Tage',
                                               related="company_id.invoice_analytic_tag_ids",readonly=False)

    reward_for_load_id = fields.Many2one('product.product', string='Default Reward For Load',
                                         related="company_id.reward_for_load_id",readonly=False)
    reward_for_analytic_account_id = fields.Many2one('account.analytic.account',
                                                     string='Reward For Load Analytic Account',
                                                     related="company_id.reward_for_analytic_account_id",
                                                     readonly=False)
    reward_for_analytic_tag_ids = fields.Many2one('account.account.tag',
                                                  string='Reward For Load Invoice Analytic Tage',
                                                  related="company_id.reward_for_analytic_tag_ids",readonly=False)

    cash_rounding_id = fields.Many2one('account.cash.rounding', string='Cash Rounding Method',
                                       related="company_id.cash_rounding_id", readonly=False)

    product_category_ids = fields.Many2many('product.category', string='Default Product Categories',
                                            related="company_id.product_category_ids",readonly=False)

    bx_customer_journal_id = fields.Many2one('account.journal', domain="[('type','=','sale')]",
                                             string='Default Bx Customer Invoice Journal',
                                             related='company_id.bx_customer_journal_id',readonly=False)
    bx_vendor_journal_id = fields.Many2one('account.journal', domain="[('type','=','purchase')]",
                                           string='Default Bx Vendor Invoice Journal',
                                           related='company_id.bx_vendor_journal_id',readonly=False)

    vehicle_type_domain_ids = fields.Many2many('vehicle.type.domain', string='Domain Name',
                                               related="company_id.vehicle_type_domain_ids",readonly=False)
    bsg_car_size_ids = fields.Many2many('bsg_car_size', string='Fleet Size', related="company_id.bsg_car_size_ids",readonly=False)

    # @api.model
    # def get_values(self):
    #     res = super(TransportMgmtConfigSettings, self).get_values()
    #     transconfig = self.env.ref('transport_management.res_transport_config_pro', False)
    #     res.update({
    #         'product_category_ids': transconfig.sudo().product_category_ids.ids,
    #         'vehicle_type_domain_ids': transconfig.sudo().vehicle_type_domain_ids.ids,
    #         'bsg_car_size_ids': transconfig.sudo().bsg_car_size_ids.ids})
    #     return res
    #
    # @api.multi
    # def set_values(self):
    #     super(TransportMgmtConfigSettings, self).set_values()
    #     ir_config = self.env['ir.config_parameter']
    #     self.ensure_one()
    #     transconfig = self.env.ref('transport_management.res_transport_config_pro', False)
    #     transconfig.sudo().write({'product_category_ids': [(6, 0, self.product_category_ids.ids)],
    #                               'vehicle_type_domain_ids': [(6, 0, self.vehicle_type_domain_ids.ids)],
    #                               'bsg_car_size_ids': [(6, 0, self.bsg_car_size_ids.ids)]})
    #     return True
