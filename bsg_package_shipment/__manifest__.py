# -*- coding: utf-8 -*-
{
    'name': "Package Shipment",
    'summary': """
        Package Shipment""",

    'description': """
        Package Shipment
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",
    'category': 'Uncategorized',
    'version': '12.0.11',
    # any module necessary for this one to work correctly
    'depends': ['sale','bsg_cargo_sale','bsg_trip_mgmt','bsg_fleet_operations'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/package_shipment_view.xml',
        
        ]
    
}
