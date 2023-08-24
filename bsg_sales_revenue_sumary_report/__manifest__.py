# -*- coding: utf-8 -*-
{
    'name': "Sales Revenue Summary Reports",

    'summary': """
      Bassami Sales Revenue Summary Reports""",

    'description': """
        Bassami Sales Revenue Summary Reports
    """,

    'author': "Arshad Khalil",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.10',

    # any module necessary for this one to work correctly
    'depends': ['base','report_xlsx','bsg_cargo_sale','bsg_hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'reports/sales_revenue_summary_report_excel.xml',
        'reports/sales_revenue_summary_report_pdf.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
'post_init_hook': 'post_init_hook',
}
