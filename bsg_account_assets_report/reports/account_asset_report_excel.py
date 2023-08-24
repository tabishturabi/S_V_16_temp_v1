from odoo import models
from datetime import date, datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import pandas as pd
from num2words import num2words


class AccountAssetsReportExcel(models.AbstractModel):
    _name = 'report.bsg_account_assets_report.asset_report_xlsx'
    _inherit ='report.report_xlsx.abstract'

    def get_asset_type_str(self, asset_type):
        if asset_type == "all":
            return 'الكل'
        if asset_type == 'purchase':
            return 'اصول'
        if asset_type == 'sale':
            return 'مبيعات'
        if asset_type == 'expense':
            return 'مصروفات'

    def generate_xlsx_report(self, workbook,lines,data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        asset_type = docs.assets_type
        asset_type_str = self.get_asset_type_str(asset_type)
        domain = [('state', 'in',['open','close'])]
        if asset_type != 'all':
            domain.append(("type", "=", asset_type))
        asset_ids = self.env['account.asset'].search(domain)
        main_heading = workbook.add_format({
            "bold": 0,
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": 'white',
            'font_size': '10',
        })
        main_heading2 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#00cc44',
            'font_size': '12',
        })
        main_heading3 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#ffffff',
            'font_size': '13',
        })
        sheet = workbook.add_worksheet('Assets Report')
        sheet.set_column('A:J',15)
        row = 0
        col = 0
        self.env.ref(
            'bsg_account_assets_report.asset_report_xlsx_id').report_file = "Assets Report"
        sheet.merge_range('A1:J1', 'تقرير الأصول', main_heading3)
        sheet.merge_range('A2:J2', 'Account Assets Report', main_heading3)
        sheet.write('D3', 'نوع الاصول', main_heading2)
        sheet.write_string('E3', asset_type_str, main_heading3)
        sheet.write('D4', 'From', main_heading2)
        sheet.write_string('E4', str(docs.date_from), main_heading)
        sheet.write('F4', 'To', main_heading2)
        sheet.write_string('G4', str(docs.date_to), main_heading)


        grand_total = 0
        gross_value_total = 0
        salvage_value_total = 0
        accum_depreciation_value_total = 0
        residual_value_total = 0
        gross_value_1_total = 0
        accum_depreciation_value_1_total = 0
        h_value_total = 0
        salvage_value_1_total = 0
        j_value_total = 0
        if asset_ids:
            if not docs.with_details:
                sheet.write('A5', 'نوع الاصل', main_heading2)
                sheet.write('B5', 'إجمالي قيمة الشراء', main_heading2)
                sheet.write('C5', 'إجمالي  القيمة التخريدية', main_heading2)
                sheet.write('D5', ' رصيد اول مجمع الاهلاك', main_heading2)
                sheet.write('E5', ' صافى الاصل  اول المدة', main_heading2)
                sheet.write('F5', 'الاضافات', main_heading2)
                accum_dep_str = "إهلاك حتي %s" % (docs.date_to)
                sheet.write_string('G5', str(accum_dep_str), main_heading2)
                sheet.write('H5', 'مجمع اهلاك اخر', main_heading2)
                sheet.write('I5', 'التخريدية اخر', main_heading2)
                sheet.write('J5', 'صافى الاصل اخر المدة', main_heading2)
                row += 5
                group_asset_ids = asset_ids.read_group([],fields=['category_id'],groupby=['category_id'],lazy=False)
                if group_asset_ids:
                    for group_asset_id in group_asset_ids:
                        filter_asset_ids = asset_ids.filtered(lambda r:(r.category_id.id == group_asset_id.get('category_id')[0]))
                        if filter_asset_ids:
                            gross_value = 0
                            salvage_value = 0
                            accum_depreciation_value = 0
                            residual_value = 0
                            gross_value_1 = 0
                            accum_depreciation_value_1 = 0
                            h_value = 0
                            salvage_value_1 = 0
                            j_value = 0
                            gross_value = sum(filter_asset_ids.mapped('value'))
                            salvage_value = sum(filter_asset_ids.mapped('salvage_value'))
                            salvage_value_1 = sum(filter_asset_ids.mapped('salvage_value'))
                            gross_value_1 = sum(filter_asset_ids.filtered(lambda r:r.date and r.date>=docs.date_from and r.date<=docs.date_to).mapped('value'))
                            for filter_asset_id in filter_asset_ids:
                                if filter_asset_id:
                                    depreciation_move_ids = filter_asset_id.depreciation_move_ids
                                    if depreciation_move_ids:
                                        accum_depreciation_value += sum(depreciation_move_ids.filtered(lambda r:r.depreciation_date<docs.date_from and r.move_check).mapped('amount'))
                                        accum_depreciation_value_1 += sum(depreciation_move_ids.filtered(lambda r:r.depreciation_date>=docs.date_from and r.depreciation_date<=docs.date_to and r.move_check).mapped('amount'))
                                    else:
                                        accum_depreciation_value += filter_asset_id.accumulated_depreciation
                            residual_value = gross_value-salvage_value-accum_depreciation_value
                            h_value = residual_value + accum_depreciation_value_1
                            j_value = gross_value-h_value-salvage_value_1
                            if group_asset_id.get('category_id'):
                                sheet.write_string(row, col, str(group_asset_id.get('category_id')[1]), main_heading)
                            if gross_value:
                                sheet.write_number(row, col + 1, round(gross_value,2), main_heading)
                                gross_value_total += gross_value
                            if salvage_value:
                                sheet.write_number(row, col + 2, round(salvage_value,2), main_heading)
                                salvage_value_total += salvage_value
                            if accum_depreciation_value:
                                sheet.write_number(row, col + 3, round(accum_depreciation_value,2), main_heading)
                                accum_depreciation_value_total += accum_depreciation_value
                            if residual_value:
                                sheet.write_number(row, col + 4, round(residual_value,2),
                                                   main_heading)
                                residual_value_total += residual_value
                            if gross_value_1:
                                sheet.write_number(row, col + 5, round(gross_value_1,2), main_heading)
                                gross_value_1_total += gross_value_1
                            if accum_depreciation_value_1:
                                sheet.write_number(row, col + 6, round(accum_depreciation_value_1,2), main_heading)
                                accum_depreciation_value_1_total += accum_depreciation_value_1
                            if h_value:
                                sheet.write_number(row, col + 7, round(h_value,2), main_heading)
                                h_value_total += h_value
                            if salvage_value_1:
                                sheet.write_number(row, col + 8, round(salvage_value_1,2), main_heading)
                                salvage_value_1_total += salvage_value_1
                            if j_value:
                                sheet.write_number(row, col + 9, round(j_value,2), main_heading)
                                j_value_total += j_value
                            row += 1
                    sheet.write(row, col,'Total', main_heading2)
                    sheet.write_number(row, col + 1, round(gross_value_total,2), main_heading)
                    sheet.write_number(row, col + 2, round(salvage_value_total,2), main_heading)
                    sheet.write_number(row, col + 3, round(accum_depreciation_value_total,2), main_heading)
                    sheet.write_number(row, col + 4, round(residual_value_total,2), main_heading)
                    sheet.write_number(row, col + 5, round(gross_value_1_total,2), main_heading)
                    sheet.write_number(row, col + 6, round(accum_depreciation_value_1_total,2), main_heading)
                    sheet.write_number(row, col + 7, round(h_value_total,2), main_heading)
                    sheet.write_number(row, col + 8, round(salvage_value_1_total,2), main_heading)
                    sheet.write_number(row, col + 9, round(j_value_total,2), main_heading)
            else:
                sheet.write('A5', 'الاصل', main_heading2)
                sheet.write('B5', 'نوع الاصل', main_heading2)
                sheet.write('C5', 'المرجع', main_heading2)
                sheet.write('D5', 'إستيكر الاسطول', main_heading2)
                sheet.write('E5', 'لحساب التحليلي', main_heading2)
                sheet.write('F5', 'إجمالي قيمة الشراء', main_heading2)
                sheet.write('G5', 'إجمالي  القيمة التخريدية', main_heading2)
                sheet.write('H5', ' رصيد اول مجمع الاهلاك', main_heading2)
                sheet.write('I5', ' صافى الاصل  اول المدة', main_heading2)
                sheet.write('J5', 'الاضافات', main_heading2)
                accum_dep_str = "إهلاك حتي %s" % (docs.date_to)
                sheet.write_string('K5', str(accum_dep_str), main_heading2)
                sheet.write('L5', 'مجمع اهلاك اخر', main_heading2)
                sheet.write('M5', 'التخريدية اخر', main_heading2)
                sheet.write('N5', 'صافى الاصل اخر المدة', main_heading2)
                sheet.write('O5', 'حالة', main_heading2)
                sheet.write('P5', 'تاريخ', main_heading2)
                sheet.write('Q5', 'تم البيع', main_heading2)

                row += 5
                for asset_id in asset_ids:
                    if asset_id:
                        residual_value = 0
                        h_value = 0
                        j_value = 0
                        accum_depreciation_value = 0
                        accum_depreciation_value_1 = 0
                        depreciation_move_ids = asset_id.depreciation_move_ids
                        if depreciation_move_ids:
                            accum_depreciation_value = sum(depreciation_move_ids.filtered(
                                lambda r: r.depreciation_date < docs.date_from and r.move_check).mapped('amount'))
                            accum_depreciation_value_1 = sum(depreciation_move_ids.filtered(lambda
                                                                                                r: r.depreciation_date >= docs.date_from and r.depreciation_date <= docs.date_to and r.move_check).mapped(
                                'amount'))
                        else:
                            accum_depreciation_value += asset_id.accumulated_depreciation
                        residual_value = asset_id.value - asset_id.salvage_value - accum_depreciation_value
                        h_value = residual_value + accum_depreciation_value_1
                        j_value = asset_id.value - h_value - asset_id.salvage_value
                        if asset_id.name:
                            sheet.write_string(row, col, str(asset_id.name), main_heading)
                        if asset_id.category_id.name:
                            sheet.write_string(row, col + 1, str(asset_id.category_id.name), main_heading)
                        if asset_id.code:
                            sheet.write_string(row, col + 2, str(asset_id.code), main_heading)
                        if asset_id.fleet_vehicle_id.display_name:
                            sheet.write_string(row, col + 3, str(asset_id.fleet_vehicle_id.display_name), main_heading)
                        if asset_id.account_analytic_id.display_name:
                            sheet.write_string(row, col + 4, str(asset_id.account_analytic_id.display_name),
                                               main_heading)
                        if asset_id.value:
                            sheet.write_number(row, col + 5, round(asset_id.value, 2), main_heading)
                            gross_value_total += asset_id.value
                        if asset_id.salvage_value:
                            sheet.write_number(row, col + 6, round(asset_id.salvage_value, 2), main_heading)
                            salvage_value_total += asset_id.salvage_value
                        if accum_depreciation_value:
                            sheet.write_number(row, col + 7, round(accum_depreciation_value, 2), main_heading)
                            accum_depreciation_value_total += accum_depreciation_value
                        if residual_value:
                            sheet.write_number(row, col + 8, round(residual_value, 2),
                                               main_heading)
                            residual_value_total += residual_value
                        if asset_id.date:
                            if asset_id.date >= docs.date_from and asset_id.date <= docs.date_to:
                                if asset_id.value:
                                    sheet.write_number(row, col + 9, round(asset_id.value, 2), main_heading)
                                    gross_value_1_total += asset_id.value
                        if accum_depreciation_value_1:
                            sheet.write_number(row, col + 10, round(accum_depreciation_value_1, 2), main_heading)
                            accum_depreciation_value_1_total += accum_depreciation_value_1
                        if h_value:
                            sheet.write_number(row, col + 11, round(h_value, 2), main_heading)
                            h_value_total += h_value
                        if asset_id.salvage_value:
                            sheet.write_number(row, col + 12, round(asset_id.salvage_value, 2), main_heading)
                            salvage_value_1_total += asset_id.salvage_value
                        if j_value:
                            sheet.write_number(row, col + 13, round(j_value, 2), main_heading)
                            j_value_total += j_value
                        if asset_id.state:
                            sheet.write_string(row, col + 14, str(asset_id.state), main_heading)
                        if asset_id.date:
                            sheet.write_string(row, col + 15, str(asset_id.date), main_heading)
                        if asset_id.is_sold:
                            sheet.write_string(row, col + 16, str(True), main_heading)
                        if not asset_id.is_sold:
                            sheet.write_string(row, col + 16, str(False), main_heading)
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 5, round(gross_value_total, 2), main_heading)
                sheet.write_number(row, col + 6, round(salvage_value_total, 2), main_heading)
                sheet.write_number(row, col + 7, round(accum_depreciation_value_total, 2), main_heading)
                sheet.write_number(row, col + 8, round(residual_value_total, 2), main_heading)
                sheet.write_number(row, col + 9, round(gross_value_1_total, 2), main_heading)
                sheet.write_number(row, col + 10, round(accum_depreciation_value_1_total, 2), main_heading)
                sheet.write_number(row, col + 11, round(h_value_total, 2), main_heading)
                sheet.write_number(row, col + 12, round(salvage_value_1_total, 2), main_heading)
                sheet.write_number(row, col + 13, round(j_value_total, 2), main_heading)