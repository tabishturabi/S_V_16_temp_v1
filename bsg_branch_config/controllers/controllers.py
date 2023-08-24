# -*- coding: utf-8 -*-
from odoo import http

# class BsgBranchConfig(http.Controller):
#     @http.route('/bsg_branch_config/bsg_branch_config/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bsg_branch_config/bsg_branch_config/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bsg_branch_config.listing', {
#             'root': '/bsg_branch_config/bsg_branch_config',
#             'objects': http.request.env['bsg_branch_config.bsg_branch_config'].search([]),
#         })

#     @http.route('/bsg_branch_config/bsg_branch_config/objects/<model("bsg_branch_config.bsg_branch_config"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bsg_branch_config.object', {
#             'object': obj
#         })
