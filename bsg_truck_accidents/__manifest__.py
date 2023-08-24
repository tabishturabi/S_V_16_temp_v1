# -*- coding: utf-8 -*-

{
    'name': "Bsg Truck Accidents",
    'summary': """
        Bsg Truck Accidents
    """,
    'description': """
        Bsg Truck Accidents of Bassami
    """,
    'author': "bassamitech",
    'website': "http://www.bassamitech.com",
    'category': '',
    'version': '12.1.114',
    'depends': ['base','account','fleet','bsg_fleet_operations','bsg_trip_mgmt','bsg_corporate_invoice_contract','purchase_enhanced'],
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'wizard/refuse.xml',
        'views/bsg_truck_accident_view.xml',
        'views/bsg_companies_claims.xml',
        'views/bsg_individual_claims.xml',
        'views/configuration.xml',
        'views/accident_attachment.xml',
        'views/ir_attachment.xml',
        'data/sequence.xml',
        'views/account_invoice.xml',
        'views/claims_account_config.xml',
        'views/car_places_config.xml',
        'views/bta_clear_car_claim.xml',
        'views/bta_shaamil_claim.xml',
        'views/bta_third_party_claim.xml',
        'views/ir_actions_server.xml',
        'report/case_proof_report.xml',
        'report/damage_preview_report.xml',
        'wizard/driver_deduction_report.xml',
        'wizard/claims_report.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
