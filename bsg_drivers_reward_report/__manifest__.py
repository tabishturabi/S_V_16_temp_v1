{
    'name': "bsg_drivers_reward_report",
    'description': "bsg_drivers_reward_report",
    'author': 'bassamitech',
    'website': "http://www.bassamitech.com",
    'category': 'sale',
    'version': '12.0.44',
    'application': True,
    'depends': ['base', 'bsg_trip_mgmt'],
    'data': [
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
}