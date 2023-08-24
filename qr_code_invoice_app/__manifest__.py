# -*- coding: utf-8 -*-
{
    'name': 'QR Code Invoice App',
    'version': '2.12',
    'category': 'Accounting',
    'author': 'Zain-Alabdin',
    'summary': 'Generate QR Code for Invoice',
    'website': 'https://www.albassami.com',
    'description': """
    -Configuration For Qr Code Type (Url,Text Information)
    -For Url It Will Open Invoice In Portal.
    -For Text Information , You Must Specify Invoice Field's To Show.
    -Add Qr Code In Invoice Form View.
    -Add Qr Code In Invoice Report.
    """,
    # Migration Note
    # access_invoice_qr_fields,access.invoice.qr.fields,model_invoice_qr_fields,,1,1,1,1
    'depends': [
        'account',
        'bassami_customer_invoices',
        'partner_autocomplete',
        'backend_frontend_font',
        'bsg_corporate_invoice_contract'
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/template.xml',
        'views/base_model_trans.xml',
        'views/qr_code_invoice_view.xml',
        'report/invoice_report.xml',
        'report/tax_invoice_report_template.xml',
        #'report/account_invoice_report_template.xml',
    ],
    'images': [
        'static/description/banner.jpg',
    ],
    # 'assets': {
    #         'web.report_assets_common': [
    #             'qr_code_invoice_app/static/css/font.css',
    #         ],
    #     },
    'css': [
    'static/css/font.css',
    ],
    'installable': True,
    'application': True,
    'license': "AGPL-3",
}
