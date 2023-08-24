# -*- coding: utf-8 -*-

{
    'name': 'User Role History',
    'summary': """
        User Role History.""",
    'version': '12.0.1',
    'author': "ALbassami-Group",
    'website': 'http://www.albassamitransport.com',
    'depends': [
        'mail',
    ],
    'data': [
        'security/base_user_role_line_history.xml',
        'views/res_users.xml',
        'views/base_user_role_line_history.xml'
    ],
}
