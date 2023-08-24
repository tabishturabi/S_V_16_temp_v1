{
    'name': "bassami_branches_vouchers_report",
    'description': "bassami_branches_vouchers_report",
    'author': 'bassamitech',
    'website': "http://www.bassamitech.com",
    'category': 'account',
    'version': '12.0.05',
    'application': True,
    'depends': ['base', 'account','bsg_branch_config'],
    'data': [
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
}