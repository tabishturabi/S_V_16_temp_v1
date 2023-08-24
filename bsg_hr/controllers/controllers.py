# -*- coding: utf-8 -*-
from odoo import http

# class BsgHr(http.Controller):
#     @http.route('/bsg_hr/bsg_hr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bsg_hr/bsg_hr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bsg_hr.listing', {
#             'root': '/bsg_hr/bsg_hr',
#             'objects': http.request.env['bsg_hr.bsg_hr'].search([]),
#         })

#     @http.route('/bsg_hr/bsg_hr/objects/<model("bsg_hr.bsg_hr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bsg_hr.object', {
#             'object': obj
#         })