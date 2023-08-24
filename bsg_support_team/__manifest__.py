# -*- coding: utf-8 -*-
{
    'name': "bsg_cargo_sale",
    'summary': """
        Basami Support Team""",

    'description': """
        Support Team
    """,

    'author': "SolutionFounder",
    'website': "http://www.solutionfounder.com",
    'category': 'Uncategorized',
    'version': '12.0.31',
    # any module necessary for this one to work correctly
    'depends': ['base','bsg_cargo_sale','bsg_trip_mgmt','fleet','bsg_fleet_operations','bsg_branch_config'],
    # 'assets': {
    #     'web.assets_backend': [
    #         '/bsg_support_team/static/js/disable_delete.js',
    #     ],
    # },
    # always loaded
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'views/cargo_sale_inherit_view.xml',
        'views/cargo_sale_line_inherit_view.xml',
        'views/trip_view_inherit.xml',
        'views/support_team_fleet_vehicle_view.xml',
        'views/support_team_fleet_vehicle_link_driver_view.xml',
        'views/support_team_change_cargo_sale_line_price_view.xml',
        'views/fleet_daily_trip_count_view.xml',
        'wizard/cahnge_so_line_state_view.xml',
        'wizard/cahnge_fleet_trip_state_view.xml',
        'wizard/change_so_customer_view.xml',
        'templates/assets.xml',
    ],
}
