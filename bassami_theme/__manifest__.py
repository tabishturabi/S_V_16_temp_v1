# -*- coding: utf-8 -*-
{
    'name': "Bassami Theme",

    'summary': """ Bassami Backend theme """,

    'description': """
        Bassami Backend theme
    """,

    'author': "ALbassami-Group",
    'website': "http://www.albassamitransport.com",

    'category': 'theme',
    'version': '12.0.6',

    'depends': ['web'],

    # always loaded
    'data': [
        'views/assets.xml',
    ],
    'qweb'  : [
                    "static/src/xml/web.xml",
                ],
    "images"  : ['static/description/icon.jpg'],
    # 'assets': {
    #     'web.assets_backend': [
    #         '/bassami_theme/static/src/scss/style.scss',
    #     ],
    # },

    'installable': True,
    'auto_install': False,
}