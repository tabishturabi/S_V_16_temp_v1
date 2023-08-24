# -*- coding: utf-8 -*-
{
    'name': "bsg_trip_mgmt",

    'summary': """
        Trip Management of Bassami Group""",

    'description': """
        Trip Management of Bassami Group
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'fleet',
    'version': '12.6.62',
    # any module necessary for this one to work correctly
    'depends': ['base','survey','account','report_xlsx','account_generic_enhanced','bsg_master_config','fleet','bsg_cargo_sale','bsg_fleet_operations','hr','sol_import_excel_csv','hr_maintenance'],

    # Migration Note Once transport management will be migrated to v16 then this access will be added in csv of this module
    # access_transport_management_fleet_user,transport_management_fleet_user,transport_management.model_transport_management,fleet.fleet_group_user,1,0,0,0

    # always loaded
    'data': [
        'data/survey_question.xml',
        'data/data.xml',
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'report/dispatch_report.xml',
        'report/trip_arrival_report.xml',
        'views/account_invoice_inherit.xml',
        'views/trip_view.xml',
        'views/config.xml',
        'views/suvey_inherit.xml',
        'views/fleet_vehicle_odometer_view.xml',
        'views/sequence.xml',
        'wizard/calculate_value_view.xml',
        'views/cargo_sale_view.xml',
        'views/bsg_route_waypoints.xml',
        'views/hr_employee_inherit_view.xml',
        'views/survey_question_config_view.xml',
        'views/driver_reward_by_delivery_config_view.xml',
        'views/driver_reqard_by_revenue_config_view.xml',
        'views/fleet_trio_arriavla_form.xml',
        'views/fine_for_late_arrival_view.xml',
        'views/safety_of_load_view.xml',
        'views/fleet_vehicle_fuel_log.xml',
        # 'views/menu.xml',
        'views/product_product_inherits_view.xml',
        'report/vehicle_performance_report.xml',
        'wizard/vehicle_performance_report_wizard.xml',
    ],
}
