# -*- coding: utf-8 -*-
{
    'name': "Employee Reports",

    'summary': """
      Bassami Employee Reports""",

    'description': """
        Bassami Employee Reports
    """,

    'author': "Bassami IT Team",
    'website': "http://www.albassami.com",

    'category': 'Human Resources',
    'version': '0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report_xlsx', 'bsg_hr', 'employee_info_report', 'sale'],

    # always loaded
    'data': [
        # security
        'security/ir.model.access.csv',
        'security/groups.xml',

        # reports
        'reports/reports.xml',

        # wizard
        'wizard/employee_directory_report_wizard_views.xml',

        # 'reports/employee_salary_info_report_pdf.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
