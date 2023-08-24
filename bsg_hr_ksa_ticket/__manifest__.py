# -*- coding: utf-8 -*-
{
    'name': "Albassami HR KSA Ticketing Costom",

    'summary': """
        A module to manage hr employee ticketing""",

    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Human Resources',
    'version': '12.31.38',

    # any module necessary for this one to work correctly
    'depends': ['hr','hr_payroll','account','bsg_hr','loan','employee_human_resource'],

    # always loaded
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        'data/seq.xml',
        'data/salary_rule.xml',
        'wizard/reject.xml',
        'views/views.xml',

    ],
}
