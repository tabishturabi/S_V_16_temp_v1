# -*- coding: utf-8 -*-
from werkzeug import utils

from odoo import api, http, SUPERUSER_ID, _
from odoo.addons.web.controllers.main import Home
from odoo.http import request, route

from odoo import registry as registry_get
from odoo.addons.portal.controllers.portal import \
    CustomerPortal as CustomerPortalMain
#from odoo.addons.web.controllers.main import login_and_redirect


class Auth2FAController(Home):
    @http.route('/web/verify_2fa', type='http', auth='none')
    def login_2fa(self, redirect=None, **kw):
        url = request.httprequest.headers.get('Referer')
        if url == None:
            return utils.redirect('/', 303)
        if request.session.auth_2fa is not None and \
                not request.session.auth_2fa['enable']\
                or request.session.auth_2fa['2fa_valid']:
            return utils.redirect('/', 303)
        user = request.env['res.users'].browse(
            request.session.user_identity).sudo(request.session.user_identity)
        values = request.params.copy()
        if request.httprequest.method == 'POST':
            code = request.params['code']
            credentials = user.check_secret_code(code)
            if credentials:
                del request.session['loginKey']
                request.session.auth_2fa['2fa_valid'] = True
                return login_and_redirect(*credentials, redirect_url='/')
            else:
                values['error'] = _("Wrong security code")
        return request.render("axis_google_2fa_auth.login_2fa", values)


class Login2FA(Home):

    @http.route()
    def index(self, *args, **kw):
        if request.session.uid and not request.env['res.users'].sudo().browse(
                request.session.uid).has_group('base.group_user'):
            auth_2fa = request.session.auth_2fa
            try:
                if auth_2fa is not None and auth_2fa['required'] and \
                        not auth_2fa['2fa_valid']:
                    # request.params['login_success'] = False
                    with registry_get(request.session.db).cursor() as cr:
                        env = api.Environment(cr, SUPERUSER_ID, {})
                        user = env['res.users'].browse(request.session.uid)
                        if user:
                            if user.check_2fa_status():
                                old_uid = request.session.uid
                                old_key = request.session.loginKey
                                request.session['user_identity'] = request.session.uid
                                request.session.logout(keep_db=True)
                                request.session.user_identity = old_uid
                                request.session.loginKey = old_key
                                request.session.auth_2fa = auth_2fa
                                return utils.redirect('/web/verify_2fa')
            except Exception as e:
                raise e
        return super(Login2FA, self).index(*args, **kw)

    @http.route('/web', type='http', auth="user")
    def web_client(self, s_action=None, **kw):
        response = super(Login2FA, self).web_client(s_action=s_action, **kw)
        auth_2fa = request.session.auth_2fa
        try:
            if auth_2fa is not None and auth_2fa['required'] and \
                    not auth_2fa['2fa_valid']:
                with registry_get(request.session.db).cursor() as cr:
                    env = api.Environment(cr, SUPERUSER_ID, {})
                    user = env['res.users'].browse(request.session.uid)
                    if user:
                        if user.check_2fa_status():
                            old_uid = request.session.uid
                            old_key = request.session.loginKey
                            request.session['user_identity'] = request.session.uid
                            request.session.logout(keep_db=True)
                            request.session.user_identity = old_uid
                            request.session.loginKey = old_key
                            request.session.auth_2fa = auth_2fa
                            return utils.redirect('/web/verify_2fa', 303)
        except Exception as e:
            raise e
        return response


class CustomerPortal(CustomerPortalMain):

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        if request.httprequest.method == 'POST':
            if 'is_2fa_change' in post and post.get('is_2fa_change') == 'yes':
                post.pop('is_2fa_change')
                user = request.env.user
                if 'is_2fa_enable' in post and \
                        post.get('is_2fa_enable') == 'on':
                    post.pop('is_2fa_enable')
                    user.sudo().write({'is_2fa_enable': True})
                else:
                    user.sudo().write({'is_2fa_enable': False})
                user.sudo().generate_secret_key_qrcode()
            if 'is_2fa_change' in post:
                post.pop('is_2fa_change')
            if 'is_2fa_enable' in post:
                post.pop('is_2fa_enable')
        return super(CustomerPortal, self).account(
            redirect=redirect, **post)
