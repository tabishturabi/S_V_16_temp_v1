# -*- coding: utf-8 -*-
from odoo import http

# class AuthSignupCustom(http.Controller):
#     @http.route('/auth_signup_custom/auth_signup_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/auth_signup_custom/auth_signup_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('auth_signup_custom.listing', {
#             'root': '/auth_signup_custom/auth_signup_custom',
#             'objects': http.request.env['auth_signup_custom.auth_signup_custom'].search([]),
#         })

#     @http.route('/auth_signup_custom/auth_signup_custom/objects/<model("auth_signup_custom.auth_signup_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('auth_signup_custom.object', {
#             'object': obj
#         })