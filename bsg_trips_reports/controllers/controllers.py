# -*- coding: utf-8 -*-
from odoo import http

# class LmsManagment(http.Controller):
#     @http.route('/lms_managment/lms_managment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lms_managment/lms_managment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lms_managment.listing', {
#             'root': '/lms_managment/lms_managment',
#             'objects': http.request.env['lms_managment.lms_managment'].search([]),
#         })

#     @http.route('/lms_managment/lms_managment/objects/<model("lms_managment.lms_managment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lms_managment.object', {
#             'object': obj
#         })