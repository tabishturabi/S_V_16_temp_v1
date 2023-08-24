# -*- coding: utf-8 -*-
{
    'name': "bsg_branch_config",

    'summary': """
        Branches Configuration For Bassami Group""",

    'description': """
        Branches Configuration For Bassami Group
    """,

    'author': "bassamitech ",
    'website': "http://www.bassamitech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.1.4',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','hr','account_accountant','stock','contacts','report_xlsx'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/branches.xml',
        'views/region_config_view.xml',
        'views/sponsor_info_view.xml',
        'views/license_info_view.xml',
        'views/branch_classification_view.xml',
        'views/branch_sales_target_view.xml',
        'views/branch_doc_type_view.xml'
    ],
    'license': 'LGPL-3',
}
