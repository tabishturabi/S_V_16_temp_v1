# -*- coding: utf-8 -*-
{
    'name': "Transport Management",
    'version': '12.1.22',
    'summary': """it will handle the transport management work""",
    'description': """it will handle the transport management work""",
    'category': 'Custom',
    'author': 'Solution Founder Team',
    'company': 'Solution Founder (Simplifying IT)',
    'website': "www.bassamitech.com",
    'depends': ['sale','mail', 'account','bsg_cargo_sale','custom_clearance','fleet','bsg_master_config','bsg_trip_mgmt','bsg_vehicle_type_domain','contract_enhanced','base'],
    'data': [
        'data/data.xml',
        'data/cron_bx_delete.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
#         'report/dispatch_report.xml',
#         'report/trip_arrival_report.xml',
        'views/views.xml',
        'views/config.xml',
        'views/account_payment_view.xml',
        'views/account_invocie_inherit_view.xml',
        'views/ext_fleet_vehicle_odometer_view.xml',
        'wizard/traport_cancel_wizard_view.xml',
        # MIgration Note
        # 'templates/assets.xml'
            ],
    'demo': [],
    # 'assets': {
    #     'web.assets_backend': [
    #         'transport_management/static/src/**/*',
    #     ],
    # },

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
