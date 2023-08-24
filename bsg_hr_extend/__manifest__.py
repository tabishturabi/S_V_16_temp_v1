# -*- coding: utf-8 -*-
{
    'name': "bsg_hr_extend",

    'summary': """
        Hr Extend Module For Bassami """,

    'description': """
        Hr Extend Module For Bassami
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '12.0.3',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','bsg_hr_payroll','bsg_branch_config','bsg_fleet_operations','hr_payroll'],

    # always loaded
    'data': [
        'views/hr_iqama_view.xml',
        'views/hr_passport_view.xml',
        'views/hr_insurance_view.xml',
        'views/hr_nationality_detail.xml',
        'views/hr_employee_banks.xml'
    ],
}
