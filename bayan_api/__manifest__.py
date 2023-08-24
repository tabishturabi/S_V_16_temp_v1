{
    "name": "Odoo Bayan API",
    "version": "12.13.54",
    "category": "API",
    "description": """ Odoo Bayan API For Odoo
With use of this module user can enable REST API in Odoo for Bayan platform

""",
    "depends": ["base","bsg_trip_mgmt", "bsg_hr", "bsg_master_config","transport_management",'government_sale'],
    "data": [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/bayan_form.xml',
        # 'views/hr_iqama.xml',
        # 'views/bsg_route_waypoint.xml',
        # 'views/bsg_car_size.xml',
        # 'views/fleet_vehicle.xml',
        'views/fleet_vehicle_trip.xml',
        # 'views/region_config.xml',
        'views/configurations.xml',
        'wizard/bayan_trip_details_wizard.xml',
        'wizard/wizard_close_waybill.xml',
        'wizard/wizard_cancel_waybill.xml',
        'views/bsg_cargo_sale_line.xml',
        'views/bayan_config_settings.xml',
        'views/transport_management.xml',
        # 'views/cancel_status_reasons.xml'
    ],
    "installable": True,
    "auto_install": False,
}
