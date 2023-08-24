# -*- coding: utf-8 -*-
{
    'name': "BX Credit Customer Collection",
    'summary': """
        BX Credit Customer Collection
    """,
    'author': "bassamitech",
    'website': "http://www.bassamitech.com",
    'category': 'Accounting',
    'version': '12.0.49',
    'depends': ['web','transport_management','bsg_cargo_sale','account','payments_enhanced'],
    'data': [
        'data/ir_sequnce.xml',
        'data/data.xml',
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'views/bx_credit_customer_invoice_view.xml',
        'views/account_journal_inherit_view.xml',
        'views/transport_management_line_inherit_view.xml',
        'report/template.xml',
        'report_xlsx/template.xml',
        'report/module_report.xml',
        'report/bx_certificate_of_achievement_report_pdf.xml',
        'report/bx_claim_report_pdf.xml',
        'report/bx_summary_collection_invoice_report_pdf.xml',
    ],
    'demo': [
    ],
}
