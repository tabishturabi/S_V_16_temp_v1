# -*- coding: utf-8 -*-
{
    'name': "Customers Contract Button",

    'summary': """
      Customers Contract Button""",

    'description': """
        Bassami Customers Contract Button
    """,

    'author': "Albassami",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','bsg_cargo_sale','bsg_customer_contract'],

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
