# -*- coding: utf-8 -*-
{
    'name' : 'Custom Clearance',
    'version' : '12.1.0',
    'summary': 'Custom Clearance Sale',
    'description': """Custom Clearance About Sale""",
    'category': 'Sale',
    'website': 'www.albassami.com',
    'depends' : ['sale_management','account','fleet','bsg_fleet_operations','bsg_master_config'],
    # Migration Note removed from csv
# // access_import_status,import.status,model_import_status,group_can_access_custom_clearance_as_user,1,1,1,1
# // access_freight_forward,freight.forward,model_freight_forward,group_can_access_custom_clearance_as_user,1,1,1,1
# // access_field_officer,field.officer,model_field_officer,group_can_access_custom_clearance_as_user,1,1,1,1
    'data': [
        'data/ir_sequence_data.xml',
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'views/import_custom_view.xml',
        'views/export_custom_view.xml',
#         'views/import_site_view.xml',
        'views/freight_forward_view.xml',
        'views/status_view.xml',
#         'views/other_charges_view.xml',
#         'views/container_tree_config.xml',
#         'views/car_details_view.xml'
        ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
