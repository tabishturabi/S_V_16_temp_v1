{
    'name': "bx_sales_report",
    'description': "bx_sales_report",
    'author': 'SolutionFounder',
    'website': "http://www.solutionfounder.com",
    'category': 'sale',
    'version': '12.0.2.2',
    'depends': ['report_xlsx','bsg_branch_config','bsg_cargo_sale','transport_management'],
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'template.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
    
