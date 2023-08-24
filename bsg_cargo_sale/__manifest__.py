# -*- coding: utf-8 -*-
{
    'name': "bsg_cargo_sale",
    'summary': """
        Vehicle Cargo Sale""",

    'description': """
        Vehicle Cargo Sale
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",
    'category': 'Uncategorized',
    'version': '12.6.718',
    # any module necessary for this one to work correctly
    'depends': ['web','base','bsg_master_config', 'sale', 'bsg_customer_contract', 'account', 'website',
                'web_m2x_options','base_customer',
                'send_mobile_sms','website_payment'],

    # always loaded
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'data/cron_order_status.xml',
        'report/cargo_sale_report_view.xml',
        'report/cargo_sale_report_view_template.xml',
	    'data/data.xml',
        'report/cargo_sale_delivery_report_view.xml',
        'report/cargo_shipment_data_view.xml',
        'data/data.xml',
        'wizard/map_wizard.xml',
        'wizard/so_cancel_wizard.xml',
        'wizard/verify_sms_otp.xml',
        'wizard/cancel_multi_so_line_wizard_view.xml',
        'wizard/change_location_so_view.xml',
        'wizard/show_cargo_sale_line_warning_view.xml',
        'wizard/cancel_so_line_wizard_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_confirmation_message_wizard.xml',
        'views/vehicle_cargo_sale_view.xml',
        'views/cargo_sale_line_view.xml',
        'views/product_template_view.xml',
        'views/account_paymet.xml',
        'views/res_users_view.xml',
        'views/cargo_pymt_mthd_view.xml',
        'views/config.xml',
        'views/cargo_sale_config_master_view.xml',
        'views/menu_inherits_views.xml',
        'views/cargo_shipment_price.xml',
        'views/owner_deal_conf.xml',
        'views/cargo_sale_config_master_view.xml',
        'views/black_list_view.xml',
        'views/price_list_view.xml',
        'views/owner_deal_conf.xml',
        'views/qitaf_copoun_redeem.xml',
        'templates/assets.xml',
        
    ],
    'qweb' : ['templates/warning_message.xml'],
    # 'assets': {
    #     'web.assets_backend': [
    #         'bsg_cargo_sale/static/src/**/*',
    #     ],
    # }

    # -------------------------
    # Key - AIzaSyDnNqTAwXB1pQwHRLCwM2TGlx-VvZ5o8jU
    #
}
