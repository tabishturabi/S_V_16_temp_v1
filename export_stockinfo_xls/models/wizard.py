# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api


class StockReport(models.TransientModel):
    _name = "wizard.stock.history"
    _description = "Current Stock History"

    warehouse = fields.Many2many('stock.warehouse', 'wh_wiz_rel', 'wh', 'wiz', string='Warehouse', required=True)
    category = fields.Many2many('product.category', 'categ_wiz_rel', 'categ', 'wiz', string='Warehouse')
    filter_by = fields.Selection([('product', 'Product'), ('category', 'Category')], string="Filter By")
    product_ids = fields.Many2many('product.product', 'product_wiz_rel', 'product', 'wiz', string="Products")
    by_location = fields.Boolean(string="By Location")
    by_quantity = fields.Boolean(string="By Quantity")
    location_ids = fields.Many2many('stock.location', 'loc_wiz_rel', 'loc', 'wiz', string='Lacation')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)

    @api.onchange('warehouse')
    def onchange_warehouse_ids(self):
        stock_location_obj = self.env['stock.location']
        location_ids = stock_location_obj.search([('usage', '=', 'internal'), ('company_id', '=', self.company_id.id)])
        addtional_ids = []
        if self.warehouse:
            for warehouse in self.warehouse:
                addtional_ids.extend([y.id for y in stock_location_obj.search(
                    [('location_id', 'child_of', warehouse.view_location_id.id), ('usage', '=', 'internal')])])
            self.location_ids = False
        return {'domain': {'location_ids': [('id', 'in', addtional_ids)]}}

    #@api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard.stock.history'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('export_stockinfo_xls.stock_xlsx').report_action(self, data=datas)

    def print_pdf(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [1],
            'model': 'export.stock.info.wiz',
            'form': data
        }
        return self.env.ref('export_stockinfo_xls.stock_pdf_action').report_action([], data=datas)

