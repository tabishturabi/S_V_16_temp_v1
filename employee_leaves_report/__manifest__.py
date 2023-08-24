# -*- coding: utf-8 -*-
{
    'name': "Employee Annual Leaves Report",

    'summary': """
        Dynamic report to fetch data regarding annual leaves for one or more employees""",

    'description': """
        In Leaves/Reporting/Employee Annual Report a wizard popup is opened with all input values to filter data as per user input
    """,

    'author': "Tabish Turabi || Al-Bassami ",
    'website': "http://www.albasssami.com",
    'category': 'Uncategorized',
    'version': '0.1.0.3',
    'depends': ['report_xlsx','bsg_hr','hr_holidays'],
    'data': [
        'views/employee_leaves_report.xml',
        'views/views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}