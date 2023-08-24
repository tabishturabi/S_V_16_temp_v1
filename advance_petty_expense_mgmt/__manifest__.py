# -*- coding: utf-8 -*-
{
    'name': 'Petty Cash Management',
    'author': 'bassamitech',
    'website': "http://www.bassamitech.com",
    'description': """
        Petty Cash Management 
        """,
    'category': 'expense',
    'version': '12.0.57',
    'depends': ['account','hr','base_customer','analytic','bsg_fleet_operations','bsg_branch_config','payments_enhanced','stock_account'],
    'data': [
        'data/data.xml',
        'data/expense_sequnce.xml',
        'data/mail_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_journal.xml',
        'views/petty_cash_mgmt_view.xml',
        # 'views/res_partner_inherit.xml',
        'views/account_expense_view.xml',
        'views/expense_template.xml',
        'views/config.xml',
        'views/petty_cash_user_rules_view.xml',
        'views/menu_view.xml',
        'wizard/declined_petty_cash_request_view.xml',
        'wizard/petty_expence_create_view.xml',
        'templates/assets.xml',
        'data/ir_attachment.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'advance_petty_expense_mgmt/static/src/js/disable_action_view.js',
    #     ],
    # },

    # 'installable': True,
#     'assets': {
#             'web.assets_backend': [
#                 'advance_petty_expense_mgmt/static/src/**/*',
#             ],
#         }
# # Migration Note model_account_account_type does not exist in odoo16
# # access_petty_cash_res_petty_account_type_accounting,access_petty_cash_res_petty_account_type_accounting,account.model_account_account_type,advance_petty_expense_mgmt.petty_accounting_manager,1,0,0,0
# # access_petty_cash_internal_editor_account_account_type,access_petty_cash_internal_editor_account_account_type,account.model_account_account_type,advance_petty_expense_mgmt.petty_cash_internal_editor,1,0,0,0
# # access_petty_cash_user_rule_account_account_type,access_petty_cash_user_rule_account_account_type,account.model_account_account_type,advance_petty_expense_mgmt.petty_cash_user_rule,1,0,0,0
# # access_petty_cash_setting_account_account_type,access_petty_cash_setting_account_account_type,account.model_account_account_type,advance_petty_expense_mgmt.petty_cash_settings,1,0,0,0
# # access_res_petty_cash_account_type_manager,access_res_petty_cash_account_type_manager,account.model_account_account_type,advance_petty_expense_mgmt.petty_cash_manager,1,0,0,0
# # access_res_petty_cash_account_type_user,access_res_petty_cash_account_type_user,account.model_account_account_type,advance_petty_expense_mgmt.petty_cash_user,1,0,0,0
#
}
