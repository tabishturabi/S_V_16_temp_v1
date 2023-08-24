# -*- coding: utf-8 -*-
{
    'name': "Items Gatepass",

    'summary': """
      Albassami Items Gatepass""",

    'description': """
        Albassami Items Gatepass
    """,

    'author': "Albassami",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.17',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','stock'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'wizards/reason_to_refuse_or_cancel.xml',
        'report/report.xml',
        'views/sequence.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ]
}
