# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class ResCompany(models.Model):
    _inherit = 'res.company'

    portal_create_individual_order = fields.Boolean()
    portal_create_cooreperate_orders = fields.Boolean()
    portal_service_ids = fields.Many2many('product.template','portal_service_company_rel','company_id','service_id')
    online_journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))])

class CargoSalePortalConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    portal_create_individual_order = fields.Boolean(readonly=False,related='company_id.portal_create_individual_order',store=True)
    portal_create_cooreperate_orders = fields.Boolean(readonly=False,related='company_id.portal_create_cooreperate_orders',store=True)
    portal_service_ids = fields.Many2many('product.template','portal_service_config_rel','config_id','service_id',related='company_id.portal_service_ids',store=True,readonly=False)
    online_journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))],related='company_id.online_journal_id',store=True,readonly=False)
