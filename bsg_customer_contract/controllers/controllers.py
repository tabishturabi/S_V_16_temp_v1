# -*- coding: utf-8 -*-
from odoo import http

# class BsgCustomerContract(http.Controller):
#     @http.route('/bsg_customer_contract/bsg_customer_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bsg_customer_contract/bsg_customer_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bsg_customer_contract.listing', {
#             'root': '/bsg_customer_contract/bsg_customer_contract',
#             'objects': http.request.env['bsg_customer_contract.bsg_customer_contract'].search([]),
#         })

#     @http.route('/bsg_customer_contract/bsg_customer_contract/objects/<model("bsg_customer_contract.bsg_customer_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bsg_customer_contract.object', {
#             'object': obj
#         })