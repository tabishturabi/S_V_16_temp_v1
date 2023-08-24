# -*- coding: utf-8 -*-
{
    'name': "Bsg Account Log",
    'version': '12.0.6',
    'summary': """it will Show Log history for Journal(account.move) History""",
    'description': """"it will Show Log history for Journal(account.move) History""",
    'category': 'Account',
    'author': 'Solution Founder',
    'company': 'Solution Founder (Simplifying IT)',
    'website': "www.solutionfounder.com",
    'depends': ['mail', 'account','base'],
    'data': [
            'security/access_security.xml',
            'views/account_move_view.xml'
            ],
    'demo': [],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
