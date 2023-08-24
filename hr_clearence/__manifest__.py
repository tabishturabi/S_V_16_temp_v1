# -*- coding: utf-8 -*-
{
    'name': "HR Clearance",

    'summary': """
        A module to manage hr employee Clearance""",

    'description': """
        A module to manage hr employee Clearance
    """,
    'author': "Albassami",
    'website': "http://www.albassami.com",
    'category': 'Human Resources',
    'version': '12.40',

    # any module necessary for this one to work correctly
    'depends': ['hr','bsg_hr','mail','hr_holidays','employee_human_resource','employee_service','bsg_fleet_operations'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        'wizards/reason_to_refuse_or_cancel.xml',
        'views/views.xml',
        'views/hr_leave.xml',
        'views/hr_termination.xml',
    ],
}
