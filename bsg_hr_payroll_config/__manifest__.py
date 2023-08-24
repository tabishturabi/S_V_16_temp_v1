# -*- coding: utf-8 -*-
{
    'name': "Employee Payroll Config",
    'summary': """
      Albassami Employee Payroll Configuration""",
    'description': """
        Albassami Employee Payroll Configuration
    """,
    'author': "Albassami",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.14',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/failed_logs_file.xml',
        'wizards/view_import_inputs.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ]
}
