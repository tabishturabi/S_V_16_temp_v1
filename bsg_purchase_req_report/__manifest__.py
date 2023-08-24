# -*- coding: utf-8 -*-
{
    'name': "Purchase Request Report",

    'summary': """
      Bassami Purchase Request Report""",

    'description': """
        Purchase Request Report
    """,

    'author': "Arshad Khalil",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.13',

    # any module necessary for this one to work correctly
    'depends': ['base','report_xlsx','purchase','bsg_branch_config'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'reports/purchase_req_report_excel.xml',
        'reports/purchase_req_report_pdf.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
'post_init_hook': 'post_init_hook',
}
