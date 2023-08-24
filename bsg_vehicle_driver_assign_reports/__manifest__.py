# -*- coding: utf-8 -*-
{
    'name': "Vehicle Driver Assignment Report",

    'summary': """
      Bassami Vehicle Driver Assignment Report""",

    'description': """
        Bassami Vehicle Driver Assignment Report
    """,

    'author': "Arshad Khalil",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Reporting',
    'version': '0.0.0.9',

    # any module necessary for this one to work correctly
    'depends': ['base','bsg_trip_mgmt','report_xlsx','bsg_fleet_operations','bsg_vehicle_type_domain','bsg_master_config'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'reports/vehicle_driver_assign_report_excel.xml',
        'reports/vehicle_driver_assign_report_pdf.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
'post_init_hook': 'post_init_hook',
}
