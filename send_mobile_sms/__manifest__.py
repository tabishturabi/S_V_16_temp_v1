# -*- coding: utf-8 -*-
{
    'name': "Send Mobile Sms",

    'summary': """
        SENDING SMS""",

    'description': """
        SENDING SMS
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.4',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/api_auth_setting_view.xml',
        'views/send_sms_view.xml',
        'views/ir_actions_server_views.xml',
        'views/sms_track_view.xml',
        'wizard/sms_compose_view.xml',
        'views/views.xml',
    ],
}