# -*- coding: utf-8 -*-
{
    'name': "Sim Card Reports",

    'summary': """Sim Card Reports""",

    'description': """Sim Card Reports""",

    'author': "Tabish Turabi",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.14',

    # any module necessary for this one to work correctly
    'depends': ['base','report_xlsx','sim_card'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/views.xml',
        'views/sim_card_report.xml',
    ],
}
