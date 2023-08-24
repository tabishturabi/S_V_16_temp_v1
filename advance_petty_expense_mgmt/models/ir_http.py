# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super(Http, self).session_info()
        user = request.env.user
        res.update({
            'petty_cash_auditor': user and user.has_group(
                'advance_petty_expense_mgmt.petty_cash_internal_editor'),
        })
        return res
