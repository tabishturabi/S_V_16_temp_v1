# -*- coding: utf-8 -*-
{
    'name': "Bsg Warehouse Restrictions",

    'summary': """
        Add Restruction For Warehouse / Locations / Picking / Products """,

    'description': """
        -This Restruct Related To User Restriction Group. 
        -User Can Access Just Warehouse Specified in his Profile.
        -User Can Access Just Locations Specified in his Profile, If Not Specify Will Take Location Of Warehouse.
        -User Can Access Just Stock Picking Specified in his Profile, If Not Specify Will Take Picking Of Warehouse.
        -User Can Access Just Products/Product Template  Specified in his Profile, If Not Specify Will Take Products In  His access Location.
        -Product On Hand Quantity Will Compute Just From User Locations Of His Current Warehouse.
    """,

    'author': "Albassami",
    'website': "http://www.Albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '12.47',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock','purchase_enhanced'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'security/stock_security.xml',
        'templates/assets.xml',
    ],
    # 'qweb': [
    #     'static/src/xml/switch_warehouse.xml'
    # ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    # 'assets': {
    #         'web.assets_backend': [
    #             'bsg_warehouse_restrictions/static/src/**/*',
    #         ],
    #     }
}
