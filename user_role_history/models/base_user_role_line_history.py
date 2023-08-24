# -*- coding: utf-8 -*-

from odoo import api, fields, models


class BaseUserRoleLineHistory(models.Model):
    _name = 'base.user.role.line.history'
    _description = "History of user roles"
    _order = 'id desc'


    user_id = fields.Many2one(
        string="User",
        comodel_name='res.users',
        ondelete='cascade',
        readonly=True,
        index=True,
    )
    updated_user_id = fields.Many2one('res.users')
    group_name = fields.Char(string="Group Name")
    old_is_enabled = fields.Boolean(
        string="Old Access",
        readonly=True,
    )
    category_name = fields.Char(string="Category Name")
    new_is_enabled = fields.Boolean(
        string="New Access",
        readonly=True,
    )
    last_role_line_modification = fields.Datetime(
        string="Last roles modification",
        readonly=True,
    )

    # @api.model
    # def _prepare_create_from_vals(
    #         self,
    #         old_role_line_values_by_user,
    #         new_role_line_values_by_user
    # ):
    #     role_history_line_vals_by_role_line = {}
    #     for key, value in new_role_line_values_by_user.items():
    #         old_vals = old_role_line_values_by_user.get(key, {})
    #         new_vals = value
    #         # Manage deletion of role lines and old values of modified lines
    #         for role_line_id, role_line_vals in old_vals.items():
    #             action = 'unlink' if role_line_id not in new_vals else 'edit'
    #             if action == 'edit':
    #                 # Skip if no change
    #                 if not any(
    #                         role_line_vals[k] != new_vals[role_line_id][k]
    #                         for k in role_line_vals
    #                 ):
    #                     continue
    #             role_history_line_vals_by_role_line.setdefault(
    #                 role_line_id, {}
    #             )
    #             role_history_line_vals_by_role_line[role_line_id].update({
    #                 'performed_action': action,
    #                 'user_id': role_line_vals['user_id'],
    #                 'old_role_id': role_line_vals['role_id'],
    #                 'old_date_from': role_line_vals['date_from'],
    #                 'old_date_to': role_line_vals['date_to'],
    #                 'old_is_enabled': role_line_vals['is_enabled'],
    #             })
    #         # Manage addition of role lines and new values of modified ones
    #         for role_line_id, role_line_vals in new_vals.items():
    #             action = 'add' if role_line_id not in old_vals else 'edit'
    #             if action == 'edit':
    #                 # Skip if no change
    #                 if not any(
    #                         role_line_vals[k] != old_vals[role_line_id][k]
    #                         for k in role_line_vals
    #                 ):
    #                     continue
    #             role_history_line_vals_by_role_line.setdefault(
    #                 role_line_id, {}
    #             )
    #             role_history_line_vals_by_role_line[role_line_id].update({
    #                 'performed_action': action,
    #                 'user_id': role_line_vals['user_id'],
    #                 'new_role_id': role_line_vals['role_id'],
    #                 'new_date_from': role_line_vals['date_from'],
    #                 'new_date_to': role_line_vals['date_to'],
    #                 'new_is_enabled': role_line_vals['is_enabled'],
    #             })
    #     return role_history_line_vals_by_role_line

    # @api.model
    # def create_from_vals(
    #         self,
    #         old_role_line_values_by_user,
    #         new_role_line_values_by_user
    # ):
    #     """
    #     This method creates user role line history objects based on given
    #     old/new values.
    #     old_role_line_values_by_user and new_role_line_values_by_user are like:
    #     {user_id:
    #      {role_line_id:
    #       {role_line_values},
    #      },
    #     }
    #     """
    #     role_history_line_vals_by_role_line = self._prepare_create_from_vals(
    #         old_role_line_values_by_user, new_role_line_values_by_user
    #     )
    #     # Create the history lines with suspend security
    #     # (nobody has the create right)
    #     for role_history_vals in role_history_line_vals_by_role_line.values():
    #         self.suspend_security().create(role_history_vals)
