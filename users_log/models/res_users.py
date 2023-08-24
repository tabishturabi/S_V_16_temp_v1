# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero

def is_boolean_group(name):
    return name.startswith('in_group_')

def is_selection_groups(name):
    return name.startswith('sel_groups_')

def get_boolean_group(name):
    return int(name[9:])

def get_selection_groups(name):
    return [int(v) for v in name[11:].split('_')]


class ResUsers(models.Model):
    _inherit = 'res.users'

    def log_group_change(self, vals, effected_user):
        added_ids = []
        removed_ids = []
        for key, value in vals.items():
            if is_boolean_group(key):
               group_id = get_boolean_group(key)
               added_ids.append(group_id) if value else removed_ids.append(group_id)
            if is_selection_groups(key):
                user_groups = effected_user.groups_id.ids
                selection_options = [gid for gid in get_selection_groups(key)]
                previously_sel = [gid for gid in selection_options if gid in user_groups]
                newly_selected = [value] if value else []
                if value:
                    if previously_sel:
                        upgraded = max(previously_sel) < value
                        if upgraded:
                            added_ids+=newly_selected
                        else:
                            removed_ids.append(max(previously_sel))
                            added_ids += newly_selected
                    else:
                        added_ids += newly_selected
                else:
                    # should not be here if there is no new vlue and no old value
                    # previously_sel should always have a value here
                    removed_ids.append(max(previously_sel))
        log_vals = {
            "effected_user_id": effected_user.id,
            "add_group_ids": [(6, 0, added_ids)],
            "remove_group_ids": [(6, 0, removed_ids)],
        }
        self.env["users.log"].create(log_vals)

    #@api.multi
    def write(self, vals):
        self.log_group_change(vals, self)
        res = super(ResUsers, self).write(vals)
        return res