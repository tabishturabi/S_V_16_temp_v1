{
    'name': "budget_reconciliation_report",
    'description': "budget_reconciliation_report",
    'author': 'bassamitech',
    'website': "http://www.bassamitech.com",
    'category': 'account',
    'version': '12.0.04',
    'application': True,
    'depends': ['base', 'account','bsg_branch_config'],
    'data': [
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
}