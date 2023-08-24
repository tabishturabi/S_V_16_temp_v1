from odoo import models


class EmployeeDirectoryReportExcel(models.AbstractModel):
    _name = 'report.bsg_employee_reports.employee_directory_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_employee_status(self, employee_status):
        domain = []
        if employee_status == 'on_job':
            domain += [('employee_state', '=', 'on_job')]
        if employee_status == 'on_leave':
            domain += [('employee_state', '=', 'on_leave')]
        if employee_status == 'return_from_holiday':
            domain += [('employee_state', '=', 'return_from_holiday')]
        if employee_status == 'resignation':
            domain += [('employee_state', '=', 'resignation')]
        if employee_status == 'suspended':
            domain += [('employee_state', '=', 'suspended')]
        if employee_status == 'service_expired':
            domain += [('employee_state', '=', 'service_expired')]
        if employee_status == 'contract_terminated':
            domain += [('employee_state', '=', 'contract_terminated')]
        if employee_status == 'ending_contract_during_trial_period':
            domain += [('employee_state', '=', 'ending_contract_during_trial_period')]
        return domain

    def get_appointment_decision(self, employee):
        return self.sudo().env["employees.appointment"].search(
            [("employee_name", "=", employee.id), ("decision_type", "=", "appoint_employee")], order='id desc', limit=1)

    def get_transfer_decision(self, employee):
        return self.sudo().env["employees.appointment"].search(
            [("employee_name", "=", employee.id), ("decision_type", "=", "transfer_employee")], order='id desc', limit=1)

    def generate_xlsx_report(self, workbook, lines, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].sudo().browse(self.env.context.get('active_id'))
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
        main_heading2_group = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            # "bg_color": '#00cc44',
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
        sheet = workbook.add_worksheet('Employee Directory Information Report')
        sheet.set_column('A:W', 15)
        domain = []
        row = 2
        col = 0
        sheet.write(row, col + 2, 'Print Date', main_heading2)
        sheet.write_string(row, col + 3, str(docs.print_date_time.strftime('%Y-%m-%d %H:%M:%S')), main_heading)
        # domain from selection options
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
        if docs.company_ids:
            domain += [('company_id', 'in', docs.company_ids.ids)]
            sheet.write(row, col, 'Company', main_heading2)
            rec_names = docs.company_ids.mapped('name')
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
        # domain from employee status
        domain += self.get_employee_status(docs.employee_status)

        employee_ids = self.sudo().env['hr.employee'].search(domain)
        row += 1

        # # ALL ##
        ###########
        if docs.grouping_by == 'all':
            self.sudo().env.ref('bsg_employee_reports.employee_directory_report_xlsx_action').report_file = \
                "Employee Directory Report"
            sheet.merge_range('A1:W1', 'تقرير معلومات الموظف', main_heading3)
            sheet.merge_range('A2:W2', 'Employee Salary Information Report', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Region', main_heading2)
            sheet.write(row, col + 5, 'Branch', main_heading2)
            sheet.write(row, col + 6, 'Department', main_heading2)
            sheet.write(row, col + 7, 'Manager', main_heading2)
            sheet.write(row, col + 8, 'Jop Position', main_heading2)
            sheet.write(row, col + 9, 'Employ Status', main_heading2)
            sheet.write(row, col + 10, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 11, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 12, 'Mobile No.', main_heading2)
            sheet.write(row, col + 13, 'Nationality', main_heading2)
            sheet.write(row, col + 14, 'ID No.', main_heading2)
            sheet.write(row, col + 15, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 16, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 17, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 18, 'Date of Join', main_heading2)
            sheet.write(row, col + 19, 'Appointment Decision', main_heading2)
            sheet.write(row, col + 20, 'Date of Appointment Decision', main_heading2)
            sheet.write(row, col + 21, 'Transfer Decision', main_heading2)
            sheet.write(row, col + 22, 'Date of Transfer Decision', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'منطقة', main_heading2)
            sheet.write(row, col + 5, 'الفرع', main_heading2)
            sheet.write(row, col + 6, 'الادارة', main_heading2)
            sheet.write(row, col + 7, 'المدير', main_heading2)
            sheet.write(row, col + 8, 'الوظيفه', main_heading2)
            sheet.write(row, col + 9, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 10, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 11, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 12, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 13, 'الجنسية', main_heading2)
            sheet.write(row, col + 14, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 15, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 16, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 17, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 18, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 19, 'قرار التعيين', main_heading2)
            sheet.write(row, col + 20, 'تاريخ قرار التعيين', main_heading2)
            sheet.write(row, col + 21, 'قرار النقل ', main_heading2)
            sheet.write(row, col + 22, 'تاريخ قرار النقل', main_heading2)
            row += 1
            for employee_id in employee_ids:
                if employee_id:
                    appointment_decision = self.sudo().get_appointment_decision(employee_id)
                    transfer_decision = self.sudo().get_transfer_decision(employee_id)

                    if employee_id.driver_code:
                        sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                    if employee_id.employee_code:
                        sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                    if employee_id.name:
                        sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                    if employee_id.name_english:
                        sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                    if employee_id.branch_id.region.bsg_region_name:
                        sheet.write_string(row, col + 4, str(employee_id.branch_id.region.bsg_region_name),
                                           main_heading)
                    if employee_id.branch_id.branch_ar_name:
                        sheet.write_string(row, col + 5,str(employee_id.branch_id.branch_ar_name), main_heading)
                    if employee_id.department_id.display_name:
                        sheet.write_string(row, col + 6,str(employee_id.department_id.display_name), main_heading)
                    if employee_id.parent_id.name:
                        sheet.write_string(row, col + 7,str(employee_id.parent_id.name), main_heading)
                    if employee_id.job_id.name:
                        sheet.write_string(row, col + 8,str(employee_id.job_id.name), main_heading)
                    if employee_id.employee_state:
                        sheet.write_string(row, col + 9,str(employee_id.employee_state), main_heading)
                    if employee_id.suspend_salary:
                        sheet.write_string(row, col + 10,str('True'), main_heading)
                    if employee_id.last_return_date:
                        sheet.write_string(row, col + 11, str(employee_id.last_return_date), main_heading)
                    if employee_id.mobile_phone:
                        sheet.write_string(row, col + 12,str(employee_id.mobile_phone), main_heading)
                    if employee_id.country_id.name:
                        sheet.write_string(row, col + 13, str(employee_id.country_id.name), main_heading)
                    if employee_id.country_id:
                        if employee_id.country_id.code == 'SA':
                            if employee_id.bsg_national_id.bsg_nationality_name:
                                sheet.write_string(row, col + 14, str(employee_id.bsg_national_id.bsg_nationality_name),
                                                   main_heading)
                        else:
                            if employee_id.bsg_empiqama.bsg_iqama_name:
                                sheet.write_string(row, col + 14,
                                                   str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                   main_heading)
                    if employee_id.bsg_bank_id.bsg_acc_number:
                        sheet.write_string(row, col + 15,str(employee_id.bsg_bank_id.bsg_acc_number), main_heading)
                    if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                        sheet.write_string(row, col + 16,str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code), main_heading)
                    if employee_id.salary_payment_method:
                        sheet.write_string(row, col + 17, str(employee_id.salary_payment_method), main_heading)
                    # if employee_id.category_ids:
                    #     rec_names = employee_id.category_ids.mapped('name')
                    #     names = ','.join(rec_names)
                    #     sheet.write_string(row, col+17, str(names), main_heading)
                    if employee_id.bsgjoining_date:
                        sheet.write_string(row, col + 18, str(employee_id.bsgjoining_date), main_heading)
                    if appointment_decision:
                        sheet.write_string(row, col + 19, str(appointment_decision.name_get()[0][1]), main_heading)
                        sheet.write_string(row, col + 20, str(appointment_decision.decision_date), main_heading)
                    if transfer_decision:
                        sheet.write_string(row, col + 21, str(transfer_decision.name_get()[0][1]), main_heading)
                        sheet.write_string(row, col + 22, str(transfer_decision.decision_date), main_heading)
                    row += 1
        # # branches ##
        ###########
        if docs.grouping_by == 'by_branches':
            self.sudo().env.ref(
                'bsg_employee_reports.employee_directory_report_xlsx_action').report_file = \
                "Employee Directory Report Group By Branches"
            sheet.merge_range('A1:W1', 'مجموعة تقرير معلومات الموظف حسب الفروع', main_heading3)
            sheet.merge_range('A2:W2', 'Employee  Directory Report Group By Branches', main_heading3)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Region', main_heading2)
            sheet.write(row, col + 5, 'Branch', main_heading2)
            sheet.write(row, col + 6, 'Department', main_heading2)
            sheet.write(row, col + 7, 'Manager', main_heading2)
            sheet.write(row, col + 8, 'Jop Position', main_heading2)
            sheet.write(row, col + 9, 'Employ Status', main_heading2)
            sheet.write(row, col + 10, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 11, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 12, 'Mobile No.', main_heading2)
            sheet.write(row, col + 13, 'Nationality', main_heading2)
            sheet.write(row, col + 14, 'ID No.', main_heading2)
            sheet.write(row, col + 15, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 16, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 17, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 18, 'Date of Join', main_heading2)
            sheet.write(row, col + 19, 'Appointment Decision', main_heading2)
            sheet.write(row, col + 20, 'Date of Appointment Decision', main_heading2)
            sheet.write(row, col + 21, 'Transfer Decision', main_heading2)
            sheet.write(row, col + 22, 'Date of Transfer Decision', main_heading2)

            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'منطقة', main_heading2)
            sheet.write(row, col + 5, 'الفرع', main_heading2)
            sheet.write(row, col + 6, 'الادارة', main_heading2)
            sheet.write(row, col + 7, 'المدير', main_heading2)
            sheet.write(row, col + 8, 'الوظيفه', main_heading2)
            sheet.write(row, col + 9, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 10, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 11, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 12, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 13, 'الجنسية', main_heading2)
            sheet.write(row, col + 14, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 15, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 16, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 17, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 18, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 19, 'قرار التعيين', main_heading2)
            sheet.write(row, col + 20, 'تاريخ قرار التعيين', main_heading2)
            sheet.write(row, col + 21, 'قرار النقل ', main_heading2)
            sheet.write(row, col + 22, 'تاريخ قرار النقل', main_heading2)
            row += 1
            branch_list = []
            branch_ids = self.sudo().env['bsg_branches.bsg_branches'].search([])
            for branch_id in branch_ids:
                if branch_id:
                    branch_list.append(branch_id.branch_ar_name)
            for branch_name in branch_list:
                if branch_name:
                    branch_employee_ids = employee_ids.filtered(lambda r:r.branch_id.branch_ar_name == branch_name)
                    if branch_employee_ids:
                        sheet.write(row, col, 'Branch', main_heading2)
                        sheet.write(row, col + 1, 'الفرع', main_heading2)
                        sheet.merge_range(row, col + 2, row, 22, str(branch_name), main_heading2_group)
                        row += 1
                        for employee_id in branch_employee_ids:
                            if employee_id:
                                appointment_decision = self.sudo().get_appointment_decision(employee_id)
                                transfer_decision = self.sudo().get_transfer_decision(employee_id)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                if employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                if employee_id.name:
                                    sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                if employee_id.name_english:
                                    sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                if employee_id.branch_id.region.bsg_region_name:
                                    sheet.write_string(row, col + 4, str(employee_id.branch_id.region.bsg_region_name),
                                                       main_heading)
                                if employee_id.branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 5, str(employee_id.branch_id.branch_ar_name),
                                                       main_heading)
                                if employee_id.department_id.display_name:
                                    sheet.write_string(row, col + 6, str(employee_id.department_id.display_name),
                                                       main_heading)
                                if employee_id.parent_id.name:
                                    sheet.write_string(row, col + 7, str(employee_id.parent_id.name), main_heading)
                                if employee_id.job_id.name:
                                    sheet.write_string(row, col + 8, str(employee_id.job_id.name), main_heading)
                                if employee_id.employee_state:
                                    sheet.write_string(row, col + 9, str(employee_id.employee_state), main_heading)
                                if employee_id.suspend_salary:
                                    sheet.write_string(row, col + 10, str('True'), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 11, str(employee_id.last_return_date), main_heading)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 12, str(employee_id.mobile_phone), main_heading)
                                if employee_id.country_id.name:
                                    sheet.write_string(row, col + 13, str(employee_id.country_id.name), main_heading)
                                if employee_id.country_id:
                                    if employee_id.country_id.code == 'SA':
                                        if employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 14,
                                                               str(employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 14,
                                                               str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if employee_id.bsg_bank_id.bsg_acc_number:
                                    sheet.write_string(row, col + 15, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                    sheet.write_string(row, col + 16,
                                                       str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                       main_heading)
                                if employee_id.salary_payment_method:
                                    sheet.write_string(row, col + 17, str(employee_id.salary_payment_method),
                                                       main_heading)
                                # if employee_id.category_ids:
                                #     rec_names = employee_id.category_ids.mapped('name')
                                #     names = ','.join(rec_names)
                                #     sheet.write_string(row, col+17, str(names), main_heading)
                                if employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 18, str(employee_id.bsgjoining_date), main_heading)
                                if appointment_decision:
                                    sheet.write_string(row, col + 19, str(appointment_decision.name_get()[0][1]),
                                                       main_heading)
                                    sheet.write_string(row, col + 20, str(appointment_decision.decision_date),
                                                       main_heading)
                                if transfer_decision:
                                    sheet.write_string(row, col + 21, str(transfer_decision.name_get()[0][1]),
                                                       main_heading)
                                    sheet.write_string(row, col + 22, str(transfer_decision.decision_date),
                                                       main_heading)
                                row += 1
                        row += 1
        if docs.grouping_by == 'by_departments':
            self.sudo().env.ref(
                'bsg_employee_reports.employee_directory_report_xlsx_action').report_file = \
                "Employee Directory Report Group By Departments"
            sheet.merge_range('A1:W1', 'مجموعة تقرير معلومات الموظف حسب الأقسام', main_heading3)
            sheet.merge_range('A2:W2', 'Employee Directory Report Group By Departments', main_heading3)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Region', main_heading2)
            sheet.write(row, col + 5, 'Branch', main_heading2)
            sheet.write(row, col + 6, 'Department', main_heading2)
            sheet.write(row, col + 7, 'Manager', main_heading2)
            sheet.write(row, col + 8, 'Jop Position', main_heading2)
            sheet.write(row, col + 9, 'Employ Status', main_heading2)
            sheet.write(row, col + 10, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 11, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 12, 'Mobile No.', main_heading2)
            sheet.write(row, col + 13, 'Nationality', main_heading2)
            sheet.write(row, col + 14, 'ID No.', main_heading2)
            sheet.write(row, col + 15, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 16, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 17, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 18, 'Date of Join', main_heading2)
            sheet.write(row, col + 19, 'Appointment Decision', main_heading2)
            sheet.write(row, col + 20, 'Date of Appointment Decision', main_heading2)
            sheet.write(row, col + 21, 'Transfer Decision', main_heading2)
            sheet.write(row, col + 22, 'Date of Transfer Decision', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'منطقة', main_heading2)
            sheet.write(row, col + 5, 'الفرع', main_heading2)
            sheet.write(row, col + 6, 'الادارة', main_heading2)
            sheet.write(row, col + 7, 'المدير', main_heading2)
            sheet.write(row, col + 8, 'الوظيفه', main_heading2)
            sheet.write(row, col + 9, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 10, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 11, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 12, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 13, 'الجنسية', main_heading2)
            sheet.write(row, col + 14, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 15, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 16, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 17, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 18, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 19, 'قرار التعيين', main_heading2)
            sheet.write(row, col + 20, 'تاريخ قرار التعيين', main_heading2)
            sheet.write(row, col + 21, 'قرار النقل ', main_heading2)
            sheet.write(row, col + 22, 'تاريخ قرار النقل', main_heading2)

            row += 1
            department_list = []
            main_depart_list = []
            department_ids = self.sudo().env['hr.department'].search([])
            if docs.is_parent_dempart:
                for department_id in department_ids:
                    if department_id:
                        if department_id.display_name.split('/')[0].strip() not in main_depart_list:
                            main_depart_list.append(department_id.display_name.split('/')[0].strip())
                for department_name in main_depart_list:
                    if department_name:
                        main_department_employee_ids = employee_ids.filtered(lambda r:r.department_id and r.department_id.display_name.split('/')[0].strip() == department_name)
                        if main_department_employee_ids:
                            sheet.write(row, col, 'Department', main_heading2)
                            sheet.write(row, col + 1, 'الادارة', main_heading2)
                            sheet.merge_range(row, col + 2, row, 22, str(department_name), main_heading2_group)
                            #
                            # sheet.write(row, col, 'Department', main_heading2)
                            # sheet.write_string(row, col + 1, str(department_name), main_heading)
                            # sheet.write(row, col + 2, 'الادارة', main_heading2)
                            row += 1
                            for employee_id in main_department_employee_ids:
                                if employee_id:
                                    appointment_decision = self.sudo().get_appointment_decision(employee_id)
                                    transfer_decision = self.sudo().get_transfer_decision(employee_id)
                                    if employee_id.driver_code:
                                        sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                    if employee_id.employee_code:
                                        sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                    if employee_id.name:
                                        sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                    if employee_id.name_english:
                                        sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                    if employee_id.branch_id.region.bsg_region_name:
                                        sheet.write_string(row, col + 4,
                                                           str(employee_id.branch_id.region.bsg_region_name),
                                                           main_heading)
                                    if employee_id.branch_id.branch_ar_name:
                                        sheet.write_string(row, col + 5, str(employee_id.branch_id.branch_ar_name),
                                                           main_heading)
                                    if employee_id.department_id.display_name:
                                        sheet.write_string(row, col + 6, str(employee_id.department_id.display_name),
                                                           main_heading)
                                    if employee_id.parent_id.name:
                                        sheet.write_string(row, col + 7, str(employee_id.parent_id.name), main_heading)
                                    if employee_id.job_id.name:
                                        sheet.write_string(row, col + 8, str(employee_id.job_id.name), main_heading)
                                    if employee_id.employee_state:
                                        sheet.write_string(row, col + 9, str(employee_id.employee_state), main_heading)
                                    if employee_id.suspend_salary:
                                        sheet.write_string(row, col + 10, str('True'), main_heading)
                                    if employee_id.last_return_date:
                                        sheet.write_string(row, col + 11, str(employee_id.last_return_date),
                                                           main_heading)
                                    if employee_id.mobile_phone:
                                        sheet.write_string(row, col + 12, str(employee_id.mobile_phone), main_heading)
                                    if employee_id.country_id.name:
                                        sheet.write_string(row, col + 13, str(employee_id.country_id.name),
                                                           main_heading)
                                    if employee_id.country_id:
                                        if employee_id.country_id.code == 'SA':
                                            if employee_id.bsg_national_id.bsg_nationality_name:
                                                sheet.write_string(row, col + 14,
                                                                   str(employee_id.bsg_national_id.bsg_nationality_name),
                                                                   main_heading)
                                        else:
                                            if employee_id.bsg_empiqama.bsg_iqama_name:
                                                sheet.write_string(row, col + 14,
                                                                   str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                                   main_heading)
                                    if employee_id.bsg_bank_id.bsg_acc_number:
                                        sheet.write_string(row, col + 15, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                           main_heading)
                                    if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                        sheet.write_string(row, col + 16,
                                                           str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                           main_heading)
                                    if employee_id.salary_payment_method:
                                        sheet.write_string(row, col + 17, str(employee_id.salary_payment_method),
                                                           main_heading)
                                    # if employee_id.category_ids:
                                    #     rec_names = employee_id.category_ids.mapped('name')
                                    #     names = ','.join(rec_names)
                                    #     sheet.write_string(row, col+17, str(names), main_heading)
                                    if employee_id.bsgjoining_date:
                                        sheet.write_string(row, col + 18, str(employee_id.bsgjoining_date),
                                                           main_heading)
                                    if appointment_decision:
                                        sheet.write_string(row, col + 19, str(appointment_decision.name_get()[0][1]),
                                                           main_heading)
                                        sheet.write_string(row, col + 20, str(appointment_decision.decision_date),
                                                           main_heading)
                                    if transfer_decision:
                                        sheet.write_string(row, col + 21, str(transfer_decision.name_get()[0][1]),
                                                           main_heading)
                                        sheet.write_string(row, col + 22, str(transfer_decision.decision_date),
                                                           main_heading)
                                    row += 1
                            row += 1
            if not docs.is_parent_dempart:
                for department_id in department_ids:
                    if department_id:
                        if department_id.display_name not in department_list:
                            department_list.append(department_id.display_name)
                for department_name in department_list:
                    if department_name:
                        department_employee_ids = employee_ids.filtered(lambda r: r.department_id.display_name == department_name)
                        if department_employee_ids:
                            sheet.write(row, col, 'Department', main_heading2)
                            sheet.write(row, col + 1, 'الادارة', main_heading2)
                            sheet.merge_range(row, col + 2, row, 22, str(department_name), main_heading2_group)

                            # sheet.write(row, col, 'Department', main_heading2)
                            # sheet.write_string(row, col + 1, str(department_name), main_heading)
                            # sheet.write(row, col + 2, 'الادارة', main_heading2)
                            row += 1
                            for employee_id in department_employee_ids:
                                if employee_id:
                                    appointment_decision = self.sudo().get_appointment_decision(employee_id)
                                    transfer_decision = self.sudo().get_transfer_decision(employee_id)
                                    if employee_id.driver_code:
                                        sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                    if employee_id.employee_code:
                                        sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                    if employee_id.name:
                                        sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                    if employee_id.name_english:
                                        sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                    if employee_id.branch_id.region.bsg_region_name:
                                        sheet.write_string(row, col + 4,
                                                           str(employee_id.branch_id.region.bsg_region_name),
                                                           main_heading)
                                    if employee_id.branch_id.branch_ar_name:
                                        sheet.write_string(row, col + 5, str(employee_id.branch_id.branch_ar_name),
                                                           main_heading)
                                    if employee_id.department_id.display_name:
                                        sheet.write_string(row, col + 6, str(employee_id.department_id.display_name),
                                                           main_heading)
                                    if employee_id.parent_id.name:
                                        sheet.write_string(row, col + 7, str(employee_id.parent_id.name), main_heading)
                                    if employee_id.job_id.name:
                                        sheet.write_string(row, col + 8, str(employee_id.job_id.name), main_heading)
                                    if employee_id.employee_state:
                                        sheet.write_string(row, col + 9, str(employee_id.employee_state), main_heading)
                                    if employee_id.suspend_salary:
                                        sheet.write_string(row, col + 10, str('True'), main_heading)
                                    if employee_id.last_return_date:
                                        sheet.write_string(row, col + 11, str(employee_id.last_return_date),
                                                           main_heading)
                                    if employee_id.mobile_phone:
                                        sheet.write_string(row, col + 12, str(employee_id.mobile_phone), main_heading)
                                    if employee_id.country_id.name:
                                        sheet.write_string(row, col + 13, str(employee_id.country_id.name),
                                                           main_heading)
                                    if employee_id.country_id:
                                        if employee_id.country_id.code == 'SA':
                                            if employee_id.bsg_national_id.bsg_nationality_name:
                                                sheet.write_string(row, col + 14,
                                                                   str(employee_id.bsg_national_id.bsg_nationality_name),
                                                                   main_heading)
                                        else:
                                            if employee_id.bsg_empiqama.bsg_iqama_name:
                                                sheet.write_string(row, col + 14,
                                                                   str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                                   main_heading)
                                    if employee_id.bsg_bank_id.bsg_acc_number:
                                        sheet.write_string(row, col + 15, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                           main_heading)
                                    if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                        sheet.write_string(row, col + 16,
                                                           str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                           main_heading)
                                    if employee_id.salary_payment_method:
                                        sheet.write_string(row, col + 17, str(employee_id.salary_payment_method),
                                                           main_heading)
                                    # if employee_id.category_ids:
                                    #     rec_names = employee_id.category_ids.mapped('name')
                                    #     names = ','.join(rec_names)
                                    #     sheet.write_string(row, col+17, str(names), main_heading)
                                    if employee_id.bsgjoining_date:
                                        sheet.write_string(row, col + 18, str(employee_id.bsgjoining_date),
                                                           main_heading)
                                    if appointment_decision:
                                        sheet.write_string(row, col + 19, str(appointment_decision.name_get()[0][1]),
                                                           main_heading)
                                        sheet.write_string(row, col + 20, str(appointment_decision.decision_date),
                                                           main_heading)
                                    if transfer_decision:
                                        sheet.write_string(row, col + 21, str(transfer_decision.name_get()[0][1]),
                                                           main_heading)
                                        sheet.write_string(row, col + 22, str(transfer_decision.decision_date),
                                                           main_heading)
                                    row += 1
                            row += 1
        if docs.grouping_by == 'by_job_positions':
            self.sudo().env.ref(
                'bsg_employee_reports.employee_directory_report_xlsx_action').report_file = \
                "Employee Directory Report Group By Job Position"
            sheet.merge_range('A1:W1', 'مجموعة تقرير معلومات الموظف حسب الوظيفة', main_heading3)
            sheet.merge_range('A2:W2', 'Employee Directory Report Group By Job Position', main_heading3)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Region', main_heading2)
            sheet.write(row, col + 5, 'Branch', main_heading2)
            sheet.write(row, col + 6, 'Department', main_heading2)
            sheet.write(row, col + 7, 'Manager', main_heading2)
            sheet.write(row, col + 8, 'Jop Position', main_heading2)
            sheet.write(row, col + 9, 'Employ Status', main_heading2)
            sheet.write(row, col + 10, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 11, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 12, 'Mobile No.', main_heading2)
            sheet.write(row, col + 13, 'Nationality', main_heading2)
            sheet.write(row, col + 14, 'ID No.', main_heading2)
            sheet.write(row, col + 15, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 16, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 17, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 18, 'Date of Join', main_heading2)
            sheet.write(row, col + 19, 'Appointment Decision', main_heading2)
            sheet.write(row, col + 20, 'Date of Appointment Decision', main_heading2)
            sheet.write(row, col + 21, 'Transfer Decision', main_heading2)
            sheet.write(row, col + 22, 'Date of Transfer Decision', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'منطقة', main_heading2)
            sheet.write(row, col + 5, 'الفرع', main_heading2)
            sheet.write(row, col + 6, 'الادارة', main_heading2)
            sheet.write(row, col + 7, 'المدير', main_heading2)
            sheet.write(row, col + 8, 'الوظيفه', main_heading2)
            sheet.write(row, col + 9, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 10, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 11, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 12, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 13, 'الجنسية', main_heading2)
            sheet.write(row, col + 14, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 15, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 16, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 17, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 18, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 19, 'قرار التعيين', main_heading2)
            sheet.write(row, col + 20, 'تاريخ قرار التعيين', main_heading2)
            sheet.write(row, col + 21, 'قرار النقل ', main_heading2)
            sheet.write(row, col + 22, 'تاريخ قرار النقل', main_heading2)
            row += 1
            job_position_list = []
            job_ids = self.sudo().env['hr.job'].search([])
            for job_id in job_ids:
                if job_id:
                    job_position_list.append(job_id.name)
            for job_position_name in job_position_list:
                if job_position_name:
                    job_employee_ids = employee_ids.filtered(lambda r: r.job_id.name == job_position_name)
                    if job_employee_ids:
                        sheet.write(row, col, 'Job Position', main_heading2)
                        sheet.write(row, col + 1, 'الوظيفه', main_heading2)
                        sheet.merge_range(row, col + 2, row, 22, str(job_position_name), main_heading2_group)
                        #
                        # sheet.write(row, col, 'Job Position', main_heading2)
                        # sheet.write_string(row, col + 1, str(job_position_name), main_heading)
                        # sheet.write(row, col + 2, 'الوظيفه', main_heading2)
                        row += 1
                        for employee_id in job_employee_ids:
                            if employee_id:
                                appointment_decision = self.sudo().get_appointment_decision(employee_id)
                                transfer_decision = self.sudo().get_transfer_decision(employee_id)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                if employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                if employee_id.name:
                                    sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                if employee_id.name_english:
                                    sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                if employee_id.branch_id.region.bsg_region_name:
                                    sheet.write_string(row, col + 4, str(employee_id.branch_id.region.bsg_region_name),
                                                       main_heading)
                                if employee_id.branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 5, str(employee_id.branch_id.branch_ar_name),
                                                       main_heading)
                                if employee_id.department_id.display_name:
                                    sheet.write_string(row, col + 6, str(employee_id.department_id.display_name),
                                                       main_heading)
                                if employee_id.parent_id.name:
                                    sheet.write_string(row, col + 7, str(employee_id.parent_id.name), main_heading)
                                if employee_id.job_id.name:
                                    sheet.write_string(row, col + 8, str(employee_id.job_id.name), main_heading)
                                if employee_id.employee_state:
                                    sheet.write_string(row, col + 9, str(employee_id.employee_state), main_heading)
                                if employee_id.suspend_salary:
                                    sheet.write_string(row, col + 10, str('True'), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 11, str(employee_id.last_return_date), main_heading)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 12, str(employee_id.mobile_phone), main_heading)
                                if employee_id.country_id.name:
                                    sheet.write_string(row, col + 13, str(employee_id.country_id.name), main_heading)
                                if employee_id.country_id:
                                    if employee_id.country_id.code == 'SA':
                                        if employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 14,
                                                               str(employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 14,
                                                               str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if employee_id.bsg_bank_id.bsg_acc_number:
                                    sheet.write_string(row, col + 15, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                    sheet.write_string(row, col + 16,
                                                       str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                       main_heading)
                                if employee_id.salary_payment_method:
                                    sheet.write_string(row, col + 17, str(employee_id.salary_payment_method),
                                                       main_heading)
                                # if employee_id.category_ids:
                                #     rec_names = employee_id.category_ids.mapped('name')
                                #     names = ','.join(rec_names)
                                #     sheet.write_string(row, col+17, str(names), main_heading)
                                if employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 18, str(employee_id.bsgjoining_date), main_heading)
                                if appointment_decision:
                                    sheet.write_string(row, col + 19, str(appointment_decision.name_get()[0][1]),
                                                       main_heading)
                                    sheet.write_string(row, col + 20, str(appointment_decision.decision_date),
                                                       main_heading)
                                if transfer_decision:
                                    sheet.write_string(row, col + 21, str(transfer_decision.name_get()[0][1]),
                                                       main_heading)
                                    sheet.write_string(row, col + 22, str(transfer_decision.decision_date),
                                                       main_heading)
                                row += 1
                        row += 1
        if docs.grouping_by == 'by_nationality':
            self.sudo().env.ref(
                'bsg_employee_reports.employee_directory_report_xlsx_action').report_file = \
                "Employee Directory Report Group By Nationality"
            sheet.merge_range('A1:W1', 'مجموعة تقرير معلومات الموظف حسب الجنسية', main_heading3)
            sheet.merge_range('A2:W2', 'Employee Directory Report Group By Nationality', main_heading3)
            sheet.write(row, col, 'Employee Id', main_heading2)
            sheet.write(row, col + 1, 'Employee Code', main_heading2)
            sheet.write(row, col + 2, 'Employee Name', main_heading2)
            sheet.write(row, col + 3, 'English Name', main_heading2)
            sheet.write(row, col + 4, 'Region', main_heading2)
            sheet.write(row, col + 5, 'Branch', main_heading2)
            sheet.write(row, col + 6, 'Department', main_heading2)
            sheet.write(row, col + 7, 'Manager', main_heading2)
            sheet.write(row, col + 8, 'Jop Position', main_heading2)
            sheet.write(row, col + 9, 'Employ Status', main_heading2)
            sheet.write(row, col + 10, 'Suspend Salary', main_heading2)
            sheet.write(row, col + 11, 'Last Return Leaves Date', main_heading2)
            sheet.write(row, col + 12, 'Mobile No.', main_heading2)
            sheet.write(row, col + 13, 'Nationality', main_heading2)
            sheet.write(row, col + 14, 'ID No.', main_heading2)
            sheet.write(row, col + 15, 'Bank Account Number', main_heading2)
            sheet.write(row, col + 16, 'Bank Swift Code', main_heading2)
            sheet.write(row, col + 17, 'Salary Payment Method', main_heading2)
            sheet.write(row, col + 18, 'Date of Join', main_heading2)
            sheet.write(row, col + 19, 'Appointment Decision', main_heading2)
            sheet.write(row, col + 20, 'Date of Appointment Decision', main_heading2)
            sheet.write(row, col + 21, 'Transfer Decision', main_heading2)
            sheet.write(row, col + 22, 'Date of Transfer Decision', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'كود الموظف', main_heading2)
            sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 3, 'الاسم الانجليزي', main_heading2)
            sheet.write(row, col + 4, 'منطقة', main_heading2)
            sheet.write(row, col + 5, 'الفرع', main_heading2)
            sheet.write(row, col + 6, 'الادارة', main_heading2)
            sheet.write(row, col + 7, 'المدير', main_heading2)
            sheet.write(row, col + 8, 'الوظيفه', main_heading2)
            sheet.write(row, col + 9, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 10, 'تعليق الراتب ', main_heading2)
            sheet.write(row, col + 11, 'تاريخ اخر عوده', main_heading2)
            sheet.write(row, col + 12, 'رقم الجوال', main_heading2)
            sheet.write(row, col + 13, 'الجنسية', main_heading2)
            sheet.write(row, col + 14, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 15, 'رقم الحساب البنكي', main_heading2)
            sheet.write(row, col + 16, 'سوفت البنك ', main_heading2)
            sheet.write(row, col + 17, 'طريقة صرف الراتب', main_heading2)
            sheet.write(row, col + 18, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 19, 'قرار التعيين', main_heading2)
            sheet.write(row, col + 20, 'تاريخ قرار التعيين', main_heading2)
            sheet.write(row, col + 21, 'قرار النقل ', main_heading2)
            sheet.write(row, col + 22, 'تاريخ قرار النقل', main_heading2)

            row += 1
            country_list = []
            country_ids = self.sudo().env['res.country'].search([])
            for country_id in country_ids:
                if country_id:
                    country_list.append(country_id.name)
            for country_name in country_list:
                if country_name:
                    country_employee_ids = employee_ids.filtered(lambda r: r.country_id.name == country_name)
                    if country_employee_ids:
                        sheet.write(row, col, 'Nationality', main_heading2)
                        sheet.write(row, col + 1, 'الجنسية', main_heading2)
                        sheet.merge_range(row, col + 2, row, 22, str(country_name), main_heading2_group)

                        # sheet.write(row, col, 'Nationality', main_heading2)
                        # sheet.write_string(row, col + 1, str(country_name), main_heading)
                        # sheet.write(row, col + 2, 'الجنسية', main_heading2)
                        row += 1
                        for employee_id in country_employee_ids:
                            if employee_id:
                                appointment_decision = self.sudo().get_appointment_decision(employee_id)
                                transfer_decision = self.sudo().get_transfer_decision(employee_id)
                                if employee_id.driver_code:
                                    sheet.write_string(row, col, str(employee_id.driver_code), main_heading)
                                if employee_id.employee_code:
                                    sheet.write_string(row, col + 1, str(employee_id.employee_code), main_heading)
                                if employee_id.name:
                                    sheet.write_string(row, col + 2, str(employee_id.name), main_heading)
                                if employee_id.name_english:
                                    sheet.write_string(row, col + 3, str(employee_id.name_english), main_heading)
                                if employee_id.branch_id.region.bsg_region_name:
                                    sheet.write_string(row, col + 4, str(employee_id.branch_id.region.bsg_region_name),
                                                       main_heading)
                                if employee_id.branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 5, str(employee_id.branch_id.branch_ar_name),
                                                       main_heading)
                                if employee_id.department_id.display_name:
                                    sheet.write_string(row, col + 6, str(employee_id.department_id.display_name),
                                                       main_heading)
                                if employee_id.parent_id.name:
                                    sheet.write_string(row, col + 7, str(employee_id.parent_id.name), main_heading)
                                if employee_id.job_id.name:
                                    sheet.write_string(row, col + 8, str(employee_id.job_id.name), main_heading)
                                if employee_id.employee_state:
                                    sheet.write_string(row, col + 9, str(employee_id.employee_state), main_heading)
                                if employee_id.suspend_salary:
                                    sheet.write_string(row, col + 10, str('True'), main_heading)
                                if employee_id.last_return_date:
                                    sheet.write_string(row, col + 11, str(employee_id.last_return_date), main_heading)
                                if employee_id.mobile_phone:
                                    sheet.write_string(row, col + 12, str(employee_id.mobile_phone), main_heading)
                                if employee_id.country_id.name:
                                    sheet.write_string(row, col + 13, str(employee_id.country_id.name), main_heading)
                                if employee_id.country_id:
                                    if employee_id.country_id.code == 'SA':
                                        if employee_id.bsg_national_id.bsg_nationality_name:
                                            sheet.write_string(row, col + 14,
                                                               str(employee_id.bsg_national_id.bsg_nationality_name),
                                                               main_heading)
                                    else:
                                        if employee_id.bsg_empiqama.bsg_iqama_name:
                                            sheet.write_string(row, col + 14,
                                                               str(employee_id.bsg_empiqama.bsg_iqama_name),
                                                               main_heading)
                                if employee_id.bsg_bank_id.bsg_acc_number:
                                    sheet.write_string(row, col + 15, str(employee_id.bsg_bank_id.bsg_acc_number),
                                                       main_heading)
                                if employee_id.bsg_bank_id.bsg_swift_code_id.swift_code:
                                    sheet.write_string(row, col + 16,
                                                       str(employee_id.bsg_bank_id.bsg_swift_code_id.swift_code),
                                                       main_heading)
                                if employee_id.salary_payment_method:
                                    sheet.write_string(row, col + 17, str(employee_id.salary_payment_method),
                                                       main_heading)
                                # if employee_id.category_ids:
                                #     rec_names = employee_id.category_ids.mapped('name')
                                #     names = ','.join(rec_names)
                                #     sheet.write_string(row, col+17, str(names), main_heading)
                                if employee_id.bsgjoining_date:
                                    sheet.write_string(row, col + 18, str(employee_id.bsgjoining_date), main_heading)
                                if appointment_decision:
                                    sheet.write_string(row, col + 19, str(appointment_decision.name_get()[0][1]),
                                                       main_heading)
                                    sheet.write_string(row, col + 20, str(appointment_decision.decision_date),
                                                       main_heading)
                                if transfer_decision:
                                    sheet.write_string(row, col + 21, str(transfer_decision.name_get()[0][1]),
                                                       main_heading)
                                    sheet.write_string(row, col + 22, str(transfer_decision.decision_date),
                                                       main_heading)
                                row += 1

                        row += 1
