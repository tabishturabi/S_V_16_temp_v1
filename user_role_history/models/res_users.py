# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.base.models.res_users import is_selection_groups


class ResUsers(models.Model):
    _inherit = 'res.users'

    last_role_line_modification = fields.Datetime(
        string="Last roles modification",
        readonly=True,
    )

    #return dictionary
    @api.model
    def _prepare_role_line_history_dict(self, group_name,values,category_val):
        return {
            'user_id': self.id,
            'updated_user_id': self.env.user.id,
            'category_name' : category_val,
            'group_name': group_name,
            'old_is_enabled': False if values == True else True,
            'new_is_enabled': values,
            'last_role_line_modification' : fields.Datetime.now()

        }

    #return list of dictionary
    #@api.multi
    def _get_role_line_values_by_user(self,vals):
        role_line_values_by_user = {}
        new_value_list = []
        for rec in self:
            if vals:
                for data in vals.items():
                    group_name = ''
                    vals = data[0]
                    vals_value = data[1]
                    category_val = False
                    check_condition = str(vals_value)
                    is_digit = check_condition.isdigit()
                    if is_digit == True:
                        group_name = self.env['res.groups'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(vals_value).name
                        category_val = self.env['res.groups'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(vals_value).category_id.name
                        vals_value = True
                    else:
                        if vals.startswith('in_group'):
                            getting_id = vals.replace("in_group_", "")
                            group_name = self.env['res.groups'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(getting_id)).name
                            category_val = self.env['res.groups'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(getting_id)).category_id.name
                        elif vals.startswith('sel_groups'):
                            split_val =[int(v) for v in vals[11:].split('_')]
                            group_name = ''
                            category_val = self.env['res.groups'].search([('id','in',split_val)],limit=1).category_id.name
                    # role_line_values_by_user.setdefault(rec, {})
                    role_line_values_by_user= self._prepare_role_line_history_dict(group_name,vals_value,category_val)
                    new_value_list.append(role_line_values_by_user)
        return new_value_list

    #override write method
    #@api.multi
    def write(self, vals):
        if vals:
            cahnge_value = self._get_role_line_values_by_user(vals)
            if cahnge_value:
                for data in cahnge_value:
                    self.env['base.user.role.line.history'].create(data)
        res = super().write(vals)
        return res

    #to see roles change history
    #@api.multi
    def show_role_lines_history(self):  
        self.ensure_one()
        domain = [('user_id', '=', self.id)]
        return {
            'name': _("Roles history"),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'base.user.role.line.history',
            'domain': domain,
        }
