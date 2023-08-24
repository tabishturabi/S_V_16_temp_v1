# -*- coding: utf-8 -*-
{
    'name': "bsg_hr",

    'summary': """
        Hr Module For Bassami """,

    'description': """
        Hr Module For Bassami
    """,

    'author': "ALbassami-Group",
    'website': "http://www.albassamitransport.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '12.1.173',

    # any module necessary for this one to work correctly
    'depends': ['report_xlsx','base','hr','bsg_branch_config','bsg_fleet_operations','hr_payroll','timesheet_grid','account','hr_holidays','hr_payroll_account','bsg_hr_payroll'],

    # always loaded
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        'data/data.xml',
        'wizards/reject_leave_reason.xml',
        'views/bsg_menu.xml',
        'views/hr_employee_view.xml',
        'views/hr_iqama_view.xml',
        'views/hr_passport_view.xml',
        'views/hr_employee_religion.xml',
        'views/hr_doc_type.xml',
        'views/hr_insurance_view.xml',
        'views/hr_asset_type.xml',
        'views/hr_employee_access.xml',
        'views/hr_education_type.xml',
        'views/hr_access_type.xml',
        'views/hr_nationality_detail.xml',
        'views/hr_id_type.xml',
        'views/hr_employee_banks_config.xml',
        'views/hr_employee_banks.xml',
        'views/hr_state_view.xml',
        'views/hr_contract.xml',
        'views/hr_leave_type.xml',
        'views/hr_leave.xml',
        'views/hr_department.xml',
        'views/menu_inherits_views.xml',
        'views/hr_leave_config.xml',
        'views/hr_salary_rule.xml',
        'views/extend_trial_period.xml',


        # 'views/hr_empdoc_type.xml'
    ],
    # only loaded in demonstration mode
    # 'assets': {
    #     'web.assets_backend': [
    #         'bsg_hr/static/src/js/disable_archive.js',
    #         'bsg_hr/static/src/css/form_buton_box.css',
    #     ]
    # },

    'demo': [
        'demo/demo.xml',
    ],
}
