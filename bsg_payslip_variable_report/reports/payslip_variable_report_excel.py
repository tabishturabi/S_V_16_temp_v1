from odoo import models
from datetime import date, datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import pandas as pd
from num2words import num2words


class PayslipVariableReportExcel(models.AbstractModel):
    _name = 'report.bsg_payslip_variable_report.pv_report_xlsx'
    _inherit ='report.report_xlsx.abstract'




    def get_payslip_from_to(self,wiz_month,wiz_year):
        month_list_with_31 = [1, 3, 5, 7, 8, 10, 12]
        month_list_with_30 = [4, 6, 9, 11]
        month_list_with_29 = [2]
        year = str(wiz_year)
        month = str(wiz_month)
        from_time = '00:00:00'
        to_time = '23:59:59'
        from_day = '1'
        to_day = ''
        if wiz_month in month_list_with_31:
            to_day = '31'
        if wiz_month in month_list_with_30:
            to_day = '30'
        if wiz_month in month_list_with_29:
            if int(wiz_year)%4 == 0:
                to_day = '29'
            else:
                to_day = '28'

        period_from = '/'.join([month, from_day, year])
        period_from += ' ' + from_time
        period_to = '/'.join([month, to_day, year])
        period_to += ' ' + to_time
        period_date_from = datetime.strptime(period_from, '%m/%d/%Y %H:%M:%S')
        period_date_to = datetime.strptime(period_to, '%m/%d/%Y %H:%M:%S')

        return period_date_from.date(),period_date_to.date()



    def generate_xlsx_report(self, workbook,lines,data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
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
        sheet = workbook.add_worksheet('Monthly variables On Payslips  Report')
        sheet.set_column('A:AE', 15)
        domain=[]
        row = 2
        col = 0
        sheet.write(row, col, 'Print Date', main_heading2)
        sheet.write_string(row, col + 1, str(docs.print_date_time.strftime('%Y-%m-%d %H:%M:%S')), main_heading)
        if docs.period_month and docs.period_year:
            payslip_from_to = self.get_payslip_from_to(docs.period_month, docs.period_year.car_year_name)
            domain += [('date_from','>=',payslip_from_to[0]),
                       ('date_to','<=',payslip_from_to[1])]
            # print('............payslip_from.......', payslip_from_to[0])
            # print('............payslip_to.......', payslip_from_to[1])
        if docs.payslip_batch_ids:
            domain += [('payslip_run_id', 'in', docs.payslip_batch_ids.ids)]
            sheet.write(row, col,'Payslip Batches', main_heading2)
            rec_names = docs.payslip_batch_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1,str(names),main_heading)
            row+=1
        if docs.department_ids:
            domain += [('department_id', 'in', docs.department_ids.ids)]
            sheet.write(row, col, 'Departments', main_heading2)
            rec_names = docs.department_ids.mapped('display_name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.job_position_ids:
            domain += [('job_id', 'in', docs.job_position_ids.ids)]
            sheet.write(row, col, 'Job Positions', main_heading2)
            rec_names = docs.job_position_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.employee_ids:
            domain += [('employee_id', 'in', docs.employee_ids.ids)]
            sheet.write(row, col,'Employees', main_heading2)
            rec_names = docs.employee_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1,str(names),main_heading)
            row+=1
        if docs.branch_ids:
            domain += [('branch_id', 'in', docs.branch_ids.ids)]
            sheet.write(row, col, 'Branches', main_heading2)
            rec_names = docs.branch_ids.mapped('branch_ar_name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.country_ids:
            domain += [('employee_id.country_id', 'in', docs.country_ids.ids)]
            sheet.write(row, col, 'Nationality', main_heading2)
            rec_names = docs.country_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.company_ids:
            domain += [('company_id', 'in', docs.company_ids.ids)]
            sheet.write(row, col, 'Company', main_heading2)
            rec_names = docs.company_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.salary_structure_ids:
            domain += [('struct_id', 'in', docs.salary_structure_ids.ids)]
            sheet.write(row, col, 'Sallary Structure', main_heading2)
            rec_names = docs.partner_type_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.rule_category_ids:
            domain += [('line_ids.category_id', 'in', docs.rule_category_ids.ids)]
            sheet.write(row, col, 'Salary Rule Category', main_heading2)
            rec_names = docs.rule_category_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.rule_ids:
            domain += [('line_ids.salary_rule_id', 'in', docs.rule_ids.ids)]
            sheet.write(row, col, 'Salary Rule', main_heading2)
            rec_names = docs.rule_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.salary_payment_method == 'bank':
            domain += [('salary_payment_method', '=', 'bank')]
        if docs.salary_payment_method == 'cash':
            domain += [('salary_payment_method', '=', 'cash')]
        if docs.employee_status == 'on_job':
            domain += [('employee_state', '=', 'on_job')]
        if docs.employee_status == 'on_leave':
            domain += [('employee_state', '=', 'on_leave')]
        if docs.employee_status == 'return_from_holiday':
            domain += [('employee_state', '=', 'return_from_holiday')]
        if docs.employee_status == 'resignation':
            domain += [('employee_state', '=', 'resignation')]
        if docs.employee_status == 'suspended':
            domain += [('employee_state', '=', 'suspended')]
        if docs.employee_status == 'service_expired':
            domain += [('employee_state', '=', 'service_expired')]
        if docs.employee_status == 'contract_terminated':
            domain += [('employee_state', '=', 'contract_terminated')]
        if docs.employee_status == 'ending_contract_during_trial_period':
            domain += [('employee_state', '=', 'ending_contract_during_trial_period')]
        if docs.employee_state_id:
            domain += [('employee_state_id', '=', docs.employee_state_id.id)]
        if docs.start_date_condition == 'all':
            sheet.write(row, col, 'Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('All'), main_heading)
            row += 1
        if docs.start_date_condition == 'is_equal_to':
            sheet.write(row, col, 'Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Equal To'), main_heading)
            row += 1
            domain += [('contract_id.date_start', '=', docs.start_date)]
        if docs.start_date_condition == 'is_not_equal_to':
            sheet.write(row, col, 'Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Not Equal To'), main_heading)
            row += 1
            domain += [('contract_id.date_start', '!=', docs.start_date)]
        if docs.start_date_condition == 'is_after':
            sheet.write(row, col, 'Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Greater Than'), main_heading)
            row += 1
            domain += [('contract_id.date_start', '>', docs.start_date)]
        if docs.start_date_condition == 'is_before':
            sheet.write(row, col, 'Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Less Than'), main_heading)
            row += 1
            domain += [('contract_id.date_start', '<', docs.start_date)]
        if docs.start_date_condition == 'is_after_or_equal_to':
            sheet.write(row, col, 'Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Greater Than Or Equal To'), main_heading)
            row += 1
            domain += [('contract_id.date_start', '>=', docs.start_date)]
        if docs.start_date_condition == 'is_before_or_equal_to':
            sheet.write(row, col, 'Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Less Than Or Equal To'), main_heading)
            row += 1
            domain += [('contract_id.date_start', '<=', docs.start_date)]
        if docs.start_date_condition == 'is_between':
            sheet.write(row, col, 'Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Between'), main_heading)
            row += 1
            domain += [('contract_id.date_start', '>', docs.date_from),
                       ('contract_id.date_start', '<', docs.date_to)]
        if docs.start_date_condition == 'is_set':
            sheet.write(row, col, 'Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Set'), main_heading)
            row += 1
            domain += [('contract_id.date_start', '!=', None)]
        if docs.start_date_condition == 'is_not_set':
            sheet.write(row, col, 'Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Not Set'), main_heading)
            row += 1
            domain += [('contract_id.date_start', '=', None)]
        if docs.slip_start_date_condition == 'all':
            sheet.write(row, col, 'Slip Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('All'), main_heading)
            row += 1
        if docs.slip_start_date_condition == 'is_equal_to':
            sheet.write(row, col, 'Slip Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Equal To'), main_heading)
            row += 1
            domain += [('date_from', '=', docs.slip_start_date)]
        if docs.slip_start_date_condition == 'is_not_equal_to':
            sheet.write(row, col, 'Slip Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Not Equal To'), main_heading)
            row += 1
            domain += [('date_from', '!=', docs.slip_start_date)]
        if docs.slip_start_date_condition == 'is_after':
            sheet.write(row, col, 'Slip Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Greater Than'), main_heading)
            row += 1
            domain += [('date_from', '>', docs.slip_start_date)]
        if docs.slip_start_date_condition == 'is_before':
            sheet.write(row, col, 'Slip Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Less Than'), main_heading)
            row += 1
            domain += [('date_from', '<', docs.slip_start_date)]
        if docs.slip_start_date_condition == 'is_after_or_equal_to':
            sheet.write(row, col, 'Slip Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Greater Than Or Equal To'), main_heading)
            row += 1
            domain += [('date_from', '>=', docs.slip_start_date)]
        if docs.slip_start_date_condition == 'is_before_or_equal_to':
            sheet.write(row, col, 'Slip Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Less Than Or Equal To'), main_heading)
            row += 1
            domain += [('date_from', '<=', docs.slip_start_date)]
        if docs.slip_start_date_condition == 'is_between':
            sheet.write(row, col, 'Slip Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Between'), main_heading)
            row += 1
            domain += [('date_from', '>', docs.slip_date_from),
                       ('date_from', '<', docs.slip_date_to)]
        if docs.slip_start_date_condition == 'is_set':
            sheet.write(row, col, 'Slip Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Set'), main_heading)
            row += 1
            domain += [('date_from', '!=', None)]
        if docs.slip_start_date_condition == 'is_not_set':
            sheet.write(row, col, 'Slip Start Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is Not Set'), main_heading)
            row += 1
            domain += [('date_from', '=', None)]
        payslip_ids = self.env['hr.payslip'].search(domain)
        row+=1
        if docs.grouping_by == 'all':
            self.env.ref('bsg_payslip_variable_report.payslip_variable_report_xlsx_id').report_file = "Monthly variables On Payslips  Report"
            sheet.merge_range('A1:AD1', 'تقرير المتغيرات الشهرية في مسير الرواتب', main_heading3)
            sheet.merge_range('A2:AD2', 'Monthly variables On Payslips  Report', main_heading3)
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'Employee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality (Country)', main_heading2)
            sheet.write(row, col + 5, 'ID NO', main_heading2)
            sheet.write(row, col + 6, 'Work Mobile', main_heading2)
            sheet.write(row, col + 7, 'Start Date', main_heading2)
            sheet.write(row, col + 8, 'Date of Join', main_heading2)
            sheet.write(row, col + 9, 'Date From', main_heading2)
            sheet.write(row, col + 10, 'Date To', main_heading2)
            sheet.write(row, col + 11, 'Payslip Batches', main_heading2)
            sheet.write(row, col + 12, 'Reference', main_heading2)
            sheet.write(row, col + 13, 'Payslip Name', main_heading2)
            sheet.write(row, col + 14, 'Branch', main_heading2)
            sheet.write(row, col + 15, 'Department',main_heading2)
            sheet.write(row, col + 16, 'Job Position', main_heading2)
            sheet.write(row, col + 17, 'Status', main_heading2)
            sheet.write(row, col + 18, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 19, 'Salary Structure', main_heading2)
            sheet.write(row, col + 20, 'Sequence', main_heading2)
            sheet.write(row, col + 21, 'Rule Name', main_heading2)
            sheet.write(row, col + 22, 'Rule Code', main_heading2)
            sheet.write(row, col + 23, 'Rule Category Name', main_heading2)
            sheet.write(row, col + 24, 'Description', main_heading2)
            sheet.write(row, col + 25, 'Quantity', main_heading2)
            sheet.write(row, col + 26, 'Rate (%)', main_heading2)
            sheet.write(row, col + 27, 'Amount', main_heading2)
            sheet.write(row, col + 28, 'Total', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, 'رقم بطاقة الهوية', main_heading2)
            sheet.write(row, col + 6, 'رقم جوال الموظف', main_heading2)
            sheet.write(row, col + 7, 'تاريخ الالتحاق', main_heading2)
            sheet.write(row, col + 8, 'تاريخ الالتحاق ', main_heading2)
            sheet.write(row, col + 9, 'من تاريخ', main_heading2)
            sheet.write(row, col + 10, 'الي تاريخ', main_heading2)
            sheet.write(row, col + 11, 'اسم دفعة مسير الرواتب', main_heading2)
            sheet.write(row, col + 12, 'مرجع مسير الرواتب', main_heading2)
            sheet.write(row, col + 13, 'وصف مسير الرواتب', main_heading2)
            sheet.write(row, col + 14, 'الفرع ', main_heading2)
            sheet.write(row, col + 15, 'الإدارة', main_heading2)
            sheet.write(row, col + 16, 'المنصب الوظيفي', main_heading2)
            sheet.write(row, col + 17, 'حالة المسير', main_heading2)
            sheet.write(row, col + 18, 'طريقة الدفع', main_heading2)
            sheet.write(row, col + 19, 'هيكل الرواتب', main_heading2)
            sheet.write(row, col + 20, 'رقم التسلسل', main_heading2)
            sheet.write(row, col + 21, 'اسم العنصر', main_heading2)
            sheet.write(row, col + 22, 'كود العنصر', main_heading2)
            sheet.write(row, col + 23, 'اسم فئة العنصر', main_heading2)
            sheet.write(row, col + 24, 'الوصف', main_heading2)
            sheet.write(row, col + 25, 'الكمية', main_heading2)
            sheet.write(row, col + 26, 'النسبة', main_heading2)
            sheet.write(row, col + 27, 'القيمة', main_heading2)
            sheet.write(row, col + 28, 'الإجمالي', main_heading2)
            row += 1
            qty = 0
            rate = 0
            amount = 0
            total = 0
            for payslip_id in payslip_ids:
                line_ids = payslip_id.line_ids
                if docs.rule_ids:
                    line_ids = line_ids.filtered(lambda r:r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                if docs.rule_category_ids:
                    line_ids = line_ids.filtered(lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                for line_id in line_ids:
                    if line_id.total != 0:
                        if payslip_id.employee_id.driver_code:
                            sheet.write_string(row, col, str(payslip_id.employee_id.driver_code), main_heading)
                        if payslip_id.employee_id.employee_code:
                            sheet.write_string(row, col + 1,str(payslip_id.employee_id.employee_code), main_heading)
                        if payslip_id.employee_id.name:
                            sheet.write_string(row, col + 2,str(payslip_id.employee_id.name), main_heading)
                        if payslip_id.employee_state:
                            sheet.write_string(row, col + 3,str(payslip_id.employee_state), main_heading)
                        if payslip_id.employee_id.country_id.name:
                            sheet.write_string(row, col + 4, str(payslip_id.employee_id.country_id.name),main_heading)
                        if payslip_id.employee_id.country_id:
                            if payslip_id.employee_id.country_id.code == 'SA':
                                if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col + 5,str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),main_heading)
                            else:
                                if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 5,str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),main_heading)
                        if payslip_id.employee_id.mobile_phone:
                            sheet.write_string(row, col + 6,str(payslip_id.employee_id.mobile_phone), main_heading)
                        if payslip_id.contract_id.date_start:
                            sheet.write_string(row, col + 7,str(payslip_id.contract_id.date_start), main_heading)
                        if payslip_id.employee_id.bsgjoining_date:
                            sheet.write_string(row, col + 8,str(payslip_id.employee_id.bsgjoining_date), main_heading)
                        if payslip_id.date_from:
                            sheet.write_string(row, col + 9,str(payslip_id.date_from), main_heading)
                        if payslip_id.date_to:
                            sheet.write_string(row, col + 10,str(payslip_id.date_to), main_heading)
                        if payslip_id.payslip_run_id.name:
                            sheet.write_string(row, col + 11,str(payslip_id.payslip_run_id.name), main_heading)
                        if payslip_id.number:
                            sheet.write_string(row, col + 12, str(payslip_id.number),main_heading)
                        if payslip_id.name:
                            sheet.write_string(row, col + 13,str(payslip_id.name), main_heading)
                        if payslip_id.branch_id.branch_name:
                            sheet.write_string(row, col + 14,str(payslip_id.branch_id.branch_name), main_heading)
                        if payslip_id.department_id.display_name:
                            sheet.write_string(row, col + 15,str(payslip_id.department_id.display_name), main_heading)
                        if payslip_id.job_id.name:
                            sheet.write_string(row, col+16,str(payslip_id.job_id.name), main_heading)
                        if payslip_id.state:
                            sheet.write_string(row, col + 17,str(payslip_id.state), main_heading)
                        if payslip_id.salary_payment_method:
                            sheet.write_string(row, col + 18,str(payslip_id.salary_payment_method), main_heading)
                        if payslip_id.struct_id.name:
                            sheet.write_string(row, col + 19,str(payslip_id.struct_id.name), main_heading)
                        if line_id.sequence:
                            sheet.write_string(row, col + 20,str(line_id.sequence), main_heading)
                        if line_id.name:
                            sheet.write_string(row, col + 21,str(line_id.name), main_heading)
                        if line_id.code:
                            sheet.write_string(row, col + 22,str(line_id.code), main_heading)
                        if line_id.category_id.name:
                            sheet.write_string(row, col + 23,str(line_id.category_id.name), main_heading)
                        if payslip_id.input_line_ids:
                            input_line_ids = payslip_id.input_line_ids.filtered(lambda r: r.code == line_id.code)
                            if input_line_ids:
                                if input_line_ids.mapped('description')[0]:
                                    sheet.write_string(row, col + 24,str(input_line_ids.mapped('description')[0]), main_heading)
                        if line_id.quantity:
                            sheet.write_number(row, col + 25, line_id.quantity, main_heading)
                            qty += line_id.quantity
                        if line_id.rate:
                            sheet.write_number(row, col + 26, line_id.rate, main_heading)
                            rate = line_id.rate
                        if line_id.amount:
                            sheet.write_number(row, col + 27, line_id.amount, main_heading)
                            amount += line_id.amount
                        if line_id.total:
                            sheet.write_number(row, col + 28, line_id.total, main_heading)
                            total += line_id.total
                        row += 1
            sheet.write(row, col, 'Total', main_heading2)
            sheet.write_number(row, col + 25, qty, main_heading)
            sheet.write_number(row, col + 28, total, main_heading)
            row += 1
        if docs.grouping_by == 'by_department':
            self.env.ref('bsg_payslip_variable_report.payslip_variable_report_xlsx_id').report_file = "Monthly variables On Payslips Grouping by Departments Report"
            sheet.merge_range('A1:AE1', 'تقرير المتغيرات الشهرية في مسير الرواتب بحسب الإدارات', main_heading3)
            sheet.merge_range('A2:AE2', 'Monthly variables On Payslips Grouping by Departments Report', main_heading3)
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'Employee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality (Country)', main_heading2)
            sheet.write(row, col + 5, 'ID NO', main_heading2)
            sheet.write(row, col + 6, 'Work Mobile', main_heading2)
            sheet.write(row, col + 7, 'Start Date', main_heading2)
            sheet.write(row, col + 8, 'Date of Join', main_heading2)
            sheet.write(row, col + 9, 'Date From', main_heading2)
            sheet.write(row, col + 10, 'Date To', main_heading2)
            sheet.write(row, col + 11, 'Payslip Batches', main_heading2)
            sheet.write(row, col + 12, 'Reference', main_heading2)
            sheet.write(row, col + 13, 'Payslip Name', main_heading2)
            sheet.write(row, col + 14, 'Branch', main_heading2)
            sheet.write(row, col + 15, 'Job Position', main_heading2)
            sheet.write(row, col + 16, 'Status', main_heading2)
            sheet.write(row, col + 17, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 18, 'Salary Structure', main_heading2)
            sheet.write(row, col + 19, 'Sequence', main_heading2)
            sheet.write(row, col + 20, 'Rule Name', main_heading2)
            sheet.write(row, col + 21, 'Rule Code', main_heading2)
            sheet.write(row, col + 22, 'Rule Category Name', main_heading2)
            sheet.write(row, col + 23, 'Description', main_heading2)
            sheet.write(row, col + 24, 'Quantity', main_heading2)
            sheet.write(row, col + 25, 'Rate (%)', main_heading2)
            sheet.write(row, col + 26, 'Amount', main_heading2)
            sheet.write(row, col + 27, 'Total', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, 'رقم بطاقة الهوية', main_heading2)
            sheet.write(row, col + 6, 'رقم جوال الموظف', main_heading2)
            sheet.write(row, col + 7, 'تاريخ الالتحاق', main_heading2)
            sheet.write(row, col + 8, 'تاريخ الالتحاق ', main_heading2)
            sheet.write(row, col + 9, 'من تاريخ', main_heading2)
            sheet.write(row, col + 10, 'الي تاريخ', main_heading2)
            sheet.write(row, col + 11, 'اسم دفعة مسير الرواتب', main_heading2)
            sheet.write(row, col + 12, 'مرجع مسير الرواتب', main_heading2)
            sheet.write(row, col + 13, 'وصف مسير الرواتب', main_heading2)
            sheet.write(row, col + 14, 'الفرع ', main_heading2)
            sheet.write(row, col + 15, 'المنصب الوظيفي', main_heading2)
            sheet.write(row, col + 16, 'حالة المسير', main_heading2)
            sheet.write(row, col + 17, 'طريقة الدفع', main_heading2)
            sheet.write(row, col + 18, 'هيكل الرواتب', main_heading2)
            sheet.write(row, col + 19, 'رقم التسلسل', main_heading2)
            sheet.write(row, col + 20, 'اسم العنصر', main_heading2)
            sheet.write(row, col + 21, 'كود العنصر', main_heading2)
            sheet.write(row, col + 22, 'اسم فئة العنصر', main_heading2)
            sheet.write(row, col + 23, 'الوصف', main_heading2)
            sheet.write(row, col + 24, 'الكمية', main_heading2)
            sheet.write(row, col + 25, 'النسبة', main_heading2)
            sheet.write(row, col + 26, 'القيمة', main_heading2)
            sheet.write(row, col + 27, 'الإجمالي', main_heading2)
            row += 1
            payslip_ids_group_by_dept = payslip_ids.read_group([],fields=['department_id'],groupby=['department_id'], lazy=False)
            if payslip_ids_group_by_dept:
                grand_qty=0
                grand_rate=0
                grand_amount=0
                grand_total=0
                for payslip_id_group_by_dept in payslip_ids_group_by_dept:
                    payslip_ids_filtered_by_dept = payslip_ids.filtered(lambda r:r.department_id.id == payslip_id_group_by_dept.get('department_id')[0] if payslip_id_group_by_dept.get('department_id') else r.department_id.id == payslip_id_group_by_dept.get('department_id'))
                    if payslip_ids_filtered_by_dept:
                        sheet.write(row, col, 'Department', main_heading2)
                        if payslip_id_group_by_dept.get('department_id'):
                            sheet.write_string(row, col + 1, str(payslip_id_group_by_dept.get('department_id')[1]), main_heading)
                        else:
                            sheet.write_string(row, col + 1, str('Undefined'),main_heading)
                        sheet.write(row, col + 2, 'الإدارة', main_heading2)
                        row += 1
                        qty=0
                        rate=0
                        amount=0
                        total=0
                        for payslip_id in payslip_ids_filtered_by_dept:
                            line_ids = payslip_id.line_ids
                            if docs.rule_ids:
                                line_ids = line_ids.filtered(
                                    lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                            if docs.rule_category_ids:
                                line_ids = line_ids.filtered(
                                    lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                            for line_id in line_ids:
                                if line_id.total != 0:
                                    if payslip_id.employee_id.driver_code:
                                        sheet.write_string(row, col, str(payslip_id.employee_id.driver_code),
                                                           main_heading)
                                    if payslip_id.employee_id.employee_code:
                                        sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                           main_heading)
                                    if payslip_id.employee_id.name:
                                        sheet.write_string(row, col + 2, str(payslip_id.employee_id.name), main_heading)
                                    if payslip_id.employee_state:
                                        sheet.write_string(row, col + 3, str(payslip_id.employee_state), main_heading)
                                    if payslip_id.employee_id.country_id.name:
                                        sheet.write_string(row, col + 4, str(payslip_id.employee_id.country_id.name),
                                                           main_heading)
                                    if payslip_id.employee_id.country_id:
                                        if payslip_id.employee_id.country_id.code == 'SA':
                                            if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                                sheet.write_string(row, col + 5,
                                                                   str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                                   main_heading)
                                        else:
                                            if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                                sheet.write_string(row, col + 5,
                                                                   str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                                   main_heading)
                                    if payslip_id.employee_id.mobile_phone:
                                        sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                           main_heading)
                                    if payslip_id.contract_id.date_start:
                                        sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                           main_heading)
                                    if payslip_id.employee_id.bsgjoining_date:
                                        sheet.write_string(row, col + 8, str(payslip_id.employee_id.bsgjoining_date),
                                                           main_heading)
                                    if payslip_id.date_from:
                                        sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                    if payslip_id.date_to:
                                        sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                    if payslip_id.payslip_run_id.name:
                                        sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name),
                                                           main_heading)
                                    if payslip_id.number:
                                        sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                    if payslip_id.name:
                                        sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                    if payslip_id.branch_id.branch_name:
                                        sheet.write_string(row, col + 14, str(payslip_id.branch_id.branch_name),
                                                           main_heading)
                                    if payslip_id.job_id.name:
                                        sheet.write_string(row, col + 15, str(payslip_id.job_id.name), main_heading)
                                    if payslip_id.state:
                                        sheet.write_string(row, col + 16, str(payslip_id.state), main_heading)
                                    if payslip_id.salary_payment_method:
                                        sheet.write_string(row, col + 17, str(payslip_id.salary_payment_method),
                                                           main_heading)
                                    if payslip_id.struct_id.name:
                                        sheet.write_string(row, col + 18, str(payslip_id.struct_id.name), main_heading)
                                    if line_id.sequence:
                                        sheet.write_string(row, col + 19, str(line_id.sequence), main_heading)
                                    if line_id.name:
                                        sheet.write_string(row, col + 20, str(line_id.name), main_heading)
                                    if line_id.code:
                                        sheet.write_string(row, col + 21, str(line_id.code), main_heading)
                                    if line_id.category_id.name:
                                        sheet.write_string(row, col + 22, str(line_id.category_id.name), main_heading)
                                    if payslip_id.input_line_ids:
                                        input_line_ids = payslip_id.input_line_ids.filtered(
                                            lambda r: r.code == line_id.code)
                                        if input_line_ids:
                                            if input_line_ids.mapped('description')[0]:
                                                sheet.write_string(row, col + 23,
                                                                   str(input_line_ids.mapped('description')[0]),
                                                                   main_heading)
                                    if line_id.quantity:
                                        sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                        qty += line_id.quantity
                                    if line_id.rate:
                                        sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                        rate = line_id.rate
                                    if line_id.amount:
                                        sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                        amount += line_id.amount
                                    if line_id.total:
                                        sheet.write_number(row, col + 27, line_id.total, main_heading)
                                        total += line_id.total
                                    row += 1
                        sheet.write(row,col, 'Total', main_heading2)
                        sheet.write_number(row, col + 24,qty , main_heading)
                        grand_qty += qty
                        sheet.write_number(row, col + 27,total , main_heading)
                        grand_total += total
                        row+=1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 24, grand_qty, main_heading)
                sheet.write_number(row, col + 27, grand_total, main_heading)
                row += 1
        if docs.grouping_by == 'by_branch':
            self.env.ref(
                'bsg_payslip_variable_report.payslip_variable_report_xlsx_id').report_file = "Monthly variables On Payslips Grouping by Branches Report"
            sheet.merge_range('A1:AE1', 'تقرير المتغيرات الشهرية في مسير الرواتب بحسب الفروع', main_heading3)
            sheet.merge_range('A2:AE2', 'Monthly variables On Payslips Grouping by Branches Report', main_heading3)
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'Employee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality (Country)', main_heading2)
            sheet.write(row, col + 5, 'ID NO', main_heading2)
            sheet.write(row, col + 6, 'Work Mobile', main_heading2)
            sheet.write(row, col + 7, 'Start Date', main_heading2)
            sheet.write(row, col + 8, 'Date of Join', main_heading2)
            sheet.write(row, col + 9, 'Date From', main_heading2)
            sheet.write(row, col + 10, 'Date To', main_heading2)
            sheet.write(row, col + 11, 'Payslip Batches', main_heading2)
            sheet.write(row, col + 12, 'Reference', main_heading2)
            sheet.write(row, col + 13, 'Payslip Name', main_heading2)
            sheet.write(row, col + 14, 'Department', main_heading2)
            sheet.write(row, col + 15, 'Job Position', main_heading2)
            sheet.write(row, col + 16, 'Status', main_heading2)
            sheet.write(row, col + 17, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 18, 'Salary Structure', main_heading2)
            sheet.write(row, col + 19, 'Sequence', main_heading2)
            sheet.write(row, col + 20, 'Rule Name', main_heading2)
            sheet.write(row, col + 21, 'Rule Code', main_heading2)
            sheet.write(row, col + 22, 'Rule Category Name', main_heading2)
            sheet.write(row, col + 23, 'Description', main_heading2)
            sheet.write(row, col + 24, 'Quantity', main_heading2)
            sheet.write(row, col + 25, 'Rate (%)', main_heading2)
            sheet.write(row, col + 26, 'Amount', main_heading2)
            sheet.write(row, col + 27, 'Total', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, 'رقم بطاقة الهوية', main_heading2)
            sheet.write(row, col + 6, 'رقم جوال الموظف', main_heading2)
            sheet.write(row, col + 7, 'تاريخ الالتحاق', main_heading2)
            sheet.write(row, col + 8, 'تاريخ الالتحاق ', main_heading2)
            sheet.write(row, col + 9, 'من تاريخ', main_heading2)
            sheet.write(row, col + 10, 'الي تاريخ', main_heading2)
            sheet.write(row, col + 11, 'اسم دفعة مسير الرواتب', main_heading2)
            sheet.write(row, col + 12, 'مرجع مسير الرواتب', main_heading2)
            sheet.write(row, col + 13, 'وصف مسير الرواتب', main_heading2)
            sheet.write(row, col + 14, 'الإدارة', main_heading2)
            sheet.write(row, col + 15, 'المنصب الوظيفي', main_heading2)
            sheet.write(row, col + 16, 'حالة المسير', main_heading2)
            sheet.write(row, col + 17, 'طريقة الدفع', main_heading2)
            sheet.write(row, col + 18, 'هيكل الرواتب', main_heading2)
            sheet.write(row, col + 19, 'رقم التسلسل', main_heading2)
            sheet.write(row, col + 20, 'اسم العنصر', main_heading2)
            sheet.write(row, col + 21, 'كود العنصر', main_heading2)
            sheet.write(row, col + 22, 'اسم فئة العنصر', main_heading2)
            sheet.write(row, col + 23, 'الوصف', main_heading2)
            sheet.write(row, col + 24, 'الكمية', main_heading2)
            sheet.write(row, col + 25, 'النسبة', main_heading2)
            sheet.write(row, col + 26, 'القيمة', main_heading2)
            sheet.write(row, col + 27, 'الإجمالي', main_heading2)
            row += 1
            payslip_ids_group_by_branch = payslip_ids.read_group([], fields=['branch_id'], groupby=['branch_id'],lazy=False)
            if payslip_ids_group_by_branch:
                grand_qty = 0
                grand_rate = 0
                grand_amount = 0
                grand_total = 0
                for payslip_id_group_by_branch in payslip_ids_group_by_branch:
                    if payslip_id_group_by_branch:
                        # print('..............payslip_id_group_by_branch.......',
                        #       payslip_id_group_by_branch.get('branch_id')[1])
                        payslip_ids_filtered_by_branch = payslip_ids.filtered(lambda r: r.branch_id and r.branch_id.id == payslip_id_group_by_branch.get('branch_id')[0] if payslip_id_group_by_branch.get('branch_id') else r.branch_id.id == payslip_id_group_by_branch.get('branch_id'))
                        if payslip_ids_filtered_by_branch:
                            sheet.write(row, col, 'Branch', main_heading2)
                            if payslip_id_group_by_branch.get('branch_id'):
                                sheet.write_string(row, col + 1, str(payslip_id_group_by_branch.get('branch_id')[1]),
                                                   main_heading)
                            else:
                                sheet.write_string(row, col + 1, str('Undefined'),main_heading)

                            sheet.write(row, col + 2, 'الفرع', main_heading2)
                            row += 1
                            qty = 0
                            rate = 0
                            amount = 0
                            total = 0
                            for payslip_id in payslip_ids_filtered_by_branch:
                                line_ids = payslip_id.line_ids
                                if docs.rule_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                                if docs.rule_category_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                                for line_id in line_ids:
                                    if line_id.total != 0:
                                        print('............payslip_id...............', payslip_id.date_from)
                                        if payslip_id.employee_id.driver_code:
                                            sheet.write_string(row, col, str(payslip_id.employee_id.driver_code),
                                                               main_heading)
                                        if payslip_id.employee_id.employee_code:
                                            sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                               main_heading)
                                        if payslip_id.employee_id.name:
                                            sheet.write_string(row, col + 2, str(payslip_id.employee_id.name),
                                                               main_heading)
                                        if payslip_id.employee_state:
                                            sheet.write_string(row, col + 3, str(payslip_id.employee_state),
                                                               main_heading)
                                        if payslip_id.employee_id.country_id.name:
                                            sheet.write_string(row, col + 4,
                                                               str(payslip_id.employee_id.country_id.name),
                                                               main_heading)
                                        if payslip_id.employee_id.country_id:
                                            if payslip_id.employee_id.country_id.code == 'SA':
                                                if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                                    sheet.write_string(row, col + 5,
                                                                       str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                                       main_heading)
                                            else:
                                                if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                                    sheet.write_string(row, col + 5,
                                                                       str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                                       main_heading)
                                        if payslip_id.employee_id.mobile_phone:
                                            sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                               main_heading)
                                        if payslip_id.contract_id.date_start:
                                            sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                               main_heading)
                                        if payslip_id.employee_id.bsgjoining_date:
                                            sheet.write_string(row, col + 8,
                                                               str(payslip_id.employee_id.bsgjoining_date),
                                                               main_heading)
                                        if payslip_id.date_from:
                                            sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                        if payslip_id.date_to:
                                            sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                        if payslip_id.payslip_run_id.name:
                                            sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name),
                                                               main_heading)
                                        if payslip_id.number:
                                            sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                        if payslip_id.name:
                                            sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                        if payslip_id.department_id.display_name:
                                            sheet.write_string(row, col + 14,
                                                               str(payslip_id.department_id.display_name), main_heading)
                                        if payslip_id.job_id.name:
                                            sheet.write_string(row, col + 15, str(payslip_id.job_id.name), main_heading)
                                        if payslip_id.state:
                                            sheet.write_string(row, col + 16, str(payslip_id.state), main_heading)
                                        if payslip_id.salary_payment_method:
                                            sheet.write_string(row, col + 17, str(payslip_id.salary_payment_method),
                                                               main_heading)
                                        if payslip_id.struct_id.name:
                                            sheet.write_string(row, col + 18, str(payslip_id.struct_id.name),
                                                               main_heading)
                                        if line_id.sequence:
                                            sheet.write_string(row, col + 19, str(line_id.sequence), main_heading)
                                        if line_id.name:
                                            sheet.write_string(row, col + 20, str(line_id.name), main_heading)
                                        if line_id.code:
                                            sheet.write_string(row, col + 21, str(line_id.code), main_heading)
                                        if line_id.category_id.name:
                                            sheet.write_string(row, col + 22, str(line_id.category_id.name),
                                                               main_heading)
                                        if payslip_id.input_line_ids:
                                            input_line_ids = payslip_id.input_line_ids.filtered(
                                                lambda r: r.code == line_id.code)
                                            if input_line_ids:
                                                if input_line_ids.mapped('description')[0]:
                                                    sheet.write_string(row, col + 23,
                                                                       str(input_line_ids.mapped('description')[0]),
                                                                       main_heading)
                                        if line_id.quantity:
                                            sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                            qty += line_id.quantity
                                        if line_id.rate:
                                            sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                            rate = line_id.rate
                                        if line_id.amount:
                                            sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                            amount += line_id.amount
                                        if line_id.total:
                                            sheet.write_number(row, col + 27, line_id.total, main_heading)
                                            total += line_id.total
                                        row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_number(row, col + 24, qty, main_heading)
                            grand_qty += qty
                            sheet.write_number(row, col + 27, total, main_heading)
                            grand_total += total
                            row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 24, grand_qty, main_heading)
                sheet.write_number(row, col + 27, grand_total, main_heading)
                row += 1
        if docs.grouping_by == 'by_job_position':
            self.env.ref(
                'bsg_payslip_variable_report.payslip_variable_report_xlsx_id').report_file = "Monthly variables On Payslips Grouping by Job Positions Report "
            sheet.merge_range('A1:AE1', 'تقرير المتغيرات الشهرية في مسير الرواتب بحسب المناصب الوظيفية', main_heading3)
            sheet.merge_range('A2:AE2', 'Monthly variables On Payslips Grouping by Job Positions Report ', main_heading3)
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'Employee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality (Country)', main_heading2)
            sheet.write(row, col + 5, 'ID NO', main_heading2)
            sheet.write(row, col + 6, 'Work Mobile', main_heading2)
            sheet.write(row, col + 7, 'Start Date', main_heading2)
            sheet.write(row, col + 8, 'Date of Join', main_heading2)
            sheet.write(row, col + 9, 'Date From', main_heading2)
            sheet.write(row, col + 10, 'Date To', main_heading2)
            sheet.write(row, col + 11, 'Payslip Batches', main_heading2)
            sheet.write(row, col + 12, 'Reference', main_heading2)
            sheet.write(row, col + 13, 'Payslip Name', main_heading2)
            sheet.write(row, col + 14, 'Branch', main_heading2)
            sheet.write(row, col + 15, 'Department', main_heading2)
            sheet.write(row, col + 16, 'Status', main_heading2)
            sheet.write(row, col + 17, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 18, 'Salary Structure', main_heading2)
            sheet.write(row, col + 19, 'Sequence', main_heading2)
            sheet.write(row, col + 20, 'Rule Name', main_heading2)
            sheet.write(row, col + 21, 'Rule Code', main_heading2)
            sheet.write(row, col + 22, 'Rule Category Name', main_heading2)
            sheet.write(row, col + 23, 'Description', main_heading2)
            sheet.write(row, col + 24, 'Quantity', main_heading2)
            sheet.write(row, col + 25, 'Rate (%)', main_heading2)
            sheet.write(row, col + 26, 'Amount', main_heading2)
            sheet.write(row, col + 27, 'Total', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, 'رقم بطاقة الهوية', main_heading2)
            sheet.write(row, col + 6, 'رقم جوال الموظف', main_heading2)
            sheet.write(row, col + 7, 'تاريخ الالتحاق', main_heading2)
            sheet.write(row, col + 8, 'تاريخ الالتحاق ', main_heading2)
            sheet.write(row, col + 9, 'من تاريخ', main_heading2)
            sheet.write(row, col + 10, 'الي تاريخ', main_heading2)
            sheet.write(row, col + 11, 'اسم دفعة مسير الرواتب', main_heading2)
            sheet.write(row, col + 12, 'مرجع مسير الرواتب', main_heading2)
            sheet.write(row, col + 13, 'وصف مسير الرواتب', main_heading2)
            sheet.write(row, col + 14, 'الفرع ', main_heading2)
            sheet.write(row, col + 15, 'الإدارة', main_heading2)
            sheet.write(row, col + 16, 'حالة المسير', main_heading2)
            sheet.write(row, col + 17, 'طريقة الدفع', main_heading2)
            sheet.write(row, col + 18, 'هيكل الرواتب', main_heading2)
            sheet.write(row, col + 19, 'رقم التسلسل', main_heading2)
            sheet.write(row, col + 20, 'اسم العنصر', main_heading2)
            sheet.write(row, col + 21, 'كود العنصر', main_heading2)
            sheet.write(row, col + 22, 'اسم فئة العنصر', main_heading2)
            sheet.write(row, col + 23, 'الوصف', main_heading2)
            sheet.write(row, col + 24, 'الكمية', main_heading2)
            sheet.write(row, col + 25, 'النسبة', main_heading2)
            sheet.write(row, col + 26, 'القيمة', main_heading2)
            sheet.write(row, col + 27, 'الإجمالي', main_heading2)
            row += 1
            payslip_ids_group_by_job_pos = payslip_ids.read_group([], fields=['job_id'], groupby=['job_id'],
                                                                 lazy=False)
            if payslip_ids_group_by_job_pos:
                grand_qty = 0
                grand_rate = 0
                grand_amount = 0
                grand_total = 0
                for payslip_id_group_by_job_pos in payslip_ids_group_by_job_pos:
                    if payslip_id_group_by_job_pos:
                        payslip_ids_filtered_by_job_pos = payslip_ids.filtered(lambda r: r.job_id and r.job_id.id == payslip_id_group_by_job_pos.get('job_id')[0] if payslip_id_group_by_job_pos.get('job_id') else r.job_id.id == payslip_id_group_by_job_pos.get('job_id'))
                        if payslip_ids_filtered_by_job_pos:
                            sheet.write(row, col, 'Job Position', main_heading2)
                            if payslip_id_group_by_job_pos.get('job_id'):
                                sheet.write_string(row, col + 1, str(payslip_id_group_by_job_pos.get('job_id')[1]),main_heading)
                            else:
                                sheet.write_string(row, col + 1, str('Undefined'), main_heading)

                            sheet.write(row, col + 2, 'المنصب الوظيفي', main_heading2)
                            row += 1
                            qty = 0
                            rate = 0
                            amount = 0
                            total = 0
                            for payslip_id in payslip_ids_filtered_by_job_pos:
                                line_ids = payslip_id.line_ids
                                if docs.rule_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                                if docs.rule_category_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                                for line_id in line_ids:
                                    if line_id.total != 0:
                                        if payslip_id.employee_id.driver_code:
                                            sheet.write_string(row, col, str(payslip_id.employee_id.driver_code),
                                                               main_heading)
                                        if payslip_id.employee_id.employee_code:
                                            sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                               main_heading)
                                        if payslip_id.employee_id.name:
                                            sheet.write_string(row, col + 2, str(payslip_id.employee_id.name),
                                                               main_heading)
                                        if payslip_id.employee_state:
                                            sheet.write_string(row, col + 3, str(payslip_id.employee_state),
                                                               main_heading)
                                        if payslip_id.employee_id.country_id.name:
                                            sheet.write_string(row, col + 4,
                                                               str(payslip_id.employee_id.country_id.name),
                                                               main_heading)
                                        if payslip_id.employee_id.country_id:
                                            if payslip_id.employee_id.country_id.code == 'SA':
                                                if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                                    sheet.write_string(row, col + 5,
                                                                       str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                                       main_heading)
                                            else:
                                                if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                                    sheet.write_string(row, col + 5,
                                                                       str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                                       main_heading)
                                        if payslip_id.employee_id.mobile_phone:
                                            sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                               main_heading)
                                        if payslip_id.contract_id.date_start:
                                            sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                               main_heading)
                                        if payslip_id.employee_id.bsgjoining_date:
                                            sheet.write_string(row, col + 8,
                                                               str(payslip_id.employee_id.bsgjoining_date),
                                                               main_heading)
                                        if payslip_id.date_from:
                                            sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                        if payslip_id.date_to:
                                            sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                        if payslip_id.payslip_run_id.name:
                                            sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name),
                                                               main_heading)
                                        if payslip_id.number:
                                            sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                        if payslip_id.name:
                                            sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                        if payslip_id.branch_id.branch_name:
                                            sheet.write_string(row, col + 14, str(payslip_id.branch_id.branch_name),
                                                               main_heading)
                                        if payslip_id.department_id.display_name:
                                            sheet.write_string(row, col + 15,
                                                               str(payslip_id.department_id.display_name), main_heading)
                                        if payslip_id.state:
                                            sheet.write_string(row, col + 16, str(payslip_id.state), main_heading)
                                        if payslip_id.salary_payment_method:
                                            sheet.write_string(row, col + 17, str(payslip_id.salary_payment_method),
                                                               main_heading)
                                        if payslip_id.struct_id.name:
                                            sheet.write_string(row, col + 18, str(payslip_id.struct_id.name),
                                                               main_heading)
                                        if line_id.sequence:
                                            sheet.write_string(row, col + 19, str(line_id.sequence), main_heading)
                                        if line_id.name:
                                            sheet.write_string(row, col + 20, str(line_id.name), main_heading)
                                        if line_id.code:
                                            sheet.write_string(row, col + 21, str(line_id.code), main_heading)
                                        if line_id.category_id.name:
                                            sheet.write_string(row, col + 22, str(line_id.category_id.name),
                                                               main_heading)
                                        if payslip_id.input_line_ids:
                                            input_line_ids = payslip_id.input_line_ids.filtered(
                                                lambda r: r.code == line_id.code)
                                            if input_line_ids:
                                                if input_line_ids.mapped('description')[0]:
                                                    sheet.write_string(row, col + 23,
                                                                       str(input_line_ids.mapped('description')[0]),
                                                                       main_heading)
                                        if line_id.quantity:
                                            sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                            qty += line_id.quantity
                                        if line_id.rate:
                                            sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                            rate = line_id.rate
                                        if line_id.amount:
                                            sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                            amount += line_id.amount
                                        if line_id.total:
                                            sheet.write_number(row, col + 27, line_id.total, main_heading)
                                            total += line_id.total
                                        row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_number(row, col + 24, qty, main_heading)
                            grand_qty += qty
                            sheet.write_number(row, col + 27, total, main_heading)
                            grand_total += total
                            row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 24, grand_qty, main_heading)
                sheet.write_number(row, col + 27, grand_total, main_heading)
                row += 1
        if docs.grouping_by == 'by_payslip_batch':
            self.env.ref(
                'bsg_payslip_variable_report.payslip_variable_report_xlsx_id').report_file = "Monthly variables On Payslips Grouping by Payslip Batches Report "
            sheet.merge_range('A1:AE1', 'تقرير المتغيرات الشهرية في مسير الرواتب بحسب دفعة مسيرات الرواتب', main_heading3)
            sheet.merge_range('A2:AE2', 'Monthly variables On Payslips Grouping by Payslip Batches Report ', main_heading3)
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'Employee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality (Country)', main_heading2)
            sheet.write(row, col + 5, 'ID NO', main_heading2)
            sheet.write(row, col + 6, 'Work Mobile', main_heading2)
            sheet.write(row, col + 7, 'Start Date', main_heading2)
            sheet.write(row, col + 8, 'Date of Join', main_heading2)
            sheet.write(row, col + 9, 'Date From', main_heading2)
            sheet.write(row, col + 10, 'Date To', main_heading2)
            sheet.write(row, col + 11, 'Reference', main_heading2)
            sheet.write(row, col + 12, 'Payslip Name', main_heading2)
            sheet.write(row, col + 13, 'Branch', main_heading2)
            sheet.write(row, col + 14, 'Department', main_heading2)
            sheet.write(row, col + 15, 'Job Position', main_heading2)
            sheet.write(row, col + 16, 'Status', main_heading2)
            sheet.write(row, col + 17, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 18, 'Salary Structure', main_heading2)
            sheet.write(row, col + 19, 'Sequence', main_heading2)
            sheet.write(row, col + 20, 'Rule Name', main_heading2)
            sheet.write(row, col + 21, 'Rule Code', main_heading2)
            sheet.write(row, col + 22, 'Rule Category Name', main_heading2)
            sheet.write(row, col + 23, 'Description', main_heading2)
            sheet.write(row, col + 24, 'Quantity', main_heading2)
            sheet.write(row, col + 25, 'Rate (%)', main_heading2)
            sheet.write(row, col + 26, 'Amount', main_heading2)
            sheet.write(row, col + 27, 'Total', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, 'رقم بطاقة الهوية', main_heading2)
            sheet.write(row, col + 6, 'رقم جوال الموظف', main_heading2)
            sheet.write(row, col + 7, 'تاريخ الالتحاق', main_heading2)
            sheet.write(row, col + 8, 'تاريخ الالتحاق ', main_heading2)
            sheet.write(row, col + 9, 'من تاريخ', main_heading2)
            sheet.write(row, col + 10, 'الي تاريخ', main_heading2)
            sheet.write(row, col + 11, 'مرجع مسير الرواتب', main_heading2)
            sheet.write(row, col + 12, 'وصف مسير الرواتب', main_heading2)
            sheet.write(row, col + 13, 'الفرع ', main_heading2)
            sheet.write(row, col + 14, 'الإدارة', main_heading2)
            sheet.write(row, col + 15, 'المنصب الوظيفي', main_heading2)
            sheet.write(row, col + 16, 'حالة المسير', main_heading2)
            sheet.write(row, col + 17, 'طريقة الدفع', main_heading2)
            sheet.write(row, col + 18, 'هيكل الرواتب', main_heading2)
            sheet.write(row, col + 19, 'رقم التسلسل', main_heading2)
            sheet.write(row, col + 20, 'اسم العنصر', main_heading2)
            sheet.write(row, col + 21, 'كود العنصر', main_heading2)
            sheet.write(row, col + 22, 'اسم فئة العنصر', main_heading2)
            sheet.write(row, col + 23, 'الوصف', main_heading2)
            sheet.write(row, col + 24, 'الكمية', main_heading2)
            sheet.write(row, col + 25, 'النسبة', main_heading2)
            sheet.write(row, col + 26, 'القيمة', main_heading2)
            sheet.write(row, col + 27, 'الإجمالي', main_heading2)
            row += 1
            payslip_ids_group_by_batch = payslip_ids.read_group([], fields=['payslip_run_id'], groupby=['payslip_run_id'], lazy=False)
            if payslip_ids_group_by_batch:
                grand_qty = 0
                grand_rate = 0
                grand_amount = 0
                grand_total = 0
                for payslip_id_group_by_batch in payslip_ids_group_by_batch:
                    if payslip_id_group_by_batch:
                        payslip_ids_filtered_by_batch = payslip_ids.filtered(lambda r: r.payslip_run_id and r.payslip_run_id.id == payslip_id_group_by_batch.get('payslip_run_id')[0] if payslip_id_group_by_batch.get('payslip_run_id') else r.payslip_run_id.id == payslip_id_group_by_batch.get('payslip_run_id'))
                        if payslip_ids_filtered_by_batch:
                            sheet.write(row, col, 'Payslip Batches', main_heading2)
                            if payslip_id_group_by_batch.get('payslip_run_id'):
                                sheet.write_string(row, col + 1, str(payslip_id_group_by_batch.get('payslip_run_id')[1]),main_heading)
                            else:
                                sheet.write_string(row, col + 1, str('Undefined'), main_heading)

                            sheet.write(row, col + 2, 'اسم دفعة مسير الرواتب', main_heading2)
                            row += 1
                            qty = 0
                            rate = 0
                            amount = 0
                            total = 0
                            for payslip_id in payslip_ids_filtered_by_batch:
                                line_ids = payslip_id.line_ids
                                if docs.rule_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                                if docs.rule_category_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                                for line_id in line_ids:
                                    if line_id.total != 0:
                                        if payslip_id.employee_id.driver_code:
                                            sheet.write_string(row, col, str(payslip_id.employee_id.driver_code),
                                                               main_heading)
                                        if payslip_id.employee_id.employee_code:
                                            sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                               main_heading)
                                        if payslip_id.employee_id.name:
                                            sheet.write_string(row, col + 2, str(payslip_id.employee_id.name),
                                                               main_heading)
                                        if payslip_id.employee_state:
                                            sheet.write_string(row, col + 3, str(payslip_id.employee_state),
                                                               main_heading)
                                        if payslip_id.employee_id.country_id.name:
                                            sheet.write_string(row, col + 4,
                                                               str(payslip_id.employee_id.country_id.name),
                                                               main_heading)
                                        if payslip_id.employee_id.country_id:
                                            if payslip_id.employee_id.country_id.code == 'SA':
                                                if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                                    sheet.write_string(row, col + 5,
                                                                       str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                                       main_heading)
                                            else:
                                                if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                                    sheet.write_string(row, col + 5,
                                                                       str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                                       main_heading)
                                        if payslip_id.employee_id.mobile_phone:
                                            sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                               main_heading)
                                        if payslip_id.contract_id.date_start:
                                            sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                               main_heading)
                                        if payslip_id.employee_id.bsgjoining_date:
                                            sheet.write_string(row, col + 8,
                                                               str(payslip_id.employee_id.bsgjoining_date),
                                                               main_heading)
                                        if payslip_id.date_from:
                                            sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                        if payslip_id.date_to:
                                            sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                        if payslip_id.number:
                                            sheet.write_string(row, col + 11, str(payslip_id.number), main_heading)
                                        if payslip_id.name:
                                            sheet.write_string(row, col + 12, str(payslip_id.name), main_heading)
                                        if payslip_id.branch_id.branch_name:
                                            sheet.write_string(row, col + 13, str(payslip_id.branch_id.branch_name),
                                                               main_heading)
                                        if payslip_id.department_id.display_name:
                                            sheet.write_string(row, col + 14,
                                                               str(payslip_id.department_id.display_name), main_heading)
                                        if payslip_id.job_id.name:
                                            sheet.write_string(row, col + 15, str(payslip_id.job_id.name), main_heading)
                                        if payslip_id.state:
                                            sheet.write_string(row, col + 16, str(payslip_id.state), main_heading)
                                        if payslip_id.salary_payment_method:
                                            sheet.write_string(row, col + 17, str(payslip_id.salary_payment_method),
                                                               main_heading)
                                        if payslip_id.struct_id.name:
                                            sheet.write_string(row, col + 18, str(payslip_id.struct_id.name),
                                                               main_heading)
                                        if line_id.sequence:
                                            sheet.write_string(row, col + 19, str(line_id.sequence), main_heading)
                                        if line_id.name:
                                            sheet.write_string(row, col + 20, str(line_id.name), main_heading)
                                        if line_id.code:
                                            sheet.write_string(row, col + 21, str(line_id.code), main_heading)
                                        if line_id.category_id.name:
                                            sheet.write_string(row, col + 22, str(line_id.category_id.name),
                                                               main_heading)
                                        if payslip_id.input_line_ids:
                                            input_line_ids = payslip_id.input_line_ids.filtered(
                                                lambda r: r.code == line_id.code)
                                            if input_line_ids:
                                                if input_line_ids.mapped('description')[0]:
                                                    sheet.write_string(row, col + 23,
                                                                       str(input_line_ids.mapped('description')[0]),
                                                                       main_heading)
                                        if line_id.quantity:
                                            sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                            qty += line_id.quantity
                                        if line_id.rate:
                                            sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                            rate = line_id.rate
                                        if line_id.amount:
                                            sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                            amount += line_id.amount
                                        if line_id.total:
                                            sheet.write_number(row, col + 27, line_id.total, main_heading)
                                            total += line_id.total
                                        row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_number(row, col + 24, qty, main_heading)
                            grand_qty += qty
                            sheet.write_number(row, col + 27, total, main_heading)
                            grand_total += total
                            row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 24, grand_qty, main_heading)
                sheet.write_number(row, col + 27, grand_total, main_heading)
                row += 1
        if docs.grouping_by == 'by_salary_rule_name':
            self.env.ref(
                'bsg_payslip_variable_report.payslip_variable_report_xlsx_id').report_file = "Monthly variables On Payslips Grouping by Sales Rules Name Report "
            sheet.merge_range('A1:AE1', 'تقرير المتغيرات الشهرية في مسير الرواتب بحسب العناصر', main_heading3)
            sheet.merge_range('A2:AE2', 'Monthly variables On Payslips Grouping by Sales Rules Name Report ', main_heading3)
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'Employee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality (Country)', main_heading2)
            sheet.write(row, col + 5, 'ID NO', main_heading2)
            sheet.write(row, col + 6, 'Work Mobile', main_heading2)
            sheet.write(row, col + 7, 'Start Date', main_heading2)
            sheet.write(row, col + 8, 'Date of Join', main_heading2)
            sheet.write(row, col + 9, 'Date From', main_heading2)
            sheet.write(row, col + 10, 'Date To', main_heading2)
            sheet.write(row, col + 11, 'Payslip Batches', main_heading2)
            sheet.write(row, col + 12, 'Reference', main_heading2)
            sheet.write(row, col + 13, 'Payslip Name', main_heading2)
            sheet.write(row, col + 14, 'Branch', main_heading2)
            sheet.write(row, col + 15, 'Department', main_heading2)
            sheet.write(row, col + 16, 'Job Position', main_heading2)
            sheet.write(row, col + 17, 'Status', main_heading2)
            sheet.write(row, col + 18, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 19, 'Salary Structure', main_heading2)
            sheet.write(row, col + 20, 'Sequence', main_heading2)
            sheet.write(row, col + 21, 'Rule Code', main_heading2)
            sheet.write(row, col + 22, 'Rule Category Name', main_heading2)
            sheet.write(row, col + 23, 'Description', main_heading2)
            sheet.write(row, col + 24, 'Quantity', main_heading2)
            sheet.write(row, col + 25, 'Rate (%)', main_heading2)
            sheet.write(row, col + 26, 'Amount', main_heading2)
            sheet.write(row, col + 27, 'Total', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, 'رقم بطاقة الهوية', main_heading2)
            sheet.write(row, col + 6, 'رقم جوال الموظف', main_heading2)
            sheet.write(row, col + 7, 'تاريخ الالتحاق', main_heading2)
            sheet.write(row, col + 8, 'تاريخ الالتحاق ', main_heading2)
            sheet.write(row, col + 9, 'من تاريخ', main_heading2)
            sheet.write(row, col + 10, 'الي تاريخ', main_heading2)
            sheet.write(row, col + 11, 'اسم دفعة مسير الرواتب', main_heading2)
            sheet.write(row, col + 12, 'مرجع مسير الرواتب', main_heading2)
            sheet.write(row, col + 13, 'وصف مسير الرواتب', main_heading2)
            sheet.write(row, col + 14, 'الفرع ', main_heading2)
            sheet.write(row, col + 15, 'الإدارة', main_heading2)
            sheet.write(row, col + 16, 'المنصب الوظيفي', main_heading2)
            sheet.write(row, col + 17, 'حالة المسير', main_heading2)
            sheet.write(row, col + 18, 'طريقة الدفع', main_heading2)
            sheet.write(row, col + 19, 'هيكل الرواتب', main_heading2)
            sheet.write(row, col + 20, 'رقم التسلسل', main_heading2)
            sheet.write(row, col + 21, 'كود العنصر', main_heading2)
            sheet.write(row, col + 22, 'اسم فئة العنصر', main_heading2)
            sheet.write(row, col + 23, 'الوصف', main_heading2)
            sheet.write(row, col + 24, 'الكمية', main_heading2)
            sheet.write(row, col + 25, 'النسبة', main_heading2)
            sheet.write(row, col + 26, 'القيمة', main_heading2)
            sheet.write(row, col + 27, 'الإجمالي', main_heading2)
            row += 1
            rule_ids = self.env['hr.salary.rule'].search([])
            if docs.rule_ids:
                rule_ids = rule_ids.filtered(lambda r:r.id in docs.rule_ids.ids)
            grand_qty = 0
            grand_rate = 0
            grand_amount = 0
            grand_total = 0
            for rule_id in rule_ids:
                sheet.write(row, col, 'Salary Rule Name', main_heading2)
                sheet.write_string(row, col + 1,str(rule_id.name),main_heading)
                sheet.write(row, col + 2, 'اسم قاعدة الراتب', main_heading2)
                row += 1
                qty = 0
                rate = 0
                amount = 0
                total = 0
                for payslip_id in payslip_ids:
                    if rule_id.code in payslip_id.line_ids.mapped('code'):
                        line_ids = payslip_id.line_ids
                        if docs.rule_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                        if docs.rule_category_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                        for line_id in line_ids:
                            if line_id.code == rule_id.code and line_id.total != 0:
                                if payslip_id.employee_id.driver_code:
                                    sheet.write_string(row, col, str(payslip_id.employee_id.driver_code), main_heading)
                                if payslip_id.employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                       main_heading)
                                if payslip_id.employee_id.name:
                                    sheet.write_string(row, col + 2, str(payslip_id.employee_id.name), main_heading)
                                if payslip_id.employee_state:
                                    sheet.write_string(row, col + 3, str(payslip_id.employee_state), main_heading)
                                if payslip_id.employee_id.country_id.name:
                                    sheet.write_string(row, col + 4, str(payslip_id.employee_id.country_id.name),
                                                       main_heading)
                                if payslip_id.employee_id.country_id:
                                    if payslip_id.employee_id.country_id.code == 'SA':
                                        if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if payslip_id.employee_id.mobile_phone:
                                    sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                       main_heading)
                                if payslip_id.contract_id.date_start:
                                    sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                       main_heading)
                                if payslip_id.employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 8, str(payslip_id.employee_id.bsgjoining_date),
                                                       main_heading)
                                if payslip_id.date_from:
                                    sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                if payslip_id.date_to:
                                    sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                if payslip_id.payslip_run_id.name:
                                    sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name), main_heading)
                                if payslip_id.number:
                                    sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                if payslip_id.name:
                                    sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                if payslip_id.branch_id.branch_name:
                                    sheet.write_string(row, col + 14, str(payslip_id.branch_id.branch_name),
                                                       main_heading)
                                if payslip_id.department_id.display_name:
                                    sheet.write_string(row, col + 15, str(payslip_id.department_id.display_name),
                                                       main_heading)
                                if payslip_id.job_id.name:
                                    sheet.write_string(row, col + 16, str(payslip_id.job_id.name), main_heading)
                                if payslip_id.state:
                                    sheet.write_string(row, col + 17, str(payslip_id.state), main_heading)
                                if payslip_id.salary_payment_method:
                                    sheet.write_string(row, col + 18, str(payslip_id.salary_payment_method),
                                                       main_heading)
                                if payslip_id.struct_id.name:
                                    sheet.write_string(row, col + 19, str(payslip_id.struct_id.name), main_heading)
                                if line_id.sequence:
                                    sheet.write_string(row, col + 20, str(line_id.sequence), main_heading)
                                if line_id.code:
                                    sheet.write_string(row, col + 21, str(line_id.code), main_heading)
                                if line_id.category_id.name:
                                    sheet.write_string(row, col + 22, str(line_id.category_id.name), main_heading)
                                if payslip_id.input_line_ids:
                                    input_line_ids = payslip_id.input_line_ids.filtered(
                                        lambda r: r.code == line_id.code)
                                    if input_line_ids:
                                        if input_line_ids.mapped('description')[0]:
                                            sheet.write_string(row, col + 23,
                                                               str(input_line_ids.mapped('description')[0]),
                                                               main_heading)
                                if line_id.quantity:
                                    sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                    qty += line_id.quantity
                                if line_id.rate:
                                    sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                    rate = line_id.rate
                                if line_id.amount:
                                    sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                    amount += line_id.amount
                                if line_id.total:
                                    sheet.write_number(row, col + 27, line_id.total, main_heading)
                                    total += line_id.total
                                row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 24, qty, main_heading)
                grand_qty += qty
                sheet.write_number(row, col + 27, total, main_heading)
                grand_total += total
                row += 1
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 24, grand_qty, main_heading)
            sheet.write_number(row, col + 27, grand_total, main_heading)
            row += 1
        if docs.grouping_by == 'by_salary_rule_category':
            self.env.ref(
                'bsg_payslip_variable_report.payslip_variable_report_xlsx_id').report_file = "Monthly variables On Payslips Grouping by Sales Rules Category Report "
            sheet.merge_range('A1:AE1', 'تقرير المتغيرات الشهرية في مسير الرواتب بحسب فئة العناصر', main_heading3)
            sheet.merge_range('A2:AE2', 'Monthly variables On Payslips Grouping by Sales Rules Category Report ', main_heading3)
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'Employee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality (Country)', main_heading2)
            sheet.write(row, col + 5, 'ID NO', main_heading2)
            sheet.write(row, col + 6, 'Work Mobile', main_heading2)
            sheet.write(row, col + 7, 'Start Date', main_heading2)
            sheet.write(row, col + 8, 'Date of Join', main_heading2)
            sheet.write(row, col + 9, 'Date From', main_heading2)
            sheet.write(row, col + 10, 'Date To', main_heading2)
            sheet.write(row, col + 11, 'Payslip Batches', main_heading2)
            sheet.write(row, col + 12, 'Reference', main_heading2)
            sheet.write(row, col + 13, 'Payslip Name', main_heading2)
            sheet.write(row, col + 14, 'Branch', main_heading2)
            sheet.write(row, col + 15, 'Department', main_heading2)
            sheet.write(row, col + 16, 'Job Position', main_heading2)
            sheet.write(row, col + 17, 'Status', main_heading2)
            sheet.write(row, col + 18, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 19, 'Salary Structure', main_heading2)
            sheet.write(row, col + 20, 'Sequence', main_heading2)
            sheet.write(row, col + 21, 'Rule Name', main_heading2)
            sheet.write(row, col + 22, 'Rule Code', main_heading2)
            sheet.write(row, col + 23, 'Description', main_heading2)
            sheet.write(row, col + 24, 'Quantity', main_heading2)
            sheet.write(row, col + 25, 'Rate (%)', main_heading2)
            sheet.write(row, col + 26, 'Amount', main_heading2)
            sheet.write(row, col + 27, 'Total', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, 'رقم بطاقة الهوية', main_heading2)
            sheet.write(row, col + 6, 'رقم جوال الموظف', main_heading2)
            sheet.write(row, col + 7, 'تاريخ الالتحاق', main_heading2)
            sheet.write(row, col + 8, 'تاريخ الالتحاق ', main_heading2)
            sheet.write(row, col + 9, 'من تاريخ', main_heading2)
            sheet.write(row, col + 10, 'الي تاريخ', main_heading2)
            sheet.write(row, col + 11, 'اسم دفعة مسير الرواتب', main_heading2)
            sheet.write(row, col + 12, 'مرجع مسير الرواتب', main_heading2)
            sheet.write(row, col + 13, 'وصف مسير الرواتب', main_heading2)
            sheet.write(row, col + 14, 'الفرع ', main_heading2)
            sheet.write(row, col + 15, 'الإدارة', main_heading2)
            sheet.write(row, col + 16, 'المنصب الوظيفي', main_heading2)
            sheet.write(row, col + 17, 'حالة المسير', main_heading2)
            sheet.write(row, col + 18, 'طريقة الدفع', main_heading2)
            sheet.write(row, col + 19, 'هيكل الرواتب', main_heading2)
            sheet.write(row, col + 20, 'رقم التسلسل', main_heading2)
            sheet.write(row, col + 21, 'اسم العنصر', main_heading2)
            sheet.write(row, col + 22, 'كود العنصر', main_heading2)
            sheet.write(row, col + 23, 'الوصف', main_heading2)
            sheet.write(row, col + 24, 'الكمية', main_heading2)
            sheet.write(row, col + 25, 'النسبة', main_heading2)
            sheet.write(row, col + 26, 'القيمة', main_heading2)
            sheet.write(row, col + 27, 'الإجمالي', main_heading2)
            row += 1
            category_ids = self.env['hr.salary.rule.category'].search([])
            if docs.rule_category_ids:
                category_ids = category_ids.filtered(lambda r: r.id in docs.rule_category_ids.ids)
            grand_qty = 0
            grand_rate = 0
            grand_amount = 0
            grand_total = 0
            for category_id in category_ids:
                sheet.write(row, col, 'Salary Rule Category', main_heading2)
                sheet.write_string(row, col + 1, str(category_id.name), main_heading)
                sheet.write(row, col + 2, 'اسم قاعدة الراتب', main_heading2)
                row += 1
                qty = 0
                rate = 0
                amount = 0
                total = 0
                for payslip_id in payslip_ids:
                    if category_id.id in payslip_id.line_ids.mapped('category_id').ids:
                        line_ids = payslip_id.line_ids
                        if docs.rule_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                        if docs.rule_category_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                        for line_id in line_ids:
                            if line_id.category_id.id == category_id.id and line_id.total != 0:
                                if payslip_id.employee_id.driver_code:
                                    sheet.write_string(row, col, str(payslip_id.employee_id.driver_code), main_heading)
                                if payslip_id.employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                       main_heading)
                                if payslip_id.employee_id.name:
                                    sheet.write_string(row, col + 2, str(payslip_id.employee_id.name), main_heading)
                                if payslip_id.employee_state:
                                    sheet.write_string(row, col + 3, str(payslip_id.employee_state), main_heading)
                                if payslip_id.employee_id.country_id.name:
                                    sheet.write_string(row, col + 4, str(payslip_id.employee_id.country_id.name),
                                                       main_heading)
                                if payslip_id.employee_id.country_id:
                                    if payslip_id.employee_id.country_id.code == 'SA':
                                        if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if payslip_id.employee_id.mobile_phone:
                                    sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                       main_heading)
                                if payslip_id.contract_id.date_start:
                                    sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                       main_heading)
                                if payslip_id.employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 8, str(payslip_id.employee_id.bsgjoining_date),
                                                       main_heading)
                                if payslip_id.date_from:
                                    sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                if payslip_id.date_to:
                                    sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                if payslip_id.payslip_run_id.name:
                                    sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name), main_heading)
                                if payslip_id.number:
                                    sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                if payslip_id.name:
                                    sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                if payslip_id.branch_id.branch_name:
                                    sheet.write_string(row, col + 14, str(payslip_id.branch_id.branch_name),
                                                       main_heading)
                                if payslip_id.department_id.display_name:
                                    sheet.write_string(row, col + 15, str(payslip_id.department_id.display_name),
                                                       main_heading)
                                if payslip_id.job_id.name:
                                    sheet.write_string(row, col + 16, str(payslip_id.job_id.name), main_heading)
                                if payslip_id.state:
                                    sheet.write_string(row, col + 17, str(payslip_id.state), main_heading)
                                if payslip_id.salary_payment_method:
                                    sheet.write_string(row, col + 18, str(payslip_id.salary_payment_method),
                                                       main_heading)
                                if payslip_id.struct_id.name:
                                    sheet.write_string(row, col + 19, str(payslip_id.struct_id.name), main_heading)
                                if line_id.sequence:
                                    sheet.write_string(row, col + 20, str(line_id.sequence), main_heading)
                                if line_id.name:
                                    sheet.write_string(row, col + 21, str(line_id.name), main_heading)
                                if line_id.code:
                                    sheet.write_string(row, col + 22, str(line_id.code), main_heading)
                                if payslip_id.input_line_ids:
                                    input_line_ids = payslip_id.input_line_ids.filtered(
                                        lambda r: r.code == line_id.code)
                                    if input_line_ids:
                                        if input_line_ids.mapped('description')[0]:
                                            sheet.write_string(row, col + 23,
                                                               str(input_line_ids.mapped('description')[0]),
                                                               main_heading)
                                if line_id.quantity:
                                    sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                    qty += line_id.quantity
                                if line_id.rate:
                                    sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                    rate = line_id.rate
                                if line_id.amount:
                                    sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                    amount += line_id.amount
                                if line_id.total:
                                    sheet.write_number(row, col + 27, line_id.total, main_heading)
                                    total += line_id.total
                                row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 24, qty, main_heading)
                grand_qty += qty
                sheet.write_number(row, col + 27, total, main_heading)
                grand_total += total
                row += 1
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 24, grand_qty, main_heading)
            sheet.write_number(row, col + 27, grand_total, main_heading)
            row += 1
        if docs.grouping_by == 'by_payslip_periods':
            self.env.ref('bsg_payslip_variable_report.payslip_variable_report_xlsx_id').report_file = "Monthly variables On Payslips Grouping by Payslip Periods Report "
            sheet.merge_range('A1:AE1', 'تقرير المتغيرات الشهرية في مسير الرواتب بحسب فترة المسيرات', main_heading3)
            sheet.merge_range('A2:AE2', 'Monthly variables On Payslips Grouping by Payslip Periods Report ', main_heading3)
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'Employee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality (Country)', main_heading2)
            sheet.write(row, col + 5, 'ID NO', main_heading2)
            sheet.write(row, col + 6, 'Work Mobile', main_heading2)
            sheet.write(row, col + 7, 'Start Date', main_heading2)
            sheet.write(row, col + 8, 'Date of Join', main_heading2)
            sheet.write(row, col + 9, 'Date From', main_heading2)
            sheet.write(row, col + 10, 'Date To', main_heading2)
            sheet.write(row, col + 11, 'Payslip Batches', main_heading2)
            sheet.write(row, col + 12, 'Reference', main_heading2)
            sheet.write(row, col + 13, 'Payslip Name', main_heading2)
            sheet.write(row, col + 14, 'Branch', main_heading2)
            sheet.write(row, col + 15, 'Department', main_heading2)
            sheet.write(row, col + 16, 'Job Position', main_heading2)
            sheet.write(row, col + 17, 'Status', main_heading2)
            sheet.write(row, col + 18, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 19, 'Salary Structure', main_heading2)
            sheet.write(row, col + 20, 'Sequence', main_heading2)
            sheet.write(row, col + 21, 'Rule Name', main_heading2)
            sheet.write(row, col + 22, 'Rule Code', main_heading2)
            sheet.write(row, col + 23, 'Rule Category Name', main_heading2)
            sheet.write(row, col + 24, 'Description', main_heading2)
            sheet.write(row, col + 25, 'Quantity', main_heading2)
            sheet.write(row, col + 26, 'Rate (%)', main_heading2)
            sheet.write(row, col + 27, 'Amount', main_heading2)
            sheet.write(row, col + 28, 'Total', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, 'رقم بطاقة الهوية', main_heading2)
            sheet.write(row, col + 6, 'رقم جوال الموظف', main_heading2)
            sheet.write(row, col + 7, 'تاريخ الالتحاق', main_heading2)
            sheet.write(row, col + 8, 'تاريخ الالتحاق ', main_heading2)
            sheet.write(row, col + 9, 'من تاريخ', main_heading2)
            sheet.write(row, col + 10, 'الي تاريخ', main_heading2)
            sheet.write(row, col + 11, 'اسم دفعة مسير الرواتب', main_heading2)
            sheet.write(row, col + 12, 'مرجع مسير الرواتب', main_heading2)
            sheet.write(row, col + 13, 'وصف مسير الرواتب', main_heading2)
            sheet.write(row, col + 14, 'الفرع ', main_heading2)
            sheet.write(row, col + 15, 'الإدارة', main_heading2)
            sheet.write(row, col + 16, 'المنصب الوظيفي', main_heading2)
            sheet.write(row, col + 17, 'حالة المسير', main_heading2)
            sheet.write(row, col + 18, 'طريقة الدفع', main_heading2)
            sheet.write(row, col + 19, 'هيكل الرواتب', main_heading2)
            sheet.write(row, col + 20, 'رقم التسلسل', main_heading2)
            sheet.write(row, col + 21, 'اسم العنصر', main_heading2)
            sheet.write(row, col + 22, 'كود العنصر', main_heading2)
            sheet.write(row, col + 23, 'اسم فئة العنصر', main_heading2)
            sheet.write(row, col + 24, 'الوصف', main_heading2)
            sheet.write(row, col + 25, 'الكمية', main_heading2)
            sheet.write(row, col + 26, 'النسبة', main_heading2)
            sheet.write(row, col + 27, 'القيمة', main_heading2)
            sheet.write(row, col + 28, 'الإجمالي', main_heading2)
            row += 1
            if not docs.period_grouping_by:
                date_list = []
                grand_qty = 0
                grand_rate = 0
                grand_amount = 0
                grand_total = 0
                for payslip_id in payslip_ids:
                    if payslip_id:
                        if payslip_id.date_from not in date_list:
                            date_list.append(payslip_id.date_from)
                for date_id in date_list:
                    if date_id:
                        qty = 0
                        rate = 0
                        amount = 0
                        total = 0
                        sheet.write(row, col, 'Date', main_heading2)
                        sheet.write_string(row, col + 1, str(date_id), main_heading)
                        sheet.write(row, col + 2, 'تاريخ', main_heading2)
                        row += 1
                        filtered_payslip_ids = payslip_ids.filtered(lambda r: r.date_from and r.date_from == date_id)
                        for payslip_id in filtered_payslip_ids:
                            line_ids = payslip_id.line_ids
                            if docs.rule_ids:
                                line_ids = line_ids.filtered(
                                    lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                            if docs.rule_category_ids:
                                line_ids = line_ids.filtered(
                                    lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                            for line_id in line_ids:
                                if line_id.total != 0:
                                    if payslip_id.employee_id.driver_code:
                                        sheet.write_string(row, col, str(payslip_id.employee_id.driver_code),
                                                           main_heading)
                                    if payslip_id.employee_id.employee_code:
                                        sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                           main_heading)
                                    if payslip_id.employee_id.name:
                                        sheet.write_string(row, col + 2, str(payslip_id.employee_id.name), main_heading)
                                    if payslip_id.employee_state:
                                        sheet.write_string(row, col + 3, str(payslip_id.employee_state), main_heading)
                                    if payslip_id.employee_id.country_id.name:
                                        sheet.write_string(row, col + 4, str(payslip_id.employee_id.country_id.name),
                                                           main_heading)
                                    if payslip_id.employee_id.country_id:
                                        if payslip_id.employee_id.country_id.code == 'SA':
                                            if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                                sheet.write_string(row, col + 5,
                                                                   str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                                   main_heading)
                                        else:
                                            if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                                sheet.write_string(row, col + 5,
                                                                   str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                                   main_heading)
                                    if payslip_id.employee_id.mobile_phone:
                                        sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                           main_heading)
                                    if payslip_id.contract_id.date_start:
                                        sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                           main_heading)
                                    if payslip_id.employee_id.bsgjoining_date:
                                        sheet.write_string(row, col + 8, str(payslip_id.employee_id.bsgjoining_date),
                                                           main_heading)
                                    if payslip_id.date_from:
                                        sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                    if payslip_id.date_to:
                                        sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                    if payslip_id.payslip_run_id.name:
                                        sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name),
                                                           main_heading)
                                    if payslip_id.number:
                                        sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                    if payslip_id.name:
                                        sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                    if payslip_id.branch_id.branch_name:
                                        sheet.write_string(row, col + 14, str(payslip_id.branch_id.branch_name),
                                                           main_heading)
                                    if payslip_id.department_id.display_name:
                                        sheet.write_string(row, col + 15, str(payslip_id.department_id.display_name),
                                                           main_heading)
                                    if payslip_id.job_id.name:
                                        sheet.write_string(row, col + 16, str(payslip_id.job_id.name), main_heading)
                                    if payslip_id.state:
                                        sheet.write_string(row, col + 17, str(payslip_id.state), main_heading)
                                    if payslip_id.salary_payment_method:
                                        sheet.write_string(row, col + 18, str(payslip_id.salary_payment_method),
                                                           main_heading)
                                    if payslip_id.struct_id.name:
                                        sheet.write_string(row, col + 19, str(payslip_id.struct_id.name), main_heading)
                                    if line_id.sequence:
                                        sheet.write_string(row, col + 20, str(line_id.sequence), main_heading)
                                    if line_id.name:
                                        sheet.write_string(row, col + 21, str(line_id.name), main_heading)
                                    if line_id.code:
                                        sheet.write_string(row, col + 22, str(line_id.code), main_heading)
                                    if line_id.category_id.name:
                                        sheet.write_string(row, col + 23, str(line_id.category_id.name), main_heading)
                                    if payslip_id.input_line_ids:
                                        input_line_ids = payslip_id.input_line_ids.filtered(
                                            lambda r: r.code == line_id.code)
                                        if input_line_ids:
                                            if input_line_ids.mapped('description')[0]:
                                                sheet.write_string(row, col + 24,
                                                                   str(input_line_ids.mapped('description')[0]),
                                                                   main_heading)
                                    if line_id.quantity:
                                        sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                        qty += line_id.quantity
                                    if line_id.rate:
                                        sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                        rate = line_id.rate
                                    if line_id.amount:
                                        sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                        amount += line_id.amount
                                    if line_id.total:
                                        sheet.write_number(row, col + 27, line_id.total, main_heading)
                                        total += line_id.total
                                    row += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_number(row, col + 24, qty, main_heading)
                        grand_qty += qty
                        sheet.write_number(row, col + 27, total, main_heading)
                        grand_total += total
                        row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 24, grand_qty, main_heading)
                sheet.write_number(row, col + 27, grand_total, main_heading)
                row += 1
            if docs.period_grouping_by == 'month':
                months_list = []
                grand_qty = 0
                grand_rate = 0
                grand_amount = 0
                grand_total = 0
                for payslip_id in payslip_ids:
                    if payslip_id.date_from:
                        if payslip_id.date_from.strftime('%B') not in months_list:
                            months_list.append(payslip_id.date_from.strftime('%B'))
                for month in months_list:
                    qty = 0
                    rate = 0
                    amount = 0
                    total = 0
                    sheet.write(row, col, 'Month', main_heading2)
                    sheet.write_string(row, col + 1, str(month), main_heading)
                    sheet.write(row, col + 2, 'شهر', main_heading2)
                    row += 1
                    filtered_payslip_ids = payslip_ids.filtered(lambda r: r.date_from and r.date_from.strftime('%B') == month)
                    for payslip_id in filtered_payslip_ids:
                        line_ids = payslip_id.line_ids
                        if docs.rule_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                        if docs.rule_category_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                        for line_id in line_ids:
                            if line_id.total != 0:
                                if payslip_id.employee_id.driver_code:
                                    sheet.write_string(row, col, str(payslip_id.employee_id.driver_code), main_heading)
                                if payslip_id.employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                       main_heading)
                                if payslip_id.employee_id.name:
                                    sheet.write_string(row, col + 2, str(payslip_id.employee_id.name), main_heading)
                                if payslip_id.employee_state:
                                    sheet.write_string(row, col + 3, str(payslip_id.employee_state), main_heading)
                                if payslip_id.employee_id.country_id.name:
                                    sheet.write_string(row, col + 4, str(payslip_id.employee_id.country_id.name),
                                                       main_heading)
                                if payslip_id.employee_id.country_id:
                                    if payslip_id.employee_id.country_id.code == 'SA':
                                        if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if payslip_id.employee_id.mobile_phone:
                                    sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                       main_heading)
                                if payslip_id.contract_id.date_start:
                                    sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                       main_heading)
                                if payslip_id.employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 8, str(payslip_id.employee_id.bsgjoining_date),
                                                       main_heading)
                                if payslip_id.date_from:
                                    sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                if payslip_id.date_to:
                                    sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                if payslip_id.payslip_run_id.name:
                                    sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name), main_heading)
                                if payslip_id.number:
                                    sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                if payslip_id.name:
                                    sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                if payslip_id.branch_id.branch_name:
                                    sheet.write_string(row, col + 14, str(payslip_id.branch_id.branch_name),
                                                       main_heading)
                                if payslip_id.department_id.display_name:
                                    sheet.write_string(row, col + 15, str(payslip_id.department_id.display_name),
                                                       main_heading)
                                if payslip_id.job_id.name:
                                    sheet.write_string(row, col + 16, str(payslip_id.job_id.name), main_heading)
                                if payslip_id.state:
                                    sheet.write_string(row, col + 17, str(payslip_id.state), main_heading)
                                if payslip_id.salary_payment_method:
                                    sheet.write_string(row, col + 18, str(payslip_id.salary_payment_method),
                                                       main_heading)
                                if payslip_id.struct_id.name:
                                    sheet.write_string(row, col + 19, str(payslip_id.struct_id.name), main_heading)
                                if line_id.sequence:
                                    sheet.write_string(row, col + 20, str(line_id.sequence), main_heading)
                                if line_id.name:
                                    sheet.write_string(row, col + 21, str(line_id.name), main_heading)
                                if line_id.code:
                                    sheet.write_string(row, col + 22, str(line_id.code), main_heading)
                                if line_id.category_id.name:
                                    sheet.write_string(row, col + 23, str(line_id.category_id.name), main_heading)
                                if payslip_id.input_line_ids:
                                    input_line_ids = payslip_id.input_line_ids.filtered(
                                        lambda r: r.code == line_id.code)
                                    if input_line_ids:
                                        if input_line_ids.mapped('description')[0]:
                                            sheet.write_string(row, col + 24,
                                                               str(input_line_ids.mapped('description')[0]),
                                                               main_heading)
                                if line_id.quantity:
                                    sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                    qty += line_id.quantity
                                if line_id.rate:
                                    sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                    rate = line_id.rate
                                if line_id.amount:
                                    sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                    amount += line_id.amount
                                if line_id.total:
                                    sheet.write_number(row, col + 27, line_id.total, main_heading)
                                    total += line_id.total
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_number(row, col + 24, qty, main_heading)
                    grand_qty += qty
                    sheet.write_number(row, col + 27, total, main_heading)
                    grand_total += total
                    row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 24, grand_qty, main_heading)
                sheet.write_number(row, col + 27, grand_total, main_heading)
                row += 1
            if docs.period_grouping_by == 'year':
                years_list = []
                grand_qty = 0
                grand_rate = 0
                grand_amount = 0
                grand_total = 0
                for payslip_id in payslip_ids:
                    if payslip_id.date_from:
                        if payslip_id.date_from.year not in years_list:
                            years_list.append(payslip_id.date_from.year)
                if years_list:
                    for year in years_list:
                        if year:
                            qty = 0
                            rate = 0
                            amount = 0
                            total = 0
                            sheet.write(row, col, 'Year', main_heading2)
                            sheet.write_string(row, col + 1, str(year), main_heading)
                            sheet.write(row, col + 2, 'عام', main_heading2)
                            row += 1
                            filtered_payslip_ids = payslip_ids.filtered(lambda r: r.date_from and r.date_from.year == year)
                            for payslip_id in filtered_payslip_ids:
                                line_ids = payslip_id.line_ids
                                if docs.rule_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                                if docs.rule_category_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                                for line_id in line_ids:
                                    if line_id.total != 0:
                                        if payslip_id.employee_id.driver_code:
                                            sheet.write_string(row, col, str(payslip_id.employee_id.driver_code),
                                                               main_heading)
                                        if payslip_id.employee_id.employee_code:
                                            sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                               main_heading)
                                        if payslip_id.employee_id.name:
                                            sheet.write_string(row, col + 2, str(payslip_id.employee_id.name),
                                                               main_heading)
                                        if payslip_id.employee_state:
                                            sheet.write_string(row, col + 3, str(payslip_id.employee_state),
                                                               main_heading)
                                        if payslip_id.employee_id.country_id.name:
                                            sheet.write_string(row, col + 4,
                                                               str(payslip_id.employee_id.country_id.name),
                                                               main_heading)
                                        if payslip_id.employee_id.country_id:
                                            if payslip_id.employee_id.country_id.code == 'SA':
                                                if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                                    sheet.write_string(row, col + 5,
                                                                       str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                                       main_heading)
                                            else:
                                                if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                                    sheet.write_string(row, col + 5,
                                                                       str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                                       main_heading)
                                        if payslip_id.employee_id.mobile_phone:
                                            sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                               main_heading)
                                        if payslip_id.contract_id.date_start:
                                            sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                               main_heading)
                                        if payslip_id.employee_id.bsgjoining_date:
                                            sheet.write_string(row, col + 8,
                                                               str(payslip_id.employee_id.bsgjoining_date),
                                                               main_heading)
                                        if payslip_id.date_from:
                                            sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                        if payslip_id.date_to:
                                            sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                        if payslip_id.payslip_run_id.name:
                                            sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name),
                                                               main_heading)
                                        if payslip_id.number:
                                            sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                        if payslip_id.name:
                                            sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                        if payslip_id.branch_id.branch_name:
                                            sheet.write_string(row, col + 14, str(payslip_id.branch_id.branch_name),
                                                               main_heading)
                                        if payslip_id.department_id.display_name:
                                            sheet.write_string(row, col + 15,
                                                               str(payslip_id.department_id.display_name), main_heading)
                                        if payslip_id.job_id.name:
                                            sheet.write_string(row, col + 16, str(payslip_id.job_id.name), main_heading)
                                        if payslip_id.state:
                                            sheet.write_string(row, col + 17, str(payslip_id.state), main_heading)
                                        if payslip_id.salary_payment_method:
                                            sheet.write_string(row, col + 18, str(payslip_id.salary_payment_method),
                                                               main_heading)
                                        if payslip_id.struct_id.name:
                                            sheet.write_string(row, col + 19, str(payslip_id.struct_id.name),
                                                               main_heading)
                                        if line_id.sequence:
                                            sheet.write_string(row, col + 20, str(line_id.sequence), main_heading)
                                        if line_id.name:
                                            sheet.write_string(row, col + 21, str(line_id.name), main_heading)
                                        if line_id.code:
                                            sheet.write_string(row, col + 22, str(line_id.code), main_heading)
                                        if line_id.category_id.name:
                                            sheet.write_string(row, col + 23, str(line_id.category_id.name),
                                                               main_heading)
                                        if payslip_id.input_line_ids:
                                            input_line_ids = payslip_id.input_line_ids.filtered(
                                                lambda r: r.code == line_id.code)
                                            if input_line_ids:
                                                if input_line_ids.mapped('description')[0]:
                                                    sheet.write_string(row, col + 24,
                                                                       str(input_line_ids.mapped('description')[0]),
                                                                       main_heading)
                                        if line_id.quantity:
                                            sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                            qty += line_id.quantity
                                        if line_id.rate:
                                            sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                            rate = line_id.rate
                                        if line_id.amount:
                                            sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                            amount += line_id.amount
                                        if line_id.total:
                                            sheet.write_number(row, col + 27, line_id.total, main_heading)
                                            total += line_id.total
                                        row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_number(row, col + 24, qty, main_heading)
                            grand_qty += qty
                            sheet.write_number(row, col + 27, total, main_heading)
                            grand_total += total
                            row += 1
                    sheet.write(row, col, 'Grand Total', main_heading2)
                    sheet.write_number(row, col + 24, grand_qty, main_heading)
                    sheet.write_number(row, col + 27, grand_total, main_heading)
                    row += 1
            if docs.period_grouping_by == 'quarterly':
                grand_qty = 0
                grand_rate = 0
                grand_amount = 0
                grand_total = 0
                first_quarter = ['January', 'February', 'March']
                second_quarter = ['April', 'May', 'June']
                third_quarter = ['July', 'August', 'September']
                fourth_quarter = ['October', 'November', 'December']
                first_quarter_ids = payslip_ids.filtered(
                    lambda r: (r.date_from and r.date_from.strftime('%B') in first_quarter))
                second_quarter_ids = payslip_ids.filtered(
                    lambda r: (r.date_from and r.date_from.strftime('%B') in second_quarter))
                third_quarter_ids = payslip_ids.filtered(
                    lambda r: (r.date_from and r.date_from.strftime('%B') in third_quarter))
                fourth_quarter_ids = payslip_ids.filtered(
                    lambda r: (r.date_from and r.date_from.strftime('%B') in fourth_quarter))
                if first_quarter_ids:
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'First', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    qty = 0
                    rate = 0
                    amount = 0
                    total = 0
                    for payslip_id in first_quarter_ids:
                        line_ids = payslip_id.line_ids
                        if docs.rule_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                        if docs.rule_category_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                        for line_id in line_ids:
                            if line_id.total != 0:
                                if payslip_id.employee_id.driver_code:
                                    sheet.write_string(row, col, str(payslip_id.employee_id.driver_code), main_heading)
                                if payslip_id.employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                       main_heading)
                                if payslip_id.employee_id.name:
                                    sheet.write_string(row, col + 2, str(payslip_id.employee_id.name), main_heading)
                                if payslip_id.employee_state:
                                    sheet.write_string(row, col + 3, str(payslip_id.employee_state), main_heading)
                                if payslip_id.employee_id.country_id.name:
                                    sheet.write_string(row, col + 4, str(payslip_id.employee_id.country_id.name),
                                                       main_heading)
                                if payslip_id.employee_id.country_id:
                                    if payslip_id.employee_id.country_id.code == 'SA':
                                        if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if payslip_id.employee_id.mobile_phone:
                                    sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                       main_heading)
                                if payslip_id.contract_id.date_start:
                                    sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                       main_heading)
                                if payslip_id.employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 8, str(payslip_id.employee_id.bsgjoining_date),
                                                       main_heading)
                                if payslip_id.date_from:
                                    sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                if payslip_id.date_to:
                                    sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                if payslip_id.payslip_run_id.name:
                                    sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name), main_heading)
                                if payslip_id.number:
                                    sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                if payslip_id.name:
                                    sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                if payslip_id.branch_id.branch_name:
                                    sheet.write_string(row, col + 14, str(payslip_id.branch_id.branch_name),
                                                       main_heading)
                                if payslip_id.department_id.display_name:
                                    sheet.write_string(row, col + 15, str(payslip_id.department_id.display_name),
                                                       main_heading)
                                if payslip_id.job_id.name:
                                    sheet.write_string(row, col + 16, str(payslip_id.job_id.name), main_heading)
                                if payslip_id.state:
                                    sheet.write_string(row, col + 17, str(payslip_id.state), main_heading)
                                if payslip_id.salary_payment_method:
                                    sheet.write_string(row, col + 18, str(payslip_id.salary_payment_method),
                                                       main_heading)
                                if payslip_id.struct_id.name:
                                    sheet.write_string(row, col + 19, str(payslip_id.struct_id.name), main_heading)
                                if line_id.sequence:
                                    sheet.write_string(row, col + 20, str(line_id.sequence), main_heading)
                                if line_id.name:
                                    sheet.write_string(row, col + 21, str(line_id.name), main_heading)
                                if line_id.code:
                                    sheet.write_string(row, col + 22, str(line_id.code), main_heading)
                                if line_id.category_id.name:
                                    sheet.write_string(row, col + 23, str(line_id.category_id.name), main_heading)
                                if payslip_id.input_line_ids:
                                    input_line_ids = payslip_id.input_line_ids.filtered(
                                        lambda r: r.code == line_id.code)
                                    if input_line_ids:
                                        if input_line_ids.mapped('description')[0]:
                                            sheet.write_string(row, col + 24,
                                                               str(input_line_ids.mapped('description')[0]),
                                                               main_heading)
                                if line_id.quantity:
                                    sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                    qty += line_id.quantity
                                if line_id.rate:
                                    sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                    rate = line_id.rate
                                if line_id.amount:
                                    sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                    amount += line_id.amount
                                if line_id.total:
                                    sheet.write_number(row, col + 27, line_id.total, main_heading)
                                    total += line_id.total
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_number(row, col + 24, qty, main_heading)
                    grand_qty += qty
                    sheet.write_number(row, col + 27, total, main_heading)
                    grand_total += total
                    row += 1
                if second_quarter_ids:
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Second', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    qty = 0
                    rate = 0
                    amount = 0
                    total = 0
                    for payslip_id in second_quarter_ids:
                        line_ids = payslip_id.line_ids
                        if docs.rule_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                        if docs.rule_category_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                        for line_id in line_ids:
                            if line_id.total != 0:
                                if payslip_id.employee_id.driver_code:
                                    sheet.write_string(row, col, str(payslip_id.employee_id.driver_code), main_heading)
                                if payslip_id.employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                       main_heading)
                                if payslip_id.employee_id.name:
                                    sheet.write_string(row, col + 2, str(payslip_id.employee_id.name), main_heading)
                                if payslip_id.employee_state:
                                    sheet.write_string(row, col + 3, str(payslip_id.employee_state), main_heading)
                                if payslip_id.employee_id.country_id.name:
                                    sheet.write_string(row, col + 4, str(payslip_id.employee_id.country_id.name),
                                                       main_heading)
                                if payslip_id.employee_id.country_id:
                                    if payslip_id.employee_id.country_id.code == 'SA':
                                        if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if payslip_id.employee_id.mobile_phone:
                                    sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                       main_heading)
                                if payslip_id.contract_id.date_start:
                                    sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                       main_heading)
                                if payslip_id.employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 8, str(payslip_id.employee_id.bsgjoining_date),
                                                       main_heading)
                                if payslip_id.date_from:
                                    sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                if payslip_id.date_to:
                                    sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                if payslip_id.payslip_run_id.name:
                                    sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name), main_heading)
                                if payslip_id.number:
                                    sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                if payslip_id.name:
                                    sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                if payslip_id.branch_id.branch_name:
                                    sheet.write_string(row, col + 14, str(payslip_id.branch_id.branch_name),
                                                       main_heading)
                                if payslip_id.department_id.display_name:
                                    sheet.write_string(row, col + 15, str(payslip_id.department_id.display_name),
                                                       main_heading)
                                if payslip_id.job_id.name:
                                    sheet.write_string(row, col + 16, str(payslip_id.job_id.name), main_heading)
                                if payslip_id.state:
                                    sheet.write_string(row, col + 17, str(payslip_id.state), main_heading)
                                if payslip_id.salary_payment_method:
                                    sheet.write_string(row, col + 18, str(payslip_id.salary_payment_method),
                                                       main_heading)
                                if payslip_id.struct_id.name:
                                    sheet.write_string(row, col + 19, str(payslip_id.struct_id.name), main_heading)
                                if line_id.sequence:
                                    sheet.write_string(row, col + 20, str(line_id.sequence), main_heading)
                                if line_id.name:
                                    sheet.write_string(row, col + 21, str(line_id.name), main_heading)
                                if line_id.code:
                                    sheet.write_string(row, col + 22, str(line_id.code), main_heading)
                                if line_id.category_id.name:
                                    sheet.write_string(row, col + 23, str(line_id.category_id.name), main_heading)
                                if payslip_id.input_line_ids:
                                    input_line_ids = payslip_id.input_line_ids.filtered(
                                        lambda r: r.code == line_id.code)
                                    if input_line_ids:
                                        if input_line_ids.mapped('description')[0]:
                                            sheet.write_string(row, col + 24,
                                                               str(input_line_ids.mapped('description')[0]),
                                                               main_heading)
                                if line_id.quantity:
                                    sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                    qty += line_id.quantity
                                if line_id.rate:
                                    sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                    rate = line_id.rate
                                if line_id.amount:
                                    sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                    amount += line_id.amount
                                if line_id.total:
                                    sheet.write_number(row, col + 27, line_id.total, main_heading)
                                    total += line_id.total
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_number(row, col + 24, qty, main_heading)
                    grand_qty += qty
                    sheet.write_number(row, col + 27, total, main_heading)
                    grand_total += total
                    row += 1
                if third_quarter_ids:
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Third', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    qty = 0
                    rate = 0
                    amount = 0
                    total = 0
                    for payslip_id in third_quarter_ids:
                        line_ids = payslip_id.line_ids
                        if docs.rule_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                        if docs.rule_category_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                        for line_id in line_ids:
                            if line_id.total != 0:
                                if payslip_id.employee_id.driver_code:
                                    sheet.write_string(row, col, str(payslip_id.employee_id.driver_code), main_heading)
                                if payslip_id.employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                       main_heading)
                                if payslip_id.employee_id.name:
                                    sheet.write_string(row, col + 2, str(payslip_id.employee_id.name), main_heading)
                                if payslip_id.employee_state:
                                    sheet.write_string(row, col + 3, str(payslip_id.employee_state), main_heading)
                                if payslip_id.employee_id.country_id.name:
                                    sheet.write_string(row, col + 4, str(payslip_id.employee_id.country_id.name),
                                                       main_heading)
                                if payslip_id.employee_id.country_id:
                                    if payslip_id.employee_id.country_id.code == 'SA':
                                        if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if payslip_id.employee_id.mobile_phone:
                                    sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                       main_heading)
                                if payslip_id.contract_id.date_start:
                                    sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                       main_heading)
                                if payslip_id.employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 8, str(payslip_id.employee_id.bsgjoining_date),
                                                       main_heading)
                                if payslip_id.date_from:
                                    sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                if payslip_id.date_to:
                                    sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                if payslip_id.payslip_run_id.name:
                                    sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name), main_heading)
                                if payslip_id.number:
                                    sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                if payslip_id.name:
                                    sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                if payslip_id.branch_id.branch_name:
                                    sheet.write_string(row, col + 14, str(payslip_id.branch_id.branch_name),
                                                       main_heading)
                                if payslip_id.department_id.display_name:
                                    sheet.write_string(row, col + 15, str(payslip_id.department_id.display_name),
                                                       main_heading)
                                if payslip_id.job_id.name:
                                    sheet.write_string(row, col + 16, str(payslip_id.job_id.name), main_heading)
                                if payslip_id.state:
                                    sheet.write_string(row, col + 17, str(payslip_id.state), main_heading)
                                if payslip_id.salary_payment_method:
                                    sheet.write_string(row, col + 18, str(payslip_id.salary_payment_method),
                                                       main_heading)
                                if payslip_id.struct_id.name:
                                    sheet.write_string(row, col + 19, str(payslip_id.struct_id.name), main_heading)
                                if line_id.sequence:
                                    sheet.write_string(row, col + 20, str(line_id.sequence), main_heading)
                                if line_id.name:
                                    sheet.write_string(row, col + 21, str(line_id.name), main_heading)
                                if line_id.code:
                                    sheet.write_string(row, col + 22, str(line_id.code), main_heading)
                                if line_id.category_id.name:
                                    sheet.write_string(row, col + 23, str(line_id.category_id.name), main_heading)
                                if payslip_id.input_line_ids:
                                    input_line_ids = payslip_id.input_line_ids.filtered(
                                        lambda r: r.code == line_id.code)
                                    if input_line_ids:
                                        if input_line_ids.mapped('description')[0]:
                                            sheet.write_string(row, col + 24,
                                                               str(input_line_ids.mapped('description')[0]),
                                                               main_heading)
                                if line_id.quantity:
                                    sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                    qty += line_id.quantity
                                if line_id.rate:
                                    sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                    rate = line_id.rate
                                if line_id.amount:
                                    sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                    amount += line_id.amount
                                if line_id.total:
                                    sheet.write_number(row, col + 27, line_id.total, main_heading)
                                    total += line_id.total
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_number(row, col + 24, qty, main_heading)
                    grand_qty += qty
                    sheet.write_number(row, col + 27, total, main_heading)
                    grand_total += total
                    row += 1
                if fourth_quarter_ids:
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Fourth', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    qty = 0
                    rate = 0
                    amount = 0
                    total = 0
                    for payslip_id in fourth_quarter_ids:
                        line_ids = payslip_id.line_ids
                        if docs.rule_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                        if docs.rule_category_ids:
                            line_ids = line_ids.filtered(
                                lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                        for line_id in line_ids:
                            if line_id.total != 0:
                                if payslip_id.employee_id.driver_code:
                                    sheet.write_string(row, col, str(payslip_id.employee_id.driver_code), main_heading)
                                if payslip_id.employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                       main_heading)
                                if payslip_id.employee_id.name:
                                    sheet.write_string(row, col + 2, str(payslip_id.employee_id.name), main_heading)
                                if payslip_id.employee_state:
                                    sheet.write_string(row, col + 3, str(payslip_id.employee_state), main_heading)
                                if payslip_id.employee_id.country_id.name:
                                    sheet.write_string(row, col + 4, str(payslip_id.employee_id.country_id.name),
                                                       main_heading)
                                if payslip_id.employee_id.country_id:
                                    if payslip_id.employee_id.country_id.code == 'SA':
                                        if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 5,
                                                               str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if payslip_id.employee_id.mobile_phone:
                                    sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                       main_heading)
                                if payslip_id.contract_id.date_start:
                                    sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                       main_heading)
                                if payslip_id.employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 8, str(payslip_id.employee_id.bsgjoining_date),
                                                       main_heading)
                                if payslip_id.date_from:
                                    sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                if payslip_id.date_to:
                                    sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                if payslip_id.payslip_run_id.name:
                                    sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name), main_heading)
                                if payslip_id.number:
                                    sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                if payslip_id.name:
                                    sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                if payslip_id.branch_id.branch_name:
                                    sheet.write_string(row, col + 14, str(payslip_id.branch_id.branch_name),
                                                       main_heading)
                                if payslip_id.department_id.display_name:
                                    sheet.write_string(row, col + 15, str(payslip_id.department_id.display_name),
                                                       main_heading)
                                if payslip_id.job_id.name:
                                    sheet.write_string(row, col + 16, str(payslip_id.job_id.name), main_heading)
                                if payslip_id.state:
                                    sheet.write_string(row, col + 17, str(payslip_id.state), main_heading)
                                if payslip_id.salary_payment_method:
                                    sheet.write_string(row, col + 18, str(payslip_id.salary_payment_method),
                                                       main_heading)
                                if payslip_id.struct_id.name:
                                    sheet.write_string(row, col + 19, str(payslip_id.struct_id.name), main_heading)
                                if line_id.sequence:
                                    sheet.write_string(row, col + 20, str(line_id.sequence), main_heading)
                                if line_id.name:
                                    sheet.write_string(row, col + 21, str(line_id.name), main_heading)
                                if line_id.code:
                                    sheet.write_string(row, col + 22, str(line_id.code), main_heading)
                                if line_id.category_id.name:
                                    sheet.write_string(row, col + 23, str(line_id.category_id.name), main_heading)
                                if payslip_id.input_line_ids:
                                    input_line_ids = payslip_id.input_line_ids.filtered(
                                        lambda r: r.code == line_id.code)
                                    if input_line_ids:
                                        if input_line_ids.mapped('description')[0]:
                                            sheet.write_string(row, col + 24,
                                                               str(input_line_ids.mapped('description')[0]),
                                                               main_heading)
                                if line_id.quantity:
                                    sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                    qty += line_id.quantity
                                if line_id.rate:
                                    sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                    rate = line_id.rate
                                if line_id.amount:
                                    sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                    amount += line_id.amount
                                if line_id.total:
                                    sheet.write_number(row, col + 27, line_id.total, main_heading)
                                    total += line_id.total
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_number(row, col + 24, qty, main_heading)
                    grand_qty += qty
                    sheet.write_number(row, col + 27, total, main_heading)
                    grand_total += total
                    row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 24, grand_qty, main_heading)
                sheet.write_number(row, col + 27, grand_total, main_heading)
                row += 1
        if docs.grouping_by == 'by_nationality':
            self.env.ref(
                'bsg_payslip_variable_report.payslip_variable_report_xlsx_id').report_file = "Monthly variables On Payslips Grouping by Nationalty Report "
            sheet.merge_range('A1:AE1', 'تقرير المتغيرات الشهرية في مسير الرواتب بحسب الجنسيات', main_heading3)
            sheet.merge_range('A2:AE2', 'Monthly variables On Payslips Grouping by Nationalty Report ', main_heading3)
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'Employee Status', main_heading2)
            sheet.write(row, col + 4, 'ID NO', main_heading2)
            sheet.write(row, col + 5, 'Work Mobile', main_heading2)
            sheet.write(row, col + 6, 'Start Date', main_heading2)
            sheet.write(row, col + 7, 'Date of Join', main_heading2)
            sheet.write(row, col + 8, 'Date From', main_heading2)
            sheet.write(row, col + 9, 'Date To', main_heading2)
            sheet.write(row, col + 10, 'Payslip Batches', main_heading2)
            sheet.write(row, col + 11, 'Reference', main_heading2)
            sheet.write(row, col + 12, 'Payslip Name', main_heading2)
            sheet.write(row, col + 13, 'Branch', main_heading2)
            sheet.write(row, col + 14, 'Department', main_heading2)
            sheet.write(row, col + 15, 'Job Position', main_heading2)
            sheet.write(row, col + 16, 'Status', main_heading2)
            sheet.write(row, col + 17, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 18, 'Salary Structure', main_heading2)
            sheet.write(row, col + 19, 'Sequence', main_heading2)
            sheet.write(row, col + 20, 'Rule Name', main_heading2)
            sheet.write(row, col + 21, 'Rule Code', main_heading2)
            sheet.write(row, col + 22, 'Rule Category Name', main_heading2)
            sheet.write(row, col + 23, 'Description', main_heading2)
            sheet.write(row, col + 24, 'Quantity', main_heading2)
            sheet.write(row, col + 25, 'Rate (%)', main_heading2)
            sheet.write(row, col + 26, 'Amount', main_heading2)
            sheet.write(row, col + 27, 'Total', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'رقم بطاقة الهوية', main_heading2)
            sheet.write(row, col + 5, 'رقم جوال الموظف', main_heading2)
            sheet.write(row, col + 6, 'تاريخ الالتحاق', main_heading2)
            sheet.write(row, col + 7, 'تاريخ الالتحاق ', main_heading2)
            sheet.write(row, col + 8, 'من تاريخ', main_heading2)
            sheet.write(row, col + 9, 'الي تاريخ', main_heading2)
            sheet.write(row, col + 10, 'اسم دفعة مسير الرواتب', main_heading2)
            sheet.write(row, col + 11, 'مرجع مسير الرواتب', main_heading2)
            sheet.write(row, col + 12, 'وصف مسير الرواتب', main_heading2)
            sheet.write(row, col + 13, 'الفرع ', main_heading2)
            sheet.write(row, col + 14, 'الإدارة', main_heading2)
            sheet.write(row, col + 15, 'المنصب الوظيفي', main_heading2)
            sheet.write(row, col + 16, 'حالة المسير', main_heading2)
            sheet.write(row, col + 17, 'طريقة الدفع', main_heading2)
            sheet.write(row, col + 18, 'هيكل الرواتب', main_heading2)
            sheet.write(row, col + 19, 'رقم التسلسل', main_heading2)
            sheet.write(row, col + 20, 'اسم العنصر', main_heading2)
            sheet.write(row, col + 21, 'كود العنصر', main_heading2)
            sheet.write(row, col + 22, 'اسم فئة العنصر', main_heading2)
            sheet.write(row, col + 23, 'الوصف', main_heading2)
            sheet.write(row, col + 24, 'الكمية', main_heading2)
            sheet.write(row, col + 25, 'النسبة', main_heading2)
            sheet.write(row, col + 26, 'القيمة', main_heading2)
            sheet.write(row, col + 27, 'الإجمالي', main_heading2)
            row += 1
            payslip_ids_group_by_country = payslip_ids.read_group([], fields=['country_id'],groupby=['country_id'], lazy=False)
            print('........nationality.......',payslip_ids_group_by_country)
            if payslip_ids_group_by_country:
                grand_qty = 0
                grand_rate = 0
                grand_amount = 0
                grand_total = 0
                for payslip_id_group_by_country in payslip_ids_group_by_country:
                    if payslip_id_group_by_country:
                        payslip_ids_filtered_by_country = payslip_ids.filtered(lambda r: r.country_id and r.country_id.id == payslip_id_group_by_country.get('country_id')[0] if payslip_id_group_by_country.get('country_id') else r.country_id.id == payslip_id_group_by_country.get('country_id'))
                        if payslip_ids_filtered_by_country:
                            sheet.write(row, col, 'Nationality (Country)', main_heading2)
                            if payslip_id_group_by_country.get('country_id'):
                                sheet.write_string(row, col + 1,str(payslip_id_group_by_country.get('country_id')[1]),main_heading)
                            else:
                                sheet.write_string(row, col + 1, str('Undefined'), main_heading)

                            sheet.write(row, col + 2, 'الجنسية', main_heading2)
                            row += 1
                            qty = 0
                            rate = 0
                            amount = 0
                            total = 0
                            for payslip_id in payslip_ids_filtered_by_country:
                                line_ids = payslip_id.line_ids
                                if docs.rule_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                                if docs.rule_category_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                                for line_id in line_ids:
                                    if line_id.total != 0:
                                        if payslip_id.employee_id.driver_code:
                                            sheet.write_string(row, col, str(payslip_id.employee_id.driver_code),
                                                               main_heading)
                                        if payslip_id.employee_id.employee_code:
                                            sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                               main_heading)
                                        if payslip_id.employee_id.name:
                                            sheet.write_string(row, col + 2, str(payslip_id.employee_id.name),
                                                               main_heading)
                                        if payslip_id.employee_state:
                                            sheet.write_string(row, col + 3, str(payslip_id.employee_state),
                                                               main_heading)
                                        if payslip_id.employee_id.country_id:
                                            if payslip_id.employee_id.country_id.code == 'SA':
                                                if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                                    sheet.write_string(row, col + 4,
                                                                       str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                                       main_heading)
                                            else:
                                                if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                                    sheet.write_string(row, col + 4,
                                                                       str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                                       main_heading)
                                        if payslip_id.employee_id.mobile_phone:
                                            sheet.write_string(row, col + 5, str(payslip_id.employee_id.mobile_phone),
                                                               main_heading)
                                        if payslip_id.contract_id.date_start:
                                            sheet.write_string(row, col + 6, str(payslip_id.contract_id.date_start),
                                                               main_heading)
                                        if payslip_id.employee_id.bsgjoining_date:
                                            sheet.write_string(row, col + 7,
                                                               str(payslip_id.employee_id.bsgjoining_date),
                                                               main_heading)
                                        if payslip_id.date_from:
                                            sheet.write_string(row, col + 8, str(payslip_id.date_from), main_heading)
                                        if payslip_id.date_to:
                                            sheet.write_string(row, col + 9, str(payslip_id.date_to), main_heading)
                                        if payslip_id.payslip_run_id.name:
                                            sheet.write_string(row, col + 10, str(payslip_id.payslip_run_id.name),
                                                               main_heading)
                                        if payslip_id.number:
                                            sheet.write_string(row, col + 11, str(payslip_id.number), main_heading)
                                        if payslip_id.name:
                                            sheet.write_string(row, col + 12, str(payslip_id.name), main_heading)
                                        if payslip_id.branch_id.branch_name:
                                            sheet.write_string(row, col + 13, str(payslip_id.branch_id.branch_name),
                                                               main_heading)
                                        if payslip_id.department_id.display_name:
                                            sheet.write_string(row, col + 14,
                                                               str(payslip_id.department_id.display_name), main_heading)
                                        if payslip_id.job_id.name:
                                            sheet.write_string(row, col + 15, str(payslip_id.job_id.name), main_heading)
                                        if payslip_id.state:
                                            sheet.write_string(row, col + 16, str(payslip_id.state), main_heading)
                                        if payslip_id.salary_payment_method:
                                            sheet.write_string(row, col + 17, str(payslip_id.salary_payment_method),
                                                               main_heading)
                                        if payslip_id.struct_id.name:
                                            sheet.write_string(row, col + 18, str(payslip_id.struct_id.name),
                                                               main_heading)
                                        if line_id.sequence:
                                            sheet.write_string(row, col + 19, str(line_id.sequence), main_heading)
                                        if line_id.name:
                                            sheet.write_string(row, col + 20, str(line_id.name), main_heading)
                                        if line_id.code:
                                            sheet.write_string(row, col + 21, str(line_id.code), main_heading)
                                        if line_id.category_id.name:
                                            sheet.write_string(row, col + 22, str(line_id.category_id.name),
                                                               main_heading)
                                        if payslip_id.input_line_ids:
                                            input_line_ids = payslip_id.input_line_ids.filtered(
                                                lambda r: r.code == line_id.code)
                                            if input_line_ids:
                                                if input_line_ids.mapped('description')[0]:
                                                    sheet.write_string(row, col + 23,
                                                                       str(input_line_ids.mapped('description')[0]),
                                                                       main_heading)
                                        if line_id.quantity:
                                            sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                            qty += line_id.quantity
                                        if line_id.rate:
                                            sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                            rate = line_id.rate
                                        if line_id.amount:
                                            sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                            amount += line_id.amount
                                        if line_id.total:
                                            sheet.write_number(row, col + 27, line_id.total, main_heading)
                                            total += line_id.total
                                        row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_number(row, col + 24, qty, main_heading)
                            grand_qty += qty
                            sheet.write_number(row, col + 27, total, main_heading)
                            grand_total += total
                            row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 24, grand_qty, main_heading)
                sheet.write_number(row, col + 27, grand_total, main_heading)
                row += 1
        if docs.grouping_by == 'by_salary_payment_method':
            self.env.ref(
                'bsg_payslip_variable_report.payslip_variable_report_xlsx_id').report_file = "Monthly variables On Payslips Grouping by Salary Payment Method  Report "
            sheet.merge_range('A1:AE1', 'تقرير المتغيرات الشهرية في مسير الرواتب بحسب طريقة الدفع', main_heading3)
            sheet.merge_range('A2:AE2', 'Monthly variables On Payslips Grouping by Salary Payment Method  Report ', main_heading3)
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'Employee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality (Country)', main_heading2)
            sheet.write(row, col + 5, 'ID NO', main_heading2)
            sheet.write(row, col + 6, 'Work Mobile', main_heading2)
            sheet.write(row, col + 7, 'Start Date', main_heading2)
            sheet.write(row, col + 8, 'Date of Join', main_heading2)
            sheet.write(row, col + 9, 'Date From', main_heading2)
            sheet.write(row, col + 10, 'Date To', main_heading2)
            sheet.write(row, col + 11, 'Payslip Batches', main_heading2)
            sheet.write(row, col + 12, 'Reference', main_heading2)
            sheet.write(row, col + 13, 'Payslip Name', main_heading2)
            sheet.write(row, col + 14, 'Branch', main_heading2)
            sheet.write(row, col + 15, 'Department', main_heading2)
            sheet.write(row, col + 16, 'Job Position', main_heading2)
            sheet.write(row, col + 17, 'Status', main_heading2)
            sheet.write(row, col + 18, 'Salary Structure', main_heading2)
            sheet.write(row, col + 19, 'Sequence', main_heading2)
            sheet.write(row, col + 20, 'Rule Name', main_heading2)
            sheet.write(row, col + 21, 'Rule Code', main_heading2)
            sheet.write(row, col + 22, 'Rule Category Name', main_heading2)
            sheet.write(row, col + 23, 'Description', main_heading2)
            sheet.write(row, col + 24, 'Quantity', main_heading2)
            sheet.write(row, col + 25, 'Rate (%)', main_heading2)
            sheet.write(row, col + 26, 'Amount', main_heading2)
            sheet.write(row, col + 27, 'Total', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, 'رقم بطاقة الهوية', main_heading2)
            sheet.write(row, col + 6, 'رقم جوال الموظف', main_heading2)
            sheet.write(row, col + 7, 'تاريخ الالتحاق', main_heading2)
            sheet.write(row, col + 8, 'تاريخ الالتحاق ', main_heading2)
            sheet.write(row, col + 9, 'من تاريخ', main_heading2)
            sheet.write(row, col + 10, 'الي تاريخ', main_heading2)
            sheet.write(row, col + 11, 'اسم دفعة مسير الرواتب', main_heading2)
            sheet.write(row, col + 12, 'مرجع مسير الرواتب', main_heading2)
            sheet.write(row, col + 13, 'وصف مسير الرواتب', main_heading2)
            sheet.write(row, col + 14, 'الفرع ', main_heading2)
            sheet.write(row, col + 15, 'الإدارة', main_heading2)
            sheet.write(row, col + 16, 'المنصب الوظيفي', main_heading2)
            sheet.write(row, col + 17, 'حالة المسير', main_heading2)
            sheet.write(row, col + 18, 'هيكل الرواتب', main_heading2)
            sheet.write(row, col + 19, 'رقم التسلسل', main_heading2)
            sheet.write(row, col + 20, 'اسم العنصر', main_heading2)
            sheet.write(row, col + 21, 'كود العنصر', main_heading2)
            sheet.write(row, col + 22, 'اسم فئة العنصر', main_heading2)
            sheet.write(row, col + 23, 'الوصف', main_heading2)
            sheet.write(row, col + 24, 'الكمية', main_heading2)
            sheet.write(row, col + 25, 'النسبة', main_heading2)
            sheet.write(row, col + 26, 'القيمة', main_heading2)
            sheet.write(row, col + 27, 'الإجمالي', main_heading2)
            row += 1
            payslip_ids_group_by_payment_method = payslip_ids.read_group([], fields=['salary_payment_method'],groupby=['salary_payment_method'], lazy=False)
            print('.......salary payment method group by............',payslip_ids_group_by_payment_method)
            if payslip_ids_group_by_payment_method:
                grand_qty = 0
                grand_rate = 0
                grand_amount = 0
                grand_total = 0
                for payslip_id_group_by_payment_method in payslip_ids_group_by_payment_method:
                    if payslip_id_group_by_payment_method:
                        payslip_ids_filtered_by_payment_method = payslip_ids.filtered(lambda r: r.salary_payment_method and r.salary_payment_method == payslip_id_group_by_payment_method.get('salary_payment_method') if payslip_id_group_by_payment_method.get('salary_payment_method') else r.salary_payment_method == payslip_id_group_by_payment_method.get('salary_payment_method'))
                        if payslip_ids_filtered_by_payment_method:
                            sheet.write(row, col, 'Salary Payment Method', main_heading2)
                            if payslip_id_group_by_payment_method.get('salary_payment_method'):
                                sheet.write_string(row, col + 1,str(payslip_id_group_by_payment_method.get('salary_payment_method')),main_heading)
                            else:
                                sheet.write_string(row, col + 1, str('Undefined'), main_heading)

                            sheet.write(row, col + 2, 'طريقة الدفع', main_heading2)
                            row += 1
                            qty = 0
                            rate = 0
                            amount = 0
                            total = 0
                            for payslip_id in payslip_ids_filtered_by_payment_method:
                                line_ids = payslip_id.line_ids
                                if docs.rule_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                                if docs.rule_category_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                                for line_id in line_ids:
                                    if line_id.total != 0:
                                        if payslip_id.employee_id.driver_code:
                                            sheet.write_string(row, col, str(payslip_id.employee_id.driver_code),
                                                               main_heading)
                                        if payslip_id.employee_id.employee_code:
                                            sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                               main_heading)
                                        if payslip_id.employee_id.name:
                                            sheet.write_string(row, col + 2, str(payslip_id.employee_id.name),
                                                               main_heading)
                                        if payslip_id.employee_state:
                                            sheet.write_string(row, col + 3, str(payslip_id.employee_state),
                                                               main_heading)
                                        if payslip_id.employee_id.country_id.name:
                                            sheet.write_string(row, col + 4,
                                                               str(payslip_id.employee_id.country_id.name),
                                                               main_heading)
                                        if payslip_id.employee_id.country_id:
                                            if payslip_id.employee_id.country_id.code == 'SA':
                                                if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                                    sheet.write_string(row, col + 5,
                                                                       str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                                       main_heading)
                                            else:
                                                if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                                    sheet.write_string(row, col + 5,
                                                                       str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                                       main_heading)
                                        if payslip_id.employee_id.mobile_phone:
                                            sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                               main_heading)
                                        if payslip_id.contract_id.date_start:
                                            sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                               main_heading)
                                        if payslip_id.employee_id.bsgjoining_date:
                                            sheet.write_string(row, col + 8,
                                                               str(payslip_id.employee_id.bsgjoining_date),
                                                               main_heading)
                                        if payslip_id.date_from:
                                            sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                        if payslip_id.date_to:
                                            sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                        if payslip_id.payslip_run_id.name:
                                            sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name),
                                                               main_heading)
                                        if payslip_id.number:
                                            sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                        if payslip_id.name:
                                            sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                        if payslip_id.branch_id.branch_name:
                                            sheet.write_string(row, col + 14, str(payslip_id.branch_id.branch_name),
                                                               main_heading)
                                        if payslip_id.department_id.display_name:
                                            sheet.write_string(row, col + 15,
                                                               str(payslip_id.department_id.display_name), main_heading)
                                        if payslip_id.job_id.name:
                                            sheet.write_string(row, col + 16, str(payslip_id.job_id.name), main_heading)
                                        if payslip_id.state:
                                            sheet.write_string(row, col + 17, str(payslip_id.state), main_heading)
                                        if payslip_id.struct_id.name:
                                            sheet.write_string(row, col + 18, str(payslip_id.struct_id.name),
                                                               main_heading)
                                        if line_id.sequence:
                                            sheet.write_string(row, col + 19, str(line_id.sequence), main_heading)
                                        if line_id.name:
                                            sheet.write_string(row, col + 20, str(line_id.name), main_heading)
                                        if line_id.code:
                                            sheet.write_string(row, col + 21, str(line_id.code), main_heading)
                                        if line_id.category_id.name:
                                            sheet.write_string(row, col + 22, str(line_id.category_id.name),
                                                               main_heading)
                                        if payslip_id.input_line_ids:
                                            input_line_ids = payslip_id.input_line_ids.filtered(
                                                lambda r: r.code == line_id.code)
                                            if input_line_ids:
                                                if input_line_ids.mapped('description')[0]:
                                                    sheet.write_string(row, col + 23,
                                                                       str(input_line_ids.mapped('description')[0]),
                                                                       main_heading)
                                        if line_id.quantity:
                                            sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                            qty += line_id.quantity
                                        if line_id.rate:
                                            sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                            rate = line_id.rate
                                        if line_id.amount:
                                            sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                            amount += line_id.amount
                                        if line_id.total:
                                            sheet.write_number(row, col + 27, line_id.total, main_heading)
                                            total += line_id.total
                                        row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_number(row, col + 24, qty, main_heading)
                            grand_qty += qty
                            sheet.write_number(row, col + 27, total, main_heading)
                            grand_total += total
                            row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 24, grand_qty, main_heading)
                sheet.write_number(row, col + 27, grand_total, main_heading)
                row += 1
        if docs.grouping_by == 'by_salary_structure':
            self.env.ref('bsg_payslip_variable_report.payslip_variable_report_xlsx_id').report_file = "Monthly variables On Payslips Grouping by Salary Structure  Report "
            sheet.merge_range('A1:AE1', 'تقرير المتغيرات الشهرية في مسير الرواتب بحسب هيكل المرتبات', main_heading3)
            sheet.merge_range('A2:AE2', 'Monthly variables On Payslips Grouping by Salary Structure  Report ', main_heading3)
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'Employee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality (Country)', main_heading2)
            sheet.write(row, col + 5, 'ID NO', main_heading2)
            sheet.write(row, col + 6, 'Work Mobile', main_heading2)
            sheet.write(row, col + 7, 'Start Date', main_heading2)
            sheet.write(row, col + 8, 'Date of Join', main_heading2)
            sheet.write(row, col + 9, 'Date From', main_heading2)
            sheet.write(row, col + 10, 'Date To', main_heading2)
            sheet.write(row, col + 11, 'Payslip Batches', main_heading2)
            sheet.write(row, col + 12, 'Reference', main_heading2)
            sheet.write(row, col + 13, 'Payslip Name', main_heading2)
            sheet.write(row, col + 14, 'Branch', main_heading2)
            sheet.write(row, col + 15, 'Department', main_heading2)
            sheet.write(row, col + 16, 'Job Position', main_heading2)
            sheet.write(row, col + 17, 'Status', main_heading2)
            sheet.write(row, col + 18, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 19, 'Sequence', main_heading2)
            sheet.write(row, col + 20, 'Rule Name', main_heading2)
            sheet.write(row, col + 21, 'Rule Code', main_heading2)
            sheet.write(row, col + 22, 'Rule Category Name', main_heading2)
            sheet.write(row, col + 23, 'Description', main_heading2)
            sheet.write(row, col + 24, 'Quantity', main_heading2)
            sheet.write(row, col + 25, 'Rate (%)', main_heading2)
            sheet.write(row, col + 26, 'Amount', main_heading2)
            sheet.write(row, col + 27, 'Total', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, 'رقم بطاقة الهوية', main_heading2)
            sheet.write(row, col + 6, 'رقم جوال الموظف', main_heading2)
            sheet.write(row, col + 7, 'تاريخ الالتحاق', main_heading2)
            sheet.write(row, col + 8, 'تاريخ الالتحاق ', main_heading2)
            sheet.write(row, col + 9, 'من تاريخ', main_heading2)
            sheet.write(row, col + 10, 'الي تاريخ', main_heading2)
            sheet.write(row, col + 11, 'اسم دفعة مسير الرواتب', main_heading2)
            sheet.write(row, col + 12, 'مرجع مسير الرواتب', main_heading2)
            sheet.write(row, col + 13, 'وصف مسير الرواتب', main_heading2)
            sheet.write(row, col + 14, 'الفرع ', main_heading2)
            sheet.write(row, col + 15, 'الإدارة', main_heading2)
            sheet.write(row, col + 16, 'المنصب الوظيفي', main_heading2)
            sheet.write(row, col + 17, 'حالة المسير', main_heading2)
            sheet.write(row, col + 18, 'طريقة الدفع', main_heading2)
            sheet.write(row, col + 19, 'رقم التسلسل', main_heading2)
            sheet.write(row, col + 20, 'اسم العنصر', main_heading2)
            sheet.write(row, col + 21, 'كود العنصر', main_heading2)
            sheet.write(row, col + 22, 'اسم فئة العنصر', main_heading2)
            sheet.write(row, col + 23, 'الوصف', main_heading2)
            sheet.write(row, col + 24, 'الكمية', main_heading2)
            sheet.write(row, col + 25, 'النسبة', main_heading2)
            sheet.write(row, col + 26, 'القيمة', main_heading2)
            sheet.write(row, col + 27, 'الإجمالي', main_heading2)
            row += 1
            payslip_ids_group_by_struct = payslip_ids.read_group([], fields=['struct_id'],groupby=['struct_id'], lazy=False)
            if payslip_ids_group_by_struct:
                grand_qty = 0
                grand_rate = 0
                grand_amount = 0
                grand_total = 0
                for payslip_id_group_by_struct in payslip_ids_group_by_struct:
                    if payslip_id_group_by_struct:
                        payslip_ids_filtered_by_struct = payslip_ids.filtered(lambda r: r.struct_id and r.struct_id.id == payslip_id_group_by_struct.get('struct_id')[0] if payslip_id_group_by_struct.get('struct_id') else r.struct_id.id == payslip_id_group_by_struct.get('struct_id'))
                        if payslip_ids_filtered_by_struct:
                            sheet.write(row, col, 'Salary Structure', main_heading2)
                            if payslip_id_group_by_struct.get('struct_id'):
                                sheet.write_string(row, col + 1,str(payslip_id_group_by_struct.get('struct_id')[1]),main_heading)
                            else:
                                sheet.write_string(row, col + 1, str('Undefined'), main_heading)

                            sheet.write(row, col + 2, 'هيكل الرواتب', main_heading2)
                            row += 1
                            qty = 0
                            rate = 0
                            amount = 0
                            total = 0
                            for payslip_id in payslip_ids_filtered_by_struct:
                                line_ids = payslip_id.line_ids
                                if docs.rule_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                                if docs.rule_category_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                                for line_id in line_ids:
                                    if line_id.total != 0:
                                        if payslip_id.employee_id.driver_code:
                                            sheet.write_string(row, col, str(payslip_id.employee_id.driver_code),
                                                               main_heading)
                                        if payslip_id.employee_id.employee_code:
                                            sheet.write_string(row, col + 1, str(payslip_id.employee_id.employee_code),
                                                               main_heading)
                                        if payslip_id.employee_id.name:
                                            sheet.write_string(row, col + 2, str(payslip_id.employee_id.name),
                                                               main_heading)
                                        if payslip_id.employee_state:
                                            sheet.write_string(row, col + 3, str(payslip_id.employee_state),
                                                               main_heading)
                                        if payslip_id.employee_id.country_id.name:
                                            sheet.write_string(row, col + 4,
                                                               str(payslip_id.employee_id.country_id.name),
                                                               main_heading)
                                        if payslip_id.employee_id.country_id:
                                            if payslip_id.employee_id.country_id.code == 'SA':
                                                if payslip_id.employee_id.bsg_national_id.bsg_nationality_name:
                                                    sheet.write_string(row, col + 5,
                                                                       str(payslip_id.employee_id.bsg_national_id.bsg_nationality_name),
                                                                       main_heading)
                                            else:
                                                if payslip_id.employee_id.bsg_empiqama.bsg_iqama_name:
                                                    sheet.write_string(row, col + 5,
                                                                       str(payslip_id.employee_id.bsg_empiqama.bsg_iqama_name),
                                                                       main_heading)
                                        if payslip_id.employee_id.mobile_phone:
                                            sheet.write_string(row, col + 6, str(payslip_id.employee_id.mobile_phone),
                                                               main_heading)
                                        if payslip_id.contract_id.date_start:
                                            sheet.write_string(row, col + 7, str(payslip_id.contract_id.date_start),
                                                               main_heading)
                                        if payslip_id.employee_id.bsgjoining_date:
                                            sheet.write_string(row, col + 8,
                                                               str(payslip_id.employee_id.bsgjoining_date),
                                                               main_heading)
                                        if payslip_id.date_from:
                                            sheet.write_string(row, col + 9, str(payslip_id.date_from), main_heading)
                                        if payslip_id.date_to:
                                            sheet.write_string(row, col + 10, str(payslip_id.date_to), main_heading)
                                        if payslip_id.payslip_run_id.name:
                                            sheet.write_string(row, col + 11, str(payslip_id.payslip_run_id.name),
                                                               main_heading)
                                        if payslip_id.number:
                                            sheet.write_string(row, col + 12, str(payslip_id.number), main_heading)
                                        if payslip_id.name:
                                            sheet.write_string(row, col + 13, str(payslip_id.name), main_heading)
                                        if payslip_id.branch_id.branch_name:
                                            sheet.write_string(row, col + 14, str(payslip_id.branch_id.branch_name),
                                                               main_heading)
                                        if payslip_id.department_id.display_name:
                                            sheet.write_string(row, col + 15,
                                                               str(payslip_id.department_id.display_name), main_heading)
                                        if payslip_id.job_id.name:
                                            sheet.write_string(row, col + 16, str(payslip_id.job_id.name), main_heading)
                                        if payslip_id.state:
                                            sheet.write_string(row, col + 17, str(payslip_id.state), main_heading)
                                        if payslip_id.salary_payment_method:
                                            sheet.write_string(row, col + 18, str(payslip_id.salary_payment_method),
                                                               main_heading)
                                        if line_id.sequence:
                                            sheet.write_string(row, col + 19, str(line_id.sequence), main_heading)
                                        if line_id.name:
                                            sheet.write_string(row, col + 20, str(line_id.name), main_heading)
                                        if line_id.code:
                                            sheet.write_string(row, col + 21, str(line_id.code), main_heading)
                                        if line_id.category_id.name:
                                            sheet.write_string(row, col + 22, str(line_id.category_id.name),
                                                               main_heading)
                                        if payslip_id.input_line_ids:
                                            input_line_ids = payslip_id.input_line_ids.filtered(
                                                lambda r: r.code == line_id.code)
                                            if input_line_ids:
                                                if input_line_ids.mapped('description')[0]:
                                                    sheet.write_string(row, col + 23,
                                                                       str(input_line_ids.mapped('description')[0]),
                                                                       main_heading)
                                        if line_id.quantity:
                                            sheet.write_number(row, col + 24, line_id.quantity, main_heading)
                                            qty += line_id.quantity
                                        if line_id.rate:
                                            sheet.write_number(row, col + 25, line_id.rate, main_heading)
                                            rate = line_id.rate
                                        if line_id.amount:
                                            sheet.write_number(row, col + 26, line_id.amount, main_heading)
                                            amount += line_id.amount
                                        if line_id.total:
                                            sheet.write_number(row, col + 27, line_id.total, main_heading)
                                            total += line_id.total
                                        row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_number(row, col + 24, qty, main_heading)
                            grand_qty += qty
                            sheet.write_number(row, col + 27, total, main_heading)
                            grand_total += total
                            row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 24, grand_qty, main_heading)
                sheet.write_number(row, col + 27, grand_total, main_heading)
                row += 1
        if docs.grouping_by == 'by_employee':
            self.env.ref('bsg_payslip_variable_report.payslip_variable_report_xlsx_id').report_file = "Monthly variables On Payslips Grouping by Employee  Report"
            sheet.merge_range('A1:AE1', 'تقرير المتغيرات الشهرية في مسير الرواتب بحسب الموظف', main_heading3)
            sheet.merge_range('A2:AE2', 'Monthly variables On Payslips Grouping by Employee  Report ', main_heading3)
            sheet.write(row, col, 'Payslip Name', main_heading2)
            sheet.write(row, col + 1, 'Payslip Batches', main_heading2)
            sheet.write(row, col + 2, 'Date From', main_heading2)
            sheet.write(row, col + 3, 'Date To', main_heading2)
            sheet.write(row, col + 4, 'Reference', main_heading2)
            sheet.write(row, col + 5, 'Branch', main_heading2)
            sheet.write(row, col + 6, 'Department', main_heading2)
            sheet.write(row, col + 7, 'Job Position', main_heading2)
            sheet.write(row, col + 8, 'Status', main_heading2)
            sheet.write(row, col + 9, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 10, 'Salary Structure', main_heading2)
            sheet.write(row, col + 11, 'Employee Status', main_heading2)
            sheet.write(row, col + 12, 'Sequence', main_heading2)
            sheet.write(row, col + 13, 'Rule Name', main_heading2)
            sheet.write(row, col + 14, 'Rule Code', main_heading2)
            sheet.write(row, col + 15, 'Rule Category Name', main_heading2)
            sheet.write(row, col + 16, 'Description', main_heading2)
            sheet.write(row, col + 17, 'Quantity', main_heading2)
            sheet.write(row, col + 18, 'Rate (%)', main_heading2)
            sheet.write(row, col + 19, 'Amount', main_heading2)
            sheet.write(row, col + 20, 'Total', main_heading2)
            row += 1

            sheet.write(row, col, 'وصف مسير الرواتب', main_heading2)
            sheet.write(row, col + 1, 'اسم دفعة مسير الرواتب', main_heading2)
            sheet.write(row, col + 2, 'من تاريخ', main_heading2)
            sheet.write(row, col + 3, 'الي تاريخ', main_heading2)
            sheet.write(row, col + 4, 'مرجع مسير الرواتب', main_heading2)
            sheet.write(row, col + 5, 'الفرع ', main_heading2)
            sheet.write(row, col + 6, 'الإدارة', main_heading2)
            sheet.write(row, col + 7, 'المنصب الوظيفي', main_heading2)
            sheet.write(row, col + 8, 'حالة المسير', main_heading2)
            sheet.write(row, col + 9, 'طريقة الدفع', main_heading2)
            sheet.write(row, col + 10, 'هيكل الرواتب', main_heading2)
            sheet.write(row, col + 11, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 12, 'رقم التسلسل', main_heading2)
            sheet.write(row, col + 13, 'اسم العنصر', main_heading2)
            sheet.write(row, col + 14, 'كود العنصر', main_heading2)
            sheet.write(row, col + 15, 'اسم فئة العنصر', main_heading2)
            sheet.write(row, col + 16, 'الوصف', main_heading2)
            sheet.write(row, col + 17, 'الكمية', main_heading2)
            sheet.write(row, col + 18, 'النسبة', main_heading2)
            sheet.write(row, col + 19, 'القيمة', main_heading2)
            sheet.write(row, col + 20, 'الإجمالي', main_heading2)
            row += 1
            payslip_ids_group_by_employee = payslip_ids.read_group([], fields=['employee_id'],groupby=['employee_id'], lazy=False)
            if payslip_ids_group_by_employee:
                grand_qty = 0
                grand_rate = 0
                grand_amount = 0
                grand_total = 0
                for payslip_id_group_by_employee in payslip_ids_group_by_employee:
                    if payslip_id_group_by_employee:
                        payslip_ids_filtered_by_employee = payslip_ids.filtered(lambda r: r.employee_id and r.employee_id.id == payslip_id_group_by_employee.get('employee_id')[0] if payslip_id_group_by_employee.get('employee_id') else r.employee_id.id == payslip_id_group_by_employee.get('employee_id'))
                        if payslip_ids_filtered_by_employee:
                            employee_id = self.env['hr.employee'].search([('id','=',payslip_id_group_by_employee.get('employee_id')[0])],limit=1)
                            contract_id = self.env['hr.contract'].search([('employee_id', '=', payslip_id_group_by_employee.get('employee_id')[0]), ('state', '=', 'open')],limit=1)
                            sheet.write(row, col, 'اسم الموظف/Employee Name', main_heading2)
                            if payslip_id_group_by_employee.get('employee_id'):
                                sheet.write_string(row, col + 1,str(payslip_id_group_by_employee.get('employee_id')[1]),main_heading)
                                sheet.write(row, col+3, 'كود الموظف/Employee ID', main_heading2)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col+4, str(employee_id.driver_code),
                                                       main_heading)
                                sheet.write(row, col + 5, 'الجنسية/Nationality', main_heading2)
                                if employee_id.country_id.name:
                                    sheet.write_string(row, col + 6, str(employee_id.country_id.name),
                                                       main_heading)
                                sheet.write(row, col + 7, 'الهوية الوطنية/National ID', main_heading2)
                                if employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col +8,
                                                       str(employee_id.bsg_national_id.bsg_nationality_name),
                                                       main_heading)
                                sheet.write(row, col + 9, 'رقم جوال الموظف/Work Mobile', main_heading2)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 10, str(employee_id.mobile_phone),
                                                       main_heading)
                                sheet.write(row, col + 11, 'تاريخ الالتحاق/Start Date', main_heading2)
                                if contract_id.date_start:
                                    sheet.write_string(row, col + 12, str(contract_id.date_start),
                                                       main_heading)
                            else:
                                sheet.write_string(row, col + 1, str('Undefined'), main_heading)

                            row += 1
                            qty = 0
                            rate = 0
                            amount = 0
                            total = 0
                            for payslip_id in payslip_ids_filtered_by_employee:
                                line_ids = payslip_id.line_ids
                                if docs.rule_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.salary_rule_id and r.salary_rule_id.id in docs.rule_ids.ids)
                                if docs.rule_category_ids:
                                    line_ids = line_ids.filtered(
                                        lambda r: r.category_id and r.category_id.id in docs.rule_category_ids.ids)
                                for line_id in line_ids:
                                    if line_id.total != 0:
                                        if payslip_id.name:
                                            sheet.write_string(row, col, str(payslip_id.name), main_heading)
                                        if payslip_id.payslip_run_id.name:
                                            sheet.write_string(row, col + 1, str(payslip_id.payslip_run_id.name),
                                                               main_heading)
                                        if payslip_id.date_from:
                                            sheet.write_string(row, col + 2, str(payslip_id.date_from), main_heading)
                                        if payslip_id.date_to:
                                            sheet.write_string(row, col + 3, str(payslip_id.date_to), main_heading)
                                        if payslip_id.number:
                                            sheet.write_string(row, col + 4, str(payslip_id.number), main_heading)
                                        if payslip_id.branch_id.branch_name:
                                            sheet.write_string(row, col + 5, str(payslip_id.branch_id.branch_name),
                                                               main_heading)
                                        if payslip_id.department_id.display_name:
                                            sheet.write_string(row, col + 6, str(payslip_id.department_id.display_name),
                                                               main_heading)
                                        if payslip_id.job_id.name:
                                            sheet.write_string(row, col + 7, str(payslip_id.job_id.name), main_heading)
                                        if payslip_id.state:
                                            sheet.write_string(row, col + 8, str(payslip_id.state), main_heading)
                                        if payslip_id.salary_payment_method:
                                            sheet.write_string(row, col + 9, str(payslip_id.salary_payment_method),
                                                               main_heading)
                                        if payslip_id.struct_id.name:
                                            sheet.write_string(row, col + 10, str(payslip_id.struct_id.name), main_heading)
                                        if payslip_id.employee_state:
                                            sheet.write_string(row, col + 11, str(payslip_id.employee_state), main_heading)
                                        if line_id.sequence:
                                            sheet.write_string(row, col + 12, str(line_id.sequence), main_heading)
                                        if line_id.name:
                                            sheet.write_string(row, col + 13, str(line_id.name), main_heading)
                                        if line_id.code:
                                            sheet.write_string(row, col + 14, str(line_id.code), main_heading)
                                        if line_id.category_id.name:
                                            sheet.write_string(row, col + 15, str(line_id.category_id.name), main_heading)
                                        if payslip_id.input_line_ids:
                                            input_line_ids = payslip_id.input_line_ids.filtered(
                                                lambda r: r.code == line_id.code)
                                            if input_line_ids:
                                                if input_line_ids.mapped('description')[0]:
                                                    sheet.write_string(row, col + 16,str(input_line_ids.mapped('description')[0]),main_heading)
                                        if line_id.quantity:
                                            sheet.write_number(row, col + 17, line_id.quantity, main_heading)
                                            qty += line_id.quantity
                                        if line_id.rate:
                                            sheet.write_number(row, col + 18, line_id.rate, main_heading)
                                            rate = line_id.rate
                                        if line_id.amount:
                                            sheet.write_number(row, col + 19, line_id.amount, main_heading)
                                            amount += line_id.amount
                                        if line_id.total:
                                            sheet.write_number(row, col + 20, line_id.total, main_heading)
                                            total += line_id.total
                                        row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_number(row, col + 17, qty, main_heading)
                            grand_qty += qty
                            sheet.write_number(row, col + 20, total, main_heading)
                            grand_total += total
                            row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 17, grand_qty, main_heading)
                sheet.write_number(row, col + 20, grand_total, main_heading)
                row += 1