# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models, api, fields
from odoo.tools import pycompat
from odoo.tools.float_utils import float_round


class StockReportXls(models.AbstractModel):
    _name = 'report.export_stockinfo_xls.stock_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_warehouse(self, data):
        wh = data.warehouse.mapped('id')
        obj = self.env['stock.warehouse'].search([('id', 'in', wh)])
        l1 = []
        l2 = []
        for j in obj:
            l1.append(j.name)
            l2.append(j.id)
        return l1, l2

    def get_locations(self, data):
        loc1 = []
        loc2 = []
        if data.location_ids:
            loc1 = (data.location_ids.mapped('name'))
            loc2 = (data.location_ids.mapped('id'))
        return loc1, loc1

    def generate_xlsx_report(self, workbook, data, lines):
        if lines.by_location and lines.location_ids:
            d = lines.category
            get_warehouse = self.get_warehouse(lines)
            get_locations = self.get_locations(lines)
            comp = self.env.user.company_id.name
            sheet = workbook.add_worksheet('Stock Info')
            format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
            format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
            format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
            format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
            format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
            format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
            font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center'})
            font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
            font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right'})
            red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
            justify = workbook.add_format({'font_size': 12})
            format3.set_align('center')
            justify.set_align('justify')
            format1.set_align('center')
            red_mark.set_align('center')
            sheet.merge_range(1, 7, 2, 10, 'Product Stock Info', format0)
            sheet.merge_range(3, 7, 3, 10, comp, format11)
            sheet.freeze_panes(2, 0)
            sheet.freeze_panes(3, 0)
            sheet.freeze_panes(4, 0)
            sheet.freeze_panes(5, 0)
            sheet.freeze_panes(6, 0)
            sheet.freeze_panes(7, 0)
            sheet.freeze_panes(8, 0)
            sheet.freeze_panes(9, 0)
            sheet.freeze_panes(10, 0)
            w_house = ', '
            locations = ', '
            cat = ', '
            c = []
            d1 = d.mapped('id')
            if d1:
                for i in d1:
                    c.append(self.env['product.category'].browse(i).name)
                cat = cat.join(c)
                sheet.merge_range(4, 0, 4, 1, 'Category(s) : ', format4)
                sheet.merge_range(4, 2, 4, 3 + len(d1), cat, format4)
            sheet.merge_range(5, 0, 5, 1, 'Warehouse(s) : ', format4)
            w_house = w_house.join(get_warehouse[0])
            sheet.merge_range(5, 2, 5, 3 + len(get_warehouse[0]), w_house, format4)
            sheet.merge_range(6, 0, 6, 1, 'Location(s) : ', format4)
            locations = locations.join(get_locations[0])
            sheet.merge_range(6, 2, 6, 3 + len(get_locations[0]), locations, format4)
            if lines.by_quantity:
                user = self.env['res.users'].browse(self.env.uid)
                tz = pytz.timezone(user.tz)
                time = pytz.utc.localize(datetime.now()).astimezone(tz)
                count = len(get_warehouse[0]) * 2 + 6
                sheet.merge_range('A8:G8', 'Report Date: ' + str(time.strftime("%Y-%m-%d %H:%M %p")), format1)
                sheet.merge_range(7, 7, 7, count, 'Warehouses', format1)
                sheet.merge_range('A9:G9', 'Product Information', format11)
                w_col_no = 7
                w_col_no1 = 8
                for i in get_warehouse[0]:
                    w_col_no = w_col_no + 2
                    sheet.merge_range(8, w_col_no1, 8, w_col_no, i, format11)
                    w_col_no1 = w_col_no1 + 2
                sheet.write(9, 0, 'SKU', format21)
                sheet.merge_range(9, 1, 9, 3, 'Name', format21)
                sheet.merge_range(9, 4, 9, 5, 'Category', format21)
                sheet.merge_range(9, 6, 9, 7, 'Location', format21)
                p_col_no1 = 8
                for i in get_warehouse[0]:
                    sheet.merge_range(9, p_col_no1, 9, p_col_no1 + 1, 'Net On Hand', format21)
                    p_col_no1 = p_col_no1 + 2
                prod_row = 10
                prod_col = 0
                for i in get_warehouse[1]:
                    get_line = self.get_lines(lines, i)
                    for each in get_line:
                        sheet.write(prod_row, prod_col, each['sku'], font_size_8)
                        sheet.merge_range(prod_row, prod_col + 1, prod_row, prod_col + 3, each['name'], font_size_8_l)
                        sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['category'],
                                          font_size_8_l)
                        sheet.merge_range(prod_row, prod_col + 6, prod_row, prod_col + 7, each['location'],
                                          font_size_8_l)
                        prod_row = prod_row + 1
                    break
                prod_row = 10
                prod_col = 8
                for i in get_warehouse[1]:
                    get_line = self.get_lines(lines, i)
                    for each in get_line:
                        if each['net_on_hand'] < 0:
                            sheet.merge_range(prod_row, prod_col, prod_row, prod_col + 1, each['net_on_hand'], red_mark)
                        else:
                            sheet.merge_range(prod_row, prod_col, prod_row, prod_col + 1, each['net_on_hand'],
                                              font_size_8)
                        prod_row = prod_row + 1
                    prod_row = 10
                    prod_col = prod_col + 2
                    # continue
            else:
                user = self.env['res.users'].browse(self.env.uid)
                tz = pytz.timezone(user.tz)
                time = pytz.utc.localize(datetime.now()).astimezone(tz)
                count = len(get_warehouse[0]) * 11 + 6
                sheet.merge_range('A8:G8', 'Report Date: ' + str(time.strftime("%Y-%m-%d %H:%M %p")), format1)
                sheet.merge_range(7, 7, 7, count, 'Warehouses', format1)
                sheet.merge_range('A9:G9', 'Product Information', format11)
                w_col_no = 6
                w_col_no1 = 7

                for i in get_warehouse[0]:
                    w_col_no = w_col_no + 11
                    sheet.merge_range(8, w_col_no1, 8, w_col_no, i, format11)
                    w_col_no1 = w_col_no1 + 11
                sheet.write(9, 0, 'SKU', format21)
                sheet.merge_range(9, 1, 9, 3, 'Name', format21)
                sheet.merge_range(9, 4, 9, 5, 'Category', format21)
                sheet.merge_range(9, 6, 9, 7, 'Location', format21)
                sheet.write(9, 8, 'Cost Price', format21)
                p_col_no1 = 9
                for i in get_warehouse[0]:
                    sheet.write(9, p_col_no1, 'Available', format21)
                    sheet.write(9, p_col_no1 + 1, 'Virtual', format21)
                    sheet.write(9, p_col_no1 + 2, 'Incoming', format21)
                    sheet.write(9, p_col_no1 + 3, 'Outgoing', format21)
                    sheet.merge_range(9, p_col_no1 + 4, 9, p_col_no1 + 5, 'Net On Hand', format21)
                    sheet.merge_range(9, p_col_no1 + 6, 9, p_col_no1 + 7, 'Total Sold', format21)
                    sheet.merge_range(9, p_col_no1 + 8, 9, p_col_no1 + 9, 'Total Purchased', format21)
                    sheet.write(9, p_col_no1 + 10, 'Valuation', format21)
                    p_col_no1 = p_col_no1 + 11
                prod_row = 10
                prod_col = 0
                for i in get_warehouse[1]:
                    get_line = self.get_lines(lines, i)
                    for each in get_line:
                        sheet.write(prod_row, prod_col, each['sku'], font_size_8)
                        sheet.merge_range(prod_row, prod_col + 1, prod_row, prod_col + 3, each['name'], font_size_8_l)
                        sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['category'],
                                          font_size_8_l)
                        sheet.merge_range(prod_row, prod_col + 6, prod_row, prod_col + 7, each['location'],
                                          font_size_8_l)
                        sheet.write(prod_row, prod_col + 8, each['cost_price'], font_size_8_r)
                        prod_row = prod_row + 1
                    break
                prod_row = 10
                prod_col = 9
                for i in get_warehouse[1]:
                    get_line = self.get_lines(lines, i)
                    for each in get_line:
                        if each['available'] < 0:
                            sheet.write(prod_row, prod_col, each['available'], red_mark)
                        else:
                            sheet.write(prod_row, prod_col, each['available'], font_size_8)
                        if each['virtual'] < 0:
                            sheet.write(prod_row, prod_col + 1, each['virtual'], red_mark)
                        else:
                            sheet.write(prod_row, prod_col + 1, each['virtual'], font_size_8)
                        if each['incoming'] < 0:
                            sheet.write(prod_row, prod_col + 2, each['incoming'], red_mark)
                        else:
                            sheet.write(prod_row, prod_col + 2, each['incoming'], font_size_8)
                        if each['outgoing'] < 0:
                            sheet.write(prod_row, prod_col + 3, each['outgoing'], red_mark)
                        else:
                            sheet.write(prod_row, prod_col + 3, each['outgoing'], font_size_8)
                        if each['net_on_hand'] < 0:
                            sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['net_on_hand'],
                                              red_mark)
                        else:
                            sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['net_on_hand'],
                                              font_size_8)
                        if each['sale_value'] < 0:
                            sheet.merge_range(prod_row, prod_col + 6, prod_row, prod_col + 7, each['sale_value'],
                                              red_mark)
                        else:
                            sheet.merge_range(prod_row, prod_col + 6, prod_row, prod_col + 7, each['sale_value'],
                                              font_size_8)
                        if each['purchase_value'] < 0:
                            sheet.merge_range(prod_row, prod_col + 8, prod_row, prod_col + 9, each['purchase_value'],
                                              red_mark)
                        else:
                            sheet.merge_range(prod_row, prod_col + 8, prod_row, prod_col + 9, each['purchase_value'],
                                              font_size_8)
                        if each['total_value'] < 0:
                            sheet.write(prod_row, prod_col + 10, each['total_value'], red_mark)
                        else:
                            sheet.write(prod_row, prod_col + 10, each['total_value'], font_size_8_r)
                        prod_row = prod_row + 1
                    prod_row = 10
                    prod_col = prod_col + 11
                    # continue
        else:
            d = lines.category
            get_warehouse = self.get_warehouse(lines)
            comp = self.env.user.company_id.name
            sheet = workbook.add_worksheet('Stock Info')
            format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
            format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
            format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
            format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
            format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
            format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
            font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center'})
            font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
            font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right'})
            red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
            justify = workbook.add_format({'font_size': 12})
            format3.set_align('center')
            justify.set_align('justify')
            format1.set_align('center')
            red_mark.set_align('center')
            sheet.merge_range(1, 7, 2, 10, 'Product Stock Info', format0)
            sheet.merge_range(3, 7, 3, 10, comp, format11)
            sheet.freeze_panes(2, 0)
            sheet.freeze_panes(3, 0)
            sheet.freeze_panes(4, 0)
            sheet.freeze_panes(5, 0)
            sheet.freeze_panes(6, 0)
            sheet.freeze_panes(7, 0)
            sheet.freeze_panes(8, 0)
            sheet.freeze_panes(9, 0)
            sheet.freeze_panes(10, 0)
            w_house = ', '
            cat = ', '
            c = []
            d1 = d.mapped('id')
            if d1:
                for i in d1:
                    c.append(self.env['product.category'].browse(i).name)
                cat = cat.join(c)
                sheet.merge_range(4, 0, 4, 1, 'Category(s) : ', format4)
                sheet.merge_range(4, 2, 4, 3 + len(d1), cat, format4)
            sheet.merge_range(5, 0, 5, 1, 'Warehouse(s) : ', format4)
            w_house = w_house.join(get_warehouse[0])
            sheet.merge_range(5, 2, 5, 3 + len(get_warehouse[0]), w_house, format4)
            if lines.by_quantity:
                count = len(get_warehouse[0]) * 2 + 6
                user = self.env['res.users'].browse(self.env.uid)
                tz = pytz.timezone(user.tz)
                time = pytz.utc.localize(datetime.now()).astimezone(tz)
                sheet.merge_range('A8:F8', 'Report Date: ' + str(time.strftime("%Y-%m-%d %H:%M %p")), format1)
                sheet.merge_range(7, 6, 7, count, 'Warehouses', format1)
                sheet.merge_range('A9:F9', 'Product Information', format11)
                w_col_no = 5
                w_col_no1 = 6
                for i in get_warehouse[0]:
                    w_col_no = w_col_no + 2
                    sheet.merge_range(8, w_col_no1, 8, w_col_no, i, format11)
                    w_col_no1 = w_col_no1 + 2
                sheet.write(9, 0, 'SKU', format21)
                sheet.merge_range(9, 1, 9, 3, 'Name', format21)
                sheet.merge_range(9, 4, 9, 5, 'Category', format21)
                p_col_no1 = 6
                for i in get_warehouse[0]:
                    sheet.merge_range(9, p_col_no1, 9, p_col_no1 + 1, 'Net On Hand', format21)
                    p_col_no1 = p_col_no1 + 2
                prod_row = 10
                prod_col = 0
                for i in get_warehouse[1]:
                    get_line = self.get_lines(lines, i)
                    for each in get_line:
                        sheet.write(prod_row, prod_col, each['sku'], font_size_8)
                        sheet.merge_range(prod_row, prod_col + 1, prod_row, prod_col + 3, each['name'], font_size_8_l)
                        sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['category'],
                                          font_size_8_l)
                        prod_row = prod_row + 1
                    break
                prod_row = 10
                prod_col = 6
                for i in get_warehouse[1]:
                    get_line = self.get_lines(lines, i)
                    for each in get_line:
                        if each['net_on_hand'] < 0:
                            sheet.merge_range(prod_row, prod_col, prod_row, prod_col + 1, each['net_on_hand'], red_mark)
                        else:
                            sheet.merge_range(prod_row, prod_col, prod_row, prod_col + 1, each['net_on_hand'],
                                              font_size_8)
                        prod_row = prod_row + 1
                    prod_row = 10
                    prod_col = prod_col + 2
                    # continue
            else:
                count = len(get_warehouse[0]) * 11 + 6
                user = self.env['res.users'].browse(self.env.uid)
                tz = pytz.timezone(user.tz)
                time = pytz.utc.localize(datetime.now()).astimezone(tz)
                sheet.merge_range('A8:G8', 'Report Date: ' + str(time.strftime("%Y-%m-%d %H:%M %p")), format1)
                sheet.merge_range(7, 7, 7, count, 'Warehouses', format1)
                sheet.merge_range('A9:G9', 'Product Information', format11)
                w_col_no = 6
                w_col_no1 = 7
                for i in get_warehouse[0]:
                    w_col_no = w_col_no + 11
                    sheet.merge_range(8, w_col_no1, 8, w_col_no, i, format11)
                    w_col_no1 = w_col_no1 + 11
                sheet.write(9, 0, 'SKU', format21)
                sheet.merge_range(9, 1, 9, 3, 'Name', format21)
                sheet.merge_range(9, 4, 9, 5, 'Category', format21)
                sheet.write(9, 6, 'Cost Price', format21)
                p_col_no1 = 7
                for i in get_warehouse[0]:
                    sheet.write(9, p_col_no1, 'Available', format21)
                    sheet.write(9, p_col_no1 + 1, 'Virtual', format21)
                    sheet.write(9, p_col_no1 + 2, 'Incoming', format21)
                    sheet.write(9, p_col_no1 + 3, 'Outgoing', format21)
                    sheet.merge_range(9, p_col_no1 + 4, 9, p_col_no1 + 5, 'Net On Hand', format21)
                    sheet.merge_range(9, p_col_no1 + 6, 9, p_col_no1 + 7, 'Total Sold', format21)
                    sheet.merge_range(9, p_col_no1 + 8, 9, p_col_no1 + 9, 'Total Purchased', format21)
                    sheet.write(9, p_col_no1 + 10, 'Valuation', format21)
                    p_col_no1 = p_col_no1 + 11
                prod_row = 10
                prod_col = 0
                for i in get_warehouse[1]:
                    get_line = self.get_lines(lines, i)
                    for each in get_line:
                        sheet.write(prod_row, prod_col, each['sku'], font_size_8)
                        sheet.merge_range(prod_row, prod_col + 1, prod_row, prod_col + 3, each['name'], font_size_8_l)
                        sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['category'],
                                          font_size_8_l)
                        sheet.write(prod_row, prod_col + 6, each['cost_price'], font_size_8_r)
                        prod_row = prod_row + 1
                    break
                prod_row = 10
                prod_col = 7
                for i in get_warehouse[1]:
                    get_line = self.get_lines(lines, i)
                    for each in get_line:
                        if each['available'] < 0:
                            sheet.write(prod_row, prod_col, each['available'], red_mark)
                        else:
                            sheet.write(prod_row, prod_col, each['available'], font_size_8)
                        if each['virtual'] < 0:
                            sheet.write(prod_row, prod_col + 1, each['virtual'], red_mark)
                        else:
                            sheet.write(prod_row, prod_col + 1, each['virtual'], font_size_8)
                        if each['incoming'] < 0:
                            sheet.write(prod_row, prod_col + 2, each['incoming'], red_mark)
                        else:
                            sheet.write(prod_row, prod_col + 2, each['incoming'], font_size_8)
                        if each['outgoing'] < 0:
                            sheet.write(prod_row, prod_col + 3, each['outgoing'], red_mark)
                        else:
                            sheet.write(prod_row, prod_col + 3, each['outgoing'], font_size_8)
                        if each['net_on_hand'] < 0:
                            sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['net_on_hand'],
                                              red_mark)
                        else:
                            sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['net_on_hand'],
                                              font_size_8)
                        if each['sale_value'] < 0:
                            sheet.merge_range(prod_row, prod_col + 6, prod_row, prod_col + 7, each['sale_value'],
                                              red_mark)
                        else:
                            sheet.merge_range(prod_row, prod_col + 6, prod_row, prod_col + 7, each['sale_value'],
                                              font_size_8)
                        if each['purchase_value'] < 0:
                            sheet.merge_range(prod_row, prod_col + 8, prod_row, prod_col + 9, each['purchase_value'],
                                              red_mark)
                        else:
                            sheet.merge_range(prod_row, prod_col + 8, prod_row, prod_col + 9, each['purchase_value'],
                                              font_size_8)
                        if each['total_value'] < 0:
                            sheet.write(prod_row, prod_col + 10, each['total_value'], red_mark)
                        else:
                            sheet.write(prod_row, prod_col + 10, each['total_value'], font_size_8_r)
                        prod_row = prod_row + 1
                    prod_row = 10
                    prod_col = prod_col + 11
                    # continue

    def get_lines(self, data, warehouse):
        if data.by_location and data.location_ids:
            lines = []
            categ_id = data.category.mapped('id')
            prod_id = data.product_ids.mapped('id')
            locations = tuple(data.location_ids.ids)
            categ_products = self.env['product.product'].search([])
            if data.filter_by == 'category':
                if categ_id:
                    categ_products = self.env['product.product'].search([('categ_id', 'in', categ_id)])
            if data.filter_by == 'product':
                if prod_id:
                    categ_products = self.env['product.product'].search([('id', 'in', prod_id)])
            product_ids = tuple([pro_id.id for pro_id in categ_products])
            sale_query = """
                   SELECT sum(s_o_l.product_uom_qty) AS product_uom_qty, s_o_l.product_id FROM sale_order_line AS s_o_l
                   JOIN sale_order AS s_o ON s_o_l.order_id = s_o.id
                   JOIN stock_warehouse AS s_w ON s_o.warehouse_id = s_w.id
                   WHERE s_o.state IN ('sale','done')
                   AND s_o.warehouse_id = %s
                   AND s_w.view_location_id in %s
                   AND s_o_l.product_id in %s group by s_o_l.product_id"""
            purchase_query = """
                   SELECT sum(p_o_l.product_qty) AS product_qty, p_o_l.product_id FROM purchase_order_line AS p_o_l
                   JOIN purchase_order AS p_o ON p_o_l.order_id = p_o.id
                   INNER JOIN stock_picking_type AS s_p_t ON p_o.picking_type_id = s_p_t.id
                   INNER JOIN stock_warehouse AS p_s_w ON s_p_t.warehouse_id = p_s_w.id
                   WHERE p_o.state IN ('purchase','done')
                   AND s_p_t.warehouse_id = %s 
                   AND p_s_w.view_location_id in %s
                   AND p_o_l.product_id in %s group by p_o_l.product_id"""
            params = warehouse, locations, product_ids if product_ids else (0, 0)
            self._cr.execute(sale_query, params)
            sol_query_obj = self._cr.dictfetchall()
            self._cr.execute(purchase_query, params)
            pol_query_obj = self._cr.dictfetchall()
            for obj in categ_products:
                print('..............stock quant ids........', obj.stock_quant_ids)
                if obj.stock_quant_ids:
                    filter_stock_quant_ids = obj.stock_quant_ids.filtered(lambda l: l.location_id.usage == 'internal')
                    if filter_stock_quant_ids:
                        for stock_id in filter_stock_quant_ids:
                            if stock_id.location_id.id in data.location_ids.ids:
                                sale_value = 0
                                purchase_value = 0
                                for sol_product in sol_query_obj:
                                    if sol_product['product_id'] == obj.id:
                                        sale_value = sol_product['product_uom_qty']
                                for pol_product in pol_query_obj:
                                    if pol_product['product_id'] == obj.id:
                                        purchase_value = pol_product['product_qty']
                                virtual_available = obj.with_context({'warehouse': warehouse}).virtual_available
                                outgoing_qty = obj.with_context({'warehouse': warehouse}).outgoing_qty
                                incoming_qty = obj.with_context({'warehouse': warehouse}).incoming_qty
                                available_qty = virtual_available + outgoing_qty - incoming_qty
                                value = available_qty * obj.standard_price
                                vals = {
                                    'sku': obj.default_code,
                                    'name': obj.name,
                                    'category': obj.categ_id.display_name,
                                    'location': stock_id.location_id.display_name,
                                    'cost_price': obj.standard_price,
                                    'available': available_qty,
                                    'virtual': virtual_available,
                                    'incoming': incoming_qty,
                                    'outgoing': outgoing_qty,
                                    'net_on_hand': stock_id.quantity,
                                    'total_value': value,
                                    'sale_value': sale_value,
                                    'purchase_value': purchase_value,
                                }
                                lines.append(vals)
            return lines
        else:
            lines = []
            categ_id = data.category.mapped('id')
            prod_id = data.product_ids.mapped('id')
            categ_products = self.env['product.product'].search([])
            if data.filter_by == 'category':
                if categ_id:
                    categ_products = self.env['product.product'].search([('categ_id', 'in', categ_id)])
            if data.filter_by == 'product':
                if prod_id:
                    categ_products = self.env['product.product'].search([('id', 'in', prod_id)])
            product_ids = tuple([pro_id.id for pro_id in categ_products])
            sale_query = """
                              SELECT sum(s_o_l.product_uom_qty) AS product_uom_qty, s_o_l.product_id FROM sale_order_line AS s_o_l
                              JOIN sale_order AS s_o ON s_o_l.order_id = s_o.id
                              WHERE s_o.state IN ('sale','done')
                              AND s_o.warehouse_id = %s
                              AND s_o_l.product_id in %s group by s_o_l.product_id"""
            purchase_query = """
                              SELECT sum(p_o_l.product_qty) AS product_qty, p_o_l.product_id FROM purchase_order_line AS p_o_l
                              JOIN purchase_order AS p_o ON p_o_l.order_id = p_o.id
                              INNER JOIN stock_picking_type AS s_p_t ON p_o.picking_type_id = s_p_t.id
                              WHERE p_o.state IN ('purchase','done')
                              AND s_p_t.warehouse_id = %s AND p_o_l.product_id in %s group by p_o_l.product_id"""
            params = warehouse, product_ids if product_ids else (0, 0)
            self._cr.execute(sale_query, params)
            sol_query_obj = self._cr.dictfetchall()
            self._cr.execute(purchase_query, params)
            pol_query_obj = self._cr.dictfetchall()
            for obj in categ_products:
                sale_value = 0
                purchase_value = 0
                for sol_product in sol_query_obj:
                    if sol_product['product_id'] == obj.id:
                        sale_value = sol_product['product_uom_qty']
                for pol_product in pol_query_obj:
                    if pol_product['product_id'] == obj.id:
                        purchase_value = pol_product['product_qty']
                print('..........product context...........', obj._context)
                virtual_available = obj.with_context({'warehouse': warehouse}).virtual_available
                outgoing_qty = obj.with_context({'warehouse': warehouse}).outgoing_qty
                incoming_qty = obj.with_context({'warehouse': warehouse}).incoming_qty
                available_qty = virtual_available + outgoing_qty - incoming_qty
                value = available_qty * obj.standard_price
                print('..........product context after...........', obj.env.context)
                vals = {
                    'sku': obj.default_code,
                    'name': obj.name,
                    'category': obj.categ_id.display_name,
                    'cost_price': obj.standard_price,
                    'available': available_qty,
                    'virtual': virtual_available,
                    'incoming': incoming_qty,
                    'outgoing': outgoing_qty,
                    'net_on_hand': obj.with_context({'warehouse': warehouse}).qty_available,
                    'total_value': value,
                    'sale_value': sale_value,
                    'purchase_value': purchase_value,
                }
                lines.append(vals)
            return lines


class StockReportPdf(models.AbstractModel):
    _name = 'report.export_stockinfo_xls.stock_report_pdf'

    def get_warehouse(self, data):
        wh = data.warehouse.mapped('id')
        obj = self.env['stock.warehouse'].search([('id', 'in', wh)])
        l1 = []
        l2 = []
        for j in obj:
            l1.append(j.name)
            l2.append(j.id)
        return l1, l2

    def get_locations(self, data):
        loc1 = []
        loc2 = []
        if data.location_ids:
            loc1 = (data.location_ids.mapped('name'))
            loc2 = (data.location_ids.mapped('id'))
        return loc1, loc2

    #@api.multi
    def _get_warehouse_details(self, data, warehouse):
        if data['by_location'] and data['location_ids']:
            lines = []
            categ_id = data['category'].mapped('id')
            prod_id = data['product_ids'].mapped('id')
            locations = tuple(data['location_ids'].ids)
            categ_products = self.env['product.product'].search([])
            if data['filter_by'] == 'category':
                if categ_id:
                    categ_products = self.env['product.product'].search([('categ_id', 'in', categ_id)])
            if data['filter_by'] == 'product':
                if prod_id:
                    categ_products = self.env['product.product'].search([('id', 'in', prod_id)])
            product_ids = tuple([pro_id.id for pro_id in categ_products])
            sale_query = """
                         SELECT sum(s_o_l.product_uom_qty) AS product_uom_qty, s_o_l.product_id FROM sale_order_line AS s_o_l
                         JOIN sale_order AS s_o ON s_o_l.order_id = s_o.id
                         JOIN stock_warehouse AS s_w ON s_o.warehouse_id = s_w.id
                         WHERE s_o.state IN ('sale','done')
                         AND s_o.warehouse_id = %s
                         AND s_w.view_location_id in %s
                         AND s_o_l.product_id in %s group by s_o_l.product_id"""
            purchase_query = """
                         SELECT sum(p_o_l.product_qty) AS product_qty, p_o_l.product_id FROM purchase_order_line AS p_o_l
                         JOIN purchase_order AS p_o ON p_o_l.order_id = p_o.id
                         INNER JOIN stock_picking_type AS s_p_t ON p_o.picking_type_id = s_p_t.id
                         INNER JOIN stock_warehouse AS p_s_w ON s_p_t.warehouse_id = p_s_w.id
                         WHERE p_o.state IN ('purchase','done')
                         AND s_p_t.warehouse_id = %s 
                         AND p_s_w.view_location_id in %s
                         AND p_o_l.product_id in %s group by p_o_l.product_id"""
            params = warehouse, locations, product_ids if product_ids else (0, 0)
            self._cr.execute(sale_query, params)
            sol_query_obj = self._cr.dictfetchall()
            self._cr.execute(purchase_query, params)
            pol_query_obj = self._cr.dictfetchall()
            for obj in categ_products:
                print('..............stock quant ids........', obj.stock_quant_ids)
                if obj.stock_quant_ids:
                    filter_stock_quant_ids = obj.stock_quant_ids.filtered(lambda l: l.location_id.usage == 'internal')
                    if filter_stock_quant_ids:
                        for stock_id in filter_stock_quant_ids:
                            if stock_id.location_id.id in data['location_ids'].ids:
                                sale_value = 0
                                purchase_value = 0
                                for sol_product in sol_query_obj:
                                    if sol_product['product_id'] == obj.id:
                                        sale_value = sol_product['product_uom_qty']
                                for pol_product in pol_query_obj:
                                    if pol_product['product_id'] == obj.id:
                                        purchase_value = pol_product['product_qty']
                                virtual_available = obj.with_context({'warehouse': warehouse}).virtual_available
                                outgoing_qty = obj.with_context({'warehouse': warehouse}).outgoing_qty
                                incoming_qty = obj.with_context({'warehouse': warehouse}).incoming_qty
                                available_qty = virtual_available + outgoing_qty - incoming_qty
                                value = available_qty * obj.standard_price
                                vals = {
                                    'sku': obj.default_code,
                                    'name': obj.name,
                                    'category': obj.categ_id.display_name,
                                    'location': stock_id.location_id.display_name,
                                    'cost_price': obj.standard_price,
                                    'available': available_qty,
                                    'virtual': virtual_available,
                                    'incoming': incoming_qty,
                                    'outgoing': outgoing_qty,
                                    'net_on_hand': stock_id.quantity,
                                    'total_value': value,
                                    'sale_value': sale_value,
                                    'purchase_value': purchase_value,
                                }
                                lines.append(vals)
            return lines
        else:
            lines = []
            categ_id = data['category'].mapped('id')
            prod_id = data['product_ids'].mapped('id')
            categ_products = self.env['product.product'].search([])
            if data['filter_by'] == 'category':
                if categ_id:
                    categ_products = self.env['product.product'].search([('categ_id', 'in', categ_id)])
            if data['filter_by'] == 'product':
                if prod_id:
                    categ_products = self.env['product.product'].search([('id', 'in', prod_id)])
            product_ids = tuple([pro_id.id for pro_id in categ_products])
            sale_query = """
                                    SELECT sum(s_o_l.product_uom_qty) AS product_uom_qty, s_o_l.product_id FROM sale_order_line AS s_o_l
                                    JOIN sale_order AS s_o ON s_o_l.order_id = s_o.id
                                    WHERE s_o.state IN ('sale','done')
                                    AND s_o.warehouse_id = %s
                                    AND s_o_l.product_id in %s group by s_o_l.product_id"""
            purchase_query = """
                                    SELECT sum(p_o_l.product_qty) AS product_qty, p_o_l.product_id FROM purchase_order_line AS p_o_l
                                    JOIN purchase_order AS p_o ON p_o_l.order_id = p_o.id
                                    INNER JOIN stock_picking_type AS s_p_t ON p_o.picking_type_id = s_p_t.id
                                    WHERE p_o.state IN ('purchase','done')
                                    AND s_p_t.warehouse_id = %s AND p_o_l.product_id in %s group by p_o_l.product_id"""
            params = warehouse, product_ids if product_ids else (0, 0)
            self._cr.execute(sale_query, params)
            sol_query_obj = self._cr.dictfetchall()
            self._cr.execute(purchase_query, params)
            pol_query_obj = self._cr.dictfetchall()
            for obj in categ_products:
                sale_value = 0
                purchase_value = 0
                for sol_product in sol_query_obj:
                    if sol_product['product_id'] == obj.id:
                        sale_value = sol_product['product_uom_qty']
                for pol_product in pol_query_obj:
                    if pol_product['product_id'] == obj.id:
                        purchase_value = pol_product['product_qty']
                print('..........product context...........', obj._context)
                virtual_available = obj.with_context({'warehouse': warehouse}).virtual_available
                outgoing_qty = obj.with_context({'warehouse': warehouse}).outgoing_qty
                incoming_qty = obj.with_context({'warehouse': warehouse}).incoming_qty
                available_qty = virtual_available + outgoing_qty - incoming_qty
                value = available_qty * obj.standard_price
                print('..........product context after...........', obj.env.context)
                vals = {
                    'sku': obj.default_code,
                    'name': obj.name,
                    'category': obj.categ_id.display_name,
                    'cost_price': obj.standard_price,
                    'available': available_qty,
                    'virtual': virtual_available,
                    'incoming': incoming_qty,
                    'outgoing': outgoing_qty,
                    'net_on_hand': obj.with_context({'warehouse': warehouse}).qty_available,
                    'total_value': value,
                    'sale_value': sale_value,
                    'purchase_value': purchase_value,
                }
                lines.append(vals)
            return lines

    #@api.multi
    def _get_location_details(self, data, location_id):
        lines = []
        if location_id:
            category_ids = data.get('category')
            if category_ids:
                product_ids = self.env['product.product'].search([('categ_id', 'in', category_ids.ids)])
            else:
                product_ids = self.env['product.product'].search([])

            move_ids = self.env['stock.move'].search(
                [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available', 'done')),
                 ('product_id', 'in', product_ids.ids),
                 '|', ('location_id', '=', location_id.id),
                 ('location_dest_id', '=', location_id.id)
                 ])
            product_ids = []
            for stock_move in move_ids:
                if stock_move.product_id not in product_ids:
                    product_ids.append(stock_move.product_id)
            for product_id in product_ids:
                value = {}
                res = self._compute_quantities_dict(product_id, location_id=location_id)
                qty_available = res.get(product_id.id).get('qty_available') or 0.0
                incoming_qty = res.get(product_id.id).get('incoming_qty') or 0.0
                outgoing_qty = res.get(product_id.id).get('outgoing_qty') or 0.0
                virtual_available = res.get(product_id.id).get('virtual_available') or 0.0
                net_on_hand_qty = (qty_available - outgoing_qty) or 0.0
                # Total Sold Qty
                sale_order_line_ids = self.env['sale.order.line']. \
                    search([('state', 'in', ('sale', 'done')),
                            ('product_id', '=', product_id.id),
                            ('order_id.picking_ids', '!=', False)
                            ])
                total_sold_qty = 0.0
                for line in sale_order_line_ids:
                    total_sold_qty += line.product_uom_qty

                # Total Purchase Qty
                purchase_order_line_ids = self.env['purchase.order.line']. \
                    search([('state', 'in', ('purchase', 'done')),
                            ('product_id', '=', product_id.id),
                            ('order_id.picking_ids', '!=', False)
                            ])
                total_purchase_qty = 0.0
                for line in purchase_order_line_ids:
                    total_purchase_qty += line.product_qty

                value.update({
                    'product_id': product_id.id,
                    'product_name': product_id.name or '',
                    'product_code': product_id.default_code or '',
                    'standard_price': product_id.standard_price or 0.00,
                    'stock_value': product_id.stock_value or 0.00,
                    'uom': product_id.uom_id.name or '',
                    'qty_available': qty_available or 0.00,
                    'incoming_qty': incoming_qty or 0.00,
                    'outgoing_qty': outgoing_qty or 0.00,
                    'net_on_hand_qty': net_on_hand_qty or 0.00,
                    'virtual_available': virtual_available or 0.00,
                    'total_sold_qty': total_sold_qty or 0.00,
                    'total_purchase_qty': total_purchase_qty or 0.00,
                })
                lines.append(value)
            return lines

    @api.model
    def _get_report_values(self, docids, data=None):
        location_ids = self.env['stock.location'].browse(data['form']['location_ids'])
        warehouse_ids = self.env['stock.warehouse'].browse(data['form']['warehouse'])
        category_ids = self.env['product.category'].browse(data['form']['category'])
        product_ids = self.env['product.category'].browse(data['form']['product_ids'])
        date_today = datetime.today().strftime('%Y-%m-%d')
        data = {
            'warehouse': warehouse_ids,
            'location_ids': location_ids,
            'category': category_ids,
            'product_ids': product_ids,
            'by_location': data['form']['by_location'],
            'by_quantity': data['form']['by_quantity'],
            'filter_by': data['form']['filter_by'],
            'date_today': date_today,
            'company_name': self.env.user.company_id.name,
        }
        docargs = {
            'doc_model': 'wizard.stock.history',
            'data': data,
            'get_warehouse_details': self._get_warehouse_details,
            'get_location_details': self._get_location_details,
        }
        return docargs
