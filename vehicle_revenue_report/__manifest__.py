{
    'name': "vehicle_revenue_report",
    'description': "vehicle_revenue_report",
    'author': 'bassamitech',
    'website': "http://www.bassamitech.com",
    'category': 'account',
    'version': '12.0.30',
    'application': True,
    'depends': ['base','bsg_trip_mgmt'],
    'data': [
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
}
