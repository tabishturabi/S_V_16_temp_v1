
{
    "name": "Umm Al Qura(Hijri) Datepicker",
    'version': '1.0',
    'author': 'Albassamitransport',
    'summary': 'Web',
    "description":
        """
        Odoo Web Displays Umm Al Qura(Hijri) Datepicker.
        =======================================================
        """,
    'website': 'www.albassamitransport.com',
    "depends": ['base', 'web'],
    'category': 'web',
    'sequence': 5,
    'version': '1.8',
    'data': [
        'data/res_lang.xml',
        'views/hijri_datepicker_templates.xml',
    ],
    'qweb' : [
        "static/src/xml/*.xml",
    ],
    # 'assets': {
    #         'web.assets_backend': [
    #             'hijri_datepicker/static/src/**/*',
    #         ],
    #     },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}
