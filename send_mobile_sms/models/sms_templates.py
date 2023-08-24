# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import datetime
from werkzeug import urls
import functools
import urllib
import requests
import re
_logger = logging.getLogger(__name__)
try:
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,               # do not output newline after blocks
        autoescape=True,                # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': urls.url_quote,
        'urlencode': urls.url_encode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': functools.reduce,
        'map': map,
        'round': round,

        'relativedelta': lambda *a, **kw : relativedelta.relativedelta(*a, **kw),
    })
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")

class SendMobileSmsTemplate(models.Model):
    _name = "send.mobile.sms.template"
    _description = "Send SMS"


    # Get default 
    @api.model
    def _default_api_url(self):
        return self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('send_mobile_sms.api_url')

    @api.model
    def _default_username(self):        
        return self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('send_mobile_sms.sms_username')

    @api.model
    def _default_password(self):
        return self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('send_mobile_sms.sms_password')

    name = fields.Char(required=True, string='Name')
    model_id = fields.Many2one('ir.model', string='Applies to', help="The kind of document with with this template can be used")
    sms_to = fields.Char(string='To (Mobile)', help="To mobile number (placeholders may be used here)")
    sms_html = fields.Text('Body')
    sms_template_code = fields.Char('Code')
    
    ref_ir_act_window = fields.Many2one('ir.actions.act_window', 'Sidebar action', readonly=True, copy=False,help="Sidebar action to make this template available on records " "of the related document model")
    # ref_ir_value = fields.Many2one('ir.values', 'Sidebar Button', readonly=True, copy=False, help="Sidebar button to open the sidebar action")

    def convert(self, message):
        return ''.join(['{:04x}'.format(ord(byte)).upper() for byte in message])

    @api.model
    def send_sms(self, template_id, record_id):
        sms_rendered_content = self.env['send.mobile.sms.template'].render_template(template_id.sms_html, template_id.model_id.model, record_id)
        rendered_sms_to = self.env['send.mobile.sms.template'].render_template(template_id.sms_to, template_id.model_id.model, record_id)
        return self.send_sms_link(sms_rendered_content,rendered_sms_to,record_id,template_id.model_id.model)

    def send_sms_link(self,sms_rendered_content,rendered_sms_to,record_id,model):
        # sms_rendered_contents = sms_rendered_content.encode('utf-8', 'ignore')
        # sms_rendered_content_msg = urllib.parse.quote_plus(sms_rendered_contents)
        sms_rendered_content_msg = self.convert(sms_rendered_content)
        # if rendered_sms_to:
        #     rendered_sms_to = re.sub(r' ', '', rendered_sms_to)
        #     if '+' in rendered_sms_to:
        #         rendered_sms_to = rendered_sms_to.replace('+', '')
        #     if '-' in rendered_sms_to:
        #         rendered_sms_to = rendered_sms_to.replace('-', '')

        if rendered_sms_to:
            send_url = self._default_api_url()
            username = self._default_username()
            password = self._default_password()
            if not send_url:
                raise UserError(
                    _('URL not defined..! Go to Settings >>> General Settings >>> SMS Configuration'),
                )
            if not username:
                raise UserError(
                    _('Username not defined..! Go to Settings >>> General Settings >>> SMS Configuration'),
                )
            if not password:
                raise UserError(
                    _('Password not defined..! Go to Settings >>> General Settings >>> SMS Configuration'),
                )
            send_link = send_url.replace('{username}',username).replace('{password}',password).\
            replace('{sender}','Albassami').replace('{numbers}',rendered_sms_to).replace('{message}',sms_rendered_content_msg)
            response = requests.request("GET", url = send_link).text
            self.env['sms_track'].sms_track_create(record_id, sms_rendered_content, rendered_sms_to, response, model )
            return response

    def render_template(self, template, model, res_id):
        """Render the given template text, replace mako expressions ``${expr}``
           with the result of evaluating these expressions with
           an evaluation context containing:

                * ``user``: browse_record of the current user
                * ``object``: browse_record of the document record this sms is
                              related to
                * ``context``: the context passed to the sms composition wizard

           :param str template: the template text to render
           :param str model: model name of the document record this sms is related to.
           :param int res_id: id of document records those sms are related to.
        """
        template = mako_template_env.from_string(tools.ustr(template))
        user = self.env.user
        record = self.env[model].browse(res_id)

        variables = {
            'user': user
        }
        variables['object'] = record
        try:
            render_result = template.render(variables)
        except Exception:
            _logger.error("Failed to render template %r using values %r" % (template, variables))
            render_result = u""
        if render_result == u"False":
            render_result = u""

        return render_result

    
    def create_action(self):
        action_obj = self.env['ir.actions.act_window'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id)
        view = self.env.ref('send_mobile_sms.sms_compose_wizard_form')
        src_obj = self.model_id.model
        button_name = _('SMS Send (%s)') % self.name
        action = action_obj.create({
            'name': button_name,
            'type': 'ir.actions.act_window',
            'res_model': 'sms.compose',
            'src_model': src_obj,
            'view_type': 'form',
            'context': "{'default_template_id' : %d, 'default_use_template': True}" % (self.id),
            'view_mode': 'form,tree',
            'view_id': view.id,
            'target': 'new',
            'auto_refresh': 1,
            'binding_model_id': self.model_id.id,})
        self.write({
            'ref_ir_act_window': action.id,
        })
        return True
    
    def unlink_action(self):
        for template in self:
            if template.ref_ir_act_window:
                template.ref_ir_act_window.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).unlink()
        return True
