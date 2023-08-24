{
    'name': "bx_information_report",
    'description': "bx_information_report",
    'author': 'SolutionFounder',
    'website': "http://www.solutionfounder.com",
    'category': 'sale',
    'version': '12.0.1.28',
    'application': True,
    'depends': ['base','report_xlsx','bsg_branch_config','bsg_cargo_sale','transport_management'],
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'template.xml',
    ],
    
}