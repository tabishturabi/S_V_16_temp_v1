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
from odoo import models, fields, api
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta
from num2words import num2words


class SoaReportXlsx(models.TransientModel):
	_name = 'report.bassami_statement_of_accounts.stat_of_accounts_xlsx'
	_inherit = 'report.report_xlsx.abstract'

	# @api.multi
	def generate_xlsx_report(self, workbook,input_records,lines):
		data = input_records['form']

		form = data['form']
		to = data['to']
		entry_type = data['entry_type']
		customer_type = data['customer_type']
		account_ids = data['account_ids']
		account_type = data['account_type']
		partner_types = data['partner_types']
		partner_ids = data['partner_ids']
		with_details = data['with_details']
		for_emp = data['for_emp']
		one_page = data['one_page']
		sort_details = data['sort_details']
		branch_ids = data['branch_ids']
		partner_types_name = " "
		partner_types_ids = []
		if partner_types:
			p = partner_types[0]
			partner_ids_type = self.env['partner.type'].search([('id','=',p)])
			partner_types_name = str(partner_types_name) +' '+ str(partner_ids_type.name)
			partner_types_ids.append(partner_ids_type.id)
		branches_ids = []
		for b in branch_ids:
			branches_ids.append(b)


		new_from = datetime.strptime(data['form'], '%Y-%m-%d')
		new_to = datetime.strptime(data['to'], '%Y-%m-%d')
		new_from = datetime.date(new_from)
		new_to = datetime.date(new_to)

		details = 0

		enteries_type = " "
		if entry_type == 'all':
			enteries_type = "All Enteries"
		else:
			enteries_type = "Posted Enteries"

		if not partner_types:
			if customer_type != 'all':
				partner_ids_list = partner_ids
			if customer_type == 'all':
				if data['with_inactive_partner']:
					partner_ids_list = self.env['res.partner'].search(['|',('active', '=',True),('active', '=',False)]).ids
				else:
					partner_ids_list = self.env['res.partner'].search([('active', '=', True)]).ids

		if partner_types:
			if customer_type != 'all':
				partner_ids_list = partner_ids
			if customer_type == 'all':
				if data['with_inactive_partner']:
					partner_ids_list = self.env['res.partner'].search(['&','|',('active', '=',True),('active', '=',False),('partner_types.id','in',partner_types_ids)]).ids
				else:
					partner_ids_list = self.env['res.partner'].search([('active', '=', True),('partner_types.id', 'in', partner_types_ids)]).ids


		act_ids = []
		if account_ids and account_type == 'others':
			account_type_name = "Others"
			act_ids += list(account_ids)
			# for act in account_ids:
			# 	act_ids.append(act)
		if not account_ids and account_type == 'others':
			account_type_name = "Others"
			all_acts = self.env['account.account'].search([])
			for act in all_acts:
				act_ids.append(act.id)
		if account_type == 'receive':
			account_type_name = "Receivable"
			if not partner_types:
				all_acts = self.env['account.account'].search([('user_type_id','=','Receivable')])
				for act in all_acts:
					act_ids.append(act.id)
			else:
				all_acts = self.env['partner.type'].search([('id','in',partner_types_ids)])
				for act in all_acts:
					act_ids.append(act.accont_rec.id)
		if account_type == 'pay':
			account_type_name = "Payable"
			if not partner_types:
				all_acts = self.env['account.account'].search([('user_type_id','=','Payable')])
				for act in all_acts:
					act_ids.append(act.id)
			else:
				all_acts = self.env['partner.type'].search([('id','in',partner_types_ids)])
				for act in all_acts:
					act_ids.append(act.accont_payable.id)

		partner_ids_str = len(partner_ids_list) == 1 and "(%s)" %partner_ids_list[0] or  str(tuple(partner_ids_list))
		table_name = "account_account"
		act_ids_str = len(act_ids) == 1 and "(%s)" %act_ids[0] or  str(tuple(act_ids))
		self.env.cr.execute("select id,user_type_id,name,code,levels,parent_id FROM "+table_name+" where id in %s" %act_ids_str)
		result = self._cr.fetchall()
		all_acts_frame = pd.DataFrame(list(result))
		all_acts_frame = all_acts_frame.rename(columns={0: 'act_id',1: 'act_user_type_id',2: 'act_name',3: 'act_code',4: 'act_levels',5: 'act_parent_id'})

		move_line_table = "account_move_line"
		self.env.cr.execute("select id,account_id,date,debit,credit,move_id,partner_id,bsg_branches_id,name FROM "+move_line_table+" where account_id in %s and partner_id in %s" %(act_ids_str, partner_ids_str))
		move_line_result = self._cr.fetchall()
		period_acts = pd.DataFrame(list(move_line_result))
		open_acts = pd.DataFrame(list(move_line_result))

		period_acts = period_acts.rename(columns={0: 'line_id',1: 'move_act_id',2: 'move_date',3: 'period_debit',4: 'period_credit',5: 'move_id',6: 'partner_id',7: 'bsg_branches_id',8: 'label'})

		open_acts = open_acts.rename(columns={0: 'open_line_id',1: 'open_move_act_id',2: 'open_move_date',3: 'open_period_debit',4: 'open_period_credit',5: 'open_move_id',6: 'open_partner_id',7: 'open_bsg_branches_id'})

		if not period_acts.empty or not open_acts.empty:
			move_table = "account_move"
			self.env.cr.execute("select id,state,name FROM "+move_table+" ")
			move_result = self._cr.fetchall()
			move_frame = pd.DataFrame(list(move_result))
			move_frame = move_frame.rename(columns={0: 'form_id',1: 'move_state',2: 'move_name'})

			cust_table = "res_partner"
			self.env.cr.execute("select id,name,street,phone,city,vat,parent_id,function,ref FROM "+cust_table+" ")
			cust_result = self._cr.fetchall()
			cust_frame = pd.DataFrame(list(cust_result))
			parent_frame = pd.DataFrame(list(cust_result))

			cust_frame = cust_frame.rename(columns={0: 'cust_id',1: 'cust_name',2: 'street',3: 'phone',4: 'city',5: 'vat',6: 'cust_parent_id',7:'function',8:'ref'})
			parent_frame = parent_frame.rename(columns={0: 'parent_id',1: 'parent_name'})

			cust_frame = pd.merge(cust_frame,parent_frame,  how='left', left_on='cust_parent_id', right_on ='parent_id')

			period_acts = pd.merge(period_acts,move_frame,  how='left', left_on='move_id', right_on ='form_id')
			open_acts = pd.merge(open_acts,move_frame,  how='left', left_on='open_move_id', right_on ='form_id')

			if entry_type == 'all':
				period_acts = period_acts.loc[(period_acts['move_date'] >= new_from) & (period_acts['move_date'] <= new_to) & (period_acts['partner_id'].isin(partner_ids_list))]

				open_acts = open_acts.loc[(open_acts['open_move_date'] < new_from) & (open_acts['open_partner_id'].isin(partner_ids_list))]


			if entry_type == 'posted':
				period_acts = period_acts.loc[(period_acts['move_date'] >= new_from) & (period_acts['move_date'] <= new_to) & (period_acts['move_state'] == 'posted') & (period_acts['partner_id'].isin(partner_ids_list))]

				open_acts = open_acts.loc[(open_acts['open_move_date'] < new_from) & (open_acts['move_state'] == 'posted') & (open_acts['open_partner_id'].isin(partner_ids_list))]

			if branch_ids:
				period_acts = period_acts[period_acts['bsg_branches_id'].isin(branches_ids)]
				open_acts = open_acts[open_acts['open_bsg_branches_id'].isin(branches_ids)]

			details_period_acts = period_acts
			details_period_acts = period_acts
			details_period_acts = pd.merge(details_period_acts,all_acts_frame,  how='left', left_on='move_act_id', right_on ='act_id')

			period_acts = period_acts.groupby(['partner_id'],as_index = False).sum()
			open_acts = open_acts.groupby(['open_partner_id'],as_index = False).sum()


			if len(period_acts) >= len(open_acts):
				final_frame = pd.merge(period_acts,open_acts,  how='left', left_on='partner_id', right_on ='open_partner_id')
				final_frame = pd.merge(final_frame,cust_frame,  how='left', left_on='partner_id', right_on ='cust_id')

			if len(period_acts) < len(open_acts):
				final_frame = pd.merge(open_acts,period_acts,  how='left', left_on='open_partner_id', right_on ='partner_id')
				final_frame = pd.merge(final_frame,cust_frame,  how='left', left_on='open_partner_id', right_on ='cust_id')

			final_frame = final_frame.fillna(0)

			report_data = []
			if not with_details:

				details = 2

				for q,r in final_frame.iterrows():

					real_open_bal = r['open_period_debit'] - r['open_period_credit']
					debits = r['period_debit']
					credits = r['period_credit']
					closing_bal = (real_open_bal + debits) - credits

					if real_open_bal or debits or credits > 0:

						parent_name = " "
						if r['parent_name'] != 0:
							parent_name = r['parent_name']

						phone = " "
						if r['phone'] != 0:
							phone = r['phone']

						street = " "
						if r['street'] != 0:
							street = r['street']

						vat = " "
						if r['vat'] != 0:
							vat = r['vat']

						function = " "
						if r['function'] !=0:
							function = r['function']

						ref = " "
						if r['ref'] != 0:
							ref = r['ref']

						report_data.append({
							'name': r['cust_name'],
							'street': street,
							'phone': phone,
							'city': r['city'],
							'parent_id': parent_name,
							'function':function,
							'ref':ref,
							'vat': vat,
							'real_open_bal':real_open_bal,
							'debit': debits,
							'credit': credits,
							'closing_bal':closing_bal,
							})

			else:

				details = 1
				for q,r in final_frame.iterrows():

					enteries = []
					enteries_frame = details_period_acts.loc[(details_period_acts['partner_id'] == r['partner_id'])]
					if sort_details:
						enteries_frame = enteries_frame.sort_values(by='act_code')
					else:
						enteries_frame = enteries_frame.sort_values(by='move_date')

					for i,j in enteries_frame.iterrows():
						enteries.append({
							'date': j['move_date'],
							'debit': j['period_debit'],
							'credit': j['period_credit'],
							'label': j['label'],
							'move_name': j['move_name'],
							'act_name': j['act_name'],
							'act_code': j['act_code'],
							})

					real_open_bal = r['open_period_debit'] - r['open_period_credit']
					debits = r['period_debit']
					credits = r['period_credit']
					closing_bal = (real_open_bal + debits) - credits

					if real_open_bal or debits or credits > 0:

						parent_name = " "
						if r['parent_name'] != 0:
							parent_name = r['parent_name']

						phone = " "
						if r['phone'] != 0:
							phone = r['phone']

						street = " "
						if r['street'] != 0:
							street = r['street']

						vat = " "
						if r['vat'] != 0:
							vat = r['vat']

						function = " "
						if r['function'] !=0:
							function = r['function']

						ref = " "
						if r['ref'] != 0:
							ref = r['ref']

						report_data.append({
							'name': r['cust_name'],
							'ids': r['cust_id'],
							'street': street,
							'phone': phone,
							'city': r['city'],
							'parent_id': parent_name,
							'function':function,
							'ref':ref,
							'vat': vat,
							'enteries': enteries,
							'real_open_bal':real_open_bal,
							'debit': debits,
							'credit': credits,
							'closing_bal':closing_bal,
							})



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
				"align": 'center',
				"valign": 'vcenter',
				"font_color":'black',
				"bg_color": 'red',
				'font_size': '10',
				})

			# Create a format to use in the merged range.
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

			if details == 1:

				if not one_page:

					count = 0
					for rec in report_data:
						count = count + 1
						worksheet_name = str(rec['name'])+' '+str(count)
						worksheet = workbook.add_worksheet(str(worksheet_name))


						cust_name = str(rec['parent_id'])+' , '+str(rec['name'])

						worksheet.merge_range('A1:G1','Statement of Account    كشف حساب',merge_format)
						worksheet.write('A2','Date From', main_heading)
						worksheet.write('B2',str(form),main_data)
						worksheet.write('A3','Date To', main_heading)
						worksheet.write('B3',str(to),main_data)
						worksheet.write('D2','Partner Type', main_heading)
						worksheet.write('E2',str(partner_types_name),main_data)
						worksheet.write('D3','Account Type', main_heading)
						worksheet.write('E3',str(account_type_name),main_data)
						worksheet.write('F2','Enteries', main_heading)
						worksheet.write('G2',str(enteries_type),main_data)
						worksheet.merge_range('A5:C5','Customer Information    بيانات‬ العميل‬',main_heading)
						worksheet.write('A6','Customer Name', main_heading)
						worksheet.write('B6',str(cust_name),main_data)
						worksheet.write('C6','اسم‬ العميل‬', main_heading)
						worksheet.write('A7','Tax Account No', main_heading)
						worksheet.write('B7',str(rec['vat']),main_data)
						worksheet.write('C7','الرقم‬ الضريبي‬', main_heading)
						worksheet.write('A8','Address', main_heading)
						worksheet.write('B8',str(rec['street']),main_data)
						worksheet.write('C8','‫‪العنوان‬', main_heading)
						worksheet.write('A9','Telephone No', main_heading)
						worksheet.write('B9',str(rec['phone']),main_data)
						worksheet.write('C9','رقم‬ الھاتف‬', main_heading)
						if for_emp:
							worksheet.write('A10','Emp Code', main_heading)
							worksheet.write('B10',str(rec['ref']),main_data)
							worksheet.write('C10','رقم المـوظف‬', main_heading)
							worksheet.write('A11','Job Position', main_heading)
							worksheet.write('B11',str(rec['function']),main_data)
							worksheet.write('C11','المهنـة', main_heading)


						worksheet.merge_range('E5:G5','Company Information    بيانات‬ الشركه‬',main_heading)
						worksheet.write('E6','Company Name', main_heading)
						worksheet.write('F6','مجموعة أعمال البسامي الدولية',main_data)
						worksheet.write('G6','اسم‬ الشركه‬', main_heading)
						worksheet.write('E7','Tax Account No', main_heading)
						worksheet.write('F7','‫‪300043273800003‬‬',main_data)
						worksheet.write('G7','الرقم‬ الضريبي‬', main_heading)
						worksheet.write('E8','Address', main_heading)
						worksheet.write('F8','Between Exit 10 and Exit 11, Al Bassami Building,Al Quds,Riyadh',main_data)
						worksheet.write('G8','‫‪العنوان‬', main_heading)
						worksheet.write('E9','Telephone No', main_heading)
						worksheet.write('F9','‫‪920005353‬‬',main_data)
						worksheet.write('G9','رقم‬ الھاتف‬', main_heading)

						worksheet.set_column('A:A', 15)
						worksheet.set_column('B:B', 40)
						worksheet.set_column('C:C', 15)
						worksheet.set_column('D:D', 18)
						worksheet.set_column('E:E', 15)
						worksheet.set_column('F:F', 40)
						worksheet.set_column('G:G', 15)


						if for_emp:
							worksheet.write('A13', 'Date', main_heading1)
							worksheet.write('B13', 'Description', main_heading1)
							worksheet.write('C13', 'Entry No', main_heading1)
							worksheet.write('D13', 'Account Name', main_heading1)
							worksheet.write('E13', 'Debit', main_heading1)
							worksheet.write('F13', 'Credit', main_heading1)
							worksheet.write('G13', 'Balance', main_heading1)
							worksheet.merge_range('A14:G14',str('Opening Balance'+' : '+ str("{0:.2f}".format(rec['real_open_bal']))),main_heading)
							row = 14
						else:
							worksheet.write('A11', 'Date', main_heading1)
							worksheet.write('B11', 'Description', main_heading1)
							worksheet.write('C11', 'Entry No', main_heading1)
							worksheet.write('D11', 'Account Name', main_heading1)
							worksheet.write('E11', 'Debit', main_heading1)
							worksheet.write('F11', 'Credit', main_heading1)
							worksheet.write('G11', 'Balance', main_heading1)

						worksheet.merge_range('A12:G12',str('Opening Balance'+' : '+ str("{0:.2f}".format(rec['real_open_bal']))),main_heading)

						row = 12
						col = 0

						deb = 0
						cre = 0
						open_bal = rec['real_open_bal']
						bal = open_bal

						for  line in rec['enteries']:

							bal = (bal + line['debit']) - line['credit']

							worksheet.write_string (row, col,str(line['date']),main_data)
							worksheet.write_string (row, col+1,str(line['label']),main_data)
							worksheet.write_string (row, col+2,str(line['move_name']),main_data)
							account_name = str(line['act_name']) +'   '+ str(line['act_code'])
							worksheet.write_string (row, col+3,str(account_name),main_data)
							worksheet.write_string (row, col+4,str("{0:.2f}".format(line['debit'])),main_data)
							worksheet.write_string (row, col+5,str("{0:.2f}".format(line['credit'])),main_data)
							worksheet.write_string (row, col+6,str("{0:.2f}".format(bal)),main_data)

							deb = deb + line['debit']
							cre = cre + line['credit']

							row += 1


						loc = 'A'+str(row+1)
						loc1 = 'G'+str(row+1)
						close_bal = str(loc)+':'+str(loc1)
						worksheet.merge_range(str(close_bal),str('Closing Balance'+' : '+ str("{0:.2f}".format(bal))),main_heading)

						loc_1 = 'A'+str(row+2)
						loc_2 = 'D'+str(row+2)
						loc_3 = 'E'+str(row+2)
						loc_4 = 'F'+str(row+2)
						loc_5 = 'G'+str(row+2)

						end_1 = str(loc_1)+':'+str(loc_2)


						worksheet.merge_range(str(end_1), 'Total' ,main_heading)
						worksheet.write(str(loc_3), str(deb) ,main_heading)
						worksheet.write(str(loc_4), str(cre),main_heading)
						worksheet.write(str(loc_5), str(bal) ,main_heading)

				if one_page:

					worksheet = workbook.add_worksheet("Statement of Accounts")

					worksheet.merge_range('A1:E1','Statement of Account    كشف حساب',merge_format)
					worksheet.write('A2','Date From', main_heading)
					worksheet.write('B2',str(form),main_data)
					worksheet.write('A3','Date To', main_heading)
					worksheet.write('B3',str(to),main_data)
					worksheet.write('D2','Partner Type', main_heading)
					worksheet.write('E2',str(partner_types_name),main_data)
					worksheet.write('D3','Account Type', main_heading)
					worksheet.write('E3',str(account_type_name),main_data)
					worksheet.write('A4','Enteries', main_heading)
					worksheet.write('B4',str(enteries_type),main_data)



					worksheet.set_column('A:A', 15)
					worksheet.set_column('B:B', 40)
					worksheet.set_column('C:C', 15)
					worksheet.set_column('D:D', 18)
					worksheet.set_column('E:E', 15)
					worksheet.set_column('F:F', 15)
					worksheet.set_column('G:G', 15)


					worksheet.write('A6', 'Date', main_heading1)
					worksheet.write('B6', 'Description', main_heading1)
					worksheet.write('C6', 'Entry No', main_heading1)
					worksheet.write('D6', 'Account Name', main_heading1)
					worksheet.write('E6', 'Debit', main_heading1)
					worksheet.write('F6', 'Credit', main_heading1)
					worksheet.write('G6', 'Balance', main_heading1)


					row = 6
					col = 0

					real_open_bal_tot = 0
					debits_tot = 0
					credits_tot = 0
					closing_bal_tot = 0
					for rec in report_data:

						cust_name = str(rec['parent_id'])+' , '+str(rec['name'])

						worksheet.write_string (row, col,str("Partner Name"),main_heading1)
						worksheet.write_string (row, col+1,str(cust_name),main_data)
						worksheet.write_string (row, col+2,str(
							'Opening Balance'),main_heading1)

						worksheet.write_string (row, col+3,str("{0:.2f}".format(rec['real_open_bal'])),main_data)

						row = row + 1
						if for_emp:
							worksheet.write_string (row, col,str("Emp Code"),main_heading1)
							worksheet.write_string (row, col+1,str(rec['ref']),main_data)
							worksheet.write_string (row, col+2,str('Job Position'),main_heading1)
							worksheet.write_string (row, col+3,str(rec['function']),main_data)
							row = row + 1
						col = 0

						deb = 0
						cre = 0
						open_bal = rec['real_open_bal']
						bal = open_bal

						for  line in rec['enteries']:

							bal = (bal + line['debit']) - line['credit']

							worksheet.write_string (row, col,str(line['date']),main_data)
							worksheet.write_string (row, col+1,str(line['label']),main_data)
							worksheet.write_string (row, col+2,str(line['move_name']),main_data)
							account_name = str(line['act_name']) +'   '+ str(line['act_code'])
							worksheet.write_string (row, col+3,str(account_name),main_data)
							worksheet.write_string (row, col+4,str("{0:.2f}".format(line['debit'])),main_data)
							worksheet.write_string (row, col+5,str("{0:.2f}".format(line['credit'])),main_data)
							worksheet.write_string (row, col+6,str("{0:.2f}".format(bal)),main_data)

							deb = deb + line['debit']
							cre = cre + line['credit']

							row += 1

						loc = 'A'+str(row+1)
						loc1 = 'G'+str(row+1)
						close_bal = str(loc)+':'+str(loc1)
						worksheet.merge_range(str(close_bal),str('Closing Balance'+' : '+ str("{0:.2f}".format(bal))),main_heading)

						loc_1 = 'A'+str(row+2)
						loc_2 = 'D'+str(row+2)
						loc_3 = 'E'+str(row+2)
						loc_4 = 'F'+str(row+2)
						loc_5 = 'G'+str(row+2)

						end_1 = str(loc_1)+':'+str(loc_2)


						worksheet.merge_range(str(end_1), 'Total' ,main_heading)
						worksheet.write(str(loc_3), str(deb) ,main_heading)
						worksheet.write(str(loc_4), str(cre),main_heading)
						worksheet.write(str(loc_5), str(bal) ,main_heading)

						row += 3




			if details == 2:

				worksheet = workbook.add_worksheet("Statement of Accounts")

				worksheet.merge_range('A1:E1','Statement of Account    كشف حساب',merge_format)
				worksheet.write('A2','Date From', main_heading)
				worksheet.write('B2',str(form),main_data)
				worksheet.write('A3','Date To', main_heading)
				worksheet.write('B3',str(to),main_data)
				worksheet.write('D2','Partner Type', main_heading)
				worksheet.write('E2',str(partner_types_name),main_data)
				worksheet.write('D3','Account Type', main_heading)
				worksheet.write('E3',str(account_type_name),main_data)
				worksheet.write('A4','Enteries', main_heading)
				worksheet.write('B4',str(enteries_type),main_data)



				worksheet.set_column('A:A', 25)
				worksheet.set_column('B:E', 18)

				if for_emp:
					worksheet.write('A6', 'Partner Name', main_heading1)
					worksheet.write('B6', 'Emp Code', main_heading1)
					worksheet.write('C6', 'Job Position', main_heading1)
					worksheet.write('D6', 'Opening Balance', main_heading1)
					worksheet.write('E6', 'Debit', main_heading1)
					worksheet.write('F6', 'Credit', main_heading1)
					worksheet.write('G6', 'Balance', main_heading1)
				else:
					worksheet.write('A6', 'Partner Name', main_heading1)
					worksheet.write('B6', 'Opening Balance', main_heading1)
					worksheet.write('C6', 'Debit', main_heading1)
					worksheet.write('D6', 'Credit', main_heading1)
					worksheet.write('E6', 'Balance', main_heading1)

				row = 6
				col = 0

				real_open_bal_tot = 0
				debits_tot = 0
				credits_tot = 0
				closing_bal_tot = 0
				for rec in report_data:
					real_open_bal_tot = real_open_bal_tot + rec['real_open_bal']
					debits_tot = debits_tot + rec['debit']
					credits_tot = credits_tot + rec['credit']
					closing_bal_tot = closing_bal_tot + rec['closing_bal']

					cust_name = str(rec['parent_id'])+' , '+str(rec['name'])

					worksheet.write_string (row, col,str(cust_name),main_data)
					if for_emp:
						worksheet.write_string (row, col+1,str(rec['ref']),main_data)
						worksheet.write_string (row, col+2,str(rec['function']),main_data)
						worksheet.write_string (row, col+3,str("{0:.2f}".format(rec['real_open_bal'])),main_data)
						worksheet.write_string (row, col+4,str("{0:.2f}".format(rec['debit'])),main_data)
						worksheet.write_string (row, col+5,str("{0:.2f}".format(rec['credit'])),main_data)
						worksheet.write_string (row, col+6,str("{0:.2f}".format(rec['closing_bal'])),main_data)
					else:
						worksheet.write_string (row, col+1,str("{0:.2f}".format(rec['real_open_bal'])),main_data)
						worksheet.write_string (row, col+2,str("{0:.2f}".format(rec['debit'])),main_data)
						worksheet.write_string (row, col+3,str("{0:.2f}".format(rec['credit'])),main_data)
						worksheet.write_string (row, col+4,str("{0:.2f}".format(rec['closing_bal'])),main_data)

					row += 1

				if for_emp:
					loc_1 = 'A'+str(row+1)
					loc_2 = 'D'+str(row+1)
					loc_3 = 'E'+str(row+1)
					loc_4 = 'F'+str(row+1)
					loc_5 = 'G'+str(row+1)
				else:
					loc_1 = 'A'+str(row+1)
					loc_2 = 'B'+str(row+1)
					loc_3 = 'C'+str(row+1)
					loc_4 = 'D'+str(row+1)
					loc_5 = 'E'+str(row+1)



				worksheet.write(str(loc_1), 'Total' ,main_heading)
				worksheet.write(str(loc_2), str(real_open_bal_tot),main_heading)
				worksheet.write(str(loc_3), str(debits_tot) ,main_heading)
				worksheet.write(str(loc_4), str(credits_tot),main_heading)
				worksheet.write(str(loc_5), str(closing_bal_tot) ,main_heading)


		else:
			worksheet = workbook.add_worksheet("Statement of Accounts")
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
				"align": 'center',
				"valign": 'vcenter',
				"font_color":'black',
				"bg_color": 'red',
				'font_size': '10',
				})

			# Create a format to use in the merged range.
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
			partner_ids = self.env['res.partner'].sudo().browse(partner_ids)
			for partner in partner_ids:
				cust_name = str(partner.name)
				worksheet.merge_range('A1:G1','Statement of Account    كشف حساب',merge_format)
				worksheet.write('A2','Date From', main_heading)
				worksheet.write('B2',str(form),main_data)
				worksheet.write('A3','Date To', main_heading)
				worksheet.write('B3',str(to),main_data)
				worksheet.write('D2','Partner Type', main_heading)
				worksheet.write('E2',str(partner.partner_types.name),main_data)
				worksheet.write('D3','Account Type', main_heading)
				worksheet.write('E3',str(account_type_name),main_data)
				worksheet.write('F2','Enteries', main_heading)
				worksheet.write('G2',str(entry_type),main_data)
				worksheet.merge_range('A5:C5','Customer Information    بيانات‬ العميل‬',main_heading)
				worksheet.write('A6','Customer Name', main_heading)
				worksheet.write('B6',str(cust_name),main_data)
				worksheet.write('C6','اسم‬ العميل‬', main_heading)
				if not for_emp:
					worksheet.write('A7','Tax Account No', main_heading)
					worksheet.write('B7',str(partner.vat),main_data)
					worksheet.write('C7','الرقم‬ الضريبي‬', main_heading)
					worksheet.write('A8','Address', main_heading)
					worksheet.write('B8',str(partner.street),main_data)
					worksheet.write('C8','‫‪العنوان‬', main_heading)
					worksheet.write('A9','Telephone No', main_heading)
					worksheet.write('B9',str(partner.phone),main_data)
					worksheet.write('C9','رقم‬ الھاتف‬', main_heading)
				if for_emp:
					worksheet.write('A7','Emp Code', main_heading)
					worksheet.write('B7',str(partner.ref),main_data)
					worksheet.write('C7','رقم المـوظف‬', main_heading)
					worksheet.write('A8','Job Position', main_heading)
					worksheet.write('B8',str(partner.function),main_data)
					worksheet.write('C8','المهنـة', main_heading)


				worksheet.merge_range('E5:G5','Company Information    بيانات‬ الشركه‬',main_heading)
				worksheet.write('E6','Company Name', main_heading)
				worksheet.write('F6','مجموعة أعمال البسامي الدولية',main_data)
				worksheet.write('G6','اسم‬ الشركه‬', main_heading)
				worksheet.write('E7','Tax Account No', main_heading)
				worksheet.write('F7','‫‪300043273800003‬‬',main_data)
				worksheet.write('G7','الرقم‬ الضريبي‬', main_heading)
				worksheet.write('E8','Address', main_heading)
				worksheet.write('F8','Between Exit 10 and Exit 11, Al Bassami Building,Al Quds,Riyadh',main_data)
				worksheet.write('G8','‫‪العنوان‬', main_heading)
				worksheet.write('E9','Telephone No', main_heading)
				worksheet.write('F9','‫‪920005353‬‬',main_data)
				worksheet.write('G9','رقم‬ الھاتف‬', main_heading)
				worksheet.merge_range('A11:G11','No Matching Record    لا توجد  سجلات  مطابقة',merge_format)
			
				worksheet.set_column('A:A', 15)
				worksheet.set_column('B:B', 40)
				worksheet.set_column('C:C', 15)
				worksheet.set_column('D:D', 18)
				worksheet.set_column('E:E', 15)
				worksheet.set_column('F:F', 40)
				worksheet.set_column('G:G', 15)


		
