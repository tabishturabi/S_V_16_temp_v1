from odoo import models
from datetime import date, datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import pandas as pd
import json
from num2words import num2words


class AccountMoveReportExcel(models.AbstractModel):
    _name = 'report.bsg_account_move_report.am_report_xlsx'
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
            "bg_color": '#999999',
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
        sheet = workbook.add_worksheet('Account Move Report')
        sheet.freeze_panes(6,0)
        sheet.set_column('A:Z',15)
        row = 0
        col = 0
        account_move_line_ids = self.env['account.move.line'].search([('date','>=',docs.date_from),('date','<=',docs.date_to),('account_id','in',docs.account_ids.ids)])
        if account_move_line_ids:
            self.env.ref('bsg_account_move_report.account_move_report_xlsx_id').report_file = "Account Move Report"
            sheet.merge_range('A1:M1', 'تقرير كشف الحساب', main_heading3)
            sheet.merge_range('A2:M2', 'Account Move Report', main_heading3)
            sheet.merge_range('A3:C3', 'Accounts', main_heading2)
            vals_list = docs.account_ids.mapped('name')
            vals = ",".join(vals_list)
            sheet.merge_range('E3:G3', str(vals), main_heading2)
            sheet.merge_range('A4:B4', 'Date From', main_heading2)
            sheet.merge_range('C4:D4', str(docs.date_from), main_heading2)
            sheet.merge_range('E4:F4','Date To', main_heading2)
            sheet.merge_range('G4:H4',str(docs.date_to) , main_heading2)
            row += 5
            if not docs.is_partner:
                sheet.write(row, col, 'Date', main_heading2)
                sheet.write(row, col + 1, 'Move/Invoice', main_heading2)
                sheet.write(row, col + 2, 'Label', main_heading2)
                sheet.write(row, col + 3, 'Reference', main_heading2)
                sheet.write(row, col + 4, 'Partner', main_heading2)
                sheet.write(row, col + 5, 'Account', main_heading2)
                sheet.write(row, col + 6, 'Debit', main_heading2)
                sheet.write(row, col + 7, 'Credit', main_heading2)
                sheet.write(row, col + 8, 'Balance', main_heading2)
                row += 1
                total_balance=0
                for move_line_id in account_move_line_ids:
                    if move_line_id:
                        balance=move_line_id.debit - move_line_id.credit
                        total_balance += balance
                        if move_line_id.date:
                            sheet.write_string(row, col, str(move_line_id.date), main_heading)
                        if move_line_id.move_id.name:
                            sheet.write_string(row, col+1, str(move_line_id.move_id.name), main_heading)
                        if move_line_id.name:
                            sheet.write_string(row, col+2, str(move_line_id.name), main_heading)
                        if move_line_id.ref:
                            sheet.write_string(row, col+3, str(move_line_id.ref), main_heading)
                        if move_line_id.partner_id.name:
                            sheet.write_string(row, col+4, str(move_line_id.partner_id.name), main_heading)
                        if move_line_id.account_id.name:
                            sheet.write_string(row, col+5, str(move_line_id.account_id.name), main_heading)
                        if move_line_id.debit:
                            sheet.write_number(row, col + 6, move_line_id.debit, main_heading)
                        if move_line_id.credit:
                            sheet.write_number(row, col + 7, move_line_id.credit, main_heading)
                        if balance:
                            sheet.write_number(row, col + 8, total_balance, main_heading)
                        row+=1
            else:
                sheet.write(row, col, 'Date', main_heading2)
                sheet.write(row, col + 1, 'Move/Invoice', main_heading2)
                sheet.write(row, col + 2, 'Label', main_heading2)
                sheet.write(row, col + 3, 'Reference', main_heading2)
                sheet.write(row, col + 4, 'Account', main_heading2)
                sheet.write(row, col + 5, 'Debit', main_heading2)
                sheet.write(row, col + 6, 'Credit', main_heading2)
                sheet.write(row, col + 7, 'Balance', main_heading2)
                row += 1
                partner_list = []
                for move_line_id in account_move_line_ids:
                    if move_line_id.partner_id.name not in partner_list:
                        partner_list.append(move_line_id.partner_id.name)
                if partner_list:
                    total_balance=0
                    for partner in partner_list:
                        if partner:
                            sheet.write(row, col, 'Partner', main_heading2)
                            sheet.write_string(row, col + 1, str(partner), main_heading)
                            sheet.write(row, col + 2, 'الشريك', main_heading2)
                            row+=1
                            for move_line_id in account_move_line_ids:
                                if partner == move_line_id.partner_id.name:
                                    balance = move_line_id.debit - move_line_id.credit
                                    total_balance += balance
                                    if move_line_id.date:
                                        sheet.write_string(row, col, str(move_line_id.date), main_heading)
                                    if move_line_id.move_id.name:
                                        sheet.write_string(row, col + 1, str(move_line_id.move_id.name), main_heading)
                                    if move_line_id.name:
                                        sheet.write_string(row, col + 2, str(move_line_id.name), main_heading)
                                    if move_line_id.ref:
                                        sheet.write_string(row, col + 3, str(move_line_id.ref), main_heading)
                                    if move_line_id.account_id.name:
                                        sheet.write_string(row, col + 4, str(move_line_id.account_id.name),
                                                           main_heading)
                                    if move_line_id.debit:
                                        sheet.write_number(row, col + 5, move_line_id.debit, main_heading)
                                    if move_line_id.credit:
                                        sheet.write_number(row, col + 6, move_line_id.credit, main_heading)
                                    if balance:
                                        sheet.write_number(row, col + 7, total_balance, main_heading)
                                    row += 1

















