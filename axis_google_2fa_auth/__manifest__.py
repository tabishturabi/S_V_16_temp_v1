# -*- coding: utf-8 -*-
{
    'name': "Google authenticator odoo two factor authentication (2FA) for login security",

    'summary': """
        Enable two step authentication for Odoo user +
        supported in odoo v10, v11, v12 & v13""",

    'description': """
        Enable two step authentication for Odoo (version 12) users.
        Google Authenticator odoo Two Factor Authentication (2FA) for Login Security
        Implement security in Odoo login with Google Two Factor Authentication.
        High security for odoo, one time password security, Time-Based One Time Password, OTP security
        v12 Odoo12
    """,
    'category': 'Website',
    'version': '12.0.1.1.1',

    'depends': ['base', 'website', 'auth_signup'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',  # for permission
        'data/axis_2fa_auth_data.xml',
        'views/assets.xml',
        'views/res_users.xml',
        'views/2fa_template.xml'
    ],
    'demo': [],
    'price': 20.00,
    'currency': 'EUR',
    'support': ': business@axistechnolabs.com',
    'author': 'Axis Technolabs',
    'website': 'http://www.axistechnolabs.com',
    'installable': True,
    'license': 'AGPL-3',
    'external_dependencies': {'python': ['qrcode', 'pyotp']},
    'images': ['static/description/images/banner-thumb.gif'],
}
