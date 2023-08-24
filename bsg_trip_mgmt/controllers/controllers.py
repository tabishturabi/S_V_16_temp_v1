# -*- coding: utf-8 -*-
from odoo import http

# class BsgTripMgmt(http.Controller):
#     @http.route('/bsg_trip_mgmt/bsg_trip_mgmt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bsg_trip_mgmt/bsg_trip_mgmt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bsg_trip_mgmt.listing', {
#             'root': '/bsg_trip_mgmt/bsg_trip_mgmt',
#             'objects': http.request.env['bsg_trip_mgmt.bsg_trip_mgmt'].search([]),
#         })

#     @http.route('/bsg_trip_mgmt/bsg_trip_mgmt/objects/<model("bsg_trip_mgmt.bsg_trip_mgmt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bsg_trip_mgmt.object', {
#             'object': obj
#         })