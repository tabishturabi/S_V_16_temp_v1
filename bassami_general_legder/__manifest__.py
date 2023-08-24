{
    'name': "bassami_general_legder",
    'description': "bassami_general_legder",
    'author': 'SolutionFounder',
    'website': "http://www.solutionfounder.com",
    'category': 'account',
    'version': '12.0.9',
    'application': True,
    'depends': ['base', 'account', 'account_reports','payments_enhanced'],
    'data': [
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
}
