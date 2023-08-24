# -*- coding: utf-8 -*-
{
    'name': "Employee Leave Request Extend",

    'summary': """HR Leave Request duration with decimal digits""",

    'description': """
        Adding exception and constraint to leaves model
    """,

    'author': "Tabish Turabi",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_holidays'],

    # always loaded
    'data': [
        # 'views/hr_leave_request.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
