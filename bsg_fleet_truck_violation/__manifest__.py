# -*- coding: utf-8 -*-
{
    'name': "Truck Violation",

    'summary': """
      Menu under fleet operations/truck violation""",

    'description': """Truck Violation""",

    'author': "Tabish Turabi",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.8.3',

    # any module necessary for this one to work correctly
    'depends': ['base','bsg_trip_mgmt'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/data.xml',
        'views/violation_action.xml',
        'views/violation_type.xml',
        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}