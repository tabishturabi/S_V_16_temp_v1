from odoo import models
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
from ummalqura.hijri_date import HijriDate
import json


class SimCardMovementReport(models.AbstractModel):
    _name = 'report.sim_card.sim_card_report_temp_xlsx'
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

        main_heading2 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#00cc44',
            'font_size': '12',
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

        worksheet = workbook.add_worksheet('Sim Card Movement Report' + str('report'))
        worksheet.set_column('A:A', 38)
        worksheet.set_column('B:P', 20)
        worksheet.freeze_panes(3, 0)
        eng_name = ""
        ar_name = ""
        if not data.report_mode:
            eng_name = "SIM Card Movement Report "
            ar_name = "تقرير حركة شرائح البيانات"
        if data.report_mode == 'sim_card_delivery':
            eng_name = "SIM Card Movement Report by Delivery"
            ar_name = " تقرير حركة شرائح البيانات حسب التسليم"
        if data.report_mode == 'sim_card_receipt':
            eng_name = "SIM Card Movement Report by Receipts"
            ar_name = "تقرير حركة شرائح البيانات حسب الاستلام"

        if data.report_mode == 'sim_card_upgrade':
            eng_name = "SIM Card Movement Report by Upgrade "
            ar_name = "تقرير حركة شرائح البيانات حسب ترقية الشريحة"

        if data.report_mode == 'sim_card_lost':
            eng_name = "Replacement for Lost  SIM Request"
            ar_name = "طلب بدل فاقد لشريحة تقرير"


        rows = 0
        worksheet.merge_range(rows, 0, rows, 15, eng_name, main_heading_right_side)
        rows += 1
        worksheet.merge_range(rows, 0, rows, 15, ar_name, main_heading_right_side)
        rows += 1

        domain = []

        col = 0
        if data.mble_no:
            domain += [('id', 'in', data.mble_no.ids)]
            worksheet.write(rows, col, 'Mobile NO', main_heading_right_side)
            rec_names = data.mble_no.mapped('mble_no')
            names = ','.join(rec_names)
            worksheet.write_string(rows, col + 1, str(names), main_heading_right_side)
            rows += 1

        col = 0
        if data.branch_id:
            domain += [('branch_id', 'in', data.branch_id.ids)]
            worksheet.write(rows, col, 'Branches', main_heading_right_side)
            rec_names = data.branch_id.mapped('branch_ar_name')
            names = ','.join(rec_names)
            worksheet.write_string(rows, col + 1, str(names), main_heading_right_side)
            rows += 1

        col = 0
        if data.department_id:
            domain += [('department_id', 'in', data.department_id.ids)]
            worksheet.write(rows, col, 'Departments', main_heading_right_side)
            rec_names = data.department_id.mapped('display_name')
            names = ','.join(rec_names)
            worksheet.write_string(rows, col + 1, str(names), main_heading_right_side)
            rows += 1

        col = 0
        if data.job_id:
            domain += [('job_id', 'in', data.job_id.ids)]
            worksheet.write(rows, col, 'Job Position', main_heading_right_side)
            rec_names = data.job_id.mapped('name')
            names = ','.join(rec_names)
            worksheet.write_string(rows, col + 1, str(names), main_heading_right_side)
            rows += 1

        col = 0
        if data.pkg_id:
            domain += [('pkg_id', 'in', data.pkg_id.ids)]
            worksheet.write(rows, col, 'Package', main_heading_right_side)
            rec_names = data.pkg_id.mapped('name')
            names = ','.join(rec_names)
            worksheet.write_string(rows, col + 1, str(names), main_heading_right_side)
            rows += 1

        col = 0
        if data.sim_type:
            domain += [('sim_type', 'in', data.sim_type)]
            worksheet.write(rows, col, 'Sim Type', main_heading_right_side)
            worksheet.write_string(rows, col + 1, str(data.sim_type), main_heading_right_side)
            rows += 1

        col = 0
        if data.is_cost:
            domain += [('sim_type', 'in', data.is_cost)]
            worksheet.write(rows, col, 'Bear The Cost', main_heading_right_side)
            worksheet.write_string(rows, col + 1, str(data.is_cost), main_heading_right_side)
            rows += 1

        col = 0
        if data.day_condition:
            domain += [('day_condition', 'in', data.day_condition)]
            worksheet.write(rows, col, 'Date Condition', main_heading_right_side)
            worksheet.write_string(rows, col + 1, str(data.day_condition), main_heading_right_side)
            rows += 1

        col = 0
        if data.date_from:
            domain += [('day_condition', 'in', data.date_from)]
            worksheet.write(rows, col, 'Date From', main_heading_right_side)
            worksheet.write_string(rows, col + 1, str(data.date_from), main_heading_right_side)
            rows += 1

        col = 0
        if data.date_to:
            domain += [('day_condition', 'in', data.date_to)]
            worksheet.write(rows, col, 'Date To', main_heading_right_side)
            worksheet.write_string(rows, col + 1, str(data.date_to), main_heading_right_side)
            rows += 1

        worksheet.write(rows, 0, 'Date', main_heading_top)
        worksheet.write(rows, 1, 'Reference', main_heading_top)
        worksheet.write(rows, 2, 'Transaction type', main_heading_top)
        worksheet.write(rows, 3, 'Package Type Name', main_heading_top)
        worksheet.write(rows, 4, 'Service Provider ', main_heading_top)
        worksheet.write(rows, 5, 'Employee Id ', main_heading_top)
        worksheet.write(rows, 6, 'Employee Name', main_heading_top)
        worksheet.write(rows, 7, 'Company Name', main_heading_top)
        worksheet.write(rows, 8, 'Department Name', main_heading_top)
        worksheet.write(rows, 9, 'Branch Name', main_heading_top)
        worksheet.write(rows, 10, 'Job Position', main_heading_top)
        worksheet.write(rows, 11, 'Bear The Cost', main_heading_top)
        worksheet.write(rows, 12, 'Sim Card Type', main_heading_top)
        worksheet.write(rows, 13, 'Request No.', main_heading_top)
        worksheet.write(rows, 14, 'Request Date', main_heading_top)
        worksheet.write(rows, 15, 'Description', main_heading_top)
        rows += 1

        worksheet.write(rows, 0, 'التاريخ', main_heading_top)
        worksheet.write(rows, 1, 'المرجع', main_heading_top)
        worksheet.write(rows, 2, 'نوع الحركة', main_heading_top)
        worksheet.write(rows, 3, 'اسم الباقة', main_heading_top)
        worksheet.write(rows, 4, 'مزود الخدمة', main_heading_top)
        worksheet.write(rows, 5, 'كود الموظف', main_heading_top)
        worksheet.write(rows, 6, 'اسم الموظف', main_heading_top)
        worksheet.write(rows, 7, 'اسم الشركة', main_heading_top)
        worksheet.write(rows, 8, 'اسم الإدارة', main_heading_top)
        worksheet.write(rows, 9, 'اسم الفرع', main_heading_top)
        worksheet.write(rows, 10, 'اسم الوظيفة', main_heading_top)
        worksheet.write(rows, 11, 'علي حساب', main_heading_top)
        worksheet.write(rows, 12, 'نوع الشريحة', main_heading_top)
        worksheet.write(rows, 13, 'رقم الطلب', main_heading_top)
        worksheet.write(rows, 14, 'تاريخ الطلب', main_heading_top)
        worksheet.write(rows, 15, 'الوصف', main_heading_top)

        domain_delivery = []
        domain_receipt = []
        domain_upgrade = []

        if not data.report_mode:
            self.env.ref(
                'sim_card.sim_card_report_id').report_file = "SIM CARD Movement Report"
            if data.pkg_id:
                domain_delivery += [('pkg_id', 'in', data.pkg_id.ids)]
                domain_upgrade += [('pkg_id', 'in', data.pkg_id.ids)]
                domain_receipt += [('pkg_id', 'in', data.pkg_id.ids)]
            if data.job_id:
                domain_delivery += [('job_id', 'in', data.job_id.ids)]
                domain_receipt += [('job_id', 'in', data.job_id.ids)]
                domain_upgrade += [('job_id', 'in', data.job_id.ids)]
            if data.branch_id:
                domain_delivery += [('branch_id', 'in', data.branch_id.ids)]
                domain_receipt += [('branch_id', 'in', data.branch_id.ids)]
                domain_upgrade += [('branch_id', 'in', data.branch_id.ids)]
            if data.department_id:
                domain_delivery += [('department_id', 'in', data.department_id.ids)]
                domain_receipt += [('department_id', 'in', data.department_id.ids)]
                domain_upgrade += [('department_id', 'in', data.department_id.ids)]
            if data.mble_no:
                domain_delivery += [('mble_no', 'in', data.mble_no.ids)]
                domain_receipt += [('mble_no', 'in', data.mble_no.ids)]
                domain_upgrade += [('mble_no', 'in', data.mble_no.ids)]
            if data.sim_type == 'voice':
                domain_delivery += [('sim_type', '=', 'voice')]
                domain_upgrade += [('sim_type', '=', 'voice')]
                domain_receipt += [('sim_type', '=', 'voice')]
            if data.sim_type == 'data':
                domain_delivery += [('sim_type', '=', 'data')]
                domain_upgrade += [('sim_type', '=', 'data')]
                domain_receipt += [('sim_type', '=', 'data')]
            if data.is_cost == 'employee':
                domain_delivery += [('is_cost', '=', 'employee')]
                domain_upgrade += [('is_cost', '=', 'employee')]
                domain_receipt += [('is_cost', '=', 'employee')]
            if data.is_cost == 'company':
                domain_delivery += [('is_cost', '=', 'company')]
                domain_upgrade += [('is_cost', '=', 'company')]
                domain_receipt += [('is_cost', '=', 'company')]
            if data.day_condition == 'is equal to':
                domain_delivery += [('date1', '=', data.date_from)]
                domain_receipt += [('date1', '=', data.date_from)]
                domain_upgrade += [('date1', '=', data.date_from)]
            if data.day_condition == 'is not equal to':
                domain_delivery += [('date1', '!=', data.date_from)]
                domain_receipt += [('date1', '!=', data.date_from)]
                domain_upgrade += [('date1', '!=', data.date_from)]
            if data.day_condition == 'is after':
                domain_delivery += [('date1', '>', data.date_from)]
                domain_receipt += [('date1', '>', data.date_from)]
                domain_upgrade += [('date1', '>', data.date_from)]
            if data.day_condition == 'is before':
                domain_delivery += [('date1', '<', data.date_from)]
                domain_receipt += [('date1', '<', data.date_from)]
                domain_upgrade += [('date1', '<', data.date_from)]
            if data.day_condition == 'is after or equal to':
                domain_delivery += [('date1', '>=', data.date_from)]
                domain_receipt += [('date1', '>=', data.date_from)]
                domain_upgrade += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is before or equal to':
                domain_delivery += [('date1', '<=', data.date_from)]
                domain_receipt += [('date1', '<=', data.date_from)]
                domain_upgrade += [('date1', '<=', data.date_from)]
            if data.day_condition == 'is between':
                domain_delivery += [('date1', '>=', data.date_from)]
                domain_receipt += [('date1', '>=', data.date_from)]
                domain_upgrade += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is set':
                domain_delivery += [('date1', '!=', False)]
                domain_receipt += [('date1', '!=', False)]
                domain_upgrade += [('date1', '!=', False)]
            if data.day_condition == 'is not set':
                domain_delivery += [('date1', '=', False)]
                domain_receipt += [('date1', '=', False)]
                domain_upgrade += [('date1', '=', False)]


            mobile_list = []
            mobile_numbers = self.env['sim.card.delivery'].sudo().read_group(domain_delivery, fields=['mble_no'], groupby=['mble_no'], lazy=False)
            for mobile in mobile_numbers:
                mobile_list.append(mobile['mble_no'][0])
            rows += 1
            for rec in mobile_list:
                d1 = self.env['sim.card.delivery'].sudo().search([('mble_no.id', '=', rec)])
                d2 = self.env['sim.card.receipt'].sudo().search([('mble_no.id', '=', rec)])
                d3 = self.env['upgrade.request'].sudo().search([('mble_no.id', '=', rec)])

                worksheet.write(rows, 0, 'Mobile Number', main_heading_top)
                worksheet.write_string(rows, 1, str(self.env['sim.card.define'].browse(rec).mble_no), main_heading_top)
                rows += 1
                for d in d1:
                    worksheet.write_string(rows, 0, str(d.date), main_heading_lines)
                    worksheet.write_string(rows, 1, str(d.name), main_heading_lines)
                    worksheet.write_string(rows, 2, str(d.transaction_type), main_heading_lines)
                    worksheet.write_string(rows, 3, str(d.pkg_id.name) if d.pkg_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 4, str(d.mble_no.service_id.name) if d.mble_no.service_id.name  else "", main_heading_lines)
                    worksheet.write_string(rows, 5, str(d.employee_id.employee_code) if d.employee_id.employee_code  else "", main_heading_lines)
                    worksheet.write_string(rows, 6, str(d.employee_id.name) if d.employee_id.name  else "", main_heading_lines)
                    worksheet.write_string(rows, 7, str(d.company_id.name) if d.company_id.name  else "", main_heading_lines)
                    worksheet.write_string(rows, 8, str(d.department_id.complete_name) if d.department_id.complete_name  else "", main_heading_lines)
                    worksheet.write_string(rows, 9, str(d.branch_id.branch_ar_name) if d.branch_id.branch_ar_name  else "", main_heading_lines)
                    worksheet.write_string(rows, 10, str(d.job_id.name) if d.job_id.name  else "", main_heading_lines)
                    worksheet.write_string(rows, 11, str(d.is_cost) if d.is_cost  else "", main_heading_lines)
                    worksheet.write_string(rows, 12, str(d.sim_type) if d.sim_type  else "", main_heading_lines)
                    worksheet.write_string(rows, 13, str(d.name_id.name) if d.name_id.name  else "", main_heading_lines)
                    worksheet.write_string(rows, 14, str(d.name_id.date) if d.name_id.date  else "", main_heading_lines)
                    worksheet.write_string(rows, 15, str(d.description) if d.description  else "", main_heading_lines)
                    rows += 1

                for r in d2:

                    worksheet.write_string(rows, 0, str(r.date), main_heading_lines)
                    worksheet.write_string(rows, 1, str(r.name), main_heading_lines)
                    worksheet.write_string(rows, 2, str(r.transaction_type), main_heading_lines)
                    worksheet.write_string(rows, 3, str(r.pkg_id.name) if r.pkg_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 4, str(r.mble_no.service_id.name) if r.mble_no.service_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 5, str(r.employee_id.employee_code) if r.employee_id.employee_code else "", main_heading_lines)
                    worksheet.write_string(rows, 6, str(r.employee_id.name) if r.employee_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 7, str(r.company_id.name) if r.company_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 8, str(r.department_id.complete_name) if r.department_id.complete_name else "", main_heading_lines)
                    worksheet.write_string(rows, 9, str(r.branch_id.branch_ar_name) if r.branch_id.branch_ar_name else "", main_heading_lines)
                    worksheet.write_string(rows, 10, str(r.job_id.name) if r.job_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 11, str(r.is_cost) if r.is_cost else "", main_heading_lines)
                    worksheet.write_string(rows, 12, str(r.sim_type) if r.sim_type else "", main_heading_lines)
                    worksheet.write_string(rows, 13, str(r.delivery_seq_id.name) if r.delivery_seq_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 14, str(r.delivery_seq_id.date) if r.delivery_seq_id.date else "", main_heading_lines)
                    worksheet.write_string(rows, 15, str(r.description) if r.description else "", main_heading_lines)
                    rows += 1

                for u in d3:
                    worksheet.write_string(rows, 0, str(u.date), main_heading_lines)
                    worksheet.write_string(rows, 1, str(u.name), main_heading_lines)
                    worksheet.write_string(rows, 2, str(u.transaction_type), main_heading_lines)
                    worksheet.write_string(rows, 3, str(u.pkg_id.name) if u.pkg_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 4, str(u.service_id.name) if u.service_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 5, str(u.employee_id.employee_code) if u.employee_id.employee_code else "", main_heading_lines)
                    worksheet.write_string(rows, 6, str(u.employee_id.name) if u.employee_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 7, str(u.company_id.name) if u.company_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 8, str(u.department_id.complete_name) if u.department_id.complete_name else "", main_heading_lines)
                    worksheet.write_string(rows, 9, str(u.branch_id.branch_ar_name) if u.branch_id.branch_ar_name else "", main_heading_lines)
                    worksheet.write_string(rows, 10, str(u.job_id.name) if u.job_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 11, str(u.is_cost) if u.is_cost else "", main_heading_lines)
                    worksheet.write_string(rows, 12, str(u.sim_type) if u.sim_type else "", main_heading_lines)
                    worksheet.write_string(rows, 13, '', main_heading_lines)
                    worksheet.write_string(rows, 14, '', main_heading_lines)
                    worksheet.write_string(rows, 15, str(u.description) if u.description else "", main_heading_lines)
                    rows += 1
                worksheet.write(rows, 0, 'Total', main_heading_top)
                worksheet.write_number(rows, 1, len(d1)+len(d2)+len(d3), main_heading_top)
                worksheet.write(rows, 2, 'الإجمالي', main_heading_top)

                rows += 1
        d_delivery = []
        if data.report_mode == 'sim_card_delivery':
            self.env.ref('sim_card.sim_card_report_id').report_file = "SIM CARD Movement Report by Delivery"

            if data.mble_no:
                d_delivery += [('mble_no', 'in', data.mble_no.ids)]
            if data.pkg_id:
                d_delivery += [('pkg_id', 'in', data.pkg_id.ids)]
            if data.job_id:
                d_delivery += [('job_id', 'in', data.job_id.ids)]
            if data.branch_id:
                d_delivery += [('branch_id', 'in', data.branch_id.ids)]
            if data.department_id:
                d_delivery += [('department_id', 'in', data.department_id.ids)]
            if data.department_id:
                d_delivery += [('department_id', 'in', data.department_id.ids)]
            if data.sim_type == 'voice':
                d_delivery += [('sim_type', '=', 'voice')]
            if data.sim_type == 'data':
                d_delivery += [('sim_type', '=', 'data')]
            if data.is_cost == 'employee':
                d_delivery += [('is_cost', '=', 'employee')]
            if data.is_cost == 'company':
                d_delivery += [('is_cost', '=', 'company')]
            if data.day_condition == 'is equal to':
                d_delivery += [('date1', '=', data.date_from)]
            if data.day_condition == 'is not equal to':
                d_delivery += [('date1', '!=', data.date_from)]
            if data.day_condition == 'is after':
                d_delivery += [('date1', '>', data.date_from)]
            if data.day_condition == 'is before':
                d_delivery += [('date1', '<', data.date_from)]
            if data.day_condition == 'is after or equal to':
                d_delivery += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is before or equal to':
                d_delivery += [('date1', '<=', data.date_from)]
            if data.day_condition == 'is between':
                d_delivery += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is set':
                d_delivery += [('date1', '!=', False)]
            if data.day_condition == 'is not set':
                d_delivery += [('date1', '=', False)]
            d_delivery_data = self.env['sim.card.delivery'].sudo().search(d_delivery)

            mobile_list = []
            mobile_numbers = self.env['sim.card.delivery'].read_group(domain_delivery, fields=['mble_no'],
                                                                      groupby=['mble_no'], lazy=False)
            for mobile in mobile_numbers:
                mobile_list.append(mobile['mble_no'][0])
            print("MMMMMMMMMMMMM", mobile_list)
            rows += 1
            for md in mobile_list:
                worksheet.write(rows, 0, 'Mobile Number', main_heading_top)
                worksheet.write_string(rows, 1, str(self.env['sim.card.define'].browse(md).mble_no),
                                       main_heading_top)
                rows += 1
                d1 = self.env['sim.card.delivery'].sudo().search([('mble_no.id', '=', md)])
                for rec in d1:
                    worksheet.write_string(rows, 0, str(rec.date) if rec.date else "", main_heading_lines)
                    worksheet.write_string(rows, 1, str(rec.name), main_heading_lines)
                    worksheet.write_string(rows, 2, str(rec.transaction_type), main_heading_lines)
                    worksheet.write_string(rows, 3, str(rec.pkg_id.name) if rec.pkg_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 4, str(rec.mble_no.service_id.name) if rec.mble_no.service_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 5, str(rec.employee_id.employee_code) if rec.employee_id.employee_code else "", main_heading_lines)
                    worksheet.write_string(rows, 6, str(rec.employee_id.name) if rec.employee_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 7, str(rec.company_id.name) if rec.company_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 8, str(rec.department_id.complete_name) if rec.department_id.complete_name else "", main_heading_lines)
                    worksheet.write_string(rows, 9, str(rec.branch_id.branch_ar_name) if rec.branch_id.branch_ar_name else "", main_heading_lines)
                    worksheet.write_string(rows, 10, str(rec.job_id.name) if rec.job_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 11, str(rec.is_cost) if rec.is_cost else "", main_heading_lines)
                    worksheet.write_string(rows, 12, str(rec.sim_type) if rec.sim_type else "", main_heading_lines)
                    worksheet.write_string(rows, 13, str(rec.name_id.name) if rec.name_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 14, str(rec.name_id.date) if rec.name_id.date else "", main_heading_lines)
                    worksheet.write_string(rows, 15, str(rec.description) if rec.description else "", main_heading_lines)

                    rows += 1
                worksheet.write(rows, 0, 'Total', main_heading_top)
                worksheet.write_number(rows, 1, len(d1), main_heading_top)
                worksheet.write(rows, 2, 'الإجمالي', main_heading_top)

                rows += 1

        r_receipt = []
        if data.report_mode == 'sim_card_receipt':
            self.env.ref('sim_card.sim_card_report_id').report_file = "SIM CARD Movement Report by Receipt"
            if data.mble_no:
                r_receipt += [('mble_no', 'in', data.mble_no.ids)]
            if data.pkg_id:
                r_receipt += [('pkg_id', 'in', data.pkg_id.ids)]
            if data.job_id:
                r_receipt += [('job_id', 'in', data.job_id.ids)]
            if data.branch_id:
                r_receipt += [('branch_id', 'in', data.branch_id.ids)]
            if data.department_id:
                r_receipt += [('department_id', 'in', data.department_id.ids)]
            if data.department_id:
                r_receipt += [('department_id', 'in', data.department_id.ids)]
            if data.sim_type == 'voice':
                r_receipt += [('sim_type', '=', 'voice')]
            if data.sim_type == 'data':
                r_receipt += [('sim_type', '=', 'data')]
            if data.is_cost == 'employee':
                r_receipt += [('is_cost', '=', 'employee')]
            if data.is_cost == 'company':
                r_receipt += [('is_cost', '=', 'company')]
            if data.day_condition == 'is equal to':
                r_receipt += [('date1', '=', data.date_from)]
            if data.day_condition == 'is not equal to':
                r_receipt += [('date1', '!=', data.date_from)]
            if data.day_condition == 'is after':
                r_receipt += [('date1', '>', data.date_from)]
            if data.day_condition == 'is before':
                r_receipt += [('date1', '<', data.date_from)]
            if data.day_condition == 'is after or equal to':
                r_receipt += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is before or equal to':
                r_receipt += [('date1', '<=', data.date_from)]
            if data.day_condition == 'is between':
                r_receipt += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is set':
                r_receipt += [('date1', '!=', False)]
            if data.day_condition == 'is not set':
                r_receipt += [('date1', '=', False)]
            r_receipt_data = self.env['sim.card.receipt'].sudo().search(r_receipt)

            mobile_list = []
            mobile_numbers = self.env['sim.card.receipt'].read_group(domain_receipt, fields=['mble_no'],
                                                                     groupby=['mble_no'], lazy=False)
            for mobile in mobile_numbers:
                mobile_list.append(mobile['mble_no'][0])
            rows += 1
            for cd in mobile_list:
                worksheet.write(rows, 0, 'Mobile Number', main_heading_top)
                worksheet.write_string(rows, 1, str(self.env['sim.card.define'].browse(cd).mble_no),
                                       main_heading_top)
                rows += 1
                c1 = self.env['sim.card.receipt'].sudo().search([('mble_no.id', '=', cd)])

                for r in c1:
                    worksheet.write_string(rows, 0, str(r.date) if r.date else "", main_heading_lines)
                    worksheet.write_string(rows, 1, str(r.name) if r.name else "", main_heading_lines)
                    worksheet.write_string(rows, 2, str(r.transaction_type) if r.name else "", main_heading_lines)
                    worksheet.write_string(rows, 3, str(r.pkg_id.name) if r.pkg_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 4, str(r.mble_no.service_id.name) if r.mble_no.service_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 5, str(r.employee_id.employee_code) if r.employee_id.employee_code else "", main_heading_lines)
                    worksheet.write_string(rows, 6, str(r.employee_id.name) if r.employee_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 7, str(r.company_id.name) if r.company_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 8, str(r.department_id.complete_name) if r.department_id.complete_name else "", main_heading_lines)
                    worksheet.write_string(rows, 9, str(r.branch_id.branch_ar_name) if r.branch_id.branch_ar_name else "", main_heading_lines)
                    worksheet.write_string(rows, 10, str(r.job_id.name) if r.job_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 11, str(r.is_cost) if r.is_cost else "", main_heading_lines)
                    worksheet.write_string(rows, 12, str(r.sim_type) if r.sim_type else "", main_heading_lines)
                    worksheet.write_string(rows, 13, str(r.delivery_seq_id.name) if r.delivery_seq_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 14, str(r.delivery_seq_id.date) if r.delivery_seq_id else "", main_heading_lines)
                    worksheet.write_string(rows, 15, str(r.description) if r.description else "", main_heading_lines)
                    rows += 1

                worksheet.write(rows, 0, 'Total', main_heading_top)
                worksheet.write_number(rows, 1, len(c1), main_heading_top)
                worksheet.write(rows, 2, 'الإجمالي', main_heading_top)

                rows += 1

        u_receipt = []
        if data.report_mode == 'sim_card_upgrade':
            self.env.ref('sim_card.sim_card_report_id').report_file = "SIM CARD Movement Report by Upgrade"
            if data.mble_no:
                u_receipt += [('mble_no', 'in', data.mble_no.ids)]
            if data.pkg_id:
                u_receipt += [('pkg_id', 'in', data.pkg_id.ids)]
            if data.job_id:
                u_receipt += [('job_id', 'in', data.job_id.ids)]
            if data.branch_id:
                u_receipt += [('branch_id', 'in', data.branch_id.ids)]
            if data.department_id:
                u_receipt += [('department_id', 'in', data.department_id.ids)]
            if data.department_id:
                u_receipt += [('department_id', 'in', data.department_id.ids)]
            if data.sim_type == 'voice':
                u_receipt += [('sim_type', '=', 'voice')]
            if data.sim_type == 'data':
                u_receipt += [('sim_type', '=', 'data')]
            if data.is_cost == 'employee':
                u_receipt += [('is_cost', '=', 'employee')]
            if data.is_cost == 'company':
                u_receipt += [('is_cost', '=', 'company')]
            if data.day_condition == 'is equal to':
                u_receipt += [('date1', '=', data.date_from)]
            if data.day_condition == 'is not equal to':
                u_receipt += [('date1', '!=', data.date_from)]
            if data.day_condition == 'is after':
                u_receipt += [('date1', '>', data.date_from)]
            if data.day_condition == 'is before':
                u_receipt += [('date1', '<', data.date_from)]
            if data.day_condition == 'is after or equal to':
                u_receipt += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is before or equal to':
                u_receipt += [('date1', '<=', data.date_from)]
            if data.day_condition == 'is between':
                u_receipt += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is set':
                u_receipt += [('date1', '!=', False)]
            if data.day_condition == 'is not set':
                u_receipt += [('date1', '=', False)]
            u_upgrade_data = self.env['upgrade.request'].sudo().search(u_receipt)

            mobile_list = []
            mobile_numbers = self.env['upgrade.request'].read_group(domain_upgrade, fields=['mble_no'],
                                                                     groupby=['mble_no'], lazy=False)
            for mobile in mobile_numbers:
                mobile_list.append(mobile['mble_no'][0])
            rows += 1
            for ud in mobile_list:
                worksheet.write(rows, 0, 'Mobile Number', main_heading_top)
                worksheet.write_string(rows, 1, str(self.env['sim.card.define'].browse(ud).mble_no),
                                       main_heading_top)
                rows += 1
                up_data = self.env['upgrade.request'].sudo().search([('mble_no.id', '=', ud)])
                for c in up_data:
                    worksheet.write_string(rows, 0, str(c.date), main_heading_lines)
                    worksheet.write_string(rows, 1, str(c.name), main_heading_lines)
                    worksheet.write_string(rows, 2, str(c.transaction_type), main_heading_lines)
                    worksheet.write_string(rows, 3, str(c.pkg_id.name) if c.pkg_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 4, str(c.service_id.name) if c.service_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 5, str(c.employee_id.employee_code) if c.employee_id.employee_code else "", main_heading_lines)
                    worksheet.write_string(rows, 6, str(c.employee_id.name) if c.employee_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 7, str(c.company_id.name) if c.company_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 8, str(c.department_id.complete_name) if c.department_id.complete_name else "", main_heading_lines)
                    worksheet.write_string(rows, 9, str(c.branch_id.branch_ar_name) if c.branch_id.branch_ar_name else "", main_heading_lines)
                    worksheet.write_string(rows, 10, str(c.job_id.name) if c.job_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 11, str(c.is_cost) if c.is_cost else "", main_heading_lines)
                    worksheet.write_string(rows, 12, str(c.sim_type) if c.sim_type else "", main_heading_lines)
                    worksheet.write_string(rows, 13, "", main_heading_lines)
                    worksheet.write_string(rows, 14, "", main_heading_lines)
                    worksheet.write_string(rows, 15, str(c.description) if c.description else "", main_heading_lines)
                    rows += 1
                # worksheet.write(rows, 0, 'Total '+str(len(up_data)), main_heading_top)
                worksheet.write(rows, 0, 'Total', main_heading_top)
                worksheet.write_number(rows, 1, len(up_data), main_heading_top)
                worksheet.write(rows, 2, 'الإجمالي', main_heading_top)

                rows += 1

        lost_receipt = []
        if data.report_mode == 'sim_card_lost':
            self.env.ref('sim_card.sim_card_report_id').report_file = "Replacement for Lost  SIM Request"
            if data.mble_no:
                lost_receipt += [('mble_no', 'in', data.mble_no.ids)]
            if data.pkg_id:
                lost_receipt += [('pkg_id', 'in', data.pkg_id.ids)]
            if data.job_id:
                lost_receipt += [('job_id', 'in', data.job_id.ids)]
            if data.branch_id:
                lost_receipt += [('branch_id', 'in', data.branch_id.ids)]
            if data.department_id:
                lost_receipt += [('department_id', 'in', data.department_id.ids)]
            if data.department_id:
                lost_receipt += [('department_id', 'in', data.department_id.ids)]
            if data.sim_type == 'voice':
                lost_receipt += [('sim_type', '=', 'voice')]
            if data.sim_type == 'data':
                lost_receipt += [('sim_type', '=', 'data')]
            if data.is_cost == 'employee':
                lost_receipt += [('is_cost', '=', 'employee')]
            if data.is_cost == 'company':
                lost_receipt += [('is_cost', '=', 'company')]
            if data.day_condition == 'is equal to':
                lost_receipt += [('date1', '=', data.date_from)]
            if data.day_condition == 'is not equal to':
                lost_receipt += [('date1', '!=', data.date_from)]
            if data.day_condition == 'is after':
                lost_receipt += [('date1', '>', data.date_from)]
            if data.day_condition == 'is before':
                lost_receipt += [('date1', '<', data.date_from)]
            if data.day_condition == 'is after or equal to':
                lost_receipt += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is before or equal to':
                lost_receipt += [('date1', '<=', data.date_from)]
            if data.day_condition == 'is between':
                lost_receipt += [('date1', '>=', data.date_from)]
            if data.day_condition == 'is set':
                lost_receipt += [('date1', '!=', False)]
            if data.day_condition == 'is not set':
                lost_receipt += [('date1', '=', False)]
            u_upgrade_data = self.env['lost.request'].sudo().search(lost_receipt)

            mobile_list = []
            mobile_numbers = self.env['lost.request'].read_group(domain_upgrade, fields=['mble_no'],
                                                                    groupby=['mble_no'], lazy=False)
            for mobile in mobile_numbers:
                mobile_list.append(mobile['mble_no'][0])
            rows += 1
            for ud in mobile_list:
                worksheet.write(rows, 0, 'Mobile Number', main_heading_top)
                worksheet.write_string(rows, 1, str(self.env['sim.card.define'].browse(ud).mble_no),
                                       main_heading_top)
                rows += 1
                up_data = self.env['lost.request'].sudo().search([('mble_no.id', '=', ud)])
                for c in up_data:
                    worksheet.write_string(rows, 0, str(c.date), main_heading_lines)
                    worksheet.write_string(rows, 1, str(c.name), main_heading_lines)
                    worksheet.write_string(rows, 2, str(c.transaction_type), main_heading_lines)
                    worksheet.write_string(rows, 3, str(c.pkg_id.name) if c.pkg_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 4, str(c.service_id.name) if c.service_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 5,
                                           str(c.employee_id.employee_code) if c.employee_id.employee_code else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 6, str(c.employee_id.name) if c.employee_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 7, str(c.company_id.name) if c.company_id.name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 8,
                                           str(c.department_id.complete_name) if c.department_id.complete_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 9,
                                           str(c.branch_id.branch_ar_name) if c.branch_id.branch_ar_name else "",
                                           main_heading_lines)
                    worksheet.write_string(rows, 10, str(c.job_id.name) if c.job_id.name else "", main_heading_lines)
                    worksheet.write_string(rows, 11, str(c.is_cost) if c.is_cost else "", main_heading_lines)
                    worksheet.write_string(rows, 12, str(c.sim_type) if c.sim_type else "", main_heading_lines)
                    worksheet.write_string(rows, 13, "", main_heading_lines)
                    worksheet.write_string(rows, 14, "", main_heading_lines)
                    worksheet.write_string(rows, 15, str(c.description) if c.description else "", main_heading_lines)
                    rows += 1
                # worksheet.write(rows, 0, 'Total '+str(len(up_data)), main_heading_top)
                worksheet.write(rows, 0, 'Total', main_heading_top)
                worksheet.write_number(rows, 1, len(up_data), main_heading_top)
                worksheet.write(rows, 2, 'الإجمالي', main_heading_top)

                rows += 1

