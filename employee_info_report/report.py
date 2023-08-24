import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
import re
import pandas as pd
import numpy as np
import psycopg2 as pg
import pandas.io.sql as psql
import getpass
from odoo import models, fields, api, _
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta
import string


class TrialBalanceReportXlsx(models.TransientModel):
	_name = 'report.employee_info_report.employee_info_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'

	# @api.multi
	def generate_xlsx_report(self, workbook, input_records, lines):
		data = input_records['form']

		employee_ids = self.env['hr.employee'].search([])

		if data['mode'] == 'specific':
			employee_ids = employee_ids.filtered(lambda l: l.id in data['employee_ids'])

		if data['mode'] == 'branch':
			employee_ids = employee_ids.filtered(lambda l: l.branch_id.id in data['branch_ids'])

		if data['mode'] == 'dept':
			employee_ids = employee_ids.filtered(lambda l: l.department_id.id in data['dept_ids'])

		if data['mode'] == 'company':
			employee_ids = employee_ids.filtered(lambda l: l.company_id.id in data['company_ids'])

		if data['mode'] == 'emp_tag':
			employee_ids = employee_ids.filtered(lambda l: l.category_ids and l.category_ids[0].id in data['tag_ids'])

		if data['salary_payment_method']:
			employee_ids = employee_ids.filtered(lambda l: l.salary_payment_method == data['salary_payment_method'])

		if data['employee_state']:
			employee_ids = employee_ids.filtered(lambda l: l.employee_state == data['employee_state'])

		table_name = "hr_salary_rule"
		self.env.cr.execute("select id,sequence FROM "+table_name+" ")
		result = self._cr.fetchall()
		rule_frame = pd.DataFrame(list(result))
		rule_frame = rule_frame.rename(columns={0: 'rule_id',1: 'sequence'})

		table_name = "hr_payslip"
		self.env.cr.execute("select id,employee_id FROM "+table_name+" ")
		pay_result = self._cr.fetchall()
		pay_frame = pd.DataFrame(list(pay_result))
		pay_frame = pay_frame.rename(columns={0: 'pay_id',1: 'employee_id'})

		table_name = "hr_payslip_line"
		self.env.cr.execute("select id,salary_rule_id,slip_id,total FROM "+table_name+" ")
		payline_result = self._cr.fetchall()
		payline_frame = pd.DataFrame(list(payline_result))
		payline_frame = payline_frame.rename(columns={0: 'line_id',1: 'salary_rule_id',2: 'slip_id',3: 'total'})


	
			
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
			'font_size': '10',
			})

		main_heading2 = workbook.add_format({
			"bold": 1, 
			"border": 1,
			"align": 'right',
			"valign": 'vcenter',
			"font_color":'black',
			"bg_color": '#D3D3D3',
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
			'font_size': '8',
			})
		merge_format.set_shrink()
		main_heading.set_text_justlast(1)
		main_data.set_border()
		worksheet = workbook.add_worksheet('Employee Information Report')

		rule_ids = self.env['hr.salary.rule'].search([('input_ids','=',False)], order='sequence')
		rule_ids_check = self.env['hr.salary.rule'].search([('input_ids','=',False)], order='sequence').ids

		rule_frame = rule_frame.loc[(rule_frame['rule_id'].isin(rule_ids_check))]
		rule_frame = rule_frame.sort_values(by=['sequence','rule_id'])

		letters = list(string.ascii_uppercase)

		worksheet.merge_range('A1:H1',"Employee Information Report",merge_format)

		worksheet.write('A3', 'كود', main_heading1)
		worksheet.write('B3', 'اسم الموظف', main_heading1)
		worksheet.write('C3',  'English Name', main_heading1)
		worksheet.write('D3',  'الوظيفه', main_heading1)
		worksheet.write('E3',  'الادارة', main_heading1)
		worksheet.write('F3',  'الفرع', main_heading1)
		worksheet.write('G3',  'حالة الموظف', main_heading1)
		worksheet.write('H3',  'تعليق الراتب', main_heading1)
		worksheet.write('I3',  'تاريخ اخر عوده', main_heading1)
		worksheet.write('J3',  'رقم الجوال', main_heading1)
		worksheet.write('K3',  'الجنسية', main_heading1)
		worksheet.write('L3',  'رقم الهوية', main_heading1)
		worksheet.write('M3',  'رقم الحساب البنكي', main_heading1)
		worksheet.write('N3',  'سوفت البنك', main_heading1)
		worksheet.write('O3',  'طريقة صرف الراتب', main_heading1)
		worksheet.write('P3',  'الوسم', main_heading1)
		worksheet.write('Q3',  'تاريخ التعيين', main_heading1)
		worksheet.write('R3',  'مسير الرواتب', main_heading1)
		i =18
		for rule in rule_ids:
			if i < 52:
				letter = i > 25 and 'A' + letters[i - 26] or letters[i]
				worksheet.write(letter + '3', rule.name, main_heading1)
			else:
				letter = i > 51 and 'B' + letters[i - 52]
				worksheet.write(letter + '3', rule.name, main_heading1)
			i += 1

		row = 3
		col = 0
		main_totals = []
		for rec in employee_ids:
			col = 0

			bsg_national_id = rec.bsg_national_id
			iqama = rec.bsg_empiqama
			driver_code = rec.driver_code or ""
			emp_name = rec.name or ""
			eng_name = rec.name_english or ""
			suspend_salary = rec.suspend_salary or ""
			last_return_date = rec.last_return_date or ""
			mobile_phone = rec.mobile_phone or ""
			job = rec.job_id.name or ""
			department = rec.department_id.display_name or ""
			branch = rec.branch_id and rec.branch_id.branch_ar_name or ""
			employee_state = rec.employee_state 
			joining_date =  rec.contract_id.date_start and rec.contract_id.date_start.strftime("%m/%d/%Y") or ""
			struct_id =  rec.contract_id.struct_id.name or ""
			country = rec and rec.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).country_id.name or ""
			id_iqama = (rec.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).country_id.code == 'SA' and  bsg_national_id and bsg_national_id.bsg_nationality_name or "") or  (iqama and iqama.bsg_iqama_name or "") 
			back_account = rec.bsg_bank_id and rec.bsg_bank_id.bsg_acc_number or  ""
			swift_code = rec.bsg_bank_id and rec.bsg_bank_id.bsg_bank_name or ""
			salary_payment_method = rec.salary_payment_method and dict(rec._fields['salary_payment_method'].selection)[rec.salary_payment_method] or ""
			tags = rec.category_ids and ", ".join(rec.category_ids.mapped('name')) or ""

			worksheet.write_string (row, col,driver_code)
			worksheet.write_string (row, col+1,emp_name,main_data)
			worksheet.write_string (row, col+2,eng_name,main_data)
			worksheet.write_string (row, col+3,str(job),main_data)
			worksheet.write_string (row, col+4,department,main_data)
			worksheet.write_string (row, col+5,str(branch),main_data)
			worksheet.write_string (row, col+6, _(employee_state),main_data)
			worksheet.write_string (row, col+7,str(suspend_salary),main_data)
			worksheet.write_string (row, col+8,str(last_return_date),main_data)
			worksheet.write_string (row, col+9,str(mobile_phone),main_data)
			worksheet.write_string (row, col+10,_(country),main_data)
			worksheet.write_string (row, col+11,_(id_iqama),main_data)
			worksheet.write_string (row, col+12,str(back_account),main_data)
			worksheet.write_string (row, col+13,str(swift_code),main_data)
			worksheet.write_string (row, col+14,_(salary_payment_method),main_data)
			worksheet.write_string (row, col+15,str(tags),main_data)
			worksheet.write_string (row, col+16,joining_date,main_data)
			worksheet.write_string (row, col+17,str(struct_id),main_data)
			col=18
			emp_pay_frame = pay_frame.loc[(pay_frame['employee_id'] == rec.id)]
			if len(emp_pay_frame) > 0:
				emp_pay_frame = emp_pay_frame.sort_values(by=['pay_id'])
				emp_pay_frame = emp_pay_frame.drop_duplicates(subset='employee_id', keep="last")
				for i,j in emp_pay_frame.iterrows():
					rule_tot = []
					for index,line in rule_frame.iterrows():
						local_payline = payline_frame.loc[(payline_frame['salary_rule_id'] == line['rule_id']) & (payline_frame['slip_id'] == j['pay_id'])]
						if len(local_payline) > 0:
							for l,m in local_payline.iterrows():
								amount = m['total']
								amount = abs(amount)
								worksheet.write_number (row, col, amount)
								rule_tot.append(amount)
								col+=1
						else:
							amount = 0
							rule_tot.append(amount)
							worksheet.write_number (row, col, amount)
							col+=1

			else:
				rule_tot = []
				for index,line in rule_frame.iterrows():
					amount = 0
					rule_tot.append(amount)
					worksheet.write_number (row, col, amount)
					col+=1

			main_totals.append(rule_tot)

			row+=1

		grand_total_summing = [sum(x) for x in zip(*main_totals)]

		col=18
		row+=1
		for total in grand_total_summing:
			worksheet.write_number (row, col, total, main_heading2)
			col+=1

		

				
			

	
