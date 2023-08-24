from odoo import fields, models,api

class MeNotficationUser(models.Model):
    _name = "me.notification.user"

    user_ids = fields.Many2many('res.users')

    # @api.multi
    def execute_settings(self):
        self.ensure_one()
        bonus_config = self.env.ref('maintenance_enhance.me_notification_users_data', False)
        bonus_config.sudo().write({'user_ids': [(6, 0, self.user_ids.ids)]})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def default_get(self, fields):
        res = super(MeNotficationUser, self).default_get(fields)
        notification_config = self.env.ref('maintenance_enhance.me_notification_users_data', False)
        if notification_config:
            res.update({'user_ids': notification_config.sudo().user_ids.ids})
        return res