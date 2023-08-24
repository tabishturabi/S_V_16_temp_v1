from odoo import models
from datetime import datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict


class EmployeePayslipReportExcel(models.AbstractModel):
    _name = 'report.bsg_employee_payslip_report.employee_payslip_report_xlsx'
    _inherit ='report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook,lines,data=None):
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
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#acadb2',
            'font_size': '12',
        })
        sheet = workbook.add_worksheet('Employees Payslips')
        sheet.set_column('A2:A2',30)
        sheet.set_column('B:M',15)
        row=1
        col=0
        for rec in data.employee_id:
            sheet.write(row,col,'Employee ID',main_heading)
            sheet.write_string(row,col+1,str(rec.employee_code),main_heading)
            sheet.write(row,col+2,'Employee Name',main_heading)
            sheet.write_string(row,col+3,str(rec.name),main_heading)
            sheet.write(row+1,col,'Job Position',main_heading)
            sheet.write_string(row+1,col+1,str(rec.job_id.name),main_heading)
            sheet.write(row+1,col+2,'Joining Date',main_heading)
            sheet.write_string(row+1,col+3,rec.bsgjoining_date.strftime("%m/%d/%Y"))
            emp_payslip = self.env['hr.payslip'].search([('employee_id','=',rec.id),('date_from','<=',data.to_date),
                                                         ('date_to','>',data.from_date)])
            row+=3
            list_dict =[]
            if emp_payslip:
                rule_dict = self._get_payslips(emp_payslip)
                sheet.write(row,col,'Payslip Name',main_heading2)
                sheet.write(row, col+1, 'Month', main_heading2)
                sheet.write(row, col+2, 'Branch', main_heading2)
                sheet.write(row, col+3, 'Department', main_heading2)
                sheet.write(row, col+4, 'Job Position', main_heading2)
                sheet.write(row, col+5, 'Analytic Account', main_heading2)
                col+=6
                for key in rule_dict.keys():
                    rule_name = key.split('+')
                    sheet.write_string(row,col, rule_name[0], main_heading2)
                    col+=1
                row+=1
                col=0
                for payslip in emp_payslip:
                    if payslip:
                        month=payslip.date_from.strftime('%B')
                        year = payslip.date_from.year
                        slip_month = "%s %s" % (month, year)
                        analytic_account = payslip.move_id.line_ids.mapped('analytic_account_id')
                        print('Analytic Account',analytic_account.display_name)
                        rule_dict = self._get_payslips(emp_payslip)
                        for lines in payslip.line_ids:
                            for name,total in rule_dict.items():
                                split_code = name.split('+')
                                if split_code[1]==lines.code:
                                    rule_dict.update({
                                        name:abs(lines.total)
                                    })
                        list_dict.append(rule_dict)
                        sheet.write_string(row, col, payslip.name, main_heading)
                        sheet.write_string(row, col + 1, slip_month, main_heading)
                        sheet.write_string(row, col + 2, payslip.branch_id.branch_ar_name, main_heading)
                        sheet.write_string(row, col + 3, payslip.department_id.display_name, main_heading)
                        sheet.write_string(row, col + 4,payslip.job_id.name, main_heading)
                        sheet.write_string(row, col + 5,str(analytic_account.display_name), main_heading)
                        col+=6
                        for total in rule_dict.values():
                            sheet.write_string(row, col,str(total), main_heading)
                            col+=1
                        row+=1
                        col=0
                row+=1
                result_dict = self._get_payslips(emp_payslip)
                result = dict(functools.reduce(operator.add,
                                               map(collections.Counter, list_dict)))
                result_dict.update(result)
                sheet.write_string(row, col,'Total', main_heading2)
                col+=6
                for total in result_dict.values():
                    sheet.write_string(row, col,str(total), main_heading2)
                    col+=1
            row += 2
            col = 0

    def _get_payslips(self, payslip_id):
        rule_dict = OrderedDict.fromkeys(
            (rule.name + '+' + rule.code for payslip in payslip_id for rule in payslip.line_ids), 0.0)
        filter_dict_list = []
        for key in list(rule_dict.keys()):
            split_key = key.split('+')
            if split_key[1] in filter_dict_list:
                del rule_dict[key]
            else:
                filter_dict_list.append(split_key[1])
        for key in rule_dict.keys():
            split_key = key.split('+')
            if split_key[1] == 'NET':
                rule_dict.move_to_end(key)
                break
        return rule_dict






















































