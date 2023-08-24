# -*- coding: utf-8 -*-

{
    'name': 'Assets Enhanced',
    'version': '1.08',
    'summary': 'Assets Enhanced',
    'description': """
        Assets Enhanced
    """,
    'author': 'Solutionfounder',
    'website': "http://www.solutionfounder.com",
    'category': 'Accounting',
    'sequence': 33,
    'depends': ['account_asset','hr','bsg_branch_config','bsg_trip_mgmt','contract_enhanced','payments_enhanced'],
    'data': [
        #'views/asset_type_inherit_view.xml',
        'views/asset_inherit_view.xml',
    ],
}
