# -*- coding: utf-8 -*-
{
    'name': "effective_date_notes",

    'summary': """
    Effective date Notes
    """,

    'description': """
    Effective date Notes
    """,

    'author': "Al-Bassami || Rai Muhammad Kashif ",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '12.88',
    'depends': ['base', 'hr','bsg_hr', 'bsg_branch_config','account_accountant','hr_payroll','fleet','bsg_hr_employees_decisions','bsg_fleet_operations','hr_holidays','loan','employee_service'],
    'data': [
        'security/access_security.xml',
        'security/record_rule.xml',
        'security/ir.model.access.csv',
        'wizard/refuse.xml',
        'views/effect_request.xml',
        # 'views/vacation.xml',
        'views/ext_employee.xml',
        'views/sequence.xml',
        'data/email_submitted_manager.xml',
        'data/email_mng_approve.xml',
        'data/data.xml',
        'data/ir_attachment.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}
