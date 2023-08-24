# -*- coding: utf-8 -*-
{
    'name': "Employee Leave And Service Date",

    'summary': """
      Employee Leave And Service Date""",

    'description': """
        Bassami Employee Leave And Service Date
    """,

    'author': "Albassami",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.1.7',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','bsg_hr_payroll','hr_holidays'],

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
