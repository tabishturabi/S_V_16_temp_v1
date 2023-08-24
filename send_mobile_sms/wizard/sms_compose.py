# -*- coding: utf-8 -*-
import base64
import re
import logging
from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.tools.translate import _
from odoo import tools
from odoo.tools.safe_eval import safe_eval as eval

_logger = logging.getLogger(__name__)

class SMSComposer(models.TransientModel):
    _name = 'sms.compose'
    _description = 'SMS composition wizard'
    _log_access = True

    @api.onchange('template_id')
    def _get_body_text(self):
        self.body_text= self.template_id.sms_html
        self.sms_to_lead = self.template_id.sms_to

    template_id = fields.Many2one('send.mobile.sms.template', 'SMS Template')
    body_text = fields.Text('Body')
    sms_to_lead = fields.Char(string='To (Mobile)')

    
    def send_sms_action(self):
        active_ids = self.env.context.get('active_ids')
        for ids in active_ids:
            my_model = self._context['active_model']
            message = self.env['send.mobile.sms.template'].render_template(self.body_text, my_model, ids)
            mobile_no = self.env['send.mobile.sms.template'].render_template(self.sms_to_lead, my_model, ids)
            self.env['send.mobile.sms.template'].send_sms_link(message, mobile_no,ids,my_model)
        return True
