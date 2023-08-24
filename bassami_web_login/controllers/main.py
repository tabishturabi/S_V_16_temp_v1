# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug
import odoo
import base64
import datetime

from odoo import http, fields
from odoo.http import request

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as df
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

from odoo.addons.website.controllers.main import Website

import werkzeug.utils
# 
class WebLoginWl(object):
    def check_client_db_redirect(self, session_info):
        print (">>>>redirect")
        if session_info:
            return werkzeug.utils.redirect('/web-my-barnchs')
        return session_info
    
class HomeLogin(odoo.addons.web.controllers.main.Home, WebLoginWl):
    
    @http.route('/web/login', type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        session_info = super(HomeLogin, self).web_login(redirect=redirect)
        print (">>>>redirect",redirect, session_info, kw)
        if kw and request.env.user and request.env.user.user_branch_ids and len(request.env.user.user_branch_ids.ids) > 1:
            return self.check_client_db_redirect(session_info)
        else:
            if request.env.user and request.env.user.user_branch_ids and len(request.env.user.user_branch_ids.ids) == 1:
                request.env.user.user_branch_id = request.env.user.user_branch_ids[0].id
                request.env['ir.rule'].clear_cache()
            return session_info
 
 
class SessionLogin(odoo.addons.web.controllers.main.Session, WebLoginWl):
    @http.route('/web/session/authenticate', type='json', auth="none")
    def authenticate(self, db, login, password, base_location=None):
        session_info = super(SessionLogin, self).authenticate(db, login, password, base_location=base_location)
        return self.check_client_db_redirect(session_info)

class BassmiWebsite(http.Controller):
    
    @http.route(['/web-my-barnchs'], type='http', auth="user", website=True)
    def BassmiBarnchs(self, **post):
        return request.render("bassami_web_login.branchs_layout", {})
    
    @http.route(['/my-web-my-barnchs'], type='http', auth="user", website=True)
    def VofficeHome(self, **post):
        if post.get('branch_id'):
            request.env.user.user_branch_id = int(post.get('branch_id'))
            request.env['ir.rule'].clear_cache()
            return werkzeug.utils.redirect('/web')
