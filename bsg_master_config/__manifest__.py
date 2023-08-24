# -*- coding: utf-8 -*-
{
    'name': "bsg_master_config",

    'summary': """
        Master Configuration of Bassami""",

    'description': """
        Master Configuration of Bassami
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',


    'version': '12.0.114',
    # any module necessary for this one to work correctly
    'depends': ['mail','bsg_branch_config','bsg_branches_zone_and_region_and_branch_config'],

    # always loaded
    'data': [
        'data/demurrage_charges_config_data.xml',
        'data/ir_cron_update_price.xml',
        'data/email_template.xml',
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'views/sequence.xml',
        'views/car_size_view.xml',
        'views/car_make_view.xml',
        'views/car_config_view.xml',
        'views/route_view.xml',
        'views/route_waypoints_view.xml',
        'views/price_config_view.xml',
        'views/plate_config_view.xml',
        'views/vehicle_color_config.xml',
        'views/vehicle_service_type_view.xml',
        'views/car_year_view.xml',
        'views/customer_location_view.xml',
        'views/car_model_view.xml',
        'views/car_classfication_view.xml',
        'views/demurrage_charges.xml',
        'views/discount_on_cargo.xml',
        'views/estimated_delivery_days.xml',
        'views/single_trip_cancel_view.xml',
        'views/round_trip_cancel_view.xml',
        'views/car_shipment_type_view.xml',
        'views/max_daily_so_per_branch_view.xml',
        'views/config.xml',
        'views/trucks_dedicating_area.xml',
        'views/menu.xml',
        'views/app_config_view.xml',
        'views/type_config_view.xml',
        'views/branch_distance_view.xml',
        'views/product_product_inherits_view.xml',
        'views/warning_and_error_view.xml',
        'views/customer_contract_notifi_view.xml',
        'views/bayan_plate_type_config.xml',
        'views/cancel_status_reason.xml',
    ],
    'license': 'LGPL-3',
}
