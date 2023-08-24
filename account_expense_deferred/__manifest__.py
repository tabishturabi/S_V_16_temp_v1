# -*- coding: utf-8 -*-
{
    'name': 'Deferred Expense Management',
    'description': """
Assets management
=================
Manage Deferred Expense owned by a company or a person.
Keeps track of depreciations, and creates corresponding journal entries.

    """,
    'category': 'Accounting/Accounting',
    'sequence': 32,
    'depends': ['account_asset', 'payments_enhanced', 'asset_enhanced'],
    # Migration Note
# ,   'account_deferred_revenue'

# access_deferred_exp_type_read,access.deferred.expe.type.read,model_account_asset_category,group_def_expense_type_read,1,0,0,0
# access_deferred_exp_type_user,access.deferred.expe.type.user,model_account_asset_category,group_def_expense_type_create,1,1,1,1
# access_deferred_exp_type,access.deferred.exp.type,model_account_asset_category,base.group_user,1,1,0,0
# access_account_asset_depreciation_line_manager,account.asset.depreciation.line,account_asset.model_account_asset_depreciation_line,group_def_expense_create,1,1,1,1


    'data': [
        # security
        'security/account_asset_security.xml',
        'security/ir.model.access.csv',
        # data
        'data/asset_data.xml',
        # wizard
        'wizard/wizard_asset_compute_view.xml',
        'wizard/asset_modify_views.xml',
        # views
        'views/assets.xml',
        'views/product_views.xml',
        'views/account_deferred_expense.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    # 'assets': {
    #         'web.assets_backend': [
    #             # 'account_expense_deferred/static/src/**/*',
    #         ],
    #     },
    'license': 'OEEL-1',
    'auto_install': False,
}
