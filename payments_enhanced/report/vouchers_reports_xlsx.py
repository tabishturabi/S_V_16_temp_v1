from odoo import models
from datetime import datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
from ummalqura.hijri_date import HijriDate
import json

class EmployeeIqamaReportExcelAbs(models.AbstractModel):
    _name = 'report.payments_enhanced.voucher_report_temp_xlsx'
    _inherit ='report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook,lines,data=None):
        main_heading_top = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#D3D3D3',
            'font_size': '12',
        })
        main_heading_lines = workbook.add_format({
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": 'white',
            'font_size': '12',
        })
        main_heading_right_side = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#D3D3D3',
            'font_size': '12',
        })
        main_data = workbook.add_format({
            'align': 'center',
            "valign": 'vcenter',
            'font_size': '11',
            "bg_color": '#cc3300',
            "border": 1,
            'num_format': '#,##0',
        })

        main_data1 = workbook.add_format({
            'align': 'center',
            "valign": 'vcenter',
            'font_size': '11',
            "border": 1,
            'num_format': '#,##0',
        })
        main_data_profit = workbook.add_format({
            'bold': 1,
            'align': 'center',
            "valign": 'vcenter',
            'font_size': '11',
            "border": 1,
            'num_format': '#,##0',
            "bg_color": '#D3D3D3',

        })

        worksheet = workbook.add_worksheet('Payment voucher report-' + str('selfmonth'))
        # worksheet.set_row(1, 38)
        worksheet.set_column('A:A', 38)
        worksheet.set_column('B:K', 20)

        worksheet.freeze_panes(3, 3)

        rows = 0
        worksheet.merge_range(rows, 0, rows,9, 'Voucher Report', main_heading_right_side)
        rows = 1

        worksheet.merge_range(rows, 0, rows,9, 'تقرير السندات', main_heading_right_side)

        rows = 2
        worksheet.write(rows, 0, 'Voucher Number', main_heading_right_side)
        worksheet.write(rows, 1, 'State ', main_heading_right_side)
        worksheet.write(rows, 2, 'Payment Date ', main_heading_right_side)
        worksheet.write(rows, 3, 'Payment Journal ', main_heading_right_side)
        worksheet.write(rows, 4, 'Partner', main_heading_right_side)
        worksheet.write(rows, 5, 'Payment Amount', main_heading_right_side)
        worksheet.write(rows, 6, 'Invoice No', main_heading_right_side)
        worksheet.write(rows, 7, 'Total Invoice', main_heading_right_side)
        worksheet.write(rows, 8, 'Paid Voucher Amount', main_heading_right_side)
        worksheet.write(rows, 9, 'Difference Account', main_heading_right_side)
        # worksheet.write(rows, 10, 'Difference Amount', main_heading_right_side)
        rows = 3
        worksheet.write(rows, 0, 'رقم سند القبض', main_heading_right_side)
        worksheet.write(rows, 1, 'الحالة', main_heading_right_side)
        worksheet.write(rows, 2, 'تاريخ السند', main_heading_right_side)
        worksheet.write(rows, 3, 'دفتر يومية السداد', main_heading_right_side)
        worksheet.write(rows, 4, 'العميل', main_heading_right_side)
        worksheet.write(rows, 5, 'قيمة السند الإجمالية', main_heading_right_side)
        worksheet.write(rows, 6, 'رقم الفاتورة', main_heading_right_side)
        worksheet.write(rows, 7, 'قمية الفاتورة الإجمالية', main_heading_right_side)
        worksheet.write(rows, 8, 'السداد ع الفاتورة', main_heading_right_side)
        worksheet.write(rows, 9, 'حساب الفرق', main_heading_right_side)
        # worksheet.write(rows, 10, 'مبلغ الفرق', main_heading_right_side)

        if data.payment_type != 'all':
            payment_data = self.env['account.payment'].search(
                [('date', '>=', data.form), ('date', '<=', data.to),
                 ('payment_type', '=', data.payment_type),('state', 'not in' , ['draft','reversal_entry','cancelled'])])
        else:
            payment_data = self.env['account.payment'].search(
                [('date', '>=', data.form), ('date', '<=', data.to),('state', 'not in' , ['draft','reversal_entry','cancelled'])])
        rows = 4
        for rec in payment_data:
            worksheet.write_string(rows, 0, str(rec.name), main_heading_lines)
            worksheet.write_string(rows, 1, str(rec.state), main_heading_lines)
            worksheet.write_string(rows, 2, str(rec.date), main_heading_lines)
            worksheet.write_string(rows, 3, str(rec.journal_id.name), main_heading_lines)
            worksheet.write_string(rows, 4, str(rec.partner_id.name), main_heading_lines)
            worksheet.write_string(rows, 5, str(rec.amount), main_heading_lines)
            worksheet.write_string(rows, 9, str(self.get_data(rec.writeoff_account_id.name)), main_heading_lines)

            for reconcile in rec.reconciled_invoice_ids:
                payment_dict = json.loads(reconcile.payments_widget)
                if payment_dict:
                    get_data = payment_dict.get('content')
                    for dic_data in get_data:
                        if dic_data.get("name") and rec.name in dic_data.get('name'):
                            worksheet.write_string(rows, 0, str(rec.name), main_heading_lines)
                            worksheet.write(rows, 6, reconcile.number, main_heading_lines)
                            worksheet.write(rows, 7, reconcile.amount_total, main_heading_lines)
                            worksheet.write(rows, 8, dic_data.get('amount'), main_heading_lines)
                        # if rec.writeoff_account_id:
                        #     worksheet.write_string(rows, 9, str(self.get_data(rec.writeoff_account_id.name)), main_heading_lines)

                            # difference = rec.amount - reconcile.amount_total
                            # worksheet.write_number(rows, 10, difference, main_heading_lines)

                            rows += 1
            if not rec.reconciled_invoice_ids:
                rows += 1


    def get_data(self, data):
        if data:
            return data
        else:
            return ''

