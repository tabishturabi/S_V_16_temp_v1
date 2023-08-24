# -*- coding: utf-8 -*-
{
    'name': "Employee Sallary Summary Report",

    'summary': """
      Bassami Employee Sallary Summary Report""",

    'description': """
        Bassami Employee Sallary Summary Report
    """,

    'author': "Arshad Khalil",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.5',

    # any module necessary for this one to work correctly
    'depends': ['base','report_xlsx','bsg_hr','employee_info_report'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'reports/salary_sumary_report_excel.xml',
        'reports/salary_sumary_report_pdf.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
'post_init_hook': 'post_init_hook',
}
