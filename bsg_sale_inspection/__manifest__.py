# -*- coding: utf-8 -*-
{
    'name': 'Sale Inspection',
    'description': """
Sale Line Inspection Wizard
===========================
    """,
    'category': 'Sales',
    'sequence': 32,
    'version': '12.0.12',
    'depends': ["bsg_cargo_sale", "hr", "bsg_hr_payroll"],
    'data': [
        # security
        'security/security.xml',
        'security/ir.model.access.csv',
        # data
        # wizard
        'wizard/add_inspection_wizard_views.xml',
        # views
        'views/sale_line_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'license': 'OEEL-1',
    'auto_install': False,
}
