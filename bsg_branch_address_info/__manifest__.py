# -*- coding: utf-8 -*-
{
    'name': "Branches Address Info",

    'summary': """
      Albassami Branches Address Info""",

    'description': """
        Albassami Branches Address Info
    """,

    'author': "Albassami",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.4',

    # any module necessary for this one to work correctly
    'depends': ['base','bsg_branch_config','bsg_branches_zone_and_region_and_branch_config','bsg_cargo_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ]
}
