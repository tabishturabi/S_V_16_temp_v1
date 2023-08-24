# -*- coding: utf-8 -*-
{
    'name': 'Attendance Reports',
    'description': """
    
Attendance Reports
=================
    """,
    'category': 'hr',
    'sequence': 32,
    'version': '12.5.6',
    'depends': ['base', 'hr_attendance_zktecho', 'hr_attendance_permission'],
    'data': [
        # security
        'security/security.xml',
        'security/ir.model.access.csv',
        # reports
        'reports/reports.xml',
        'reports/attendance_daily_template.xml',
        'reports/attendance_summary_template.xml',
        'reports/employee_permission_report.xml',
        # wizards
        'wizard/hr_attendance_report_wiz_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'license': 'OEEL-1',
    'auto_install': False,
    'installable': True,

}
