# -*- coding: utf-8 -*-
{
    'name': "Iqama Renewels",

    'summary': """
      Iqama Renewels""",

    'description': """
        Iqama Renewels
    """,

    'author': "Arshad Khalil",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.36',

    # any module necessary for this one to work correctly
    'depends': ['base','bsg_hr','hr','mail','bsg_fleet_operations','analytic','account','base_customer','bsg_branch_config','payments_enhanced','advance_petty_expense_mgmt'],

    # always loaded
    'data': [
        'views/groups.xml',
        'views/record_rule.xml',
        'security/ir.model.access.csv',
        'wizards/refuse_iqama_renewel_reasons.xml',
        'views/sequence.xml',
        'views/views.xml',
        'views/templates.xml',
        'data/ir_attachment.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
