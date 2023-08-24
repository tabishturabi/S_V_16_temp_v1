# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class IrActionsServer(models.Model):

    _inherit = 'ir.actions.server'

    state = fields.Selection(selection_add=[
        ('sms', 'Send SMS'),
    ],ondelete={'sms': 'set default'})

    sms_template_id = fields.Many2one('send.mobile.sms.template',string="SMS Template", ondelete='set null', domain="[('model_id', '=', model_id)]",)

    @api.model
    def run_action_sms(self, action, eval_context=None):
        if not action.sms_template_id or not self._context.get('active_id'):
            return False
        self.env['send.mobile.sms.template'].send_sms(action.sms_template_id, self.env.context.get('active_id'))
        return False
