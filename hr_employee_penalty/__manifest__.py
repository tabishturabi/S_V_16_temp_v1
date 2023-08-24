# -*- coding: utf-8 -*-
{
    'name': "HR Employee Penalty (Saudi)",

    'summary': """
        A module to manage hr employee penalties""",

    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Human Resources',
    'version': '16.9',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_payroll','mail','employee_service','bsg_hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        'wizards/reason_to_refuse_or_cancel.xml',
        'views/views.xml',
        'data/penalty_data.xml',
    ],
}
