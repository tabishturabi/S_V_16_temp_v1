# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'


    # @api.multi
    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if vals.get('company_id'):
            branch_list = []
            if self.user_branch_ids:
                for branch in self.user_branch_ids:
                    if branch.company_id.id == vals.get('company_id'):
                        branch_list.append(branch.id)
                        break
            self.env.user.update({'user_branch_id': branch_list[0] if branch_list else False})
            self.env['ir.rule'].clear_cache()
        if vals.get('branch-id'):
            self.env.user.update({'user_branch_id': vals.get('branch-id')})
            self.env['ir.rule'].clear_cache()
        return res
