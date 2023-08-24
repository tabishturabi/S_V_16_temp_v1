# -*- coding: utf-8 -*-
from odoo import http

# class BsgCargoSale(http.Controller):
#     @http.route('/bsg_cargo_sale/bsg_cargo_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bsg_cargo_sale/bsg_cargo_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bsg_cargo_sale.listing', {
#             'root': '/bsg_cargo_sale/bsg_cargo_sale',
#             'objects': http.request.env['bsg_cargo_sale.bsg_cargo_sale'].search([]),
#         })

#     @http.route('/bsg_cargo_sale/bsg_cargo_sale/objects/<model("bsg_cargo_sale.bsg_cargo_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bsg_cargo_sale.object', {
#             'object': obj
#         })