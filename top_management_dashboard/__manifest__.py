# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Aswani PC (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': "Top Management Dashboard",
    'version': '12.0.1.0.29',
    'summary': """Bassami - Top Management Dashboard""",
    'description': """Bassami - Top Management Dashboard""",
    'category': 'Accounting',
    'author': 'Muhammad Arshad Khalil',
    'company': 'Albassami International Group Of Companies',
    'maintainer': 'Albassami International Group Of Companies',
    'website': "https://www.albassami.com",
    'depends': ['web','hr','hr_holidays','account','bsg_cargo_sale','bsg_trip_mgmt','fleet','purchase_enhanced','bsg_hr_employees_decisions','effective_date_notes','hr_clearence'],
    # 'external_dependencies': {
    #     'python': ['pandas'],
    # },
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/top_management_dashboard.xml',
        'views/assets.xml',
    ],

    # 'qweb': [
    #     "static/src/xml/top_management_dashboard.xml",
    #     "static/src/xml/hr_management_dashboard.xml",
    #     "static/src/xml/operations_dashboard.xml",
    # ],
    # 'assets': {
    #         # 'web.assets_common': [
    #         'web.assets_backend': [
    #             "top_management_dashboard/static/src/xml/top_management_dashboard.xml",
    #             "top_management_dashboard/static/src/xml/hr_management_dashboard.xml",
    #             "top_management_dashboard/static/src/xml/operations_dashboard.xml",
    #             'top_management_dashboard/static/src/css/top_management_dashboard.css',
    #             'top_management_dashboard/static/src/js/top_management_dashboard.js',
    #             'top_management_dashboard/static/src/js/hr_management_dashboard.js',
    #             'top_management_dashboard/static/src/js/operations_dashboard.js',
    #         ],
    #     },
    # 'images': ["static/description/banner.gif"],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
