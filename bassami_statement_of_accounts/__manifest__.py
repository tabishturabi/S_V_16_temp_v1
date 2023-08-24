{
    'name': "bassami_statement_of_accounts",
    'description': "bassami_statement_of_accounts",
    'author': 'bassamitech',
    'website': "http://www.bassamitech.com",
    'category': 'account',
    'version': '10.0.41',
    'application': True,
    'depends': ['base', 'account','bsg_branch_config','report_xlsx', 'account_reports','purchase'],
    # Migration Note
# access_accoun_type_soa,access_account_type_soa,account.model_account_account_type,bassami_statement_of_accounts.group_soa_report,1,0,0,0

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_view.xml',
        'template.xml',
        'views/module_report.xml',
    ],
}
