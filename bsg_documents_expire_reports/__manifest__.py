# -*- coding: utf-8 -*-
{
    'name': "Documents Expire Notification Reports",

    'summary': """
      Bassami Documents Expire Notification Reports""",

    'description': """
        Bassami Documents Expire Notification Reports
    """,

    'author': "Arshad Khalil",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.37',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','bsg_hr','employee_info_report','bsg_branch_config'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'reports/employee_iqama_report_excel.xml',
        'reports/employee_iqama_report_pdf.xml',
        'reports/employee_nid_report_excel.xml',
        'reports/employee_nid_report_pdf.xml',
        'reports/employee_passport_report_excel.xml',
        'reports/employee_passport_report_pdf.xml',
        'views/menu.xml',
        'views/employee_iqama_report_wizard.xml',
        'views/employee_national_id_report_wizard.xml',
        'views/employee_passport_report_wizard.xml',
        'views/templates.xml',
        'views/ext_res_config_settings.xml',
        'views/res_config_settings_views.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
