{
    'name': "bsg_license_report",
    'description': "bsg_license_report",
    'author': 'SolutionFounder',
    'website': "http://www.solutionfounder.com",
    'category': 'sale',
    'version': '12.0.1.9',
    'application': True,
    'depends': ['base','report_xlsx','bsg_branch_config'],
    'data': ['security/access_security.xml','template.xml',
             'ext_res_config_settings.xml'
             ],
    
}
