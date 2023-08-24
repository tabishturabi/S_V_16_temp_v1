# -*- coding: utf-8 -*-
{
    'name': "Trailer Managment",

    'summary': """
        Module for fleet operation and trailer management""",

    'description': """
        Module for fleet operation and trailer management varity of things
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.32',
    # any module necessary for this one to work correctly
    'depends': ['base','portal','fleet','hr','hr_contract','hr_payroll','hr_recruitment','mail','bsg_master_config','bsg_cargo_sale','report_xlsx'],

    # Migration Note Once transport management will be migrated to v16 then this access will be added in csv of this module

# access_transport_management_fleet_manager,transport_management_fleet_manager,transport_management.model_transport_management,fleet.fleet_group_manager,1,0,0,0
# access_transport_management_fleet_manager2,transport_management_fleet_manager2,transport_management.model_transport_management,fleet.fleet_group_manager,1,0,0,0

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'cron/cron_jobs.xml',
        'report/driver_assign_report.xml',
        'report/driver_unassign_report.xml',
        'report/driver_info_report_xlsx.xml',
        'views/fleet_view.xml',
        'views/hr_employee_view.xml',
        'views/trailer_config.xml',
        'views/trailer_type_view.xml',
        'views/trailer_cat_view.xml',
        'views/service_logs_view.xml',
        'views/driver_history_view.xml',
        'views/asset_group_view.xml',
        'views/asset_status_view.xml',
        'views/int_fuel_amt_view.xml',
        'views/port_fuel_amt_view.xml',
        'views/fuel_expense_method_view.xml',
        'views/vehicle_group_view.xml',
        'views/vehicle_type_table_view.xml',
        'views/vehicle_status_view.xml',
        'views/driver_assign_view.xml',
        'views/driver_unassign_view.xml',
        'views/fleet_tracking_config_view.xml',
        'views/document_type_view.xml',
        'views/renewal_vehicle_document_view.xml',
        'views/asset_location_view.xml',
        'views/menu.xml',
        'views/release_trailer_wizard.xml',
        'views/add_trailer_wizard.xml',
        'views/driver_information_view.xml',
        'wizards/driver_info_report_wiz.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
