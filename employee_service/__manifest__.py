# -*- coding: utf-8 -*-
{
    'name': "Employee Service",
    'summary': """
    Employee Service
    """,
    'description': """
    Employee Service
    """,
    'author': "Al-Bassami || Rai Muhammad Kashif ",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '12.0.81',
    'depends': ['base', 'bsg_hr', 'bsg_branch_config','account_accountant','hr_payroll','fleet','sim_card','bsg_employee_salary_info','hr_holidays','employee_human_resource'],
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        'wizard/refuse.xml',
        'report/report.xml',
        'views/service.xml',
        'views/config.xml',
        'views/sequence.xml',
        'views/ext_employee.xml',
        'views/settings.xml',
        'views/termination.xml',
        'data/data.xml',
        'data/ir_attachment.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
