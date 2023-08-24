# -*- coding: utf-8 -*-
import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import models, fields, api, _
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta
import string

class HRPayslipXlsReport(models.TransientModel):
    _name = 'report.bsg_hr_xlsx.hr_payslip_xls_temp'
    _inherit = 'report.report_xlsx.abstract'
    
    
    
    # @api.multi
    def generate_xlsx_report(self, workbook, input_records, lines):
        data = input_records['form']
        category_ids = data.get('category_ids', [])
        salary_payment_method = data.get('salary_payment_method',False)
        if len(category_ids) == 0 and not salary_payment_method:
            lines = lines.slip_ids
        elif len(category_ids) > 0 and not salary_payment_method:
            lines = lines.slip_ids.filtered(lambda l: l.category_ids and l.category_ids[0].id in category_ids)
        elif len(category_ids) == 0 and salary_payment_method:
            lines = lines.slip_ids.filtered(lambda l: l.salary_payment_method == salary_payment_method)
        else:
            lines = lines.slip_ids.filtered(lambda l:l.salary_payment_method == salary_payment_method and  l.category_ids and l.category_ids[0].id in category_ids)
        if not lines:
            return ValidationError("NO records matching your selected filters!")
        total_wage = 0
        total_gross = 0
        total_net = 0
        rule_ids = self.env['hr.salary.rule'].search([], order='sequence')
        letters = list(string.ascii_uppercase)
        main_heading = workbook.add_format({
            "bold": 1, 
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color":'black',
            "bg_color": '#D3D3D3',
            'font_size': '10',
            })

        main_heading1 = workbook.add_format({
            "bold": 1, 
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color":'black',
            "bg_color": '#D3D3D3',
            'font_size': '14',
            })

        main_heading2 = workbook.add_format({
            "bold": 1, 
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color":'black',
            'font_size': '10',
            })

        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': '13',
            "font_color":'black',
            'bg_color': '#D3D3D3'})

        main_data = workbook.add_format({
            "align": 'left',
            "valign": 'vcenter',
            'font_size': '14',
            })
        merge_format.set_shrink()
        main_heading.set_text_justlast(1)
        main_data.set_border()
        worksheet = workbook.add_worksheet('HR Payroll Report')
        
        worksheet.merge_range('A1:F1',data['payslip_run_id'][1],merge_format)
        worksheet.write('A4', 'كود', main_heading1)
        worksheet.write('B4', 'اسم الموظف', main_heading1)
        worksheet.write('C4',  'الوظيفه', main_heading1)
        worksheet.write('D4',  'الادارة', main_heading1)
        worksheet.write('E4',  'الفرع', main_heading1)
        worksheet.write('F4',  'حالة الموظف', main_heading1)
        worksheet.write('G4',  'تاريخ التعيين', main_heading1)
        worksheet.write('H4',  'الجنسية', main_heading1)
        worksheet.write('I4',  'رقم الهوية', main_heading1)
        worksheet.write('J4',  'رقم الحساب البنكي', main_heading1)
        worksheet.write('K4',  'سوفت البنك', main_heading1)
        worksheet.write('L4',  'طريقة صرف الراتب', main_heading1)
        worksheet.write('M4',  'الوسم', main_heading1)
        i =13
        for rule in rule_ids:
            letter = i >25 and 'A'+letters[i-26] or letters[i]
            worksheet.write(letter+'4', rule.name, main_heading1)
            i+=1
       
        row = 4
        col = 0
        totals = {}
        for rec in lines:
            col = 0

            bsg_national_id = rec.employee_id.bsg_national_id
            iqama = rec.employee_id.bsg_empiqama

            driver_code = rec.employee_id.driver_code or ""
            emp_name = rec.employee_id.name or ""
            job = rec.job_id.name or ""
            department = rec.department_id.name or ""
            branch = rec.branch_id and rec.branch_id.branch_ar_name or ""
            employee_state = rec.employee_state and dict(rec._fields['employee_state'].selection)[rec.employee_state] or ""
            joining_date =  rec.contract_id.date_start and rec.contract_id.date_start.strftime("%m/%d/%Y") or ""
            country = rec.employee_id and rec.employee_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).country_id.name or ""
            id_iqama = (rec.employee_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).country_id.code == 'SA' and  bsg_national_id and bsg_national_id.bsg_nationality_name or "") or  (iqama and iqama.bsg_iqama_name or "") 
            back_account = rec.employee_id.bsg_bank_id and rec.employee_id.bsg_bank_id.bsg_acc_number or  ""
            swift_code = rec.employee_id.bsg_bank_id and rec.employee_id.bsg_bank_id.bsg_bank_name or ""
            salary_payment_method = rec.salary_payment_method and dict(rec._fields['salary_payment_method'].selection)[rec.salary_payment_method] or ""
            tags = rec.category_ids and ", ".join(rec.category_ids.mapped('name')) or ""

            worksheet.write_string (row, col,driver_code)
            worksheet.write_string (row, col+1,emp_name,main_data)
            worksheet.write_string (row, col+2,str(job),main_data)
            worksheet.write_string (row, col+3,department,main_data)
            worksheet.write_string (row, col+4,str(branch),main_data)
            worksheet.write_string (row, col+5, _(employee_state),main_data)
            worksheet.write_string (row, col+6,joining_date,main_data)
            worksheet.write_string (row, col+7,_(country),main_data)
            worksheet.write_string (row, col+8,_(id_iqama),main_data)
            worksheet.write_string (row, col+9,str(back_account),main_data)
            worksheet.write_string (row, col+10,str(swift_code),main_data)
            worksheet.write_string (row, col+11,_(salary_payment_method),main_data)
            worksheet.write_string (row, col+12,str(tags),main_data)
            col=13
            for rule in rule_ids:
                amount = sum(rec.line_ids.filtered(lambda l: l.salary_rule_id.id == rule.id).mapped('total'))
                amount = rule.category_id.code == 'DED' and abs(amount) or amount
                totals.update({rule.id:totals.get(rule.id, 0) + amount})
                worksheet.write_number (row, col, amount)
                col+=1
            row+=1
        col=13
        row+=2
        for total in totals.values():
             worksheet.write_number (row, col, total, main_heading2)
             col+=1
        
            
class HRPayslipXlsReport(models.TransientModel):
    _name = 'report.bsg_hr_xlsx.hr_payslip_xls_bank'
    _inherit = 'report.report_xlsx.abstract'
    
    
    
    # @api.multi
    def generate_xlsx_report(self, workbook, input_records, lines):
        data = input_records['form']
        category_ids = data.get('category_ids', [])
        salary_payment_method = data.get('salary_payment_method',False)
        if len(category_ids) == 0 and not salary_payment_method:
            lines = lines.slip_ids
        elif len(category_ids) > 0 and not salary_payment_method:
            lines = lines.slip_ids.filtered(lambda l: l.category_ids and l.category_ids[0].id in category_ids)
        elif len(category_ids) == 0 and salary_payment_method:
            lines = lines.slip_ids.filtered(lambda l: l.salary_payment_method == salary_payment_method)
        else:
            lines = lines.slip_ids.filtered(lambda l:l.salary_payment_method == salary_payment_method and  l.category_ids and l.category_ids[0].id in category_ids)
        if not lines:
            return ValidationError("NO records matching your selected filters!")
        total_wage = 0
        total_gross = 0
        total_net = 0
        rule_ids = self.env['hr.salary.rule'].search([], order='sequence')
        letters = list(string.ascii_uppercase)
        main_heading = workbook.add_format({
            "bold": 1, 
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color":'black',
            "bg_color": '#D3D3D3',
            'font_size': '10',
            })

        main_heading1 = workbook.add_format({
            "bold": 1, 
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color":'black',
            "bg_color": '#D3D3D3',
            'font_size': '14',
            })

        main_heading2 = workbook.add_format({
            "bold": 1, 
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color":'black',
            'font_size': '10',
            })

        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': '13',
            "font_color":'black',
            'bg_color': '#D3D3D3'})

        main_data = workbook.add_format({
            "align": 'left',
            "valign": 'vcenter',
            'font_size': '14',
            })
        merge_format.set_shrink()
        main_heading.set_text_justlast(1)
        main_data.set_border()
        worksheet = workbook.add_worksheet('HR Payroll Report')
        
        worksheet.merge_range('A1:F1',data['payslip_run_id'][1],merge_format)
        worksheet.write('A4', 'كود', main_heading1)
        worksheet.write('B4',  'رقم الهوية', main_heading1)
        worksheet.write('C4', 'الاسم', main_heading1)
        worksheet.write('D4',  ' الايبان البنكي', main_heading1)
        worksheet.write('E4',  'رمز البنك', main_heading1)
        worksheet.write('F4',  'الصافي', main_heading1)
        worksheet.write('G4',  'الاساسي', main_heading1)
        worksheet.write('H4',  'بدل سكن', main_heading1)
        worksheet.write('I4',  'البدلات الاخرى', main_heading1)
        worksheet.write('J4',  'جميع الخصومات', main_heading1)
        i =10
        # for rule in rule_ids:
        #     letter = i >25 and 'A'+letters[i-26] or letters[i]
        #     worksheet.write(letter+'4', rule.name, main_heading1)
        #     i+=1
       
        row = 4
        col = 0
        totals = {}
        for rec in lines:
            col = 0

            bsg_national_id = rec.employee_id.bsg_national_id
            iqama = rec.employee_id.bsg_empiqama

            driver_code = rec.employee_id.driver_code or ""
            emp_name = rec.employee_id.name or ""
            country = rec.employee_id and rec.employee_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).country_id.name or ""
            id_iqama = (rec.employee_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).country_id.code == 'SA' and  bsg_national_id and bsg_national_id.bsg_nationality_name or "") or  (iqama and iqama.bsg_iqama_name or "") 
            back_account = rec.employee_id.bsg_bank_id and rec.employee_id.bsg_bank_id.bsg_acc_number or  ""
            swift_code = rec.employee_id.bsg_bank_id and rec.employee_id.bsg_bank_id.bsg_bank_name or ""
            net_salary = rec.line_ids.filtered(lambda line: line.code == 'NET').total or 0.0
            basic_salary = rec.line_ids.filtered(lambda line: line.code == 'BASIC').total or 0.0
            if self.env.user.company_id.company_code == "BIC":
                housing_allow = sum(
                    rec.line_ids.filtered(lambda line: line.code in ['HRA2', 'HRA3', 'HA20']).mapped('total')) or 0.0
            else:
                housing_allow = sum(
                    rec.line_ids.filtered(lambda line: line.code in ['HRA2', 'HRA3']).mapped('total')) or 0.0
            other_allow = sum(rec.line_ids.filtered(lambda line: line.category_id.code == 'ALW').mapped('total')) or 0.0
            total_deduct = sum(rec.line_ids.filtered(lambda line: line.category_id.code == 'DED').mapped('total')) or 0.0
            worksheet.write_string (row, col,str(driver_code))
            worksheet.write_string (row, col+1,str(id_iqama),main_data)
            worksheet.write_string (row, col+2,str(emp_name),main_data)
            worksheet.write_string (row, col+3,str(back_account),main_data)
            worksheet.write_string (row, col+4,str(swift_code),main_data)
            worksheet.write_number (row, col+5,net_salary ,main_data)
            worksheet.write_number (row, col+6,basic_salary ,main_data)
            worksheet.write_number (row, col+7,housing_allow ,main_data)
            worksheet.write_number (row, col+8,other_allow ,main_data)
            worksheet.write_number (row, col+9,abs(total_deduct),main_data)
            row+=1

        