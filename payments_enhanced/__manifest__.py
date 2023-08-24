# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Solution founder IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Payment Enhanced",
    'summary': """
        
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",
    'category': 'Accounting',
    'version': '12.1.55',
    'depends': ['web','report_xlsx' ,'bsg_trip_mgmt', 'account_analytic_parent', 'analytic', 'bsg_cargo_sale', 'account_accountant',
                'sales_team', 'account_generic_enhanced', 'base', 'account', 'sale',
                'bsg_branch_config', 'base_customer', 'account_asset', 'account_reports', 'account_parent','fleet',
                'hr','analytic_base_department','bassami_statement_of_accounts','bassami_statement_of_invoices',
                'vouchers_history_report','bassami_vouchers_report','bassami_branches_vouchers_report','budget_reconciliation_report'],
    # Migration Note
    # 'account_cancel' removed from depends as it is no more needed
    'data': [
        'data/data.xml',
        'data/cron_job.xml',
        'security/access_security.xml',
        'security/groups.xml',
        'security/access_security_update.xml',
        'security/ir.model.access.csv',
        'views/Customer_Collection.xml',
        'views/vendor_collection.xml',
        'views/register_payment_custom.xml',
        'views/payment_internal.xml',
        'views/account_move_custom.xml',
        'views/account_inherit.xml',
        'views/config.xml',
        'views/menu_inherits_views.xml',
        'report/report_payment_receipt.xml',
        'report/vouchers_report.xml',
        'views/budget_number_view.xml',
        'views/res_partner_inherit_view.xml',
        'report/collection_report.xml',
    ],
    'demo': [
    ],
}
