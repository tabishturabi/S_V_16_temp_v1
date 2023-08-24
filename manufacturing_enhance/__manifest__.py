# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Manufacturing enhance',
    'version': '12.2.17',
    'website': 'https://www.albassami.com/page/manufacturing',
    'category': 'Manufacturing',
    'sequence': 16,
    'summary': 'Manufacturing Orders & BOMs',
    'depends': ['product', 'stock','purchase_enhanced'],
    'description': "",
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'security/mrp_security.xml',
        'views/menus.xml',
        'views/mrp_production_views.xml',
        'views/projects.xml',
        'views/project_type.xml',
        'views/mrp_bom_views.xml',
        'views/purchase_req.xml',
        'views/quality_control.xml',
        'views/quality_teams.xml',

        # 'views/mrp_bom_views.xml',
    ],
    'qweb': ['static/src/xml/mrp.xml'],
    'demo': [
        'data/mrp_demo.xml',
    ],
    'test': [],
    'application': True,
}
