# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_soa_account = fields.Boolean('Is SOA Account')
    is_allowed_entry = fields.Boolean('Not allowed on Move Entry')


class PartnerType(models.Model):
    _inherit = 'partner.type'

    is_soa_partner = fields.Boolean('Is SOA Partner')
    is_soa_vendor = fields.Boolean('Is SOA Vendor')
    
