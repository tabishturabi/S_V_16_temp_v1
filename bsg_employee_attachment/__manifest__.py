# -*- coding: utf-8 -*-
{
    'name': "Attachment On Employee",

    'summary': """Added wizard on employee form for attachments.""",

    'description': """
        A popup opens on pressing button(Attach Document) in header of employee form for creating attachment""",

    'author': "Tabish Turabi",
    'website': "www.albassami.com",

    # Categories can be used to filter modules in modules listing
    'category': 'tools',
    'version': '12.0.8',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        'security/groups.xml',
        'views/views.xml',
        'data/ir_attachment.xml',
    ]
}
