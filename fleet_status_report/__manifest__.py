# -*- coding: utf-8 -*-
{
    'name': "Fleet Status Report",

    'summary': """
        Fleet Info""",

    'description': """
        Fleet Info
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.0.21',

    # any module necessary for this one to work correctly
    'depends': ['base','bsg_branch_config','fleet','bsg_cargo_sale','bsg_trip_mgmt'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/cron.xml',
        'views/views.xml',
        'views/fleet_report.xml',
        'report_xlsx/template.xml',
    ],
}