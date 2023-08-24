# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_accouting_manage_by_child = fields.Boolean(string="Allowed  Accounting managed By child")

    #override to full fill need as need by m.khaleed
    def _find_accounting_partner(self, partner):
        ''' Find the partner for which the accounting entries will be created '''
        if partner.is_accouting_manage_by_child:
            return partner
        else:
            return partner.commercial_partner_id
