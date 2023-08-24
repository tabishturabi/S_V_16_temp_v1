# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigTax(models.Model):
    _name = 'res.config.tax'
    _description = "Res Config Tax "

    tax_ids = fields.Many2many('account.tax', 'account_tax_data', 'account_id', 'tax_id',
                               string="Tax")  # , config_parameter='bsg_cargo_sale.tax_ids'


class CargoSaleConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    satah_account_id = fields.Many2one('account.account', string="Satah Account",readonly=False,related="company_id.satah_account_id")
    inv_line_account_id = fields.Many2one('account.account', string="Default Invoice Line Account",readonly=False,related="company_id.inv_line_account_id")
    tax_ids = fields.Many2many('account.tax', 'account_tax_conf', 'account_id', 'tax_id',
                               string="Tax",related="company_id.tax_ids",readonly=False)  # , config_parameter='bsg_cargo_sale.tax_ids'
    cargo_service_id = fields.Many2one('product.template', string="Cargo Service",readonly=False,related="company_id.cargo_service_id")
    international_cargo_service_id = fields.Many2one('product.template', string="Cargo Service",readonly=False,related="company_id.international_cargo_service_id")

