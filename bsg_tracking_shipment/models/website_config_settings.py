# Copyright 2019 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    recaptcha_key_site = fields.Char(
        readonly=False,config_parameter='bsg_tracking_shipment.default_recaptcha_key_site'
    )
    recaptcha_key_secret = fields.Char(
        readonly=False,config_parameter='bsg_tracking_shipment.default_recaptcha_key_secret'
    )
    has_google_recaptcha = fields.Boolean(
        'Google reCaptcha',
        readonly=False,config_parameter='bsg_tracking_shipment.default_has_google_recaptcha'
    )


class NationalDayCustomer(models.Model):
    _name = 'national.day.customer'

    name = fields.Char('Customer Name')
    id_number = fields.Char('ID Card')
    phone = fields.Char('Phone Number')
    email = fields.Char('Email')
    package = fields.Selection([('90_pack', '90-Package'), ('190_pack', '190-Package')], 'Package')

