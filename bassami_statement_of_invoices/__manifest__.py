{
    'name': "bassami_statement_of_invoices",
    'description': "bassami_statement_of_invoices",
    'author': 'bassamitech',
    'website': "http://www.bassamitech.com",
    'category': 'account',
    'version': '10.0.10',
    'application': True,
    'depends': ['base', 'account', 'account_reports'],
    'data': [
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
}