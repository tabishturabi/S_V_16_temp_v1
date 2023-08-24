# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        res = super(IrHttp, self).session_info()
        # res['branch-id'] = user.user_branch_id.id if request.session.uid and user.company_id.id == user.user_branch_id.company_id.id else None
        # res['user_banch'] = {'current_branch': (user.user_branch_id.id, user.user_branch_id.branch_ar_name), 'allowed_branch': [(branch.id, branch.branch_ar_name) for branch in user.user_branch_ids if branch.company_id.id == user.company_id.id]},
        return res
