{
    'name': "bassami_fleet_trip_report",
    'description': "bassami_fleet_trip_report",
    'author': 'bassamitech',
    'website': "http://www.bassamitech.com",
    'category': 'fleet',
    'version': '12.0.46',
    'application': True,
    'depends': ['base', 'fleet','bsg_trip_mgmt'],
    'data': [
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
}
