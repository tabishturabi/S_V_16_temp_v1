# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class EmployeePayslipReportWizard(models.TransientModel):
    _name = 'employee.payslip.report.wizard'

    MONTH_SEL = [('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'), ('05', 'May'), ('06', 'June'),
                 ('07', 'July'), ('08', 'August'), ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')]

    employee_id = fields.Many2many('hr.employee',string='Employee Name')
    from_month = fields.Selection(MONTH_SEL, string="From Month", required=True, default="01")
    end_month = fields.Selection(MONTH_SEL, string="End Month", required=True, default="01")
    from_year = fields.Many2one('account.fiscal.year', string="From Year", required=True)
    end_year = fields.Many2one('account.fiscal.year', string="End Year", required=True)

    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    print_date = fields.Date(string='Today Date', default=fields.date.today())

    @api.onchange("from_month", "from_year")
    def onchange_from_params(self):
        month = self.from_month
        year = self.from_year
        if month and year:
            self.from_date = fields.Date.from_string(str(year.name) + '-' + str(month + '-' + '01'))

    @api.onchange("end_month", "end_year")
    def onchange_to_params(self):
        month = self.end_month
        year = self.end_year
        if month and year:
            self.to_date = fields.Date.from_string(str(year.name) + '-' + str(month + '-' + '30'))

    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'employee_id': self.employee_id,
                'from_date': self.from_date,
                'to_date': self.to_date
            }
        }
        return self.env.ref('bsg_employee_payslip_report.employee_payslip_report_xlsx_id').report_action(self,data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_employee_payslip_report.employee_payslip_report_pdf_id').report_action(self,data=data)

    # @api.multi
    def get_list(self, payslip_line, total):
        if not len(total):
            for line in payslip_line:
                total.append(line.total)
        else:
            index = 0
            for line in payslip_line:
                total[index] += line.total
                index += 1
        return total

    # @api.multi
    def get_payslip(self, employee_id):
        payslip_id = self.env['hr.payslip'].search(
            [('employee_id', '=', employee_id), ('date_from','<=',self.to_date),
             ('date_to', '>', self.from_date)], order="date_from asc")
        return payslip_id

    def get_report_rules(self):
        return ["BASIC", "CA", "CASO", "HRA3", "HRA2", "FA", "NWA", "ADD1", "ADD2", "GOSI", "DED1", "LOAN", "DED2", "NET"]

    def get_rule_dict(self, emp_payslips):
        keys = self.get_report_rules()
        payslip_rules = emp_payslips.mapped("line_ids.salary_rule_id.code")
        duplicate_rules = ["CA", "CASO", "HRA3", "HRA2"]
        for rule in duplicate_rules:
            if rule not in payslip_rules:  keys.pop(keys.index(rule))
        rule_dict = OrderedDict.fromkeys(keys, {'name': '', 'amount': 0})
        for key, value in rule_dict.items():
            if key == "BASIC": rule_dict.update({key:  {'name': 'الراتب الأساسي', 'amount': 0, 'value': "rule"}})
            if key in ["CA", "CASO"]: rule_dict.update({key:  {'name': 'بدل نقل', 'amount': 0, 'value': "rule"}})
            if key in ["HRA3", "HRA2"]: rule_dict.update({key:  {'name': 'بدل السكن ', 'amount': 0, 'value': "rule"}})
            if key == "FA": rule_dict.update({key:  {'name': 'بدل طعام', 'amount': 0, 'value': "rule"}})
            if key == "NWA": rule_dict.update({key:  {'name': 'بدل طبيعية عمل', 'amount': 0, 'value': "rule"}})
            if key == "ADD1": rule_dict.update({key:  {'name': 'الاضافيات ', 'amount': 0, 'value': "ADD"}})
            if key == "ADD2": rule_dict.update({key:  {'name': 'اجمالي المستحق ', 'amount': 0, 'value': "ADD"}})
            if key == "GOSI": rule_dict.update({key:  {'name': 'التامينات الاجتماعيه  ', 'amount': 0, 'value': "rule"}})
            if key == "DED1": rule_dict.update({key:  {'name': 'الخصومات ', 'amount': 0, 'value': "ADD"}})
            if key == "LOAN": rule_dict.update({key:  {'name': 'خصم السلف ', 'amount': 0, 'value': "rule"}})
            if key == "DED2": rule_dict.update({key:  {'name': 'اجمالي الخصومات ', 'amount': 0, 'value': "ADD"}})
            if key == "NET": rule_dict.update({key:  {'name': 'صافي الراتب ', 'amount': 0, 'value': "rule"}})

        return rule_dict

    def calculate_amount(self, key, payslip):
        if key == "ADD1":
            codes_list = ["FAA", "ADDHRS", "ADDMHRS", "ADDDAYS","ADDVAR"]
        if key == "ADD2":
            codes_list = ["FAA", "ADDHRS", "ADDMHRS", "ADDDAYS","ADDVAR", "BASIC", "CA", "CASO", "HRA3", "HRA2", "FA", "NWA"]
        if key == "DED1":
            codes_list = ["late", "unjustified", "LATEHRS", "DEDDAYS", "DEDP", "DEDINC", "DEDABS", "DEDWDAYS", "DEDVAR", "DEDFIXD"]
        if key == "DED2":
            codes_list = ["late", "unjustified", "LATEHRS", "DEDDAYS", "DEDP", "DEDINC", "DEDABS", "DEDWDAYS", "DEDVAR",
                          "DEDFIXD", "LOAN", "GOSI"]
        lines = payslip.line_ids.filtered(lambda x: x.code in codes_list)
        return sum(lines.mapped("total"))

    def update_rule_dict(self, payslip, emp_payslips):
        rule_dict = self.get_rule_dict(emp_payslips)
        payslip_lines = payslip.line_ids
        for key, value in rule_dict.items():
            if value["value"] == "rule":
                matching_payslip_line = payslip_lines.filtered(lambda x: x.code == key)
                rule_dict.update({key: {'amount': abs(matching_payslip_line.total)}})
            if value["value"] == "ADD":
                amount = self.calculate_amount(key, payslip)
                rule_dict.update({key: {'amount': amount}})

        return rule_dict

    def get_dict_list(self,payslip, emp_paylips, dict_list):
        rule_dict = self.update_rule_dict(payslip, emp_paylips)
        dict_list.append(rule_dict)
        return dict_list

    def _get_total(self, dict_list, emp_payslips):
        result_dict = self.get_rule_dict(emp_payslips)
        if dict_list:
            for key, value in result_dict.items():
                rule_total = 0
                for payslip in dict_list:
                    rule_total += payslip.get(key)["amount"]
                result_dict.update(({key: {'amount': round(rule_total)}}))

        #     result = dict(functools.reduce(operator.add,
        #                                    map(collections.Counter, dict_list[0])))
        #     print("result 111111111111", result)
        #     result_dict.update(result)
        #     print("get_rule_dict after update :", result_dict)

            return result_dict
        else:
            return result_dict










