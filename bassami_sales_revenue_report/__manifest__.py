{
    'name': "bassami_sales_revenue_report",
    'description': "bassami_sales_revenue_report",
    'author': 'bassamitech',
    'website': "http://www.bassamitech.com",
    'category': 'sale',
    'version': '12.0.2',
    'application': True,
    'depends': ['base', 'bsg_cargo_sale'],
    'data': [
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
}