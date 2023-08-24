# -*- coding: utf-8 -*-
{
    'name': 'Attendance Permission',
    'description': """
    
Attendance Employee Permission
=================
- Permission allowance
- Permission request
    """,
    'category': 'hr',
    'sequence': 32,
    'version': '12.5.5',
    'depends': ['base', 'hr_attendance_zktecho',],
    'data': [
        # security
        'security/security.xml',
        'security/ir.model.access.csv',
        # data
        'data/ir.cron.xml',
        # views
        'views/permission_type_views.xml',
        'views/permission_request_views.xml',
        'views/hr_attendance_views.xml',

    ],
    'demo': [
    ],
    'qweb': [
    ],
    'license': 'OEEL-1',
    'auto_install': False,
    'installable': True,

}
