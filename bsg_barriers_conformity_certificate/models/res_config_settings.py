# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api

from ast import literal_eval

class BccConfigSettings(models.Model):
    _name = 'saso_settings'

    manufacturer = fields.Char(string='Manufacturer')
    manufacturer_code = fields.Char(string='Manufactuere Code')
    bcc_journal_ids = fields.Many2many('account.journal','saso_settings_account_joural_rel','setting_id','journal_id',string="Payment Journals")

    # @api.multi
    def execute_settings(self):
        self.ensure_one()
        saso_config = self.env.ref('bsg_barriers_conformity_certificate.saso_settings_data', False)
        if saso_config:
            saso_config.sudo().write({
                                       'manufacturer': self.manufacturer,
                                       'manufacturer_code': self.manufacturer_code,
                                       'bcc_journal_ids': [(6, 0, self.bcc_journal_ids.ids)],
                                       })

        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def default_get(self, fields):
        res = super(BccConfigSettings, self).default_get(fields)
        saso_config = self.env.ref('bsg_barriers_conformity_certificate.saso_settings_data', False)
        if saso_config:
            res.update({
                'manufacturer': saso_config.sudo().manufacturer,
                'manufacturer_code': saso_config.sudo().manufacturer_code,
                'bcc_journal_ids': [(6, 0, saso_config.sudo().bcc_journal_ids.ids)],
            })
        return res


