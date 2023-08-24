# -*- coding: utf-8 -*-
{
    'name': "HR Custody",

    'summary': """
        A module to manage hr employee custodies""",

    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Human Resources',
    'version': '12.19',

    # any module necessary for this one to work correctly
    'depends': ['base','account_asset','hr','mail','bsg_fleet_operations','bsg_hr','account_asset'],

    # always loaded
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        'views/views.xml',
    ],
}
