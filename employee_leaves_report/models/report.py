import pandas as pd
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ReportEmployeeAnnualReport(models.TransientModel):
    _name = 'report.employee_leaves_report.employee_leaves_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    # @api.multi
    def generate_xlsx_report(self, workbook, input_records, lines):
        data = input_records['form']

        main_heading = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#D3D3D3',
            'font_size': '10',
        })

        main_heading1 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#D3D3D3',
            'font_size': '10',
        })

        main_heading2 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'right',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#D3D3D3',
            'font_size': '10',
        })

        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': '13',
            "font_color": 'black',
            'bg_color': '#D3D3D3'})

        main_data = workbook.add_format({
            "align": 'left',
            "valign": 'vcenter',
            'font_size': '8',
        })

        merge_format.set_shrink()
        main_heading.set_text_justlast(1)
        main_data.set_border()
        worksheet = workbook.add_worksheet('Employee Annual Leaves')
        worksheet.merge_range('A1:K1', "Employee Annual Leaves", merge_format)
        # worksheet.merge_range('A2:K2', "تقرير تفصيلي لمبيعات نقل البضائع", merge_format)
        if len(data['employee_ids']) == 1:
            emp = self.env['hr.employee'].browse(data['employee_ids'][0])
            worksheet.write('A3', 'الكود الوظيفي', main_heading1)
            worksheet.write('A4', 'Employee Code', main_heading1)
            worksheet.write('A5', str(emp.employee_code), main_heading1)
            worksheet.write('C3', 'إسم الموظف', main_heading1)
            worksheet.write('C4', 'Employee Name', main_heading1)
            worksheet.write('C5', str(emp.name), main_heading1)
            worksheet.write('A7', 'تاريخ الحركة', main_heading1)
            worksheet.write('B7', 'البيان', main_heading1)
            worksheet.write('C7', 'مخصص', main_heading1)
            worksheet.write('D7', 'إجازات مصروفة', main_heading1)
            worksheet.write('E7', 'الرصيد', main_heading1)
            worksheet.write('A8', 'Date', main_heading1)
            worksheet.write('B8', 'Description', main_heading1)
            worksheet.write('C8', 'Annual Leaves Allocated', main_heading1)
            worksheet.write('D8', 'Leaves Consumed', main_heading1)
            worksheet.write('E8', 'Annual Leaves Credit', main_heading1)
            worksheet.set_column('A:AB', 15)
        else:
            worksheet.write('A3', 'التاريخ من', main_heading1)
            worksheet.write('A4', 'Date From', main_heading1)
            worksheet.write('A5', str(data['form']), main_heading1)
            worksheet.write('C3', 'التاريخ إلى', main_heading1)
            worksheet.write('C4', 'Date To', main_heading1)
            worksheet.write('C5', str(data['to']), main_heading1)

            worksheet.write('A7', 'Counter', main_heading1)
            worksheet.write('B7', 'الكود الوظيفي / Employee Code', main_heading1)
            worksheet.write('C7', 'مخصص/ Annual Leaves Allocated', main_heading1)
            worksheet.write('D7', 'إجازات مصروفة / Leaves Consumed', main_heading1)
            worksheet.write('E7', ' الرصيد / Annual Leaves Credit', main_heading1)
            worksheet.set_column('A:AB', 15)
        domain = [('state', '=', 'validate'), ('holiday_status_id.is_annual', '=', True)]

        if len(data['employee_ids']) > 1:
            if data['form'] and data['to']:
                domain += [('create_date', '>=', data['form']), ('create_date', '<=', data['to'])]
            index = 0
            col = 0
            row = 8
            for rec in data['employee_ids']:
                emp = self.env['hr.employee'].browse(rec)
                if emp:
                    emp_domain = domain + [('employee_id', '=', emp.id)]
                    annual_leaves_allocated = sum(
                        self.env['hr.leave.allocation'].search(emp_domain).mapped('number_of_days'))
                    leaves_consumed = sum(self.env['hr.leave'].search(emp_domain).mapped('number_of_days'))
                    annual_leaves_credit = annual_leaves_allocated - leaves_consumed
                    worksheet.write_string(row, col + 0, str(index), main_data)
                    worksheet.write_string(row, col + 1, str(emp.employee_code), main_data)
                    worksheet.write_string(row, col + 2, str(annual_leaves_allocated), main_data)
                    worksheet.write_string(row, col + 3, str(leaves_consumed), main_data)
                    worksheet.write_string(row, col + 4, str(annual_leaves_credit), main_data)
                    row += 1
                    index += 1
        else:
            col = 0
            row = 8
            employee_id = emp = self.env['hr.employee'].browse(data['employee_ids'][0])
            domain += [('employee_id', '=', employee_id.id)]
            domain += [('create_date', '<', data['form'])]

            r1_ala = sum(self.env['hr.leave.allocation'].search(domain).mapped('number_of_days'))
            r1_lc = sum(self.env['hr.leave'].search(domain).mapped('number_of_days'))
            r1_alc = r1_ala - r1_lc
            yesterday = datetime.strptime(data['form'], DEFAULT_SERVER_DATE_FORMAT) - timedelta(days=1)
            worksheet.write_string(row, col + 0, yesterday.strftime("%d-%b-%Y"), main_data)
            worksheet.write_string(row, col + 1, 'رصيد مرحل / Initial Credit', main_data)
            worksheet.write_string(row, col + 2, str(r1_ala), main_data)
            worksheet.write_string(row, col + 3, str(r1_lc), main_data)
            worksheet.write_string(row, col + 4, str(r1_alc), main_data)

            row += 1
            domain2 = [('employee_id', '=', employee_id.id), ('create_date', '>=', data['form']),
                       ('create_date', '<=', data['to']), ('state', '=', 'validate')]
            allocation_ids = self.env['hr.leave.allocation'].search(domain2)
            leave_ids = self.env['hr.leave'].search(domain2)

            dates = set(allocation_ids.mapped('create_date') + leave_ids.mapped('create_date'))
            
            for date in dates:
                today_allocated_recs = allocation_ids.filtered(lambda al: al.create_date.date() == date.date())
                today_allocated_days = today_allocated_recs and sum(today_allocated_recs.mapped('number_of_days')) or 0
                today_leave_request_recs = leave_ids.filtered(lambda leave: leave.create_date.date() == date.date())
                today_leave_days = today_leave_request_recs and sum(today_leave_request_recs.mapped('number_of_days')) or 0
                worksheet.write_string(row, col + 0, date.strftime("%d-%b-%Y"), main_data)
                if not today_leave_request_recs:
                    worksheet.write_string(row, col + 1, 'مخصص شهري / Annual leave allocation', main_data)
                elif not today_allocated_recs:
                    worksheet.write_string(row, col + 1, 'إجازة من الرصيد / Leave request', main_data)
                else:
                    worksheet.write_string(row, col + 1, 'مخصص شهري / Annual leave allocation + إجازة من الرصيد / Leave request', main_data)

                worksheet.write_string(row, col + 2, str(today_allocated_days), main_data)
                r1_lc += today_leave_days
                worksheet.write_string(row, col + 3, str(today_leave_days), main_data)
                r1_alc += today_allocated_days
                today_credit =  r1_alc - r1_lc
                worksheet.write_string(row, col + 4, str(today_credit), main_data)

                row += 1
            worksheet.write_string(row, col + 0, 'الاجمالي / total', main_data)
            worksheet.write_string(row, col + 2, str(r1_alc), main_data)
            worksheet.write_string(row, col + 3, str(r1_lc), main_data)
            worksheet.write_string(row, col + 4, str(r1_alc - r1_lc), main_data)
