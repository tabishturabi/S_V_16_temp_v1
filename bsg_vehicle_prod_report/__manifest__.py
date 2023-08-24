{
    'name': "Vehicle Porductivity Control",
    'description': "Vehicle Porductivity Control",
    'author': 'SolutionFounder',
    'website': "http://www.solutionfounder.com",
    'category': 'sale',
    'version': '12.0.22',
    'application': True,
    'depends': ['base', 'bsg_trip_mgmt'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/module_report.xml',
        'wizard/vehcile_prod_report_wiz.xml'

        # 'views/module_report.xml',
    ],
}