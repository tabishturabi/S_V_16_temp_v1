# -*- coding: utf-8 -*-

{

    'name': 'Hr Deputation Management(Saudi)',
    'version': '16.31',

    'category': 'Human Resources/Employees',

    'author': '',
    'depends': ['base','account','hr', 'base_address_extended','bsg_hr','maintenance','bsg_hr_ksa_ticket'],
    'data': [
        'security/hr_deputation_security.xml',
        'security/ir.model.access.csv',
        'views/sequence.xml',
        'wizard/deputation_summary_wizard.xml',
        'wizard/deputation_register_payment.xml',
        'wizard/refuse.xml',
        'views/deputation_request_view.xml',
        'views/tickiting_view.xml',
        'views/configuration_view.xml',
        'views/basic_deptuation_allownce.xml',
        'views/other_deptuation_allownce.xml',
        'views/deputation_other_allow_type.xml',
        'views/country_groups.xml',


    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
