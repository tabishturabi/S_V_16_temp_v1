# -*- coding: utf-8 -*-
{
    'name': "Sales Branches Access Rights And Menues",

    'summary': """
      Sales Branches Access Rights And Menues""",

    'description': """
        Sales Branches Access Rights And Menues
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['base','bsg_license_report','bsg_branch_config','sale', 'bsg_cargo_sale'],

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
    ],
}
