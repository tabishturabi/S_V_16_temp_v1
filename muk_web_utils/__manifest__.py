###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Web Utils 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
# 
###################################################################################
 
{ 
    "name": "MuK Web Utils",
    "summary": """Utility Features""",
    "version": "12.0.3.0.4", 
    "category": "Extra Tools",
    "license": "LGPL-3",
    "author": "MuK IT",
    "website": "http://www.mukit.at",
    'live_test_url': 'https://mukit.at/r/SgN',
    "contributors": [
        "Mathias Markl <mathias.markl@mukit.at>",
    ],
    "depends": [
        "web_editor",
        "muk_autovacuum",
    ],
    "data": [
        "template/assets.xml",
        "views/res_config_settings_view.xml",
        "data/autovacuum.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],

# 'assets': {
#         'web.assets_backend': [
#             "muk_web_utils/static/libs/simplebar/simplebar.css",
#             "muk_web_utils/static/libs/simplebar/simplebar.js",
#             "muk_web_utils/static/src/js/libs/jquery.js",
#             "muk_web_utils/static/src/js/libs/scrollbar.js",
#             "muk_web_utils/static/src/js/libs/underscore.js",
#             "muk_web_utils/static/src/js/core/utils.js",
# 			"muk_web_utils/static/src/js/core/async.js",
# 			"muk_web_utils/static/src/js/core/files.js",
# 			"muk_web_utils/static/src/js/core/dropzone.js",
# 			"muk_web_utils/static/src/js/core/mimetype.js",
# 			"muk_web_utils/static/src/js/core/dialog.js",
# 			"muk_web_utils/static/src/js/services/notification_service.js",
# 			"muk_web_utils/static/src/js/widgets/notification.js",
# 			"muk_web_utils/static/src/js/fields/abstract.js",
# 			"muk_web_utils/static/src/js/fields/utils.js",
# 			"muk_web_utils/static/src/js/fields/color.js",
# 			"muk_web_utils/static/src/js/fields/image.js",
# 			"muk_web_utils/static/src/js/fields/copy.js",
# 			"muk_web_utils/static/src/js/fields/share.js",
# 			"muk_web_utils/static/src/js/fields/path.js",
# 			"muk_web_utils/static/src/js/fields/binary.js",
# 			"muk_web_utils/static/src/js/fields/module.js",
# 			"muk_web_utils/static/src/js/fields/domain.js",
# 			"muk_web_utils/static/src/js/views/form/renderer.js",
#             "muk_web_utils/static/src/scss/variables.scss",
# 			"muk_web_utils/static/src/scss/mixins.scss",
# 			"muk_web_utils/static/src/scss/switch.scss",
# 			"muk_web_utils/static/src/scss/dropzone.scss",
# 			"muk_web_utils/static/src/scss/module.scss",
# 			"muk_web_utils/static/src/scss/color.scss",
# 			"muk_web_utils/static/src/scss/binary.scss",
# 			"muk_web_utils/static/src/scss/image.scss",
# 			"muk_web_utils/static/src/scss/copy.scss",
# 			"muk_web_utils/static/src/scss/share.scss",
# 			"muk_web_utils/static/src/scss/notification.scss",
#         ],
#         'web.qunit_suite':[
#             'muk_web_utils/static/tests/fields.js',
#         ]
#     },
    "images": [
        'static/description/banner.png'
    ],
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "application": False,
    "installable": True,
    'auto_install': False,
} 
