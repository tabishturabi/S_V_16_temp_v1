# -*- coding: utf-8 -*-
{
    'name': "Employee Payslips Report",

    'summary': """
      Bassami Eployee Payslips Report""",

    'description': """
        Bassami Employee Payslip Report
    """,

    'author': "Arshad Khalil",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.7.17',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','bsg_hr','employee_info_report'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'reports/employee_payslip_report_excel.xml',
        'reports/employee_payslip_report_pdf.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/report_payslip_templates_extend.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
