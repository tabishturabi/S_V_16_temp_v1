# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', 'like', name), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        if not self._context.get('show_parent_account'):
            domain += [('user_type_id.name','!=','View')]
        account_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(account_ids).name_get()

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    branch_id = fields.Many2one('bsg_branches.bsg_branches',string="Branch")