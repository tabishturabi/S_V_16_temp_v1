# -*- coding: utf-8 -*-
{
    'name': "Employee Salary Information",

    'summary': """
      Bassami Employee Salary Information""",

    'description': """
        Bassami Employee Salary Information
    """,

    'author': "Albassami",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',

    'version': '0.0.0.40',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll', 'bsg_hr'],

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