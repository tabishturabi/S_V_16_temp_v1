# -*- coding: utf-8 -*-
from dateutil import relativedelta as re
from datetime import datetime, timedelta

from odoo import models, fields, api, tools,exceptions, _, SUPERUSER_ID


class InheritHrContract(models.Model):
    _inherit = 'hr.contract'

    is_not_required_attendance = fields.Boolean(default=False, string='Is Not Required Attendance')
    type_attendance = fields.Selection([('bywork', 'By Working Time'), ('byrota', 'Other')],
                                       string='Working Schedule By',default='bywork')
    bywork = fields.Boolean(defualt=False, compute='byworkvisible')


    @api.depends('is_not_required_attendance', 'type_attendance')
    def byworkvisible(self):
        if not self.is_not_required_attendance and self.type_attendance == 'bywork':
            self.bywork = True
        else:
            self.bywork = False




