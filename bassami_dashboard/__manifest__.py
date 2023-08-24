# -*- coding: utf-8 -*-

{
    'name': 'Bassami Dashboard',
    'summary': 'Bassami Dashboard',
    'category': 'Sales',
    'version': '12.0.8',
    'author': 'SolutionFounder',
    'website': "http://www.solutionfounder.com",
    'depends': ['base','web','bsg_branch_config','bsg_cargo_sale'],
    'data': [
        'security/ir.model.access.csv',
        'templates/data.xml',
        'templates/view.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'bassami_dashboard/static/src/css/style.css',
    #     ],
    # },
    'installable': True,
}
