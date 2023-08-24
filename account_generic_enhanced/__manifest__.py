# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Solution founder IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Enhance Generic Chat of Account",
    'summary': """
        
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",
    'category': 'Accounting',
    'version': '1.0.12',
    'depends': ['account','bsg_branch_config','analytic'],
    'data': [
        'data/account_extends.xml', 
        'security/ir.model.access.csv',
        'views/account_extends.xml',
        'views/account_generic.xml',
        'views/basg_brances.xml',
        'views/account_journals_custom.xml'
        # data file heirarchy set at last to remove "Model account.fuel.trip.configuration has no table" Bug 
        # 

    ],
    'demo': [
    ],
}