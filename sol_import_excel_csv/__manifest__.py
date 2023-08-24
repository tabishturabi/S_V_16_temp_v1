# -*- coding: utf-8 -*-
{
	'name': 'Import from CSV or Excel File',	
	'summary': 'This apps helps to import using CSV or Excel file',
	'description': '''
	This apps helps to import using CSV or Excel file
	''',
	'author': 'bassamitech',
	'website': 'http://www.bassamitech.com',
	'category': 'Accounting',
	'version': '12.0.0.14',
	'depends': ['base','account','bsg_master_config','stock'],
	'data': [
		'security/ir.model.access.csv',
		'wizard/view_import_chart.xml',
		'wizard/view_update_chart.xml',
		'wizard/view_impor_price_config.xml',
		'wizard/view_import_car_model.xml',
		'wizard/view_link_truck_trailer.xml',
		'wizard/view_wiz_import_product.xml'
		],

	'installable': True,
    'application': True,
    'qweb': [
    		],
}

