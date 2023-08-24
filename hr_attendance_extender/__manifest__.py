# -*- coding: utf-8 -*-
{

    'name': 'HR Attendance Extender',
    'summary': """
        It Helps You To Keep  Track of Employee Attendance""",
    'description': """
    Customize Two Modules:
            1- Customize the Basic Resource Management Module By Modifying Working Time and Adding Some properties
            
            2- Customize the Basic HR Attendance Management Module To Follow Working Time 
    """,
    'author': 'Reem ELobeid',
    'version': '1.0',
    'depends':
        [
            'base',
            'mail',
            'resource',
            'hr_attendance',
            'hr_contract',
            'hr_payroll',
        ],
    'external_dependencies': {
        'python': [],
    },

    'data':
        [   # security
            'security/attendance_security.xml',
            'security/ir.model.access.csv',
            # data
            'cron/cron_data.xml',
            'data/attendance_data.xml',
            'data/attendance_sequence.xml',
            # report

            # wizard views
            # 'wizard/generate_attendance_sheet_wizard_views.xml',
            # 'wizard/modify_attendance_record_views.xml',
            # 'wizard/attendance_report_wizard_views.xml',
            # 'wizard/rota_swap_request_wizard.xml',

            # model views
            'views/hr_employee_views.xml',
            'views/hr_contract_views.xml',
            'views/resource_calendar_views.xml',
            'views/hr_attendance_views.xml',
            # 'views/biometric_machine_views.xml',
            'views/attendance_views.xml',
            # 'views/hr_payslip_views.xml',




        ],
    'application': True,
    'sequence': 0,

}
