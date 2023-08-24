# -*- coding: utf-8 -*-
{
    'name': "Warehouse Multi Deliver",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Albassami",
    'website': "http://www.Albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'purchase',
    'version': '1.14',

    # any module necessary for this one to work correctly
    'depends': ['purchase_enhanced'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template_view.xml',
        'wizard/create_rfq_views.xml',
        'views/deliver_to_line.xml',
        'views/res_config_settings_views.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
