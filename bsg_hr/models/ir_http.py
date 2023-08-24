# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super(Http, self).session_info()
        user = request.env.user
        res.update({
            'group_employee_archive': user and user.has_group(
                'bsg_hr.group_archive_employee'),

        })
        return res
