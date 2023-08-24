# -*- coding: utf-8 -*-
{
    'name': "Bassami Inspection",

    'summary': """ Bassami Car Inspection """,

    'description': """
        Bassami Car Inspection
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",

    'category': 'theme',
    'version': '12.4.9',

    'depends': ['bsg_cargo_sale','sale', 'sign','bsg_hr_payroll'],

    # always loaded
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/assets.xml',
        'wizard/get_image.xml',
        'views/bassami_inspection.xml',
        'reports/bassami_inspection.xml'
    ],
    'qweb'  : [
            'static/src/xml/web.xml'
            ],
    "images"  : ['static/description/icon.jpg'],
    # 'assets': {
    #
    #     'web.assets_backend': [
    #         '/bassami_inspection/static/src/js/add_image.js',
    #         '/bassami_inspection/static/src/scss/style.scss',
    #         '/bassami_inspection/static/src/less/my_dev.less',
    #     ],
    #
    # },

    'installable': True,
    'auto_install': False,
}