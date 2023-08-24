# -*- coding: utf-8 -*-
{
    'name': "Enhancements On Vehicle Document",

    'summary': """
      Hijri to Gregorian and vice versa, Documentation button on fleet,Petty cash logic""",

    'description': """
        Hijri to Gregorian and vice versa, Documentation button on fleet,Petty cash logic
    """,

    'author': "Tabish Turabi,Hasabalrasool",
    'website': "http://www.albassami.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.42',

    # any module necessary for this one to work correctly
    'depends': ['base','hijri_datepicker','bsg_trip_mgmt','bsg_employee_attachment','bsg_hr_payroll','advance_petty_expense_mgmt'],

    # always loaded
    'data': [
        'security/access_security.xml',
        'data/data.xml',
        'views/fleet_vehicle.xml',
        'views/document_info_fleet.xml',
        'views/renewal_vehicle_document.xml',
        'views/vehicles_documents_license.xml',
        'data/ir_attachment.xml',
    ],
}
