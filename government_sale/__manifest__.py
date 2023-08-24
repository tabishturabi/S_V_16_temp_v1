# -*- coding: utf-8 -*-
{
    'name': 'Government Sale',
    'version': '12.1.34',
    'summary': 'Add new menu after Cargo Sale Line with name "Government Sale"',
    'description': """Government_sale Add a new boolean in transport.managment field_name : is_government default set it to True""",
    'author': 'tabish',
    'website': 'https://www.albassami.com',
    'depends': ['base','transport_management','bsg_tranport_bx_credit_customer_collection','bsg_trip_mgmt'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/view.xml',
        'views/partner_type.xml',
        'views/bsg_customer_contract_line.xml',
        'views/bsg_route_waypoints.xml',
        'views/bsg_car_size.xml',
        'views/product_template.xml',
        'views/gov_cc.xml',
        'views/trips.xml',
        'report/report.xml',
    ],
}
