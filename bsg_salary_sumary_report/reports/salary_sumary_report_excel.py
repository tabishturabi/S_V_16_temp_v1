from odoo import models
from datetime import date, datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import pandas as pd
from num2words import num2words


class SalarySummaryReportExcel(models.AbstractModel):
    _name = 'report.bsg_salary_sumary_report.sumary_report_xlsx'
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
        sheet = workbook.add_worksheet('Employee Salary Summary Report')
        sheet.set_column('A:AE', 15)
        domain=[]
        row = 2
        col = 0
        sheet.write(row, col + 2, 'Print Date', main_heading2)
        sheet.write_string(row, col + 3, str(docs.print_date_time.strftime('%Y-%m-%d %H:%M:%S')), main_heading)
        if docs.employee_ids:
            domain += [('id', 'in', docs.employee_ids.ids)]
            sheet.write(row, col, 'Employees', main_heading2)
            rec_names = docs.employee_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
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
        if docs.company_ids:
            domain += [('company_id', 'in', docs.company_ids.ids)]
            sheet.write(row, col, 'Company', main_heading2)
            rec_names = docs.company_ids.mapped('name')
            names = ','.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
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
        if docs.salary_payment_method == 'bank':
            domain += [('salary_payment_method', '=', 'bank')]
        if docs.salary_payment_method == 'cash':
            domain += [('is_driver', '=', 'cash')]
        if docs.is_driver == 'yes':
            domain += [('is_driver','=',True)]
        if docs.is_driver == 'no':
            domain += [('is_driver','=',False)]
        employee_ids = self.env['hr.employee'].search(domain)
        row+=2
        if docs.grouping_by == 'all':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Summary Report"
            sheet.merge_range('A1:N1', 'تقرير ملخص رواتب الموظفين', main_heading3)
            sheet.merge_range('A2:N2', 'Employee Salary Summary Report', main_heading3)
            sheet.write(row, col,'Department', main_heading2)
            sheet.write(row, col + 1, 'Branch', main_heading2)
            sheet.write(row, col + 2 , 'Region', main_heading2)
            sheet.write(row, col + 3, 'Jop Position', main_heading2)
            sheet.write(row, col + 4, 'Total Employees', main_heading2)
            sheet.write(row, col + 5, 'Wage', main_heading2)
            sheet.write(row, col + 6, 'Transport', main_heading2)
            sheet.write(row, col + 7, 'House Rent', main_heading2)
            sheet.write(row, col + 8, 'Food', main_heading2)
            sheet.write(row, col + 9, 'Work Nature', main_heading2)
            sheet.write(row, col + 10, 'Gross', main_heading2)
            sheet.write(row, col + 11, 'Fixed Additional', main_heading2)
            sheet.write(row, col + 12, 'Fixed Deduction', main_heading2)
            sheet.write(row, col + 13, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 14, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 15, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 16, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'الادارة', main_heading2)
            sheet.write(row, col + 1, 'الفرع', main_heading2)
            sheet.write(row, col + 2, 'منطقة', main_heading2)
            sheet.write(row, col + 3, 'الوظيفه', main_heading2)
            sheet.write(row, col + 4, 'عدد الموظفي', main_heading2)
            sheet.write(row, col + 5, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 6, 'بدل نقل', main_heading2)
            sheet.write(row, col + 7, 'بدل سكن', main_heading2)
            sheet.write(row, col + 8, 'بدل طعام', main_heading2)
            sheet.write(row, col + 9, 'بدل طبيعية عمل', main_heading2)
            sheet.write(row, col + 10, 'اجمالي المستحق', main_heading2)
            sheet.write(row, col + 11, 'بدل إضافي ثابت', main_heading2)
            sheet.write(row, col + 12, 'الخصم الثابت', main_heading2)
            sheet.write(row, col + 13, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 14, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 15, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 16, 'صافي الراتب', main_heading2)
            row += 1
            summary_employee_ids = employee_ids.read_group([],fields=['branch_id','department_id','job_id','region_id'],groupby=['department_id','branch_id','job_id','region_id'],lazy=False)
            if summary_employee_ids:
                employee_grand_total = 0
                wage_grand_total = 0.0
                transport_grand_total = 0.0
                house_rent_grand_total = 0.0
                food_grand_total = 0.0
                work_nature_grand_total = 0.0
                gross_grand_total = 0.0
                fixed_additional_grand_total = 0.0
                fixed_deduction_grand_total = 0.0
                saudi_gosi_grand_total = 0.0
                company_gosi_12_grand_total = 0.0
                company_gosi_22_grand_total = 0.0
                net_grand_total = 0.0
                for sumary in summary_employee_ids:
                    # print('...sumary.....',sumary)
                    filter_summary_employee_ids = employee_ids.filtered(lambda r:(r.branch_id.id == sumary.get('branch_id')[0] if sumary.get('branch_id') else r.branch_id.id == sumary.get('branch_id')) and (r.department_id.id == sumary.get('department_id')[0] if sumary.get('department_id') else r.department_id.id == sumary.get('department_id') ) and (r.job_id.id == sumary.get('job_id')[0] if sumary.get('job_id') else r.job_id.id == sumary.get('job_id')) and (r.region_id.id == sumary.get('region_id')[0] if sumary.get('region_id') else r.region_id.id == sumary.get('region_id')))
                    print('......filtered employee',filter_summary_employee_ids)
                    if filter_summary_employee_ids:
                        print('......filtered employee', filter_summary_employee_ids)
                        wage_total = 0.0
                        transport_total = 0.0
                        house_rent_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        for employee_id in filter_summary_employee_ids:
                            if employee_id:
                                contract_id = self.env['hr.contract'].search(
                                    [('employee_id', '=', employee_id.id), ('state', '=', 'open')],limit=1)
                                if contract_id.wage:
                                    wage_total += contract_id.wage
                                if employee_id.line_ids:
                                    gross_id = employee_id.line_ids.filtered(lambda l: l.code == 'GROSS')
                                    transport_id = employee_id.line_ids.filtered(lambda l: l.code == 'CA')
                                    house_id = employee_id.line_ids.filtered(lambda l: l.code == 'HRA2')
                                    house_id_1 = employee_id.line_ids.filtered(lambda l: l.code == 'HRA3')
                                    saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code == 'GOSI')
                                    company_gosi_12_id = employee_id.line_ids.filtered(lambda l: l.code == 'CGOSI')
                                    company_gosi_22_id = employee_id.line_ids.filtered(lambda l: l.code == 'FCGOSI')
                                    net_id = employee_id.line_ids.filtered(lambda l: l.code == 'Net')
                                    food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FA')
                                    work_nature_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'NWA')
                                    fixed_add_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FAA')
                                    fixed_deduct_amount_id = employee_id.line_ids.filtered(lambda l: l.code == 'DEDFIXD')
                                    if gross_id:
                                        gross_total += gross_id.total
                                    if transport_id:
                                        transport_total += transport_id.total
                                    if house_id:
                                        house_rent_total += house_id.total
                                    if house_id_1:
                                        house_rent_total += house_id_1.total
                                    if saudi_gosi_10_id:
                                        saudi_gosi_total += saudi_gosi_10_id.total
                                    if company_gosi_12_id:
                                        company_gosi_12_total += company_gosi_12_id.total
                                    if company_gosi_22_id:
                                        company_gosi_22_total += company_gosi_22_id.total
                                    if net_id:
                                        net_total += net_id.total
                                    if food_allowance_id:
                                        food_total += food_allowance_id.total
                                    if work_nature_allowance_id:
                                        work_nature_total += work_nature_allowance_id.total
                                    if fixed_add_allowance_id:
                                        fixed_additional_total += fixed_add_allowance_id.total
                                    if fixed_deduct_amount_id:
                                        fixed_deduction_total += fixed_deduct_amount_id.total
                        if sumary.get('department_id'):
                            if docs.is_parent_dempart:
                                sheet.write_string(row, col, str(sumary.get('department_id')[1].split()[0]), main_heading)
                            else:
                                sheet.write_string(row, col, str(sumary.get('department_id')[1]),
                                                   main_heading)
                        if sumary.get('branch_id'):
                            sheet.write_string(row, col + 1, str(sumary.get('branch_id')[1]), main_heading)
                        if sumary.get('region_id'):
                            sheet.write_string(row, col + 2, str(sumary.get('region_id')[1]), main_heading)
                        if sumary.get('job_id'):
                            sheet.write_string(row, col + 3, str(sumary.get('job_id')[1]), main_heading)
                        if sumary.get('__count'):
                            sheet.write_number(row, col + 4, sumary.get('__count'),
                                               main_heading)
                            employee_grand_total += sumary.get('__count')
                        if wage_total:
                            sheet.write_number(row, col + 5, wage_total, main_heading)
                            wage_grand_total += wage_total
                        if transport_total:
                            sheet.write_number(row, col + 6, transport_total, main_heading)
                            transport_grand_total += transport_total
                        if house_rent_total:
                            sheet.write_number(row, col + 7, house_rent_total, main_heading)
                            house_rent_grand_total += house_rent_total
                        if food_total:
                            sheet.write_number(row, col + 8, food_total, main_heading)
                            food_grand_total += food_total
                        if work_nature_total:
                            sheet.write_number(row, col + 9, work_nature_total, main_heading)
                            work_nature_grand_total += work_nature_total
                        if gross_total:
                            sheet.write_number(row, col + 10, gross_total, main_heading)
                            gross_grand_total += gross_total
                        if fixed_additional_total:
                            sheet.write_number(row, col + 11, fixed_additional_total, main_heading)
                            fixed_additional_grand_total += fixed_additional_total
                        if fixed_deduction_total:
                            sheet.write_number(row, col + 12, fixed_deduction_total, main_heading)
                            fixed_deduction_grand_total += fixed_deduction_total
                        if saudi_gosi_total:
                            sheet.write_number(row, col + 13, saudi_gosi_total, main_heading)
                            saudi_gosi_grand_total += saudi_gosi_total
                        if company_gosi_22_total:
                            sheet.write_number(row, col + 14, company_gosi_22_total, main_heading)
                            company_gosi_22_grand_total += company_gosi_22_total
                        if company_gosi_12_total:
                            sheet.write_number(row, col + 15, company_gosi_12_total, main_heading)
                            company_gosi_12_grand_total += company_gosi_12_total
                        if net_total:
                            sheet.write_number(row, col + 16, net_total, main_heading)
                            net_grand_total += net_total
                        row+=1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 4, employee_grand_total,main_heading)
                sheet.write_number(row, col + 5, wage_grand_total, main_heading)
                sheet.write_number(row, col + 6, transport_grand_total, main_heading)
                sheet.write_number(row, col + 7, house_rent_grand_total, main_heading)
                sheet.write_number(row, col + 8, food_grand_total, main_heading)
                sheet.write_number(row, col + 9, work_nature_grand_total, main_heading)
                sheet.write_number(row, col + 10, gross_grand_total, main_heading)
                sheet.write_number(row, col + 11, fixed_additional_grand_total, main_heading)
                sheet.write_number(row, col + 12, fixed_deduction_grand_total, main_heading)
                sheet.write_number(row, col + 13, saudi_gosi_grand_total, main_heading)
                sheet.write_number(row, col + 14, company_gosi_22_grand_total, main_heading)
                sheet.write_number(row, col + 15, company_gosi_12_grand_total, main_heading)
                sheet.write_number(row, col + 16, net_grand_total, main_heading)
        if docs.grouping_by == 'by_departments':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Summary Report Group By Departments"
            sheet.merge_range('A1:N1', 'تقرير ملخص رواتب الموظفين بحسب الإدارات', main_heading3)
            sheet.merge_range('A2:N2', 'Employee Salary Summary Report Group By Departments', main_heading3)
            sheet.write(row, col,'Department', main_heading2)
            sheet.write(row, col + 1, 'Total Employees', main_heading2)
            sheet.write(row, col + 2, 'Wage', main_heading2)
            sheet.write(row, col + 3, 'Transport', main_heading2)
            sheet.write(row, col + 4, 'House Rent', main_heading2)
            sheet.write(row, col + 5, 'Food', main_heading2)
            sheet.write(row, col + 6, 'Work Nature', main_heading2)
            sheet.write(row, col + 7, 'Gross', main_heading2)
            sheet.write(row, col + 8, 'Fixed Additional', main_heading2)
            sheet.write(row, col + 9, 'Fixed Deduction', main_heading2)
            sheet.write(row, col + 10, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 11, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 12, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 13, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'الادارة', main_heading2)
            sheet.write(row, col + 1, 'عدد الموظفي', main_heading2)
            sheet.write(row, col + 2, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 3, 'بدل نقل', main_heading2)
            sheet.write(row, col + 4, 'بدل سكن', main_heading2)
            sheet.write(row, col + 5, 'بدل طعام', main_heading2)
            sheet.write(row, col + 6, 'بدل طبيعية عمل', main_heading2)
            sheet.write(row, col + 7, 'اجمالي المستحق', main_heading2)
            sheet.write(row, col + 8, 'بدل إضافي ثابت', main_heading2)
            sheet.write(row, col + 9, 'الخصم الثابت', main_heading2)
            sheet.write(row, col + 10, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 11, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 12, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 13, 'صافي الراتب', main_heading2)
            row += 1
            grand_total = 0
            summary_employee_ids = employee_ids.read_group([],fields=['department_id'],groupby=['department_id'],lazy=False)
            if summary_employee_ids:
                employee_grand_total = 0
                wage_grand_total = 0.0
                transport_grand_total = 0.0
                house_rent_grand_total = 0.0
                food_grand_total = 0.0
                work_nature_grand_total = 0.0
                gross_grand_total = 0.0
                fixed_additional_grand_total = 0.0
                fixed_deduction_grand_total = 0.0
                saudi_gosi_grand_total = 0.0
                company_gosi_12_grand_total = 0.0
                company_gosi_22_grand_total = 0.0
                net_grand_total = 0.0
                for sumary in summary_employee_ids:
                    # print('...sumary.....',sumary)
                    filter_summary_employee_ids = employee_ids.filtered(lambda r:(r.department_id.id == sumary.get('department_id')[0] if sumary.get('department_id') else r.department_id.id == sumary.get('department_id')))
                    print('......filtered employee',filter_summary_employee_ids)
                    if filter_summary_employee_ids:
                        print('......filtered employee', filter_summary_employee_ids)
                        wage_total = 0.0
                        transport_total = 0.0
                        house_rent_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        for employee_id in filter_summary_employee_ids:
                            if employee_id:
                                contract_id = self.env['hr.contract'].search(
                                    [('employee_id', '=', employee_id.id), ('state', '=', 'open')],limit=1)
                                if contract_id.wage:
                                    wage_total += contract_id.wage
                                if employee_id.line_ids:
                                    gross_id = employee_id.line_ids.filtered(lambda l: l.code == 'GROSS')
                                    transport_id = employee_id.line_ids.filtered(lambda l: l.code == 'CA')
                                    house_id = employee_id.line_ids.filtered(lambda l: l.code == 'HRA2')
                                    house_id_1 = employee_id.line_ids.filtered(lambda l: l.code == 'HRA3')
                                    saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code == 'GOSI')
                                    company_gosi_12_id = employee_id.line_ids.filtered(lambda l: l.code == 'CGOSI')
                                    company_gosi_22_id = employee_id.line_ids.filtered(lambda l: l.code == 'FCGOSI')
                                    net_id = employee_id.line_ids.filtered(lambda l: l.code == 'Net')
                                    food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FA')
                                    work_nature_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'NWA')
                                    fixed_add_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FAA')
                                    fixed_deduct_amount_id = employee_id.line_ids.filtered(lambda l: l.code == 'DEDFIXD')
                                    if gross_id:
                                        gross_total += gross_id.total
                                    if transport_id:
                                        transport_total += transport_id.total
                                    if house_id:
                                        house_rent_total += house_id.total
                                    if house_id_1:
                                        house_rent_total += house_id_1.total
                                    if saudi_gosi_10_id:
                                        saudi_gosi_total += saudi_gosi_10_id.total
                                    if company_gosi_12_id:
                                        company_gosi_12_total += company_gosi_12_id.total
                                    if company_gosi_22_id:
                                        company_gosi_22_total += company_gosi_22_id.total
                                    if net_id:
                                        net_total += net_id.total
                                    if food_allowance_id:
                                        food_total += food_allowance_id.total
                                    if work_nature_allowance_id:
                                        work_nature_total += work_nature_allowance_id.total
                                    if fixed_add_allowance_id:
                                        fixed_additional_total += fixed_add_allowance_id.total
                                    if fixed_deduct_amount_id:
                                        fixed_deduction_total += fixed_deduct_amount_id.total
                        if sumary.get('department_id'):
                            sheet.write_string(row, col, str(sumary.get('department_id')[1]),
                                               main_heading)
                        if sumary.get('__count'):
                            sheet.write_number(row, col + 1, sumary.get('__count'),
                                               main_heading)
                            employee_grand_total += sumary.get('__count')
                        if wage_total:
                            sheet.write_number(row, col + 2, wage_total, main_heading)
                            wage_grand_total += wage_total
                        if transport_total:
                            sheet.write_number(row, col + 3, transport_total, main_heading)
                            transport_grand_total += transport_total
                        if house_rent_total:
                            sheet.write_number(row, col + 4, house_rent_total, main_heading)
                            house_rent_grand_total += house_rent_total
                        if food_total:
                            sheet.write_number(row, col + 5, food_total, main_heading)
                            food_grand_total += food_total
                        if work_nature_total:
                            sheet.write_number(row, col + 6, work_nature_total, main_heading)
                            work_nature_grand_total += work_nature_total
                        if gross_total:
                            sheet.write_number(row, col + 7, gross_total, main_heading)
                            gross_grand_total += gross_total
                        if fixed_additional_total:
                            sheet.write_number(row, col + 8, fixed_additional_total, main_heading)
                            fixed_additional_grand_total += fixed_additional_total
                        if fixed_deduction_total:
                            sheet.write_number(row, col + 9, fixed_deduction_total, main_heading)
                            fixed_deduction_grand_total += fixed_deduction_total
                        if saudi_gosi_total:
                            sheet.write_number(row, col + 10, saudi_gosi_total, main_heading)
                            saudi_gosi_grand_total += saudi_gosi_total
                        if company_gosi_22_total:
                            sheet.write_number(row, col + 11, company_gosi_22_total, main_heading)
                            company_gosi_22_grand_total += company_gosi_22_total
                        if company_gosi_12_total:
                            sheet.write_number(row, col + 12, company_gosi_12_total, main_heading)
                            company_gosi_12_grand_total += company_gosi_12_total
                        if net_total:
                            sheet.write_number(row, col + 13, net_total, main_heading)
                            net_grand_total += net_total
                        row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 1, employee_grand_total, main_heading)
                sheet.write_number(row, col + 2, wage_grand_total, main_heading)
                sheet.write_number(row, col + 3, transport_grand_total, main_heading)
                sheet.write_number(row, col + 4, house_rent_grand_total, main_heading)
                sheet.write_number(row, col + 5, food_grand_total, main_heading)
                sheet.write_number(row, col + 6, work_nature_grand_total, main_heading)
                sheet.write_number(row, col + 7, gross_grand_total, main_heading)
                sheet.write_number(row, col + 8, fixed_additional_grand_total, main_heading)
                sheet.write_number(row, col + 9, fixed_deduction_grand_total, main_heading)
                sheet.write_number(row, col + 10, saudi_gosi_grand_total, main_heading)
                sheet.write_number(row, col + 11, company_gosi_22_grand_total, main_heading)
                sheet.write_number(row, col + 12, company_gosi_12_grand_total, main_heading)
                sheet.write_number(row, col + 13, net_grand_total, main_heading)
        if docs.grouping_by == 'by_parent_departments':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Summary Report Group By Parent Department"
            sheet.merge_range('A1:N1', 'تقرير ملخص رواتب الموظفين بحسب الإدارات', main_heading3)
            sheet.merge_range('A2:N2', 'Employee Salary Summary Report Group By Parent Department', main_heading3)
            sheet.write(row, col, 'Department', main_heading2)
            sheet.write(row, col + 1, 'Total Employees', main_heading2)
            sheet.write(row, col + 2, 'Wage', main_heading2)
            sheet.write(row, col + 3, 'Transport', main_heading2)
            sheet.write(row, col + 4, 'House Rent', main_heading2)
            sheet.write(row, col + 5, 'Food', main_heading2)
            sheet.write(row, col + 6, 'Work Nature', main_heading2)
            sheet.write(row, col + 7, 'Gross', main_heading2)
            sheet.write(row, col + 8, 'Fixed Additional', main_heading2)
            sheet.write(row, col + 9, 'Fixed Deduction', main_heading2)
            sheet.write(row, col + 10, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 11, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 12, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 13, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'الادارة', main_heading2)
            sheet.write(row, col + 1, 'عدد الموظفي', main_heading2)
            sheet.write(row, col + 2, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 3, 'بدل نقل', main_heading2)
            sheet.write(row, col + 4, 'بدل سكن', main_heading2)
            sheet.write(row, col + 5, 'بدل طعام', main_heading2)
            sheet.write(row, col + 6, 'بدل طبيعية عمل', main_heading2)
            sheet.write(row, col + 7, 'اجمالي المستحق', main_heading2)
            sheet.write(row, col + 8, 'بدل إضافي ثابت', main_heading2)
            sheet.write(row, col + 9, 'الخصم الثابت', main_heading2)
            sheet.write(row, col + 10, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 11, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 12, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 13, 'صافي الراتب', main_heading2)
            row += 1
            grand_total = 0
            if employee_ids:
                parent_depart_list = []
                for employee_id in employee_ids:
                    if employee_id.department_id:
                        if employee_id.department_id.display_name.split('/')[0].strip() not in parent_depart_list:
                            parent_depart_list.append(employee_id.department_id.display_name.split('/')[0].strip())
                if parent_depart_list:
                    employee_grand_total = 0
                    wage_grand_total = 0.0
                    transport_grand_total = 0.0
                    house_rent_grand_total = 0.0
                    food_grand_total = 0.0
                    work_nature_grand_total = 0.0
                    gross_grand_total = 0.0
                    fixed_additional_grand_total = 0.0
                    fixed_deduction_grand_total = 0.0
                    saudi_gosi_grand_total = 0.0
                    company_gosi_12_grand_total = 0.0
                    company_gosi_22_grand_total = 0.0
                    net_grand_total = 0.0
                    for parent_depart_name in parent_depart_list:
                        if parent_depart_name:
                            filter_summary_employee_ids = employee_ids.filtered(lambda r:r.department_id and r.department_id.display_name.split('/')[0].strip() == parent_depart_name)
                            if filter_summary_employee_ids:
                                employee_count = 0
                                wage_total = 0.0
                                transport_total = 0.0
                                house_rent_total = 0.0
                                food_total = 0.0
                                work_nature_total = 0.0
                                gross_total = 0.0
                                fixed_additional_total = 0.0
                                fixed_deduction_total = 0.0
                                saudi_gosi_total = 0.0
                                company_gosi_12_total = 0.0
                                company_gosi_22_total = 0.0
                                net_total = 0.0
                                for employee_id in filter_summary_employee_ids:
                                    if employee_id:
                                        employee_count += 1
                                        contract_id = self.env['hr.contract'].search(
                                            [('employee_id', '=', employee_id.id), ('state', '=', 'open')], limit=1)
                                        if contract_id.wage:
                                            wage_total += contract_id.wage
                                        if employee_id.line_ids:
                                            gross_id = employee_id.line_ids.filtered(lambda l: l.code == 'GROSS')
                                            transport_id = employee_id.line_ids.filtered(lambda l: l.code == 'CA')
                                            house_id = employee_id.line_ids.filtered(lambda l: l.code == 'HRA2')
                                            house_id_1 = employee_id.line_ids.filtered(lambda l: l.code == 'HRA3')
                                            saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code == 'GOSI')
                                            company_gosi_12_id = employee_id.line_ids.filtered(lambda l: l.code == 'CGOSI')
                                            company_gosi_22_id = employee_id.line_ids.filtered(lambda l: l.code == 'FCGOSI')
                                            net_id = employee_id.line_ids.filtered(lambda l: l.code == 'Net')
                                            food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FA')
                                            work_nature_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'NWA')
                                            fixed_add_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FAA')
                                            fixed_deduct_amount_id = employee_id.line_ids.filtered(lambda l: l.code == 'DEDFIXD')
                                            if gross_id:
                                                gross_total += gross_id.total
                                            if transport_id:
                                                transport_total += transport_id.total
                                            if house_id:
                                                house_rent_total += house_id.total
                                            if house_id_1:
                                                house_rent_total += house_id_1.total
                                            if saudi_gosi_10_id:
                                                saudi_gosi_total += saudi_gosi_10_id.total
                                            if company_gosi_12_id:
                                                company_gosi_12_total += company_gosi_12_id.total
                                            if company_gosi_22_id:
                                                company_gosi_22_total += company_gosi_22_id.total
                                            if net_id:
                                                net_total += net_id.total
                                            if food_allowance_id:
                                                food_total += food_allowance_id.total
                                            if work_nature_allowance_id:
                                                work_nature_total += work_nature_allowance_id.total
                                            if fixed_add_allowance_id:
                                                fixed_additional_total += fixed_add_allowance_id.total
                                            if fixed_deduct_amount_id:
                                                fixed_deduction_total += fixed_deduct_amount_id.total
                                sheet.write_string(row, col, str(parent_depart_name),
                                                   main_heading)
                                if employee_count:
                                    sheet.write_number(row, col + 1, employee_count,
                                                       main_heading)
                                    employee_grand_total += employee_count
                                if wage_total:
                                    sheet.write_number(row, col + 2, wage_total, main_heading)
                                    wage_grand_total += wage_total
                                if transport_total:
                                    sheet.write_number(row, col + 3, transport_total, main_heading)
                                    transport_grand_total += transport_total
                                if house_rent_total:
                                    sheet.write_number(row, col + 4, house_rent_total, main_heading)
                                    house_rent_grand_total += house_rent_total
                                if food_total:
                                    sheet.write_number(row, col + 5, food_total, main_heading)
                                    food_grand_total += food_total
                                if work_nature_total:
                                    sheet.write_number(row, col + 6, work_nature_total, main_heading)
                                    work_nature_grand_total += work_nature_total
                                if gross_total:
                                    sheet.write_number(row, col + 7, gross_total, main_heading)
                                    gross_grand_total += gross_total
                                if fixed_additional_total:
                                    sheet.write_number(row, col + 8, fixed_additional_total, main_heading)
                                    fixed_additional_grand_total += fixed_additional_total
                                if fixed_deduction_total:
                                    sheet.write_number(row, col + 9, fixed_deduction_total, main_heading)
                                    fixed_deduction_grand_total += fixed_deduction_total
                                if saudi_gosi_total:
                                    sheet.write_number(row, col + 10, saudi_gosi_total, main_heading)
                                    saudi_gosi_grand_total += saudi_gosi_total
                                if company_gosi_22_total:
                                    sheet.write_number(row, col + 11, company_gosi_22_total, main_heading)
                                    company_gosi_22_grand_total += company_gosi_22_total
                                if company_gosi_12_total:
                                    sheet.write_number(row, col + 12, company_gosi_12_total, main_heading)
                                    company_gosi_12_grand_total += company_gosi_12_total
                                if net_total:
                                    sheet.write_number(row, col + 13, net_total, main_heading)
                                    net_grand_total += net_total
                                row += 1
                    sheet.write(row, col, 'Grand Total', main_heading2)
                    sheet.write_number(row, col + 1, employee_grand_total, main_heading)
                    sheet.write_number(row, col + 2, wage_grand_total, main_heading)
                    sheet.write_number(row, col + 3, transport_grand_total, main_heading)
                    sheet.write_number(row, col + 4, house_rent_grand_total, main_heading)
                    sheet.write_number(row, col + 5, food_grand_total, main_heading)
                    sheet.write_number(row, col + 6, work_nature_grand_total, main_heading)
                    sheet.write_number(row, col + 7, gross_grand_total, main_heading)
                    sheet.write_number(row, col + 8, fixed_additional_grand_total, main_heading)
                    sheet.write_number(row, col + 9, fixed_deduction_grand_total, main_heading)
                    sheet.write_number(row, col + 10, saudi_gosi_grand_total, main_heading)
                    sheet.write_number(row, col + 11, company_gosi_22_grand_total, main_heading)
                    sheet.write_number(row, col + 12, company_gosi_12_grand_total, main_heading)
                    sheet.write_number(row, col + 13, net_grand_total, main_heading)
        if docs.grouping_by == 'by_branches':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Summary Report Group By Branches"
            sheet.merge_range('A1:N1', 'تقرير ملخص رواتب الموظفين بحسب الفروع', main_heading3)
            sheet.merge_range('A2:N2', 'Employee Salary Summary Report Group By Branches', main_heading3)
            sheet.write(row, col, 'Branch', main_heading2)
            sheet.write(row, col + 1, 'Total Employees', main_heading2)
            sheet.write(row, col + 2, 'Wage', main_heading2)
            sheet.write(row, col + 3, 'Transport', main_heading2)
            sheet.write(row, col + 4, 'House Rent', main_heading2)
            sheet.write(row, col + 5, 'Food', main_heading2)
            sheet.write(row, col + 6, 'Work Nature', main_heading2)
            sheet.write(row, col + 7, 'Gross', main_heading2)
            sheet.write(row, col + 8, 'Fixed Additional', main_heading2)
            sheet.write(row, col + 9, 'Fixed Deduction', main_heading2)
            sheet.write(row, col + 10, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 11, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 12, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 13, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'الفرع', main_heading2)
            sheet.write(row, col + 1, 'عدد الموظفي', main_heading2)
            sheet.write(row, col + 2, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 3, 'بدل نقل', main_heading2)
            sheet.write(row, col + 4, 'بدل سكن', main_heading2)
            sheet.write(row, col + 5, 'بدل طعام', main_heading2)
            sheet.write(row, col + 6, 'بدل طبيعية عمل', main_heading2)
            sheet.write(row, col + 7, 'اجمالي المستحق', main_heading2)
            sheet.write(row, col + 8, 'بدل إضافي ثابت', main_heading2)
            sheet.write(row, col + 9, 'الخصم الثابت', main_heading2)
            sheet.write(row, col + 10, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 11, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 12, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 13, 'صافي الراتب', main_heading2)
            row += 1
            grand_total = 0
            summary_employee_ids = employee_ids.read_group([],fields=['branch_id'],groupby=['branch_id'],lazy=False)
            if summary_employee_ids:
                employee_grand_total = 0
                wage_grand_total = 0.0
                transport_grand_total = 0.0
                house_rent_grand_total = 0.0
                food_grand_total = 0.0
                work_nature_grand_total = 0.0
                gross_grand_total = 0.0
                fixed_additional_grand_total = 0.0
                fixed_deduction_grand_total = 0.0
                saudi_gosi_grand_total = 0.0
                company_gosi_12_grand_total = 0.0
                company_gosi_22_grand_total = 0.0
                net_grand_total = 0.0
                for sumary in summary_employee_ids:
                    # print('...sumary.....',sumary)
                    filter_summary_employee_ids = employee_ids.filtered(lambda r:(r.branch_id.id == sumary.get('branch_id')[0] if sumary.get('branch_id') else r.branch_id.id == sumary.get('branch_id')))
                    print('......filtered employee',filter_summary_employee_ids)
                    if filter_summary_employee_ids:
                        print('......filtered employee', filter_summary_employee_ids)
                        wage_total = 0.0
                        transport_total = 0.0
                        house_rent_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        for employee_id in filter_summary_employee_ids:
                            if employee_id:
                                contract_id = self.env['hr.contract'].search(
                                    [('employee_id', '=', employee_id.id), ('state', '=', 'open')],limit=1)
                                if contract_id.wage:
                                    wage_total += contract_id.wage
                                if employee_id.line_ids:
                                    gross_id = employee_id.line_ids.filtered(lambda l: l.code == 'GROSS')
                                    transport_id = employee_id.line_ids.filtered(lambda l: l.code == 'CA')
                                    house_id = employee_id.line_ids.filtered(lambda l: l.code == 'HRA2')
                                    house_id_1 = employee_id.line_ids.filtered(lambda l: l.code == 'HRA3')
                                    saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code == 'GOSI')
                                    company_gosi_12_id = employee_id.line_ids.filtered(lambda l: l.code == 'CGOSI')
                                    company_gosi_22_id = employee_id.line_ids.filtered(lambda l: l.code == 'FCGOSI')
                                    net_id = employee_id.line_ids.filtered(lambda l: l.code == 'Net')
                                    food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FA')
                                    work_nature_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'NWA')
                                    fixed_add_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FAA')
                                    fixed_deduct_amount_id = employee_id.line_ids.filtered(lambda l: l.code == 'DEDFIXD')
                                    if gross_id:
                                        gross_total += gross_id.total
                                    if transport_id:
                                        transport_total += transport_id.total
                                    if house_id:
                                        house_rent_total += house_id.total
                                    if house_id_1:
                                        house_rent_total += house_id_1.total
                                    if saudi_gosi_10_id:
                                        saudi_gosi_total += saudi_gosi_10_id.total
                                    if company_gosi_12_id:
                                        company_gosi_12_total += company_gosi_12_id.total
                                    if company_gosi_22_id:
                                        company_gosi_22_total += company_gosi_22_id.total
                                    if net_id:
                                        net_total += net_id.total
                                    if food_allowance_id:
                                        food_total += food_allowance_id.total
                                    if work_nature_allowance_id:
                                        work_nature_total += work_nature_allowance_id.total
                                    if fixed_add_allowance_id:
                                        fixed_additional_total += fixed_add_allowance_id.total
                                    if fixed_deduct_amount_id:
                                        fixed_deduction_total += fixed_deduct_amount_id.total
                        if sumary.get('branch_id'):
                            sheet.write_string(row, col, str(sumary.get('branch_id')[1]), main_heading)
                        if sumary.get('__count'):
                            sheet.write_number(row, col + 1, sumary.get('__count'),
                                               main_heading)
                            employee_grand_total += sumary.get('__count')
                        if wage_total:
                            sheet.write_number(row, col + 2, wage_total, main_heading)
                            wage_grand_total += wage_total
                        if transport_total:
                            sheet.write_number(row, col + 3, transport_total, main_heading)
                            transport_grand_total += transport_total
                        if house_rent_total:
                            sheet.write_number(row, col + 4, house_rent_total, main_heading)
                            house_rent_grand_total += house_rent_total
                        if food_total:
                            sheet.write_number(row, col + 5, food_total, main_heading)
                            food_grand_total += food_total
                        if work_nature_total:
                            sheet.write_number(row, col + 6, work_nature_total, main_heading)
                            work_nature_grand_total += work_nature_total
                        if gross_total:
                            sheet.write_number(row, col + 7, gross_total, main_heading)
                            gross_grand_total += gross_total
                        if fixed_additional_total:
                            sheet.write_number(row, col + 8, fixed_additional_total, main_heading)
                            fixed_additional_grand_total += fixed_additional_total
                        if fixed_deduction_total:
                            sheet.write_number(row, col + 9, fixed_deduction_total, main_heading)
                            fixed_deduction_grand_total += fixed_deduction_total
                        if saudi_gosi_total:
                            sheet.write_number(row, col + 10, saudi_gosi_total, main_heading)
                            saudi_gosi_grand_total += saudi_gosi_total
                        if company_gosi_22_total:
                            sheet.write_number(row, col + 11, company_gosi_22_total, main_heading)
                            company_gosi_22_grand_total += company_gosi_22_total
                        if company_gosi_12_total:
                            sheet.write_number(row, col + 12, company_gosi_12_total, main_heading)
                            company_gosi_12_grand_total += company_gosi_12_total
                        if net_total:
                            sheet.write_number(row, col + 13, net_total, main_heading)
                            net_grand_total += net_total
                        row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 1, employee_grand_total, main_heading)
                sheet.write_number(row, col + 2, wage_grand_total, main_heading)
                sheet.write_number(row, col + 3, transport_grand_total, main_heading)
                sheet.write_number(row, col + 4, house_rent_grand_total, main_heading)
                sheet.write_number(row, col + 5, food_grand_total, main_heading)
                sheet.write_number(row, col + 6, work_nature_grand_total, main_heading)
                sheet.write_number(row, col + 7, gross_grand_total, main_heading)
                sheet.write_number(row, col + 8, fixed_additional_grand_total, main_heading)
                sheet.write_number(row, col + 9, fixed_deduction_grand_total, main_heading)
                sheet.write_number(row, col + 10, saudi_gosi_grand_total, main_heading)
                sheet.write_number(row, col + 11, company_gosi_22_grand_total, main_heading)
                sheet.write_number(row, col + 12, company_gosi_12_grand_total, main_heading)
                sheet.write_number(row, col + 13, net_grand_total, main_heading)
        if docs.grouping_by == 'by_job_positions':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Summary Report Group By Job Position"
            sheet.merge_range('A1:N1', 'تقرير ملخص رواتب الموظفين بحسب المناصب الوظيفية', main_heading3)
            sheet.merge_range('A2:N2', 'Employee Salary Summary Report Group By Job Position', main_heading3)
            sheet.write(row, col, 'Jop Position', main_heading2)
            sheet.write(row, col + 1, 'Total Employees', main_heading2)
            sheet.write(row, col + 2, 'Wage', main_heading2)
            sheet.write(row, col + 3, 'Transport', main_heading2)
            sheet.write(row, col + 4, 'House Rent', main_heading2)
            sheet.write(row, col + 5, 'Food', main_heading2)
            sheet.write(row, col + 6, 'Work Nature', main_heading2)
            sheet.write(row, col + 7, 'Gross', main_heading2)
            sheet.write(row, col + 8, 'Fixed Additional', main_heading2)
            sheet.write(row, col + 9, 'Fixed Deduction', main_heading2)
            sheet.write(row, col + 10, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 11, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 12, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 13, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'الوظيفه', main_heading2)
            sheet.write(row, col + 1, 'عدد الموظفي', main_heading2)
            sheet.write(row, col + 2, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 3, 'بدل نقل', main_heading2)
            sheet.write(row, col + 4, 'بدل سكن', main_heading2)
            sheet.write(row, col + 5, 'بدل طعام', main_heading2)
            sheet.write(row, col + 6, 'بدل طبيعية عمل', main_heading2)
            sheet.write(row, col + 7, 'اجمالي المستحق', main_heading2)
            sheet.write(row, col + 8, 'بدل إضافي ثابت', main_heading2)
            sheet.write(row, col + 9, 'الخصم الثابت', main_heading2)
            sheet.write(row, col + 10, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 11, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 12, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 13, 'صافي الراتب', main_heading2)
            row += 1
            grand_total = 0
            summary_employee_ids = employee_ids.read_group([],fields=['job_id'],groupby=['job_id'],lazy=False)
            if summary_employee_ids:
                employee_grand_total = 0
                wage_grand_total = 0.0
                transport_grand_total = 0.0
                house_rent_grand_total = 0.0
                food_grand_total = 0.0
                work_nature_grand_total = 0.0
                gross_grand_total = 0.0
                fixed_additional_grand_total = 0.0
                fixed_deduction_grand_total = 0.0
                saudi_gosi_grand_total = 0.0
                company_gosi_12_grand_total = 0.0
                company_gosi_22_grand_total = 0.0
                net_grand_total = 0.0
                for sumary in summary_employee_ids:
                    # print('...sumary.....',sumary)
                    filter_summary_employee_ids = employee_ids.filtered(lambda r:(r.job_id.id == sumary.get('job_id')[0] if sumary.get('job_id') else r.job_id.id == sumary.get('job_id')))
                    print('......filtered employee',filter_summary_employee_ids)
                    if filter_summary_employee_ids:
                        print('......filtered employee', filter_summary_employee_ids)
                        wage_total = 0.0
                        transport_total = 0.0
                        house_rent_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        for employee_id in filter_summary_employee_ids:
                            if employee_id:
                                contract_id = self.env['hr.contract'].search(
                                    [('employee_id', '=', employee_id.id), ('state', '=', 'open')],limit=1)
                                if contract_id.wage:
                                    wage_total += contract_id.wage
                                if employee_id.line_ids:
                                    gross_id = employee_id.line_ids.filtered(lambda l: l.code == 'GROSS')
                                    transport_id = employee_id.line_ids.filtered(lambda l: l.code == 'CA')
                                    house_id = employee_id.line_ids.filtered(lambda l: l.code == 'HRA2')
                                    house_id_1 = employee_id.line_ids.filtered(lambda l: l.code == 'HRA3')
                                    saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code == 'GOSI')
                                    company_gosi_12_id = employee_id.line_ids.filtered(lambda l: l.code == 'CGOSI')
                                    company_gosi_22_id = employee_id.line_ids.filtered(lambda l: l.code == 'FCGOSI')
                                    net_id = employee_id.line_ids.filtered(lambda l: l.code == 'Net')
                                    food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FA')
                                    work_nature_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'NWA')
                                    fixed_add_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FAA')
                                    fixed_deduct_amount_id = employee_id.line_ids.filtered(lambda l: l.code == 'DEDFIXD')
                                    if gross_id:
                                        gross_total += gross_id.total
                                    if transport_id:
                                        transport_total += transport_id.total
                                    if house_id:
                                        house_rent_total += house_id.total
                                    if house_id_1:
                                        house_rent_total += house_id_1.total
                                    if saudi_gosi_10_id:
                                        saudi_gosi_total += saudi_gosi_10_id.total
                                    if company_gosi_12_id:
                                        company_gosi_12_total += company_gosi_12_id.total
                                    if company_gosi_22_id:
                                        company_gosi_22_total += company_gosi_22_id.total
                                    if net_id:
                                        net_total += net_id.total
                                    if food_allowance_id:
                                        food_total += food_allowance_id.total
                                    if work_nature_allowance_id:
                                        work_nature_total += work_nature_allowance_id.total
                                    if fixed_add_allowance_id:
                                        fixed_additional_total += fixed_add_allowance_id.total
                                    if fixed_deduct_amount_id:
                                        fixed_deduction_total += fixed_deduct_amount_id.total
                        if sumary.get('job_id'):
                            sheet.write_string(row, col, str(sumary.get('job_id')[1]), main_heading)
                        if sumary.get('__count'):
                            sheet.write_number(row, col + 1, sumary.get('__count'),
                                               main_heading)
                            employee_grand_total += sumary.get('__count')
                        if wage_total:
                            sheet.write_number(row, col + 2, wage_total, main_heading)
                            wage_grand_total += wage_total
                        if transport_total:
                            sheet.write_number(row, col + 3, transport_total, main_heading)
                            transport_grand_total += transport_total
                        if house_rent_total:
                            sheet.write_number(row, col + 4, house_rent_total, main_heading)
                            house_rent_grand_total += house_rent_total
                        if food_total:
                            sheet.write_number(row, col + 5, food_total, main_heading)
                            food_grand_total += food_total
                        if work_nature_total:
                            sheet.write_number(row, col + 6, work_nature_total, main_heading)
                            work_nature_grand_total += work_nature_total
                        if gross_total:
                            sheet.write_number(row, col + 7, gross_total, main_heading)
                            gross_grand_total += gross_total
                        if fixed_additional_total:
                            sheet.write_number(row, col + 8, fixed_additional_total, main_heading)
                            fixed_additional_grand_total += fixed_additional_total
                        if fixed_deduction_total:
                            sheet.write_number(row, col + 9, fixed_deduction_total, main_heading)
                            fixed_deduction_grand_total += fixed_deduction_total
                        if saudi_gosi_total:
                            sheet.write_number(row, col + 10, saudi_gosi_total, main_heading)
                            saudi_gosi_grand_total += saudi_gosi_total
                        if company_gosi_22_total:
                            sheet.write_number(row, col + 11, company_gosi_22_total, main_heading)
                            company_gosi_22_grand_total += company_gosi_22_total
                        if company_gosi_12_total:
                            sheet.write_number(row, col + 12, company_gosi_12_total, main_heading)
                            company_gosi_12_grand_total += company_gosi_12_total
                        if net_total:
                            sheet.write_number(row, col + 13, net_total, main_heading)
                            net_grand_total += net_total
                        row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 1, employee_grand_total, main_heading)
                sheet.write_number(row, col + 2, wage_grand_total, main_heading)
                sheet.write_number(row, col + 3, transport_grand_total, main_heading)
                sheet.write_number(row, col + 4, house_rent_grand_total, main_heading)
                sheet.write_number(row, col + 5, food_grand_total, main_heading)
                sheet.write_number(row, col + 6, work_nature_grand_total, main_heading)
                sheet.write_number(row, col + 7, gross_grand_total, main_heading)
                sheet.write_number(row, col + 8, fixed_additional_grand_total, main_heading)
                sheet.write_number(row, col + 9, fixed_deduction_grand_total, main_heading)
                sheet.write_number(row, col + 10, saudi_gosi_grand_total, main_heading)
                sheet.write_number(row, col + 11, company_gosi_22_grand_total, main_heading)
                sheet.write_number(row, col + 12, company_gosi_12_grand_total, main_heading)
                sheet.write_number(row, col + 13, net_grand_total, main_heading)
        if docs.grouping_by == 'by_region':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Summary Report Group By Region"
            sheet.merge_range('A1:N1', 'تقرير ملخص رواتب الموظفين بحسب المناطق', main_heading3)
            sheet.merge_range('A2:N2', 'Employee Salary Summary Report Group By Region', main_heading3)
            sheet.write(row, col , 'Region', main_heading2)
            sheet.write(row, col + 1, 'Total Employees', main_heading2)
            sheet.write(row, col + 2, 'Wage', main_heading2)
            sheet.write(row, col + 3, 'Transport', main_heading2)
            sheet.write(row, col + 4, 'House Rent', main_heading2)
            sheet.write(row, col + 5, 'Food', main_heading2)
            sheet.write(row, col + 6, 'Work Nature', main_heading2)
            sheet.write(row, col + 7, 'Gross', main_heading2)
            sheet.write(row, col + 8, 'Fixed Additional', main_heading2)
            sheet.write(row, col + 9, 'Fixed Deduction', main_heading2)
            sheet.write(row, col + 10, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 11, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 12, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 13, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'منطقة', main_heading2)
            sheet.write(row, col + 1, 'عدد الموظفي', main_heading2)
            sheet.write(row, col + 2, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 3, 'بدل نقل', main_heading2)
            sheet.write(row, col + 4, 'بدل سكن', main_heading2)
            sheet.write(row, col + 5, 'بدل طعام', main_heading2)
            sheet.write(row, col + 6, 'بدل طبيعية عمل', main_heading2)
            sheet.write(row, col + 7, 'اجمالي المستحق', main_heading2)
            sheet.write(row, col + 8, 'بدل إضافي ثابت', main_heading2)
            sheet.write(row, col + 9, 'الخصم الثابت', main_heading2)
            sheet.write(row, col + 10, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 11, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 12, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 13, 'صافي الراتب', main_heading2)
            row += 1
            grand_total = 0
            summary_employee_ids = employee_ids.read_group([],fields=['region_id'],groupby=['region_id'],lazy=False)
            if summary_employee_ids:
                employee_grand_total = 0
                wage_grand_total = 0.0
                transport_grand_total = 0.0
                house_rent_grand_total = 0.0
                food_grand_total = 0.0
                work_nature_grand_total = 0.0
                gross_grand_total = 0.0
                fixed_additional_grand_total = 0.0
                fixed_deduction_grand_total = 0.0
                saudi_gosi_grand_total = 0.0
                company_gosi_12_grand_total = 0.0
                company_gosi_22_grand_total = 0.0
                net_grand_total = 0.0
                for sumary in summary_employee_ids:
                    # print('...sumary.....',sumary)
                    filter_summary_employee_ids = employee_ids.filtered(lambda r:(r.region_id.id == sumary.get('region_id')[0] if sumary.get('region_id') else r.region_id.id == sumary.get('region_id')))
                    print('......filtered employee',filter_summary_employee_ids)
                    if filter_summary_employee_ids:
                        print('......filtered employee', filter_summary_employee_ids)
                        wage_total = 0.0
                        transport_total = 0.0
                        house_rent_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        for employee_id in filter_summary_employee_ids:
                            if employee_id:
                                contract_id = self.env['hr.contract'].search(
                                    [('employee_id', '=', employee_id.id), ('state', '=', 'open')],limit=1)
                                if contract_id.wage:
                                    wage_total += contract_id.wage
                                if employee_id.line_ids:
                                    gross_id = employee_id.line_ids.filtered(lambda l: l.code == 'GROSS')
                                    transport_id = employee_id.line_ids.filtered(lambda l: l.code == 'CA')
                                    house_id = employee_id.line_ids.filtered(lambda l: l.code == 'HRA2')
                                    house_id_1 = employee_id.line_ids.filtered(lambda l: l.code == 'HRA3')
                                    saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code == 'GOSI')
                                    company_gosi_12_id = employee_id.line_ids.filtered(lambda l: l.code == 'CGOSI')
                                    company_gosi_22_id = employee_id.line_ids.filtered(lambda l: l.code == 'FCGOSI')
                                    net_id = employee_id.line_ids.filtered(lambda l: l.code == 'Net')
                                    food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FA')
                                    work_nature_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'NWA')
                                    fixed_add_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FAA')
                                    fixed_deduct_amount_id = employee_id.line_ids.filtered(lambda l: l.code == 'DEDFIXD')
                                    if gross_id:
                                        gross_total += gross_id.total
                                    if transport_id:
                                        transport_total += transport_id.total
                                    if house_id:
                                        house_rent_total += house_id.total
                                    if house_id_1:
                                        house_rent_total += house_id_1.total
                                    if saudi_gosi_10_id:
                                        saudi_gosi_total += saudi_gosi_10_id.total
                                    if company_gosi_12_id:
                                        company_gosi_12_total += company_gosi_12_id.total
                                    if company_gosi_22_id:
                                        company_gosi_22_total += company_gosi_22_id.total
                                    if net_id:
                                        net_total += net_id.total
                                    if food_allowance_id:
                                        food_total += food_allowance_id.total
                                    if work_nature_allowance_id:
                                        work_nature_total += work_nature_allowance_id.total
                                    if fixed_add_allowance_id:
                                        fixed_additional_total += fixed_add_allowance_id.total
                                    if fixed_deduct_amount_id:
                                        fixed_deduction_total += fixed_deduct_amount_id.total
                        if sumary.get('region_id'):
                            sheet.write_string(row, col + 2, str(sumary.get('region_id')[1]), main_heading)
                        if sumary.get('__count'):
                            sheet.write_number(row, col + 1, sumary.get('__count'),
                                               main_heading)
                            employee_grand_total += sumary.get('__count')
                        if wage_total:
                            sheet.write_number(row, col + 2, wage_total, main_heading)
                            wage_grand_total += wage_total
                        if transport_total:
                            sheet.write_number(row, col + 3, transport_total, main_heading)
                            transport_grand_total += transport_total
                        if house_rent_total:
                            sheet.write_number(row, col + 4, house_rent_total, main_heading)
                            house_rent_grand_total += house_rent_total
                        if food_total:
                            sheet.write_number(row, col + 5, food_total, main_heading)
                            food_grand_total += food_total
                        if work_nature_total:
                            sheet.write_number(row, col + 6, work_nature_total, main_heading)
                            work_nature_grand_total += work_nature_total
                        if gross_total:
                            sheet.write_number(row, col + 7, gross_total, main_heading)
                            gross_grand_total += gross_total
                        if fixed_additional_total:
                            sheet.write_number(row, col + 8, fixed_additional_total, main_heading)
                            fixed_additional_grand_total += fixed_additional_total
                        if fixed_deduction_total:
                            sheet.write_number(row, col + 9, fixed_deduction_total, main_heading)
                            fixed_deduction_grand_total += fixed_deduction_total
                        if saudi_gosi_total:
                            sheet.write_number(row, col + 10, saudi_gosi_total, main_heading)
                            saudi_gosi_grand_total += saudi_gosi_total
                        if company_gosi_22_total:
                            sheet.write_number(row, col + 11, company_gosi_22_total, main_heading)
                            company_gosi_22_grand_total += company_gosi_22_total
                        if company_gosi_12_total:
                            sheet.write_number(row, col + 12, company_gosi_12_total, main_heading)
                            company_gosi_12_grand_total += company_gosi_12_total
                        if net_total:
                            sheet.write_number(row, col + 13, net_total, main_heading)
                            net_grand_total += net_total
                        row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 1, employee_grand_total, main_heading)
                sheet.write_number(row, col + 2, wage_grand_total, main_heading)
                sheet.write_number(row, col + 3, transport_grand_total, main_heading)
                sheet.write_number(row, col + 4, house_rent_grand_total, main_heading)
                sheet.write_number(row, col + 5, food_grand_total, main_heading)
                sheet.write_number(row, col + 6, work_nature_grand_total, main_heading)
                sheet.write_number(row, col + 7, gross_grand_total, main_heading)
                sheet.write_number(row, col + 8, fixed_additional_grand_total, main_heading)
                sheet.write_number(row, col + 9, fixed_deduction_grand_total, main_heading)
                sheet.write_number(row, col + 10, saudi_gosi_grand_total, main_heading)
                sheet.write_number(row, col + 11, company_gosi_22_grand_total, main_heading)
                sheet.write_number(row, col + 12, company_gosi_12_grand_total, main_heading)
                sheet.write_number(row, col + 13, net_grand_total, main_heading)
        if docs.grouping_by == 'by_nationality':
            self.env.ref(
                'bsg_employee_salary_report.salary_info_report_xlsx_id').report_file = "Employee Salary Summary Report Group By Nationality"
            sheet.merge_range('A1:N1', 'تقرير ملخص رواتب الموظفين بحسب الجنسية', main_heading3)
            sheet.merge_range('A2:N2', 'Employee Salary Summary Report Group By Nationality', main_heading3)
            sheet.write(row, col, 'Nationality', main_heading2)
            sheet.write(row, col + 1, 'Total Employees', main_heading2)
            sheet.write(row, col + 2, 'Wage', main_heading2)
            sheet.write(row, col + 3, 'Transport', main_heading2)
            sheet.write(row, col + 4, 'House Rent', main_heading2)
            sheet.write(row, col + 5, 'Food', main_heading2)
            sheet.write(row, col + 6, 'Work Nature', main_heading2)
            sheet.write(row, col + 7, 'Gross', main_heading2)
            sheet.write(row, col + 8, 'Fixed Additional', main_heading2)
            sheet.write(row, col + 9, 'Fixed Deduction', main_heading2)
            sheet.write(row, col + 10, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 11, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 12, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 13, 'Net Salary', main_heading2)
            row += 1
            sheet.write(row, col, 'الجنسية', main_heading2)
            sheet.write(row, col + 1, 'عدد الموظفي', main_heading2)
            sheet.write(row, col + 2, 'الراتب الاساسي', main_heading2)
            sheet.write(row, col + 3, 'بدل نقل', main_heading2)
            sheet.write(row, col + 4, 'بدل سكن', main_heading2)
            sheet.write(row, col + 5, 'بدل طعام', main_heading2)
            sheet.write(row, col + 6, 'بدل طبيعية عمل', main_heading2)
            sheet.write(row, col + 7, 'اجمالي المستحق', main_heading2)
            sheet.write(row, col + 8, 'بدل إضافي ثابت', main_heading2)
            sheet.write(row, col + 9, 'الخصم الثابت', main_heading2)
            sheet.write(row, col + 10, 'SAUDI GOSI 10%', main_heading2)
            sheet.write(row, col + 11, 'Company GOSI 22%', main_heading2)
            sheet.write(row, col + 12, 'Company GOSI 12%', main_heading2)
            sheet.write(row, col + 13, 'صافي الراتب', main_heading2)
            row += 1
            grand_total = 0
            summary_employee_ids = employee_ids.read_group([],fields=['country_id'],groupby=['country_id'],lazy=False)
            if summary_employee_ids:
                employee_grand_total = 0
                wage_grand_total = 0.0
                transport_grand_total = 0.0
                house_rent_grand_total = 0.0
                food_grand_total = 0.0
                work_nature_grand_total = 0.0
                gross_grand_total = 0.0
                fixed_additional_grand_total = 0.0
                fixed_deduction_grand_total = 0.0
                saudi_gosi_grand_total = 0.0
                company_gosi_12_grand_total = 0.0
                company_gosi_22_grand_total = 0.0
                net_grand_total = 0.0
                for sumary in summary_employee_ids:
                    # print('...sumary.....',sumary)
                    filter_summary_employee_ids = employee_ids.filtered(lambda r:(r.country_id.id == sumary.get('country_id')[0] if sumary.get('country_id') else r.country_id.id == sumary.get('country_id')))
                    print('......filtered employee',filter_summary_employee_ids)
                    if filter_summary_employee_ids:
                        print('......filtered employee', filter_summary_employee_ids)
                        wage_total = 0.0
                        transport_total = 0.0
                        house_rent_total = 0.0
                        food_total = 0.0
                        work_nature_total = 0.0
                        gross_total = 0.0
                        fixed_additional_total = 0.0
                        fixed_deduction_total = 0.0
                        saudi_gosi_total = 0.0
                        company_gosi_12_total = 0.0
                        company_gosi_22_total = 0.0
                        net_total = 0.0
                        for employee_id in filter_summary_employee_ids:
                            if employee_id:
                                contract_id = self.env['hr.contract'].search(
                                    [('employee_id', '=', employee_id.id), ('state', '=', 'open')],limit=1)
                                if contract_id.wage:
                                    wage_total += contract_id.wage
                                if employee_id.line_ids:
                                    gross_id = employee_id.line_ids.filtered(lambda l: l.code == 'GROSS')
                                    transport_id = employee_id.line_ids.filtered(lambda l: l.code == 'CA')
                                    house_id = employee_id.line_ids.filtered(lambda l: l.code == 'HRA2')
                                    house_id_1 = employee_id.line_ids.filtered(lambda l: l.code == 'HRA3')
                                    saudi_gosi_10_id = employee_id.line_ids.filtered(lambda l: l.code == 'GOSI')
                                    company_gosi_12_id = employee_id.line_ids.filtered(lambda l: l.code == 'CGOSI')
                                    company_gosi_22_id = employee_id.line_ids.filtered(lambda l: l.code == 'FCGOSI')
                                    net_id = employee_id.line_ids.filtered(lambda l: l.code == 'Net')
                                    food_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FA')
                                    work_nature_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'NWA')
                                    fixed_add_allowance_id = employee_id.line_ids.filtered(lambda l: l.code == 'FAA')
                                    fixed_deduct_amount_id = employee_id.line_ids.filtered(lambda l: l.code == 'DEDFIXD')
                                    if gross_id:
                                        gross_total += gross_id.total
                                    if transport_id:
                                        transport_total += transport_id.total
                                    if house_id:
                                        house_rent_total += house_id.total
                                    if house_id_1:
                                        house_rent_total += house_id_1.total
                                    if saudi_gosi_10_id:
                                        saudi_gosi_total += saudi_gosi_10_id.total
                                    if company_gosi_12_id:
                                        company_gosi_12_total += company_gosi_12_id.total
                                    if company_gosi_22_id:
                                        company_gosi_22_total += company_gosi_22_id.total
                                    if net_id:
                                        net_total += net_id.total
                                    if food_allowance_id:
                                        food_total += food_allowance_id.total
                                    if work_nature_allowance_id:
                                        work_nature_total += work_nature_allowance_id.total
                                    if fixed_add_allowance_id:
                                        fixed_additional_total += fixed_add_allowance_id.total
                                    if fixed_deduct_amount_id:
                                        fixed_deduction_total += fixed_deduct_amount_id.total
                        if sumary.get('country_id'):
                            sheet.write_string(row, col, str(sumary.get('country_id')[1]), main_heading)
                        if sumary.get('__count'):
                            sheet.write_number(row, col + 1, sumary.get('__count'),
                                               main_heading)
                            employee_grand_total += sumary.get('__count')
                        if wage_total:
                            sheet.write_number(row, col + 2, wage_total, main_heading)
                            wage_grand_total += wage_total
                        if transport_total:
                            sheet.write_number(row, col + 3, transport_total, main_heading)
                            transport_grand_total += transport_total
                        if house_rent_total:
                            sheet.write_number(row, col + 4, house_rent_total, main_heading)
                            house_rent_grand_total += house_rent_total
                        if food_total:
                            sheet.write_number(row, col + 5, food_total, main_heading)
                            food_grand_total += food_total
                        if work_nature_total:
                            sheet.write_number(row, col + 6, work_nature_total, main_heading)
                            work_nature_grand_total += work_nature_total
                        if gross_total:
                            sheet.write_number(row, col + 7, gross_total, main_heading)
                            gross_grand_total += gross_total
                        if fixed_additional_total:
                            sheet.write_number(row, col + 8, fixed_additional_total, main_heading)
                            fixed_additional_grand_total += fixed_additional_total
                        if fixed_deduction_total:
                            sheet.write_number(row, col + 9, fixed_deduction_total, main_heading)
                            fixed_deduction_grand_total += fixed_deduction_total
                        if saudi_gosi_total:
                            sheet.write_number(row, col + 10, saudi_gosi_total, main_heading)
                            saudi_gosi_grand_total += saudi_gosi_total
                        if company_gosi_22_total:
                            sheet.write_number(row, col + 11, company_gosi_22_total, main_heading)
                            company_gosi_22_grand_total += company_gosi_22_total
                        if company_gosi_12_total:
                            sheet.write_number(row, col + 12, company_gosi_12_total, main_heading)
                            company_gosi_12_grand_total += company_gosi_12_total
                        if net_total:
                            sheet.write_number(row, col + 13, net_total, main_heading)
                            net_grand_total += net_total
                        row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_number(row, col + 1, employee_grand_total, main_heading)
                sheet.write_number(row, col + 2, wage_grand_total, main_heading)
                sheet.write_number(row, col + 3, transport_grand_total, main_heading)
                sheet.write_number(row, col + 4, house_rent_grand_total, main_heading)
                sheet.write_number(row, col + 5, food_grand_total, main_heading)
                sheet.write_number(row, col + 6, work_nature_grand_total, main_heading)
                sheet.write_number(row, col + 7, gross_grand_total, main_heading)
                sheet.write_number(row, col + 8, fixed_additional_grand_total, main_heading)
                sheet.write_number(row, col + 9, fixed_deduction_grand_total, main_heading)
                sheet.write_number(row, col + 10, saudi_gosi_grand_total, main_heading)
                sheet.write_number(row, col + 11, company_gosi_22_grand_total, main_heading)
                sheet.write_number(row, col + 12, company_gosi_12_grand_total, main_heading)
                sheet.write_number(row, col + 13, net_grand_total, main_heading)