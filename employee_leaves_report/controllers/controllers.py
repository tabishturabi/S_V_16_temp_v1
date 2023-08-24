# -*- coding: utf-8 -*-
from odoo import http

# class BxProductivityReports(http.Controller):
#     @http.route('/bx_productivity_reports/bx_productivity_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bx_productivity_reports/bx_productivity_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bx_productivity_reports.listing', {
#             'root': '/bx_productivity_reports/bx_productivity_reports',
#             'objects': http.request.env['bx_productivity_reports.bx_productivity_reports'].search([]),
#         })

#     @http.route('/bx_productivity_reports/bx_productivity_reports/objects/<model("bx_productivity_reports.bx_productivity_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bx_productivity_reports.object', {
#             'object': obj
#         })