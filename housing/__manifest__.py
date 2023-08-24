# -*- coding: utf-8 -*-
{
    'name': "housing",

    'summary': """
    Housing Module
    """,

    'description': """
    Housing Module
    """,

    'author': "Al-Bassami || Rai Muhammad Kashif ",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1.0.19',
    'depends': ['base', 'hr', 'bsg_branch_config','account_accountant','hr_payroll','sim_card','fleet'],
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'views/housing.xml',
        'views/exit_housing.xml',
        'views/reason_entry.xml',
        'views/sequence.xml',
        'views/config_settings.xml',
        'views/ext_employee.xml',
        'data/data.xml',
        'report/report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
