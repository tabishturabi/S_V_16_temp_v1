from odoo import models
from datetime import date, datetime
from ummalqura.hijri_date import HijriDate
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import pandas as pd
import math
from pytz import timezone,UTC


class DriverInfoReportExcel(models.AbstractModel):
    _name = 'report.bsg_fleet_operations.driver_info_xlsx'
    _inherit ='report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook,lines,data=None):
        model = self.env.context.get('active_model')
        wiz_id = self.env[model].browse(self.env.context.get('active_id'))
        domain = [('card_expire_date', '>=', wiz_id.form), ('card_expire_date', '<=', wiz_id.to)]
        print('.............domain................', domain)
        driver_info_ids = self.env['driver.information'].search(domain)
        print('...................driver_info_ids length..............',len(driver_info_ids))
        main_heading = workbook.add_format({
            "bold": 0,
            "border": 1,
            "align": 'center',
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
        sheet = workbook.add_worksheet('Driver Information Report')
        sheet.set_column('A:F',15)
        row = 0
        col = 0
        self.env.ref('bsg_fleet_operations.report_driver_info_id').report_file = "Driver Information Report Xlsx"
        sheet.merge_range('A1:F1', 'تقرير معلومات السائق', main_heading3)
        row += 1
        sheet.merge_range('A2:F2', 'Driver INFO Report', main_heading3)
        row += 2
        sheet.write(row, col, 'Print By', main_heading2)
        sheet.write_string(row, col+1, str(self.env.user.display_name), main_heading)
        sheet.write(row, col+2, 'طباعة بواسطة', main_heading2)
        row += 1
        sheet.write(row, col, 'Print Date', main_heading2)
        sheet.write_string(row, col+1, str(date.today()), main_heading)
        sheet.write(row, col+2, 'تاريخ الطباعة', main_heading2)
        row += 1
        sheet.write(row, col, 'From Date', main_heading2)
        sheet.write_string(row, col + 1, str(wiz_id.form), main_heading)
        sheet.write(row, col + 2, 'من التاريخ', main_heading2)
        row += 1
        sheet.write(row, col, 'To Date', main_heading2)
        sheet.write_string(row, col + 1, str(wiz_id.to), main_heading)
        sheet.write(row, col + 2, 'حتي اليوم', main_heading2)
        row += 1
        sheet.write(row, col, 'Driver', main_heading2)
        sheet.write(row, col+1, 'Mobile', main_heading2)
        sheet.write(row, col+2, 'Sticker NO', main_heading2)
        sheet.write(row, col+3, 'Trailer', main_heading2)
        sheet.write(row, col+4, 'Card Expire Date', main_heading2)
        sheet.write(row, col + 5, 'Left Days', main_heading2)
        sheet.write(row, col + 6, 'Card NO', main_heading2)
        row += 1
        for info_id in driver_info_ids:
            if info_id.employee_id:
                sheet.write_string(row, col,str(info_id.employee_id.display_name), main_heading)
            if info_id.mobile:
                sheet.write_string(row, col + 1,str(info_id.mobile), main_heading)
            if info_id.taq_number:
                sheet.write_string(row, col + 2, str(info_id.taq_number), main_heading)
            if info_id.trailer_id:
                sheet.write_string(row, col + 3, str(info_id.trailer_id), main_heading)
            if info_id.card_expire_date:
                sheet.write_string(row, col + 4,str(info_id.card_expire_date), main_heading)
            if info_id.left_days:
                sheet.write_string(row, col + 5,str(info_id.left_days), main_heading)
            if info_id.card_no:
                sheet.write_string(row, col + 6,str(info_id.card_no), main_heading)
            row+=1
