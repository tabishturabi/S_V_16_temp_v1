from odoo import models
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
from ummalqura.hijri_date import HijriDate
import json


class HousingMovementreport(models.AbstractModel):
    _name = 'report.housing.house_movement_report_temp_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, lines, data=None):
        main_heading_top = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#00cc44',
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

        worksheet = workbook.add_worksheet('House Movement Report' + str('report'))
        worksheet.set_column('A:A', 38)
        worksheet.set_column('B:V', 20)
        worksheet.freeze_panes(3, 0)
        eng_name = ""
        ar_name = ""
        if data.report_mode == 'house_movement':
            eng_name = "House Movement Report "
            # ar_name = "تقرير حركة شرائح البيانات"
        if data.report_mode == 'house_movement_transaction_type':
            eng_name = "House Movement Report Grouping By Transaction Type"
            # ar_name = " تقرير حركة شرائح البيانات حسب التسليم"
        if data.report_mode == 'house_movement_employee_type':
            eng_name = "House Movement Report Grouping By Employee Type"
            # ar_name = "تقرير حركة شرائح البيانات حسب الاستلام"
        if data.report_mode == 'house_movement_period':
            eng_name = "House Movement Report Grouping By Period"
            # ar_name = "تقرير حركة شرائح البيانات حسب ترقية الشريحة"
        if data.report_mode == 'house_movement_house':
            eng_name = "House Movement Report Grouping By House Location"
            # ar_name = "تقرير حركة شرائح البيانات حسب ترقية الشريحة"
        rows = 0
        worksheet.merge_range(rows, 0, rows, 21, eng_name, main_heading_right_side)
        rows = 1
        worksheet.merge_range(rows, 0, rows, 21, ar_name, main_heading_right_side)
        rows = 2
        worksheet.write(rows, 0, 'Name', main_heading_top)
        worksheet.write(rows, 1, 'Entry Date', main_heading_top)
        worksheet.write(rows, 2, 'Employee ID', main_heading_top)
        worksheet.write(rows, 3, 'Employee Name', main_heading_top)
        worksheet.write(rows, 4, 'Employee Iqama ID/National ID', main_heading_top)
        worksheet.write(rows, 5, 'Mobile Number', main_heading_top)
        worksheet.write(rows, 6, 'Company Name', main_heading_top)
        worksheet.write(rows, 7, 'Branch Name ', main_heading_top)
        worksheet.write(rows, 8, 'Department Name', main_heading_top)
        worksheet.write(rows, 9, 'Job Position', main_heading_top)
        worksheet.write(rows, 10, 'Analytic account', main_heading_top)
        worksheet.write(rows, 11, 'Analytic Tags', main_heading_top)
        worksheet.write(rows, 12, 'Sticker No', main_heading_top)
        worksheet.write(rows, 13, 'Vehicle Name', main_heading_top)
        worksheet.write(rows, 14, 'Vehicle Type Name', main_heading_top)
        worksheet.write(rows, 15, 'Entry Reason Type', main_heading_top)
        worksheet.write(rows, 16, 'Exiting House seq', main_heading_top)
        worksheet.write(rows, 17, 'Exiting Date', main_heading_top)
        worksheet.write(rows, 18, 'Days', main_heading_top)
        worksheet.write(rows, 19, 'House Location', main_heading_top)
        worksheet.write(rows, 20, 'state', main_heading_top)
        worksheet.write(rows, 21, 'Description', main_heading_top)
        rows = 3
        # worksheet.write(rows, 0, 'التاريخ', main_heading_top)
        # worksheet.write(rows, 1, 'المرجع', main_heading_top)
        # worksheet.write(rows, 2, 'نوع الحركة', main_heading_top)
        # worksheet.write(rows, 3, 'اسم الباقة', main_heading_top)
        # worksheet.write(rows, 4, 'مزود الخدمة', main_heading_top)
        # worksheet.write(rows, 5, 'كود الموظف', main_heading_top)
        # worksheet.write(rows, 6, 'اسم الموظف', main_heading_top)
        # worksheet.write(rows, 7, 'اسم الشركة', main_heading_top)
        # worksheet.write(rows, 8, 'اسم الإدارة', main_heading_top)
        # worksheet.write(rows, 9, 'اسم الفرع', main_heading_top)
        # worksheet.write(rows, 10, 'اسم الوظيفة', main_heading_top)
        # worksheet.write(rows, 11, 'علي حساب', main_heading_top)
        # worksheet.write(rows, 12, 'نوع الشريحة', main_heading_top)
        # worksheet.write(rows, 13, 'رقم الطلب', main_heading_top)
        # worksheet.write(rows, 14, 'تاريخ الطلب', main_heading_top)
        # worksheet.write(rows, 15, 'الوصف', main_heading_top)

        domain_entry = []
        domain_exit = []
        if data.report_mode == "house_movement":
            if data.day_condition == 'is equal to':
                domain_entry += [('date1', '=', data.date_from)]
                domain_exit += [('date1', '=', data.date_from)]
            if data.day_condition == 'is not equal to':
                domain_entry += [('date1', '!=', data.date_from)]
                domain_exit += [('date1', '!=', data.date_from)]
            if data.day_condition == 'is after':
                domain_entry += [('date1', '>', data.date_from)]
                domain_exit += [('date1', '>', data.date_from)]
            if data.day_condition == 'is before':
                domain_entry += [('date1', '<', data.date_from)]
                domain_exit += [('date1', '<', data.date_from)]
            if data.day_condition == 'is after or equal to':
                domain_entry += [('date1', '>=', data.date_from)]
                domain_exit += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is before or equal to':
                domain_entry += [('date1', '<=', data.date_from)]
                domain_exit += [('date1', '<=', data.date_from)]
            if data.day_condition == 'is between':
                domain_entry += [('date1', '>=', data.date_from)]
                domain_exit += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is set':
                domain_entry += [('date1', '!=', False)]
                domain_exit += [('date1', '!=', False)]
            if data.day_condition == 'is not set':
                domain_entry += [('date1', '=', False)]
                domain_exit += [('date1', '=', False)]
            if data.created_id:
                domain_entry += [('created_id', 'in', data.created_id.ids)]
                domain_exit += [('created_id', 'in', data.created_id.ids)]

            if data.job_id:
                domain_entry += [('job_id', 'in', data.job_id.ids)]
                domain_exit += [('job_id', 'in', data.job_id.ids)]
            if data.house_location:
                domain_entry += [('house_location', 'in', data.house_location.ids)]
                domain_exit += [('house_location', 'in', data.house_location.ids)]
            if data.branch_id:
                domain_entry += [('branch_id', 'in', data.branch_id.ids)]
                domain_exit += [('branch_id', 'in', data.branch_id.ids)]
            if data.department_id:
                domain_entry += [('department_id', 'in', data.department_id.ids)]
                domain_exit += [('department_id', 'in', data.department_id.ids)]

            if data.vehicle_id:
                domain_entry += [('sticker_no', '=', data.vehicle_id.taq_number)]
                domain_exit += [('sticker_no', '=', data.vehicle_id.taq_number)]

            if data.company_id:
                domain_entry += [('company_id', 'in', data.company_id.ids)]
                domain_exit += [('company_id', 'in', data.company_id.ids)]
            if data.vehicle_type_id:
                domain_entry += [('vehicle_type_id', 'in', data.vehicle_type_id.ids)]
                domain_exit += [('vehicle_type_id', 'in', data.vehicle_type_id.ids)]



            entry_data = self.env['entry.housing'].sudo().search(domain_entry)
            exit_data = self.env['exit.housing'].sudo().search(domain_exit)
            rows = 4
            for rec in entry_data:
                worksheet.write_string(rows, 0, str(rec.name), main_heading_lines)
                worksheet.write_string(rows, 1, str(rec.date), main_heading_lines)
                worksheet.write_string(rows, 2, str(rec.employee_code), main_heading_lines)
                worksheet.write_string(rows, 3, str(rec.employee_id.name) if rec.employee_id.name else "", main_heading_lines)
                worksheet.write_string(rows, 4, str(rec.bsg_empiqama.bsg_iqama_name) if rec.bsg_empiqama.bsg_iqama_name  else "", main_heading_lines)
                worksheet.write_string(rows, 5, str(rec.mobile_phone) if rec.mobile_phone  else "", main_heading_lines)
                worksheet.write_string(rows, 6, str(rec.company_id.name) if rec.company_id.name  else "", main_heading_lines)
                worksheet.write_string(rows, 7, str(rec.branch_id.branch_ar_name) if rec.branch_id.branch_ar_name  else "", main_heading_lines)
                worksheet.write_string(rows, 8, str(rec.department_id.complete_name) if rec.department_id.complete_name  else "", main_heading_lines)
                worksheet.write_string(rows, 9, str(rec.job_id.name) if rec.job_id.name  else "", main_heading_lines)
                worksheet.write_string(rows, 11, str(rec.analytic_tag_ids.name) if rec.analytic_tag_ids.name  else "", main_heading_lines)
                worksheet.write_string(rows, 10, str(rec.analytic_account_id.name) if rec.analytic_account_id.name  else "", main_heading_lines)
                worksheet.write_string(rows, 12, str(rec.sticker_no) if rec.sticker_no  else "", main_heading_lines)
                worksheet.write_string(rows, 13, str(rec.vehicle_name.name) if rec.vehicle_name.name  else "", main_heading_lines)
                worksheet.write_string(rows, 14, str(rec.vehicle_type_id) if rec.vehicle_type_id  else "", main_heading_lines)
                worksheet.write_string(rows, 15, str(rec.reason_id.description) if rec.reason_id.description  else "", main_heading_lines)
                worksheet.write_string(rows, 16, str(rec.house_seq.name) if rec.house_seq.name  else "", main_heading_lines)
                worksheet.write_string(rows, 17, str(rec.exit_date) if rec.exit_date  else "", main_heading_lines)
                worksheet.write_string(rows, 18, str(rec.days_count) if rec.days_count  else "", main_heading_lines)
                worksheet.write_string(rows, 19, str(rec.house_location.branch_ar_name) if rec.house_location.branch_ar_name  else "", main_heading_lines)
                worksheet.write_string(rows, 20, str(rec.state) if rec.state  else "", main_heading_lines)
                worksheet.write_string(rows, 21, str(rec.description) if rec.description  else "", main_heading_lines)
                rows += 1

            for rec in exit_data:
                worksheet.write_string(rows, 0, str(rec.name), main_heading_lines)
                worksheet.write_string(rows, 1, str(rec.entry_date), main_heading_lines)
                worksheet.write_string(rows, 2, str(rec.employee_code), main_heading_lines)
                worksheet.write_string(rows, 3, str(rec.employee_id.name) if rec.employee_id.name else "", main_heading_lines)
                worksheet.write_string(rows, 4, str(rec.bsg_empiqama.bsg_iqama_name) if rec.bsg_empiqama.bsg_iqama_name  else "", main_heading_lines)
                worksheet.write_string(rows, 5, str(rec.mobile_phone) if rec.mobile_phone  else "", main_heading_lines)
                worksheet.write_string(rows, 6, str(rec.company_id.name) if rec.company_id.name  else "", main_heading_lines)
                worksheet.write_string(rows, 7, str(rec.branch_id.branch_ar_name) if rec.branch_id.branch_ar_name  else "", main_heading_lines)
                worksheet.write_string(rows, 8, str(rec.department_id.complete_name) if rec.department_id.complete_name  else "", main_heading_lines)
                worksheet.write_string(rows, 9, str(rec.job_id.name) if rec.job_id.name  else "", main_heading_lines)
                worksheet.write_string(rows, 11, str(rec.analytic_tag_ids.name) if rec.analytic_tag_ids.name  else "", main_heading_lines)
                worksheet.write_string(rows, 10, str(rec.analytic_account_id.name) if rec.analytic_account_id.name  else "", main_heading_lines)
                worksheet.write_string(rows, 12, str(rec.sticker_no) if rec.sticker_no  else "", main_heading_lines)
                worksheet.write_string(rows, 13, str(rec.vehicle_name.name) if rec.vehicle_name.name  else "", main_heading_lines)
                worksheet.write_string(rows, 14, str(rec.vehicle_type_id) if rec.vehicle_type_id  else "", main_heading_lines)
                worksheet.write_string(rows, 15, str(rec.reason_id.description) if rec.reason_id.description  else "", main_heading_lines)
                worksheet.write_string(rows, 16, str(rec.name) if rec.name  else "", main_heading_lines)
                worksheet.write_string(rows, 17, str(rec.date) if rec.date  else "", main_heading_lines)
                worksheet.write_string(rows, 18, str(rec.days_count) if rec.days_count  else "", main_heading_lines)
                worksheet.write_string(rows, 19, str(rec.house_location.branch_ar_name) if rec.house_location.branch_ar_name  else "", main_heading_lines)
                worksheet.write_string(rows, 20, str(rec.state) if rec.state  else "", main_heading_lines)
                worksheet.write_string(rows, 21, str(rec.description) if rec.description  else "", main_heading_lines)

                rows += 1

        domain_transaction_type_entry = []
        domain_transaction_type_exit = []
        if data.transaction_type == 'all':
            if data.day_condition == 'is equal to':
                domain_transaction_type_entry += [('date1', '=', data.date_from)]
                domain_transaction_type_exit += [('date1', '=', data.date_from)]
            if data.day_condition == 'is not equal to':
                domain_transaction_type_entry += [('date1', '!=', data.date_from)]
                domain_transaction_type_exit += [('date1', '!=', data.date_from)]
            if data.day_condition == 'is after':
                domain_transaction_type_entry += [('date1', '>', data.date_from)]
                domain_transaction_type_exit += [('date1', '>', data.date_from)]
            if data.day_condition == 'is before':
                domain_transaction_type_entry += [('date1', '<', data.date_from)]
                domain_transaction_type_exit += [('date1', '<', data.date_from)]
            if data.day_condition == 'is after or equal to':
                domain_transaction_type_entry += [('date1', '>=', data.date_from)]
                domain_transaction_type_exit += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is before or equal to':
                domain_transaction_type_entry += [('date1', '<=', data.date_from)]
                domain_transaction_type_exit += [('date1', '<=', data.date_from)]
            if data.day_condition == 'is between':
                domain_transaction_type_entry += [('date1', '>=', data.date_from)]
                domain_transaction_type_exit += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is set':
                domain_transaction_type_entry += [('date1', '!=', False)]
                domain_transaction_type_exit += [('date1', '!=', False)]
            if data.day_condition == 'is not set':
                domain_transaction_type_entry += [('date1', '=', False)]
                domain_transaction_type_exit += [('date1', '=', False)]
            if data.created_id:
                domain_transaction_type_entry += [('created_id', 'in', data.created_id.ids)]
                domain_transaction_type_exit += [('created_id', 'in', data.created_id.ids)]

            if data.job_id:
                domain_transaction_type_entry += [('job_id', 'in', data.job_id.ids)]
                domain_transaction_type_exit += [('job_id', 'in', data.job_id.ids)]
            if data.house_location:
                domain_transaction_type_entry += [('house_location', 'in', data.house_location.ids)]
                domain_transaction_type_exit += [('house_location', 'in', data.house_location.ids)]
            if data.branch_id:
                domain_transaction_type_entry += [('branch_id', 'in', data.branch_id.ids)]
                domain_transaction_type_exit += [('branch_id', 'in', data.branch_id.ids)]
            if data.department_id:
                domain_transaction_type_entry += [('department_id', 'in', data.department_id.ids)]
                domain_transaction_type_exit += [('department_id', 'in', data.department_id.ids)]
            if data.vehicle_id:
                domain_transaction_type_entry += [('sticker_no', '=', data.vehicle_id.taq_number)]
                domain_transaction_type_exit += [('sticker_no', '=', data.vehicle_id.taq_number)]
            if data.company_id:
                domain_transaction_type_entry += [('company_id', 'in', data.company_id.ids)]
                domain_transaction_type_exit += [('company_id', 'in', data.company_id.ids)]
            if data.vehicle_type_id:
                domain_transaction_type_entry += [('vehicle_type_id', 'in', data.vehicle_type_id.ids)]
                domain_transaction_type_exit += [('vehicle_type_id', 'in', data.vehicle_type_id.ids)]

            transaction_type_entry_data = self.env['entry.housing'].sudo().search(domain_transaction_type_entry)
            transaction_type_exit_data = self.env['exit.housing'].sudo().search(domain_transaction_type_exit)
            rows = 4
            for rec in transaction_type_entry_data:
                worksheet.write_string(rows, 0, str(rec.name), main_heading_lines)
                worksheet.write_string(rows, 1, str(rec.date), main_heading_lines)
                worksheet.write_string(rows, 2, str(rec.employee_code), main_heading_lines)
                worksheet.write_string(rows, 3, str(rec.employee_id.name) if rec.employee_id.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 4,
                                       str(rec.bsg_empiqama.bsg_iqama_name) if rec.bsg_empiqama.bsg_iqama_name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 5, str(rec.mobile_phone) if rec.mobile_phone else "", main_heading_lines)
                worksheet.write_string(rows, 6, str(rec.company_id.name) if rec.company_id.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 7,
                                       str(rec.branch_id.branch_ar_name) if rec.branch_id.branch_ar_name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 8,
                                       str(rec.department_id.complete_name) if rec.department_id.complete_name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 9, str(rec.job_id.name) if rec.job_id.name else "", main_heading_lines)
                worksheet.write_string(rows, 11, str(rec.analytic_tag_ids.name) if rec.analytic_tag_ids.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 10,
                                       str(rec.analytic_account_id.name) if rec.analytic_account_id.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 12, str(rec.sticker_no) if rec.sticker_no else "", main_heading_lines)
                worksheet.write_string(rows, 13, str(rec.vehicle_name.name) if rec.vehicle_name.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 14, str(rec.vehicle_type_id) if rec.vehicle_type_id else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 15, str(rec.reason_id.description) if rec.reason_id.description else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 16, str(rec.house_seq.name) if rec.house_seq.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 17, str(rec.exit_date) if rec.exit_date else "", main_heading_lines)
                worksheet.write_string(rows, 18, str(rec.days_count) if rec.days_count else "", main_heading_lines)
                worksheet.write_string(rows, 19, str(
                    rec.house_location.branch_ar_name) if rec.house_location.branch_ar_name else "", main_heading_lines)
                worksheet.write_string(rows, 20, str(rec.state) if rec.state else "", main_heading_lines)
                worksheet.write_string(rows, 21, str(rec.description) if rec.description else "", main_heading_lines)
                rows += 1

            for rec in transaction_type_exit_data:
                worksheet.write_string(rows, 0, str(rec.name), main_heading_lines)
                worksheet.write_string(rows, 1, str(rec.entry_date), main_heading_lines)
                worksheet.write_string(rows, 2, str(rec.employee_code), main_heading_lines)
                worksheet.write_string(rows, 3, str(rec.employee_id.name) if rec.employee_id.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 4,
                                       str(rec.bsg_empiqama.bsg_iqama_name) if rec.bsg_empiqama.bsg_iqama_name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 5, str(rec.mobile_phone) if rec.mobile_phone else "", main_heading_lines)
                worksheet.write_string(rows, 6, str(rec.company_id.name) if rec.company_id.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 7,
                                       str(rec.branch_id.branch_ar_name) if rec.branch_id.branch_ar_name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 8,
                                       str(rec.department_id.complete_name) if rec.department_id.complete_name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 9, str(rec.job_id.name) if rec.job_id.name else "", main_heading_lines)
                worksheet.write_string(rows, 11, str(rec.analytic_tag_ids.name) if rec.analytic_tag_ids.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 10,
                                       str(rec.analytic_account_id.name) if rec.analytic_account_id.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 12, str(rec.sticker_no) if rec.sticker_no else "", main_heading_lines)
                worksheet.write_string(rows, 13, str(rec.vehicle_name.name) if rec.vehicle_name.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 14, str(rec.vehicle_type_id) if rec.vehicle_type_id else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 15, str(rec.reason_id.description) if rec.reason_id.description else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 16, str(rec.name) if rec.name else "", main_heading_lines)
                worksheet.write_string(rows, 17, str(rec.date) if rec.date else "", main_heading_lines)
                worksheet.write_string(rows, 18, str(rec.days_count) if rec.days_count  else "", main_heading_lines)
                worksheet.write_string(rows, 19, str(
                    rec.house_location.branch_ar_name) if rec.house_location.branch_ar_name else "", main_heading_lines)
                worksheet.write_string(rows, 20, str(rec.state) if rec.state else "", main_heading_lines)
                worksheet.write_string(rows, 21, str(rec.description) if rec.description else "", main_heading_lines)
                rows += 1

        domain_entry_type_entry = []
        if data.transaction_type == 'entry_housing':
            if data.day_condition == 'is equal to':
                domain_entry_type_entry += [('date1', '=', data.date_from)]
            if data.day_condition == 'is not equal to':
                domain_entry_type_entry += [('date1', '!=', data.date_from)]
            if data.day_condition == 'is after':
                domain_entry_type_entry += [('date1', '>', data.date_from)]
            if data.day_condition == 'is before':
                domain_entry_type_entry += [('date1', '<', data.date_from)]
            if data.day_condition == 'is after or equal to':
                domain_entry_type_entry += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is before or equal to':
                domain_entry_type_entry += [('date1', '<=', data.date_from)]
            if data.day_condition == 'is between':
                domain_entry_type_entry += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is set':
                domain_entry_type_entry += [('date1', '!=', False)]
            if data.day_condition == 'is not set':
                domain_entry_type_entry += [('date1', '=', False)]

            if data.created_id:
                domain_entry_type_entry += [('created_id', 'in', data.created_id.ids)]

            if data.job_id:
                domain_entry_type_entry += [('job_id', 'in', data.job_id.ids)]
            if data.house_location:
                domain_entry_type_entry += [('house_location', 'in', data.house_location.ids)]
            if data.branch_id:
                domain_entry_type_entry += [('branch_id', 'in', data.branch_id.ids)]
            if data.department_id:
                domain_entry_type_entry += [('department_id', 'in', data.department_id.ids)]
            if data.vehicle_id:
                domain_entry_type_entry += [('sticker_no', '=', data.vehicle_id.taq_number)]
            if data.company_id:
                domain_entry_type_entry += [('company_id', 'in', data.company_id.ids)]
            if data.vehicle_type_id:
                domain_entry_type_entry += [('vehicle_type_id', 'in', data.vehicle_type_id.ids)]

            transaction_entry_data = self.env['entry.housing'].sudo().search(domain_entry_type_entry)
            rows = 4
            for transaction in transaction_entry_data:
                worksheet.write_string(rows, 0, str(transaction.name), main_heading_lines)
                worksheet.write_string(rows, 1, str(transaction.date), main_heading_lines)
                worksheet.write_string(rows, 2, str(transaction.employee_code), main_heading_lines)
                worksheet.write_string(rows, 3, str(transaction.employee_id.name) if transaction.employee_id.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 4,
                                       str(transaction.bsg_empiqama.bsg_iqama_name) if transaction.bsg_empiqama.bsg_iqama_name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 5, str(transaction.mobile_phone) if transaction.mobile_phone else "", main_heading_lines)
                worksheet.write_string(rows, 6, str(transaction.company_id.name) if transaction.company_id.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 7,
                                       str(transaction.branch_id.branch_ar_name) if transaction.branch_id.branch_ar_name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 8,
                                       str(transaction.department_id.complete_name) if transaction.department_id.complete_name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 9, str(transaction.job_id.name) if transaction.job_id.name else "", main_heading_lines)
                worksheet.write_string(rows, 11, str(transaction.analytic_tag_ids.name) if transaction.analytic_tag_ids.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 10,
                                       str(transaction.analytic_account_id.name) if transaction.analytic_account_id.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 12, str(transaction.sticker_no) if transaction.sticker_no else "", main_heading_lines)
                worksheet.write_string(rows, 13, str(transaction.vehicle_name.name) if transaction.vehicle_name.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 14, str(transaction.vehicle_type_id) if transaction.vehicle_type_id else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 15, str(transaction.reason_id.description) if transaction.reason_id.description else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 16, str(transaction.house_seq.name) if transaction.house_seq.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 17, str(transaction.exit_date) if transaction.exit_date else "", main_heading_lines)
                worksheet.write_string(rows, 18, str(transaction.days_count) if transaction.days_count else "", main_heading_lines)
                worksheet.write_string(rows, 19, str(
                    transaction.house_location.branch_ar_name) if transaction.house_location.branch_ar_name else "", main_heading_lines)
                worksheet.write_string(rows, 20, str(transaction.state) if transaction.state else "", main_heading_lines)
                worksheet.write_string(rows, 21, str(transaction.description) if transaction.description else "", main_heading_lines)
                rows += 1

        domain_t_exit_type_exit = []
        if data.transaction_type == 'exit_housing':
            if data.day_condition == 'is equal to':
                domain_t_exit_type_exit += [('date1', '=', data.date_from)]
            if data.day_condition == 'is not equal to':
                domain_t_exit_type_exit += [('date1', '!=', data.date_from)]
            if data.day_condition == 'is after':
                domain_t_exit_type_exit += [('date1', '>', data.date_from)]
            if data.day_condition == 'is before':
                domain_t_exit_type_exit += [('date1', '<', data.date_from)]
            if data.day_condition == 'is after or equal to':
                domain_t_exit_type_exit += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is before or equal to':
                domain_t_exit_type_exit += [('date1', '<=', data.date_from)]
            if data.day_condition == 'is between':
                domain_t_exit_type_exit += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is set':
                domain_t_exit_type_exit += [('date1', '!=', False)]
            if data.day_condition == 'is not set':
                domain_t_exit_type_exit += [('date1', '=', False)]
            if data.created_id:
                domain_t_exit_type_exit += [('created_id', 'in', data.created_id.ids)]
            if data.job_id:
                domain_t_exit_type_exit += [('job_id', 'in', data.job_id.ids)]
            if data.house_location:
                domain_t_exit_type_exit += [('house_location', 'in', data.house_location.ids)]
            if data.branch_id:
                domain_t_exit_type_exit += [('branch_id', 'in', data.branch_id.ids)]
            if data.department_id:
                domain_t_exit_type_exit += [('department_id', 'in', data.department_id.ids)]
            if data.vehicle_id:
                domain_t_exit_type_exit += [('sticker_no', '=', data.vehicle_id.taq_number)]
            if data.company_id:
                domain_t_exit_type_exit += [('company_id', 'in', data.company_id.ids)]
            if data.vehicle_type_id:
                domain_t_exit_type_exit += [('vehicle_type_id', 'in', data.vehicle_type_id.ids)]
            transaction_t_exit_data = self.env['exit.housing'].sudo().search(domain_t_exit_type_exit)
            rows = 4
            for rec in transaction_t_exit_data:
                worksheet.write_string(rows, 0, str(rec.name), main_heading_lines)
                worksheet.write_string(rows, 1, str(rec.entry_date), main_heading_lines)
                worksheet.write_string(rows, 2, str(rec.employee_code), main_heading_lines)
                worksheet.write_string(rows, 3, str(rec.employee_id.name) if rec.employee_id.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 4,
                                       str(rec.bsg_empiqama.bsg_iqama_name) if rec.bsg_empiqama.bsg_iqama_name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 5, str(rec.mobile_phone) if rec.mobile_phone else "", main_heading_lines)
                worksheet.write_string(rows, 6, str(rec.company_id.name) if rec.company_id.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 7,
                                       str(rec.branch_id.branch_ar_name) if rec.branch_id.branch_ar_name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 8,
                                       str(rec.department_id.complete_name) if rec.department_id.complete_name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 9, str(rec.job_id.name) if rec.job_id.name else "", main_heading_lines)
                worksheet.write_string(rows, 11, str(rec.analytic_tag_ids.name) if rec.analytic_tag_ids.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 10,
                                       str(rec.analytic_account_id.name) if rec.analytic_account_id.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 12, str(rec.sticker_no) if rec.sticker_no else "", main_heading_lines)
                worksheet.write_string(rows, 13, str(rec.vehicle_name.name) if rec.vehicle_name.name else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 14, str(rec.vehicle_type_id) if rec.vehicle_type_id else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 15, str(rec.reason_id.description) if rec.reason_id.description else "",
                                       main_heading_lines)
                worksheet.write_string(rows, 16, str(rec.name) if rec.name else "", main_heading_lines)
                worksheet.write_string(rows, 17, str(rec.date) if rec.date else "", main_heading_lines)
                worksheet.write_string(rows, 18, str(rec.days_count) if rec.days_count  else "", main_heading_lines)
                worksheet.write_string(rows, 19, str(
                    rec.house_location.branch_ar_name) if rec.house_location.branch_ar_name else "", main_heading_lines)
                worksheet.write_string(rows, 20, str(rec.state) if rec.state else "", main_heading_lines)
                worksheet.write_string(rows, 21, str(rec.description) if rec.description else "", main_heading_lines)
                rows += 1

        domain_employee_type_entry = []
        domain_employee_type_exit = []
        if data.report_mode == 'house_movement_employee_type':
            if data.day_condition == 'is equal to':
                domain_employee_type_entry += [('date1', '=', data.date_from)]
                domain_employee_type_exit += [('date1', '=', data.date_from)]
            if data.day_condition == 'is not equal to':
                domain_employee_type_entry += [('date1', '!=', data.date_from)]
                domain_employee_type_exit += [('date1', '!=', data.date_from)]
            if data.day_condition == 'is after':
                domain_employee_type_entry += [('date1', '>', data.date_from)]
                domain_employee_type_exit += [('date1', '>', data.date_from)]
            if data.day_condition == 'is before':
                domain_employee_type_entry += [('date1', '<', data.date_from)]
                domain_employee_type_exit += [('date1', '<', data.date_from)]
            if data.day_condition == 'is after or equal to':
                domain_employee_type_entry += [('date1', '>=', data.date_from)]
                domain_employee_type_exit += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is before or equal to':
                domain_employee_type_entry += [('date1', '<=', data.date_from)]
                domain_employee_type_exit += [('date1', '<=', data.date_from)]
            if data.day_condition == 'is between':
                domain_employee_type_entry += [('date1', '>=', data.date_from)]
                domain_employee_type_exit += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is set':
                domain_employee_type_entry += [('date1', '!=', False)]
                domain_employee_type_exit += [('date1', '!=', False)]
            if data.day_condition == 'is not set':
                domain_employee_type_entry += [('date1', '=', False)]
                domain_employee_type_exit += [('date1', '=', False)]
            if data.created_id:
                domain_employee_type_entry += [('created_id', 'in', data.created_id.ids)]
                domain_employee_type_exit += [('created_id', 'in', data.created_id.ids)]

            if data.job_id:
                domain_employee_type_entry += [('job_id', 'in', data.job_id.ids)]
                domain_employee_type_exit += [('job_id', 'in', data.job_id.ids)]
            if data.house_location:
                domain_employee_type_entry += [('house_location', 'in', data.house_location.ids)]
                domain_employee_type_exit += [('house_location', 'in', data.house_location.ids)]
            if data.branch_id:
                domain_employee_type_entry += [('branch_id', 'in', data.branch_id.ids)]
                domain_employee_type_exit += [('branch_id', 'in', data.branch_id.ids)]
            if data.department_id:
                domain_employee_type_entry += [('department_id', 'in', data.department_id.ids)]
                domain_employee_type_exit += [('department_id', 'in', data.department_id.ids)]
            if data.vehicle_id:
                domain_employee_type_entry += [('sticker_no', '=', data.vehicle_id.taq_number)]
                domain_employee_type_exit += [('sticker_no', '=', data.vehicle_id.taq_number)]
            if data.company_id:
                domain_employee_type_entry += [('company_id', 'in', data.company_id.ids)]
                domain_employee_type_exit += [('company_id', 'in', data.company_id.ids)]
            if data.vehicle_type_id:
                domain_employee_type_entry += [('vehicle_type_id', 'in', data.vehicle_type_id.ids)]
                domain_employee_type_exit += [('vehicle_type_id', 'in', data.vehicle_type_id.ids)]

            employee_list = []
            employees = self.env['entry.housing'].sudo().read_group(domain_employee_type_entry, fields=['employee_id'],
                                                                             groupby=['employee_id'], lazy=False)
            for emp in employees:
                employee_list.append(emp['employee_id'][0])
            rows = 4
            for rec in employee_list:
                entry_employee = self.env['entry.housing'].sudo().search([('employee_id.id', '=', rec)])
                exit_employee = self.env['exit.housing'].sudo().search([('employee_id.id', '=', rec)])
                worksheet.write(rows, 0, 'Employee', main_heading_top)
                worksheet.write_string(rows, 1, str(self.env['hr.employee'].browse(rec).name), main_heading_top)
                rows += 1
                for entry in entry_employee:
                    worksheet.write_string(rows, 0, str(entry.name), main_heading_lines)
                    worksheet.write_string(rows, 1, str(entry.date), main_heading_lines)
                    worksheet.write_string(rows, 2, str(entry.employee_code), main_heading_lines)
                    worksheet.write_string(rows, 3, str(entry.employee_id.name) if entry.employee_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 4,
                                           str(entry.bsg_empiqama.bsg_iqama_name) if entry.bsg_empiqama.bsg_iqama_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 5, str(entry.mobile_phone) if entry.mobile_phone else "", main_heading_lines)
                    worksheet.write_string(rows, 6, str(entry.company_id.name) if entry.company_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 7,
                                           str(entry.branch_id.branch_ar_name) if entry.branch_id.branch_ar_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 8,
                                           str(entry.department_id.complete_name) if entry.department_id.complete_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 9, str(entry.job_id.name) if entry.job_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 11, str(entry.analytic_tag_ids.name) if entry.analytic_tag_ids.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 10,
                                           str(entry.analytic_account_id.name) if entry.analytic_account_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 12, str(entry.sticker_no) if entry.sticker_no else "", main_heading_lines)
                    worksheet.write_string(rows, 13, str(entry.vehicle_name.name) if entry.vehicle_name.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 14, str(entry.vehicle_type_id) if entry.vehicle_type_id else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 15, str(entry.reason_id.description) if entry.reason_id.description else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 16, str(entry.house_seq.name) if entry.house_seq.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 17, str(entry.exit_date) if entry.exit_date else "", main_heading_lines)
                    worksheet.write_string(rows, 18, str(entry.days_count) if entry.days_count else "", main_heading_lines)
                    worksheet.write_string(rows, 19, str(
                        entry.house_location.branch_ar_name) if entry.house_location.branch_ar_name else "", main_heading_lines)
                    worksheet.write_string(rows, 20, str(entry.state) if entry.state else "", main_heading_lines)
                    worksheet.write_string(rows, 21, str(entry.description) if entry.description else "", main_heading_lines)
                    rows += 1

                for exit in exit_employee:
                    worksheet.write_string(rows, 0, str(exit.name), main_heading_lines)
                    worksheet.write_string(rows, 1, str(exit.entry_date), main_heading_lines)
                    worksheet.write_string(rows, 2, str(exit.employee_code), main_heading_lines)
                    worksheet.write_string(rows, 3, str(exit.employee_id.name) if exit.employee_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 4,
                                           str(exit.bsg_empiqama.bsg_iqama_name) if exit.bsg_empiqama.bsg_iqama_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 5, str(exit.mobile_phone) if exit.mobile_phone else "", main_heading_lines)
                    worksheet.write_string(rows, 6, str(exit.company_id.name) if exit.company_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 7,
                                           str(exit.branch_id.branch_ar_name) if exit.branch_id.branch_ar_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 8,
                                           str(exit.department_id.complete_name) if exit.department_id.complete_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 9, str(exit.job_id.name) if exit.job_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 11, str(exit.analytic_tag_ids.name) if exit.analytic_tag_ids.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 10,
                                           str(exit.analytic_account_id.name) if exit.analytic_account_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 12, str(exit.sticker_no) if exit.sticker_no else "", main_heading_lines)
                    worksheet.write_string(rows, 13, str(exit.vehicle_name.name) if exit.vehicle_name.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 14, str(exit.vehicle_type_id) if exit.vehicle_type_id else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 15, str(exit.reason_id.description) if exit.reason_id.description else "",main_heading_lines)
                    worksheet.write_string(rows, 16, str(exit.name) if exit.name else "", main_heading_lines)
                    worksheet.write_string(rows, 17, str(exit.date) if exit.date else "", main_heading_lines)
                    worksheet.write_string(rows, 18, str(exit.days_count) if exit.days_count  else "", main_heading_lines)
                    worksheet.write_string(rows, 19, str(
                        exit.house_location.branch_ar_name) if exit.house_location.branch_ar_name else "", main_heading_lines)
                    worksheet.write_string(rows, 20, str(exit.state) if exit.state else "", main_heading_lines)
                    worksheet.write_string(rows, 21, str(exit.description) if exit.description else "", main_heading_lines)
                    rows += 1

        domain_location_type_entry = []
        domain_location_type_exit = []
        if data.report_mode == 'house_movement_house_location':
            if data.day_condition == 'is equal to':
                domain_location_type_entry += [('date1', '=', data.date_from)]
                domain_location_type_exit += [('date1', '=', data.date_from)]
            if data.day_condition == 'is not equal to':
                domain_location_type_entry += [('date1', '!=', data.date_from)]
                domain_location_type_exit += [('date1', '!=', data.date_from)]
            if data.day_condition == 'is after':
                domain_location_type_entry += [('date1', '>', data.date_from)]
                domain_location_type_exit += [('date1', '>', data.date_from)]
            if data.day_condition == 'is before':
                domain_location_type_entry += [('date1', '<', data.date_from)]
                domain_location_type_exit += [('date1', '<', data.date_from)]
            if data.day_condition == 'is after or equal to':
                domain_location_type_entry += [('date1', '>=', data.date_from)]
                domain_location_type_exit += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is before or equal to':
                domain_location_type_entry += [('date1', '<=', data.date_from)]
                domain_location_type_exit += [('date1', '<=', data.date_from)]
            if data.day_condition == 'is between':
                domain_location_type_entry += [('date1', '>=', data.date_from)]
                domain_location_type_exit += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is set':
                domain_location_type_entry += [('date1', '!=', False)]
                domain_location_type_exit += [('date1', '!=', False)]
            if data.day_condition == 'is not set':
                domain_location_type_entry += [('date1', '=', False)]
                domain_location_type_exit += [('date1', '=', False)]

            if data.created_id:
                domain_location_type_entry += [('created_id', 'in', data.created_id.ids)]
                domain_location_type_exit += [('created_id', 'in', data.created_id.ids)]

            if data.job_id:
                domain_location_type_entry += [('job_id', 'in', data.job_id.ids)]
                domain_location_type_exit += [('job_id', 'in', data.job_id.ids)]
            if data.house_location:
                domain_location_type_entry += [('house_location', 'in', data.house_location.ids)]
                domain_location_type_exit += [('house_location', 'in', data.house_location.ids)]
            if data.branch_id:
                domain_location_type_entry += [('branch_id', 'in', data.branch_id.ids)]
                domain_location_type_exit += [('branch_id', 'in', data.branch_id.ids)]
            if data.department_id:
                domain_location_type_entry += [('department_id', 'in', data.department_id.ids)]
                domain_location_type_exit += [('department_id', 'in', data.department_id.ids)]
            if data.vehicle_id:
                domain_location_type_entry += [('sticker_no', '=', data.vehicle_id.taq_number)]
                domain_location_type_exit += [('sticker_no', '=', data.vehicle_id.taq_number)]
            if data.company_id:
                domain_location_type_entry += [('company_id', 'in', data.company_id.ids)]
                domain_location_type_exit += [('company_id', 'in', data.company_id.ids)]
            if data.vehicle_type_id:
                domain_location_type_entry += [('vehicle_type_id', 'in', data.vehicle_type_id.ids)]
                domain_location_type_exit += [('vehicle_type_id', 'in', data.vehicle_type_id.ids)]

            location_list = []
            location = self.env['entry.housing'].sudo().read_group(domain_location_type_entry, fields=['house_location'],
                                                                    groupby=['house_location'], lazy=False)
            for loc in location:
                location_list.append(loc['house_location'][0])
            rows = 4
            for rec in location_list:
                entry_location = self.env['entry.housing'].sudo().search([('house_location.id', '=', rec)])
                exit_location = self.env['exit.housing'].sudo().search([('house_location.id', '=', rec)])
                worksheet.write(rows, 0, 'Location type', main_heading_top)
                worksheet.write_string(rows, 1, str(self.env['bsg_branches.bsg_branches'].browse(rec).branch_ar_name), main_heading_top)
                rows += 1
                for loc_data in entry_location:
                    worksheet.write_string(rows, 0, str(loc_data.name), main_heading_lines)
                    worksheet.write_string(rows, 1, str(loc_data.date), main_heading_lines)
                    worksheet.write_string(rows, 2, str(loc_data.employee_code), main_heading_lines)
                    worksheet.write_string(rows, 3, str(loc_data.employee_id.name) if loc_data.employee_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 4,
                                           str(
                                               loc_data.bsg_empiqama.bsg_iqama_name) if loc_data.bsg_empiqama.bsg_iqama_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 5, str(loc_data.mobile_phone) if loc_data.mobile_phone else "", main_heading_lines)
                    worksheet.write_string(rows, 6, str(loc_data.company_id.name) if loc_data.company_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 7,
                                           str(
                                               loc_data.branch_id.branch_ar_name) if loc_data.branch_id.branch_ar_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 8,
                                           str(
                                               loc_data.department_id.complete_name) if loc_data.department_id.complete_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 9, str(loc_data.job_id.name) if loc_data.job_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 11,
                                           str(loc_data.analytic_tag_ids.name) if loc_data.analytic_tag_ids.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 10,
                                           str(
                                               loc_data.analytic_account_id.name) if loc_data.analytic_account_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 12, str(loc_data.sticker_no) if loc_data.sticker_no else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 13, str(loc_data.vehicle_name.name) if loc_data.vehicle_name.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 14, str(loc_data.vehicle_type_id) if loc_data.vehicle_type_id else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 15,
                                           str(loc_data.reason_id.description) if loc_data.reason_id.description else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 16, str(loc_data.house_seq.name) if loc_data.house_seq.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 17, str(loc_data.exit_date) if loc_data.exit_date else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 18, str(loc_data.days_count) if loc_data.days_count else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 19, str(
                        loc_data.house_location.branch_ar_name) if loc_data.house_location.branch_ar_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 20, str(loc_data.state) if loc_data.state else "", main_heading_lines)
                    worksheet.write_string(rows, 21, str(loc_data.description) if loc_data.description else "",
                                           main_heading_lines)
                    rows += 1

                for exit in exit_location:
                    worksheet.write_string(rows, 0, str(exit.name), main_heading_lines)
                    worksheet.write_string(rows, 1, str(exit.entry_date), main_heading_lines)
                    worksheet.write_string(rows, 2, str(exit.employee_code), main_heading_lines)
                    worksheet.write_string(rows, 3, str(exit.employee_id.name) if exit.employee_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 4,
                                           str(
                                               exit.bsg_empiqama.bsg_iqama_name) if exit.bsg_empiqama.bsg_iqama_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 5, str(exit.mobile_phone) if exit.mobile_phone else "", main_heading_lines)
                    worksheet.write_string(rows, 6, str(exit.company_id.name) if exit.company_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 7,
                                           str(exit.branch_id.branch_ar_name) if exit.branch_id.branch_ar_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 8,
                                           str(
                                               exit.department_id.complete_name) if exit.department_id.complete_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 9, str(exit.job_id.name) if exit.job_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 11,
                                           str(exit.analytic_tag_ids.name) if exit.analytic_tag_ids.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 10,
                                           str(exit.analytic_account_id.name) if exit.analytic_account_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 12, str(exit.sticker_no) if exit.sticker_no else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 13, str(exit.vehicle_name.name) if exit.vehicle_name.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 14, str(exit.vehicle_type_id) if exit.vehicle_type_id else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 15,
                                           str(exit.reason_id.description) if exit.reason_id.description else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 16, str(exit.name) if exit.name else "", main_heading_lines)
                    worksheet.write_string(rows, 17, str(exit.date) if exit.date else "", main_heading_lines)
                    worksheet.write_string(rows, 18, str(exit.days_count) if exit.days_count else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 19, str(
                        exit.house_location.branch_ar_name) if exit.house_location.branch_ar_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 20, str(exit.state) if exit.state else "", main_heading_lines)
                    worksheet.write_string(rows, 21, str(exit.description) if exit.description else "",
                                           main_heading_lines)
                    rows += 1

        domain_period_by_day_entry = []
        domain_period_by_day_exit = []
        if data.period_group == 'day':
            if data.day_condition == 'is equal to':
                domain_period_by_day_entry += [('date1', '=', data.date_from)]
                domain_period_by_day_exit += [('date1', '=', data.date_from)]
            if data.day_condition == 'is not equal to':
                domain_period_by_day_entry += [('date1', '!=', data.date_from)]
                domain_period_by_day_exit += [('date1', '!=', data.date_from)]
            if data.day_condition == 'is after':
                domain_period_by_day_entry += [('date1', '>', data.date_from)]
                domain_period_by_day_exit += [('date1', '>', data.date_from)]
            if data.day_condition == 'is before':
                domain_period_by_day_entry += [('date1', '<', data.date_from)]
                domain_period_by_day_exit += [('date1', '<', data.date_from)]
            if data.day_condition == 'is after or equal to':
                domain_period_by_day_entry += [('date1', '>=', data.date_from)]
                domain_period_by_day_exit += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is before or equal to':
                domain_period_by_day_entry += [('date1', '<=', data.date_from)]
                domain_period_by_day_exit += [('date1', '<=', data.date_from)]
            if data.day_condition == 'is between':
                domain_period_by_day_entry += [('date1', '>=', data.date_from)]
                domain_period_by_day_exit += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is set':
                domain_period_by_day_entry += [('date1', '!=', False)]
                domain_period_by_day_exit += [('date1', '!=', False)]
            if data.day_condition == 'is not set':
                domain_period_by_day_entry += [('date1', '=', False)]
                domain_period_by_day_exit += [('date1', '=', False)]

            if data.job_id:
                domain_period_by_day_entry += [('job_id', 'in', data.job_id.ids)]
                domain_period_by_day_exit += [('job_id', 'in', data.job_id.ids)]
            if data.house_location:
                domain_period_by_day_entry += [('house_location', 'in', data.house_location.ids)]
                domain_period_by_day_exit += [('house_location', 'in', data.house_location.ids)]
            if data.branch_id:
                domain_period_by_day_entry += [('branch_id', 'in', data.branch_id.ids)]
                domain_period_by_day_exit += [('branch_id', 'in', data.branch_id.ids)]
            if data.department_id:
                domain_period_by_day_entry += [('department_id', 'in', data.department_id.ids)]
                domain_period_by_day_exit += [('department_id', 'in', data.department_id.ids)]
            if data.vehicle_id:
                domain_period_by_day_entry += [('sticker_no', '=', data.vehicle_id.taq_number)]
                domain_period_by_day_exit += [('sticker_no', '=', data.vehicle_id.taq_number)]
            if data.company_id:
                domain_period_by_day_entry += [('company_id', 'in', data.company_id.ids)]
                domain_period_by_day_exit += [('company_id', 'in', data.company_id.ids)]
            if data.vehicle_type_id:
                domain_period_by_day_entry += [('vehicle_type_id', 'in', data.vehicle_type_id.ids)]
                domain_period_by_day_exit += [('vehicle_type_id', 'in', data.vehicle_type_id.ids)]


            day_list = []
            daysx = self.env['entry.housing'].sudo().read_group(domain_period_by_day_entry, fields=['date1'],
                                                                    groupby=['date1'], lazy=False)
            for dayxx in daysx:
                day_list.append(dayxx['date1'][0])
            rows = 4
            for rec in day_list:
                day_entry = self.env['entry.housing'].sudo().search([('date1', '=', rec)])
                day_exit = self.env['exit.housing'].sudo().search([('date1', '=', rec)])
                worksheet.write(rows, 0, 'Date', main_heading_top)
                worksheet.write_string(rows, 1, str(self.env['entry.housing'].browse(rec).date1), main_heading_top)
                rows += 1
                for entry in day_entry:
                    worksheet.write_string(rows, 0, str(entry.name), main_heading_lines)
                    worksheet.write_string(rows, 1, str(entry.date), main_heading_lines)
                    worksheet.write_string(rows, 2, str(entry.employee_code), main_heading_lines)
                    worksheet.write_string(rows, 3, str(entry.employee_id.name) if entry.employee_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 4,
                                           str(
                                               entry.bsg_empiqama.bsg_iqama_name) if entry.bsg_empiqama.bsg_iqama_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 5, str(entry.mobile_phone) if entry.mobile_phone else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 6, str(entry.company_id.name) if entry.company_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 7,
                                           str(
                                               entry.branch_id.branch_ar_name) if entry.branch_id.branch_ar_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 8,
                                           str(
                                               entry.department_id.complete_name) if entry.department_id.complete_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 9, str(entry.job_id.name) if entry.job_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 11,
                                           str(entry.analytic_tag_ids.name) if entry.analytic_tag_ids.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 10,
                                           str(
                                               entry.analytic_account_id.name) if entry.analytic_account_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 12, str(entry.sticker_no) if entry.sticker_no else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 13, str(entry.vehicle_name.name) if entry.vehicle_name.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 14, str(entry.vehicle_type_id) if entry.vehicle_type_id else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 15,
                                           str(entry.reason_id.description) if entry.reason_id.description else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 16, str(entry.house_seq.name) if entry.house_seq.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 17, str(entry.exit_date) if entry.exit_date else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 18, str(entry.days_count) if entry.days_count else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 19, str(
                        entry.house_location.branch_ar_name) if entry.house_location.branch_ar_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 20, str(entry.state) if entry.state else "", main_heading_lines)
                    worksheet.write_string(rows, 21, str(entry.description) if entry.description else "",
                                           main_heading_lines)
                    rows += 1

                for exit in day_exit:
                    worksheet.write_string(rows, 0, str(exit.name), main_heading_lines)
                    worksheet.write_string(rows, 1, str(exit.entry_date), main_heading_lines)
                    worksheet.write_string(rows, 2, str(exit.employee_code), main_heading_lines)
                    worksheet.write_string(rows, 3, str(exit.employee_id.name) if exit.employee_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 4,
                                           str(
                                               exit.bsg_empiqama.bsg_iqama_name) if exit.bsg_empiqama.bsg_iqama_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 5, str(exit.mobile_phone) if exit.mobile_phone else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 6, str(exit.company_id.name) if exit.company_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 7,
                                           str(exit.branch_id.branch_ar_name) if exit.branch_id.branch_ar_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 8,
                                           str(
                                               exit.department_id.complete_name) if exit.department_id.complete_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 9, str(exit.job_id.name) if exit.job_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 11,
                                           str(exit.analytic_tag_ids.name) if exit.analytic_tag_ids.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 10,
                                           str(exit.analytic_account_id.name) if exit.analytic_account_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 12, str(exit.sticker_no) if exit.sticker_no else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 13, str(exit.vehicle_name.name) if exit.vehicle_name.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 14, str(exit.vehicle_type_id) if exit.vehicle_type_id else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 15,
                                           str(exit.reason_id.description) if exit.reason_id.description else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 16, str(exit.name) if exit.name else "", main_heading_lines)
                    worksheet.write_string(rows, 17, str(exit.date) if exit.date else "", main_heading_lines)
                    worksheet.write_string(rows, 18, str(exit.days_count) if exit.days_count else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 19, str(
                        exit.house_location.branch_ar_name) if exit.house_location.branch_ar_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 20, str(exit.state) if exit.state else "", main_heading_lines)
                    worksheet.write_string(rows, 21, str(exit.description) if exit.description else "",
                                           main_heading_lines)
                    rows += 1





