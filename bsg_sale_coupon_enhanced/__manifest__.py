# -*- coding: utf-8 -*-
{
    'name': "Cargo Coupon And Promotion",

    'summary': """
        For Use Coupon And Promotion In Cargo Order""",

    'description': """
        - Apply Coupon In Cargo Order , Need  Apply Coupon/Promotion Access Group
        - Remove Applied Coupon From Order , Need  Remove Coupon/Promotion Access Group
        - Update Applied Coupon , Need  Update Coupon/Promotion Access Group
        - Can Specify Cargo Criteria For Apply Coupon/Promotion:
           1- By Specific Payment Method.
           2- By Specific Locations From.
           3- By Specific Locations To.
           4- By Specific Shipment Types.
           5- By Specific Partner Types.
           6- By Specific Agreement Types.

    """,

    'author': "Al-Bassami",
    'website': "https://albassami.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.7',

    # any module necessary for this one to work correctly
    'depends': ['sale_loyalty','portal_sales'],

    # always loaded
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/views.xml',
        'views/coupon_portal.xml',
        'wizard/message_wizard.xml',
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         '/bsg_sale_coupon_enhanced/static/src/js/bassami_coupon.js',
    #     ],
    # },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
