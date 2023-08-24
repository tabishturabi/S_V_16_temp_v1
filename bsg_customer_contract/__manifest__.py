# -*- coding: utf-8 -*-
{
    'name': "bsg_customer_contract",

    'summary': """
        Purpose of this module is to define pricing against different customer types""",

    'description': """
        Purpose of this module is to define pricing against different customer types
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.58',

    # any module necessary for this one to work correctly
    'depends': ['base','bsg_master_config'],

    # always loaded
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/menus.xml',
        'views/customer_contract_view.xml',
        'views/menus.xml',
        'views/customer_contract_line_view.xml',
        'wizard/view_import_contract_lines.xml',
        'views/sequence.xml',
        'data/ir_attachment.xml',
    ],
}
