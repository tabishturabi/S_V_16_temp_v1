{
    'name': "bassami_vouchers_report",
    'description': "bassami_vouchers_report",
    'author': 'bassamitech',
    'website': "http://www.bassamitech.com",
    'category': 'account',
    'version': '12.0.5',
    'application': True,
    'depends': ['base', 'account','bsg_branch_config','bassami_branches_legder'],
    'data': [
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
}