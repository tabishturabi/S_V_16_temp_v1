# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Solution founder IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Credit Customer Invoice",
    'summary': """
        
     """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",
    'category': 'Accounting',

    'version': '12.0.87',

    'depends': ['web','bsg_hr','bsg_customer_contract','bsg_cargo_sale','account','payments_enhanced','bsg_tranport_bx_credit_customer_collection'],
    'data': [
        'data/ir_sequnce.xml',
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'views/credit_customer_invoice_view.xml',
        'views/account_journal_inherit_view.xml',
        'views/bsg_vehicle_cargo_sale_line_inherit_view.xml',
        'views/bsg_vehicle_cargo_sale_inherit_view.xml',
        'report/template.xml',
        'report_xlsx/template.xml',
        'report/module_report.xml',
    ],
    'demo': [
    ],
}
