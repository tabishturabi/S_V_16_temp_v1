# -*- coding: utf-8 -*-
{
    'name' : 'Bsg Helpdesk Operations',
    'version' : '12.0.52',
    'summary': 'Helpdesk Ticket ',
    'description': """HelpDesk ticket""",
    'category': 'Helpdesk',
    'website': 'www.bassamitech.com',
    'depends' : [
            'base','helpdesk','hr','sale_management','purchase',
            'bsg_master_config','project','account','website_helpdesk',
            'website', 'bsg_fleet_operations', 'website_crm'
                ],
# 'website_helpdesk_form',
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'views/helpdesk_template_view.xml',
        'views/helpdesk_view.xml',
        'views/root_causes_views.xml'
        ],
        # 'assets': {
        #         'web.assets_frontend': [
        #             'bsg_helpdesk_operations/static/src/css/style.css',
        #             'bsg_helpdesk_operations/static/src/js/update.js',
        #         ],
        #     },
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
