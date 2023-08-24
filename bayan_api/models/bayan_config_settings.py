# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class BayanConfigSettings(models.Model):
    _name = 'bayan.config.settings'

    bayan_app_id = fields.Char(string="Bayan App ID")
    bayan_app_key = fields.Char(string="Bayan App Key")
    bayan_client_id = fields.Char(string="Bayan Client ID")
    bayan_live_url = fields.Char(string="Bayan Live Url")
    bayan_staging_url = fields.Char(string="Bayan Staging Url")
    is_active = fields.Boolean(string="Is Active")
    is_transport = fields.Boolean(string="Active on transport")

    
    def execute_settings(self):
        self.ensure_one()
        bayan_config_settings = self.env.ref('bayan_api.bayan_config_settings_data', False)
        bayan_config_settings.sudo().write({
            'bayan_app_id': self.bayan_app_id,
            'bayan_app_key': self.bayan_app_key,
            'bayan_client_id': self.bayan_client_id,
            'bayan_live_url': self.bayan_live_url,
            'bayan_staging_url': self.bayan_staging_url,
            'is_active': self.is_active,
            'is_transport': self.is_transport,
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def default_get(self, fields):
        res = super(BayanConfigSettings, self).default_get(fields)
        bayan_config_settings = self.env.ref('bayan_api.bayan_config_settings_data', False)
        if bayan_config_settings:
            res.update({
                'bayan_app_id': bayan_config_settings.sudo().bayan_app_id,
                'bayan_app_key': bayan_config_settings.sudo().bayan_app_key,
                'bayan_client_id': bayan_config_settings.sudo().bayan_client_id,
                'bayan_live_url': bayan_config_settings.sudo().bayan_live_url,
                'bayan_staging_url': bayan_config_settings.sudo().bayan_staging_url,
                'is_active': bayan_config_settings.sudo().is_active,
                'is_transport': bayan_config_settings.sudo().is_transport,

            })
        return res
