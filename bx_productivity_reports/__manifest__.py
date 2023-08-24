# -*- coding: utf-8 -*-
{
    'name': "bx_productivity_reports",

    'summary': """
        bx_productivity_reports""",

    'description': """
        bx_productivity_reports module's purpose
    """,

    'author': "Al-Bassami || Rai Muhammad Kashif ",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1.0.2',
    'depends': ['report_xlsx','bsg_branch_config','bsg_cargo_sale','transport_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/report.xml',
        'views/bx_productivity_reports.xml',
        'security/access_security.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}