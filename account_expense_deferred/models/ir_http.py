# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super(Http, self).session_info()
        user = request.env.user
        res.update({
            'group_deferred_exp_type_archive': user and user.has_group(
                'account_expense_deferred.group_def_expense_type_archive'),
            'group_deferred_exp_archive': user and user.has_group(
                'account_expense_deferred.group_def_expense_archive'),
        })
        return res
