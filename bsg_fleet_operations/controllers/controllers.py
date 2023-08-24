# -*- coding: utf-8 -*-
from odoo import http

# class BsgFleetOperations(http.Controller):
#     @http.route('/bsg_fleet_operations/bsg_fleet_operations/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bsg_fleet_operations/bsg_fleet_operations/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bsg_fleet_operations.listing', {
#             'root': '/bsg_fleet_operations/bsg_fleet_operations',
#             'objects': http.request.env['bsg_fleet_operations.bsg_fleet_operations'].search([]),
#         })

#     @http.route('/bsg_fleet_operations/bsg_fleet_operations/objects/<model("bsg_fleet_operations.bsg_fleet_operations"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bsg_fleet_operations.object', {
#             'object': obj
#         })