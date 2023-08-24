{
    'name': "Portal Sales",

    'summary': """
       To Create Sale Order From Website
    
       """,

    'description': """
		To Create Sale Order From Website 
    """,

    'author': "Albassami",
    'website': "http://www.albassami.com/",

    'category': 'sale',

    'version': '12.1.27',

    'depends': ['web','bsg_cargo_sale','odoo_multi_companies','payment_payfort','website','crm','payment_tamara','portal'],


    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/config.xml',
        'views/assets.xml',
        'views/account_view.xml',
        'views/edit_create_line_tmp.xml',
        'views/sale_portal_templates.xml',
        'views/moi_inquiries.xml',
        'views/custom_clearance.xml',
        'views/template.xml',
        'views/auth_signup.xml',
        'views/cargo_online_payment.xml',
        'views/get_price_template.xml',
        'views/get_cargo_so_lines.xml',
        'views/contract_users.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    # 'assets': {
    #         'web.assets_frontend': [
    #             'portal_sales/static/src/**/*',
    #             'https://code.jquery.com/jquery-3.2.1.slim.min.js',
    #             'https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js',
    #             'https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js',
    #             'https://cdn.jsdelivr.net/npm/jquery-validation@1.17.0/dist/jquery.validate.js'
    #         ],
    #     },


    'installable': True,
    'application': True,
}
# -*- coding: utf-8 -*-
