# -*- coding: utf-8 -*-
from odoo import http

# class BsgWarehouseRestrictions(http.Controller):
#     @http.route('/bsg_warehouse_restrictions/bsg_warehouse_restrictions/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bsg_warehouse_restrictions/bsg_warehouse_restrictions/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bsg_warehouse_restrictions.listing', {
#             'root': '/bsg_warehouse_restrictions/bsg_warehouse_restrictions',
#             'objects': http.request.env['bsg_warehouse_restrictions.bsg_warehouse_restrictions'].search([]),
#         })

#     @http.route('/bsg_warehouse_restrictions/bsg_warehouse_restrictions/objects/<model("bsg_warehouse_restrictions.bsg_warehouse_restrictions"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bsg_warehouse_restrictions.object', {
#             'object': obj
#         })