# -*- coding: utf-8 -*-
{
    'name': "Maintenance Enhance",

    'summary': """
    maintenance_enhance
    """,

    'description': """
    maintenance_enhance
    """,
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '12.2.103',
    'depends': ['base','purchase_enhanced','fleet','bsg_fleet_operations'],
    'data': [
        'data/ir_sequence.xml',
        'data/data.xml',
        'data/ir_cron.xml',
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'report/workshop_service_report_templates.xml',
        'views/menus.xml',
        'views/entry_permission.xml',
        'views/workshop_name.xml',
        'views/services.xml',
        'views/maintenance_req_enh.xml',
        'views/fleet_vehicle_status.xml',
        'views/technician_tasks.xml',
        'views/inspections.xml',
        'views/user_base_access.xml',
        'views/fleet_vehicle.xml',
        'views/fleet_trailer.xml',
        'views/notification_user.xml',

    ],
    'demo': [
        'demo/demo.xml',
    ],
}
