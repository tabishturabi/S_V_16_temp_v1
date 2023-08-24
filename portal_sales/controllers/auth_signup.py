# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import werkzeug

from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home
# from odoo.addons.web_settings_dashboard.controllers.main import WebSettingsDashboard as Dashboard
from odoo.exceptions import UserError
from odoo.http import request
# for regular expressions
import re

_logger = logging.getLogger(__name__)

class AuthSignupHome(Home):

    #nationality_ids = request.env['res.country'].sudo().search([])
    #default_country = request.env['res.country'].sudo().search([('code', '=', 'SA'), ('phone_code', '=', '966')],limit=1).id

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    user_sudo = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))])
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
                        ).send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        nationality_ids = request.env['res.country'].sudo().search([('visible_on_mobile_app','=',True)])
        default_country = request.env['res.country'].sudo().search([('code', '=', 'SA'), ('phone_code', '=', '966')],limit=1).id

        qcontext['nationality_ids'] = nationality_ids
        qcontext['default_country'] = default_country
        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def check_partner_already_exist(self, values):
        response = {}
        partner_id = False
        try:
            if values.get('customer_id_card_no'):
                partner_id = request.env['res.partner'].sudo().search([('customer_id_card_no', '=', values.get('customer_id_card_no'))])
            elif values.get('iqama_no'):    
                partner_id = request.env['res.partner'].sudo().search([('iqama_no', '=', values.get('iqama_no'))])
            if partner_id:
                user_id = request.env['res.users'].sudo().search([("partner_id", "=", partner_id.id)])
                if user_id:
                    raise UserError(_("Another user is already registered using this Identity Number."))
                else:
                    response['partner_id'] = partner_id.id   
        except UserError as e:
            raise UserError(_(e.name or e.value))
        except (SignupError, AssertionError) as e:
            _logger.error("%s", e)
            raise UserError(_("Sorry could not create a new account."))
        return response

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password','customer_type','customer_id_type',
                                'identity_number','country_id','phone')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang   
        if not qcontext.get('only_passwords'):  
            if values.get('login'):
                email_match = re.match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', values.get('login'))
                if email_match is None:
                    raise UserError(_("Sorry! Please Enter Valid Email Address"))
            if values.get('name'):
                name_match = re.match('^[\w\s]+$', values.get('name'))
                if name_match is None or any(char.isdigit() for char in values.get('name')):
                    raise UserError(_("Sorry! Please Enter Valid Name , It Must Contain Only Letters"))

            if values.get('country_id'):
                values['customer_nationality'] = values.get('country_id')
            # else:
            #     raise UserError(_("Sorry! Please Enter Nationality"))

            if values.get('customer_type','1'):
                if values.get('customer_type') == '1':
                    values['customer_id_card_no'] = qcontext.get('identity_number')
                    match = re.match(r'1[0-9]{9}', values['customer_id_card_no'])
                    if match is None or len(str(values['customer_id_card_no'])) != 10:
                        raise UserError(
                            _('Sorry! Identity Number Must Be Start From 1 And Must Have 10 Digits.'),
                        ) 
                if values.get('customer_type') == '2': 
                    values['iqama_no'] =  qcontext.get('identity_number')
                    if values.get('customer_id_type') == 'saudi_id_card':
                            raise UserError(
                                _("Sorry! You Can't Choose Saudi ID Card For Non-Saudi Type."),
                            )
                    if values.get('customer_id_type') == 'iqama':
                        match = re.match(r'2[0-9]{9}', values['iqama_no'])
                        if match is None or len(str(values['iqama_no'])) != 10:
                            raise UserError(
                                _('Sorry! Identity Number Must Be Start From 2 And Must Have 10 Digits.'),
                            )
                    # if values.get('country_id'):
                    #     values['customer_nationality'] = values.get('country_id')
                    # else:
                    #     raise UserError(_("Sorry! Please Enter Nationality"))
                        #else:
            #    raise UserError(_("Sorry! Please Enter Customer Type."))  
            res = self.check_partner_already_exist(values)
            partner_type = request.env['partner.type'].sudo().search([('is_default_in_portal', '=', True)],limit=1) 
            values['partner_types'] = partner_type.id
            if res.get('partner_id'):
                partner_id = request.env['res.partner'].sudo().search([('id', '=', res.get('partner_id'))],limit=1) 
                values['partner_id'] = partner_id.id
                values['name'] = partner_id.name
                if partner_id.partner_types:
                    values['partner_types'] = partner_id.partner_types.id
            values['company_ids'] =  [(6, 0, request.website.company_id.ids)]       
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()
