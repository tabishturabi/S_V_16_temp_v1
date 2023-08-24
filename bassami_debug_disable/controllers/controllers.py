# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from odoo import http
from odoo.addons.web.controllers.home import Home as WebHome

from odoo.addons.web.controllers.main import Home, ensure_db
from odoo.http import request
import werkzeug.utils


class Home(WebHome):

    @http.route()
    def web_client(self, s_action=None, **kw):
        ensure_db()
        if kw.get('debug') == '' or kw.get('debug') == '1' or kw.get('debug') == 'assets':
	        res_users = request.env['res.users'].browse(http.request.env.context.get('uid'))
	        if not res_users.has_group('base.group_system'):
	            return werkzeug.utils.redirect('/web')#redirect_with_hash('/web')
        return super().web_client(s_action, **kw)


