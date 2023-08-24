# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Solution founder IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Cash Vendor",
    'summary': """
        
    """,

    'author': "ALbassami-Group",
    'website': "http://www.albassamitransport.com",
    'category': 'Purchases',
    'version': '1.0.6',
    'depends': ['base','hr','purchase'],
    'data': [
#         'security/ir.model.access.csv',
        'views/employee.xml',
#         'views/vendor_types.xml',
        'views/purchase_order.xml',
        'views/vendor.xml',
        
    ],
    'demo': [
    ],
}