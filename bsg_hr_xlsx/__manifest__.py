# -*- coding: utf-8 -*-

{
    'name': 'Bassami Hr Payslip Xls',
    'version': '3.6',
    'category': 'HR',
    'summary': 'Bassami HR Payroll',
    'author': "Muhammad Yousef",
    'description': """
        Bassami HR Contract
    """,
    'depends': ['bsg_hr_payroll', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/hr_payslip_xls_wizard_view.xml'
    ],
    'qweb': [],
    'application': True,
}
