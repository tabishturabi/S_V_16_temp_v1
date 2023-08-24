# -*- coding: utf-8 -*-
{
    'name': "Vehicle Documents Report",

    'summary': """
      Bassami Vehicle Documents Report""",

    'description': """
        Bassami Vehicle Documents Report
    """,

    'author': "Arshad Khalil",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.35',

    # any module necessary for this one to work correctly
    'depends': ['base','bsg_trip_mgmt','report_xlsx','bsg_fleet_operations','bsg_master_config','bsg_vehicle_type_domain'],
    # always loaded bsg_vehicle_type_domain
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'reports/vehicle_document_report_excel.xml',
        'reports/vehicle_document_report_pdf.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/ext_res_config_settings.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
'post_init_hook': 'post_init_hook',
}
