# -*- coding: utf-8 -*-

{
    'name': 'User groups log Log',

    'version': '1.0',
    'category': 'HR',
    'summary': 'Users Group Log',
    'author': "Reem Elobeid",
    'description': """
       
    """,
    'depends': ['base',],
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'views/uses_log_views.xml',
    ],
    'qweb': [],
    'application': False,
}