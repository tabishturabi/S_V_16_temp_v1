# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Solution founder IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Budget Enhanced",
    'summary': """
        
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",
    'category': 'Accounting',
    'version': '12.0.13',
    'depends': ['web','analytic','bsg_cargo_sale','account_accountant','sales_team','account_generic_enhanced','base','account','sale', 'bsg_branch_config','base_customer','account_asset','account_reports','account_parent','payments_enhanced','account_generic_enhanced'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/budget_action_view.xml',
        'views/inherit_payment_view.xml',
        
    ],
    'demo': [
    ],
}
