# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseSmartButton(http.Controller):
#     @http.route('/purchase_smart_button/purchase_smart_button/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_smart_button/purchase_smart_button/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_smart_button.listing', {
#             'root': '/purchase_smart_button/purchase_smart_button',
#             'objects': http.request.env['purchase_smart_button.purchase_smart_button'].search([]),
#         })

#     @http.route('/purchase_smart_button/purchase_smart_button/objects/<model("purchase_smart_button.purchase_smart_button"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_smart_button.object', {
#             'object': obj
#         })