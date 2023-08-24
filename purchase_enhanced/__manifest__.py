# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Solution founder IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Purchased Enhanced",
    'summary': """
    """,

    'author': "bassamitech",
    'website': "http://www.bassamitech.com",
    'category': 'Purchase',

    'version': '12.3.20',

    'depends': ['base','purchase','bsg_branch_config','purchase_requisition',
                'stock_picking_batch','stock_landed_costs','stock_enterprise',
                'stock_account','barcodes','account_asset','bsg_fleet_operations','payments_enhanced','purchase_stock','stock'],
    'data': [
        'security/basamic_user_rights.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/trailer_vehicle.xml',
        'views/stock_menu.xml',
        'views/purchase_menu.xml',
        'data/mail_template_view.xml',
        'data/mail_template_data.xml',
        'wizard/reject_reason.xml',
        'wizard/get_consu_qty.xml',
        'wizard/open_stock_transfer.xml',
        'views/menu.xml',
        'views/purchase_rq.xml',
        #'views/merge_rfq.xml',
        'views/purchase_request_transfer.xml',
        'views/purchase_request_rec.xml',
        'views/purcashe_order_custom.xml',
        'views/stock_picking_cu.xml',
        'views/department.xml',
        'views/ir_attachment.xml',
        'views/account_invoice.xml',
        'views/receipt_transfer_line.xml',
        'views/delivery_transfer_lines.xml',
        'report/purchase_req.xml',
        'report/purchase_transfer.xml',
        'report/purchase_req_rec.xml',
        'report/purchase_analysis.xml',
        'report/report_deliver.xml',
        'data/ir_attachment.xml',

    ],
    'demo': [
    ],
}

# Migration Note these models alread added in csv of purchase smart button
# access_warehouse_on_hand_report,access_warehouse_on_hand_report,model_warehouse_on_hand_report,,1,1,1,1
# access_warehouse_po_year_open_report,access_warehouse_po_year_open_report,model_warehouse_po_year_open_report,,1,1,1,1
# access_warehouse_po_year_close_report,access_warehouse_po_year_close_report,model_warehouse_po_year_close_report,,1,1,1,1
# access_warehouse_po_period_report,access_warehouse_po_period_report,model_warehouse_po_period_report,,1,1,1,1
# access_warehouse_pr_period_report,access_warehouse_pr_period_report,model_warehouse_pr_period_report,,1,1,1,1
# access_warehouse_pr_year_open_report,access_warehouse_pr_year_open_report,model_warehouse_pr_year_open_report,,1,1,1,1
# access_warehouse_pr_year_close_report,access_warehouse_pr_year_close_report,model_warehouse_pr_year_close_report,,1,1,1,1

# Models does not exist in odoo base code

# open_access_model_product_putaway,open_access_model_product_putaway,stock.model_product_putaway,base.group_user,1,1,1,1
# open_access_model_report_stock_forecast,open_access_model_report_stock_forecast,stock.model_report_stock_forecast,base.group_user,1,0,0,0
# open_access_model_stock_fixed_putaway_strat,open_access_model_stock_fixed_putaway_strat,stock.model_stock_fixed_putaway_strat,base.group_user,1,1,1,1
# open_access_model_stock_inventory,open_access_model_stock_inventory,stock.model_stock_inventory,base.group_user,1,0,0,0
# open_access_model_stock_inventory_line,open_access_model_stock_inventory_line,stock.model_stock_inventory_line,base.group_user,1,0,0,0
# open_access_model_stock_location_route,open_access_model_stock_location_route,stock.model_stock_location_route,base.group_user,1,0,0,0
# open_access_model_stock_production_lot,open_access_model_stock_production_lot,stock.model_stock_production_lot,base.group_user,1,1,1,1
# open_access_model_product_price_history,open_access_model_product_price_history,product.model_product_price_history,base.group_user,1,1,1,1
# open_access_model_account_invoice_tax,open_access_model_account_invoice_tax,account.model_account_invoice_tax,base.group_user,1,0,0,0
# stock_config_access_model_stock_location_route,stock_config_access_model_stock_location_route,stock.model_stock_location_route,purchase_enhanced.custom_group_stock_configuration,1,1,1,1

# stock_custom_full_access_model_stock_inventory,stock_custom_full_access_model_stock_inventory,stock.model_stock_inventory,purchase_enhanced.custom_group_stock_user_inventory_adjustment,1,1,1,1
# stock_custom_full_access_model_stock_inventory_line,stock_custom_full_access_model_stock_inventory_line,stock.model_stock_inventory_line,purchase_enhanced.custom_group_stock_user_inventory_adjustment,1,1,1,1
# ,,,,,,,