# -*- coding: utf-8 -*-
{
    'name': "Barriers Conformity Certificate",

    'summary': """
      Barriers Conformity Certificate""",

    'description': """
        Barriers Conformity Certificate
    """,

    'author': "Muhammad Arshad Khalil",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.17',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','sale_management','bsg_master_config'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'security/groups.xml',
        'views/views.xml',
        'views/templates.xml',
        'reports/barrier_conformity_certificate.xml',
        'views/res_config_settings_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ]
}
