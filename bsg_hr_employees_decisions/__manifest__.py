# -*- coding: utf-8 -*-
{
    'name': "Employees Decisions",

    'summary': """
      Bassami Employees Decisions""",

    'description': """
        Bassami Employees Decisions
    """,

    'author': "Albassami",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.70',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','bsg_hr','bsg_hr_payroll','analytic','bsg_branch_config','mail','bsg_employee_bonus_classification'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/record_rule.xml',
        'security/ir.model.access.csv',
        'reports/employee_appointment_report_pdf.xml',
        'data/mail_template.xml',
        'data/sequence.xml',
        'views/menu.xml',
        'wizards/refuse_employee_decisions_reasons.xml',
        'wizards/emp_decisions_reports_wizards.xml',
        'views/decision_report_comment.xml',
        'views/views.xml',
        'views/templates.xml',
        'data/ir_attachment.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
