# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero


class LogUsers(models.Model):
    _name = 'users.log'
    _description = 'Users Group Logs'

    #@api.multi
    def name_get(self):
        return [(request.id, "%s - %s " %(str(request.date),  request.effected_user_id.name)) for request in self]

    effected_user_id = fields.Many2one("res.users", string="Effected User", readonly=True)
    add_group_ids = fields.Many2many('res.groups', 'user_log_group_add_rel', string="Added Groups", readonly=True)
    remove_group_ids = fields.Many2many('res.groups', 'user_log_group_del_rel', string="Removed Groups", readonly=True)
    user_id = fields.Many2one("res.users", string="User", readonly=True,  default=lambda self: self.env.user,)
    date = fields.Datetime(default=fields.Datetime.now,  readonly=True, string="Time")

