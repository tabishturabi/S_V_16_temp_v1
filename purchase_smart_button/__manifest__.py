# -*- coding: utf-8 -*-
{
    'name': "Purchase Smart Button",

    'summary': """To Add Smart Buttom In PO Line For Count Of Previous Orders""",

    'description': """
        To Add Smart Buttom In PO Line For Count Of Previous Orders
    """,

    'author': "Albassami",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase_enhanced'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'wizard/warehouse_onhand_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}