# -*- coding: utf-8 -*-
import qrcode
import pyotp
import random
import string
import base64
import os
import platform
import logging
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import Warning

from odoo import registry as registry_get
from odoo.http import request
from odoo.exceptions import UserError

_secret_key, _image_2fa = '', ''

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_2fa_enable = fields.Boolean(string="2FA authentication")
    secret_key = fields.Char(string="Secret key", readonly=True, copy=False)
    image_2fa = fields.Binary(
        string="Scan QR code", readonly=True, attachment=False, copy=False)

    @api.onchange('is_2fa_enable')
    def generate_secret_key_qrcode(self):
        global _secret_key
        global _image_2fa
        if self.is_2fa_enable:
            if not self.email:
                raise Warning(_('Please enter your email'))
            _secret_key = self._get_code(16)
            self.secret_key = _secret_key
            company_name = self.get_company_name()
            auth = pyotp.totp.TOTP(
                self.secret_key.replace(" ", "")
            ).provisioning_uri(self.email, issuer_name=company_name)
            if platform.system() == 'Linux':
                file_name = '/tmp/temp.png'
            else:
                file_name = 'temp.png'
            image_file = qrcode.make(auth)
            image_file.save(file_name)
            with open(file_name, "rb") as img:
                _image_2fa = base64.b64encode(img.read())
            self.image_2fa = _image_2fa
            os.remove(file_name)
        else:
            self.secret_key = _secret_key = ''
            self.image_2fa = _image_2fa = ''

    @api.model
    def create(self, vals):
        global _secret_key
        global _image_2fa
        if vals.get('is_2fa_enable'):
            vals['secret_key'] = _secret_key
            vals['image_2fa'] = _image_2fa
        if 'is_2fa_enable' in vals and not vals.get('is_2fa_enable'):
            vals['secret_key'] = ''
            vals['image_2fa'] = ''
        res = super(ResUsers, self).create(vals)
        return res

    #@api.multi
    def write(self, vals):
        global _secret_key
        global _image_2fa
        if vals.get('is_2fa_enable'):
            vals['secret_key'] = _secret_key
            vals['image_2fa'] = _image_2fa
        if 'is_2fa_enable' in vals and not vals.get('is_2fa_enable'):
            vals['secret_key'] = ''
            vals['image_2fa'] = ''
        res = super(ResUsers, self).write(vals)
        return res

    def _check_credentials(self, password):
        if not request.session.auth_2fa:
            request.session.auth_2fa = {
                'enable': False, 'required': False, '2fa_valid': False}
            if self.is_2fa_enable:
                request.session.auth_2fa['enable'] = True
                request.session.auth_2fa['required'] = True
        request.session['loginKey'] = password
        return super(ResUsers, self)._check_credentials(password)

    #@api.multi
    def _get_code(self, length):
        ran_str = ''.join(random.choice(
            string.ascii_uppercase) for _ in range(length))
        return self._add_spaces(ran_str, 4)

    #@api.multi
    def _add_spaces(self, string, length):
        return ' '.join(
            string[i:i+length] for i in range(0, len(string), length))

    #@api.multi
    def check_2fa_status(self):
        self.ensure_one()
        return self.is_2fa_enable

    #@api.multi
    def get_company_name(self):
        company_id = self.env.user.company_id.id
        website = self.env['website'].search(
            [('company_id', '=', company_id)], limit=1)
        website_name = 'OdooAppSecure'
        if website:
            website_name = website.name
        return website_name.replace(" ", "")

    #@api.multi
    def check_secret_code(self, code):
        dbname = request.session.db
        key = request.session.loginKey

        registry = registry_get(dbname)

        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
        # return (dbname, self.login, key)
        secret_key = self.secret_key.replace(" ", "")
        totp = pyotp.TOTP(secret_key)
        verify = totp.verify(str(code))
        return (dbname, self.login, key) if verify else False

    #@api.multi
    def action_send_qrcode(self):
        self.ensure_one()
        if not self.email:
            raise UserError(
                _("Cannot send QR-code email: user %s has no email address."
                  ) % self.name)
        template = False
        try:
            template = self.env.ref(
                'axis_google_2fa_auth.mail_template_user_2fa_qrcode',
                raise_if_not_found=False)
        except ValueError:
            pass

        if not template:
            raise UserError(_("Could not found email template."))

        template_values = {
            'email_to': '${object.email|safe}',
        }
        template.write(template_values)

        with self.env.cr.savepoint():
            template.with_context(lang=self.lang).send_mail(
                self.id, force_send=True, raise_exception=True)
        _logger.info("Two-way auth QR-code email sent for user <%s> to <%s>",
                     self.login, self.email)
