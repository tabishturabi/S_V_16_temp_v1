# -*- coding: utf-8 -*-
{
	'name': "Remove Import Button",
	'sequence': 0,
	'summary': """Use To Display or Not Import Button on Your Tree and Kanban Views""",
	'description': """
		This module is used to manage the display of the "import" button on your
		list, form, kanban view, according to your needs.
	""",
	'author': "SLife Organization, Amichia Fréjus Arnaud AKA",
	"website": "https://slifeorganization.com",
	'category': 'web',
	'version': '1.01',
	'license': 'AGPL-3',
	'depends': ['web'],
	'data': [
		'views/import_template.xml',
		'views/users.xml',
	],
	'images': [
		'static/src/img/main_1.png',
		'static/src/img/main_screenshot.png'
	],
	# 'assets': {
	# 	'web.assets_backend': [
	# 		'/display_import_button/static/src/js/tools.js',
	# 		'/display_import_button/static/src/js/kanban_controller.js',
	# 	],
	# },

	'qweb': ['static/src/xml/template.xml'],
	'installable': True,
	'auto_install': False,
}
