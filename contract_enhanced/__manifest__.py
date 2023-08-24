# -*- coding: utf-8 -*-
{
    'name': 'Recurring - Contracts Management Enhanced',
    'version': '12.0.9',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "bassamitech",
    'website': "http://www.bassamitech.com",
    'depends': ['contract', 'account', 'bsg_branch_config','hr','bsg_fleet_operations'],
    'data': [
        'security/access_security.xml',
        'views/contract_inherit_view.xml',
        'views/account_invoice_line_inherit_view.xml', 
        'views/menu_inherits_views.xml', 
    ],
    'installable': True,
}
