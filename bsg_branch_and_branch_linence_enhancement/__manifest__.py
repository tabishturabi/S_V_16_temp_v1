# -*- coding: utf-8 -*-
{
    'name': "Branches And Branch License Enhancement",

    'summary': """
      Branches And Branch License Enhancement""",

    'description': """
        Branches And Branch License Enhancement
    """,

    'author': "Muhammad Arshad Khalil",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['base','bsg_branch_config'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
