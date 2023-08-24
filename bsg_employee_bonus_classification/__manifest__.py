# -*- coding: utf-8 -*-
{
    'name': "Employee Bonus Classification",

    'summary': """
      Albassami Employee Bonus Classification""",

    'description': """
        Albassami Employee Bonus Classification
    """,

    'author': "Muhammad Arshad Khalil",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.31',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','bsg_hr','bsg_branch_config','bsg_trip_mgmt'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'wizards/add_members.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ]
}
