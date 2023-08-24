# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SetupBarBankConfigWizardExt(models.TransientModel):
    _inherit = 'account.setup.bank.manual.config'

    name = fields.Char(string="Code")
