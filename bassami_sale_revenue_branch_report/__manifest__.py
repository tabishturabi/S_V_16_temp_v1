{
    'name': "bassami_sales_revenue_report_by_branch",
    'description': "bassami_sales_revenue_report_by_branch",
    'author': 'SolutionFounder',
    'website': "http://www.solutionfounder.com",
    'category': 'sale',
    'version': '12.6.36',
    'application': True,
    'depends': ['base','web', 'bsg_cargo_sale'],
    'data': [
        'security/ir.model.access.csv',
        'template.xml',
        'views/sales_revenue_by_branch.xml',
    ],
}