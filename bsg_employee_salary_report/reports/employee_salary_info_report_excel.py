from odoo import models
from datetime import date, datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import pandas as pd
from num2words import num2words


class EmployeeSalaryReportExcel(models.AbstractModel):
    _name = 'report.bsg_employee_salary_report.salary_report_xlsx'
    _inherit ='report.report_xlsx.abstract'


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
        sheet = workbook.add_worksheet('Employee Salary Information Report')
        sheet.set_column('A:AE', 15)
        domain=[]
        row = 2
        col = 0
        sheet.write(row, col + 2, 'Print Date', main_heading2)
        sheet.write_string(row, col + 3, str(docs.print_date_time.strftime('%Y-%m-%d %H:%M:%S')), main_heading)
        if docs.employee_ids:
            domain += [('id', 'in', docs.employee_ids.ids)]
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
        if docs.department_ids:
            domain += [('department_id', 'in', docs.department_ids.ids)]
            sheet.write(row, col, 'Departments', main_heading2)
            rec_names = docs.department_ids.mapped('display_name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.resource_calendar_ids:
            domain += [('resource_calendar_id', 'in', docs.resource_calendar_ids.ids)]
            sheet.write(row, col, 'Working Hours', main_heading2)
            rec_names = docs.resource_calendar_ids.mapped('name')
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
        if docs.country_ids:
            domain += [('country_id', 'in', docs.country_ids.ids)]
            sheet.write(row, col, 'Nationality', main_heading2)
            rec_names = docs.country_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.religion_ids:
            domain += [('bsg_religion_id', 'in', docs.religion_ids.ids)]
            sheet.write(row, col, 'Religion', main_heading2)
            rec_names = docs.religion_ids.mapped('religion_name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.region_ids:
            domain += [('branch_id.region', 'in', docs.region_ids.ids)]
            sheet.write(row, col, 'Region', main_heading2)
            rec_names = docs.region_ids.mapped('bsg_region_name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.guarantor_ids:
            domain += [('guarantor_id', 'in', docs.guarantor_ids.ids)]
            sheet.write(row, col, 'Guarantor', main_heading2)
            rec_names = docs.guarantor_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        # if docs.company_ids:
        #     domain += [('company_id', 'in', docs.company_ids.ids)]
        #     sheet.write(row, col, 'Company', main_heading2)
        #     rec_names = docs.company_ids.mapped('name')
        #     names = ','.join(rec_names)
        #     sheet.write_string(row, col + 1, str(names), main_heading)
        #     row += 1
        if docs.partner_type_ids:
            domain += [('partner_type_id', 'in', docs.partner_type_ids.ids)]
            sheet.write(row, col, 'Partner Type', main_heading2)
            rec_names = docs.partner_type_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.employee_tags_ids:
            domain += [('vehicle_status', 'in', docs.employee_tags_ids.ids)]
            sheet.write(row, col, 'Employee Tags', main_heading2)
            rec_names = docs.employee_tags_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
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
            domain += [('state_id', '=', docs.employee_state_id.id)]
        if docs.salary_payment_method == 'bank':
            domain += [('salary_payment_method', '=', 'bank')]
        if docs.salary_payment_method == 'cash':
            domain += [('is_driver', '=', 'cash')]
        if docs.is_driver == 'yes':
            domain += [('is_driver','=',True)]
        if docs.is_driver == 'no':
            domain += [('is_driver','=',False)]
        employee_ids = self.env['hr.employee'].search(domain)
        row+=1
        if docs.grouping_by == 'all':
            self.env.ref('bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report"
            sheet.merge_range('A1:AE1', 'تقرير معلومات راتب الموظف', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Department', main_heading2)
            sheet.write(row, col + 8, 'Work Location', main_heading2)
            sheet.write(row, col + 9, 'Jop Position', main_heading2)
            sheet.write(row, col + 10, 'Employ Status', main_heading2)
            sheet.write(row, col + 11, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 12, 'Is Driver?', main_heading2)
            sheet.write(row, col + 13, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 14, 'Company Name', main_heading2)
            sheet.write(row, col + 15, 'User Name', main_heading2)
            sheet.write(row, col + 16, 'Partner Name', main_heading2)
            sheet.write(row, col + 17, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 18, 'Mobile No.', main_heading2)
            sheet.write(row, col + 19, 'Nationality', main_heading2)
            sheet.write(row, col + 20, 'ID No.', main_heading2)
            sheet.write(row, col + 21, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 22, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 23, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 24, 'Bank Name', main_heading2)
            sheet.write(row, col + 25, 'Tags', main_heading2)
            sheet.write(row, col + 26, 'Date of Birth',main_heading2)
            sheet.write(row, col + 27, 'Date of Join', main_heading2)
            sheet.write(row, col + 28, 'End Service Date', main_heading2)
            sheet.write(row, col + 29, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 30, 'leave start date', main_heading2)
            sheet.write(row, col + 31, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 32, 'Gender', main_heading2)
            sheet.write(row, col + 33, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 35, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 36, 'Analytic Account', main_heading2)
            sheet.write(row, col + 37, 'Salary Structure', main_heading2)
            sheet.write(row, col + 38, 'Wage', main_heading2)
            sheet.write(row, col + 39, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'Transport', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'House Rent', main_heading2)
                sheet.write(row, col + 44, 'Food', main_heading2)
                sheet.write(row, col + 45, 'Work Nature', main_heading2)
                sheet.write(row, col + 46, 'Gross', main_heading2)
                sheet.write(row, col + 47, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 48, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 40, 'House Rent', main_heading2)
                sheet.write(row, col + 41, 'Food', main_heading2)
                sheet.write(row, col + 42, 'Work Nature', main_heading2)
                sheet.write(row, col + 43, 'Gross', main_heading2)
                sheet.write(row, col + 44, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 45, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'الادارة', main_heading2)
            sheet.write(row, col + 8, 'مكان العمل', main_heading2)
            sheet.write(row, col + 9, 'الوظيفه', main_heading2)
            sheet.write(row, col + 10, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 11, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 12, 'سائق ؟', main_heading2)
            sheet.write(row, col + 13, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 14, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 15, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 16, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 17, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 18, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 19, 'الجنسية', main_heading2)
            sheet.write(row, col + 20, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 21, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 22, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 23, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 24, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 25, 'الوسم', main_heading2)
            sheet.write(row, col + 26, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 27, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 28, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 29, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 31, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 32, 'الجنس', main_heading2)
            sheet.write(row, col + 33, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 34, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 35, 'حالة العقد', main_heading2)
            sheet.write(row, col + 36, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 37, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 38, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 39, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 41, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن', main_heading2)
                sheet.write(row, col + 43, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 44, 'بدل طعام', main_heading2)
                sheet.write(row, col + 45, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 46, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 47, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 48, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 40, 'بدل سكن', main_heading2)
                sheet.write(row, col + 41, 'بدل طعام', main_heading2)
                sheet.write(row, col + 42, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 43, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 44, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 45, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'صافي الراتب', main_heading2)
            row += 1
            for employee_id in employee_ids:
                if employee_id:
                    gross=0.0
                    transport = 0.0
                    transport_300 = 0.0
                    transport_1500 = 0.0
                    house = 0.0
                    house_500 = 0.0
                    food_allowance =0.0
                    work_nature_allowance = 0.0
                    fixed_add_allowance = 0.0
                    fixed_deduct_amount = 0.0
                    saudi_gosi_10 = 0.0
                    company_gosi_12 = 0.0
                    company_gosi_22 = 0.0
                    net = 0.0
                    gross_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'GROSS')
                    transport_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'CA')
                    transport300_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'CA22')
                    transport1500_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'CA23')
                    house_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'HRA2')
                    house_id_1 = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'HRA3')
                    house500_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'HA20')
                    saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'GOSI')
                    company_gosi_12_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'CGOSI')
                    company_gosi_22_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'FCGOSI')
                    net_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'NET')
                    food_allowance_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'FA')
                    work_nature_allowance_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'NWA')
                    fixed_add_allowance_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'FAA')
                    fixed_deduct_amount_id = employee_id.line_ids.filtered(lambda l:l.code and l.code == 'DEDFIXD')
                    if gross_id:
                        gross = gross_id.total
                    if transport_id:
                        transport = transport_id.total
                    if transport300_id:
                        transport_300 = transport300_id.total
                    if transport1500_id:
                        transport_1500 = transport1500_id.total
                    if house_id:
                        house = house_id.total
                    if house_id_1:
                        house = house_id_1.total
                    if house500_id:
                        house_500 = house500_id.total
                    if saudi_gosi_10_id:
                        saudi_gosi_10 = saudi_gosi_10_id.total
                    if company_gosi_12_id:
                        company_gosi_12 = company_gosi_12_id.total
                    if company_gosi_22_id:
                        company_gosi_22 = company_gosi_22_id.total
                    if net_id:
                        net = net_id.total
                    if food_allowance_id:
                        food_allowance = food_allowance_id.total
                    if work_nature_allowance_id:
                        work_nature_allowance = work_nature_allowance_id.total
                    if fixed_add_allowance_id:
                        fixed_add_allowance = fixed_add_allowance_id.total
                    if fixed_deduct_amount_id:
                        fixed_deduct_amount = fixed_deduct_amount_id.total
                    contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                    if employee_id.driver_code:
                        sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                    if employee_id.employee_code:
                        sheet.write_string(row, col + 1,str(employee_id.employee_code), main_heading)
                    if employee_id.name:
                        sheet.write_string(row, col + 2,str(employee_id.name), main_heading)
                    if employee_id.name_english:
                        sheet.write_string(row, col + 3,str(employee_id.name_english), main_heading)
                    if employee_id.parent_id.name:
                        sheet.write_string(row, col + 4,str(employee_id.parent_id.name), main_heading)
                    if employee_id.branch_id.region.bsg_region_name:
                        sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                           main_heading)
                    if employee_id.branch_id.branch_ar_name:
                        sheet.write_string(row, col + 6,str(employee_id.branch_id.branch_ar_name), main_heading)
                    if employee_id.department_id.display_name:
                        sheet.write_string(row, col + 7,str(employee_id.department_id.display_name), main_heading)
                    if employee_id.work_location:
                        sheet.write_string(row, col + 8,str(employee_id.work_location), main_heading)
                    if employee_id.job_id.name:
                        sheet.write_string(row, col + 9,str(employee_id.job_id.name), main_heading)
                    if employee_id.employee_state:
                        sheet.write_string(row, col + 10,str(employee_id.employee_state), main_heading)
                    if employee_id.suspend_salary:
                        sheet.write_string(row, col + 11,str('True'), main_heading)
                    if employee_id.is_driver:
                        sheet.write_string(row, col + 12,str('Driver'), main_heading)
                    if employee_id.guarantor_id.name:
                        sheet.write_string(row, col + 13,str(employee_id.guarantor_id.name), main_heading)
                    if employee_id.company_id.name:
                        sheet.write_string(row, col + 14,str(employee_id.company_id.name), main_heading)
                    if employee_id.user_id.name:
                        sheet.write_string(row, col + 15,str(employee_id.user_id.name), main_heading)
                    if employee_id.partner_id.name:
                        sheet.write_string(row, col + 16,str(employee_id.partner_id.name), main_heading)
                    if employee_id.last_return_date:
                        sheet.write_string(row, col + 17,str(employee_id.last_return_date), main_heading)
                    if employee_id.mobile_phone:
                        sheet.write_string(row, col + 18,str(employee_id.mobile_phone), main_heading)
                    if employee_id.country_id.name:
                        sheet.write_string(row, col + 19,str(employee_id.country_id.name), main_heading)
                    if employee_id.country_id:
                        if employee_id.country_id.code == 'SA':
                            if employee_id.bsg_national_id.bsg_nationality_name:
                                sheet.write_string(row, col + 20, str(employee_id.bsg_national_id.bsg_nationality_name),
                                                   main_heading)
                        else:
                            if employee_id.bsg_empiqama.bsg_iqama_name:
                                sheet.write_string(row, col + 20,
                                                   str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                   main_heading)
                    if employee_id.bsg_bank_id.bsg_acc_number:
                        sheet.write_string(row, col + 21,str(employee_id.bsg_bank_id.bsg_acc_number), main_heading)
                    if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                        sheet.write_string(row, col + 22,str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code), main_heading)
                    if employee_id.salary_payment_method:
                        sheet.write_string(row, col + 23,str(employee_id.salary_payment_method), main_heading)
                    if employee_id.bsg_bank_id.bsg_bank_name:
                        sheet.write_string(row, col + 24,str(employee_id.bsg_bank_id.bsg_bank_name), main_heading)
                    if employee_id.category_ids:
                        rec_names = employee_id.category_ids.mapped('name')
                        names = ','.join(rec_names)
                        sheet.write_string(row, col+25,str(names), main_heading)
                    if employee_id.birthday:
                        sheet.write_string(row, col + 26,str(employee_id.birthday), main_heading)
                    if employee_id.bsgjoining_date:
                        sheet.write_string(row, col + 27,str(employee_id.bsgjoining_date), main_heading)
                    if employee_id.end_service_date:
                        sheet.write_string(row, col + 28,str(employee_id.end_service_date), main_heading)
                    if employee_id.remaining_leaves:
                        sheet.write_string(row, col + 29,str(employee_id.remaining_leaves), main_heading)
                    if employee_id.leave_start_date:
                        sheet.write_string(row, col + 30,str(employee_id.leave_start_date), main_heading)
                    if employee_id.last_return_date:
                        sheet.write_string(row, col + 31,str(employee_id.last_return_date), main_heading)
                    if employee_id.gender:
                        sheet.write_string(row, col + 32,str(employee_id.gender), main_heading)
                    if contract_id.date_start:
                        sheet.write_string(row, col + 33,str(contract_id.date_start), main_heading)
                    if contract_id.date_end:
                        sheet.write_string(row, col + 34,str(contract_id.date_end), main_heading)
                    if contract_id.state:
                        if contract_id.state == 'draft':
                            sheet.write_string(row, col + 35, str("New"), main_heading)
                        if contract_id.state == 'open':
                            sheet.write_string(row, col + 35, str("Running"), main_heading)
                        if contract_id.state == 'pending':
                            sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                        if contract_id.state == 'close':
                            sheet.write_string(row, col + 35, str("Expired"), main_heading)
                        if contract_id.state == 'cancel':
                            sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                    if contract_id.analytic_account_id:
                        sheet.write_string(row, col + 36,str(contract_id.analytic_account_id.display_name), main_heading)
                    if employee_id.salary_structure.name:
                        sheet.write_string(row, col + 37,str(employee_id.salary_structure.name), main_heading)
                    if contract_id.wage:
                        sheet.write_number(row, col + 38,contract_id.wage, main_heading)
                    if transport:
                        sheet.write_number(row, col + 39,transport, main_heading)
                    if self.env.user.company_id.company_code == "BIC":
                        if transport_300:
                            sheet.write_number(row, col + 40, transport_300, main_heading)
                        if transport_1500:
                            sheet.write_number(row, col + 41, transport_1500, main_heading)
                        if house:
                            sheet.write_number(row, col + 42,house, main_heading)
                        if house_500:
                            sheet.write_number(row, col + 43,house_500, main_heading)
                        if food_allowance:
                            sheet.write_number(row, col + 44,food_allowance, main_heading)
                        if work_nature_allowance:
                            sheet.write_number(row, col + 45,work_nature_allowance, main_heading)
                        if gross:
                            sheet.write_number(row, col + 46,gross, main_heading)
                        if fixed_add_allowance:
                            sheet.write_number(row, col + 47,fixed_add_allowance, main_heading)
                        if fixed_deduct_amount:
                            sheet.write_number(row, col + 48,fixed_deduct_amount, main_heading)
                        if saudi_gosi_10:
                            sheet.write_number(row, col + 49,saudi_gosi_10, main_heading)
                        if company_gosi_22:
                            sheet.write_number(row, col + 50,company_gosi_22, main_heading)
                        if company_gosi_12:
                            sheet.write_number(row, col + 51,company_gosi_12, main_heading)
                        if net:
                            sheet.write_number(row, col + 52,net, main_heading)
                    else:
                        if house:
                            sheet.write_number(row, col + 40,house, main_heading)
                        if food_allowance:
                            sheet.write_number(row, col + 41,food_allowance, main_heading)
                        if work_nature_allowance:
                            sheet.write_number(row, col + 42,work_nature_allowance, main_heading)
                        if gross:
                            sheet.write_number(row, col + 43,gross, main_heading)
                        if fixed_add_allowance:
                            sheet.write_number(row, col + 44,fixed_add_allowance, main_heading)
                        if fixed_deduct_amount:
                            sheet.write_number(row, col + 45,fixed_deduct_amount, main_heading)
                        if saudi_gosi_10:
                            sheet.write_number(row, col + 46,saudi_gosi_10, main_heading)
                        if company_gosi_22:
                            sheet.write_number(row, col + 47,company_gosi_22, main_heading)
                        if company_gosi_12:
                            sheet.write_number(row, col + 48,company_gosi_12, main_heading)
                        if net:
                            sheet.write_number(row, col + 49,net, main_heading)
                    row += 1
        if docs.grouping_by == 'by_branches':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Branches"
            sheet.merge_range('A1:AE1', 'مجموعة تقرير معلومات رواتب الموظف حسب الفروع', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Branches', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Department', main_heading2)
            sheet.write(row, col + 7, 'Work Location', main_heading2)
            sheet.write(row, col + 8, 'Jop Position', main_heading2)
            sheet.write(row, col + 9, 'Employ Status', main_heading2)
            sheet.write(row, col + 10, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 11, 'Is Driver?', main_heading2)
            sheet.write(row, col + 12, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 13, 'Company Name', main_heading2)
            sheet.write(row, col + 14, 'User Name', main_heading2)
            sheet.write(row, col + 15, 'Partner Name', main_heading2)
            sheet.write(row, col + 16, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 17, 'Mobile No.', main_heading2)
            sheet.write(row, col + 18, 'Nationality', main_heading2)
            sheet.write(row, col + 19, 'ID No.', main_heading2)
            sheet.write(row, col + 20, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 21, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 22, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 23, 'Bank Name', main_heading2)
            sheet.write(row, col + 24, 'Tags', main_heading2)
            sheet.write(row, col + 25, 'Date of Birth', main_heading2)
            sheet.write(row, col + 26, 'Date of Join', main_heading2)
            sheet.write(row, col + 27, 'End Service Date', main_heading2)
            sheet.write(row, col + 28, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 29, 'leave start date', main_heading2)
            sheet.write(row, col + 30, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 31, 'Gender', main_heading2)
            sheet.write(row, col + 32, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 33, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 35, 'Analytic Account', main_heading2)
            sheet.write(row, col + 36, 'Salary Structure', main_heading2)
            sheet.write(row, col + 37, 'Wage', main_heading2)
            sheet.write(row, col + 38, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 39, 'Transport', main_heading2)
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'House Rent', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'Food', main_heading2)
                sheet.write(row, col + 44, 'Work Nature', main_heading2)
                sheet.write(row, col + 45, 'Gross', main_heading2)
                sheet.write(row, col + 46, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 47, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 48, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 49, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 51, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 39, 'House Rent', main_heading2)
                sheet.write(row, col + 40, 'Food', main_heading2)
                sheet.write(row, col + 41, 'Work Nature', main_heading2)
                sheet.write(row, col + 42, 'Gross', main_heading2)
                sheet.write(row, col + 43, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 44, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 45, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 46, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 48, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الادارة', main_heading2)
            sheet.write(row, col + 7, 'مكان العمل', main_heading2)
            sheet.write(row, col + 8, 'الوظيفه', main_heading2)
            sheet.write(row, col + 9, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 10, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 11, 'سائق ؟', main_heading2)
            sheet.write(row, col + 12, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 13, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 14, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 15, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 16, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 17, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 18, 'الجنسية', main_heading2)
            sheet.write(row, col + 19, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 20, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 21, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 22, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 23, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 24, 'الوسم', main_heading2)
            sheet.write(row, col + 25, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 26, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 27, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 28, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 29, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 31, 'الجنس', main_heading2)
            sheet.write(row, col + 32, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 33, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 34, 'حالة العقد', main_heading2)
            sheet.write(row, col + 35, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 36, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 37, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 38, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 39, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 40, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 41, 'بدل سكن', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 43, 'بدل طعام', main_heading2)
                sheet.write(row, col + 44, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 45, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 46, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 47, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 48, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 49, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 51, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 39, 'بدل سكن', main_heading2)
                sheet.write(row, col + 40, 'بدل طعام', main_heading2)
                sheet.write(row, col + 41, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 42, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 43, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 44, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 45, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 46, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 48, 'صافي الراتب', main_heading2)
            row += 1
            branch_list = []
            grand_total = 0
            branch_ids = self.env['bsg_branches.bsg_branches'].search([])
            for branch_id in branch_ids:
                if branch_id:
                    branch_list.append(branch_id.branch_ar_name)
            for branch_name in branch_list:
                if branch_name:
                    branch_employee_ids = employee_ids.filtered(lambda r:r.branch_id.branch_ar_name == branch_name)
                    if branch_employee_ids:
                        total = 0
                        wage_total = 0.0
                        transport_total = 0.0
                        transport_300_total = 0.0
                        transport_1500_total = 0.0
                        house_rent_total = 0.0
                        house_500_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        sheet.write(row, col, 'Branch', main_heading2)
                        sheet.write_string(row, col + 1, str(branch_name), main_heading)
                        sheet.write(row, col + 2, 'الفرع', main_heading2)
                        row += 1
                        for employee_id in branch_employee_ids:
                            if employee_id:
                                gross = 0.0
                                transport = 0.0
                                transport_300 = 0.0
                                transport_1500 = 0.0
                                house = 0.0
                                house_500 = 0.0
                                food_allowance = 0.0
                                work_nature_allowance = 0.0
                                fixed_add_allowance = 0.0
                                fixed_deduct_amount = 0.0
                                saudi_gosi_10 = 0.0
                                company_gosi_12 = 0.0
                                company_gosi_22 = 0.0
                                net = 0.0
                                gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                                transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                                transport300_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA22')
                                transport1500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA23')
                                house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                                house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                                house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                                saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GOSI')
                                company_gosi_12_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CGOSI')
                                company_gosi_22_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FCGOSI')
                                net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                                food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'FA')
                                work_nature_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'NWA')
                                fixed_add_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FAA')
                                fixed_deduct_amount_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'DEDFIXD')
                                if gross_id:
                                    gross = gross_id.total
                                if transport_id:
                                    transport = transport_id.total
                                if transport300_id:
                                    transport_300 = transport300_id.total
                                if transport1500_id:
                                    transport_1500 = transport1500_id.total
                                if house_id:
                                    house = house_id.total
                                if house_id_1:
                                    house = house_id_1.total
                                if house500_id:
                                    house_500 = house500_id.total
                                if saudi_gosi_10_id:
                                    saudi_gosi_10 = saudi_gosi_10_id.total
                                if company_gosi_12_id:
                                    company_gosi_12 = company_gosi_12_id.total
                                if company_gosi_22_id:
                                    company_gosi_22 = company_gosi_22_id.total
                                if net_id:
                                    net = net_id.total
                                if food_allowance_id:
                                    food_allowance = food_allowance_id.total
                                if work_nature_allowance_id:
                                    work_nature_allowance = work_nature_allowance_id.total
                                if fixed_add_allowance_id:
                                    fixed_add_allowance = fixed_add_allowance_id.total
                                if fixed_deduct_amount_id:
                                    fixed_deduct_amount = fixed_deduct_amount_id.total
                                contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                if employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                if employee_id.name:
                                    sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                if employee_id.name_english:
                                    sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                if employee_id.parent_id.name:
                                    sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                                if employee_id.branch_id.region.bsg_region_name:
                                    sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                                       main_heading)
                                if employee_id.department_id.display_name:
                                    sheet.write_string(row, col + 6, str(employee_id.department_id.display_name),
                                                       main_heading)
                                if employee_id.work_location:
                                    sheet.write_string(row, col + 7, str(employee_id.work_location), main_heading)
                                if employee_id.job_id.name:
                                    sheet.write_string(row, col + 8, str(employee_id.job_id.name), main_heading)
                                if employee_id.employee_state:
                                    sheet.write_string(row, col + 9, str(employee_id.employee_state), main_heading)
                                if employee_id.suspend_salary:
                                    sheet.write_string(row, col + 10, str('True'), main_heading)
                                if employee_id.is_driver:
                                    sheet.write_string(row, col + 11, str('Driver'), main_heading)
                                if employee_id.guarantor_id.name:
                                    sheet.write_string(row, col + 12, str(employee_id.guarantor_id.name), main_heading)
                                if employee_id.company_id.name:
                                    sheet.write_string(row, col + 13, str(employee_id.company_id.name), main_heading)
                                if employee_id.user_id.name:
                                    sheet.write_string(row, col + 14, str(employee_id.user_id.name), main_heading)
                                if employee_id.partner_id.name:
                                    sheet.write_string(row, col + 15, str(employee_id.partner_id.name), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 16, str(employee_id.last_return_date), main_heading)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 17, str(employee_id.mobile_phone), main_heading)
                                if employee_id.country_id.name:
                                    sheet.write_string(row, col + 18, str(employee_id.country_id.name), main_heading)
                                if employee_id.country_id:
                                    if employee_id.country_id.code == 'SA':
                                        if employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 19,
                                                               str(employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 19,
                                                               str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if employee_id.bsg_bank_id.bsg_acc_number:
                                    sheet.write_string(row, col + 20, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                    sheet.write_string(row, col + 21,
                                                       str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                       main_heading)
                                if employee_id.salary_payment_method:
                                    sheet.write_string(row, col + 22, str(employee_id.salary_payment_method),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_bank_name:
                                    sheet.write_string(row, col + 23, str(employee_id.bsg_bank_id.bsg_bank_name),
                                                       main_heading)
                                if employee_id.category_ids:
                                    rec_names = employee_id.category_ids.mapped('name')
                                    names = ','.join(rec_names)
                                    sheet.write_string(row, col + 24, str(names), main_heading)
                                if employee_id.birthday:
                                    sheet.write_string(row, col + 25, str(employee_id.birthday), main_heading)
                                if employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 26, str(employee_id.bsgjoining_date), main_heading)
                                if employee_id.end_service_date:
                                    sheet.write_string(row, col + 27, str(employee_id.end_service_date), main_heading)
                                if employee_id.remaining_leaves:
                                    sheet.write_string(row, col + 28, str(employee_id.remaining_leaves), main_heading)
                                if employee_id.leave_start_date:
                                    sheet.write_string(row, col + 29, str(employee_id.leave_start_date), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 30, str(employee_id.last_return_date), main_heading)
                                if employee_id.gender:
                                    sheet.write_string(row, col + 31, str(employee_id.gender), main_heading)
                                if contract_id.date_start:
                                    sheet.write_string(row, col + 32, str(contract_id.date_start), main_heading)
                                if contract_id.date_end:
                                    sheet.write_string(row, col + 33, str(contract_id.date_end), main_heading)
                                if contract_id.state:
                                    if contract_id.state == 'draft':
                                        sheet.write_string(row, col + 34, str("New"), main_heading)
                                    if contract_id.state == 'open':
                                        sheet.write_string(row, col + 34, str("Running"), main_heading)
                                    if contract_id.state == 'pending':
                                        sheet.write_string(row, col + 34, str("To Renew"), main_heading)
                                    if contract_id.state == 'close':
                                        sheet.write_string(row, col + 34, str("Expired"), main_heading)
                                    if contract_id.state == 'cancel':
                                        sheet.write_string(row, col + 34, str("Cancelled"), main_heading)
                                if contract_id.analytic_account_id:
                                    sheet.write_string(row, col + 35, str(contract_id.analytic_account_id.display_name),
                                                       main_heading)
                                if employee_id.salary_structure.name:
                                    sheet.write_string(row, col + 36, str(employee_id.salary_structure.name),
                                                       main_heading)
                                if contract_id.wage:
                                    sheet.write_number(row, col + 37, contract_id.wage, main_heading)
                                    print('wage=',contract_id.wage)
                                    wage_total  +=  contract_id.wage
                                    print('wage total=', wage_total)
                                if transport:
                                    sheet.write_number(row, col + 38, transport, main_heading)
                                    transport_total += transport
                                if self.env.user.company_id.company_code == "BIC":
                                    if transport_300:
                                        sheet.write_number(row, col + 39, transport_300, main_heading)
                                        transport_300_total += transport_300
                                    if transport_1500:
                                        sheet.write_number(row, col + 40, transport_1500, main_heading)
                                        transport_1500_total += transport_1500
                                    if house:
                                        sheet.write_number(row, col + 41, house, main_heading)
                                        house_rent_total += house
                                    if house_500:
                                        sheet.write_number(row, col + 42, house_500, main_heading)
                                        house_500_total += house_500
                                    if food_allowance:
                                        sheet.write_number(row, col + 43, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 44, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 45, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 46, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 47, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 48, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 49, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 50, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 51, net, main_heading)
                                        net_total += net
                                else:
                                    if house:
                                        sheet.write_number(row, col + 39, house, main_heading)
                                        house_rent_total += house
                                    if food_allowance:
                                        sheet.write_number(row, col + 40, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 41, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 42, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 43, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 44, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 45, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 46, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 47, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 48, net, main_heading)
                                        net_total += net
                                row += 1
                                total+=1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_number(row, col + 1, total, main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        sheet.write_number(row, col + 37, wage_total, main_heading)
                        sheet.write_number(row, col + 38, transport_total, main_heading)
                        if self.env.user.company_id.company_code == "BIC":
                            sheet.write_number(row, col + 39, transport_300_total, main_heading)
                            sheet.write_number(row, col + 40, transport_1500_total, main_heading)
                            sheet.write_number(row, col + 41, house_rent_total, main_heading)
                            sheet.write_number(row, col + 42, house_500_total, main_heading)
                            sheet.write_number(row, col + 43, food_total, main_heading)
                            sheet.write_number(row, col + 44, work_nature_total, main_heading)
                            sheet.write_number(row, col + 45, gross_total, main_heading)
                            sheet.write_number(row, col + 46, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 47, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 48, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 49, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 50, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 51, net_total, main_heading)
                        else:
                            sheet.write_number(row, col + 39, house_rent_total, main_heading)
                            sheet.write_number(row, col + 40, food_total, main_heading)
                            sheet.write_number(row, col + 41, work_nature_total, main_heading)
                            sheet.write_number(row, col + 42, gross_total, main_heading)
                            sheet.write_number(row, col + 43, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 44, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 45, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 46, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 47, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 48, net_total, main_heading)
                        row += 1
                        grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 1, grand_total, main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_departments':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Departments"
            sheet.merge_range('A1:AE1', 'مجموعة تقرير معلومات راتب الموظف حسب الأقسام', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Departments', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Work Location', main_heading2)
            sheet.write(row, col + 8, 'Jop Position', main_heading2)
            sheet.write(row, col + 9, 'Employ Status', main_heading2)
            sheet.write(row, col + 10, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 11, 'Is Driver?', main_heading2)
            sheet.write(row, col + 12, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 13, 'Company Name', main_heading2)
            sheet.write(row, col + 14, 'User Name', main_heading2)
            sheet.write(row, col + 15, 'Partner Name', main_heading2)
            sheet.write(row, col + 16, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 17, 'Mobile No.', main_heading2)
            sheet.write(row, col + 18, 'Nationality', main_heading2)
            sheet.write(row, col + 19, 'ID No.', main_heading2)
            sheet.write(row, col + 20, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 21, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 22, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 23, 'Bank Name', main_heading2)
            sheet.write(row, col + 24, 'Tags', main_heading2)
            sheet.write(row, col + 25, 'Date of Birth', main_heading2)
            sheet.write(row, col + 26, 'Date of Join', main_heading2)
            sheet.write(row, col + 27, 'End Service Date', main_heading2)
            sheet.write(row, col + 28, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 29, 'leave start date', main_heading2)
            sheet.write(row, col + 30, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 31, 'Gender', main_heading2)
            sheet.write(row, col + 32, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 33, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 35, 'Analytic Account', main_heading2)
            sheet.write(row, col + 36, 'Salary Structure', main_heading2)
            sheet.write(row, col + 37, 'Wage', main_heading2)
            sheet.write(row, col + 38, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 39, 'Transport', main_heading2)
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'House Rent', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'Food', main_heading2)
                sheet.write(row, col + 44, 'Work Nature', main_heading2)
                sheet.write(row, col + 45, 'Gross', main_heading2)
                sheet.write(row, col + 46, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 47, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 48, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 49, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 51, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 39, 'House Rent', main_heading2)
                sheet.write(row, col + 40, 'Food', main_heading2)
                sheet.write(row, col + 41, 'Work Nature', main_heading2)
                sheet.write(row, col + 42, 'Gross', main_heading2)
                sheet.write(row, col + 43, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 44, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 45, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 46, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 48, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'مكان العمل', main_heading2)
            sheet.write(row, col + 8, 'الوظيفه', main_heading2)
            sheet.write(row, col + 9, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 10, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 11, 'سائق ؟', main_heading2)
            sheet.write(row, col + 12, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 13, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 14, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 15, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 16, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 17, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 18, 'الجنسية', main_heading2)
            sheet.write(row, col + 19, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 20, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 21, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 22, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 23, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 24, 'الوسم', main_heading2)
            sheet.write(row, col + 25, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 26, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 27, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 28, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 29, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 31, 'الجنس', main_heading2)
            sheet.write(row, col + 32, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 33, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 34, 'حالة العقد', main_heading2)
            sheet.write(row, col + 35, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 36, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 37, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 38, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 39, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 40, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 41, 'بدل سكن', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 43, 'بدل طعام', main_heading2)
                sheet.write(row, col + 44, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 45, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 46, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 47, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 48, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 49, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 51, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 39, 'بدل سكن', main_heading2)
                sheet.write(row, col + 40, 'بدل طعام', main_heading2)
                sheet.write(row, col + 41, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 42, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 43, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 44, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 45, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 46, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 48, 'صافي الراتب', main_heading2)
            row += 1
            department_list = []
            main_depart_list = []
            grand_total = 0
            department_ids = self.env['hr.department'].search([])
            if docs.is_parent_dempart:
                for department_id in department_ids:
                    if department_id:
                        if department_id.display_name.split('/')[0].strip() not in main_depart_list:
                            main_depart_list.append(department_id.display_name.split('/')[0].strip())
                for department_name in main_depart_list:
                    if department_name:
                        main_department_employee_ids = employee_ids.filtered(lambda r:r.department_id and r.department_id.display_name.split('/')[0].strip() == department_name)
                        if main_department_employee_ids:
                            total = 0
                            wage_total = 0.0
                            transport_total = 0.0
                            transport_300_total = 0.0
                            transport_1500_total = 0.0
                            house_rent_total = 0.0
                            house_500_total = 0.0
                            food_total = 0.0
                            work_nature_total = 0.0
                            gross_total = 0.0
                            fixed_additional_total = 0.0
                            fixed_deduction_total = 0.0
                            saudi_gosi_total = 0.0
                            company_gosi_12_total = 0.0
                            company_gosi_22_total = 0.0
                            net_total = 0.0
                            sheet.write(row, col, 'Department', main_heading2)
                            sheet.write_string(row, col + 1, str(department_name), main_heading)
                            sheet.write(row, col + 2, 'الادارة', main_heading2)
                            row += 1
                            for employee_id in main_department_employee_ids:
                                if employee_id:
                                    gross = 0.0
                                    transport = 0.0
                                    transport_300 = 0.0
                                    transport_1500 = 0.0
                                    house = 0.0
                                    house_500 = 0.0
                                    food_allowance = 0.0
                                    work_nature_allowance = 0.0
                                    fixed_add_allowance = 0.0
                                    fixed_deduct_amount = 0.0
                                    saudi_gosi_10 = 0.0
                                    company_gosi_12 = 0.0
                                    company_gosi_22 = 0.0
                                    net = 0.0
                                    gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                                    transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                                    transport300_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'CA22')
                                    transport1500_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'CA23')
                                    house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                                    house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                                    house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                                    saudi_gosi_10_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'GOSI')
                                    company_gosi_12_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'CGOSI')
                                    company_gosi_22_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'FCGOSI')
                                    net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                                    food_allowance_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'FA')
                                    work_nature_allowance_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'NWA')
                                    fixed_add_allowance_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'FAA')
                                    fixed_deduct_amount_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'DEDFIXD')
                                    if gross_id:
                                        gross = gross_id.total
                                    if transport_id:
                                        transport = transport_id.total
                                    if transport300_id:
                                        transport_300 = transport300_id.total
                                    if transport1500_id:
                                        transport_1500 = transport1500_id.total
                                    if house_id:
                                        house = house_id.total
                                    if house_id_1:
                                        house = house_id_1.total
                                    if house500_id:
                                        house_500 = house500_id.total
                                    if saudi_gosi_10_id:
                                        saudi_gosi_10 = saudi_gosi_10_id.total
                                    if company_gosi_12_id:
                                        company_gosi_12 = company_gosi_12_id.total
                                    if company_gosi_22_id:
                                        company_gosi_22 = company_gosi_22_id.total
                                    if net_id:
                                        net = net_id.total
                                    if food_allowance_id:
                                        food_allowance = food_allowance_id.total
                                    if work_nature_allowance_id:
                                        work_nature_allowance = work_nature_allowance_id.total
                                    if fixed_add_allowance_id:
                                        fixed_add_allowance = fixed_add_allowance_id.total
                                    if fixed_deduct_amount_id:
                                        fixed_deduct_amount = fixed_deduct_amount_id.total
                                    contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                                    if employee_id.driver_code:
                                        sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                    if employee_id.employee_code:
                                        sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                    if employee_id.name:
                                        sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                    if employee_id.name_english:
                                        sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                    if employee_id.parent_id.name:
                                        sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                                    if employee_id.branch_id.region.bsg_region_name:
                                        sheet.write_string(row, col + 5,
                                                           str(employee_id.branch_id.region.bsg_region_name),
                                                           main_heading)
                                    if employee_id.branch_id.branch_ar_name:
                                        sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                                           main_heading)
                                    if employee_id.work_location:
                                        sheet.write_string(row, col + 7, str(employee_id.work_location), main_heading)
                                    if employee_id.job_id.name:
                                        sheet.write_string(row, col + 8, str(employee_id.job_id.name), main_heading)
                                    if employee_id.employee_state:
                                        sheet.write_string(row, col + 9, str(employee_id.employee_state), main_heading)
                                    if employee_id.suspend_salary:
                                        sheet.write_string(row, col + 10, str('True'), main_heading)
                                    if employee_id.is_driver:
                                        sheet.write_string(row, col + 11, str('Driver'), main_heading)
                                    if employee_id.guarantor_id.name:
                                        sheet.write_string(row, col + 12, str(employee_id.guarantor_id.name),
                                                           main_heading)
                                    if employee_id.company_id.name:
                                        sheet.write_string(row, col + 13, str(employee_id.company_id.name),
                                                           main_heading)
                                    if employee_id.user_id.name:
                                        sheet.write_string(row, col + 14, str(employee_id.user_id.name), main_heading)
                                    if employee_id.partner_id.name:
                                        sheet.write_string(row, col + 15, str(employee_id.partner_id.name),
                                                           main_heading)
                                    if employee_id.last_return_date:
                                        sheet.write_string(row, col + 16, str(employee_id.last_return_date),
                                                           main_heading)
                                    if employee_id.mobile_phone:
                                        sheet.write_string(row, col + 17, str(employee_id.mobile_phone), main_heading)
                                    if employee_id.country_id.name:
                                        sheet.write_string(row, col + 18, str(employee_id.country_id.name),
                                                           main_heading)
                                    if employee_id.country_id:
                                        if employee_id.country_id.code == 'SA':
                                            if employee_id.bsg_national_id.bsg_nationality_name:
                                                sheet.write_string(row, col + 19,
                                                                   str(employee_id.bsg_national_id.bsg_nationality_name),
                                                                   main_heading)
                                        else:
                                            if employee_id.bsg_empiqama.bsg_iqama_name:
                                                sheet.write_string(row, col + 19,
                                                                   str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                                   main_heading)
                                    if employee_id.bsg_bank_id.bsg_acc_number:
                                        sheet.write_string(row, col + 20, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                           main_heading)
                                    if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                        sheet.write_string(row, col + 21,
                                                           str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                           main_heading)
                                    if employee_id.salary_payment_method:
                                        sheet.write_string(row, col + 22, str(employee_id.salary_payment_method),
                                                           main_heading)
                                    if employee_id.bsg_bank_id.bsg_bank_name:
                                        sheet.write_string(row, col + 23, str(employee_id.bsg_bank_id.bsg_bank_name),
                                                           main_heading)
                                    if employee_id.category_ids:
                                        rec_names = employee_id.category_ids.mapped('name')
                                        names = ','.join(rec_names)
                                        sheet.write_string(row, col + 24, str(names), main_heading)
                                    if employee_id.birthday:
                                        sheet.write_string(row, col + 25, str(employee_id.birthday), main_heading)
                                    if employee_id.bsgjoining_date:
                                        sheet.write_string(row, col + 26, str(employee_id.bsgjoining_date),
                                                           main_heading)
                                    if employee_id.end_service_date:
                                        sheet.write_string(row, col + 27, str(employee_id.end_service_date),
                                                           main_heading)
                                    if employee_id.remaining_leaves:
                                        sheet.write_string(row, col + 28, str(employee_id.remaining_leaves),
                                                           main_heading)
                                    if employee_id.leave_start_date:
                                        sheet.write_string(row, col + 29, str(employee_id.leave_start_date),
                                                           main_heading)
                                    if employee_id.last_return_date:
                                        sheet.write_string(row, col + 30, str(employee_id.last_return_date),
                                                           main_heading)
                                    if employee_id.gender:
                                        sheet.write_string(row, col + 31, str(employee_id.gender), main_heading)
                                    if contract_id.date_start:
                                        sheet.write_string(row, col + 32, str(contract_id.date_start), main_heading)
                                    if contract_id.date_end:
                                        sheet.write_string(row, col + 33, str(contract_id.date_end), main_heading)
                                    if contract_id.state:
                                        if contract_id.state == 'draft':
                                            sheet.write_string(row, col + 34, str("New"), main_heading)
                                        if contract_id.state == 'open':
                                            sheet.write_string(row, col + 34, str("Running"), main_heading)
                                        if contract_id.state == 'pending':
                                            sheet.write_string(row, col + 34, str("To Renew"), main_heading)
                                        if contract_id.state == 'close':
                                            sheet.write_string(row, col + 34, str("Expired"), main_heading)
                                        if contract_id.state == 'cancel':
                                            sheet.write_string(row, col + 34, str("Cancelled"), main_heading)
                                    if contract_id.analytic_account_id:
                                        sheet.write_string(row, col + 35,
                                                           str(contract_id.analytic_account_id.display_name),
                                                           main_heading)
                                    if employee_id.salary_structure.name:
                                        sheet.write_string(row, col + 36, str(employee_id.salary_structure.name),
                                                           main_heading)
                                    if contract_id.wage:
                                        sheet.write_number(row, col + 37, contract_id.wage, main_heading)
                                        print('wage=', contract_id.wage)
                                        wage_total += contract_id.wage
                                        print('wage total=', wage_total)
                                    if transport:
                                        sheet.write_number(row, col + 38, transport, main_heading)
                                        transport_total += transport
                                    if self.env.user.company_id.company_code == "BIC":
                                        if transport_300:
                                            sheet.write_number(row, col + 39, transport_300, main_heading)
                                            transport_300_total += transport_300
                                        if transport_1500:
                                            sheet.write_number(row, col + 40, transport_1500, main_heading)
                                            transport_1500_total += transport_1500
                                        if house:
                                            sheet.write_number(row, col + 41, house, main_heading)
                                            house_rent_total += house
                                        if house_500:
                                            sheet.write_number(row, col + 42, house_500, main_heading)
                                            house_500_total += house_500
                                        if food_allowance:
                                            sheet.write_number(row, col + 43, food_allowance, main_heading)
                                            food_total += food_allowance
                                        if work_nature_allowance:
                                            sheet.write_number(row, col + 44, work_nature_allowance, main_heading)
                                            work_nature_total += work_nature_allowance
                                        if gross:
                                            sheet.write_number(row, col + 45, gross, main_heading)
                                            gross_total += gross
                                        if fixed_add_allowance:
                                            sheet.write_number(row, col + 46, fixed_add_allowance, main_heading)
                                            fixed_additional_total += fixed_add_allowance
                                        if fixed_deduct_amount:
                                            sheet.write_number(row, col + 47, fixed_deduct_amount, main_heading)
                                            fixed_deduction_total += fixed_deduct_amount
                                        if saudi_gosi_10:
                                            sheet.write_number(row, col + 48, saudi_gosi_10, main_heading)
                                            saudi_gosi_total += saudi_gosi_10
                                        if company_gosi_22:
                                            sheet.write_number(row, col + 49, company_gosi_22, main_heading)
                                            company_gosi_22_total += company_gosi_22
                                        if company_gosi_12:
                                            sheet.write_number(row, col + 50, company_gosi_12, main_heading)
                                            company_gosi_12_total += company_gosi_12
                                        if net:
                                            sheet.write_number(row, col + 51, net, main_heading)
                                            net_total += net
                                    else:
                                        if house:
                                            sheet.write_number(row, col + 39, house, main_heading)
                                            house_rent_total += house
                                        if food_allowance:
                                            sheet.write_number(row, col + 40, food_allowance, main_heading)
                                            food_total += food_allowance
                                        if work_nature_allowance:
                                            sheet.write_number(row, col + 41, work_nature_allowance, main_heading)
                                            work_nature_total += work_nature_allowance
                                        if gross:
                                            sheet.write_number(row, col + 42, gross, main_heading)
                                            gross_total += gross
                                        if fixed_add_allowance:
                                            sheet.write_number(row, col + 43, fixed_add_allowance, main_heading)
                                            fixed_additional_total += fixed_add_allowance
                                        if fixed_deduct_amount:
                                            sheet.write_number(row, col + 44, fixed_deduct_amount, main_heading)
                                            fixed_deduction_total += fixed_deduct_amount
                                        if saudi_gosi_10:
                                            sheet.write_number(row, col + 45, saudi_gosi_10, main_heading)
                                            saudi_gosi_total += saudi_gosi_10
                                        if company_gosi_22:
                                            sheet.write_number(row, col + 46, company_gosi_22, main_heading)
                                            company_gosi_22_total += company_gosi_22
                                        if company_gosi_12:
                                            sheet.write_number(row, col + 47, company_gosi_12, main_heading)
                                            company_gosi_12_total += company_gosi_12
                                        if net:
                                            sheet.write_number(row, col + 48, net, main_heading)
                                            net_total += net
                                    row += 1
                                    total += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_number(row, col + 1, total, main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            sheet.write_number(row, col + 37, wage_total, main_heading)
                            sheet.write_number(row, col + 38, transport_total, main_heading)
                            if self.env.user.company_id.company_code == "BIC":
                                sheet.write_number(row, col + 39, transport_300_total, main_heading)
                                sheet.write_number(row, col + 40, transport_1500_total, main_heading)
                                sheet.write_number(row, col + 41, house_rent_total, main_heading)
                                sheet.write_number(row, col + 42, house_500_total, main_heading)
                                sheet.write_number(row, col + 43, food_total, main_heading)
                                sheet.write_number(row, col + 44, work_nature_total, main_heading)
                                sheet.write_number(row, col + 45, gross_total, main_heading)
                                sheet.write_number(row, col + 46, fixed_additional_total, main_heading)
                                sheet.write_number(row, col + 47, fixed_deduction_total, main_heading)
                                sheet.write_number(row, col + 48, saudi_gosi_total, main_heading)
                                sheet.write_number(row, col + 49, company_gosi_22_total, main_heading)
                                sheet.write_number(row, col + 50, company_gosi_12_total, main_heading)
                                sheet.write_number(row, col + 51, net_total, main_heading)
                            else:
                                sheet.write_number(row, col + 39, house_rent_total, main_heading)
                                sheet.write_number(row, col + 40, food_total, main_heading)
                                sheet.write_number(row, col + 41, work_nature_total, main_heading)
                                sheet.write_number(row, col + 42, gross_total, main_heading)
                                sheet.write_number(row, col + 43, fixed_additional_total, main_heading)
                                sheet.write_number(row, col + 44, fixed_deduction_total, main_heading)
                                sheet.write_number(row, col + 45, saudi_gosi_total, main_heading)
                                sheet.write_number(row, col + 46, company_gosi_22_total, main_heading)
                                sheet.write_number(row, col + 47, company_gosi_12_total, main_heading)
                                sheet.write_number(row, col + 48, net_total, main_heading)
                            row += 1
                            grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 1, grand_total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if not docs.is_parent_dempart:
                for department_id in department_ids:
                    if department_id:
                        if department_id.display_name not in department_list:
                            department_list.append(department_id.display_name)
                for department_name in department_list:
                    if department_name:
                        department_employee_ids = employee_ids.filtered(lambda r: r.department_id.display_name == department_name)
                        if department_employee_ids:
                            total = 0
                            wage_total = 0.0
                            transport_total = 0.0
                            transport_300_total = 0.0
                            transport_1500_total = 0.0
                            house_rent_total = 0.0
                            house_500_total = 0.0
                            food_total = 0.0
                            work_nature_total = 0.0
                            gross_total = 0.0
                            fixed_additional_total = 0.0
                            fixed_deduction_total = 0.0
                            saudi_gosi_total = 0.0
                            company_gosi_12_total = 0.0
                            company_gosi_22_total = 0.0
                            net_total = 0.0
                            sheet.write(row, col, 'Department', main_heading2)
                            sheet.write_string(row, col + 1, str(department_name), main_heading)
                            sheet.write(row, col + 2, 'الادارة', main_heading2)
                            row += 1
                            for employee_id in department_employee_ids:
                                if employee_id:
                                    gross = 0.0
                                    transport = 0.0
                                    transport_300 = 0.0
                                    transport_1500 = 0.0
                                    house = 0.0
                                    house_500 = 0.0
                                    food_allowance = 0.0
                                    work_nature_allowance = 0.0
                                    fixed_add_allowance = 0.0
                                    fixed_deduct_amount = 0.0
                                    saudi_gosi_10 = 0.0
                                    company_gosi_12 = 0.0
                                    company_gosi_22 = 0.0
                                    net = 0.0
                                    gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                                    transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                                    transport300_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'CA22')
                                    transport1500_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'CA23')
                                    house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                                    house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                                    house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                                    saudi_gosi_10_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'GOSI')
                                    company_gosi_12_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'CGOSI')
                                    company_gosi_22_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'FCGOSI')
                                    net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                                    food_allowance_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'FA')
                                    work_nature_allowance_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'NWA')
                                    fixed_add_allowance_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'FAA')
                                    fixed_deduct_amount_id = employee_id.line_ids.filtered(
                                        lambda l: l.code and l.code == 'DEDFIXD')
                                    if gross_id:
                                        gross = gross_id.total
                                    if transport_id:
                                        transport = transport_id.total
                                    if transport300_id:
                                        transport_300 = transport300_id.total
                                    if transport1500_id:
                                        transport_1500 = transport1500_id.total
                                    if house_id:
                                        house = house_id.total
                                    if house_id_1:
                                        house = house_id_1.total
                                    if house500_id:
                                        house_500 = house500_id.total
                                    if saudi_gosi_10_id:
                                        saudi_gosi_10 = saudi_gosi_10_id.total
                                    if company_gosi_12_id:
                                        company_gosi_12 = company_gosi_12_id.total
                                    if company_gosi_22_id:
                                        company_gosi_22 = company_gosi_22_id.total
                                    if net_id:
                                        net = net_id.total
                                    if food_allowance_id:
                                        food_allowance = food_allowance_id.total
                                    if work_nature_allowance_id:
                                        work_nature_allowance = work_nature_allowance_id.total
                                    if fixed_add_allowance_id:
                                        fixed_add_allowance = fixed_add_allowance_id.total
                                    if fixed_deduct_amount_id:
                                        fixed_deduct_amount = fixed_deduct_amount_id.total
                                    contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                                    if employee_id.driver_code:
                                        sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                    if employee_id.employee_code:
                                        sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                    if employee_id.name:
                                        sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                    if employee_id.name_english:
                                        sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                    if employee_id.parent_id.name:
                                        sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                                    if employee_id.branch_id.region.bsg_region_name:
                                        sheet.write_string(row, col + 5,
                                                           str(employee_id.branch_id.region.bsg_region_name),
                                                           main_heading)
                                    if employee_id.branch_id.branch_ar_name:
                                        sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                                           main_heading)
                                    if employee_id.work_location:
                                        sheet.write_string(row, col + 7, str(employee_id.work_location), main_heading)
                                    if employee_id.job_id.name:
                                        sheet.write_string(row, col + 8, str(employee_id.job_id.name), main_heading)
                                    if employee_id.employee_state:
                                        sheet.write_string(row, col + 9, str(employee_id.employee_state), main_heading)
                                    if employee_id.suspend_salary:
                                        sheet.write_string(row, col + 10, str('True'), main_heading)
                                    if employee_id.is_driver:
                                        sheet.write_string(row, col + 11, str('Driver'), main_heading)
                                    if employee_id.guarantor_id.name:
                                        sheet.write_string(row, col + 12, str(employee_id.guarantor_id.name),
                                                           main_heading)
                                    if employee_id.company_id.name:
                                        sheet.write_string(row, col + 13, str(employee_id.company_id.name),
                                                           main_heading)
                                    if employee_id.user_id.name:
                                        sheet.write_string(row, col + 14, str(employee_id.user_id.name), main_heading)
                                    if employee_id.partner_id.name:
                                        sheet.write_string(row, col + 15, str(employee_id.partner_id.name),
                                                           main_heading)
                                    if employee_id.last_return_date:
                                        sheet.write_string(row, col + 16, str(employee_id.last_return_date),
                                                           main_heading)
                                    if employee_id.mobile_phone:
                                        sheet.write_string(row, col + 17, str(employee_id.mobile_phone), main_heading)
                                    if employee_id.country_id.name:
                                        sheet.write_string(row, col + 18, str(employee_id.country_id.name),
                                                           main_heading)
                                    if employee_id.country_id:
                                        if employee_id.country_id.code == 'SA':
                                            if employee_id.bsg_national_id.bsg_nationality_name:
                                                sheet.write_string(row, col + 19,
                                                                   str(employee_id.bsg_national_id.bsg_nationality_name),
                                                                   main_heading)
                                        else:
                                            if employee_id.bsg_empiqama.bsg_iqama_name:
                                                sheet.write_string(row, col + 19,
                                                                   str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                                   main_heading)
                                    if employee_id.bsg_bank_id.bsg_acc_number:
                                        sheet.write_string(row, col + 20, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                           main_heading)
                                    if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                        sheet.write_string(row, col + 21,
                                                           str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                           main_heading)
                                    if employee_id.salary_payment_method:
                                        sheet.write_string(row, col + 22, str(employee_id.salary_payment_method),
                                                           main_heading)
                                    if employee_id.bsg_bank_id.bsg_bank_name:
                                        sheet.write_string(row, col + 23, str(employee_id.bsg_bank_id.bsg_bank_name),
                                                           main_heading)
                                    if employee_id.category_ids:
                                        rec_names = employee_id.category_ids.mapped('name')
                                        names = ','.join(rec_names)
                                        sheet.write_string(row, col + 24, str(names), main_heading)
                                    if employee_id.birthday:
                                        sheet.write_string(row, col + 25, str(employee_id.birthday), main_heading)
                                    if employee_id.bsgjoining_date:
                                        sheet.write_string(row, col + 26, str(employee_id.bsgjoining_date),
                                                           main_heading)
                                    if employee_id.end_service_date:
                                        sheet.write_string(row, col + 27, str(employee_id.end_service_date),
                                                           main_heading)
                                    if employee_id.remaining_leaves:
                                        sheet.write_string(row, col + 28, str(employee_id.remaining_leaves),
                                                           main_heading)
                                    if employee_id.leave_start_date:
                                        sheet.write_string(row, col + 29, str(employee_id.leave_start_date),
                                                           main_heading)
                                    if employee_id.last_return_date:
                                        sheet.write_string(row, col + 30, str(employee_id.last_return_date),
                                                           main_heading)
                                    if employee_id.gender:
                                        sheet.write_string(row, col + 31, str(employee_id.gender), main_heading)
                                    if contract_id.date_start:
                                        sheet.write_string(row, col + 32, str(contract_id.date_start), main_heading)
                                    if contract_id.date_end:
                                        sheet.write_string(row, col + 33, str(contract_id.date_end), main_heading)
                                    if contract_id.state:
                                        if contract_id.state == 'draft':
                                            sheet.write_string(row, col + 34, str("New"), main_heading)
                                        if contract_id.state == 'open':
                                            sheet.write_string(row, col + 34, str("Running"), main_heading)
                                        if contract_id.state == 'pending':
                                            sheet.write_string(row, col + 34, str("To Renew"), main_heading)
                                        if contract_id.state == 'close':
                                            sheet.write_string(row, col + 34, str("Expired"), main_heading)
                                        if contract_id.state == 'cancel':
                                            sheet.write_string(row, col + 34, str("Cancelled"), main_heading)
                                    if contract_id.analytic_account_id:
                                        sheet.write_string(row, col + 35,
                                                           str(contract_id.analytic_account_id.display_name),
                                                           main_heading)
                                    if employee_id.salary_structure.name:
                                        sheet.write_string(row, col + 36, str(employee_id.salary_structure.name),
                                                           main_heading)
                                    if contract_id.wage:
                                        sheet.write_number(row, col + 37, contract_id.wage, main_heading)
                                        print('wage=', contract_id.wage)
                                        wage_total += contract_id.wage
                                        print('wage total=', wage_total)
                                    if transport:
                                        sheet.write_number(row, col + 38, transport, main_heading)
                                        transport_total += transport
                                    if self.env.user.company_id.company_code == "BIC":
                                        if transport_300:
                                            sheet.write_number(row, col + 39, transport_300, main_heading)
                                            transport_300_total += transport_300
                                        if transport_1500:
                                            sheet.write_number(row, col + 40, transport_1500, main_heading)
                                            transport_1500_total += transport_1500
                                        if house:
                                            sheet.write_number(row, col + 41, house, main_heading)
                                            house_rent_total += house
                                        if house_500:
                                            sheet.write_number(row, col + 42, house_500, main_heading)
                                            house_500_total += house_500
                                        if food_allowance:
                                            sheet.write_number(row, col + 43, food_allowance, main_heading)
                                            food_total += food_allowance
                                        if work_nature_allowance:
                                            sheet.write_number(row, col + 44, work_nature_allowance, main_heading)
                                            work_nature_total += work_nature_allowance
                                        if gross:
                                            sheet.write_number(row, col + 45, gross, main_heading)
                                            gross_total += gross
                                        if fixed_add_allowance:
                                            sheet.write_number(row, col + 46, fixed_add_allowance, main_heading)
                                            fixed_additional_total += fixed_add_allowance
                                        if fixed_deduct_amount:
                                            sheet.write_number(row, col + 47, fixed_deduct_amount, main_heading)
                                            fixed_deduction_total += fixed_deduct_amount
                                        if saudi_gosi_10:
                                            sheet.write_number(row, col + 48, saudi_gosi_10, main_heading)
                                            saudi_gosi_total += saudi_gosi_10
                                        if company_gosi_22:
                                            sheet.write_number(row, col + 49, company_gosi_22, main_heading)
                                            company_gosi_22_total += company_gosi_22
                                        if company_gosi_12:
                                            sheet.write_number(row, col + 50, company_gosi_12, main_heading)
                                            company_gosi_12_total += company_gosi_12
                                        if net:
                                            sheet.write_number(row, col + 51, net, main_heading)
                                            net_total += net
                                    else:
                                        if house:
                                            sheet.write_number(row, col + 39, house, main_heading)
                                            house_rent_total += house
                                        if food_allowance:
                                            sheet.write_number(row, col + 40, food_allowance, main_heading)
                                            food_total += food_allowance
                                        if work_nature_allowance:
                                            sheet.write_number(row, col + 41, work_nature_allowance, main_heading)
                                            work_nature_total += work_nature_allowance
                                        if gross:
                                            sheet.write_number(row, col + 42, gross, main_heading)
                                            gross_total += gross
                                        if fixed_add_allowance:
                                            sheet.write_number(row, col + 43, fixed_add_allowance, main_heading)
                                            fixed_additional_total += fixed_add_allowance
                                        if fixed_deduct_amount:
                                            sheet.write_number(row, col + 44, fixed_deduct_amount, main_heading)
                                            fixed_deduction_total += fixed_deduct_amount
                                        if saudi_gosi_10:
                                            sheet.write_number(row, col + 45, saudi_gosi_10, main_heading)
                                            saudi_gosi_total += saudi_gosi_10
                                        if company_gosi_22:
                                            sheet.write_number(row, col + 46, company_gosi_22, main_heading)
                                            company_gosi_22_total += company_gosi_22
                                        if company_gosi_12:
                                            sheet.write_number(row, col + 47, company_gosi_12, main_heading)
                                            company_gosi_12_total += company_gosi_12
                                        if net:
                                            sheet.write_number(row, col + 48, net, main_heading)
                                            net_total += net
                                    row += 1
                                    total += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_number(row, col + 1, total, main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            sheet.write_number(row, col + 37, wage_total, main_heading)
                            sheet.write_number(row, col + 38, transport_total, main_heading)
                            if self.env.user.company_id.company_code == "BIC":
                                sheet.write_number(row, col + 39, transport_300_total, main_heading)
                                sheet.write_number(row, col + 40, transport_1500_total, main_heading)
                                sheet.write_number(row, col + 41, house_rent_total, main_heading)
                                sheet.write_number(row, col + 42, house_500_total, main_heading)
                                sheet.write_number(row, col + 43, food_total, main_heading)
                                sheet.write_number(row, col + 44, work_nature_total, main_heading)
                                sheet.write_number(row, col + 45, gross_total, main_heading)
                                sheet.write_number(row, col + 46, fixed_additional_total, main_heading)
                                sheet.write_number(row, col + 47, fixed_deduction_total, main_heading)
                                sheet.write_number(row, col + 48, saudi_gosi_total, main_heading)
                                sheet.write_number(row, col + 49, company_gosi_22_total, main_heading)
                                sheet.write_number(row, col + 50, company_gosi_12_total, main_heading)
                                sheet.write_number(row, col + 51, net_total, main_heading)
                            else:
                                sheet.write_number(row, col + 39, house_rent_total, main_heading)
                                sheet.write_number(row, col + 40, food_total, main_heading)
                                sheet.write_number(row, col + 41, work_nature_total, main_heading)
                                sheet.write_number(row, col + 42, gross_total, main_heading)
                                sheet.write_number(row, col + 43, fixed_additional_total, main_heading)
                                sheet.write_number(row, col + 44, fixed_deduction_total, main_heading)
                                sheet.write_number(row, col + 45, saudi_gosi_total, main_heading)
                                sheet.write_number(row, col + 46, company_gosi_22_total, main_heading)
                                sheet.write_number(row, col + 47, company_gosi_12_total, main_heading)
                                sheet.write_number(row, col + 48, net_total, main_heading)
                            row += 1
                            grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 1, grand_total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_job_positions':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Job Position"
            sheet.merge_range('A1:AE1', 'مجموعة تقرير معلومات راتب الموظف حسب الوظيفة', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Job Position', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Department', main_heading2)
            sheet.write(row, col + 8, 'Work Location', main_heading2)
            sheet.write(row, col + 9, 'Employ Status', main_heading2)
            sheet.write(row, col + 10, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 11, 'Is Driver?', main_heading2)
            sheet.write(row, col + 12, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 13, 'Company Name', main_heading2)
            sheet.write(row, col + 14, 'User Name', main_heading2)
            sheet.write(row, col + 15, 'Partner Name', main_heading2)
            sheet.write(row, col + 16, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 17, 'Mobile No.', main_heading2)
            sheet.write(row, col + 18, 'Nationality', main_heading2)
            sheet.write(row, col + 19, 'ID No.', main_heading2)
            sheet.write(row, col + 20, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 21, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 22, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 23, 'Bank Name', main_heading2)
            sheet.write(row, col + 24, 'Tags', main_heading2)
            sheet.write(row, col + 25, 'Date of Birth', main_heading2)
            sheet.write(row, col + 26, 'Date of Join', main_heading2)
            sheet.write(row, col + 27, 'End Service Date', main_heading2)
            sheet.write(row, col + 28, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 29, 'leave start date', main_heading2)
            sheet.write(row, col + 30, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 31, 'Gender', main_heading2)
            sheet.write(row, col + 32, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 33, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 35, 'Analytic Account', main_heading2)
            sheet.write(row, col + 36, 'Salary Structure', main_heading2)
            sheet.write(row, col + 37, 'Wage', main_heading2)
            sheet.write(row, col + 38, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 39, 'Transport', main_heading2)
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'House Rent', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'Food', main_heading2)
                sheet.write(row, col + 44, 'Work Nature', main_heading2)
                sheet.write(row, col + 45, 'Gross', main_heading2)
                sheet.write(row, col + 46, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 47, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 48, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 49, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 51, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 39, 'House Rent', main_heading2)
                sheet.write(row, col + 40, 'Food', main_heading2)
                sheet.write(row, col + 41, 'Work Nature', main_heading2)
                sheet.write(row, col + 42, 'Gross', main_heading2)
                sheet.write(row, col + 43, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 44, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 45, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 46, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 48, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'الادارة', main_heading2)
            sheet.write(row, col + 8, 'مكان العمل', main_heading2)
            sheet.write(row, col + 9, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 10, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 11, 'سائق ؟', main_heading2)
            sheet.write(row, col + 12, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 13, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 14, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 15, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 16, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 17, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 18, 'الجنسية', main_heading2)
            sheet.write(row, col + 19, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 20, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 21, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 22, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 23 ,'سوفت البنك', main_heading2)
            sheet.write(row, col + 24, 'الوسم', main_heading2)
            sheet.write(row, col + 25, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 26, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 27, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 28, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 29, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 31, 'الجنس', main_heading2)
            sheet.write(row, col + 32, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 33, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 34, 'حالة العقد', main_heading2)
            sheet.write(row, col + 35, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 36, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 37, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 38, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 39, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 40, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 41, 'بدل سكن', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 43, 'بدل طعام', main_heading2)
                sheet.write(row, col + 44, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 45, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 46, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 47, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 48, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 49, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 51, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 39, 'بدل سكن', main_heading2)
                sheet.write(row, col + 40, 'بدل طعام', main_heading2)
                sheet.write(row, col + 41, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 42, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 43, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 44, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 45, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 46, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 48, 'صافي الراتب', main_heading2)
            row += 1
            job_position_list = []
            grand_total = 0
            job_ids = self.env['hr.job'].search([])
            for job_id in job_ids:
                if job_id:
                    job_position_list.append(job_id.name)
            for job_position_name in job_position_list:
                if job_position_name:
                    job_employee_ids = employee_ids.filtered(lambda r: r.job_id.name == job_position_name)
                    if job_employee_ids:
                        total = 0
                        wage_total = 0.0
                        transport_total = 0.0
                        transport_300_total = 0.0
                        transport_1500_total = 0.0
                        house_rent_total = 0.0
                        house_500_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        sheet.write(row, col, 'Job Position', main_heading2)
                        sheet.write_string(row, col + 1, str(job_position_name), main_heading)
                        sheet.write(row, col + 2, 'الوظيفه', main_heading2)
                        row += 1
                        for employee_id in job_employee_ids:
                            if employee_id:
                                gross = 0.0
                                transport = 0.0
                                transport_300 = 0.0
                                transport_1500 = 0.0
                                house = 0.0
                                house_500 = 0.0
                                food_allowance = 0.0
                                work_nature_allowance = 0.0
                                fixed_add_allowance = 0.0
                                fixed_deduct_amount = 0.0
                                saudi_gosi_10 = 0.0
                                company_gosi_12 = 0.0
                                company_gosi_22 = 0.0
                                net = 0.0
                                gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                                transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                                transport300_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA22')
                                transport1500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA23')
                                house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                                house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                                house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                                saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GOSI')
                                company_gosi_12_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CGOSI')
                                company_gosi_22_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FCGOSI')
                                net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                                food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'FA')
                                work_nature_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'NWA')
                                fixed_add_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FAA')
                                fixed_deduct_amount_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'DEDFIXD')
                                if gross_id:
                                    gross = gross_id.total
                                if transport_id:
                                    transport = transport_id.total
                                if transport300_id:
                                    transport_300 = transport300_id.total
                                if transport1500_id:
                                    transport_1500 = transport1500_id.total
                                if house_id:
                                    house = house_id.total
                                if house_id_1:
                                    house = house_id_1.total
                                if house500_id:
                                    house_500 = house500_id.total
                                if saudi_gosi_10_id:
                                    saudi_gosi_10 = saudi_gosi_10_id.total
                                if company_gosi_12_id:
                                    company_gosi_12 = company_gosi_12_id.total
                                if company_gosi_22_id:
                                    company_gosi_22 = company_gosi_22_id.total
                                if net_id:
                                    net = net_id.total
                                if food_allowance_id:
                                    food_allowance = food_allowance_id.total
                                if work_nature_allowance_id:
                                    work_nature_allowance = work_nature_allowance_id.total
                                if fixed_add_allowance_id:
                                    fixed_add_allowance = fixed_add_allowance_id.total
                                if fixed_deduct_amount_id:
                                    fixed_deduct_amount = fixed_deduct_amount_id.total
                                contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                if employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                if employee_id.name:
                                    sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                if employee_id.name_english:
                                    sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                if employee_id.parent_id.name:
                                    sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                                if employee_id.branch_id.region.bsg_region_name:
                                    sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                                       main_heading)
                                if employee_id.branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                                       main_heading)
                                if employee_id.department_id.display_name:
                                    sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                                       main_heading)
                                if employee_id.work_location:
                                    sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                                if employee_id.employee_state:
                                    sheet.write_string(row, col + 9, str(employee_id.employee_state), main_heading)
                                if employee_id.suspend_salary:
                                    sheet.write_string(row, col + 10, str('True'), main_heading)
                                if employee_id.is_driver:
                                    sheet.write_string(row, col + 11, str('Driver'), main_heading)
                                if employee_id.guarantor_id.name:
                                    sheet.write_string(row, col + 12, str(employee_id.guarantor_id.name), main_heading)
                                if employee_id.company_id.name:
                                    sheet.write_string(row, col + 13, str(employee_id.company_id.name), main_heading)
                                if employee_id.user_id.name:
                                    sheet.write_string(row, col + 14, str(employee_id.user_id.name), main_heading)
                                if employee_id.partner_id.name:
                                    sheet.write_string(row, col + 15, str(employee_id.partner_id.name), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 16, str(employee_id.last_return_date), main_heading)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 17, str(employee_id.mobile_phone), main_heading)
                                if employee_id.country_id.name:
                                    sheet.write_string(row, col + 18, str(employee_id.country_id.name), main_heading)
                                if employee_id.country_id:
                                    if employee_id.country_id.code == 'SA':
                                        if employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 19,
                                                               str(employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 19,
                                                               str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if employee_id.bsg_bank_id.bsg_acc_number:
                                    sheet.write_string(row, col + 20, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                    sheet.write_string(row, col + 21,
                                                       str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                       main_heading)
                                if employee_id.salary_payment_method:
                                    sheet.write_string(row, col + 22, str(employee_id.salary_payment_method),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_bank_name:
                                    sheet.write_string(row, col + 23, str(employee_id.bsg_bank_id.bsg_bank_name),
                                                       main_heading)
                                if employee_id.category_ids:
                                    rec_names = employee_id.category_ids.mapped('name')
                                    names = ','.join(rec_names)
                                    sheet.write_string(row, col + 24, str(names), main_heading)
                                if employee_id.birthday:
                                    sheet.write_string(row, col + 25, str(employee_id.birthday), main_heading)
                                if employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 26, str(employee_id.bsgjoining_date), main_heading)
                                if employee_id.end_service_date:
                                    sheet.write_string(row, col + 27, str(employee_id.end_service_date), main_heading)
                                if employee_id.remaining_leaves:
                                    sheet.write_string(row, col + 28, str(employee_id.remaining_leaves), main_heading)
                                if employee_id.leave_start_date:
                                    sheet.write_string(row, col + 29, str(employee_id.leave_start_date), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 30, str(employee_id.last_return_date), main_heading)
                                if employee_id.gender:
                                    sheet.write_string(row, col + 31, str(employee_id.gender), main_heading)
                                if contract_id.date_start:
                                    sheet.write_string(row, col + 32, str(contract_id.date_start), main_heading)
                                if contract_id.date_end:
                                    sheet.write_string(row, col + 33, str(contract_id.date_end), main_heading)
                                if contract_id.state:
                                    if contract_id.state == 'draft':
                                        sheet.write_string(row, col + 34, str("New"), main_heading)
                                    if contract_id.state == 'open':
                                        sheet.write_string(row, col + 34, str("Running"), main_heading)
                                    if contract_id.state == 'pending':
                                        sheet.write_string(row, col + 34, str("To Renew"), main_heading)
                                    if contract_id.state == 'close':
                                        sheet.write_string(row, col + 34, str("Expired"), main_heading)
                                    if contract_id.state == 'cancel':
                                        sheet.write_string(row, col + 34, str("Cancelled"), main_heading)
                                if contract_id.analytic_account_id:
                                    sheet.write_string(row, col + 35, str(contract_id.analytic_account_id.display_name),
                                                       main_heading)
                                if employee_id.salary_structure.name:
                                    sheet.write_string(row, col + 36, str(employee_id.salary_structure.name),
                                                       main_heading)
                                if contract_id.wage:
                                    sheet.write_number(row, col + 37, contract_id.wage, main_heading)
                                    print('wage=', contract_id.wage)
                                    wage_total += contract_id.wage
                                    print('wage total=', wage_total)
                                if transport:
                                    sheet.write_number(row, col + 38, transport, main_heading)
                                    transport_total += transport
                                if self.env.user.company_id.company_code == "BIC":
                                    if transport_300:
                                        sheet.write_number(row, col + 39, transport_300, main_heading)
                                        transport_300_total += transport_300
                                    if transport_1500:
                                        sheet.write_number(row, col + 40, transport_1500, main_heading)
                                        transport_1500_total += transport_1500
                                    if house:
                                        sheet.write_number(row, col + 41, house, main_heading)
                                        house_rent_total += house
                                    if house_500:
                                        sheet.write_number(row, col + 42, house_500, main_heading)
                                        house_500_total += house_500
                                    if food_allowance:
                                        sheet.write_number(row, col + 43, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 44, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 45, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 46, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 47, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 48, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 49, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 50, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 51, net, main_heading)
                                        net_total += net
                                else:
                                    if house:
                                        sheet.write_number(row, col + 39, house, main_heading)
                                        house_rent_total += house
                                    if food_allowance:
                                        sheet.write_number(row, col + 40, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 41, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 42, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 43, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 44, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 45, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 46, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 47, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 48, net, main_heading)
                                        net_total += net
                                row += 1
                                total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_number(row, col + 1, total, main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        sheet.write_number(row, col + 37, wage_total, main_heading)
                        sheet.write_number(row, col + 38, transport_total, main_heading)
                        if self.env.user.company_id.company_code == "BIC":
                            sheet.write_number(row, col + 39, transport_300_total, main_heading)
                            sheet.write_number(row, col + 40, transport_1500_total, main_heading)
                            sheet.write_number(row, col + 41, house_rent_total, main_heading)
                            sheet.write_number(row, col + 42, house_500_total, main_heading)
                            sheet.write_number(row, col + 43, food_total, main_heading)
                            sheet.write_number(row, col + 44, work_nature_total, main_heading)
                            sheet.write_number(row, col + 45, gross_total, main_heading)
                            sheet.write_number(row, col + 46, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 47, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 48, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 49, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 50, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 51, net_total, main_heading)
                        else:
                            sheet.write_number(row, col + 39, house_rent_total, main_heading)
                            sheet.write_number(row, col + 40, food_total, main_heading)
                            sheet.write_number(row, col + 41, work_nature_total, main_heading)
                            sheet.write_number(row, col + 42, gross_total, main_heading)
                            sheet.write_number(row, col + 43, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 44, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 45, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 46, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 47, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 48, net_total, main_heading)
                        row += 1
                        grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 1, grand_total, main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_nationality':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Nationality"
            sheet.merge_range('A1:AE1', 'مجموعة تقرير معلومات راتب الموظف حسب الجنسية', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Nationality', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Department', main_heading2)
            sheet.write(row, col + 8, 'Work Location', main_heading2)
            sheet.write(row, col + 9, 'Jop Position', main_heading2)
            sheet.write(row, col + 10, 'Employ Status', main_heading2)
            sheet.write(row, col + 11, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 12, 'Is Driver?', main_heading2)
            sheet.write(row, col + 13, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 14, 'Company Name', main_heading2)
            sheet.write(row, col + 15, 'User Name', main_heading2)
            sheet.write(row, col + 16, 'Partner Name', main_heading2)
            sheet.write(row, col + 17, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 18, 'Mobile No.', main_heading2)
            sheet.write(row, col + 19, 'ID No.', main_heading2)
            sheet.write(row, col + 20, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 21, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 22, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 23, 'Bank Name', main_heading2)
            sheet.write(row, col + 24, 'Tags', main_heading2)
            sheet.write(row, col + 25, 'Date of Birth', main_heading2)
            sheet.write(row, col + 26, 'Date of Join', main_heading2)
            sheet.write(row, col + 27, 'End Service Date', main_heading2)
            sheet.write(row, col + 28, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 29, 'leave start date', main_heading2)
            sheet.write(row, col + 30, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 31, 'Gender', main_heading2)
            sheet.write(row, col + 32, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 33, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 35, 'Analytic Account', main_heading2)
            sheet.write(row, col + 36, 'Salary Structure', main_heading2)
            sheet.write(row, col + 37, 'Wage', main_heading2)
            sheet.write(row, col + 38, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 39, 'Transport', main_heading2)
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'House Rent', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'Food', main_heading2)
                sheet.write(row, col + 44, 'Work Nature', main_heading2)
                sheet.write(row, col + 45, 'Gross', main_heading2)
                sheet.write(row, col + 46, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 47, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 48, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 49, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 51, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 39, 'House Rent', main_heading2)
                sheet.write(row, col + 40, 'Food', main_heading2)
                sheet.write(row, col + 41, 'Work Nature', main_heading2)
                sheet.write(row, col + 42, 'Gross', main_heading2)
                sheet.write(row, col + 43, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 44, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 45, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 46, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 48, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'الادارة', main_heading2)
            sheet.write(row, col + 8, 'مكان العمل', main_heading2)
            sheet.write(row, col + 9, 'الوظيفه', main_heading2)
            sheet.write(row, col + 10, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 11, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 12, 'سائق ؟', main_heading2)
            sheet.write(row, col + 13, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 14, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 15, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 16, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 17, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 18, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 19, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 20, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 21, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 22, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 23, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 24, 'الوسم', main_heading2)
            sheet.write(row, col + 25, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 26, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 27, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 28, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 29, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 31, 'الجنس', main_heading2)
            sheet.write(row, col + 32, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 33, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 34, 'حالة العقد', main_heading2)
            sheet.write(row, col + 35, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 36, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 37, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 38, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 39, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 40, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 41, 'بدل سكن', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 43, 'بدل طعام', main_heading2)
                sheet.write(row, col + 44, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 45, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 46, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 47, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 48, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 49, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 51, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 39, 'بدل سكن', main_heading2)
                sheet.write(row, col + 40, 'بدل طعام', main_heading2)
                sheet.write(row, col + 41, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 42, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 43, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 44, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 45, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 46, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 48, 'صافي الراتب', main_heading2)
            row += 1
            country_list = []
            grand_total = 0
            country_ids = self.env['res.country'].search([])
            for country_id in country_ids:
                if country_id:
                    country_list.append(country_id.name)
            for country_name in country_list:
                if country_name:
                    country_employee_ids = employee_ids.filtered(lambda r: r.country_id.name == country_name)
                    if country_employee_ids:
                        total = 0
                        wage_total = 0.0
                        transport_total = 0.0
                        transport_300_total = 0.0
                        transport_1500_total = 0.0
                        house_rent_total = 0.0
                        house_500_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        sheet.write(row, col, 'Nationality', main_heading2)
                        sheet.write_string(row, col + 1, str(country_name), main_heading)
                        sheet.write(row, col + 2, 'الجنسية', main_heading2)
                        row += 1
                        for employee_id in country_employee_ids:
                            if employee_id:
                                gross = 0.0
                                transport = 0.0
                                transport_300 = 0.0
                                transport_1500 = 0.0
                                house = 0.0
                                house_500 = 0.0
                                food_allowance = 0.0
                                work_nature_allowance = 0.0
                                fixed_add_allowance = 0.0
                                fixed_deduct_amount = 0.0
                                saudi_gosi_10 = 0.0
                                company_gosi_12 = 0.0
                                company_gosi_22 = 0.0
                                net = 0.0
                                gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                                transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                                transport300_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA22')
                                transport1500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA23')
                                house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                                house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                                house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                                saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GOSI')
                                company_gosi_12_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CGOSI')
                                company_gosi_22_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FCGOSI')
                                net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                                food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'FA')
                                work_nature_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'NWA')
                                fixed_add_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FAA')
                                fixed_deduct_amount_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'DEDFIXD')
                                if gross_id:
                                    gross = gross_id.total
                                if transport_id:
                                    transport = transport_id.total
                                if transport300_id:
                                    transport_300 = transport300_id.total
                                if transport1500_id:
                                    transport_1500 = transport1500_id.total
                                if house_id:
                                    house = house_id.total
                                if house_id_1:
                                    house = house_id_1.total
                                if house500_id:
                                    house_500 = house500_id.total
                                if saudi_gosi_10_id:
                                    saudi_gosi_10 = saudi_gosi_10_id.total
                                if company_gosi_12_id:
                                    company_gosi_12 = company_gosi_12_id.total
                                if company_gosi_22_id:
                                    company_gosi_22 = company_gosi_22_id.total
                                if net_id:
                                    net = net_id.total
                                if food_allowance_id:
                                    food_allowance = food_allowance_id.total
                                if work_nature_allowance_id:
                                    work_nature_allowance = work_nature_allowance_id.total
                                if fixed_add_allowance_id:
                                    fixed_add_allowance = fixed_add_allowance_id.total
                                if fixed_deduct_amount_id:
                                    fixed_deduct_amount = fixed_deduct_amount_id.total
                                contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                if employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                if employee_id.name:
                                    sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                if employee_id.name_english:
                                    sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                if employee_id.parent_id.name:
                                    sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                                if employee_id.branch_id.region.bsg_region_name:
                                    sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                                       main_heading)
                                if employee_id.branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                                       main_heading)
                                if employee_id.department_id.display_name:
                                    sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                                       main_heading)
                                if employee_id.work_location:
                                    sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                                if employee_id.job_id.name:
                                    sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                                if employee_id.employee_state:
                                    sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                                if employee_id.suspend_salary:
                                    sheet.write_string(row, col + 11, str('True'), main_heading)
                                if employee_id.is_driver:
                                    sheet.write_string(row, col + 12, str('Driver'), main_heading)
                                if employee_id.guarantor_id.name:
                                    sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                                if employee_id.company_id.name:
                                    sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                                if employee_id.user_id.name:
                                    sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                                if employee_id.partner_id.name:
                                    sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                                if employee_id.country_id:
                                    if employee_id.country_id.code == 'SA':
                                        if employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 19,
                                                               str(employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 19,
                                                               str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if employee_id.bsg_bank_id.bsg_acc_number:
                                    sheet.write_string(row, col + 20, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                    sheet.write_string(row, col + 21,
                                                       str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                       main_heading)
                                if employee_id.salary_payment_method:
                                    sheet.write_string(row, col + 22, str(employee_id.salary_payment_method),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_bank_name:
                                    sheet.write_string(row, col + 23, str(employee_id.bsg_bank_id.bsg_bank_name),
                                                       main_heading)
                                if employee_id.category_ids:
                                    rec_names = employee_id.category_ids.mapped('name')
                                    names = ','.join(rec_names)
                                    sheet.write_string(row, col + 24, str(names), main_heading)
                                if employee_id.birthday:
                                    sheet.write_string(row, col + 25, str(employee_id.birthday), main_heading)
                                if employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 26, str(employee_id.bsgjoining_date), main_heading)
                                if employee_id.end_service_date:
                                    sheet.write_string(row, col + 27, str(employee_id.end_service_date), main_heading)
                                if employee_id.remaining_leaves:
                                    sheet.write_string(row, col + 28, str(employee_id.remaining_leaves), main_heading)
                                if employee_id.leave_start_date:
                                    sheet.write_string(row, col + 29, str(employee_id.leave_start_date), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 30, str(employee_id.last_return_date), main_heading)
                                if employee_id.gender:
                                    sheet.write_string(row, col + 31, str(employee_id.gender), main_heading)
                                if contract_id.date_start:
                                    sheet.write_string(row, col + 32, str(contract_id.date_start), main_heading)
                                if contract_id.date_end:
                                    sheet.write_string(row, col + 33, str(contract_id.date_end), main_heading)
                                if contract_id.state:
                                    if contract_id.state == 'draft':
                                        sheet.write_string(row, col + 34, str("New"), main_heading)
                                    if contract_id.state == 'open':
                                        sheet.write_string(row, col + 34, str("Running"), main_heading)
                                    if contract_id.state == 'pending':
                                        sheet.write_string(row, col + 34, str("To Renew"), main_heading)
                                    if contract_id.state == 'close':
                                        sheet.write_string(row, col + 34, str("Expired"), main_heading)
                                    if contract_id.state == 'cancel':
                                        sheet.write_string(row, col + 34, str("Cancelled"), main_heading)
                                if contract_id.analytic_account_id:
                                    sheet.write_string(row, col + 35, str(contract_id.analytic_account_id.display_name),
                                                       main_heading)
                                if employee_id.salary_structure.name:
                                    sheet.write_string(row, col + 36, str(employee_id.salary_structure.name),
                                                       main_heading)
                                if contract_id.wage:
                                    sheet.write_number(row, col + 37, contract_id.wage, main_heading)
                                    print('wage=', contract_id.wage)
                                    wage_total += contract_id.wage
                                    print('wage total=', wage_total)
                                if transport:
                                    sheet.write_number(row, col + 38, transport, main_heading)
                                    transport_total += transport
                                if self.env.user.company_id.company_code == "BIC":
                                    if transport_300:
                                        sheet.write_number(row, col + 39, transport_300, main_heading)
                                        transport_300_total += transport_300
                                    if transport_1500:
                                        sheet.write_number(row, col + 40, transport_1500, main_heading)
                                        transport_1500_total += transport_1500
                                    if house:
                                        sheet.write_number(row, col + 41, house, main_heading)
                                        house_rent_total += house
                                    if house_500:
                                        sheet.write_number(row, col + 42, house_500, main_heading)
                                        house_500_total += house_500
                                    if food_allowance:
                                        sheet.write_number(row, col + 43, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 44, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 45, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 46, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 47, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 48, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 49, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 50, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 51, net, main_heading)
                                        net_total += net
                                else:
                                    if house:
                                        sheet.write_number(row, col + 39, house, main_heading)
                                        house_rent_total += house
                                    if food_allowance:
                                        sheet.write_number(row, col + 40, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 41, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 42, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 43, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 44, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 45, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 46, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 47, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 48, net, main_heading)
                                        net_total += net
                                row += 1
                                total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_number(row, col + 1, total, main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        sheet.write_number(row, col + 37, wage_total, main_heading)
                        sheet.write_number(row, col + 38, transport_total, main_heading)
                        if self.env.user.company_id.company_code == "BIC":
                            sheet.write_number(row, col + 39, transport_300_total, main_heading)
                            sheet.write_number(row, col + 40, transport_1500_total, main_heading)
                            sheet.write_number(row, col + 41, house_rent_total, main_heading)
                            sheet.write_number(row, col + 42, house_500_total, main_heading)
                            sheet.write_number(row, col + 43, food_total, main_heading)
                            sheet.write_number(row, col + 44, work_nature_total, main_heading)
                            sheet.write_number(row, col + 45, gross_total, main_heading)
                            sheet.write_number(row, col + 46, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 47, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 48, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 49, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 50, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 51, net_total, main_heading)
                        else:
                            sheet.write_number(row, col + 39, house_rent_total, main_heading)
                            sheet.write_number(row, col + 40, food_total, main_heading)
                            sheet.write_number(row, col + 41, work_nature_total, main_heading)
                            sheet.write_number(row, col + 42, gross_total, main_heading)
                            sheet.write_number(row, col + 43, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 44, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 45, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 46, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 47, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 48, net_total, main_heading)
                        row += 1
                        grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 1, grand_total, main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_guarantors':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Guarantors"
            sheet.merge_range('A1:AE1', 'مجموعة تقرير معلومات رواتب الموظف حسب الضامنين', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Guarantors', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Department', main_heading2)
            sheet.write(row, col + 8, 'Work Location', main_heading2)
            sheet.write(row, col + 9, 'Jop Position', main_heading2)
            sheet.write(row, col + 10, 'Employ Status', main_heading2)
            sheet.write(row, col + 11, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 12, 'Is Driver?', main_heading2)
            sheet.write(row, col + 13, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 14, 'Company Name', main_heading2)
            sheet.write(row, col + 15, 'User Name', main_heading2)
            sheet.write(row, col + 16, 'Partner Name', main_heading2)
            sheet.write(row, col + 17, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 18, 'Mobile No.', main_heading2)
            sheet.write(row, col + 19, 'Nationality', main_heading2)
            sheet.write(row, col + 20, 'ID No.', main_heading2)
            sheet.write(row, col + 21, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 22, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 23, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 24, 'Bank Name', main_heading2)
            sheet.write(row, col + 25, 'Tags', main_heading2)
            sheet.write(row, col + 26, 'Date of Birth', main_heading2)
            sheet.write(row, col + 27, 'Date of Join', main_heading2)
            sheet.write(row, col + 28, 'End Service Date', main_heading2)
            sheet.write(row, col + 29, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 30, 'leave start date', main_heading2)
            sheet.write(row, col + 31, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 32, 'Gender', main_heading2)
            sheet.write(row, col + 33, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 35, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 36, 'Analytic Account', main_heading2)
            sheet.write(row, col + 37, 'Salary Structure', main_heading2)
            sheet.write(row, col + 38, 'Wage', main_heading2)
            sheet.write(row, col + 39, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'Transport', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'House Rent', main_heading2)
                sheet.write(row, col + 44, 'Food', main_heading2)
                sheet.write(row, col + 45, 'Work Nature', main_heading2)
                sheet.write(row, col + 46, 'Gross', main_heading2)
                sheet.write(row, col + 47, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 48, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 40, 'House Rent', main_heading2)
                sheet.write(row, col + 41, 'Food', main_heading2)
                sheet.write(row, col + 42, 'Work Nature', main_heading2)
                sheet.write(row, col + 43, 'Gross', main_heading2)
                sheet.write(row, col + 44, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 45, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'الادارة', main_heading2)
            sheet.write(row, col + 8, 'مكان العمل', main_heading2)
            sheet.write(row, col + 9, 'الوظيفه', main_heading2)
            sheet.write(row, col + 10, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 11, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 12, 'سائق ؟', main_heading2)
            sheet.write(row, col + 13, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 14, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 15, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 16, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 17, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 18, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 19, 'الجنسية', main_heading2)
            sheet.write(row, col + 20, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 21, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 22, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 23, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 24, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 25, 'الوسم', main_heading2)
            sheet.write(row, col + 26, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 27, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 28, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 29, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 31, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 32, 'الجنس', main_heading2)
            sheet.write(row, col + 33, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 34, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 35, 'حالة العقد', main_heading2)
            sheet.write(row, col + 36, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 37, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 38, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 39, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 41, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن', main_heading2)
                sheet.write(row, col + 43, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 44, 'بدل طعام', main_heading2)
                sheet.write(row, col + 45, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 46, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 47, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 48, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 40, 'بدل سكن', main_heading2)
                sheet.write(row, col + 41, 'بدل طعام', main_heading2)
                sheet.write(row, col + 42, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 43, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 44, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 45, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'صافي الراتب', main_heading2)
            row += 1
            guarantor_list = []
            grand_total = 0
            guarantor_ids = self.env['bsg.hr.guarantor'].search([])
            for guarantor_id in guarantor_ids:
                if guarantor_id:
                    guarantor_list.append(guarantor_id.name)
            for guarantor_name in guarantor_list:
                if guarantor_name:
                    guarantor_employee_ids = employee_ids.filtered(lambda r: r.bsg_empiqama.guarantor_id.name and r.bsg_empiqama.guarantor_id.name == guarantor_name)
                    if guarantor_employee_ids:
                        total = 0
                        wage_total = 0.0
                        transport_total = 0.0
                        transport_300_total = 0.0
                        transport_1500_total = 0.0
                        house_rent_total = 0.0
                        house_500_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        sheet.write(row, col, 'Guarantor', main_heading2)
                        sheet.write_string(row, col + 1, str(guarantor_name), main_heading)
                        sheet.write(row, col + 2, 'كفيل', main_heading2)
                        row += 1
                        for employee_id in guarantor_employee_ids:
                            if employee_id:
                                gross = 0.0
                                transport = 0.0
                                transport_300 = 0.0
                                transport_1500 = 0.0
                                house = 0.0
                                house_500 = 0.0
                                food_allowance = 0.0
                                work_nature_allowance = 0.0
                                fixed_add_allowance = 0.0
                                fixed_deduct_amount = 0.0
                                saudi_gosi_10 = 0.0
                                company_gosi_12 = 0.0
                                company_gosi_22 = 0.0
                                net = 0.0
                                gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                                transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                                transport300_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA22')
                                transport1500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA23')
                                house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                                house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                                house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                                saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GOSI')
                                company_gosi_12_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CGOSI')
                                company_gosi_22_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FCGOSI')
                                net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                                food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'FA')
                                work_nature_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'NWA')
                                fixed_add_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FAA')
                                fixed_deduct_amount_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'DEDFIXD')
                                if gross_id:
                                    gross = gross_id.total
                                if transport_id:
                                    transport = transport_id.total
                                if transport300_id:
                                    transport_300 = transport300_id.total
                                if transport1500_id:
                                    transport_1500 = transport1500_id.total
                                if house_id:
                                    house = house_id.total
                                if house_id_1:
                                    house = house_id_1.total
                                if house500_id:
                                    house_500 = house500_id.total
                                if saudi_gosi_10_id:
                                    saudi_gosi_10 = saudi_gosi_10_id.total
                                if company_gosi_12_id:
                                    company_gosi_12 = company_gosi_12_id.total
                                if company_gosi_22_id:
                                    company_gosi_22 = company_gosi_22_id.total
                                if net_id:
                                    net = net_id.total
                                if food_allowance_id:
                                    food_allowance = food_allowance_id.total
                                if work_nature_allowance_id:
                                    work_nature_allowance = work_nature_allowance_id.total
                                if fixed_add_allowance_id:
                                    fixed_add_allowance = fixed_add_allowance_id.total
                                if fixed_deduct_amount_id:
                                    fixed_deduct_amount = fixed_deduct_amount_id.total
                                contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                if employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                if employee_id.name:
                                    sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                if employee_id.name_english:
                                    sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                if employee_id.parent_id.name:
                                    sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                                if employee_id.branch_id.region.bsg_region_name:
                                    sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                                       main_heading)
                                if employee_id.branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                                       main_heading)
                                if employee_id.department_id.display_name:
                                    sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                                       main_heading)
                                if employee_id.work_location:
                                    sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                                if employee_id.job_id.name:
                                    sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                                if employee_id.employee_state:
                                    sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                                if employee_id.suspend_salary:
                                    sheet.write_string(row, col + 11, str('True'), main_heading)
                                if employee_id.is_driver:
                                    sheet.write_string(row, col + 12, str('Driver'), main_heading)
                                if employee_id.guarantor_id.name:
                                    sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                                if employee_id.company_id.name:
                                    sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                                if employee_id.user_id.name:
                                    sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                                if employee_id.partner_id.name:
                                    sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                                if employee_id.country_id.name:
                                    sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                                if employee_id.country_id:
                                    if employee_id.country_id.code == 'SA':
                                        if employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if employee_id.bsg_bank_id.bsg_acc_number:
                                    sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                    sheet.write_string(row, col + 22,
                                                       str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                       main_heading)
                                if employee_id.salary_payment_method:
                                    sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_bank_name:
                                    sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                                       main_heading)
                                if employee_id.category_ids:
                                    rec_names = employee_id.category_ids.mapped('name')
                                    names = ','.join(rec_names)
                                    sheet.write_string(row, col + 25, str(names), main_heading)
                                if employee_id.birthday:
                                    sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                                if employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                                if employee_id.end_service_date:
                                    sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                                if employee_id.remaining_leaves:
                                    sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                                if employee_id.leave_start_date:
                                    sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                                if employee_id.gender:
                                    sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                                if contract_id.date_start:
                                    sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                                if contract_id.date_end:
                                    sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                                if contract_id.state:
                                    if contract_id.state == 'draft':
                                        sheet.write_string(row, col + 35, str("New"), main_heading)
                                    if contract_id.state == 'open':
                                        sheet.write_string(row, col + 35, str("Running"), main_heading)
                                    if contract_id.state == 'pending':
                                        sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                                    if contract_id.state == 'close':
                                        sheet.write_string(row, col + 35, str("Expired"), main_heading)
                                    if contract_id.state == 'cancel':
                                        sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                                if contract_id.analytic_account_id:
                                    sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                                       main_heading)
                                if employee_id.salary_structure.name:
                                    sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                                       main_heading)
                                if contract_id.wage:
                                    sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                                    print('wage=', contract_id.wage)
                                    wage_total += contract_id.wage
                                    print('wage total=', wage_total)
                                if transport:
                                    sheet.write_number(row, col + 39, transport, main_heading)
                                    transport_total += transport
                                if self.env.user.company_id.company_code == "BIC":
                                    if transport_300:
                                        sheet.write_number(row, col + 40, transport_300, main_heading)
                                        transport_300_total += transport_300
                                    if transport_1500:
                                        sheet.write_number(row, col + 41, transport_1500, main_heading)
                                        transport_1500_total += transport_1500
                                    if house:
                                        sheet.write_number(row, col + 42, house, main_heading)
                                        house_rent_total += house
                                    if house_500:
                                        sheet.write_number(row, col + 43, house_500, main_heading)
                                        house_500_total += house_500
                                    if food_allowance:
                                        sheet.write_number(row, col + 44, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 46, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 52, net, main_heading)
                                        net_total += net
                                else:
                                    if house:
                                        sheet.write_number(row, col + 40, house, main_heading)
                                        house_rent_total += house
                                    if food_allowance:
                                        sheet.write_number(row, col + 41, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 43, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 49, net, main_heading)
                                        net_total += net
                                row += 1
                                total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_number(row, col + 1, total, main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        sheet.write_number(row, col + 38, wage_total, main_heading)
                        sheet.write_number(row, col + 39, transport_total, main_heading)
                        if self.env.user.company_id.company_code == "BIC":
                            sheet.write_number(row, col + 40, transport_300_total, main_heading)
                            sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                            sheet.write_number(row, col + 42, house_rent_total, main_heading)
                            sheet.write_number(row, col + 43, house_500_total, main_heading)
                            sheet.write_number(row, col + 44, food_total, main_heading)
                            sheet.write_number(row, col + 45, work_nature_total, main_heading)
                            sheet.write_number(row, col + 46, gross_total, main_heading)
                            sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 52, net_total, main_heading)
                        else:
                            sheet.write_number(row, col + 40, house_rent_total, main_heading)
                            sheet.write_number(row, col + 41, food_total, main_heading)
                            sheet.write_number(row, col + 42, work_nature_total, main_heading)
                            sheet.write_number(row, col + 43, gross_total, main_heading)
                            sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 49, net_total, main_heading)
                        row += 1
                        grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 1, grand_total, main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_emp_tags':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Employee Tags"
            sheet.merge_range('A1:AE1', 'مجموعة تقرير معلومات رواتب الموظف حسب علامات الموظف', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Employee Tags', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Department', main_heading2)
            sheet.write(row, col + 8, 'Work Location', main_heading2)
            sheet.write(row, col + 9, 'Jop Position', main_heading2)
            sheet.write(row, col + 10, 'Employ Status', main_heading2)
            sheet.write(row, col + 11, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 12, 'Is Driver?', main_heading2)
            sheet.write(row, col + 13, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 14, 'Company Name', main_heading2)
            sheet.write(row, col + 15, 'User Name', main_heading2)
            sheet.write(row, col + 16, 'Partner Name', main_heading2)
            sheet.write(row, col + 17, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 18, 'Mobile No.', main_heading2)
            sheet.write(row, col + 19, 'Nationality', main_heading2)
            sheet.write(row, col + 20, 'ID No.', main_heading2)
            sheet.write(row, col + 21, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 22, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 23, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 24, 'Bank Name', main_heading2)
            sheet.write(row, col + 25, 'Tags', main_heading2)
            sheet.write(row, col + 26, 'Date of Birth', main_heading2)
            sheet.write(row, col + 27, 'Date of Join', main_heading2)
            sheet.write(row, col + 28, 'End Service Date', main_heading2)
            sheet.write(row, col + 29, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 30, 'leave start date', main_heading2)
            sheet.write(row, col + 31, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 32, 'Gender', main_heading2)
            sheet.write(row, col + 33, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 35, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 36, 'Analytic Account', main_heading2)
            sheet.write(row, col + 37, 'Salary Structure', main_heading2)
            sheet.write(row, col + 38, 'Wage', main_heading2)
            sheet.write(row, col + 39, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'Transport', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'House Rent', main_heading2)
                sheet.write(row, col + 44, 'Food', main_heading2)
                sheet.write(row, col + 45, 'Work Nature', main_heading2)
                sheet.write(row, col + 46, 'Gross', main_heading2)
                sheet.write(row, col + 47, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 48, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 40, 'House Rent', main_heading2)
                sheet.write(row, col + 41, 'Food', main_heading2)
                sheet.write(row, col + 42, 'Work Nature', main_heading2)
                sheet.write(row, col + 43, 'Gross', main_heading2)
                sheet.write(row, col + 44, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 45, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'الادارة', main_heading2)
            sheet.write(row, col + 8, 'مكان العمل', main_heading2)
            sheet.write(row, col + 9, 'الوظيفه', main_heading2)
            sheet.write(row, col + 10, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 11, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 12, 'سائق ؟', main_heading2)
            sheet.write(row, col + 13, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 14, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 15, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 16, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 17, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 18, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 19, 'الجنسية', main_heading2)
            sheet.write(row, col + 20, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 21, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 22, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 23, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 24, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 25, 'الوسم', main_heading2)
            sheet.write(row, col + 26, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 27, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 28, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 29, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 31, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 32, 'الجنس', main_heading2)
            sheet.write(row, col + 33, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 34, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 35, 'حالة العقد', main_heading2)
            sheet.write(row, col + 36, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 37, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 38, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 39, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 41, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن', main_heading2)
                sheet.write(row, col + 43, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 44, 'بدل طعام', main_heading2)
                sheet.write(row, col + 45, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 46, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 47, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 48, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 40, 'بدل سكن', main_heading2)
                sheet.write(row, col + 41, 'بدل طعام', main_heading2)
                sheet.write(row, col + 42, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 43, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 44, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 45, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'صافي الراتب', main_heading2)
            row += 1
            tags_list = []
            grand_total = 0
            category_ids = self.env['hr.employee.category'].search([])
            for category_id in category_ids:
                if category_id:
                    tags_list.append(category_id)
            for tag_id in tags_list:
                if tag_id:
                    total = 0
                    wage_total = 0.0
                    transport_total = 0.0
                    transport_300_total = 0.0
                    transport_1500_total = 0.0
                    house_rent_total = 0.0
                    house_500_total = 0.0
                    food_total = 0.0
                    work_nature_total = 0.0
                    gross_total = 0.0
                    fixed_additional_total = 0.0
                    fixed_deduction_total = 0.0
                    saudi_gosi_total = 0.0
                    company_gosi_12_total = 0.0
                    company_gosi_22_total = 0.0
                    net_total = 0.0
                    sheet.write(row, col, 'Employee Tag', main_heading2)
                    sheet.write_string(row, col + 1, str(tag_id.name), main_heading)
                    sheet.write(row, col + 2, 'علامة الموظف', main_heading2)
                    row += 1
                    for employee_id in employee_ids:
                        if employee_id:
                            if tag_id.id in employee_id.category_ids.ids:
                                gross = 0.0
                                transport = 0.0
                                transport_300 = 0.0
                                transport_1500 = 0.0
                                house = 0.0
                                house_500 = 0.0
                                food_allowance = 0.0
                                work_nature_allowance = 0.0
                                fixed_add_allowance = 0.0
                                fixed_deduct_amount = 0.0
                                saudi_gosi_10 = 0.0
                                company_gosi_12 = 0.0
                                company_gosi_22 = 0.0
                                net = 0.0
                                gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                                transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                                transport300_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CA22')
                                transport1500_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CA23')
                                house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                                house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                                house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                                saudi_gosi_10_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'GOSI')
                                company_gosi_12_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CGOSI')
                                company_gosi_22_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FCGOSI')
                                net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                                food_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FA')
                                work_nature_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'NWA')
                                fixed_add_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FAA')
                                fixed_deduct_amount_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'DEDFIXD')
                                if gross_id:
                                    gross = gross_id.total
                                if transport_id:
                                    transport = transport_id.total
                                if transport300_id:
                                    transport_300 = transport300_id.total
                                if transport1500_id:
                                    transport_1500 = transport1500_id.total
                                if house_id:
                                    house = house_id.total
                                if house_id_1:
                                    house = house_id_1.total
                                if house500_id:
                                    house_500 = house500_id.total
                                if saudi_gosi_10_id:
                                    saudi_gosi_10 = saudi_gosi_10_id.total
                                if company_gosi_12_id:
                                    company_gosi_12 = company_gosi_12_id.total
                                if company_gosi_22_id:
                                    company_gosi_22 = company_gosi_22_id.total
                                if net_id:
                                    net = net_id.total
                                if food_allowance_id:
                                    food_allowance = food_allowance_id.total
                                if work_nature_allowance_id:
                                    work_nature_allowance = work_nature_allowance_id.total
                                if fixed_add_allowance_id:
                                    fixed_add_allowance = fixed_add_allowance_id.total
                                if fixed_deduct_amount_id:
                                    fixed_deduct_amount = fixed_deduct_amount_id.total
                                contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc',limit=1)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                if employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                if employee_id.name:
                                    sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                if employee_id.name_english:
                                    sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                if employee_id.parent_id.name:
                                    sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                                if employee_id.branch_id.region.bsg_region_name:
                                    sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                                       main_heading)
                                if employee_id.branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                                       main_heading)
                                if employee_id.department_id.display_name:
                                    sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                                       main_heading)
                                if employee_id.work_location:
                                    sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                                if employee_id.job_id.name:
                                    sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                                if employee_id.employee_state:
                                    sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                                if employee_id.suspend_salary:
                                    sheet.write_string(row, col + 11, str('True'), main_heading)
                                if employee_id.is_driver:
                                    sheet.write_string(row, col + 12, str('Driver'), main_heading)
                                if employee_id.guarantor_id.name:
                                    sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                                if employee_id.company_id.name:
                                    sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                                if employee_id.user_id.name:
                                    sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                                if employee_id.partner_id.name:
                                    sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                                if employee_id.country_id.name:
                                    sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                                if employee_id.country_id:
                                    if employee_id.country_id.code == 'SA':
                                        if employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if employee_id.bsg_bank_id.bsg_acc_number:
                                    sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                    sheet.write_string(row, col + 22,
                                                       str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                       main_heading)
                                if employee_id.salary_payment_method:
                                    sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_bank_name:
                                    sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                                       main_heading)
                                if employee_id.category_ids:
                                    rec_names = employee_id.category_ids.mapped('name')
                                    names = ','.join(rec_names)
                                    sheet.write_string(row, col + 25, str(names), main_heading)
                                if employee_id.birthday:
                                    sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                                if employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                                if employee_id.end_service_date:
                                    sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                                if employee_id.remaining_leaves:
                                    sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                                if employee_id.leave_start_date:
                                    sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                                if employee_id.gender:
                                    sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                                if contract_id.date_start:
                                    sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                                if contract_id.date_end:
                                    sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                                if contract_id.state:
                                    if contract_id.state == 'draft':
                                        sheet.write_string(row, col + 35, str("New"), main_heading)
                                    if contract_id.state == 'open':
                                        sheet.write_string(row, col + 35, str("Running"), main_heading)
                                    if contract_id.state == 'pending':
                                        sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                                    if contract_id.state == 'close':
                                        sheet.write_string(row, col + 35, str("Expired"), main_heading)
                                    if contract_id.state == 'cancel':
                                        sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                                if contract_id.analytic_account_id:
                                    sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                                       main_heading)
                                if employee_id.salary_structure.name:
                                    sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                                       main_heading)
                                if contract_id.wage:
                                    sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                                    print('wage=', contract_id.wage)
                                    wage_total += contract_id.wage
                                    print('wage total=', wage_total)
                                if transport:
                                    sheet.write_number(row, col + 39, transport, main_heading)
                                    transport_total += transport
                                if self.env.user.company_id.company_code == "BIC":
                                    if transport_300:
                                        sheet.write_number(row, col + 40, transport_300, main_heading)
                                        transport_300_total += transport_300
                                    if transport_1500:
                                        sheet.write_number(row, col + 41, transport_1500, main_heading)
                                        transport_1500_total += transport_1500
                                    if house:
                                        sheet.write_number(row, col + 42, house, main_heading)
                                        house_rent_total += house
                                    if house_500:
                                        sheet.write_number(row, col + 43, house_500, main_heading)
                                        house_500_total += house_500
                                    if food_allowance:
                                        sheet.write_number(row, col + 44, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 46, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 52, net, main_heading)
                                        net_total += net
                                else:
                                    if house:
                                        sheet.write_number(row, col + 40, house, main_heading)
                                        house_rent_total += house
                                    if food_allowance:
                                        sheet.write_number(row, col + 41, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 43, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 49, net, main_heading)
                                        net_total += net
                                row += 1
                                total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_number(row, col + 1, total, main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    sheet.write_number(row, col + 38, wage_total, main_heading)
                    sheet.write_number(row, col + 39, transport_total, main_heading)
                    if self.env.user.company_id.company_code == "BIC":
                        sheet.write_number(row, col + 40, transport_300_total, main_heading)
                        sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                        sheet.write_number(row, col + 42, house_rent_total, main_heading)
                        sheet.write_number(row, col + 43, house_500_total, main_heading)
                        sheet.write_number(row, col + 44, food_total, main_heading)
                        sheet.write_number(row, col + 45, work_nature_total, main_heading)
                        sheet.write_number(row, col + 46, gross_total, main_heading)
                        sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                        sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                        sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                        sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                        sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                        sheet.write_number(row, col + 52, net_total, main_heading)
                    else:
                        sheet.write_number(row, col + 40, house_rent_total, main_heading)
                        sheet.write_number(row, col + 41, food_total, main_heading)
                        sheet.write_number(row, col + 42, work_nature_total, main_heading)
                        sheet.write_number(row, col + 43, gross_total, main_heading)
                        sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                        sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                        sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                        sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                        sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                        sheet.write_number(row, col + 49, net_total, main_heading)
                    row += 1
                    grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 1, grand_total, main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_working_hours':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Working Hours"
            sheet.merge_range('A1:AE1', 'مجموعة تقرير معلومات راتب الموظف حسب ساعات العمل', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Working Hours', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Department', main_heading2)
            sheet.write(row, col + 8, 'Work Location', main_heading2)
            sheet.write(row, col + 9, 'Jop Position', main_heading2)
            sheet.write(row, col + 10, 'Employ Status', main_heading2)
            sheet.write(row, col + 11, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 12, 'Is Driver?', main_heading2)
            sheet.write(row, col + 13, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 14, 'Company Name', main_heading2)
            sheet.write(row, col + 15, 'User Name', main_heading2)
            sheet.write(row, col + 16, 'Partner Name', main_heading2)
            sheet.write(row, col + 17, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 18, 'Mobile No.', main_heading2)
            sheet.write(row, col + 19, 'Nationality', main_heading2)
            sheet.write(row, col + 20, 'ID No.', main_heading2)
            sheet.write(row, col + 21, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 22, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 23, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 24, 'Bank Name', main_heading2)
            sheet.write(row, col + 25, 'Tags', main_heading2)
            sheet.write(row, col + 26, 'Date of Birth', main_heading2)
            sheet.write(row, col + 27, 'Date of Join', main_heading2)
            sheet.write(row, col + 28, 'End Service Date', main_heading2)
            sheet.write(row, col + 29, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 30, 'leave start date', main_heading2)
            sheet.write(row, col + 31, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 32, 'Gender', main_heading2)
            sheet.write(row, col + 33, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 35, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 36, 'Analytic Account', main_heading2)
            sheet.write(row, col + 37, 'Salary Structure', main_heading2)
            sheet.write(row, col + 38, 'Wage', main_heading2)
            sheet.write(row, col + 39, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'Transport', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'House Rent', main_heading2)
                sheet.write(row, col + 44, 'Food', main_heading2)
                sheet.write(row, col + 45, 'Work Nature', main_heading2)
                sheet.write(row, col + 46, 'Gross', main_heading2)
                sheet.write(row, col + 47, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 48, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 40, 'House Rent', main_heading2)
                sheet.write(row, col + 41, 'Food', main_heading2)
                sheet.write(row, col + 42, 'Work Nature', main_heading2)
                sheet.write(row, col + 43, 'Gross', main_heading2)
                sheet.write(row, col + 44, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 45, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'الادارة', main_heading2)
            sheet.write(row, col + 8, 'مكان العمل', main_heading2)
            sheet.write(row, col + 9, 'الوظيفه', main_heading2)
            sheet.write(row, col + 10, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 11, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 12, 'سائق ؟', main_heading2)
            sheet.write(row, col + 13, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 14, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 15, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 16, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 17, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 18, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 19, 'الجنسية', main_heading2)
            sheet.write(row, col + 20, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 21, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 22, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 23, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 24, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 25, 'الوسم', main_heading2)
            sheet.write(row, col + 26, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 27, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 28, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 29, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 31, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 32, 'الجنس', main_heading2)
            sheet.write(row, col + 33, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 34, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 35, 'حالة العقد', main_heading2)
            sheet.write(row, col + 36, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 37, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 38, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 39, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 41, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن', main_heading2)
                sheet.write(row, col + 43, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 44, 'بدل طعام', main_heading2)
                sheet.write(row, col + 45, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 46, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 47, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 48, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 40, 'بدل سكن', main_heading2)
                sheet.write(row, col + 41, 'بدل طعام', main_heading2)
                sheet.write(row, col + 42, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 43, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 44, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 45, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'صافي الراتب', main_heading2)
            row += 1
            calendar_list = []
            grand_total = 0
            calendar_ids = self.env['resource.calendar'].search([])
            for calendar_id in calendar_ids:
                if calendar_id:
                    calendar_list.append(calendar_id.name)
            for calendar_name in calendar_list:
                if calendar_name:
                    calendar_employee_ids = employee_ids.filtered(lambda r: r.resource_calendar_id.name and r.resource_calendar_id.name == calendar_name)
                    if calendar_employee_ids:
                        total = 0
                        wage_total = 0.0
                        transport_total = 0.0
                        transport_300_total = 0.0
                        transport_1500_total = 0.0
                        house_rent_total = 0.0
                        house_500_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        sheet.write(row, col, 'Working Hours',main_heading2)
                        sheet.write_string(row, col + 1,str(calendar_name), main_heading)
                        sheet.write(row, col + 2, 'ساعات العمل',main_heading2)
                        row += 1
                        for employee_id in calendar_employee_ids:
                            if employee_id:
                                gross = 0.0
                                transport = 0.0
                                transport_300 = 0.0
                                transport_1500 = 0.0
                                house = 0.0
                                house_500 = 0.0
                                food_allowance = 0.0
                                work_nature_allowance = 0.0
                                fixed_add_allowance = 0.0
                                fixed_deduct_amount = 0.0
                                saudi_gosi_10 = 0.0
                                company_gosi_12 = 0.0
                                company_gosi_22 = 0.0
                                net = 0.0
                                gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                                transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                                transport300_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CA22')
                                transport1500_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CA23')
                                house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                                house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                                house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                                saudi_gosi_10_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'GOSI')
                                company_gosi_12_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CGOSI')
                                company_gosi_22_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FCGOSI')
                                net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                                food_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FA')
                                work_nature_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'NWA')
                                fixed_add_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FAA')
                                fixed_deduct_amount_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'DEDFIXD')
                                if gross_id:
                                    gross = gross_id.total
                                if transport_id:
                                    transport = transport_id.total
                                if transport300_id:
                                    transport_300 = transport300_id.total
                                if transport1500_id:
                                    transport_1500 = transport1500_id.total
                                if house_id:
                                    house = house_id.total
                                if house_id_1:
                                    house = house_id_1.total
                                if house500_id:
                                    house_500 = house500_id.total
                                if saudi_gosi_10_id:
                                    saudi_gosi_10 = saudi_gosi_10_id.total
                                if company_gosi_12_id:
                                    company_gosi_12 = company_gosi_12_id.total
                                if company_gosi_22_id:
                                    company_gosi_22 = company_gosi_22_id.total
                                if net_id:
                                    net = net_id.total
                                if food_allowance_id:
                                    food_allowance = food_allowance_id.total
                                if work_nature_allowance_id:
                                    work_nature_allowance = work_nature_allowance_id.total
                                if fixed_add_allowance_id:
                                    fixed_add_allowance = fixed_add_allowance_id.total
                                if fixed_deduct_amount_id:
                                    fixed_deduct_amount = fixed_deduct_amount_id.total
                                contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                if employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                if employee_id.name:
                                    sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                if employee_id.name_english:
                                    sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                if employee_id.parent_id.name:
                                    sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                                if employee_id.branch_id.region.bsg_region_name:
                                    sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                                       main_heading)
                                if employee_id.branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                                       main_heading)
                                if employee_id.department_id.display_name:
                                    sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                                       main_heading)
                                if employee_id.work_location:
                                    sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                                if employee_id.job_id.name:
                                    sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                                if employee_id.employee_state:
                                    sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                                if employee_id.suspend_salary:
                                    sheet.write_string(row, col + 11, str('True'), main_heading)
                                if employee_id.is_driver:
                                    sheet.write_string(row, col + 12, str('Driver'), main_heading)
                                if employee_id.guarantor_id.name:
                                    sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                                if employee_id.company_id.name:
                                    sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                                if employee_id.user_id.name:
                                    sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                                if employee_id.partner_id.name:
                                    sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                                if employee_id.country_id.name:
                                    sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                                if employee_id.country_id:
                                    if employee_id.country_id.code == 'SA':
                                        if employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if employee_id.bsg_bank_id.bsg_acc_number:
                                    sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                    sheet.write_string(row, col + 22,
                                                       str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                       main_heading)
                                if employee_id.salary_payment_method:
                                    sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_bank_name:
                                    sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                                       main_heading)
                                if employee_id.category_ids:
                                    rec_names = employee_id.category_ids.mapped('name')
                                    names = ','.join(rec_names)
                                    sheet.write_string(row, col + 25, str(names), main_heading)
                                if employee_id.birthday:
                                    sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                                if employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                                if employee_id.end_service_date:
                                    sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                                if employee_id.remaining_leaves:
                                    sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                                if employee_id.leave_start_date:
                                    sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                                if employee_id.gender:
                                    sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                                if contract_id.date_start:
                                    sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                                if contract_id.date_end:
                                    sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                                if contract_id.state:
                                    if contract_id.state == 'draft':
                                        sheet.write_string(row, col + 35, str("New"), main_heading)
                                    if contract_id.state == 'open':
                                        sheet.write_string(row, col + 35, str("Running"), main_heading)
                                    if contract_id.state == 'pending':
                                        sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                                    if contract_id.state == 'close':
                                        sheet.write_string(row, col + 35, str("Expired"), main_heading)
                                    if contract_id.state == 'cancel':
                                        sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                                if contract_id.analytic_account_id:
                                    sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                                       main_heading)
                                if employee_id.salary_structure.name:
                                    sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                                       main_heading)
                                if contract_id.wage:
                                    sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                                    print('wage=', contract_id.wage)
                                    wage_total += contract_id.wage
                                    print('wage total=', wage_total)
                                if transport:
                                    sheet.write_number(row, col + 39, transport, main_heading)
                                    transport_total += transport
                                if self.env.user.company_id.company_code == "BIC":
                                    if transport_300:
                                        sheet.write_number(row, col + 40, transport_300, main_heading)
                                        transport_300_total += transport_300
                                    if transport_1500:
                                        sheet.write_number(row, col + 41, transport_1500, main_heading)
                                        transport_1500_total += transport_1500
                                    if house:
                                        sheet.write_number(row, col + 42, house, main_heading)
                                        house_rent_total += house
                                    if house_500:
                                        sheet.write_number(row, col + 43, house_500, main_heading)
                                        house_500_total += house_500
                                    if food_allowance:
                                        sheet.write_number(row, col + 44, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 46, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 52, net, main_heading)
                                        net_total += net
                                else:
                                    if house:
                                        sheet.write_number(row, col + 40, house, main_heading)
                                        house_rent_total += house
                                    if food_allowance:
                                        sheet.write_number(row, col + 41, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 43, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 49, net, main_heading)
                                        net_total += net
                                row += 1
                                total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_number(row, col + 1, total, main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        sheet.write_number(row, col + 38, wage_total, main_heading)
                        sheet.write_number(row, col + 39, transport_total, main_heading)
                        if self.env.user.company_id.company_code == "BIC":
                            sheet.write_number(row, col + 40, transport_300_total, main_heading)
                            sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                            sheet.write_number(row, col + 42, house_rent_total, main_heading)
                            sheet.write_number(row, col + 43, house_500_total, main_heading)
                            sheet.write_number(row, col + 44, food_total, main_heading)
                            sheet.write_number(row, col + 45, work_nature_total, main_heading)
                            sheet.write_number(row, col + 46, gross_total, main_heading)
                            sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 52, net_total, main_heading)
                        else:
                            sheet.write_number(row, col + 40, house_rent_total, main_heading)
                            sheet.write_number(row, col + 41, food_total, main_heading)
                            sheet.write_number(row, col + 42, work_nature_total, main_heading)
                            sheet.write_number(row, col + 43, gross_total, main_heading)
                            sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 49, net_total, main_heading)
                        row += 1
                        grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 1, grand_total, main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_religion':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Religion"
            sheet.merge_range('A1:AE1', 'تقرير معلومات رواتب الموظف مجموعة حسب الدين', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Religion', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Department', main_heading2)
            sheet.write(row, col + 8, 'Work Location', main_heading2)
            sheet.write(row, col + 9, 'Jop Position', main_heading2)
            sheet.write(row, col + 10, 'Employ Status', main_heading2)
            sheet.write(row, col + 11, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 12, 'Is Driver?', main_heading2)
            sheet.write(row, col + 13, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 14, 'Company Name', main_heading2)
            sheet.write(row, col + 15, 'User Name', main_heading2)
            sheet.write(row, col + 16, 'Partner Name', main_heading2)
            sheet.write(row, col + 17, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 18, 'Mobile No.', main_heading2)
            sheet.write(row, col + 19, 'Nationality', main_heading2)
            sheet.write(row, col + 20, 'ID No.', main_heading2)
            sheet.write(row, col + 21, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 22, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 23, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 24, 'Bank Name', main_heading2)
            sheet.write(row, col + 25, 'Tags', main_heading2)
            sheet.write(row, col + 26, 'Date of Birth', main_heading2)
            sheet.write(row, col + 27, 'Date of Join', main_heading2)
            sheet.write(row, col + 28, 'End Service Date', main_heading2)
            sheet.write(row, col + 29, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 30, 'leave start date', main_heading2)
            sheet.write(row, col + 31, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 32, 'Gender', main_heading2)
            sheet.write(row, col + 33, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 35, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 36, 'Analytic Account', main_heading2)
            sheet.write(row, col + 37, 'Salary Structure', main_heading2)
            sheet.write(row, col + 38, 'Wage', main_heading2)
            sheet.write(row, col + 39, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'Transport', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'House Rent', main_heading2)
                sheet.write(row, col + 44, 'Food', main_heading2)
                sheet.write(row, col + 45, 'Work Nature', main_heading2)
                sheet.write(row, col + 46, 'Gross', main_heading2)
                sheet.write(row, col + 47, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 48, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 40, 'House Rent', main_heading2)
                sheet.write(row, col + 41, 'Food', main_heading2)
                sheet.write(row, col + 42, 'Work Nature', main_heading2)
                sheet.write(row, col + 43, 'Gross', main_heading2)
                sheet.write(row, col + 44, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 45, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'الادارة', main_heading2)
            sheet.write(row, col + 8, 'مكان العمل', main_heading2)
            sheet.write(row, col + 9, 'الوظيفه', main_heading2)
            sheet.write(row, col + 10, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 11, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 12, 'سائق ؟', main_heading2)
            sheet.write(row, col + 13, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 14, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 15, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 16, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 17, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 18, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 19, 'الجنسية', main_heading2)
            sheet.write(row, col + 20, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 21, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 22, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 23, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 24, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 25, 'الوسم', main_heading2)
            sheet.write(row, col + 26, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 27, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 28, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 29, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 31, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 32, 'الجنس', main_heading2)
            sheet.write(row, col + 33, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 34, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 35, 'حالة العقد', main_heading2)
            sheet.write(row, col + 36, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 37, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 38, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 39, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 41, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن', main_heading2)
                sheet.write(row, col + 43, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 44, 'بدل طعام', main_heading2)
                sheet.write(row, col + 45, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 46, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 47, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 48, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 40, 'بدل سكن', main_heading2)
                sheet.write(row, col + 41, 'بدل طعام', main_heading2)
                sheet.write(row, col + 42, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 43, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 44, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 45, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'صافي الراتب', main_heading2)
            row += 1
            religion_list = []
            grand_total = 0
            religion_ids = self.env['hr.employee.religion'].search([])
            for religion_id in religion_ids:
                if religion_id:
                    religion_list.append(religion_id.religion_name)
            for religion_name in religion_list:
                if religion_name:
                    religion_employee_ids = employee_ids.filtered(lambda r: r.bsg_religion_id.religion_name and r.bsg_religion_id.religion_name == religion_name)
                    if religion_employee_ids:
                        total = 0
                        wage_total = 0.0
                        transport_total = 0.0
                        transport_300_total = 0.0
                        transport_1500_total = 0.0
                        house_rent_total = 0.0
                        house_500_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        sheet.write(row, col, 'Religion', main_heading2)
                        sheet.write_string(row, col + 1, str(religion_name), main_heading)
                        sheet.write(row, col + 2, 'دين', main_heading2)
                        row += 1
                        for employee_id in religion_employee_ids:
                            if employee_id:
                                gross = 0.0
                                transport = 0.0
                                transport_300 = 0.0
                                transport_1500 = 0.0
                                house = 0.0
                                house_500 = 0.0
                                food_allowance = 0.0
                                work_nature_allowance = 0.0
                                fixed_add_allowance = 0.0
                                fixed_deduct_amount = 0.0
                                saudi_gosi_10 = 0.0
                                company_gosi_12 = 0.0
                                company_gosi_22 = 0.0
                                net = 0.0
                                gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                                transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                                transport300_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CA22')
                                transport1500_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CA23')
                                house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                                house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                                house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                                saudi_gosi_10_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'GOSI')
                                company_gosi_12_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CGOSI')
                                company_gosi_22_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FCGOSI')
                                net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                                food_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FA')
                                work_nature_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'NWA')
                                fixed_add_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FAA')
                                fixed_deduct_amount_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'DEDFIXD')
                                if gross_id:
                                    gross = gross_id.total
                                if transport_id:
                                    transport = transport_id.total
                                if transport300_id:
                                    transport_300 = transport300_id.total
                                if transport1500_id:
                                    transport_1500 = transport1500_id.total
                                if house_id:
                                    house = house_id.total
                                if house_id_1:
                                    house = house_id_1.total
                                if house500_id:
                                    house_500 = house500_id.total
                                if saudi_gosi_10_id:
                                    saudi_gosi_10 = saudi_gosi_10_id.total
                                if company_gosi_12_id:
                                    company_gosi_12 = company_gosi_12_id.total
                                if company_gosi_22_id:
                                    company_gosi_22 = company_gosi_22_id.total
                                if net_id:
                                    net = net_id.total
                                if food_allowance_id:
                                    food_allowance = food_allowance_id.total
                                if work_nature_allowance_id:
                                    work_nature_allowance = work_nature_allowance_id.total
                                if fixed_add_allowance_id:
                                    fixed_add_allowance = fixed_add_allowance_id.total
                                if fixed_deduct_amount_id:
                                    fixed_deduct_amount = fixed_deduct_amount_id.total
                                contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                if employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                if employee_id.name:
                                    sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                if employee_id.name_english:
                                    sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                if employee_id.parent_id.name:
                                    sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                                if employee_id.branch_id.region.bsg_region_name:
                                    sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                                       main_heading)
                                if employee_id.branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                                       main_heading)
                                if employee_id.department_id.display_name:
                                    sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                                       main_heading)
                                if employee_id.work_location:
                                    sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                                if employee_id.job_id.name:
                                    sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                                if employee_id.employee_state:
                                    sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                                if employee_id.suspend_salary:
                                    sheet.write_string(row, col + 11, str('True'), main_heading)
                                if employee_id.is_driver:
                                    sheet.write_string(row, col + 12, str('Driver'), main_heading)
                                if employee_id.guarantor_id.name:
                                    sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                                if employee_id.company_id.name:
                                    sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                                if employee_id.user_id.name:
                                    sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                                if employee_id.partner_id.name:
                                    sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                                if employee_id.country_id.name:
                                    sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                                if employee_id.country_id:
                                    if employee_id.country_id.code == 'SA':
                                        if employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if employee_id.bsg_bank_id.bsg_acc_number:
                                    sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                    sheet.write_string(row, col + 22,
                                                       str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                       main_heading)
                                if employee_id.salary_payment_method:
                                    sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_bank_name:
                                    sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                                       main_heading)
                                if employee_id.category_ids:
                                    rec_names = employee_id.category_ids.mapped('name')
                                    names = ','.join(rec_names)
                                    sheet.write_string(row, col + 25, str(names), main_heading)
                                if employee_id.birthday:
                                    sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                                if employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                                if employee_id.end_service_date:
                                    sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                                if employee_id.remaining_leaves:
                                    sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                                if employee_id.leave_start_date:
                                    sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                                if employee_id.gender:
                                    sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                                if contract_id.date_start:
                                    sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                                if contract_id.date_end:
                                    sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                                if contract_id.state:
                                    if contract_id.state == 'draft':
                                        sheet.write_string(row, col + 35, str("New"), main_heading)
                                    if contract_id.state == 'open':
                                        sheet.write_string(row, col + 35, str("Running"), main_heading)
                                    if contract_id.state == 'pending':
                                        sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                                    if contract_id.state == 'close':
                                        sheet.write_string(row, col + 35, str("Expired"), main_heading)
                                    if contract_id.state == 'cancel':
                                        sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                                if contract_id.analytic_account_id:
                                    sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                                       main_heading)
                                if employee_id.salary_structure.name:
                                    sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                                       main_heading)
                                if contract_id.wage:
                                    sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                                    print('wage=', contract_id.wage)
                                    wage_total += contract_id.wage
                                    print('wage total=', wage_total)
                                if transport:
                                    sheet.write_number(row, col + 39, transport, main_heading)
                                    transport_total += transport
                                if self.env.user.company_id.company_code == "BIC":
                                    if transport_300:
                                        sheet.write_number(row, col + 40, transport_300, main_heading)
                                        transport_300_total += transport_300
                                    if transport_1500:
                                        sheet.write_number(row, col + 41, transport_1500, main_heading)
                                        transport_1500_total += transport_1500
                                    if house:
                                        sheet.write_number(row, col + 42, house, main_heading)
                                        house_rent_total += house
                                    if house_500:
                                        sheet.write_number(row, col + 43, house_500, main_heading)
                                        house_500_total += house_500
                                    if food_allowance:
                                        sheet.write_number(row, col + 44, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 46, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 52, net, main_heading)
                                        net_total += net
                                else:
                                    if house:
                                        sheet.write_number(row, col + 40, house, main_heading)
                                        house_rent_total += house
                                    if food_allowance:
                                        sheet.write_number(row, col + 41, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 43, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 49, net, main_heading)
                                        net_total += net
                                row += 1
                                total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_number(row, col + 1, total, main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        sheet.write_number(row, col + 38, wage_total, main_heading)
                        sheet.write_number(row, col + 39, transport_total, main_heading)
                        if self.env.user.company_id.company_code == "BIC":
                            sheet.write_number(row, col + 40, transport_300_total, main_heading)
                            sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                            sheet.write_number(row, col + 42, house_rent_total, main_heading)
                            sheet.write_number(row, col + 43, house_500_total, main_heading)
                            sheet.write_number(row, col + 44, food_total, main_heading)
                            sheet.write_number(row, col + 45, work_nature_total, main_heading)
                            sheet.write_number(row, col + 46, gross_total, main_heading)
                            sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 52, net_total, main_heading)
                        else:
                            sheet.write_number(row, col + 40, house_rent_total, main_heading)
                            sheet.write_number(row, col + 41, food_total, main_heading)
                            sheet.write_number(row, col + 42, work_nature_total, main_heading)
                            sheet.write_number(row, col + 43, gross_total, main_heading)
                            sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 49, net_total, main_heading)
                        row += 1
                        grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 1, grand_total, main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_emp_status':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Employee Status"
            sheet.merge_range('A1:AE1', 'تقرير معلومات راتب الموظف مجموعة حسب حالة الموظف', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Employee Status', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Department', main_heading2)
            sheet.write(row, col + 8, 'Work Location', main_heading2)
            sheet.write(row, col + 9, 'Jop Position', main_heading2)
            sheet.write(row, col + 10, 'Employ Status', main_heading2)
            sheet.write(row, col + 11, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 12, 'Is Driver?', main_heading2)
            sheet.write(row, col + 13, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 14, 'Company Name', main_heading2)
            sheet.write(row, col + 15, 'User Name', main_heading2)
            sheet.write(row, col + 16, 'Partner Name', main_heading2)
            sheet.write(row, col + 17, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 18, 'Mobile No.', main_heading2)
            sheet.write(row, col + 19, 'Nationality', main_heading2)
            sheet.write(row, col + 20, 'ID No.', main_heading2)
            sheet.write(row, col + 21, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 22, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 23, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 24, 'Bank Name', main_heading2)
            sheet.write(row, col + 25, 'Tags', main_heading2)
            sheet.write(row, col + 26, 'Date of Birth', main_heading2)
            sheet.write(row, col + 27, 'Date of Join', main_heading2)
            sheet.write(row, col + 28, 'End Service Date', main_heading2)
            sheet.write(row, col + 29, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 30, 'leave start date', main_heading2)
            sheet.write(row, col + 31, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 32, 'Gender', main_heading2)
            sheet.write(row, col + 33, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 35, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 36, 'Analytic Account', main_heading2)
            sheet.write(row, col + 37, 'Salary Structure', main_heading2)
            sheet.write(row, col + 38, 'Wage', main_heading2)
            sheet.write(row, col + 39, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'Transport', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'House Rent', main_heading2)
                sheet.write(row, col + 44, 'Food', main_heading2)
                sheet.write(row, col + 45, 'Work Nature', main_heading2)
                sheet.write(row, col + 46, 'Gross', main_heading2)
                sheet.write(row, col + 47, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 48, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 40, 'House Rent', main_heading2)
                sheet.write(row, col + 41, 'Food', main_heading2)
                sheet.write(row, col + 42, 'Work Nature', main_heading2)
                sheet.write(row, col + 43, 'Gross', main_heading2)
                sheet.write(row, col + 44, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 45, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'الادارة', main_heading2)
            sheet.write(row, col + 8, 'مكان العمل', main_heading2)
            sheet.write(row, col + 9, 'الوظيفه', main_heading2)
            sheet.write(row, col + 10, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 11, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 12, 'سائق ؟', main_heading2)
            sheet.write(row, col + 13, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 14, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 15, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 16, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 17, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 18, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 19, 'الجنسية', main_heading2)
            sheet.write(row, col + 20, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 21, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 22, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 23, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 24, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 25, 'الوسم', main_heading2)
            sheet.write(row, col + 26, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 27, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 28, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 29, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 31, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 32, 'الجنس', main_heading2)
            sheet.write(row, col + 33, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 34, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 35, 'حالة العقد', main_heading2)
            sheet.write(row, col + 36, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 37, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 38, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 39, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 41, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن', main_heading2)
                sheet.write(row, col + 43, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 44, 'بدل طعام', main_heading2)
                sheet.write(row, col + 45, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 46, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 47, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 48, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 40, 'بدل سكن', main_heading2)
                sheet.write(row, col + 41, 'بدل طعام', main_heading2)
                sheet.write(row, col + 42, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 43, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 44, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 45, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'صافي الراتب', main_heading2)
            row += 1
            grand_total = 0
            job_employee_ids = employee_ids.filtered(lambda r: r.employee_state == 'on_job')
            leave_employee_ids = employee_ids.filtered(lambda r: r.employee_state == 'on_leave')
            return_employee_ids = employee_ids.filtered(lambda r: r.employee_state == 'return_from_holiday')
            resig_employee_ids = employee_ids.filtered(lambda r: r.employee_state == 'resignation')
            suspend_employee_ids = employee_ids.filtered(lambda r: r.employee_state == 'suspended')
            expire_employee_ids = employee_ids.filtered(lambda r: r.employee_state == 'service_expired')
            terminate_employee_ids = employee_ids.filtered(lambda r: r.employee_state == 'contract_terminated')
            contract_end_employee_ids = employee_ids.filtered(lambda r: r.employee_state == 'ending_contract_during_trial_period')
            if job_employee_ids:
                total = 0
                wage_total = 0.0
                transport_total = 0.0
                transport_300_total = 0.0
                transport_1500_total = 0.0
                house_rent_total = 0.0
                house_500_total = 0.0
                food_total = 0.0
                work_nature_total = 0.0
                gross_total = 0.0
                fixed_additional_total = 0.0
                fixed_deduction_total = 0.0
                saudi_gosi_total = 0.0
                company_gosi_12_total = 0.0
                company_gosi_22_total = 0.0
                net_total = 0.0
                sheet.write(row, col, 'Employee Status', main_heading2)
                sheet.write_string(row, col + 1, str('On Job'), main_heading)
                sheet.write(row, col + 2, 'حالة الموظف', main_heading2)
                row += 1
                for employee_id in job_employee_ids:
                    if employee_id:
                        gross = 0.0
                        transport = 0.0
                        transport_300 = 0.0
                        transport_1500 = 0.0
                        house = 0.0
                        house_500 = 0.0
                        food_allowance = 0.0
                        work_nature_allowance = 0.0
                        fixed_add_allowance = 0.0
                        fixed_deduct_amount = 0.0
                        saudi_gosi_10 = 0.0
                        company_gosi_12 = 0.0
                        company_gosi_22 = 0.0
                        net = 0.0
                        gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                        transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                        transport300_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA22')
                        transport1500_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA23')
                        house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                        house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                        house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                        saudi_gosi_10_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'GOSI')
                        company_gosi_12_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CGOSI')
                        company_gosi_22_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FCGOSI')
                        net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                        food_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FA')
                        work_nature_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'NWA')
                        fixed_add_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FAA')
                        fixed_deduct_amount_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'DEDFIXD')
                        if gross_id:
                            gross = gross_id.total
                        if transport_id:
                            transport = transport_id.total
                        if transport300_id:
                            transport_300 = transport300_id.total
                        if transport1500_id:
                            transport_1500 = transport1500_id.total
                        if house_id:
                            house = house_id.total
                        if house_id_1:
                            house = house_id_1.total
                        if house500_id:
                            house_500 = house500_id.total
                        if saudi_gosi_10_id:
                            saudi_gosi_10 = saudi_gosi_10_id.total
                        if company_gosi_12_id:
                            company_gosi_12 = company_gosi_12_id.total
                        if company_gosi_22_id:
                            company_gosi_22 = company_gosi_22_id.total
                        if net_id:
                            net = net_id.total
                        if food_allowance_id:
                            food_allowance = food_allowance_id.total
                        if work_nature_allowance_id:
                            work_nature_allowance = work_nature_allowance_id.total
                        if fixed_add_allowance_id:
                            fixed_add_allowance = fixed_add_allowance_id.total
                        if fixed_deduct_amount_id:
                            fixed_deduct_amount = fixed_deduct_amount_id.total
                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                        if employee_id.driver_code:
                            sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                        if employee_id.employee_code:
                            sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                        if employee_id.name:
                            sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                        if employee_id.name_english:
                            sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                        if employee_id.parent_id.name:
                            sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                        if employee_id.branch_id.region.bsg_region_name:
                            sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                               main_heading)
                        if employee_id.branch_id.branch_ar_name:
                            sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                               main_heading)
                        if employee_id.department_id.display_name:
                            sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                               main_heading)
                        if employee_id.work_location:
                            sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                        if employee_id.job_id.name:
                            sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                        if employee_id.employee_state:
                            sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                        if employee_id.suspend_salary:
                            sheet.write_string(row, col + 11, str('True'), main_heading)
                        if employee_id.is_driver:
                            sheet.write_string(row, col + 12, str('Driver'), main_heading)
                        if employee_id.guarantor_id.name:
                            sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                        if employee_id.company_id.name:
                            sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                        if employee_id.user_id.name:
                            sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                        if employee_id.partner_id.name:
                            sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                        if employee_id.mobile_phone:
                            sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                        if employee_id.country_id.name:
                            sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                        if employee_id.country_id:
                            if employee_id.country_id.code == 'SA':
                                if employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_national_id.bsg_nationality_name),
                                                       main_heading)
                            else:
                                if employee_id.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                        if employee_id.bsg_bank_id.bsg_acc_number:
                            sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                            sheet.write_string(row, col + 22,
                                               str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                               main_heading)
                        if employee_id.salary_payment_method:
                            sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_bank_name:
                            sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                               main_heading)
                        if employee_id.category_ids:
                            rec_names = employee_id.category_ids.mapped('name')
                            names = ','.join(rec_names)
                            sheet.write_string(row, col + 25, str(names), main_heading)
                        if employee_id.birthday:
                            sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                        if employee_id.bsgjoining_date:
                            sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                        if employee_id.end_service_date:
                            sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                        if employee_id.remaining_leaves:
                            sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                        if employee_id.leave_start_date:
                            sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                        if employee_id.gender:
                            sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                        if contract_id.date_start:
                            sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                        if contract_id.date_end:
                            sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                        if contract_id.state:
                            if contract_id.state == 'draft':
                                sheet.write_string(row, col + 35, str("New"), main_heading)
                            if contract_id.state == 'open':
                                sheet.write_string(row, col + 35, str("Running"), main_heading)
                            if contract_id.state == 'pending':
                                sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                            if contract_id.state == 'close':
                                sheet.write_string(row, col + 35, str("Expired"), main_heading)
                            if contract_id.state == 'cancel':
                                sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                        if contract_id.analytic_account_id:
                            sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                               main_heading)
                        if employee_id.salary_structure.name:
                            sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                               main_heading)
                        if contract_id.wage:
                            sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                            print('wage=', contract_id.wage)
                            wage_total += contract_id.wage
                            print('wage total=', wage_total)
                        if transport:
                            sheet.write_number(row, col + 39, transport, main_heading)
                            transport_total += transport
                        if self.env.user.company_id.company_code == "BIC":
                            if transport_300:
                                sheet.write_number(row, col + 40, transport_300, main_heading)
                                transport_300_total += transport_300
                            if transport_1500:
                                sheet.write_number(row, col + 41, transport_1500, main_heading)
                                transport_1500_total += transport_1500
                            if house:
                                sheet.write_number(row, col + 42, house, main_heading)
                                house_rent_total += house
                            if house_500:
                                sheet.write_number(row, col + 43, house_500, main_heading)
                                house_500_total += house_500
                            if food_allowance:
                                sheet.write_number(row, col + 44, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 46, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 52, net, main_heading)
                                net_total += net
                        else:
                            if house:
                                sheet.write_number(row, col + 40, house, main_heading)
                                house_rent_total += house
                            if food_allowance:
                                sheet.write_number(row, col + 41, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 43, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 49, net, main_heading)
                                net_total += net
                        row += 1
                        total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 1, total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                sheet.write_number(row, col + 38, wage_total, main_heading)
                sheet.write_number(row, col + 39, transport_total, main_heading)
                if self.env.user.company_id.company_code == "BIC":
                    sheet.write_number(row, col + 40, transport_300_total, main_heading)
                    sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                    sheet.write_number(row, col + 42, house_rent_total, main_heading)
                    sheet.write_number(row, col + 43, house_500_total, main_heading)
                    sheet.write_number(row, col + 44, food_total, main_heading)
                    sheet.write_number(row, col + 45, work_nature_total, main_heading)
                    sheet.write_number(row, col + 46, gross_total, main_heading)
                    sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 52, net_total, main_heading)
                else:
                    sheet.write_number(row, col + 40, house_rent_total, main_heading)
                    sheet.write_number(row, col + 41, food_total, main_heading)
                    sheet.write_number(row, col + 42, work_nature_total, main_heading)
                    sheet.write_number(row, col + 43, gross_total, main_heading)
                    sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 49, net_total, main_heading)
                row += 1
                grand_total += total
            if leave_employee_ids:
                total = 0
                wage_total = 0.0
                transport_total = 0.0
                transport_300_total = 0.0
                transport_1500_total = 0.0
                house_rent_total = 0.0
                house_500_total = 0.0
                food_total = 0.0
                work_nature_total = 0.0
                gross_total = 0.0
                fixed_additional_total = 0.0
                fixed_deduction_total = 0.0
                saudi_gosi_total = 0.0
                company_gosi_12_total = 0.0
                company_gosi_22_total = 0.0
                net_total = 0.0
                sheet.write(row, col, 'Employee Status', main_heading2)
                sheet.write_string(row, col + 1, str('On Leave'), main_heading)
                sheet.write(row, col + 2, 'حالة الموظف', main_heading2)
                row += 1
                for employee_id in leave_employee_ids:
                    if employee_id:
                        gross = 0.0
                        transport = 0.0
                        transport_300 = 0.0
                        transport_1500 = 0.0
                        house = 0.0
                        house_500 = 0.0
                        food_allowance = 0.0
                        work_nature_allowance = 0.0
                        fixed_add_allowance = 0.0
                        fixed_deduct_amount = 0.0
                        saudi_gosi_10 = 0.0
                        company_gosi_12 = 0.0
                        company_gosi_22 = 0.0
                        net = 0.0
                        gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                        transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                        transport300_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA22')
                        transport1500_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA23')
                        house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                        house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                        house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                        saudi_gosi_10_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'GOSI')
                        company_gosi_12_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CGOSI')
                        company_gosi_22_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FCGOSI')
                        net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                        food_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FA')
                        work_nature_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'NWA')
                        fixed_add_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FAA')
                        fixed_deduct_amount_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'DEDFIXD')
                        if gross_id:
                            gross = gross_id.total
                        if transport_id:
                            transport = transport_id.total
                        if transport300_id:
                            transport_300 = transport300_id.total
                        if transport1500_id:
                            transport_1500 = transport1500_id.total
                        if house_id:
                            house = house_id.total
                        if house_id_1:
                            house = house_id_1.total
                        if house500_id:
                            house_500 = house500_id.total
                        if saudi_gosi_10_id:
                            saudi_gosi_10 = saudi_gosi_10_id.total
                        if company_gosi_12_id:
                            company_gosi_12 = company_gosi_12_id.total
                        if company_gosi_22_id:
                            company_gosi_22 = company_gosi_22_id.total
                        if net_id:
                            net = net_id.total
                        if food_allowance_id:
                            food_allowance = food_allowance_id.total
                        if work_nature_allowance_id:
                            work_nature_allowance = work_nature_allowance_id.total
                        if fixed_add_allowance_id:
                            fixed_add_allowance = fixed_add_allowance_id.total
                        if fixed_deduct_amount_id:
                            fixed_deduct_amount = fixed_deduct_amount_id.total
                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                        if employee_id.driver_code:
                            sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                        if employee_id.employee_code:
                            sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                        if employee_id.name:
                            sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                        if employee_id.name_english:
                            sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                        if employee_id.parent_id.name:
                            sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                        if employee_id.branch_id.region.bsg_region_name:
                            sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                               main_heading)
                        if employee_id.branch_id.branch_ar_name:
                            sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                               main_heading)
                        if employee_id.department_id.display_name:
                            sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                               main_heading)
                        if employee_id.work_location:
                            sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                        if employee_id.job_id.name:
                            sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                        if employee_id.employee_state:
                            sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                        if employee_id.suspend_salary:
                            sheet.write_string(row, col + 11, str('True'), main_heading)
                        if employee_id.is_driver:
                            sheet.write_string(row, col + 12, str('Driver'), main_heading)
                        if employee_id.guarantor_id.name:
                            sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                        if employee_id.company_id.name:
                            sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                        if employee_id.user_id.name:
                            sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                        if employee_id.partner_id.name:
                            sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                        if employee_id.mobile_phone:
                            sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                        if employee_id.country_id.name:
                            sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                        if employee_id.country_id:
                            if employee_id.country_id.code == 'SA':
                                if employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_national_id.bsg_nationality_name),
                                                       main_heading)
                            else:
                                if employee_id.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                        if employee_id.bsg_bank_id.bsg_acc_number:
                            sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                            sheet.write_string(row, col + 22,
                                               str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                               main_heading)
                        if employee_id.salary_payment_method:
                            sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_bank_name:
                            sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                               main_heading)
                        if employee_id.category_ids:
                            rec_names = employee_id.category_ids.mapped('name')
                            names = ','.join(rec_names)
                            sheet.write_string(row, col + 25, str(names), main_heading)
                        if employee_id.birthday:
                            sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                        if employee_id.bsgjoining_date:
                            sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                        if employee_id.end_service_date:
                            sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                        if employee_id.remaining_leaves:
                            sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                        if employee_id.leave_start_date:
                            sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                        if employee_id.gender:
                            sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                        if contract_id.date_start:
                            sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                        if contract_id.date_end:
                            sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                        if contract_id.state:
                            if contract_id.state == 'draft':
                                sheet.write_string(row, col + 35, str("New"), main_heading)
                            if contract_id.state == 'open':
                                sheet.write_string(row, col + 35, str("Running"), main_heading)
                            if contract_id.state == 'pending':
                                sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                            if contract_id.state == 'close':
                                sheet.write_string(row, col + 35, str("Expired"), main_heading)
                            if contract_id.state == 'cancel':
                                sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                        if contract_id.analytic_account_id:
                            sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                               main_heading)
                        if employee_id.salary_structure.name:
                            sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                               main_heading)
                        if contract_id.wage:
                            sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                            print('wage=', contract_id.wage)
                            wage_total += contract_id.wage
                            print('wage total=', wage_total)
                        if transport:
                            sheet.write_number(row, col + 39, transport, main_heading)
                            transport_total += transport
                        if self.env.user.company_id.company_code == "BIC":
                            if transport_300:
                                sheet.write_number(row, col + 40, transport_300, main_heading)
                                transport_300_total += transport_300
                            if transport_1500:
                                sheet.write_number(row, col + 41, transport_1500, main_heading)
                                transport_1500_total += transport_1500
                            if house:
                                sheet.write_number(row, col + 42, house, main_heading)
                                house_rent_total += house
                            if house_500:
                                sheet.write_number(row, col + 43, house_500, main_heading)
                                house_500_total += house_500
                            if food_allowance:
                                sheet.write_number(row, col + 44, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 46, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 52, net, main_heading)
                                net_total += net
                        else:
                            if house:
                                sheet.write_number(row, col + 40, house, main_heading)
                                house_rent_total += house
                            if food_allowance:
                                sheet.write_number(row, col + 41, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 43, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 49, net, main_heading)
                                net_total += net
                        row += 1
                        total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 1, total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                sheet.write_number(row, col + 38, wage_total, main_heading)
                sheet.write_number(row, col + 39, transport_total, main_heading)
                if self.env.user.company_id.company_code == "BIC":
                    sheet.write_number(row, col + 40, transport_300_total, main_heading)
                    sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                    sheet.write_number(row, col + 42, house_rent_total, main_heading)
                    sheet.write_number(row, col + 43, house_500_total, main_heading)
                    sheet.write_number(row, col + 44, food_total, main_heading)
                    sheet.write_number(row, col + 45, work_nature_total, main_heading)
                    sheet.write_number(row, col + 46, gross_total, main_heading)
                    sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 52, net_total, main_heading)
                else:
                    sheet.write_number(row, col + 40, house_rent_total, main_heading)
                    sheet.write_number(row, col + 41, food_total, main_heading)
                    sheet.write_number(row, col + 42, work_nature_total, main_heading)
                    sheet.write_number(row, col + 43, gross_total, main_heading)
                    sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 49, net_total, main_heading)
                row += 1
                grand_total += total
            if return_employee_ids:
                total = 0
                wage_total = 0.0
                transport_total = 0.0
                transport_300_total = 0.0
                transport_1500_total = 0.0
                house_rent_total = 0.0
                house_500_total = 0.0
                food_total = 0.0
                work_nature_total = 0.0
                gross_total = 0.0
                fixed_additional_total = 0.0
                fixed_deduction_total = 0.0
                saudi_gosi_total = 0.0
                company_gosi_12_total = 0.0
                company_gosi_22_total = 0.0
                net_total = 0.0
                sheet.write(row, col, 'Employee Status', main_heading2)
                sheet.write_string(row, col + 1, str('Return From Holiday'), main_heading)
                sheet.write(row, col + 2, 'حالة الموظف', main_heading2)
                row += 1
                for employee_id in return_employee_ids:
                    if employee_id:
                        gross = 0.0
                        transport = 0.0
                        transport_300 = 0.0
                        transport_1500 = 0.0
                        house = 0.0
                        house_500 = 0.0
                        food_allowance = 0.0
                        work_nature_allowance = 0.0
                        fixed_add_allowance = 0.0
                        fixed_deduct_amount = 0.0
                        saudi_gosi_10 = 0.0
                        company_gosi_12 = 0.0
                        company_gosi_22 = 0.0
                        net = 0.0
                        gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                        transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                        transport300_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA22')
                        transport1500_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA23')
                        house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                        house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                        house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                        saudi_gosi_10_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'GOSI')
                        company_gosi_12_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CGOSI')
                        company_gosi_22_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FCGOSI')
                        net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                        food_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FA')
                        work_nature_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'NWA')
                        fixed_add_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FAA')
                        fixed_deduct_amount_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'DEDFIXD')
                        if gross_id:
                            gross = gross_id.total
                        if transport_id:
                            transport = transport_id.total
                        if transport300_id:
                            transport_300 = transport300_id.total
                        if transport1500_id:
                            transport_1500 = transport1500_id.total
                        if house_id:
                            house = house_id.total
                        if house_id_1:
                            house = house_id_1.total
                        if house500_id:
                            house_500 = house500_id.total
                        if saudi_gosi_10_id:
                            saudi_gosi_10 = saudi_gosi_10_id.total
                        if company_gosi_12_id:
                            company_gosi_12 = company_gosi_12_id.total
                        if company_gosi_22_id:
                            company_gosi_22 = company_gosi_22_id.total
                        if net_id:
                            net = net_id.total
                        if food_allowance_id:
                            food_allowance = food_allowance_id.total
                        if work_nature_allowance_id:
                            work_nature_allowance = work_nature_allowance_id.total
                        if fixed_add_allowance_id:
                            fixed_add_allowance = fixed_add_allowance_id.total
                        if fixed_deduct_amount_id:
                            fixed_deduct_amount = fixed_deduct_amount_id.total
                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                        if employee_id.driver_code:
                            sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                        if employee_id.employee_code:
                            sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                        if employee_id.name:
                            sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                        if employee_id.name_english:
                            sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                        if employee_id.parent_id.name:
                            sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                        if employee_id.branch_id.region.bsg_region_name:
                            sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                               main_heading)
                        if employee_id.branch_id.branch_ar_name:
                            sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                               main_heading)
                        if employee_id.department_id.display_name:
                            sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                               main_heading)
                        if employee_id.work_location:
                            sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                        if employee_id.job_id.name:
                            sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                        if employee_id.employee_state:
                            sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                        if employee_id.suspend_salary:
                            sheet.write_string(row, col + 11, str('True'), main_heading)
                        if employee_id.is_driver:
                            sheet.write_string(row, col + 12, str('Driver'), main_heading)
                        if employee_id.guarantor_id.name:
                            sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                        if employee_id.company_id.name:
                            sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                        if employee_id.user_id.name:
                            sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                        if employee_id.partner_id.name:
                            sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                        if employee_id.mobile_phone:
                            sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                        if employee_id.country_id.name:
                            sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                        if employee_id.country_id:
                            if employee_id.country_id.code == 'SA':
                                if employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_national_id.bsg_nationality_name),
                                                       main_heading)
                            else:
                                if employee_id.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                        if employee_id.bsg_bank_id.bsg_acc_number:
                            sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                            sheet.write_string(row, col + 22,
                                               str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                               main_heading)
                        if employee_id.salary_payment_method:
                            sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_bank_name:
                            sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                               main_heading)
                        if employee_id.category_ids:
                            rec_names = employee_id.category_ids.mapped('name')
                            names = ','.join(rec_names)
                            sheet.write_string(row, col + 25, str(names), main_heading)
                        if employee_id.birthday:
                            sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                        if employee_id.bsgjoining_date:
                            sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                        if employee_id.end_service_date:
                            sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                        if employee_id.remaining_leaves:
                            sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                        if employee_id.leave_start_date:
                            sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                        if employee_id.gender:
                            sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                        if contract_id.date_start:
                            sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                        if contract_id.date_end:
                            sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                        if contract_id.state:
                            if contract_id.state == 'draft':
                                sheet.write_string(row, col + 35, str("New"), main_heading)
                            if contract_id.state == 'open':
                                sheet.write_string(row, col + 35, str("Running"), main_heading)
                            if contract_id.state == 'pending':
                                sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                            if contract_id.state == 'close':
                                sheet.write_string(row, col + 35, str("Expired"), main_heading)
                            if contract_id.state == 'cancel':
                                sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                        if contract_id.analytic_account_id:
                            sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                               main_heading)
                        if employee_id.salary_structure.name:
                            sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                               main_heading)
                        if contract_id.wage:
                            sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                            print('wage=', contract_id.wage)
                            wage_total += contract_id.wage
                            print('wage total=', wage_total)
                        if transport:
                            sheet.write_number(row, col + 39, transport, main_heading)
                            transport_total += transport
                        if self.env.user.company_id.company_code == "BIC":
                            if transport_300:
                                sheet.write_number(row, col + 40, transport_300, main_heading)
                                transport_300_total += transport_300
                            if transport_1500:
                                sheet.write_number(row, col + 41, transport_1500, main_heading)
                                transport_1500_total += transport_1500
                            if house:
                                sheet.write_number(row, col + 42, house, main_heading)
                                house_rent_total += house
                            if house_500:
                                sheet.write_number(row, col + 43, house_500, main_heading)
                                house_500_total += house_500
                            if food_allowance:
                                sheet.write_number(row, col + 44, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 46, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 52, net, main_heading)
                                net_total += net
                        else:
                            if house:
                                sheet.write_number(row, col + 40, house, main_heading)
                                house_rent_total += house
                            if food_allowance:
                                sheet.write_number(row, col + 41, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 43, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 49, net, main_heading)
                                net_total += net
                        row += 1
                        total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 1, total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                sheet.write_number(row, col + 38, wage_total, main_heading)
                sheet.write_number(row, col + 39, transport_total, main_heading)
                if self.env.user.company_id.company_code == "BIC":
                    sheet.write_number(row, col + 40, transport_300_total, main_heading)
                    sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                    sheet.write_number(row, col + 42, house_rent_total, main_heading)
                    sheet.write_number(row, col + 43, house_500_total, main_heading)
                    sheet.write_number(row, col + 44, food_total, main_heading)
                    sheet.write_number(row, col + 45, work_nature_total, main_heading)
                    sheet.write_number(row, col + 46, gross_total, main_heading)
                    sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 52, net_total, main_heading)
                else:
                    sheet.write_number(row, col + 40, house_rent_total, main_heading)
                    sheet.write_number(row, col + 41, food_total, main_heading)
                    sheet.write_number(row, col + 42, work_nature_total, main_heading)
                    sheet.write_number(row, col + 43, gross_total, main_heading)
                    sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 49, net_total, main_heading)
                row += 1
                grand_total += total
            if resig_employee_ids:
                total = 0
                wage_total = 0.0
                transport_total = 0.0
                transport_300_total = 0.0
                transport_1500_total = 0.0
                house_rent_total = 0.0
                house_500_total = 0.0
                food_total = 0.0
                work_nature_total = 0.0
                gross_total = 0.0
                fixed_additional_total = 0.0
                fixed_deduction_total = 0.0
                saudi_gosi_total = 0.0
                company_gosi_12_total = 0.0
                company_gosi_22_total = 0.0
                net_total = 0.0
                sheet.write(row, col, 'Employee Status', main_heading2)
                sheet.write_string(row, col + 1, str('Resignation'), main_heading)
                sheet.write(row, col + 2, 'حالة الموظف', main_heading2)
                row += 1
                for employee_id in resig_employee_ids:
                    if employee_id:
                        gross = 0.0
                        transport = 0.0
                        transport_300 = 0.0
                        transport_1500 = 0.0
                        house = 0.0
                        house_500 = 0.0
                        food_allowance = 0.0
                        work_nature_allowance = 0.0
                        fixed_add_allowance = 0.0
                        fixed_deduct_amount = 0.0
                        saudi_gosi_10 = 0.0
                        company_gosi_12 = 0.0
                        company_gosi_22 = 0.0
                        net = 0.0
                        gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                        transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                        transport300_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA22')
                        transport1500_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA23')
                        house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                        house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                        house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                        saudi_gosi_10_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'GOSI')
                        company_gosi_12_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CGOSI')
                        company_gosi_22_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FCGOSI')
                        net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                        food_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FA')
                        work_nature_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'NWA')
                        fixed_add_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FAA')
                        fixed_deduct_amount_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'DEDFIXD')
                        if gross_id:
                            gross = gross_id.total
                        if transport_id:
                            transport = transport_id.total
                        if transport300_id:
                            transport_300 = transport300_id.total
                        if transport1500_id:
                            transport_1500 = transport1500_id.total
                        if house_id:
                            house = house_id.total
                        if house_id_1:
                            house = house_id_1.total
                        if house500_id:
                            house_500 = house500_id.total
                        if saudi_gosi_10_id:
                            saudi_gosi_10 = saudi_gosi_10_id.total
                        if company_gosi_12_id:
                            company_gosi_12 = company_gosi_12_id.total
                        if company_gosi_22_id:
                            company_gosi_22 = company_gosi_22_id.total
                        if net_id:
                            net = net_id.total
                        if food_allowance_id:
                            food_allowance = food_allowance_id.total
                        if work_nature_allowance_id:
                            work_nature_allowance = work_nature_allowance_id.total
                        if fixed_add_allowance_id:
                            fixed_add_allowance = fixed_add_allowance_id.total
                        if fixed_deduct_amount_id:
                            fixed_deduct_amount = fixed_deduct_amount_id.total
                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                        if employee_id.driver_code:
                            sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                        if employee_id.employee_code:
                            sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                        if employee_id.name:
                            sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                        if employee_id.name_english:
                            sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                        if employee_id.parent_id.name:
                            sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                        if employee_id.branch_id.region.bsg_region_name:
                            sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                               main_heading)
                        if employee_id.branch_id.branch_ar_name:
                            sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                               main_heading)
                        if employee_id.department_id.display_name:
                            sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                               main_heading)
                        if employee_id.work_location:
                            sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                        if employee_id.job_id.name:
                            sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                        if employee_id.employee_state:
                            sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                        if employee_id.suspend_salary:
                            sheet.write_string(row, col + 11, str('True'), main_heading)
                        if employee_id.is_driver:
                            sheet.write_string(row, col + 12, str('Driver'), main_heading)
                        if employee_id.guarantor_id.name:
                            sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                        if employee_id.company_id.name:
                            sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                        if employee_id.user_id.name:
                            sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                        if employee_id.partner_id.name:
                            sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                        if employee_id.mobile_phone:
                            sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                        if employee_id.country_id.name:
                            sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                        if employee_id.country_id:
                            if employee_id.country_id.code == 'SA':
                                if employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_national_id.bsg_nationality_name),
                                                       main_heading)
                            else:
                                if employee_id.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                        if employee_id.bsg_bank_id.bsg_acc_number:
                            sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                            sheet.write_string(row, col + 22,
                                               str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                               main_heading)
                        if employee_id.salary_payment_method:
                            sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_bank_name:
                            sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                               main_heading)
                        if employee_id.category_ids:
                            rec_names = employee_id.category_ids.mapped('name')
                            names = ','.join(rec_names)
                            sheet.write_string(row, col + 25, str(names), main_heading)
                        if employee_id.birthday:
                            sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                        if employee_id.bsgjoining_date:
                            sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                        if employee_id.end_service_date:
                            sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                        if employee_id.remaining_leaves:
                            sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                        if employee_id.leave_start_date:
                            sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                        if employee_id.gender:
                            sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                        if contract_id.date_start:
                            sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                        if contract_id.date_end:
                            sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                        if contract_id.state:
                            if contract_id.state == 'draft':
                                sheet.write_string(row, col + 35, str("New"), main_heading)
                            if contract_id.state == 'open':
                                sheet.write_string(row, col + 35, str("Running"), main_heading)
                            if contract_id.state == 'pending':
                                sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                            if contract_id.state == 'close':
                                sheet.write_string(row, col + 35, str("Expired"), main_heading)
                            if contract_id.state == 'cancel':
                                sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                        if contract_id.analytic_account_id:
                            sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                               main_heading)
                        if employee_id.salary_structure.name:
                            sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                               main_heading)
                        if contract_id.wage:
                            sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                            print('wage=', contract_id.wage)
                            wage_total += contract_id.wage
                            print('wage total=', wage_total)
                        if transport:
                            sheet.write_number(row, col + 39, transport, main_heading)
                            transport_total += transport
                        if self.env.user.company_id.company_code == "BIC":
                            if transport_300:
                                sheet.write_number(row, col + 40, transport_300, main_heading)
                                transport_300_total += transport_300
                            if transport_1500:
                                sheet.write_number(row, col + 41, transport_1500, main_heading)
                                transport_1500_total += transport_1500
                            if house:
                                sheet.write_number(row, col + 42, house, main_heading)
                                house_rent_total += house
                            if house_500:
                                sheet.write_number(row, col + 43, house_500, main_heading)
                                house_500_total += house_500
                            if food_allowance:
                                sheet.write_number(row, col + 44, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 46, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 52, net, main_heading)
                                net_total += net
                        else:
                            if house:
                                sheet.write_number(row, col + 40, house, main_heading)
                                house_rent_total += house
                            if food_allowance:
                                sheet.write_number(row, col + 41, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 43, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 49, net, main_heading)
                                net_total += net
                        row += 1
                        total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 1, total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                sheet.write_number(row, col + 38, wage_total, main_heading)
                sheet.write_number(row, col + 39, transport_total, main_heading)
                if self.env.user.company_id.company_code == "BIC":
                    sheet.write_number(row, col + 40, transport_300_total, main_heading)
                    sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                    sheet.write_number(row, col + 42, house_rent_total, main_heading)
                    sheet.write_number(row, col + 43, house_500_total, main_heading)
                    sheet.write_number(row, col + 44, food_total, main_heading)
                    sheet.write_number(row, col + 45, work_nature_total, main_heading)
                    sheet.write_number(row, col + 46, gross_total, main_heading)
                    sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 52, net_total, main_heading)
                else:
                    sheet.write_number(row, col + 40, house_rent_total, main_heading)
                    sheet.write_number(row, col + 41, food_total, main_heading)
                    sheet.write_number(row, col + 42, work_nature_total, main_heading)
                    sheet.write_number(row, col + 43, gross_total, main_heading)
                    sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 49, net_total, main_heading)
                row += 1
                grand_total += total
            if suspend_employee_ids:
                total = 0
                wage_total = 0.0
                transport_total = 0.0
                transport_300_total = 0.0
                transport_1500_total = 0.0
                house_rent_total = 0.0
                house_500_total = 0.0
                food_total = 0.0
                work_nature_total = 0.0
                gross_total = 0.0
                fixed_additional_total = 0.0
                fixed_deduction_total = 0.0
                saudi_gosi_total = 0.0
                company_gosi_12_total = 0.0
                company_gosi_22_total = 0.0
                net_total = 0.0
                sheet.write(row, col, 'Employee Status', main_heading2)
                sheet.write_string(row, col + 1, str('Suspended'), main_heading)
                sheet.write(row, col + 2, 'حالة الموظف', main_heading2)
                row += 1
                for employee_id in suspend_employee_ids:
                    if employee_id:
                        gross = 0.0
                        transport = 0.0
                        transport_300 = 0.0
                        transport_1500 = 0.0
                        house = 0.0
                        house_500 = 0.0
                        food_allowance = 0.0
                        work_nature_allowance = 0.0
                        fixed_add_allowance = 0.0
                        fixed_deduct_amount = 0.0
                        saudi_gosi_10 = 0.0
                        company_gosi_12 = 0.0
                        company_gosi_22 = 0.0
                        net = 0.0
                        gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                        transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                        transport300_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA22')
                        transport1500_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA23')
                        house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                        house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                        house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                        saudi_gosi_10_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'GOSI')
                        company_gosi_12_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CGOSI')
                        company_gosi_22_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FCGOSI')
                        net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                        food_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FA')
                        work_nature_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'NWA')
                        fixed_add_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FAA')
                        fixed_deduct_amount_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'DEDFIXD')
                        if gross_id:
                            gross = gross_id.total
                        if transport_id:
                            transport = transport_id.total
                        if transport300_id:
                            transport_300 = transport300_id.total
                        if transport1500_id:
                            transport_1500 = transport1500_id.total
                        if house_id:
                            house = house_id.total
                        if house_id_1:
                            house = house_id_1.total
                        if house500_id:
                            house_500 = house500_id.total
                        if saudi_gosi_10_id:
                            saudi_gosi_10 = saudi_gosi_10_id.total
                        if company_gosi_12_id:
                            company_gosi_12 = company_gosi_12_id.total
                        if company_gosi_22_id:
                            company_gosi_22 = company_gosi_22_id.total
                        if net_id:
                            net = net_id.total
                        if food_allowance_id:
                            food_allowance = food_allowance_id.total
                        if work_nature_allowance_id:
                            work_nature_allowance = work_nature_allowance_id.total
                        if fixed_add_allowance_id:
                            fixed_add_allowance = fixed_add_allowance_id.total
                        if fixed_deduct_amount_id:
                            fixed_deduct_amount = fixed_deduct_amount_id.total
                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                        if employee_id.driver_code:
                            sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                        if employee_id.employee_code:
                            sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                        if employee_id.name:
                            sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                        if employee_id.name_english:
                            sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                        if employee_id.parent_id.name:
                            sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                        if employee_id.branch_id.region.bsg_region_name:
                            sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                               main_heading)
                        if employee_id.branch_id.branch_ar_name:
                            sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                               main_heading)
                        if employee_id.department_id.display_name:
                            sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                               main_heading)
                        if employee_id.work_location:
                            sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                        if employee_id.job_id.name:
                            sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                        if employee_id.employee_state:
                            sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                        if employee_id.suspend_salary:
                            sheet.write_string(row, col + 11, str('True'), main_heading)
                        if employee_id.is_driver:
                            sheet.write_string(row, col + 12, str('Driver'), main_heading)
                        if employee_id.guarantor_id.name:
                            sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                        if employee_id.company_id.name:
                            sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                        if employee_id.user_id.name:
                            sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                        if employee_id.partner_id.name:
                            sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                        if employee_id.mobile_phone:
                            sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                        if employee_id.country_id.name:
                            sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                        if employee_id.country_id:
                            if employee_id.country_id.code == 'SA':
                                if employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_national_id.bsg_nationality_name),
                                                       main_heading)
                            else:
                                if employee_id.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                        if employee_id.bsg_bank_id.bsg_acc_number:
                            sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                            sheet.write_string(row, col + 22,
                                               str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                               main_heading)
                        if employee_id.salary_payment_method:
                            sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_bank_name:
                            sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                               main_heading)
                        if employee_id.category_ids:
                            rec_names = employee_id.category_ids.mapped('name')
                            names = ','.join(rec_names)
                            sheet.write_string(row, col + 25, str(names), main_heading)
                        if employee_id.birthday:
                            sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                        if employee_id.bsgjoining_date:
                            sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                        if employee_id.end_service_date:
                            sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                        if employee_id.remaining_leaves:
                            sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                        if employee_id.leave_start_date:
                            sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                        if employee_id.gender:
                            sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                        if contract_id.date_start:
                            sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                        if contract_id.date_end:
                            sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                        if contract_id.state:
                            if contract_id.state == 'draft':
                                sheet.write_string(row, col + 35, str("New"), main_heading)
                            if contract_id.state == 'open':
                                sheet.write_string(row, col + 35, str("Running"), main_heading)
                            if contract_id.state == 'pending':
                                sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                            if contract_id.state == 'close':
                                sheet.write_string(row, col + 35, str("Expired"), main_heading)
                            if contract_id.state == 'cancel':
                                sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                        if contract_id.analytic_account_id:
                            sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                               main_heading)
                        if employee_id.salary_structure.name:
                            sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                               main_heading)
                        if contract_id.wage:
                            sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                            print('wage=', contract_id.wage)
                            wage_total += contract_id.wage
                            print('wage total=', wage_total)
                        if transport:
                            sheet.write_number(row, col + 39, transport, main_heading)
                            transport_total += transport
                        if self.env.user.company_id.company_code == "BIC":
                            if transport_300:
                                sheet.write_number(row, col + 40, transport_300, main_heading)
                                transport_300_total += transport_300
                            if transport_1500:
                                sheet.write_number(row, col + 41, transport_1500, main_heading)
                                transport_1500_total += transport_1500
                            if house:
                                sheet.write_number(row, col + 42, house, main_heading)
                                house_rent_total += house
                            if house_500:
                                sheet.write_number(row, col + 43, house_500, main_heading)
                                house_500_total += house_500
                            if food_allowance:
                                sheet.write_number(row, col + 44, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 46, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 52, net, main_heading)
                                net_total += net
                        else:
                            if house:
                                sheet.write_number(row, col + 40, house, main_heading)
                                house_rent_total += house
                            if food_allowance:
                                sheet.write_number(row, col + 41, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 43, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 49, net, main_heading)
                                net_total += net
                        row += 1
                        total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 1, total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                sheet.write_number(row, col + 38, wage_total, main_heading)
                sheet.write_number(row, col + 39, transport_total, main_heading)
                if self.env.user.company_id.company_code == "BIC":
                    sheet.write_number(row, col + 40, transport_300_total, main_heading)
                    sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                    sheet.write_number(row, col + 42, house_rent_total, main_heading)
                    sheet.write_number(row, col + 43, house_500_total, main_heading)
                    sheet.write_number(row, col + 44, food_total, main_heading)
                    sheet.write_number(row, col + 45, work_nature_total, main_heading)
                    sheet.write_number(row, col + 46, gross_total, main_heading)
                    sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 52, net_total, main_heading)
                else:
                    sheet.write_number(row, col + 40, house_rent_total, main_heading)
                    sheet.write_number(row, col + 41, food_total, main_heading)
                    sheet.write_number(row, col + 42, work_nature_total, main_heading)
                    sheet.write_number(row, col + 43, gross_total, main_heading)
                    sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 49, net_total, main_heading)
                row += 1
                grand_total += total
            if expire_employee_ids:
                total = 0
                wage_total = 0.0
                transport_total = 0.0
                transport_300_total = 0.0
                transport_1500_total = 0.0
                house_rent_total = 0.0
                house_500_total = 0.0
                food_total = 0.0
                work_nature_total = 0.0
                gross_total = 0.0
                fixed_additional_total = 0.0
                fixed_deduction_total = 0.0
                saudi_gosi_total = 0.0
                company_gosi_12_total = 0.0
                company_gosi_22_total = 0.0
                net_total = 0.0
                sheet.write(row, col, 'Employee Status', main_heading2)
                sheet.write_string(row, col + 1, str('Service Expired'), main_heading)
                sheet.write(row, col + 2, 'حالة الموظف', main_heading2)
                row += 1
                for employee_id in expire_employee_ids:
                    if employee_id:
                        gross = 0.0
                        transport = 0.0
                        transport_300 = 0.0
                        transport_1500 = 0.0
                        house = 0.0
                        house_500 = 0.0
                        food_allowance = 0.0
                        work_nature_allowance = 0.0
                        fixed_add_allowance = 0.0
                        fixed_deduct_amount = 0.0
                        saudi_gosi_10 = 0.0
                        company_gosi_12 = 0.0
                        company_gosi_22 = 0.0
                        net = 0.0
                        gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                        transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                        transport300_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA22')
                        transport1500_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA23')
                        house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                        house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                        house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                        saudi_gosi_10_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'GOSI')
                        company_gosi_12_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CGOSI')
                        company_gosi_22_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FCGOSI')
                        net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                        food_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FA')
                        work_nature_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'NWA')
                        fixed_add_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FAA')
                        fixed_deduct_amount_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'DEDFIXD')
                        if gross_id:
                            gross = gross_id.total
                        if transport_id:
                            transport = transport_id.total
                        if transport300_id:
                            transport_300 = transport300_id.total
                        if transport1500_id:
                            transport_1500 = transport1500_id.total
                        if house_id:
                            house = house_id.total
                        if house_id_1:
                            house = house_id_1.total
                        if house500_id:
                            house_500 = house500_id.total
                        if saudi_gosi_10_id:
                            saudi_gosi_10 = saudi_gosi_10_id.total
                        if company_gosi_12_id:
                            company_gosi_12 = company_gosi_12_id.total
                        if company_gosi_22_id:
                            company_gosi_22 = company_gosi_22_id.total
                        if net_id:
                            net = net_id.total
                        if food_allowance_id:
                            food_allowance = food_allowance_id.total
                        if work_nature_allowance_id:
                            work_nature_allowance = work_nature_allowance_id.total
                        if fixed_add_allowance_id:
                            fixed_add_allowance = fixed_add_allowance_id.total
                        if fixed_deduct_amount_id:
                            fixed_deduct_amount = fixed_deduct_amount_id.total
                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                        if employee_id.driver_code:
                            sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                        if employee_id.employee_code:
                            sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                        if employee_id.name:
                            sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                        if employee_id.name_english:
                            sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                        if employee_id.parent_id.name:
                            sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                        if employee_id.branch_id.region.bsg_region_name:
                            sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                               main_heading)
                        if employee_id.branch_id.branch_ar_name:
                            sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                               main_heading)
                        if employee_id.department_id.display_name:
                            sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                               main_heading)
                        if employee_id.work_location:
                            sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                        if employee_id.job_id.name:
                            sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                        if employee_id.employee_state:
                            sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                        if employee_id.suspend_salary:
                            sheet.write_string(row, col + 11, str('True'), main_heading)
                        if employee_id.is_driver:
                            sheet.write_string(row, col + 12, str('Driver'), main_heading)
                        if employee_id.guarantor_id.name:
                            sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                        if employee_id.company_id.name:
                            sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                        if employee_id.user_id.name:
                            sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                        if employee_id.partner_id.name:
                            sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                        if employee_id.mobile_phone:
                            sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                        if employee_id.country_id.name:
                            sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                        if employee_id.country_id:
                            if employee_id.country_id.code == 'SA':
                                if employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_national_id.bsg_nationality_name),
                                                       main_heading)
                            else:
                                if employee_id.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                        if employee_id.bsg_bank_id.bsg_acc_number:
                            sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                            sheet.write_string(row, col + 22,
                                               str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                               main_heading)
                        if employee_id.salary_payment_method:
                            sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_bank_name:
                            sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                               main_heading)
                        if employee_id.category_ids:
                            rec_names = employee_id.category_ids.mapped('name')
                            names = ','.join(rec_names)
                            sheet.write_string(row, col + 25, str(names), main_heading)
                        if employee_id.birthday:
                            sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                        if employee_id.bsgjoining_date:
                            sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                        if employee_id.end_service_date:
                            sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                        if employee_id.remaining_leaves:
                            sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                        if employee_id.leave_start_date:
                            sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                        if employee_id.gender:
                            sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                        if contract_id.date_start:
                            sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                        if contract_id.date_end:
                            sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                        if contract_id.state:
                            if contract_id.state == 'draft':
                                sheet.write_string(row, col + 35, str("New"), main_heading)
                            if contract_id.state == 'open':
                                sheet.write_string(row, col + 35, str("Running"), main_heading)
                            if contract_id.state == 'pending':
                                sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                            if contract_id.state == 'close':
                                sheet.write_string(row, col + 35, str("Expired"), main_heading)
                            if contract_id.state == 'cancel':
                                sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                        if contract_id.analytic_account_id:
                            sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                               main_heading)
                        if employee_id.salary_structure.name:
                            sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                               main_heading)
                        if contract_id.wage:
                            sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                            print('wage=', contract_id.wage)
                            wage_total += contract_id.wage
                            print('wage total=', wage_total)
                        if transport:
                            sheet.write_number(row, col + 39, transport, main_heading)
                            transport_total += transport
                        if self.env.user.company_id.company_code == "BIC":
                            if transport_300:
                                sheet.write_number(row, col + 40, transport_300, main_heading)
                                transport_300_total += transport_300
                            if transport_1500:
                                sheet.write_number(row, col + 41, transport_1500, main_heading)
                                transport_1500_total += transport_1500
                            if house:
                                sheet.write_number(row, col + 42, house, main_heading)
                                house_rent_total += house
                            if house_500:
                                sheet.write_number(row, col + 43, house_500, main_heading)
                                house_500_total += house_500
                            if food_allowance:
                                sheet.write_number(row, col + 44, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 46, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 52, net, main_heading)
                                net_total += net
                        else:
                            if house:
                                sheet.write_number(row, col + 40, house, main_heading)
                                house_rent_total += house
                            if food_allowance:
                                sheet.write_number(row, col + 41, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 43, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 49, net, main_heading)
                                net_total += net
                        row += 1
                        total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 1, total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                sheet.write_number(row, col + 38, wage_total, main_heading)
                sheet.write_number(row, col + 39, transport_total, main_heading)
                if self.env.user.company_id.company_code == "BIC":
                    sheet.write_number(row, col + 40, transport_300_total, main_heading)
                    sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                    sheet.write_number(row, col + 42, house_rent_total, main_heading)
                    sheet.write_number(row, col + 43, house_500_total, main_heading)
                    sheet.write_number(row, col + 44, food_total, main_heading)
                    sheet.write_number(row, col + 45, work_nature_total, main_heading)
                    sheet.write_number(row, col + 46, gross_total, main_heading)
                    sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 52, net_total, main_heading)
                else:
                    sheet.write_number(row, col + 40, house_rent_total, main_heading)
                    sheet.write_number(row, col + 41, food_total, main_heading)
                    sheet.write_number(row, col + 42, work_nature_total, main_heading)
                    sheet.write_number(row, col + 43, gross_total, main_heading)
                    sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 49, net_total, main_heading)
                row += 1
                grand_total += total
            if terminate_employee_ids:
                total = 0
                wage_total = 0.0
                transport_total = 0.0
                transport_300_total = 0.0
                transport_1500_total = 0.0
                house_rent_total = 0.0
                house_500_total = 0.0
                food_total = 0.0
                work_nature_total = 0.0
                gross_total = 0.0
                fixed_additional_total = 0.0
                fixed_deduction_total = 0.0
                saudi_gosi_total = 0.0
                company_gosi_12_total = 0.0
                company_gosi_22_total = 0.0
                net_total = 0.0
                sheet.write(row, col, 'Employee Status', main_heading2)
                sheet.write_string(row, col + 1, str('Contract Terminated'), main_heading)
                sheet.write(row, col + 2, 'حالة الموظف', main_heading2)
                row += 1
                for employee_id in terminate_employee_ids:
                    if employee_id:
                        gross = 0.0
                        transport = 0.0
                        transport_300 = 0.0
                        transport_1500 = 0.0
                        house = 0.0
                        house_500 = 0.0
                        food_allowance = 0.0
                        work_nature_allowance = 0.0
                        fixed_add_allowance = 0.0
                        fixed_deduct_amount = 0.0
                        saudi_gosi_10 = 0.0
                        company_gosi_12 = 0.0
                        company_gosi_22 = 0.0
                        net = 0.0
                        gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                        transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                        transport300_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA22')
                        transport1500_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA23')
                        house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                        house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                        house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                        saudi_gosi_10_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'GOSI')
                        company_gosi_12_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CGOSI')
                        company_gosi_22_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FCGOSI')
                        net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                        food_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FA')
                        work_nature_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'NWA')
                        fixed_add_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FAA')
                        fixed_deduct_amount_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'DEDFIXD')
                        if gross_id:
                            gross = gross_id.total
                        if transport_id:
                            transport = transport_id.total
                        if transport300_id:
                            transport_300 = transport300_id.total
                        if transport1500_id:
                            transport_1500 = transport1500_id.total
                        if house_id:
                            house = house_id.total
                        if house_id_1:
                            house = house_id_1.total
                        if house500_id:
                            house_500 = house500_id.total
                        if saudi_gosi_10_id:
                            saudi_gosi_10 = saudi_gosi_10_id.total
                        if company_gosi_12_id:
                            company_gosi_12 = company_gosi_12_id.total
                        if company_gosi_22_id:
                            company_gosi_22 = company_gosi_22_id.total
                        if net_id:
                            net = net_id.total
                        if food_allowance_id:
                            food_allowance = food_allowance_id.total
                        if work_nature_allowance_id:
                            work_nature_allowance = work_nature_allowance_id.total
                        if fixed_add_allowance_id:
                            fixed_add_allowance = fixed_add_allowance_id.total
                        if fixed_deduct_amount_id:
                            fixed_deduct_amount = fixed_deduct_amount_id.total
                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                        if employee_id.driver_code:
                            sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                        if employee_id.employee_code:
                            sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                        if employee_id.name:
                            sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                        if employee_id.name_english:
                            sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                        if employee_id.parent_id.name:
                            sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                        if employee_id.branch_id.region.bsg_region_name:
                            sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                               main_heading)
                        if employee_id.branch_id.branch_ar_name:
                            sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                               main_heading)
                        if employee_id.department_id.display_name:
                            sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                               main_heading)
                        if employee_id.work_location:
                            sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                        if employee_id.job_id.name:
                            sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                        if employee_id.employee_state:
                            sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                        if employee_id.suspend_salary:
                            sheet.write_string(row, col + 11, str('True'), main_heading)
                        if employee_id.is_driver:
                            sheet.write_string(row, col + 12, str('Driver'), main_heading)
                        if employee_id.guarantor_id.name:
                            sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                        if employee_id.company_id.name:
                            sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                        if employee_id.user_id.name:
                            sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                        if employee_id.partner_id.name:
                            sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                        if employee_id.mobile_phone:
                            sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                        if employee_id.country_id.name:
                            sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                        if employee_id.country_id:
                            if employee_id.country_id.code == 'SA':
                                if employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_national_id.bsg_nationality_name),
                                                       main_heading)
                            else:
                                if employee_id.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                        if employee_id.bsg_bank_id.bsg_acc_number:
                            sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                            sheet.write_string(row, col + 22,
                                               str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                               main_heading)
                        if employee_id.salary_payment_method:
                            sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_bank_name:
                            sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                               main_heading)
                        if employee_id.category_ids:
                            rec_names = employee_id.category_ids.mapped('name')
                            names = ','.join(rec_names)
                            sheet.write_string(row, col + 25, str(names), main_heading)
                        if employee_id.birthday:
                            sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                        if employee_id.bsgjoining_date:
                            sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                        if employee_id.end_service_date:
                            sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                        if employee_id.remaining_leaves:
                            sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                        if employee_id.leave_start_date:
                            sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                        if employee_id.gender:
                            sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                        if contract_id.date_start:
                            sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                        if contract_id.date_end:
                            sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                        if contract_id.state:
                            if contract_id.state == 'draft':
                                sheet.write_string(row, col + 35, str("New"), main_heading)
                            if contract_id.state == 'open':
                                sheet.write_string(row, col + 35, str("Running"), main_heading)
                            if contract_id.state == 'pending':
                                sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                            if contract_id.state == 'close':
                                sheet.write_string(row, col + 35, str("Expired"), main_heading)
                            if contract_id.state == 'cancel':
                                sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                        if contract_id.analytic_account_id:
                            sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                               main_heading)
                        if employee_id.salary_structure.name:
                            sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                               main_heading)
                        if contract_id.wage:
                            sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                            print('wage=', contract_id.wage)
                            wage_total += contract_id.wage
                            print('wage total=', wage_total)
                        if transport:
                            sheet.write_number(row, col + 39, transport, main_heading)
                            transport_total += transport
                        if self.env.user.company_id.company_code == "BIC":
                            if transport_300:
                                sheet.write_number(row, col + 40, transport_300, main_heading)
                                transport_300_total += transport_300
                            if transport_1500:
                                sheet.write_number(row, col + 41, transport_1500, main_heading)
                                transport_1500_total += transport_1500
                            if house:
                                sheet.write_number(row, col + 42, house, main_heading)
                                house_rent_total += house
                            if house_500:
                                sheet.write_number(row, col + 43, house_500, main_heading)
                                house_500_total += house_500
                            if food_allowance:
                                sheet.write_number(row, col + 44, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 46, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 52, net, main_heading)
                                net_total += net
                        else:
                            if house:
                                sheet.write_number(row, col + 40, house, main_heading)
                                house_rent_total += house
                            if food_allowance:
                                sheet.write_number(row, col + 41, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 43, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 49, net, main_heading)
                                net_total += net
                        row += 1
                        total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 1, total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                sheet.write_number(row, col + 38, wage_total, main_heading)
                sheet.write_number(row, col + 39, transport_total, main_heading)
                if self.env.user.company_id.company_code == "BIC":
                    sheet.write_number(row, col + 40, transport_300_total, main_heading)
                    sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                    sheet.write_number(row, col + 42, house_rent_total, main_heading)
                    sheet.write_number(row, col + 43, house_500_total, main_heading)
                    sheet.write_number(row, col + 44, food_total, main_heading)
                    sheet.write_number(row, col + 45, work_nature_total, main_heading)
                    sheet.write_number(row, col + 46, gross_total, main_heading)
                    sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 52, net_total, main_heading)
                else:
                    sheet.write_number(row, col + 40, house_rent_total, main_heading)
                    sheet.write_number(row, col + 41, food_total, main_heading)
                    sheet.write_number(row, col + 42, work_nature_total, main_heading)
                    sheet.write_number(row, col + 43, gross_total, main_heading)
                    sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 49, net_total, main_heading)
                row += 1
                grand_total += total
            if contract_end_employee_ids:
                total = 0
                wage_total = 0.0
                transport_total = 0.0
                transport_300_total = 0.0
                transport_1500_total = 0.0
                house_rent_total = 0.0
                house_500_total = 0.0
                food_total = 0.0
                work_nature_total = 0.0
                gross_total = 0.0
                fixed_additional_total = 0.0
                fixed_deduction_total = 0.0
                saudi_gosi_total = 0.0
                company_gosi_12_total = 0.0
                company_gosi_22_total = 0.0
                net_total = 0.0
                sheet.write(row, col, 'Employee Status', main_heading2)
                sheet.write_string(row, col + 1, str('Ending Contract During Trial Period'), main_heading)
                sheet.write(row, col + 2, 'حالة الموظف', main_heading2)
                row += 1
                for employee_id in contract_end_employee_ids:
                    if employee_id:
                        gross = 0.0
                        transport = 0.0
                        transport_300 = 0.0
                        transport_1500 = 0.0
                        house = 0.0
                        house_500 = 0.0
                        food_allowance = 0.0
                        work_nature_allowance = 0.0
                        fixed_add_allowance = 0.0
                        fixed_deduct_amount = 0.0
                        saudi_gosi_10 = 0.0
                        company_gosi_12 = 0.0
                        company_gosi_22 = 0.0
                        net = 0.0
                        gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                        transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                        transport300_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA22')
                        transport1500_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA23')
                        house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                        house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                        house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                        saudi_gosi_10_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'GOSI')
                        company_gosi_12_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CGOSI')
                        company_gosi_22_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FCGOSI')
                        net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                        food_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FA')
                        work_nature_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'NWA')
                        fixed_add_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FAA')
                        fixed_deduct_amount_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'DEDFIXD')
                        if gross_id:
                            gross = gross_id.total
                        if transport_id:
                            transport = transport_id.total
                        if transport300_id:
                            transport_300 = transport300_id.total
                        if transport1500_id:
                            transport_1500 = transport1500_id.total
                        if house_id:
                            house = house_id.total
                        if house_id_1:
                            house = house_id_1.total
                        if house500_id:
                            house_500 = house500_id.total
                        if saudi_gosi_10_id:
                            saudi_gosi_10 = saudi_gosi_10_id.total
                        if company_gosi_12_id:
                            company_gosi_12 = company_gosi_12_id.total
                        if company_gosi_22_id:
                            company_gosi_22 = company_gosi_22_id.total
                        if net_id:
                            net = net_id.total
                        if food_allowance_id:
                            food_allowance = food_allowance_id.total
                        if work_nature_allowance_id:
                            work_nature_allowance = work_nature_allowance_id.total
                        if fixed_add_allowance_id:
                            fixed_add_allowance = fixed_add_allowance_id.total
                        if fixed_deduct_amount_id:
                            fixed_deduct_amount = fixed_deduct_amount_id.total
                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                        if employee_id.driver_code:
                            sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                        if employee_id.employee_code:
                            sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                        if employee_id.name:
                            sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                        if employee_id.name_english:
                            sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                        if employee_id.parent_id.name:
                            sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                        if employee_id.branch_id.region.bsg_region_name:
                            sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                               main_heading)
                        if employee_id.branch_id.branch_ar_name:
                            sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                               main_heading)
                        if employee_id.department_id.display_name:
                            sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                               main_heading)
                        if employee_id.work_location:
                            sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                        if employee_id.job_id.name:
                            sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                        if employee_id.employee_state:
                            sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                        if employee_id.suspend_salary:
                            sheet.write_string(row, col + 11, str('True'), main_heading)
                        if employee_id.is_driver:
                            sheet.write_string(row, col + 12, str('Driver'), main_heading)
                        if employee_id.guarantor_id.name:
                            sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                        if employee_id.company_id.name:
                            sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                        if employee_id.user_id.name:
                            sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                        if employee_id.partner_id.name:
                            sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                        if employee_id.mobile_phone:
                            sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                        if employee_id.country_id.name:
                            sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                        if employee_id.country_id:
                            if employee_id.country_id.code == 'SA':
                                if employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_national_id.bsg_nationality_name),
                                                       main_heading)
                            else:
                                if employee_id.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                        if employee_id.bsg_bank_id.bsg_acc_number:
                            sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                            sheet.write_string(row, col + 22,
                                               str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                               main_heading)
                        if employee_id.salary_payment_method:
                            sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_bank_name:
                            sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                               main_heading)
                        if employee_id.category_ids:
                            rec_names = employee_id.category_ids.mapped('name')
                            names = ','.join(rec_names)
                            sheet.write_string(row, col + 25, str(names), main_heading)
                        if employee_id.birthday:
                            sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                        if employee_id.bsgjoining_date:
                            sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                        if employee_id.end_service_date:
                            sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                        if employee_id.remaining_leaves:
                            sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                        if employee_id.leave_start_date:
                            sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                        if employee_id.gender:
                            sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                        if contract_id.date_start:
                            sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                        if contract_id.date_end:
                            sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                        if contract_id.state:
                            if contract_id.state == 'draft':
                                sheet.write_string(row, col + 35, str("New"), main_heading)
                            if contract_id.state == 'open':
                                sheet.write_string(row, col + 35, str("Running"), main_heading)
                            if contract_id.state == 'pending':
                                sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                            if contract_id.state == 'close':
                                sheet.write_string(row, col + 35, str("Expired"), main_heading)
                            if contract_id.state == 'cancel':
                                sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                        if contract_id.analytic_account_id:
                            sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                               main_heading)
                        if employee_id.salary_structure.name:
                            sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                               main_heading)
                        if contract_id.wage:
                            sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                            print('wage=', contract_id.wage)
                            wage_total += contract_id.wage
                            print('wage total=', wage_total)
                        if transport:
                            sheet.write_number(row, col + 39, transport, main_heading)
                            transport_total += transport
                        if self.env.user.company_id.company_code == "BIC":
                            if transport_300:
                                sheet.write_number(row, col + 40, transport_300, main_heading)
                                transport_300_total += transport_300
                            if transport_1500:
                                sheet.write_number(row, col + 41, transport_1500, main_heading)
                                transport_1500_total += transport_1500
                            if house:
                                sheet.write_number(row, col + 42, house, main_heading)
                                house_rent_total += house
                            if house_500:
                                sheet.write_number(row, col + 43, house_500, main_heading)
                                house_500_total += house_500
                            if food_allowance:
                                sheet.write_number(row, col + 44, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 46, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 52, net, main_heading)
                                net_total += net
                        else:
                            if house:
                                sheet.write_number(row, col + 40, house, main_heading)
                                house_rent_total += house
                            if food_allowance:
                                sheet.write_number(row, col + 41, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 43, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 49, net, main_heading)
                                net_total += net
                        row += 1
                        total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 1, total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                sheet.write_number(row, col + 38, wage_total, main_heading)
                sheet.write_number(row, col + 39, transport_total, main_heading)
                if self.env.user.company_id.company_code == "BIC":
                    sheet.write_number(row, col + 40, transport_300_total, main_heading)
                    sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                    sheet.write_number(row, col + 42, house_rent_total, main_heading)
                    sheet.write_number(row, col + 43, house_500_total, main_heading)
                    sheet.write_number(row, col + 44, food_total, main_heading)
                    sheet.write_number(row, col + 45, work_nature_total, main_heading)
                    sheet.write_number(row, col + 46, gross_total, main_heading)
                    sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 52, net_total, main_heading)
                else:
                    sheet.write_number(row, col + 40, house_rent_total, main_heading)
                    sheet.write_number(row, col + 41, food_total, main_heading)
                    sheet.write_number(row, col + 42, work_nature_total, main_heading)
                    sheet.write_number(row, col + 43, gross_total, main_heading)
                    sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 49, net_total, main_heading)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 1, grand_total, main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_partner_type':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Partner Type"
            sheet.merge_range('A1:AE1', 'مجموعة تقرير معلومات راتب الموظف حسب نوع الشريك', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Partner Type', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Department', main_heading2)
            sheet.write(row, col + 8, 'Work Location', main_heading2)
            sheet.write(row, col + 9, 'Jop Position', main_heading2)
            sheet.write(row, col + 10, 'Employ Status', main_heading2)
            sheet.write(row, col + 11, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 12, 'Is Driver?', main_heading2)
            sheet.write(row, col + 13, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 14, 'Company Name', main_heading2)
            sheet.write(row, col + 15, 'User Name', main_heading2)
            sheet.write(row, col + 16, 'Partner Name', main_heading2)
            sheet.write(row, col + 17, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 18, 'Mobile No.', main_heading2)
            sheet.write(row, col + 19, 'Nationality', main_heading2)
            sheet.write(row, col + 20, 'ID No.', main_heading2)
            sheet.write(row, col + 21, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 22, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 23, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 24, 'Bank Name', main_heading2)
            sheet.write(row, col + 25, 'Tags', main_heading2)
            sheet.write(row, col + 26, 'Date of Birth', main_heading2)
            sheet.write(row, col + 27, 'Date of Join', main_heading2)
            sheet.write(row, col + 28, 'End Service Date', main_heading2)
            sheet.write(row, col + 29, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 30, 'leave start date', main_heading2)
            sheet.write(row, col + 31, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 32, 'Gender', main_heading2)
            sheet.write(row, col + 33, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 35, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 36, 'Analytic Account', main_heading2)
            sheet.write(row, col + 37, 'Salary Structure', main_heading2)
            sheet.write(row, col + 38, 'Wage', main_heading2)
            sheet.write(row, col + 39, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'Transport', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'House Rent', main_heading2)
                sheet.write(row, col + 44, 'Food', main_heading2)
                sheet.write(row, col + 45, 'Work Nature', main_heading2)
                sheet.write(row, col + 46, 'Gross', main_heading2)
                sheet.write(row, col + 47, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 48, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 40, 'House Rent', main_heading2)
                sheet.write(row, col + 41, 'Food', main_heading2)
                sheet.write(row, col + 42, 'Work Nature', main_heading2)
                sheet.write(row, col + 43, 'Gross', main_heading2)
                sheet.write(row, col + 44, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 45, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'الادارة', main_heading2)
            sheet.write(row, col + 8, 'مكان العمل', main_heading2)
            sheet.write(row, col + 9, 'الوظيفه', main_heading2)
            sheet.write(row, col + 10, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 11, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 12, 'سائق ؟', main_heading2)
            sheet.write(row, col + 13, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 14, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 15, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 16, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 17, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 18, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 19, 'الجنسية', main_heading2)
            sheet.write(row, col + 20, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 21, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 22, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 23, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 24, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 25, 'الوسم', main_heading2)
            sheet.write(row, col + 26, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 27, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 28, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 29, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 31, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 32, 'الجنس', main_heading2)
            sheet.write(row, col + 33, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 34, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 35, 'حالة العقد', main_heading2)
            sheet.write(row, col + 36, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 37, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 38, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 39, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 41, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن', main_heading2)
                sheet.write(row, col + 43, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 44, 'بدل طعام', main_heading2)
                sheet.write(row, col + 45, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 46, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 47, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 48, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 40, 'بدل سكن', main_heading2)
                sheet.write(row, col + 41, 'بدل طعام', main_heading2)
                sheet.write(row, col + 42, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 43, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 44, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 45, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'صافي الراتب', main_heading2)
            row += 1
            partner_type_list = []
            grand_total = 0
            partner_type_ids = self.env['partner.type'].search([])
            for partner_id in partner_type_ids:
                if partner_id:
                    partner_type_list.append(partner_id.name)
            for partner_name in partner_type_list:
                if partner_name:
                    partner_employee_ids = employee_ids.filtered(lambda r: r.partner_type_id.name == partner_name)
                    if partner_employee_ids:
                        total = 0
                        wage_total = 0.0
                        transport_total = 0.0
                        transport_300_total = 0.0
                        transport_1500_total = 0.0
                        house_rent_total = 0.0
                        house_500_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        sheet.write(row, col, 'Partner Type', main_heading2)
                        sheet.write_string(row, col + 1, str(partner_name), main_heading)
                        sheet.write(row, col + 2, 'نوع الشريك', main_heading2)
                        row += 1
                        for employee_id in partner_employee_ids:
                            if employee_id:
                                gross = 0.0
                                transport = 0.0
                                transport_300 = 0.0
                                transport_1500 = 0.0
                                house = 0.0
                                house_500 = 0.0
                                food_allowance = 0.0
                                work_nature_allowance = 0.0
                                fixed_add_allowance = 0.0
                                fixed_deduct_amount = 0.0
                                saudi_gosi_10 = 0.0
                                company_gosi_12 = 0.0
                                company_gosi_22 = 0.0
                                net = 0.0
                                gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                                transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                                transport300_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CA22')
                                transport1500_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CA23')
                                house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                                house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                                house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                                saudi_gosi_10_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'GOSI')
                                company_gosi_12_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CGOSI')
                                company_gosi_22_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FCGOSI')
                                net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                                food_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FA')
                                work_nature_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'NWA')
                                fixed_add_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FAA')
                                fixed_deduct_amount_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'DEDFIXD')
                                if gross_id:
                                    gross = gross_id.total
                                if transport_id:
                                    transport = transport_id.total
                                if transport300_id:
                                    transport_300 = transport300_id.total
                                if transport1500_id:
                                    transport_1500 = transport1500_id.total
                                if house_id:
                                    house = house_id.total
                                if house_id_1:
                                    house = house_id_1.total
                                if house500_id:
                                    house_500 = house500_id.total
                                if saudi_gosi_10_id:
                                    saudi_gosi_10 = saudi_gosi_10_id.total
                                if company_gosi_12_id:
                                    company_gosi_12 = company_gosi_12_id.total
                                if company_gosi_22_id:
                                    company_gosi_22 = company_gosi_22_id.total
                                if net_id:
                                    net = net_id.total
                                if food_allowance_id:
                                    food_allowance = food_allowance_id.total
                                if work_nature_allowance_id:
                                    work_nature_allowance = work_nature_allowance_id.total
                                if fixed_add_allowance_id:
                                    fixed_add_allowance = fixed_add_allowance_id.total
                                if fixed_deduct_amount_id:
                                    fixed_deduct_amount = fixed_deduct_amount_id.total
                                contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                if employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                if employee_id.name:
                                    sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                if employee_id.name_english:
                                    sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                if employee_id.parent_id.name:
                                    sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                                if employee_id.branch_id.region.bsg_region_name:
                                    sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                                       main_heading)
                                if employee_id.branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                                       main_heading)
                                if employee_id.department_id.display_name:
                                    sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                                       main_heading)
                                if employee_id.work_location:
                                    sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                                if employee_id.job_id.name:
                                    sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                                if employee_id.employee_state:
                                    sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                                if employee_id.suspend_salary:
                                    sheet.write_string(row, col + 11, str('True'), main_heading)
                                if employee_id.is_driver:
                                    sheet.write_string(row, col + 12, str('Driver'), main_heading)
                                if employee_id.guarantor_id.name:
                                    sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                                if employee_id.company_id.name:
                                    sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                                if employee_id.user_id.name:
                                    sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                                if employee_id.partner_id.name:
                                    sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                                if employee_id.country_id.name:
                                    sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                                if employee_id.country_id:
                                    if employee_id.country_id.code == 'SA':
                                        if employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if employee_id.bsg_bank_id.bsg_acc_number:
                                    sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                    sheet.write_string(row, col + 22,
                                                       str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                       main_heading)
                                if employee_id.salary_payment_method:
                                    sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_bank_name:
                                    sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                                       main_heading)
                                if employee_id.category_ids:
                                    rec_names = employee_id.category_ids.mapped('name')
                                    names = ','.join(rec_names)
                                    sheet.write_string(row, col + 25, str(names), main_heading)
                                if employee_id.birthday:
                                    sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                                if employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                                if employee_id.end_service_date:
                                    sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                                if employee_id.remaining_leaves:
                                    sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                                if employee_id.leave_start_date:
                                    sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                                if employee_id.gender:
                                    sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                                if contract_id.date_start:
                                    sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                                if contract_id.date_end:
                                    sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                                if contract_id.state:
                                    if contract_id.state == 'draft':
                                        sheet.write_string(row, col + 35, str("New"), main_heading)
                                    if contract_id.state == 'open':
                                        sheet.write_string(row, col + 35, str("Running"), main_heading)
                                    if contract_id.state == 'pending':
                                        sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                                    if contract_id.state == 'close':
                                        sheet.write_string(row, col + 35, str("Expired"), main_heading)
                                    if contract_id.state == 'cancel':
                                        sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                                if contract_id.analytic_account_id:
                                    sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                                       main_heading)
                                if employee_id.salary_structure.name:
                                    sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                                       main_heading)
                                if contract_id.wage:
                                    sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                                    print('wage=', contract_id.wage)
                                    wage_total += contract_id.wage
                                    print('wage total=', wage_total)
                                if transport:
                                    sheet.write_number(row, col + 39, transport, main_heading)
                                    transport_total += transport
                                if self.env.user.company_id.company_code == "BIC":
                                    if transport_300:
                                        sheet.write_number(row, col + 40, transport_300, main_heading)
                                        transport_300_total += transport_300
                                    if transport_1500:
                                        sheet.write_number(row, col + 41, transport_1500, main_heading)
                                        transport_1500_total += transport_1500
                                    if house:
                                        sheet.write_number(row, col + 42, house, main_heading)
                                        house_rent_total += house
                                    if house_500:
                                        sheet.write_number(row, col + 43, house_500, main_heading)
                                        house_500_total += house_500
                                    if food_allowance:
                                        sheet.write_number(row, col + 44, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 46, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 52, net, main_heading)
                                        net_total += net
                                else:
                                    if house:
                                        sheet.write_number(row, col + 40, house, main_heading)
                                        house_rent_total += house
                                    if food_allowance:
                                        sheet.write_number(row, col + 41, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 43, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 49, net, main_heading)
                                        net_total += net
                                row += 1
                                total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_number(row, col + 1, total, main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        sheet.write_number(row, col + 38, wage_total, main_heading)
                        sheet.write_number(row, col + 39, transport_total, main_heading)
                        if self.env.user.company_id.company_code == "BIC":
                            sheet.write_number(row, col + 40, transport_300_total, main_heading)
                            sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                            sheet.write_number(row, col + 42, house_rent_total, main_heading)
                            sheet.write_number(row, col + 43, house_500_total, main_heading)
                            sheet.write_number(row, col + 44, food_total, main_heading)
                            sheet.write_number(row, col + 45, work_nature_total, main_heading)
                            sheet.write_number(row, col + 46, gross_total, main_heading)
                            sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 52, net_total, main_heading)
                        else:
                            sheet.write_number(row, col + 40, house_rent_total, main_heading)
                            sheet.write_number(row, col + 41, food_total, main_heading)
                            sheet.write_number(row, col + 42, work_nature_total, main_heading)
                            sheet.write_number(row, col + 43, gross_total, main_heading)
                            sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 49, net_total, main_heading)
                        row += 1
                        grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 1, grand_total, main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_company':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Company"
            sheet.merge_range('A1:AE1', 'مجموعة تقرير معلومات رواتب الموظف حسب الشركة', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Company', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Department', main_heading2)
            sheet.write(row, col + 8, 'Work Location', main_heading2)
            sheet.write(row, col + 9, 'Jop Position', main_heading2)
            sheet.write(row, col + 10, 'Employ Status', main_heading2)
            sheet.write(row, col + 11, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 12, 'Is Driver?', main_heading2)
            sheet.write(row, col + 13, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 14, 'Company Name', main_heading2)
            sheet.write(row, col + 15, 'User Name', main_heading2)
            sheet.write(row, col + 16, 'Partner Name', main_heading2)
            sheet.write(row, col + 17, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 18, 'Mobile No.', main_heading2)
            sheet.write(row, col + 19, 'Nationality', main_heading2)
            sheet.write(row, col + 20, 'ID No.', main_heading2)
            sheet.write(row, col + 21, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 22, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 23, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 24, 'Bank Name', main_heading2)
            sheet.write(row, col + 25, 'Tags', main_heading2)
            sheet.write(row, col + 26, 'Date of Birth', main_heading2)
            sheet.write(row, col + 27, 'Date of Join', main_heading2)
            sheet.write(row, col + 28, 'End Service Date', main_heading2)
            sheet.write(row, col + 29, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 30, 'leave start date', main_heading2)
            sheet.write(row, col + 31, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 32, 'Gender', main_heading2)
            sheet.write(row, col + 33, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 35, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 36, 'Analytic Account', main_heading2)
            sheet.write(row, col + 37, 'Salary Structure', main_heading2)
            sheet.write(row, col + 38, 'Wage', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'Transport', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'House Rent', main_heading2)
                sheet.write(row, col + 44, 'Food', main_heading2)
                sheet.write(row, col + 45, 'Work Nature', main_heading2)
                sheet.write(row, col + 46, 'Gross', main_heading2)
                sheet.write(row, col + 47, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 48, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 40, 'House Rent', main_heading2)
                sheet.write(row, col + 41, 'Food', main_heading2)
                sheet.write(row, col + 42, 'Work Nature', main_heading2)
                sheet.write(row, col + 43, 'Gross', main_heading2)
                sheet.write(row, col + 44, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 45, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'الادارة', main_heading2)
            sheet.write(row, col + 8, 'مكان العمل', main_heading2)
            sheet.write(row, col + 9, 'الوظيفه', main_heading2)
            sheet.write(row, col + 10, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 11, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 12, 'سائق ؟', main_heading2)
            sheet.write(row, col + 13, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 14, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 15, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 16, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 17, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 18, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 19, 'الجنسية', main_heading2)
            sheet.write(row, col + 20, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 21, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 22, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 23, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 24, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 25, 'الوسم', main_heading2)
            sheet.write(row, col + 26, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 27, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 28, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 29, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 31, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 32, 'الجنس', main_heading2)
            sheet.write(row, col + 33, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 34, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 35, 'حالة العقد', main_heading2)
            sheet.write(row, col + 36, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 37, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 38, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 39, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 41, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن', main_heading2)
                sheet.write(row, col + 43, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 44, 'بدل طعام', main_heading2)
                sheet.write(row, col + 45, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 46, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 47, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 48, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 40, 'بدل سكن', main_heading2)
                sheet.write(row, col + 41, 'بدل طعام', main_heading2)
                sheet.write(row, col + 42, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 43, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 44, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 45, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'صافي الراتب', main_heading2)
            row += 1
            company_list = []
            grand_total = 0
            company_ids = self.env['res.company'].search([])
            for company_id in company_ids:
                if company_id:
                    company_list.append(company_id.name)
            for company_name in company_list:
                if company_name:
                    company_employee_ids = employee_ids.filtered(lambda r: r.company_id.name == company_name)
                    if company_employee_ids:
                        total = 0
                        wage_total = 0.0
                        transport_total = 0.0
                        transport_300_total = 0.0
                        transport_1500_total = 0.0
                        house_rent_total = 0.0
                        house_500_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        sheet.write(row, col, 'Company', main_heading2)
                        sheet.write_string(row, col + 1, str(company_name), main_heading)
                        sheet.write(row, col + 2, 'شركة', main_heading2)
                        row += 1
                        for employee_id in company_employee_ids:
                            if employee_id:
                                gross = 0.0
                                transport = 0.0
                                transport_300 = 0.0
                                transport_1500 = 0.0
                                house = 0.0
                                house_500 = 0.0
                                food_allowance = 0.0
                                work_nature_allowance = 0.0
                                fixed_add_allowance = 0.0
                                fixed_deduct_amount = 0.0
                                saudi_gosi_10 = 0.0
                                company_gosi_12 = 0.0
                                company_gosi_22 = 0.0
                                net = 0.0
                                gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                                transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                                transport300_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CA22')
                                transport1500_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CA23')
                                house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                                house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                                house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                                saudi_gosi_10_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'GOSI')
                                company_gosi_12_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CGOSI')
                                company_gosi_22_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FCGOSI')
                                net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                                food_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FA')
                                work_nature_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'NWA')
                                fixed_add_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FAA')
                                fixed_deduct_amount_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'DEDFIXD')
                                if gross_id:
                                    gross = gross_id.total
                                if transport_id:
                                    transport = transport_id.total
                                if transport300_id:
                                    transport_300 = transport300_id.total
                                if transport1500_id:
                                    transport_1500 = transport1500_id.total
                                if house_id:
                                    house = house_id.total
                                if house_id_1:
                                    house = house_id_1.total
                                if house500_id:
                                    house_500 = house500_id.total
                                if saudi_gosi_10_id:
                                    saudi_gosi_10 = saudi_gosi_10_id.total
                                if company_gosi_12_id:
                                    company_gosi_12 = company_gosi_12_id.total
                                if company_gosi_22_id:
                                    company_gosi_22 = company_gosi_22_id.total
                                if net_id:
                                    net = net_id.total
                                if food_allowance_id:
                                    food_allowance = food_allowance_id.total
                                if work_nature_allowance_id:
                                    work_nature_allowance = work_nature_allowance_id.total
                                if fixed_add_allowance_id:
                                    fixed_add_allowance = fixed_add_allowance_id.total
                                if fixed_deduct_amount_id:
                                    fixed_deduct_amount = fixed_deduct_amount_id.total
                                contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                if employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                if employee_id.name:
                                    sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                if employee_id.name_english:
                                    sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                if employee_id.parent_id.name:
                                    sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                                if employee_id.branch_id.region.bsg_region_name:
                                    sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                                       main_heading)
                                if employee_id.branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                                       main_heading)
                                if employee_id.department_id.display_name:
                                    sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                                       main_heading)
                                if employee_id.work_location:
                                    sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                                if employee_id.job_id.name:
                                    sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                                if employee_id.employee_state:
                                    sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                                if employee_id.suspend_salary:
                                    sheet.write_string(row, col + 11, str('True'), main_heading)
                                if employee_id.is_driver:
                                    sheet.write_string(row, col + 12, str('Driver'), main_heading)
                                if employee_id.guarantor_id.name:
                                    sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                                if employee_id.company_id.name:
                                    sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                                if employee_id.user_id.name:
                                    sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                                if employee_id.partner_id.name:
                                    sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                                if employee_id.country_id.name:
                                    sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                                if employee_id.country_id:
                                    if employee_id.country_id.code == 'SA':
                                        if employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if employee_id.bsg_bank_id.bsg_acc_number:
                                    sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                    sheet.write_string(row, col + 22,
                                                       str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                       main_heading)
                                if employee_id.salary_payment_method:
                                    sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_bank_name:
                                    sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                                       main_heading)
                                if employee_id.category_ids:
                                    rec_names = employee_id.category_ids.mapped('name')
                                    names = ','.join(rec_names)
                                    sheet.write_string(row, col + 25, str(names), main_heading)
                                if employee_id.birthday:
                                    sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                                if employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                                if employee_id.end_service_date:
                                    sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                                if employee_id.remaining_leaves:
                                    sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                                if employee_id.leave_start_date:
                                    sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                                if employee_id.gender:
                                    sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                                if contract_id.date_start:
                                    sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                                if contract_id.date_end:
                                    sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                                if contract_id.state:
                                    if contract_id.state == 'draft':
                                        sheet.write_string(row, col + 35, str("New"), main_heading)
                                    if contract_id.state == 'open':
                                        sheet.write_string(row, col + 35, str("Running"), main_heading)
                                    if contract_id.state == 'pending':
                                        sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                                    if contract_id.state == 'close':
                                        sheet.write_string(row, col + 35, str("Expired"), main_heading)
                                    if contract_id.state == 'cancel':
                                        sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                                if contract_id.analytic_account_id:
                                    sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                                       main_heading)
                                if employee_id.salary_structure.name:
                                    sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                                       main_heading)
                                if contract_id.wage:
                                    sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                                    print('wage=', contract_id.wage)
                                    wage_total += contract_id.wage
                                    print('wage total=', wage_total)
                                if transport:
                                    sheet.write_number(row, col + 39, transport, main_heading)
                                    transport_total += transport
                                if self.env.user.company_id.company_code == "BIC":
                                    if transport_300:
                                        sheet.write_number(row, col + 40, transport_300, main_heading)
                                        transport_300_total += transport_300
                                    if transport_1500:
                                        sheet.write_number(row, col + 41, transport_1500, main_heading)
                                        transport_1500_total += transport_1500
                                    if house:
                                        sheet.write_number(row, col + 42, house, main_heading)
                                        house_rent_total += house
                                    if house_500:
                                        sheet.write_number(row, col + 43, house_500, main_heading)
                                        house_500_total += house_500
                                    if food_allowance:
                                        sheet.write_number(row, col + 44, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 46, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 52, net, main_heading)
                                        net_total += net
                                else:
                                    if house:
                                        sheet.write_number(row, col + 40, house, main_heading)
                                        house_rent_total += house
                                    if food_allowance:
                                        sheet.write_number(row, col + 41, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 43, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 49, net, main_heading)
                                        net_total += net
                                row += 1
                                total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_number(row, col + 1, total, main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        sheet.write_number(row, col + 38, wage_total, main_heading)
                        sheet.write_number(row, col + 39, transport_total, main_heading)
                        if self.env.user.company_id.company_code == "BIC":
                            sheet.write_number(row, col + 40, transport_300_total, main_heading)
                            sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                            sheet.write_number(row, col + 42, house_rent_total, main_heading)
                            sheet.write_number(row, col + 43, house_500_total, main_heading)
                            sheet.write_number(row, col + 44, food_total, main_heading)
                            sheet.write_number(row, col + 45, work_nature_total, main_heading)
                            sheet.write_number(row, col + 46, gross_total, main_heading)
                            sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 52, net_total, main_heading)
                        else:
                            sheet.write_number(row, col + 40, house_rent_total, main_heading)
                            sheet.write_number(row, col + 41, food_total, main_heading)
                            sheet.write_number(row, col + 42, work_nature_total, main_heading)
                            sheet.write_number(row, col + 43, gross_total, main_heading)
                            sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 49, net_total, main_heading)
                        row += 1
                        grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 1, grand_total, main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_salary_payment_method':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Salary Payment Method"
            sheet.merge_range('A1:AE1', 'مجموعة تقرير معلومات راتب الموظف حسب طريقة دفع الراتب', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Salary Payment Method', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Department', main_heading2)
            sheet.write(row, col + 8, 'Work Location', main_heading2)
            sheet.write(row, col + 9, 'Jop Position', main_heading2)
            sheet.write(row, col + 10, 'Employ Status', main_heading2)
            sheet.write(row, col + 11, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 12, 'Is Driver?', main_heading2)
            sheet.write(row, col + 13, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 14, 'Company Name', main_heading2)
            sheet.write(row, col + 15, 'User Name', main_heading2)
            sheet.write(row, col + 16, 'Partner Name', main_heading2)
            sheet.write(row, col + 17, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 18, 'Mobile No.', main_heading2)
            sheet.write(row, col + 19, 'Nationality', main_heading2)
            sheet.write(row, col + 20, 'ID No.', main_heading2)
            sheet.write(row, col + 21, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 22, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 23, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 24, 'Bank Name', main_heading2)
            sheet.write(row, col + 25, 'Tags', main_heading2)
            sheet.write(row, col + 26, 'Date of Birth', main_heading2)
            sheet.write(row, col + 27, 'Date of Join', main_heading2)
            sheet.write(row, col + 28, 'End Service Date', main_heading2)
            sheet.write(row, col + 29, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 30, 'leave start date', main_heading2)
            sheet.write(row, col + 31, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 32, 'Gender', main_heading2)
            sheet.write(row, col + 33, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 35, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 36, 'Analytic Account', main_heading2)
            sheet.write(row, col + 37, 'Salary Structure', main_heading2)
            sheet.write(row, col + 38, 'Wage', main_heading2)
            sheet.write(row, col + 39, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'Transport', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'House Rent', main_heading2)
                sheet.write(row, col + 44, 'Food', main_heading2)
                sheet.write(row, col + 45, 'Work Nature', main_heading2)
                sheet.write(row, col + 46, 'Gross', main_heading2)
                sheet.write(row, col + 47, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 48, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 40, 'House Rent', main_heading2)
                sheet.write(row, col + 41, 'Food', main_heading2)
                sheet.write(row, col + 42, 'Work Nature', main_heading2)
                sheet.write(row, col + 43, 'Gross', main_heading2)
                sheet.write(row, col + 44, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 45, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'الادارة', main_heading2)
            sheet.write(row, col + 8, 'مكان العمل', main_heading2)
            sheet.write(row, col + 9, 'الوظيفه', main_heading2)
            sheet.write(row, col + 10, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 11, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 12, 'سائق ؟', main_heading2)
            sheet.write(row, col + 13, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 14, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 15, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 16, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 17, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 18, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 19, 'الجنسية', main_heading2)
            sheet.write(row, col + 20, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 21, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 22, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 23, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 24, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 25, 'الوسم', main_heading2)
            sheet.write(row, col + 26, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 27, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 28, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 29, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 31, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 32, 'الجنس', main_heading2)
            sheet.write(row, col + 33, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 34, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 35, 'حالة العقد', main_heading2)
            sheet.write(row, col + 36, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 37, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 38, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 39, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 41, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن', main_heading2)
                sheet.write(row, col + 43, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 44, 'بدل طعام', main_heading2)
                sheet.write(row, col + 45, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 46, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 47, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 48, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 40, 'بدل سكن', main_heading2)
                sheet.write(row, col + 41, 'بدل طعام', main_heading2)
                sheet.write(row, col + 42, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 43, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 44, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 45, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'صافي الراتب', main_heading2)
            row += 1
            grand_total = 0
            bank_employee_ids = employee_ids.filtered(lambda r: r.salary_payment_method == 'bank')
            cash_employee_ids = employee_ids.filtered(lambda r: r.salary_payment_method == 'cash')
            if bank_employee_ids:
                total = 0
                wage_total = 0.0
                transport_total = 0.0
                transport_300_total = 0.0
                transport_1500_total = 0.0
                house_rent_total = 0.0
                house_500_total = 0.0
                food_total = 0.0
                work_nature_total = 0.0
                gross_total = 0.0
                fixed_additional_total = 0.0
                fixed_deduction_total = 0.0
                saudi_gosi_total = 0.0
                company_gosi_12_total = 0.0
                company_gosi_22_total = 0.0
                net_total = 0.0
                sheet.write(row, col, 'Salary Payment Method', main_heading2)
                sheet.write_string(row, col + 1,'Bank', main_heading)
                sheet.write(row, col + 2, 'طريقة دفع الراتب', main_heading2)
                row += 1
                for employee_id in bank_employee_ids:
                    if employee_id:
                        gross = 0.0
                        transport = 0.0
                        transport_300 = 0.0
                        transport_1500 = 0.0
                        house = 0.0
                        house_500 = 0.0
                        food_allowance = 0.0
                        work_nature_allowance = 0.0
                        fixed_add_allowance = 0.0
                        fixed_deduct_amount = 0.0
                        saudi_gosi_10 = 0.0
                        company_gosi_12 = 0.0
                        company_gosi_22 = 0.0
                        net = 0.0
                        gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                        transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                        transport300_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA22')
                        transport1500_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CA23')
                        house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                        house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                        house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                        saudi_gosi_10_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'GOSI')
                        company_gosi_12_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CGOSI')
                        company_gosi_22_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FCGOSI')
                        net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                        food_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FA')
                        work_nature_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'NWA')
                        fixed_add_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FAA')
                        fixed_deduct_amount_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'DEDFIXD')
                        if gross_id:
                            gross = gross_id.total
                        if transport_id:
                            transport = transport_id.total
                        if transport300_id:
                            transport_300 = transport300_id.total
                        if transport1500_id:
                            transport_1500 = transport1500_id.total
                        if house_id:
                            house = house_id.total
                        if house_id_1:
                            house = house_id_1.total
                        if house500_id:
                            house_500 = house500_id.total
                        if saudi_gosi_10_id:
                            saudi_gosi_10 = saudi_gosi_10_id.total
                        if company_gosi_12_id:
                            company_gosi_12 = company_gosi_12_id.total
                        if company_gosi_22_id:
                            company_gosi_22 = company_gosi_22_id.total
                        if net_id:
                            net = net_id.total
                        if food_allowance_id:
                            food_allowance = food_allowance_id.total
                        if work_nature_allowance_id:
                            work_nature_allowance = work_nature_allowance_id.total
                        if fixed_add_allowance_id:
                            fixed_add_allowance = fixed_add_allowance_id.total
                        if fixed_deduct_amount_id:
                            fixed_deduct_amount = fixed_deduct_amount_id.total
                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                        if employee_id.driver_code:
                            sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                        if employee_id.employee_code:
                            sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                        if employee_id.name:
                            sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                        if employee_id.name_english:
                            sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                        if employee_id.parent_id.name:
                            sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                        if employee_id.branch_id.region.bsg_region_name:
                            sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                               main_heading)
                        if employee_id.branch_id.branch_ar_name:
                            sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                               main_heading)
                        if employee_id.department_id.display_name:
                            sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                               main_heading)
                        if employee_id.work_location:
                            sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                        if employee_id.job_id.name:
                            sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                        if employee_id.employee_state:
                            sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                        if employee_id.suspend_salary:
                            sheet.write_string(row, col + 11, str('True'), main_heading)
                        if employee_id.is_driver:
                            sheet.write_string(row, col + 12, str('Driver'), main_heading)
                        if employee_id.guarantor_id.name:
                            sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                        if employee_id.company_id.name:
                            sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                        if employee_id.user_id.name:
                            sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                        if employee_id.partner_id.name:
                            sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                        if employee_id.mobile_phone:
                            sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                        if employee_id.country_id.name:
                            sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                        if employee_id.country_id:
                            if employee_id.country_id.code == 'SA':
                                if employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_national_id.bsg_nationality_name),
                                                       main_heading)
                            else:
                                if employee_id.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                        if employee_id.bsg_bank_id.bsg_acc_number:
                            sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                            sheet.write_string(row, col + 22,
                                               str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                               main_heading)
                        if employee_id.salary_payment_method:
                            sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_bank_name:
                            sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                               main_heading)
                        if employee_id.category_ids:
                            rec_names = employee_id.category_ids.mapped('name')
                            names = ','.join(rec_names)
                            sheet.write_string(row, col + 25, str(names), main_heading)
                        if employee_id.birthday:
                            sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                        if employee_id.bsgjoining_date:
                            sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                        if employee_id.end_service_date:
                            sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                        if employee_id.remaining_leaves:
                            sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                        if employee_id.leave_start_date:
                            sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                        if employee_id.gender:
                            sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                        if contract_id.date_start:
                            sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                        if contract_id.date_end:
                            sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                        if contract_id.state:
                            if contract_id.state == 'draft':
                                sheet.write_string(row, col + 35, str("New"), main_heading)
                            if contract_id.state == 'open':
                                sheet.write_string(row, col + 35, str("Running"), main_heading)
                            if contract_id.state == 'pending':
                                sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                            if contract_id.state == 'close':
                                sheet.write_string(row, col + 35, str("Expired"), main_heading)
                            if contract_id.state == 'cancel':
                                sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                        if contract_id.analytic_account_id:
                            sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                               main_heading)
                        if employee_id.salary_structure.name:
                            sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                               main_heading)
                        if contract_id.wage:
                            sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                            print('wage=', contract_id.wage)
                            wage_total += contract_id.wage
                            print('wage total=', wage_total)
                        if transport:
                            sheet.write_number(row, col + 39, transport, main_heading)
                            transport_total += transport
                        if self.env.user.company_id.company_code == "BIC":
                            if transport_300:
                                sheet.write_number(row, col + 40, transport_300, main_heading)
                                transport_300_total += transport_300
                            if transport_1500:
                                sheet.write_number(row, col + 41, transport_1500, main_heading)
                                transport_1500_total += transport_1500
                            if house:
                                sheet.write_number(row, col + 42, house, main_heading)
                                house_rent_total += house
                            if house_500:
                                sheet.write_number(row, col + 43, house_500, main_heading)
                                house_500_total += house_500
                            if food_allowance:
                                sheet.write_number(row, col + 44, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 46, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 52, net, main_heading)
                                net_total += net
                        else:
                            if house:
                                sheet.write_number(row, col + 40, house, main_heading)
                                house_rent_total += house
                            if food_allowance:
                                sheet.write_number(row, col + 41, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 43, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 49, net, main_heading)
                                net_total += net
                        row += 1
                        total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 1, total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                sheet.write_number(row, col + 38, wage_total, main_heading)
                sheet.write_number(row, col + 39, transport_total, main_heading)
                if self.env.user.company_id.company_code == "BIC":
                    sheet.write_number(row, col + 40, transport_300_total, main_heading)
                    sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                    sheet.write_number(row, col + 42, house_rent_total, main_heading)
                    sheet.write_number(row, col + 43, house_500_total, main_heading)
                    sheet.write_number(row, col + 44, food_total, main_heading)
                    sheet.write_number(row, col + 45, work_nature_total, main_heading)
                    sheet.write_number(row, col + 46, gross_total, main_heading)
                    sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 52, net_total, main_heading)
                else:
                    sheet.write_number(row, col + 40, house_rent_total, main_heading)
                    sheet.write_number(row, col + 41, food_total, main_heading)
                    sheet.write_number(row, col + 42, work_nature_total, main_heading)
                    sheet.write_number(row, col + 43, gross_total, main_heading)
                    sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 49, net_total, main_heading)
                row += 1
                grand_total += total
            if cash_employee_ids:
                total = 0
                wage_total = 0.0
                transport_total = 0.0
                transport_300_total = 0.0
                transport_1500_total = 0.0
                house_rent_total = 0.0
                house_500_total = 0.0
                food_total = 0.0
                work_nature_total = 0.0
                gross_total = 0.0
                fixed_additional_total = 0.0
                fixed_deduction_total = 0.0
                saudi_gosi_total = 0.0
                company_gosi_12_total = 0.0
                company_gosi_22_total = 0.0
                net_total = 0.0
                sheet.write(row, col, 'Salary Payment Method', main_heading2)
                sheet.write_string(row, col + 1, 'Cash', main_heading)
                sheet.write(row, col + 2, 'طريقة دفع الراتب', main_heading2)
                row += 1
                for employee_id in cash_employee_ids:
                    if employee_id:
                        gross = 0.0
                        transport = 0.0
                        transport_300 = 0.0
                        transport_1500 = 0.0
                        house = 0.0
                        house_500 = 0.0
                        food_allowance = 0.0
                        work_nature_allowance = 0.0
                        fixed_add_allowance = 0.0
                        fixed_deduct_amount = 0.0
                        saudi_gosi_10 = 0.0
                        company_gosi_12 = 0.0
                        company_gosi_22 = 0.0
                        net = 0.0
                        gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                        transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                        transport300_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA22')
                        transport1500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA23')
                        house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                        house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                        house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                        saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GOSI')
                        company_gosi_12_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CGOSI')
                        company_gosi_22_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FCGOSI')
                        net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                        food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'FA')
                        work_nature_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'NWA')
                        fixed_add_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FAA')
                        fixed_deduct_amount_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'DEDFIXD')
                        if gross_id:
                            gross = gross_id.total
                        if transport_id:
                            transport = transport_id.total
                        if transport300_id:
                            transport_300 = transport300_id.total
                        if transport1500_id:
                            transport_1500 = transport1500_id.total
                        if house_id:
                            house = house_id.total
                        if house_id_1:
                            house = house_id_1.total
                        if house500_id:
                            house_500 = house500_id.total
                        if saudi_gosi_10_id:
                            saudi_gosi_10 = saudi_gosi_10_id.total
                        if company_gosi_12_id:
                            company_gosi_12 = company_gosi_12_id.total
                        if company_gosi_22_id:
                            company_gosi_22 = company_gosi_22_id.total
                        if net_id:
                            net = net_id.total
                        if food_allowance_id:
                            food_allowance = food_allowance_id.total
                        if work_nature_allowance_id:
                            work_nature_allowance = work_nature_allowance_id.total
                        if fixed_add_allowance_id:
                            fixed_add_allowance = fixed_add_allowance_id.total
                        if fixed_deduct_amount_id:
                            fixed_deduct_amount = fixed_deduct_amount_id.total
                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                        if employee_id.driver_code:
                            sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                        if employee_id.employee_code:
                            sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                        if employee_id.name:
                            sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                        if employee_id.name_english:
                            sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                        if employee_id.parent_id.name:
                            sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                        if employee_id.branch_id.region.bsg_region_name:
                            sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                               main_heading)
                        if employee_id.branch_id.branch_ar_name:
                            sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                               main_heading)
                        if employee_id.department_id.display_name:
                            sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                               main_heading)
                        if employee_id.work_location:
                            sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                        if employee_id.job_id.name:
                            sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                        if employee_id.employee_state:
                            sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                        if employee_id.suspend_salary:
                            sheet.write_string(row, col + 11, str('True'), main_heading)
                        if employee_id.is_driver:
                            sheet.write_string(row, col + 12, str('Driver'), main_heading)
                        if employee_id.guarantor_id.name:
                            sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                        if employee_id.company_id.name:
                            sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                        if employee_id.user_id.name:
                            sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                        if employee_id.partner_id.name:
                            sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                        if employee_id.mobile_phone:
                            sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                        if employee_id.country_id.name:
                            sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                        if employee_id.country_id:
                            if employee_id.country_id.code == 'SA':
                                if employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_national_id.bsg_nationality_name),
                                                       main_heading)
                            else:
                                if employee_id.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                        if employee_id.bsg_bank_id.bsg_acc_number:
                            sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                            sheet.write_string(row, col + 22,
                                               str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                               main_heading)
                        if employee_id.salary_payment_method:
                            sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_bank_name:
                            sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                               main_heading)
                        if employee_id.category_ids:
                            rec_names = employee_id.category_ids.mapped('name')
                            names = ','.join(rec_names)
                            sheet.write_string(row, col + 25, str(names), main_heading)
                        if employee_id.birthday:
                            sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                        if employee_id.bsgjoining_date:
                            sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                        if employee_id.end_service_date:
                            sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                        if employee_id.remaining_leaves:
                            sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                        if employee_id.leave_start_date:
                            sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                        if employee_id.gender:
                            sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                        if contract_id.date_start:
                            sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                        if contract_id.date_end:
                            sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                        if contract_id.state:
                            if contract_id.state == 'draft':
                                sheet.write_string(row, col + 35, str("New"), main_heading)
                            if contract_id.state == 'open':
                                sheet.write_string(row, col + 35, str("Running"), main_heading)
                            if contract_id.state == 'pending':
                                sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                            if contract_id.state == 'close':
                                sheet.write_string(row, col + 35, str("Expired"), main_heading)
                            if contract_id.state == 'cancel':
                                sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                        if contract_id.analytic_account_id:
                            sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                               main_heading)
                        if employee_id.salary_structure.name:
                            sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                               main_heading)
                        if contract_id.wage:
                            sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                            print('wage=', contract_id.wage)
                            wage_total += contract_id.wage
                            print('wage total=', wage_total)
                        if transport:
                            sheet.write_number(row, col + 39, transport, main_heading)
                            transport_total += transport
                        if self.env.user.company_id.company_code == "BIC":
                            if transport_300:
                                sheet.write_number(row, col + 40, transport_300, main_heading)
                                transport_300_total += transport_300
                            if transport_1500:
                                sheet.write_number(row, col + 41, transport_1500, main_heading)
                                transport_1500_total += transport_1500
                            if house:
                                sheet.write_number(row, col + 42, house, main_heading)
                                house_rent_total += house
                            if house_500:
                                sheet.write_number(row, col + 43, house_500, main_heading)
                                house_500_total += house_500
                            if food_allowance:
                                sheet.write_number(row, col + 44, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 46, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 52, net, main_heading)
                                net_total += net
                        else:
                            if house:
                                sheet.write_number(row, col + 40, house, main_heading)
                                house_rent_total += house
                            if food_allowance:
                                sheet.write_number(row, col + 41, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 43, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 49, net, main_heading)
                                net_total += net
                        row += 1
                        total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 1, total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                sheet.write_number(row, col + 38, wage_total, main_heading)
                sheet.write_number(row, col + 39, transport_total, main_heading)
                if self.env.user.company_id.company_code == "BIC":
                    sheet.write_number(row, col + 40, transport_300_total, main_heading)
                    sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                    sheet.write_number(row, col + 42, house_rent_total, main_heading)
                    sheet.write_number(row, col + 43, house_500_total, main_heading)
                    sheet.write_number(row, col + 44, food_total, main_heading)
                    sheet.write_number(row, col + 45, work_nature_total, main_heading)
                    sheet.write_number(row, col + 46, gross_total, main_heading)
                    sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 52, net_total, main_heading)
                else:
                    sheet.write_number(row, col + 40, house_rent_total, main_heading)
                    sheet.write_number(row, col + 41, food_total, main_heading)
                    sheet.write_number(row, col + 42, work_nature_total, main_heading)
                    sheet.write_number(row, col + 43, gross_total, main_heading)
                    sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 49, net_total, main_heading)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 1, grand_total, main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_is_driver':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Driver/Non Driver"
            sheet.merge_range('A1:AE1', 'مجموعة تقرير معلومات رواتب الموظف حسب السائق / غير السائق', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Driver/Non Driver', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Department', main_heading2)
            sheet.write(row, col + 8, 'Work Location', main_heading2)
            sheet.write(row, col + 9, 'Jop Position', main_heading2)
            sheet.write(row, col + 10, 'Employ Status', main_heading2)
            sheet.write(row, col + 11, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 12, 'Is Driver?', main_heading2)
            sheet.write(row, col + 13, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 14, 'Company Name', main_heading2)
            sheet.write(row, col + 15, 'User Name', main_heading2)
            sheet.write(row, col + 16, 'Partner Name', main_heading2)
            sheet.write(row, col + 17, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 18, 'Mobile No.', main_heading2)
            sheet.write(row, col + 19, 'Nationality', main_heading2)
            sheet.write(row, col + 20, 'ID No.', main_heading2)
            sheet.write(row, col + 21, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 22, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 23, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 24, 'Bank Name', main_heading2)
            sheet.write(row, col + 25, 'Tags', main_heading2)
            sheet.write(row, col + 26, 'Date of Birth', main_heading2)
            sheet.write(row, col + 27, 'Date of Join', main_heading2)
            sheet.write(row, col + 28, 'End Service Date', main_heading2)
            sheet.write(row, col + 29, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 30, 'leave start date', main_heading2)
            sheet.write(row, col + 31, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 32, 'Gender', main_heading2)
            sheet.write(row, col + 33, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 35, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 36, 'Analytic Account', main_heading2)
            sheet.write(row, col + 37, 'Salary Structure', main_heading2)
            sheet.write(row, col + 38, 'Wage', main_heading2)
            sheet.write(row, col + 39, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'Transport', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'House Rent', main_heading2)
                sheet.write(row, col + 44, 'Food', main_heading2)
                sheet.write(row, col + 45, 'Work Nature', main_heading2)
                sheet.write(row, col + 46, 'Gross', main_heading2)
                sheet.write(row, col + 47, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 48, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 40, 'House Rent', main_heading2)
                sheet.write(row, col + 41, 'Food', main_heading2)
                sheet.write(row, col + 42, 'Work Nature', main_heading2)
                sheet.write(row, col + 43, 'Gross', main_heading2)
                sheet.write(row, col + 44, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 45, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'الادارة', main_heading2)
            sheet.write(row, col + 8, 'مكان العمل', main_heading2)
            sheet.write(row, col + 9, 'الوظيفه', main_heading2)
            sheet.write(row, col + 10, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 11, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 12, 'سائق ؟', main_heading2)
            sheet.write(row, col + 13, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 14, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 15, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 16, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 17, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 18, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 19, 'الجنسية', main_heading2)
            sheet.write(row, col + 20, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 21, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 22, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 23, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 24, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 25, 'الوسم', main_heading2)
            sheet.write(row, col + 26, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 27, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 28, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 29, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 31, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 32, 'الجنس', main_heading2)
            sheet.write(row, col + 33, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 34, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 35, 'حالة العقد', main_heading2)
            sheet.write(row, col + 36, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 37, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 38, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 39, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 41, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن', main_heading2)
                sheet.write(row, col + 43, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 44, 'بدل طعام', main_heading2)
                sheet.write(row, col + 45, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 46, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 47, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 48, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 40, 'بدل سكن', main_heading2)
                sheet.write(row, col + 41, 'بدل طعام', main_heading2)
                sheet.write(row, col + 42, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 43, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 44, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 45, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'صافي الراتب', main_heading2)
            row += 1
            grand_total = 0
            driver_ids = employee_ids.filtered(lambda r:r.is_driver)
            non_driver_ids = employee_ids.filtered(lambda r:not r.is_driver)
            if driver_ids:
                total = 0
                wage_total = 0.0
                transport_total = 0.0
                transport_300_total = 0.0
                transport_1500_total = 0.0
                house_rent_total = 0.0
                house_500_total = 0.0
                food_total = 0.0
                work_nature_total = 0.0
                gross_total = 0.0
                fixed_additional_total = 0.0
                fixed_deduction_total = 0.0
                saudi_gosi_total = 0.0
                company_gosi_12_total = 0.0
                company_gosi_22_total = 0.0
                net_total = 0.0
                sheet.write(row, col, 'Is Driver?', main_heading2)
                sheet.write_string(row, col + 1, str('Driver'), main_heading)
                sheet.write(row, col + 2, 'هل السائق؟', main_heading2)
                row += 1
                for employee_id in driver_ids:
                    if employee_id:
                        gross = 0.0
                        transport = 0.0
                        transport_300 = 0.0
                        transport_1500 = 0.0
                        house = 0.0
                        house_500 = 0.0
                        food_allowance = 0.0
                        work_nature_allowance = 0.0
                        fixed_add_allowance = 0.0
                        fixed_deduct_amount = 0.0
                        saudi_gosi_10 = 0.0
                        company_gosi_12 = 0.0
                        company_gosi_22 = 0.0
                        net = 0.0
                        gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                        transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                        transport300_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA22')
                        transport1500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA23')
                        house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                        house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                        house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                        saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GOSI')
                        company_gosi_12_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CGOSI')
                        company_gosi_22_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FCGOSI')
                        net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                        food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'FA')
                        work_nature_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'NWA')
                        fixed_add_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FAA')
                        fixed_deduct_amount_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'DEDFIXD')
                        if gross_id:
                            gross = gross_id.total
                        if transport_id:
                            transport = transport_id.total
                        if transport300_id:
                            transport_300 = transport300_id.total
                        if transport1500_id:
                            transport_1500 = transport1500_id.total
                        if house_id:
                            house = house_id.total
                        if house_id_1:
                            house = house_id_1.total
                        if house500_id:
                            house_500 = house500_id.total
                        if saudi_gosi_10_id:
                            saudi_gosi_10 = saudi_gosi_10_id.total
                        if company_gosi_12_id:
                            company_gosi_12 = company_gosi_12_id.total
                        if company_gosi_22_id:
                            company_gosi_22 = company_gosi_22_id.total
                        if net_id:
                            net = net_id.total
                        if food_allowance_id:
                            food_allowance = food_allowance_id.total
                        if work_nature_allowance_id:
                            work_nature_allowance = work_nature_allowance_id.total
                        if fixed_add_allowance_id:
                            fixed_add_allowance = fixed_add_allowance_id.total
                        if fixed_deduct_amount_id:
                            fixed_deduct_amount = fixed_deduct_amount_id.total
                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                        if employee_id.driver_code:
                            sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                        if employee_id.employee_code:
                            sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                        if employee_id.name:
                            sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                        if employee_id.name_english:
                            sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                        if employee_id.parent_id.name:
                            sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                        if employee_id.branch_id.region.bsg_region_name:
                            sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                               main_heading)
                        if employee_id.branch_id.branch_ar_name:
                            sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                               main_heading)
                        if employee_id.department_id.display_name:
                            sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                               main_heading)
                        if employee_id.work_location:
                            sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                        if employee_id.job_id.name:
                            sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                        if employee_id.employee_state:
                            sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                        if employee_id.suspend_salary:
                            sheet.write_string(row, col + 11, str('True'), main_heading)
                        if employee_id.is_driver:
                            sheet.write_string(row, col + 12, str('Driver'), main_heading)
                        if employee_id.guarantor_id.name:
                            sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                        if employee_id.company_id.name:
                            sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                        if employee_id.user_id.name:
                            sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                        if employee_id.partner_id.name:
                            sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                        if employee_id.mobile_phone:
                            sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                        if employee_id.country_id.name:
                            sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                        if employee_id.country_id:
                            if employee_id.country_id.code == 'SA':
                                if employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_national_id.bsg_nationality_name),
                                                       main_heading)
                            else:
                                if employee_id.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                        if employee_id.bsg_bank_id.bsg_acc_number:
                            sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                            sheet.write_string(row, col + 22,
                                               str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                               main_heading)
                        if employee_id.salary_payment_method:
                            sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_bank_name:
                            sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                               main_heading)
                        if employee_id.category_ids:
                            rec_names = employee_id.category_ids.mapped('name')
                            names = ','.join(rec_names)
                            sheet.write_string(row, col + 25, str(names), main_heading)
                        if employee_id.birthday:
                            sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                        if employee_id.bsgjoining_date:
                            sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                        if employee_id.end_service_date:
                            sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                        if employee_id.remaining_leaves:
                            sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                        if employee_id.leave_start_date:
                            sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                        if employee_id.gender:
                            sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                        if contract_id.date_start:
                            sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                        if contract_id.date_end:
                            sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                        if contract_id.state:
                            if contract_id.state == 'draft':
                                sheet.write_string(row, col + 35, str("New"), main_heading)
                            if contract_id.state == 'open':
                                sheet.write_string(row, col + 35, str("Running"), main_heading)
                            if contract_id.state == 'pending':
                                sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                            if contract_id.state == 'close':
                                sheet.write_string(row, col + 35, str("Expired"), main_heading)
                            if contract_id.state == 'cancel':
                                sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                        if contract_id.analytic_account_id:
                            sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                               main_heading)
                        if employee_id.salary_structure.name:
                            sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                               main_heading)
                        if contract_id.wage:
                            sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                            print('wage=', contract_id.wage)
                            wage_total += contract_id.wage
                            print('wage total=', wage_total)
                        if transport:
                            sheet.write_number(row, col + 39, transport, main_heading)
                            transport_total += transport
                        if self.env.user.company_id.company_code == "BIC":
                            if transport_300:
                                sheet.write_number(row, col + 40, transport_300, main_heading)
                                transport_300_total += transport_300
                            if transport_1500:
                                sheet.write_number(row, col + 41, transport_1500, main_heading)
                                transport_1500_total += transport_1500
                            if house:
                                sheet.write_number(row, col + 42, house, main_heading)
                                house_rent_total += house
                            if house_500:
                                sheet.write_number(row, col + 43, house_500, main_heading)
                                house_500_total += house_500
                            if food_allowance:
                                sheet.write_number(row, col + 44, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 46, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 52, net, main_heading)
                                net_total += net
                        else:
                            if house:
                                sheet.write_number(row, col + 40, house, main_heading)
                                house_rent_total += house
                            if food_allowance:
                                sheet.write_number(row, col + 41, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 43, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 49, net, main_heading)
                                net_total += net
                        row += 1
                        total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 1, total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                sheet.write_number(row, col + 38, wage_total, main_heading)
                sheet.write_number(row, col + 39, transport_total, main_heading)
                if self.env.user.company_id.company_code == "BIC":
                    sheet.write_number(row, col + 40, transport_300_total, main_heading)
                    sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                    sheet.write_number(row, col + 42, house_rent_total, main_heading)
                    sheet.write_number(row, col + 43, house_500_total, main_heading)
                    sheet.write_number(row, col + 44, food_total, main_heading)
                    sheet.write_number(row, col + 45, work_nature_total, main_heading)
                    sheet.write_number(row, col + 46, gross_total, main_heading)
                    sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 52, net_total, main_heading)
                else:
                    sheet.write_number(row, col + 40, house_rent_total, main_heading)
                    sheet.write_number(row, col + 41, food_total, main_heading)
                    sheet.write_number(row, col + 42, work_nature_total, main_heading)
                    sheet.write_number(row, col + 43, gross_total, main_heading)
                    sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 49, net_total, main_heading)
                row += 1
                grand_total += total
            if non_driver_ids:
                total = 0
                wage_total = 0.0
                transport_total = 0.0
                transport_300_total = 0.0
                transport_1500_total = 0.0
                house_rent_total = 0.0
                house_500_total = 0.0
                food_total = 0.0
                work_nature_total = 0.0
                gross_total = 0.0
                fixed_additional_total = 0.0
                fixed_deduction_total = 0.0
                saudi_gosi_total = 0.0
                company_gosi_12_total = 0.0
                company_gosi_22_total = 0.0
                net_total = 0.0
                sheet.write(row, col, 'Is Driver?', main_heading2)
                sheet.write_string(row, col + 1, str('Non Driver'), main_heading)
                sheet.write(row, col + 2, 'هل السائق؟', main_heading2)
                row += 1
                for employee_id in non_driver_ids:
                    if employee_id:
                        gross = 0.0
                        transport = 0.0
                        transport_300 = 0.0
                        transport_1500 = 0.0
                        house = 0.0
                        house_500 = 0.0
                        food_allowance = 0.0
                        work_nature_allowance = 0.0
                        fixed_add_allowance = 0.0
                        fixed_deduct_amount = 0.0
                        saudi_gosi_10 = 0.0
                        company_gosi_12 = 0.0
                        company_gosi_22 = 0.0
                        net = 0.0
                        gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                        transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                        transport300_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA22')
                        transport1500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA23')
                        house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                        house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                        house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                        saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GOSI')
                        company_gosi_12_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'CGOSI')
                        company_gosi_22_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FCGOSI')
                        net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                        food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'FA')
                        work_nature_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'NWA')
                        fixed_add_allowance_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'FAA')
                        fixed_deduct_amount_id = employee_id.line_ids.filtered(
                            lambda l: l.code and l.code == 'DEDFIXD')
                        if gross_id:
                            gross = gross_id.total
                        if transport_id:
                            transport = transport_id.total
                        if transport300_id:
                            transport_300 = transport300_id.total
                        if transport1500_id:
                            transport_1500 = transport1500_id.total
                        if house_id:
                            house = house_id.total
                        if house_id_1:
                            house = house_id_1.total
                        if house500_id:
                            house_500 = house500_id.total
                        if saudi_gosi_10_id:
                            saudi_gosi_10 = saudi_gosi_10_id.total
                        if company_gosi_12_id:
                            company_gosi_12 = company_gosi_12_id.total
                        if company_gosi_22_id:
                            company_gosi_22 = company_gosi_22_id.total
                        if net_id:
                            net = net_id.total
                        if food_allowance_id:
                            food_allowance = food_allowance_id.total
                        if work_nature_allowance_id:
                            work_nature_allowance = work_nature_allowance_id.total
                        if fixed_add_allowance_id:
                            fixed_add_allowance = fixed_add_allowance_id.total
                        if fixed_deduct_amount_id:
                            fixed_deduct_amount = fixed_deduct_amount_id.total
                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                        if employee_id.driver_code:
                            sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                        if employee_id.employee_code:
                            sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                        if employee_id.name:
                            sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                        if employee_id.name_english:
                            sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                        if employee_id.parent_id.name:
                            sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                        if employee_id.branch_id.region.bsg_region_name:
                            sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                               main_heading)
                        if employee_id.branch_id.branch_ar_name:
                            sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                               main_heading)
                        if employee_id.department_id.display_name:
                            sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                               main_heading)
                        if employee_id.work_location:
                            sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                        if employee_id.job_id.name:
                            sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                        if employee_id.employee_state:
                            sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                        if employee_id.suspend_salary:
                            sheet.write_string(row, col + 11, str('True'), main_heading)
                        if employee_id.is_driver:
                            sheet.write_string(row, col + 12, str('Driver'), main_heading)
                        if employee_id.guarantor_id.name:
                            sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                        if employee_id.company_id.name:
                            sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                        if employee_id.user_id.name:
                            sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                        if employee_id.partner_id.name:
                            sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                        if employee_id.mobile_phone:
                            sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                        if employee_id.country_id.name:
                            sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                        if employee_id.country_id:
                            if employee_id.country_id.code == 'SA':
                                if employee_id.bsg_national_id.bsg_nationality_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_national_id.bsg_nationality_name),
                                                       main_heading)
                            else:
                                if employee_id.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 20,
                                                       str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                        if employee_id.bsg_bank_id.bsg_acc_number:
                            sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                            sheet.write_string(row, col + 22,
                                               str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                               main_heading)
                        if employee_id.salary_payment_method:
                            sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                               main_heading)
                        if employee_id.bsg_bank_id.bsg_bank_name:
                            sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                               main_heading)
                        if employee_id.category_ids:
                            rec_names = employee_id.category_ids.mapped('name')
                            names = ','.join(rec_names)
                            sheet.write_string(row, col + 25, str(names), main_heading)
                        if employee_id.birthday:
                            sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                        if employee_id.bsgjoining_date:
                            sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                        if employee_id.end_service_date:
                            sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                        if employee_id.remaining_leaves:
                            sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                        if employee_id.leave_start_date:
                            sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                        if employee_id.last_return_date:
                            sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                        if employee_id.gender:
                            sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                        if contract_id.date_start:
                            sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                        if contract_id.date_end:
                            sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                        if contract_id.state:
                            if contract_id.state == 'draft':
                                sheet.write_string(row, col + 35, str("New"), main_heading)
                            if contract_id.state == 'open':
                                sheet.write_string(row, col + 35, str("Running"), main_heading)
                            if contract_id.state == 'pending':
                                sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                            if contract_id.state == 'close':
                                sheet.write_string(row, col + 35, str("Expired"), main_heading)
                            if contract_id.state == 'cancel':
                                sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                        if contract_id.analytic_account_id:
                            sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                               main_heading)
                        if employee_id.salary_structure.name:
                            sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                               main_heading)
                        if contract_id.wage:
                            sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                            print('wage=', contract_id.wage)
                            wage_total += contract_id.wage
                            print('wage total=', wage_total)
                        if transport:
                            sheet.write_number(row, col + 39, transport, main_heading)
                            transport_total += transport
                        if self.env.user.company_id.company_code == "BIC":
                            if transport_300:
                                sheet.write_number(row, col + 40, transport_300, main_heading)
                                transport_300_total += transport_300
                            if transport_1500:
                                sheet.write_number(row, col + 41, transport_1500, main_heading)
                                transport_1500_total += transport_1500
                            if house:
                                sheet.write_number(row, col + 42, house, main_heading)
                                house_rent_total += house
                            if house_500:
                                sheet.write_number(row, col + 43, house_500, main_heading)
                                house_500_total += house_500
                            if food_allowance:
                                sheet.write_number(row, col + 44, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 46, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 52, net, main_heading)
                                net_total += net
                        else:
                            if house:
                                sheet.write_number(row, col + 40, house, main_heading)
                                house_rent_total += house
                            if food_allowance:
                                sheet.write_number(row, col + 41, food_allowance, main_heading)
                                food_total += food_allowance
                            if work_nature_allowance:
                                sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                work_nature_total += work_nature_allowance
                            if gross:
                                sheet.write_number(row, col + 43, gross, main_heading)
                                gross_total += gross
                            if fixed_add_allowance:
                                sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                fixed_additional_total += fixed_add_allowance
                            if fixed_deduct_amount:
                                sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                fixed_deduction_total += fixed_deduct_amount
                            if saudi_gosi_10:
                                sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                saudi_gosi_total += saudi_gosi_10
                            if company_gosi_22:
                                sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                company_gosi_22_total += company_gosi_22
                            if company_gosi_12:
                                sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                company_gosi_12_total += company_gosi_12
                            if net:
                                sheet.write_number(row, col + 49, net, main_heading)
                                net_total += net
                        row += 1
                        total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_number(row, col + 1, total, main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                sheet.write_number(row, col + 38, wage_total, main_heading)
                sheet.write_number(row, col + 39, transport_total, main_heading)
                if self.env.user.company_id.company_code == "BIC":
                    sheet.write_number(row, col + 40, transport_300_total, main_heading)
                    sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                    sheet.write_number(row, col + 42, house_rent_total, main_heading)
                    sheet.write_number(row, col + 43, house_500_total, main_heading)
                    sheet.write_number(row, col + 44, food_total, main_heading)
                    sheet.write_number(row, col + 45, work_nature_total, main_heading)
                    sheet.write_number(row, col + 46, gross_total, main_heading)
                    sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 52, net_total, main_heading)
                else:
                    sheet.write_number(row, col + 40, house_rent_total, main_heading)
                    sheet.write_number(row, col + 41, food_total, main_heading)
                    sheet.write_number(row, col + 42, work_nature_total, main_heading)
                    sheet.write_number(row, col + 43, gross_total, main_heading)
                    sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                    sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                    sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                    sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                    sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                    sheet.write_number(row, col + 49, net_total, main_heading)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 1, grand_total, main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_region':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Information Report Group By Region"
            sheet.merge_range('A1:AE1', 'تقرير معلومات راتب الموظف مجموعة حسب المنطقة', main_heading3)
            sheet.merge_range('A2:AE2', 'Employee Salary Information Report Group By Region', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Manager Name', main_heading2)
            sheet.write(row, col + 5, 'Region', main_heading2)
            sheet.write(row, col + 6, 'Branch', main_heading2)
            sheet.write(row, col + 7, 'Department', main_heading2)
            sheet.write(row, col + 8, 'Work Location', main_heading2)
            sheet.write(row, col + 9, 'Jop Position', main_heading2)
            sheet.write(row, col + 10, 'Employ Status', main_heading2)
            sheet.write(row, col + 11, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 12, 'Is Driver?', main_heading2)
            sheet.write(row, col + 13, 'Guarantor Name', main_heading2)
            sheet.write(row, col + 14, 'Company Name', main_heading2)
            sheet.write(row, col + 15, 'User Name', main_heading2)
            sheet.write(row, col + 16, 'Partner Name', main_heading2)
            sheet.write(row, col + 17, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 18, 'Mobile No.', main_heading2)
            sheet.write(row, col + 19, 'Nationality', main_heading2)
            sheet.write(row, col + 20, 'ID No.', main_heading2)
            sheet.write(row, col + 21, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 22, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 23, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 24, 'Bank Name', main_heading2)
            sheet.write(row, col + 25, 'Tags', main_heading2)
            sheet.write(row, col + 26, 'Date of Birth', main_heading2)
            sheet.write(row, col + 27, 'Date of Join', main_heading2)
            sheet.write(row, col + 28, 'End Service Date', main_heading2)
            sheet.write(row, col + 29, 'Remaining Legal Leaves', main_heading2)
            sheet.write(row, col + 30, 'leave start date', main_heading2)
            sheet.write(row, col + 31, 'Last Leave Return Date', main_heading2)
            sheet.write(row, col + 32, 'Gender', main_heading2)
            sheet.write(row, col + 33, 'Current Contract Start Date', main_heading2)
            sheet.write(row, col + 34, 'Current Contract End Date', main_heading2)
            sheet.write(row, col + 35, 'Current Contract Status', main_heading2)
            sheet.write(row, col + 36, 'Analytic Account', main_heading2)
            sheet.write(row, col + 37, 'Salary Structure', main_heading2)
            sheet.write(row, col + 38, 'Wage', main_heading2)
            sheet.write(row, col + 39, 'Transport', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'Transport', main_heading2)
                sheet.write(row, col + 41, 'Transport', main_heading2)
                sheet.write(row, col + 42, 'House Rent', main_heading2)
                sheet.write(row, col + 43, 'House Rent', main_heading2)
                sheet.write(row, col + 44, 'Food', main_heading2)
                sheet.write(row, col + 45, 'Work Nature', main_heading2)
                sheet.write(row, col + 46, 'Gross', main_heading2)
                sheet.write(row, col + 47, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 48, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'Net Salary', main_heading2)
            else:
                sheet.write(row, col + 40, 'House Rent', main_heading2)
                sheet.write(row, col + 41, 'Food', main_heading2)
                sheet.write(row, col + 42, 'Work Nature', main_heading2)
                sheet.write(row, col + 43, 'Gross', main_heading2)
                sheet.write(row, col + 44, 'Fixed Additional', main_heading2)
                sheet.write(row, col + 45, 'Fixed Deduction', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'اسم المدير', main_heading2)
            sheet.write(row, col + 5, 'منطقة', main_heading2)
            sheet.write(row, col + 6, 'الفرع', main_heading2)
            sheet.write(row, col + 7, 'الادارة', main_heading2)
            sheet.write(row, col + 8, 'مكان العمل', main_heading2)
            sheet.write(row, col + 9, 'الوظيفه', main_heading2)
            sheet.write(row, col + 10, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 11, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 12, 'سائق ؟', main_heading2)
            sheet.write(row, col + 13, 'اسم الكفيل', main_heading2)
            sheet.write(row, col + 14, 'اسم الشركة', main_heading2)
            sheet.write(row, col + 15, 'اسم المستخدم', main_heading2)
            sheet.write(row, col + 16, 'اسم الشريك', main_heading2)
            sheet.write(row, col + 17, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 18, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 19, 'الجنسية', main_heading2)
            sheet.write(row, col + 20, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 21, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 22, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 23, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 24, 'سوفت البنك', main_heading2)
            sheet.write(row, col + 25, 'الوسم', main_heading2)
            sheet.write(row, col + 26, 'تاريخ الميلاد', main_heading2)
            sheet.write(row, col + 27, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 28, 'تاريخ ترك الخدمة', main_heading2)
            sheet.write(row, col + 29, 'رصيد الاجازة', main_heading2)
            sheet.write(row, col + 30, 'تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 31, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 32, 'الجنس', main_heading2)
            sheet.write(row, col + 33, 'تاريخ بدائة العقد', main_heading2)
            sheet.write(row, col + 34, 'تاريخ انتهاء العقد', main_heading2)
            sheet.write(row, col + 35, 'حالة العقد', main_heading2)
            sheet.write(row, col + 36, 'الحساب التحليلي', main_heading2)
            sheet.write(row, col + 37, 'مسير الرواتب', main_heading2)
            sheet.write(row, col + 38, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 39, 'بدل نقل', main_heading2)
            if self.env.user.company_id.company_code == "BIC":
                sheet.write(row, col + 40, 'بدل نقل 300', main_heading2)
                sheet.write(row, col + 41, 'بدل نقل 1500 ', main_heading2)
                sheet.write(row, col + 42, 'بدل سكن', main_heading2)
                sheet.write(row, col + 43, 'بدل سكن 500', main_heading2)
                sheet.write(row, col + 44, 'بدل طعام', main_heading2)
                sheet.write(row, col + 45, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 46, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 47, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 48, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 49, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 50, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 51, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 52, 'صافي الراتب', main_heading2)
            else:
                sheet.write(row, col + 40, 'بدل سكن', main_heading2)
                sheet.write(row, col + 41, 'بدل طعام', main_heading2)
                sheet.write(row, col + 42, 'بدل طبيعية عمل', main_heading2)
                sheet.write(row, col + 43, 'اجمالي المستحق', main_heading2)
                sheet.write(row, col + 44, 'بدل إضافي ثابت', main_heading2)
                sheet.write(row, col + 45, 'الخصم الثابت', main_heading2)
                sheet.write(row, col + 46, 'SAUDI GOSI 10%', main_heading2)
                sheet.write(row, col + 47, 'Company GOSI 22%', main_heading2)
                sheet.write(row, col + 48, 'Company GOSI 12%', main_heading2)
                sheet.write(row, col + 49, 'صافي الراتب', main_heading2)
            row += 1
            region_list = []
            grand_total = 0
            region_ids = self.env['region.config'].search([])
            for region_id in region_ids:
                if region_id:
                    if region_id.bsg_region_name not in region_list:
                        region_list.append(region_id.bsg_region_name)
            for region_name in region_list:
                if region_name:
                    region_employee_ids = employee_ids.filtered(lambda r:r.branch_id.region.bsg_region_name == region_name)
                    if region_employee_ids:
                        total = 0
                        wage_total = 0.0
                        transport_total = 0.0
                        transport_300_total = 0.0
                        transport_1500_total = 0.0
                        house_rent_total = 0.0
                        house_500_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        sheet.write(row, col, 'Region', main_heading2)
                        sheet.write_string(row, col + 1, str(region_name), main_heading)
                        sheet.write(row, col + 2, 'الفرع', main_heading2)
                        row += 1
                        for employee_id in region_employee_ids:
                            if employee_id:
                                gross = 0.0
                                transport = 0.0
                                transport_300 = 0.0
                                transport_1500 = 0.0
                                house = 0.0
                                house_500 = 0.0
                                food_allowance = 0.0
                                work_nature_allowance = 0.0
                                fixed_add_allowance = 0.0
                                fixed_deduct_amount = 0.0
                                saudi_gosi_10 = 0.0
                                company_gosi_12 = 0.0
                                company_gosi_22 = 0.0
                                net = 0.0
                                gross_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GROSS')
                                transport_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA')
                                transport300_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA22')
                                transport1500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'CA23')
                                house_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA2')
                                house_id_1 = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HRA3')
                                house500_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'HA20')
                                saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'GOSI')
                                company_gosi_12_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'CGOSI')
                                company_gosi_22_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FCGOSI')
                                net_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'NET')
                                food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code and l.code == 'FA')
                                work_nature_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'NWA')
                                fixed_add_allowance_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'FAA')
                                fixed_deduct_amount_id = employee_id.line_ids.filtered(
                                    lambda l: l.code and l.code == 'DEDFIXD')
                                if gross_id:
                                    gross = gross_id.total
                                if transport_id:
                                    transport = transport_id.total
                                if transport300_id:
                                    transport_300 = transport300_id.total
                                if transport1500_id:
                                    transport_1500 = transport1500_id.total
                                if house_id:
                                    house = house_id.total
                                if house_id_1:
                                    house = house_id_1.total
                                if house500_id:
                                    house_500 = house500_id.total
                                if saudi_gosi_10_id:
                                    saudi_gosi_10 = saudi_gosi_10_id.total
                                if company_gosi_12_id:
                                    company_gosi_12 = company_gosi_12_id.total
                                if company_gosi_22_id:
                                    company_gosi_22 = company_gosi_22_id.total
                                if net_id:
                                    net = net_id.total
                                if food_allowance_id:
                                    food_allowance = food_allowance_id.total
                                if work_nature_allowance_id:
                                    work_nature_allowance = work_nature_allowance_id.total
                                if fixed_add_allowance_id:
                                    fixed_add_allowance = fixed_add_allowance_id.total
                                if fixed_deduct_amount_id:
                                    fixed_deduct_amount = fixed_deduct_amount_id.total
                                contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],order='date_start desc', limit=1)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                if employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                if employee_id.name:
                                    sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                if employee_id.name_english:
                                    sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                if employee_id.parent_id.name:
                                    sheet.write_string(row, col + 4, str(employee_id.parent_id.name), main_heading)
                                if employee_id.branch_id.region.bsg_region_name:
                                    sheet.write_string(row, col + 5, str(employee_id.branch_id.region.bsg_region_name),
                                                       main_heading)
                                if employee_id.branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 6, str(employee_id.branch_id.branch_ar_name),
                                                       main_heading)
                                if employee_id.department_id.display_name:
                                    sheet.write_string(row, col + 7, str(employee_id.department_id.display_name),
                                                       main_heading)
                                if employee_id.work_location:
                                    sheet.write_string(row, col + 8, str(employee_id.work_location), main_heading)
                                if employee_id.job_id.name:
                                    sheet.write_string(row, col + 9, str(employee_id.job_id.name), main_heading)
                                if employee_id.employee_state:
                                    sheet.write_string(row, col + 10, str(employee_id.employee_state), main_heading)
                                if employee_id.suspend_salary:
                                    sheet.write_string(row, col + 11, str('True'), main_heading)
                                if employee_id.is_driver:
                                    sheet.write_string(row, col + 12, str('Driver'), main_heading)
                                if employee_id.guarantor_id.name:
                                    sheet.write_string(row, col + 13, str(employee_id.guarantor_id.name), main_heading)
                                if employee_id.company_id.name:
                                    sheet.write_string(row, col + 14, str(employee_id.company_id.name), main_heading)
                                if employee_id.user_id.name:
                                    sheet.write_string(row, col + 15, str(employee_id.user_id.name), main_heading)
                                if employee_id.partner_id.name:
                                    sheet.write_string(row, col + 16, str(employee_id.partner_id.name), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 17, str(employee_id.last_return_date), main_heading)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 18, str(employee_id.mobile_phone), main_heading)
                                if employee_id.country_id.name:
                                    sheet.write_string(row, col + 19, str(employee_id.country_id.name), main_heading)
                                if employee_id.country_id:
                                    if employee_id.country_id.code == 'SA':
                                        if employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 20,
                                                               str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if employee_id.bsg_bank_id.bsg_acc_number:
                                    sheet.write_string(row, col + 21, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                    sheet.write_string(row, col + 22,
                                                       str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                       main_heading)
                                if employee_id.salary_payment_method:
                                    sheet.write_string(row, col + 23, str(employee_id.salary_payment_method),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_bank_name:
                                    sheet.write_string(row, col + 24, str(employee_id.bsg_bank_id.bsg_bank_name),
                                                       main_heading)
                                if employee_id.category_ids:
                                    rec_names = employee_id.category_ids.mapped('name')
                                    names = ','.join(rec_names)
                                    sheet.write_string(row, col + 25, str(names), main_heading)
                                if employee_id.birthday:
                                    sheet.write_string(row, col + 26, str(employee_id.birthday), main_heading)
                                if employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 27, str(employee_id.bsgjoining_date), main_heading)
                                if employee_id.end_service_date:
                                    sheet.write_string(row, col + 28, str(employee_id.end_service_date), main_heading)
                                if employee_id.remaining_leaves:
                                    sheet.write_string(row, col + 29, str(employee_id.remaining_leaves), main_heading)
                                if employee_id.leave_start_date:
                                    sheet.write_string(row, col + 30, str(employee_id.leave_start_date), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 31, str(employee_id.last_return_date), main_heading)
                                if employee_id.gender:
                                    sheet.write_string(row, col + 32, str(employee_id.gender), main_heading)
                                if contract_id.date_start:
                                    sheet.write_string(row, col + 33, str(contract_id.date_start), main_heading)
                                if contract_id.date_end:
                                    sheet.write_string(row, col + 34, str(contract_id.date_end), main_heading)
                                if contract_id.state:
                                    if contract_id.state == 'draft':
                                        sheet.write_string(row, col + 35, str("New"), main_heading)
                                    if contract_id.state == 'open':
                                        sheet.write_string(row, col + 35, str("Running"), main_heading)
                                    if contract_id.state == 'pending':
                                        sheet.write_string(row, col + 35, str("To Renew"), main_heading)
                                    if contract_id.state == 'close':
                                        sheet.write_string(row, col + 35, str("Expired"), main_heading)
                                    if contract_id.state == 'cancel':
                                        sheet.write_string(row, col + 35, str("Cancelled"), main_heading)
                                if contract_id.analytic_account_id:
                                    sheet.write_string(row, col + 36, str(contract_id.analytic_account_id.display_name),
                                                       main_heading)
                                if employee_id.salary_structure.name:
                                    sheet.write_string(row, col + 37, str(employee_id.salary_structure.name),
                                                       main_heading)
                                if contract_id.wage:
                                    sheet.write_number(row, col + 38, contract_id.wage, main_heading)
                                    print('wage=', contract_id.wage)
                                    wage_total += contract_id.wage
                                    print('wage total=', wage_total)
                                if transport:
                                    sheet.write_number(row, col + 39, transport, main_heading)
                                    transport_total += transport
                                if self.env.user.company_id.company_code == "BIC":
                                    if transport_300:
                                        sheet.write_number(row, col + 40, transport_300, main_heading)
                                        transport_300_total += transport_300
                                    if transport_1500:
                                        sheet.write_number(row, col + 41, transport_1500, main_heading)
                                        transport_1500_total += transport_1500
                                    if house:
                                        sheet.write_number(row, col + 42, house, main_heading)
                                        house_rent_total += house
                                    if house_500:
                                        sheet.write_number(row, col + 43, house_500, main_heading)
                                        house_500_total += house_500
                                    if food_allowance:
                                        sheet.write_number(row, col + 44, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 45, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 46, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 47, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 48, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 49, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 50, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 51, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 52, net, main_heading)
                                        net_total += net
                                else:
                                    if house:
                                        sheet.write_number(row, col + 40, house, main_heading)
                                        house_rent_total += house
                                    if food_allowance:
                                        sheet.write_number(row, col + 41, food_allowance, main_heading)
                                        food_total += food_allowance
                                    if work_nature_allowance:
                                        sheet.write_number(row, col + 42, work_nature_allowance, main_heading)
                                        work_nature_total += work_nature_allowance
                                    if gross:
                                        sheet.write_number(row, col + 43, gross, main_heading)
                                        gross_total += gross
                                    if fixed_add_allowance:
                                        sheet.write_number(row, col + 44, fixed_add_allowance, main_heading)
                                        fixed_additional_total += fixed_add_allowance
                                    if fixed_deduct_amount:
                                        sheet.write_number(row, col + 45, fixed_deduct_amount, main_heading)
                                        fixed_deduction_total += fixed_deduct_amount
                                    if saudi_gosi_10:
                                        sheet.write_number(row, col + 46, saudi_gosi_10, main_heading)
                                        saudi_gosi_total += saudi_gosi_10
                                    if company_gosi_22:
                                        sheet.write_number(row, col + 47, company_gosi_22, main_heading)
                                        company_gosi_22_total += company_gosi_22
                                    if company_gosi_12:
                                        sheet.write_number(row, col + 48, company_gosi_12, main_heading)
                                        company_gosi_12_total += company_gosi_12
                                    if net:
                                        sheet.write_number(row, col + 49, net, main_heading)
                                        net_total += net
                                row += 1
                                total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_number(row, col + 1, total, main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        sheet.write_number(row, col + 38, wage_total, main_heading)
                        sheet.write_number(row, col + 39, transport_total, main_heading)
                        if self.env.user.company_id.company_code == "BIC":
                            sheet.write_number(row, col + 40, transport_300_total, main_heading)
                            sheet.write_number(row, col + 41, transport_1500_total, main_heading)
                            sheet.write_number(row, col + 42, house_rent_total, main_heading)
                            sheet.write_number(row, col + 43, house_500_total, main_heading)
                            sheet.write_number(row, col + 44, food_total, main_heading)
                            sheet.write_number(row, col + 45, work_nature_total, main_heading)
                            sheet.write_number(row, col + 46, gross_total, main_heading)
                            sheet.write_number(row, col + 47, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 48, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 49, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 50, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 51, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 52, net_total, main_heading)
                        else:
                            sheet.write_number(row, col + 40, house_rent_total, main_heading)
                            sheet.write_number(row, col + 41, food_total, main_heading)
                            sheet.write_number(row, col + 42, work_nature_total, main_heading)
                            sheet.write_number(row, col + 43, gross_total, main_heading)
                            sheet.write_number(row, col + 44, fixed_additional_total, main_heading)
                            sheet.write_number(row, col + 45, fixed_deduction_total, main_heading)
                            sheet.write_number(row, col + 46, saudi_gosi_total, main_heading)
                            sheet.write_number(row, col + 47, company_gosi_22_total, main_heading)
                            sheet.write_number(row, col + 48, company_gosi_12_total, main_heading)
                            sheet.write_number(row, col + 49, net_total, main_heading)
                        row += 1
                        grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_number(row, col + 1, grand_total, main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        # if docs.grouping_by == 'by_sumany':
        #     self.env.ref(
        #         'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Summary Report"
        #     sheet.merge_range('A1:AE1', 'تقرير ملخص راتب الموظف', main_heading3)
        #     row += 1
        #     sheet.merge_range('A2:AE2', 'Employee Salary Summary Report', main_heading3)
        #     row += 2
        #     sheet.write(row, col,'Department', main_heading2)
        #     sheet.write(row, col + 1, 'Branch', main_heading2)
        #     sheet.write(row, col + 2 , 'Region', main_heading2)
        #     sheet.write(row, col + 3, 'Jop Position', main_heading2)
        #     sheet.write(row, col + 4, 'Total Employees', main_heading2)
        #     sheet.write(row, col + 5, 'Wage', main_heading2)
        #     sheet.write(row, col + 6, 'Transport', main_heading2)
        #     sheet.write(row, col + 7, 'House Rent', main_heading2)
        #     sheet.write(row, col + 8, 'Food', main_heading2)
        #     sheet.write(row, col + 9, 'Work Nature', main_heading2)
        #     sheet.write(row, col + 10, 'Gross', main_heading2)
        #     sheet.write(row, col + 11, 'Fixed Additional', main_heading2)
        #     sheet.write(row, col + 12, 'Fixed Deduction', main_heading2)
        #     sheet.write(row, col + 13, 'SAUDI GOSI 10%', main_heading2)
        #     sheet.write(row, col + 14, 'Company GOSI 22%', main_heading2)
        #     sheet.write(row, col + 15, 'Company GOSI 12%', main_heading2)
        #     sheet.write(row, col + 16, 'Net Salary', main_heading2)
        #     row += 1
        #     sheet.write(row, col, 'الادارة', main_heading2)
        #     sheet.write(row, col + 1, 'الفرع', main_heading2)
        #     sheet.write(row, col + 2, 'منطقة', main_heading2)
        #     sheet.write(row, col + 3, 'الوظيفه', main_heading2)
        #     sheet.write(row, col + 4, 'عدد الموظفي', main_heading2)
        #     sheet.write(row, col + 5, 'الراتب الاساسي', main_heading2)
        #     sheet.write(row, col + 6, 'بدل نقل', main_heading2)
        #     sheet.write(row, col + 7, 'بدل سكن', main_heading2)
        #     sheet.write(row, col + 8, 'بدل طعام', main_heading2)
        #     sheet.write(row, col + 9, 'بدل طبيعية عمل', main_heading2)
        #     sheet.write(row, col + 10, 'اجمالي المستحق', main_heading2)
        #     sheet.write(row, col + 11, 'بدل إضافي ثابت', main_heading2)
        #     sheet.write(row, col + 12, 'الخصم الثابت', main_heading2)
        #     sheet.write(row, col + 13, 'SAUDI GOSI 10%', main_heading2)
        #     sheet.write(row, col + 14, 'Company GOSI 22%', main_heading2)
        #     sheet.write(row, col + 15, 'Company GOSI 12%', main_heading2)
        #     sheet.write(row, col + 16, 'صافي الراتب', main_heading2)
        #     row += 1
        #     grand_total = 0
        #     summary_employee_ids = employee_ids.read_group([],fields=['branch_id','department_id','job_id','region_id'],groupby=['department_id','branch_id','job_id','region_id'],lazy=False)
        #     if summary_employee_ids:
        #         for sumary in summary_employee_ids:
        #             # print('...sumary.....',sumary)
        #             filter_summary_employee_ids = employee_ids.filtered(lambda r:(r.branch_id.id == sumary.get('branch_id')[0] if sumary.get('branch_id') else r.branch_id.id == sumary.get('branch_id')) and (r.department_id.id == sumary.get('department_id')[0] if sumary.get('department_id') else r.department_id.id == sumary.get('department_id') ) and (r.job_id.id == sumary.get('job_id')[0] if sumary.get('job_id') else r.job_id.id == sumary.get('job_id')) and (r.region_id.id == sumary.get('region_id')[0] if sumary.get('region_id') else r.region_id.id == sumary.get('region_id')))
        #             print('......filtered employee',filter_summary_employee_ids)
        #             if filter_summary_employee_ids:
        #                 print('......filtered employee', filter_summary_employee_ids)
        #                 wage_total = 0.0
        #                 transport_total = 0.0
        #                 house_rent_total = 0.0
        #                 food_total = 0.0
        #                 work_nature_total = 0.0
        #                 gross_total = 0.0
        #                 fixed_additional_total = 0.0
        #                 fixed_deduction_total = 0.0
        #                 saudi_gosi_total = 0.0
        #                 company_gosi_12_total = 0.0
        #                 company_gosi_22_total = 0.0
        #                 net_total = 0.0
        #                 for employee_id in filter_summary_employee_ids:
        #                     if employee_id:
        #                         contract_id = self.env['hr.contract'].search(
        #                             [('employee_id', '=', employee_id.id), ('state', '=', 'open')],limit=1)
        #                         if contract_id.wage:
        #                             wage_total += contract_id.wage
        #                         if contract_id.food_allowance:
        #                             food_total += contract_id.food_allowance
        #                         if contract_id.work_nature_allowance:
        #                             work_nature_total += contract_id.work_nature_allowance
        #                         if contract_id.fixed_add_allowance:
        #                             fixed_additional_total += contract_id.fixed_add_allowance
        #                         if contract_id.fixed_deduct_amount:
        #                             fixed_deduction_total += contract_id.fixed_deduct_amount
        #                         if employee_id.line_ids:
        #                             gross_id = employee_id.line_ids.filtered(lambda l: l.code == 'GROSS')
        #                             transport_id = employee_id.line_ids.filtered(lambda l: l.code == 'CA')
        #                             house_id = employee_id.line_ids.filtered(lambda l: l.code == 'HRA2')
        #                             house_id_1 = employee_id.line_ids.filtered(lambda l: l.code == 'HRA3')
        #                             saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code == 'GOSI')
        #                             company_gosi_12_id = employee_id.line_ids.filtered(lambda l: l.code == 'CGOSI')
        #                             company_gosi_22_id = employee_id.line_ids.filtered(lambda l: l.code == 'FCGOSI')
        #                             net_id = employee_id.line_ids.filtered(lambda l: l.code == 'NET')
        #                             if gross_id:
        #                                 gross_total += gross_id.total
        #                             if transport_id:
        #                                 transport_total += transport_id.total
        #                             if house_id:
        #                                 house_rent_total += house_id.total
        #                             if house_id_1:
        #                                 house_rent_total += house_id_1.total
        #                             if saudi_gosi_10_id:
        #                                 saudi_gosi_total += saudi_gosi_10_id.total
        #                             if company_gosi_12_id:
        #                                 company_gosi_12_total += company_gosi_12_id.total
        #                             if company_gosi_22_id:
        #                                 company_gosi_22_total += company_gosi_22_id.total
        #                             if net_id:
        #                                 net_total += net_id.total
        #                 if sumary.get('department_id'):
        #                     if docs.is_parent_dempart:
        #                         sheet.write_string(row, col, str(sumary.get('department_id')[1].split()[0]), main_heading)
        #                     else:
        #                         sheet.write_string(row, col, str(sumary.get('department_id')[1]),
        #                                            main_heading)
        #                 if sumary.get('branch_id'):
        #                     sheet.write_string(row, col + 1, str(sumary.get('branch_id')[1]), main_heading)
        #                 if sumary.get('region_id'):
        #                     sheet.write_string(row, col + 2, str(sumary.get('region_id')[1]), main_heading)
        #                 if sumary.get('job_id'):
        #                     sheet.write_string(row, col + 3, str(sumary.get('job_id')[1]), main_heading)
        #                 if sumary.get('__count'):
        #                     sheet.write_string(row, col + 4, str(sumary.get('__count')),
        #                                        main_heading)
        #                 if wage_total:
        #                     sheet.write_string(row, col + 5, wage_total, main_heading)
        #                 if transport_total:
        #                     sheet.write_string(row, col + 6, transport_total, main_heading)
        #                 if house_rent_total:
        #                     sheet.write_string(row, col + 7, house_rent_total, main_heading)
        #                 if food_total:
        #                     sheet.write_string(row, col + 8, food_total, main_heading)
        #                 if work_nature_total:
        #                     sheet.write_string(row, col + 9, work_nature_total, main_heading)
        #                 if gross_total:
        #                     sheet.write_string(row, col + 10, gross_total, main_heading)
        #                 if fixed_additional_total:
        #                     sheet.write_string(row, col + 11, fixed_additional_total, main_heading)
        #                 if fixed_deduction_total:
        #                     sheet.write_string(row, col + 12, fixed_deduction_total, main_heading)
        #                 if saudi_gosi_total:
        #                     sheet.write_string(row, col + 13, saudi_gosi_total, main_heading)
        #                 if company_gosi_22_total:
        #                     sheet.write_string(row, col + 14, company_gosi_22_total, main_heading)
        #                 if company_gosi_12_total:
        #                     sheet.write_string(row, col + 15, company_gosi_12_total, main_heading)
        #                 if net_total:
        #                     sheet.write_string(row, col + 16, net_total, main_heading)
        #                 row+=1
