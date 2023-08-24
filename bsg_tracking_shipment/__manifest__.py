# -*- coding: utf-8 -*-
{
    'name' : 'Bsg Tracking Shipment',
    'version' : '12.0.46',
    'summary': 'Tracking Shipment',
    'description': """Tracking Shipment""",
    'category': 'Sale',
    'website': 'www.solutionfounder.com',
    'depends' : ['base','sale_management','website', 'payment_payfort', 'auth_signup','portal_sales'],
    'data': [
        'views/assest.xml',
        'views/track_shipment_view.xml',
        'views/website_config_settings.xml',
        ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
