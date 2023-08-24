# -*- coding: utf-8 -*-
{
    'name': "Log All Fields",

    'summary': """log all fields changed in chatter.""",

    'description': """
        track all fields changes in chatter
    """,

    'author': "Tabish Turabi",
    'website': "www.albassami.com",

    # Categories can be used to filter modules in modules listing
    'category': 'tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail','hr_payroll','bsg_hr'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    'post_init_hook': 'post_init_hook',

}
