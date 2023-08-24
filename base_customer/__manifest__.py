# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Solution founder IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Customization for customer",
    'summary': """
        
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",
    'category': 'Accounting, Customer',
    'version': '12.0.40',
    'depends': ['account','base'],
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'views/partner_cust.xml',
        'views/partner_types.xml',
        
    ],
    'demo': [
    ],
}