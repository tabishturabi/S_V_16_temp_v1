
# -*- coding: utf-8 -*-

{
    "name": "Sales Dashboard",
    "summary": "Sale Dashboard",
    "version": "12.0.31",
    "description": """Sale Dashboard""",
    "author": "Tabish Turabi",
    "website": "http://www.albassami.com",
    "category": "Sales",
    "depends": [
        "sale_management","bsg_branch_config",'bsg_cargo_sale','maintenance_enhance'],
    "data": [
        "views/sale_dashboard_view.xml",
        "views/map_operation.xml",
        "views/assets.xml"
    ],
    # "qweb": [
    #     "static/src/xml/*.xml",
    # ],
    # 'assets': {
    #         # 'web.assets_common': [
    #         'web.assets_backend': [
    #             'sales_dashboard/static/src/xml/*.xml',
    #             'sales_dashboard/static/src/css/sale_dashboard.css',
    #             'sales_dashboard/static/src/js/sale_dashboard.js',
    #             'sales_dashboard/static/src/js/map_operation.js',
    #             'sales_dashboard/static/src/lib/plotly/plotly-latest.min.js',
    #             'x-special/nautilus-clipboard copy file:///home/jazzi/Downloads/saudi-arabia.svg',
    #         ],
    # },
    "installable": True,
    "application": True,

}
