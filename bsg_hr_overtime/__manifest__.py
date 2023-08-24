# -*- coding: utf-8 -*-
{
    'name': "Employee Overtime Request",

    'summary': """
      Bassami Employee OverTime Request""",

    'description': """
        Bassami Employee Overtime Request
    """,

    'author': "Albassamitransport",
    'website': "www.albassamitransport.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HR',
    'version': '12.1.42',

    # any module necessary for this one to work correctly
    'depends': ['base','bsg_hr','hr','bsg_hr_payroll','account','bsg_employee_salary_info'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/record_rule.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/sequence.xml',
        'wizard/hr_overtime_register_payment.xml',
        'wizard/hr_overtime_move_post.xml',
        'wizard/hr_overtime_refuse_reason_views.xml',
        'wizard/wiz_import_overtime_hour_lines.xml',
        'views/my_overtime_request.xml',
        'views/payslip_config.xml',
        'views/multi_emps_overtime_request.xml',
        'views/multi_emps_overtime_request_by_hours.xml',
        'views/res_config_settings_views.xml',
        'wizard/overtime_detailed_report_wizard_view.xml',
        'report/hr_overtime_details_report_template.xml',
        'report/overtime_report_action.xml',
        'data/ir_attachment.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
