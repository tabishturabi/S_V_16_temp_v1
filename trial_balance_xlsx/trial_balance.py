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


class TrialBalanceReportXlsx(models.TransientModel):
	_name = 'report.trial_balance_xlsx.report_trial_balance_xlsx'
	_inherit = 'report.report_xlsx.abstract'

	#@api.multi
	def generate_xlsx_report(self, workbook, input_records, lines):
		data = input_records['form']
		# recs = input_records['records_dict']

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
		worksheet = workbook.add_worksheet('Trial Balance')


		analytic_account_names = " "
		if data['analytic_account_ids']:
			for analytic in data['analytic_account_ids']:
				analytic_act = self.env['account.analytic.account'].search([('id','=',analytic)],limit=1)
				if analytic_account_names != " ":
					analytic_account_names = analytic_account_names +' , '+ str(analytic_act.name)
				else:
					analytic_account_names = str(analytic_act.name)

		worksheet.merge_range('A1:I1','Trial Balance',merge_format)
		worksheet.set_column('A:A', 15)
		worksheet.set_column('B:B', 23)
		worksheet.set_column('C:C', 15)
		worksheet.set_column('D:K', 15)
		worksheet.write('A2', 'Date From', main_heading)
		worksheet.write('B2', str(data['date_from']), main_data)
		worksheet.write('C2', 'Date To', main_heading)
		worksheet.write('D2', str(data['date_to']), main_data)
		worksheet.write('F2', 'Target Moves', main_heading)
		worksheet.write('G2', str(data['target_moves']), main_data)
		worksheet.write('H2', 'Level', main_heading)
		worksheet.write('I2', str(data['levels']), main_data)
		if data['analytic_account_ids']:
			worksheet.write('A3', 'Analytic Accounts', main_heading)
			worksheet.write('B3', str(analytic_account_names), main_data)

		worksheet.merge_range('D5:E5','Initial Balance',main_heading)
		worksheet.merge_range('F5:G5','Transaction Balance',main_heading)
		worksheet.merge_range('H5:I5','Closing Balance',main_heading)
		worksheet.merge_range('J5:K5','Balance',main_heading)


		worksheet.write('A6', 'Code', main_heading1)
		worksheet.write('B6', 'Name', main_heading1)
		worksheet.write('C6', 'Type', main_heading1)
		worksheet.write('D6', 'Opening Debit', main_heading1)
		worksheet.write('E6', 'Opening Credit', main_heading1)
		worksheet.write('F6', 'Transaction Debit', main_heading1)
		worksheet.write('G6', 'Transaction Credit', main_heading1)
		worksheet.write('H6', 'Closing Debit', main_heading1)
		worksheet.write('I6', 'Closing Credit', main_heading1)
		worksheet.write('J6', 'Debit Balance', main_heading1)
		worksheet.write('K6', 'Credit Balance', main_heading1)


		records = []
		table_name = "account_account"
		self.env.cr.execute("select id,user_type_id,name,code,levels,parent_id FROM "+table_name+" ")
		result = self._cr.fetchall()
		all_acts_frame = pd.DataFrame(list(result))
		all_acts_frame = all_acts_frame.rename(columns={0: 'act_id',1: 'act_user_type_id',2: 'act_name',3: 'act_code',4: 'act_levels',5: 'act_parent_id'})

		user_type_table = "account_account_type"
		self.env.cr.execute("select id,name FROM "+user_type_table+" ")
		user_type_result = self._cr.fetchall()
		user_type_frame = pd.DataFrame(list(user_type_result))
		user_type_frame = user_type_frame.rename(columns={0: 'type_id',1: 'act_user_type_name'})
		all_acts_frame = pd.merge(all_acts_frame,user_type_frame,  how='left', left_on='act_user_type_id', right_on ='type_id')

		move_line_table = "account_move_line"
		self.env.cr.execute("select id,account_id,date,debit,credit,move_id,analytic_account_id FROM "+move_line_table+" ")
		move_line_result = self._cr.fetchall()
		period_acts = pd.DataFrame(list(move_line_result))
		open_acts = pd.DataFrame(list(move_line_result))

		period_acts = period_acts.rename(columns={0: 'line_id',1: 'move_act_id',2: 'move_date',3: 'period_debit',4: 'period_credit',5: 'move_id',6: 'analytic_account_id'})

		open_acts = open_acts.rename(columns={0: 'open_line_id',1: 'open_move_act_id',2: 'open_move_date',3: 'open_period_debit',4: 'open_period_credit',5: 'open_move_id',6: 'open_analytic_account_id'})

		move_table = "account_move"
		self.env.cr.execute("select id,state FROM "+move_table+" ")
		move_result = self._cr.fetchall()
		move_frame = pd.DataFrame(list(move_result))
		move_frame = move_frame.rename(columns={0: 'form_id',1: 'move_state'})

		period_acts = pd.merge(period_acts,move_frame,  how='left', left_on='move_id', right_on ='form_id')
		open_acts = pd.merge(open_acts,move_frame,  how='left', left_on='open_move_id', right_on ='form_id')

		new_from = datetime.strptime(data['date_from'], '%Y-%m-%d')
		new_to = datetime.strptime(data['date_to'], '%Y-%m-%d')
		new_from = datetime.date(new_from)
		new_to = datetime.date(new_to)

		if data['target_moves'] == 'all':
			period_acts = period_acts.loc[(period_acts['move_date'] >= new_from) & (period_acts['move_date'] <= new_to)]

			open_acts = open_acts.loc[(open_acts['open_move_date'] < new_from)]
			
		if data['target_moves'] == 'all_posted':
			period_acts = period_acts.loc[(period_acts['move_date'] >= new_from) & (period_acts['move_date'] <= new_to) & (period_acts['move_state'] == 'posted')]

			open_acts = open_acts.loc[(open_acts['open_move_date'] < new_from) & (open_acts['move_state'] == 'posted')]

		if data['analytic_account_ids']:
			period_acts = period_acts[period_acts['analytic_account_id'].isin(data['analytic_account_ids'])]
			open_acts = open_acts[open_acts['open_analytic_account_id'].isin(data['analytic_account_ids'])]
		

		period_acts = period_acts.groupby(['move_act_id'],as_index = False).sum()
		open_acts = open_acts.groupby(['open_move_act_id'],as_index = False).sum()

		all_acts_frame = pd.merge(all_acts_frame,period_acts,  how='left', left_on='act_id', right_on ='move_act_id')

		all_acts_frame = pd.merge(all_acts_frame,open_acts,  how='left', left_on='act_id', right_on ='open_move_act_id')

		all_acts_frame = all_acts_frame.fillna(0)

		for q,r in all_acts_frame.iterrows():
			debit_close = 0
			credit_close = 0
			debit_bal = 0
			credit_bal = 0
			debit_close = r['open_period_debit']+r['period_debit']
			credit_close = r['open_period_credit']+r['period_credit']
			if debit_close > credit_close:
				debit_bal = debit_close - credit_close
			if credit_close > debit_close:
				credit_bal = credit_close - debit_close
			records.append({
				'id':r['act_id'],
				'type':r['act_user_type_name'],
				'name':r['act_name'],
				'code':r['act_code'],
				'levels':r['act_levels'],
				'parent_id':r['act_parent_id'],
				'rep_period_deb':r['period_debit'],
				'rep_period_cre':r['period_credit'],
				'rep_open_deb':r['open_period_debit'],
				'rep_open_cre':r['open_period_credit'],
				'close_debit_bal':debit_bal,
				'close_cre_bal':credit_bal,
				})

		for x in records:
			if x['levels'] == 'l6':
				for y in records:
					if y['parent_id'] == x['id']:
						x['rep_period_deb'] = x['rep_period_deb'] + y['rep_period_deb']
						x['rep_period_cre'] = x['rep_period_cre'] + y['rep_period_cre']
						x['rep_open_deb'] = x['rep_open_deb'] + y['rep_open_deb']
						x['rep_open_cre'] = x['rep_open_cre'] + y['rep_open_cre']
						x['close_debit_bal'] = x['close_debit_bal'] + y['close_debit_bal']
						x['close_cre_bal'] = x['close_cre_bal'] + y['close_cre_bal']


		for x in records:
			if x['levels'] == 'l5':
				for y in records:
					if y['parent_id'] == x['id']:
						x['rep_period_deb'] = x['rep_period_deb'] + y['rep_period_deb']
						x['rep_period_cre'] = x['rep_period_cre'] + y['rep_period_cre']
						x['rep_open_deb'] = x['rep_open_deb'] + y['rep_open_deb']
						x['rep_open_cre'] = x['rep_open_cre'] + y['rep_open_cre']
						x['close_debit_bal'] = x['close_debit_bal'] + y['close_debit_bal']
						x['close_cre_bal'] = x['close_cre_bal'] + y['close_cre_bal']


		for x in records:
			if x['levels'] == 'l4':
				for y in records:
					if y['parent_id'] == x['id']:
						x['rep_period_deb'] = x['rep_period_deb'] + y['rep_period_deb']
						x['rep_period_cre'] = x['rep_period_cre'] + y['rep_period_cre']
						x['rep_open_deb'] = x['rep_open_deb'] + y['rep_open_deb']
						x['rep_open_cre'] = x['rep_open_cre'] + y['rep_open_cre']
						x['close_debit_bal'] = x['close_debit_bal'] + y['close_debit_bal']
						x['close_cre_bal'] = x['close_cre_bal'] + y['close_cre_bal']

		for x in records:
			if x['levels'] == 'l3':
				for y in records:
					if y['parent_id'] == x['id']:
						x['rep_period_deb'] = x['rep_period_deb'] + y['rep_period_deb']
						x['rep_period_cre'] = x['rep_period_cre'] + y['rep_period_cre']
						x['rep_open_deb'] = x['rep_open_deb'] + y['rep_open_deb']
						x['rep_open_cre'] = x['rep_open_cre'] + y['rep_open_cre']
						x['close_debit_bal'] = x['close_debit_bal'] + y['close_debit_bal']
						x['close_cre_bal'] = x['close_cre_bal'] + y['close_cre_bal']

		for x in records:
			if x['levels'] == 'l2':
				for y in records:
					if y['parent_id'] == x['id']:
						x['rep_period_deb'] = x['rep_period_deb'] + y['rep_period_deb']
						x['rep_period_cre'] = x['rep_period_cre'] + y['rep_period_cre']
						x['rep_open_deb'] = x['rep_open_deb'] + y['rep_open_deb']
						x['rep_open_cre'] = x['rep_open_cre'] + y['rep_open_cre']
						x['close_debit_bal'] = x['close_debit_bal'] + y['close_debit_bal']
						x['close_cre_bal'] = x['close_cre_bal'] + y['close_cre_bal']


		for x in records:
			if x['levels'] == 'l1':
				for y in records:
					if y['parent_id'] == x['id']:
						x['rep_period_deb'] = x['rep_period_deb'] + y['rep_period_deb']
						x['rep_period_cre'] = x['rep_period_cre'] + y['rep_period_cre']
						x['rep_open_deb'] = x['rep_open_deb'] + y['rep_open_deb']
						x['rep_open_cre'] = x['rep_open_cre'] + y['rep_open_cre']
						x['close_debit_bal'] = x['close_debit_bal'] + y['close_debit_bal']
						x['close_cre_bal'] = x['close_cre_bal'] + y['close_cre_bal']




		records = sorted(records, key=lambda k: (k['code']))
		if  data['with_movement']:
			records = [i for i in records if (i['rep_open_deb'] > 0 or i['rep_open_cre'] > 0 or i['rep_period_deb'] > 0 or i['rep_period_cre'] > 0)]

	   
		deb1 = 0
		deb2 = 0
		deb3 = 0
		deb4 = 0
		deb5 = 0
		deb6 = 0
		deb7 = 0
		deb8 = 0

	   
		if data['levels'] == '1':

			row = 6
			col = 0
			for chk in records:
				# debit_close = 0
				# credit_close = 0
				# debit_bal = 0
				# credit_bal = 0
				if chk['levels'] == 'l1':

					worksheet.write_string (row, col,str(chk['code']),main_data)
					worksheet.write_string (row, col+1,str(chk['name']),main_data)
					worksheet.write_string (row, col+2,str(chk['type']),main_data)
					worksheet.write_string (row, col+3,str("{0:.2f}".format(chk['rep_open_deb'])),main_data)
					worksheet.write_string (row, col+4,str("{0:.2f}".format(chk['rep_open_cre'])),main_data)
					worksheet.write_string (row, col+5,str("{0:.2f}".format(chk['rep_period_deb'])),main_data)
					worksheet.write_string (row, col+6,str("{0:.2f}".format(chk['rep_period_cre'])),main_data)
					worksheet.write_string (row, col+7,str("{0:.2f}".format(chk['rep_open_deb']+chk['rep_period_deb'])),main_data)
					worksheet.write_string (row, col+8,str("{0:.2f}".format(chk['rep_open_cre']+chk['rep_period_cre'])),main_data)

					# debit_close = chk['rep_open_deb']+chk['rep_period_deb']
					# credit_close = chk['rep_open_cre']+chk['rep_period_cre']
					# if debit_close > credit_close:
					# 	debit_bal = debit_close - credit_close
					# if  credit_close > debit_close:
					# 	credit_bal = credit_close - debit_close

					worksheet.write_string (row, col+9,str("{0:.2f}".format(chk['close_debit_bal'])),main_data)
					worksheet.write_string (row, col+10,str("{0:.2f}".format(chk['close_cre_bal'])),main_data)

					deb1 = deb1 + chk['rep_open_deb']
					deb2 = deb2 + chk['rep_open_cre']
					deb3 = deb3 + chk['rep_period_deb']
					deb4 = deb4 + chk['rep_period_cre']
					deb5 = deb5 + chk['rep_open_deb']+chk['rep_period_deb']
					deb6 = deb6 + chk['rep_open_cre']+chk['rep_period_cre']
					deb7 = deb7 + chk['close_debit_bal']
					deb8 = deb8 + chk['close_cre_bal']

					row += 1

			loc = 'A'+str(row+1)
			loc1 = 'C'+str(row+1)
			loc15 = 'D'+str(row+1)
			loc30 = 'E'+str(row+1)
			loc45 = 'F'+str(row+1)
			loc60 = 'G'+str(row+1)
			loc75 = 'H'+str(row+1)
			loc90 = 'I'+str(row+1)
			loc91 = 'J'+str(row+1)
			loc92 = 'K'+str(row+1)

			end_loc = str(loc)+':'+str(loc1)
			worksheet.merge_range(str(end_loc), 'Total' ,main_heading)
			worksheet.write_string(str(loc15),str("{0:.2f}".format(deb1)),main_heading1)
			worksheet.write_string(str(loc30),str("{0:.2f}".format(deb2)),main_heading1)
			worksheet.write_string(str(loc45),str("{0:.2f}".format(deb3)),main_heading1)
			worksheet.write_string(str(loc60),str("{0:.2f}".format(deb4)),main_heading1)
			worksheet.write_string(str(loc75),str("{0:.2f}".format(deb5)),main_heading1)
			worksheet.write_string(str(loc90),str("{0:.2f}".format(deb6)),main_heading1)
			worksheet.write_string(str(loc91),str("{0:.2f}".format(deb7)),main_heading1)
			worksheet.write_string(str(loc92),str("{0:.2f}".format(deb8)),main_heading1)

		if data['levels'] == '2':
			
			row = 6
			col = 0
			for chk in records:
				if chk['levels'] == 'l1':
					# debit_close = 0
					# credit_close = 0
					# debit_bal = 0
					# credit_bal = 0
					
					worksheet.write_string (row, col,str(chk['code']),main_data)
					worksheet.write_string (row, col+1,str(chk['name']),main_data)
					worksheet.write_string (row, col+2,str(chk['type']),main_data)
					worksheet.write_string (row, col+3,str("{0:.2f}".format(chk['rep_open_deb'])),main_data)
					worksheet.write_string (row, col+4,str("{0:.2f}".format(chk['rep_open_cre'])),main_data)
					worksheet.write_string (row, col+5,str("{0:.2f}".format(chk['rep_period_deb'])),main_data)
					worksheet.write_string (row, col+6,str("{0:.2f}".format(chk['rep_period_cre'])),main_data)
					worksheet.write_string (row, col+7,str("{0:.2f}".format(chk['rep_open_deb']+chk['rep_period_deb'])),main_data)
					worksheet.write_string (row, col+8,str("{0:.2f}".format(chk['rep_open_cre']+chk['rep_period_cre'])),main_data)

					# debit_close = chk['rep_open_deb']+chk['rep_period_deb']
					# credit_close = chk['rep_open_cre']+chk['rep_period_cre']
					# if debit_close > credit_close:
					# 	debit_bal = debit_close - credit_close
					# if  credit_close > debit_close:
					# 	credit_bal = credit_close - debit_close

					worksheet.write_string (row, col+9,str("{0:.2f}".format(chk['close_debit_bal'])),main_data)
					worksheet.write_string (row, col+10,str("{0:.2f}".format(chk['close_cre_bal'])),main_data)

					deb1 = deb1 + chk['rep_open_deb']
					deb2 = deb2 + chk['rep_open_cre']
					deb3 = deb3 + chk['rep_period_deb']
					deb4 = deb4 + chk['rep_period_cre']
					deb5 = deb5 + chk['rep_open_deb']+chk['rep_period_deb']
					deb6 = deb6 + chk['rep_open_cre']+chk['rep_period_cre']
					deb7 = deb7 + chk['close_debit_bal']
					deb8 = deb8 + chk['close_cre_bal']

					row = row + 1
					col = 0

					for chk_2 in records:
						if chk_2['levels'] == 'l2' and chk_2['parent_id'] == chk['id']:
							# debit_close = 0
							# credit_close = 0
							# debit_bal = 0
							# credit_bal = 0
							worksheet.write_string (row, col,str(chk_2['code']),main_data)
							worksheet.write_string (row, col+1,str(chk_2['name']),main_data)
							worksheet.write_string (row, col+2,str(chk_2['type']),main_data)
							worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_2['rep_open_deb'])),main_data)
							worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_2['rep_open_cre'])),main_data)
							worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_2['rep_period_deb'])),main_data)
							worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_2['rep_period_cre'])),main_data)
							worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_2['rep_open_deb']+chk_2['rep_period_deb'])),main_data)
							worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_2['rep_open_cre']+chk_2['rep_period_cre'])),main_data)

							# debit_close = chk_2['rep_open_deb']+chk_2['rep_period_deb']
							# credit_close = chk_2['rep_open_cre']+chk_2['rep_period_cre']
							# if debit_close > credit_close:
							# 	debit_bal = debit_close - credit_close
							# if  credit_close > debit_close:
							# 	credit_bal = credit_close - debit_close

							worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_2['close_debit_bal'])),main_data)
							worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_2['close_cre_bal'])),main_data)

							# deb7 = deb7 + debit_bal
							# deb8 = deb8 + credit_bal

							row += 1

			loc = 'A'+str(row+1)
			loc1 = 'C'+str(row+1)
			loc15 = 'D'+str(row+1)
			loc30 = 'E'+str(row+1)
			loc45 = 'F'+str(row+1)
			loc60 = 'G'+str(row+1)
			loc75 = 'H'+str(row+1)
			loc90 = 'I'+str(row+1)
			loc91 = 'J'+str(row+1)
			loc92 = 'K'+str(row+1)

			end_loc = str(loc)+':'+str(loc1)
			worksheet.merge_range(str(end_loc), 'Total' ,main_heading)
			worksheet.write_string(str(loc15),str("{0:.2f}".format(deb1)),main_heading1)
			worksheet.write_string(str(loc30),str("{0:.2f}".format(deb2)),main_heading1)
			worksheet.write_string(str(loc45),str("{0:.2f}".format(deb3)),main_heading1)
			worksheet.write_string(str(loc60),str("{0:.2f}".format(deb4)),main_heading1)
			worksheet.write_string(str(loc75),str("{0:.2f}".format(deb5)),main_heading1)
			worksheet.write_string(str(loc90),str("{0:.2f}".format(deb6)),main_heading1)
			worksheet.write_string(str(loc91),str("{0:.2f}".format(deb7)),main_heading1)
			worksheet.write_string(str(loc92),str("{0:.2f}".format(deb8)),main_heading1)
			
		if data['levels'] == '3':
			
			row = 6
			col = 0
			for chk in records:
				if chk['levels'] == 'l1':
					# debit_close = 0
					# credit_close = 0
					# debit_bal = 0
					# credit_bal = 0
					worksheet.write_string (row, col,str(chk['code']),main_data)
					worksheet.write_string (row, col+1,str(chk['name']),main_data)
					worksheet.write_string (row, col+2,str(chk['type']),main_data)
					worksheet.write_string (row, col+3,str("{0:.2f}".format(chk['rep_open_deb'])),main_data)
					worksheet.write_string (row, col+4,str("{0:.2f}".format(chk['rep_open_cre'])),main_data)
					worksheet.write_string (row, col+5,str("{0:.2f}".format(chk['rep_period_deb'])),main_data)
					worksheet.write_string (row, col+6,str("{0:.2f}".format(chk['rep_period_cre'])),main_data)
					worksheet.write_string (row, col+7,str("{0:.2f}".format(chk['rep_open_deb']+chk['rep_period_deb'])),main_data)
					worksheet.write_string (row, col+8,str("{0:.2f}".format(chk['rep_open_cre']+chk['rep_period_cre'])),main_data)

					# debit_close = chk['rep_open_deb']+chk['rep_period_deb']
					# credit_close = chk['rep_open_cre']+chk['rep_period_cre']
					# if debit_close > credit_close:
					# 	debit_bal = debit_close - credit_close
					# if  credit_close > debit_close:
					# 	credit_bal = credit_close - debit_close

					worksheet.write_string (row, col+9,str("{0:.2f}".format(chk['close_debit_bal'])),main_data)
					worksheet.write_string (row, col+10,str("{0:.2f}".format(chk['close_cre_bal'])),main_data)

					deb1 = deb1 + chk['rep_open_deb']
					deb2 = deb2 + chk['rep_open_cre']
					deb3 = deb3 + chk['rep_period_deb']
					deb4 = deb4 + chk['rep_period_cre']
					deb5 = deb5 + chk['rep_open_deb']+chk['rep_period_deb']
					deb6 = deb6 + chk['rep_open_cre']+chk['rep_period_cre']
					deb7 = deb7 + chk['close_debit_bal']
					deb8 = deb8 + chk['close_cre_bal']

					row = row + 1
					col = 0

					for chk_2 in records:
						if chk_2['levels'] == 'l2' and chk_2['parent_id'] == chk['id']:
							# debit_close = 0
							# credit_close = 0
							# debit_bal = 0
							# credit_bal = 0
							worksheet.write_string (row, col,str(chk_2['code']),main_data)
							worksheet.write_string (row, col+1,str(chk_2['name']),main_data)
							worksheet.write_string (row, col+2,str(chk_2['type']),main_data)
							worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_2['rep_open_deb'])),main_data)
							worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_2['rep_open_cre'])),main_data)
							worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_2['rep_period_deb'])),main_data)
							worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_2['rep_period_cre'])),main_data)
							worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_2['rep_open_deb']+chk_2['rep_period_deb'])),main_data)
							worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_2['rep_open_cre']+chk_2['rep_period_cre'])),main_data)

							# debit_close = chk_2['rep_open_deb']+chk_2['rep_period_deb']
							# credit_close = chk_2['rep_open_cre']+chk_2['rep_period_cre']
							# if debit_close > credit_close:
							# 	debit_bal = debit_close - credit_close
							# if  credit_close > debit_close:
							# 	credit_bal = credit_close - debit_close

							worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_2['close_debit_bal'])),main_data)
							worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_2['close_cre_bal'])),main_data)
							# deb7 = deb7 + debit_bal
							# deb8 = deb8 + credit_bal

							row += 1
							col = 0

							for chk_3 in records:
								if chk_3['levels'] == 'l3' and chk_3['parent_id'] == chk_2['id']:
									# debit_close = 0
									# credit_close = 0
									# debit_bal = 0
									# credit_bal = 0
									worksheet.write_string (row, col,str(chk_3['code']),main_data)
									worksheet.write_string (row, col+1,str(chk_3['name']),main_data)
									worksheet.write_string (row, col+2,str(chk_3['type']),main_data)
									worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_3['rep_open_deb'])),main_data)
									worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_3['rep_open_cre'])),main_data)
									worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_3['rep_period_deb'])),main_data)
									worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_3['rep_period_cre'])),main_data)
									worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_3['rep_open_deb']+chk_3['rep_period_deb'])),main_data)
									worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_3['rep_open_cre']+chk_3['rep_period_cre'])),main_data)
									# debit_close = chk_3['rep_open_deb']+chk_3['rep_period_deb']
									# credit_close = chk_3['rep_open_cre']+chk_3['rep_period_cre']
									# if debit_close > credit_close:
									# 	debit_bal = debit_close - credit_close
									# if  credit_close > debit_close:
									# 	credit_bal = credit_close - debit_close

									worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_3['close_debit_bal'])),main_data)
									worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_3['close_cre_bal'])),main_data)

									# deb7 = deb7 + debit_bal
									# deb8 = deb8 + credit_bal

									row += 1


			loc = 'A'+str(row+1)
			loc1 = 'C'+str(row+1)
			loc15 = 'D'+str(row+1)
			loc30 = 'E'+str(row+1)
			loc45 = 'F'+str(row+1)
			loc60 = 'G'+str(row+1)
			loc75 = 'H'+str(row+1)
			loc90 = 'I'+str(row+1)
			loc91 = 'J'+str(row+1)
			loc92 = 'K'+str(row+1)

			end_loc = str(loc)+':'+str(loc1)
			worksheet.merge_range(str(end_loc), 'Total' ,main_heading)
			worksheet.write_string(str(loc15),str("{0:.2f}".format(deb1)),main_heading1)
			worksheet.write_string(str(loc30),str("{0:.2f}".format(deb2)),main_heading1)
			worksheet.write_string(str(loc45),str("{0:.2f}".format(deb3)),main_heading1)
			worksheet.write_string(str(loc60),str("{0:.2f}".format(deb4)),main_heading1)
			worksheet.write_string(str(loc75),str("{0:.2f}".format(deb5)),main_heading1)
			worksheet.write_string(str(loc90),str("{0:.2f}".format(deb6)),main_heading1)
			worksheet.write_string(str(loc91),str("{0:.2f}".format(deb7)),main_heading1)
			worksheet.write_string(str(loc92),str("{0:.2f}".format(deb8)),main_heading1)
				
		if data['levels'] == '4':
			
			row = 6
			col = 0
			for chk in records:
				if chk['levels'] == 'l1':
					# debit_close = 0
					# credit_close = 0
					# debit_bal = 0
					# credit_bal = 0
					worksheet.write_string (row, col,str(chk['code']),main_data)
					worksheet.write_string (row, col+1,str(chk['name']),main_data)
					worksheet.write_string (row, col+2,str(chk['type']),main_data)
					worksheet.write_string (row, col+3,str("{0:.2f}".format(chk['rep_open_deb'])),main_data)
					worksheet.write_string (row, col+4,str("{0:.2f}".format(chk['rep_open_cre'])),main_data)
					worksheet.write_string (row, col+5,str("{0:.2f}".format(chk['rep_period_deb'])),main_data)
					worksheet.write_string (row, col+6,str("{0:.2f}".format(chk['rep_period_cre'])),main_data)
					worksheet.write_string (row, col+7,str("{0:.2f}".format(chk['rep_open_deb']+chk['rep_period_deb'])),main_data)
					worksheet.write_string (row, col+8,str("{0:.2f}".format(chk['rep_open_cre']+chk['rep_period_cre'])),main_data)

					# debit_close = chk['rep_open_deb']+chk['rep_period_deb']
					# credit_close = chk['rep_open_cre']+chk['rep_period_cre']
					# if debit_close > credit_close:
					# 	debit_bal = debit_close - credit_close
					# if  credit_close > debit_close:
					# 	credit_bal = credit_close - debit_close

					worksheet.write_string (row, col+9,str("{0:.2f}".format(chk['close_debit_bal'])),main_data)
					worksheet.write_string (row, col+10,str("{0:.2f}".format(chk['close_cre_bal'])),main_data)


					deb1 = deb1 + chk['rep_open_deb']
					deb2 = deb2 + chk['rep_open_cre']
					deb3 = deb3 + chk['rep_period_deb']
					deb4 = deb4 + chk['rep_period_cre']
					deb5 = deb5 + chk['rep_open_deb']+chk['rep_period_deb']
					deb6 = deb6 + chk['rep_open_cre']+chk['rep_period_cre']
					deb7 = deb7 + chk['close_debit_bal']
					deb8 = deb8 + chk['close_cre_bal']

					row = row + 1
					col = 0

					for chk_2 in records:
						if chk_2['levels'] == 'l2' and chk_2['parent_id'] == chk['id']:
							# debit_close = 0
							# credit_close = 0
							# debit_bal = 0
							# credit_bal = 0
							worksheet.write_string (row, col,str(chk_2['code']),main_data)
							worksheet.write_string (row, col+1,str(chk_2['name']),main_data)
							worksheet.write_string (row, col+2,str(chk_2['type']),main_data)
							worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_2['rep_open_deb'])),main_data)
							worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_2['rep_open_cre'])),main_data)
							worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_2['rep_period_deb'])),main_data)
							worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_2['rep_period_cre'])),main_data)
							worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_2['rep_open_deb']+chk_2['rep_period_deb'])),main_data)
							worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_2['rep_open_cre']+chk_2['rep_period_cre'])),main_data)

							# debit_close = chk_2['rep_open_deb']+chk_2['rep_period_deb']
							# credit_close = chk_2['rep_open_cre']+chk_2['rep_period_cre']
							# if debit_close > credit_close:
							# 	debit_bal = debit_close - credit_close
							# if  credit_close > debit_close:
							# 	credit_bal = credit_close - debit_close

							worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_2['close_debit_bal'])),main_data)
							worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_2['close_cre_bal'])),main_data)

							# deb7 = deb7 + debit_bal
							# deb8 = deb8 + credit_bal

							row += 1
							col = 0

							for chk_3 in records:
								if chk_3['levels'] == 'l3' and chk_3['parent_id'] == chk_2['id']:
									# debit_close = 0
									# credit_close = 0
									# debit_bal = 0
									# credit_bal = 0
									worksheet.write_string (row, col,str(chk_3['code']),main_data)
									worksheet.write_string (row, col+1,str(chk_3['name']),main_data)
									worksheet.write_string (row, col+2,str(chk_3['type']),main_data)
									worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_3['rep_open_deb'])),main_data)
									worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_3['rep_open_cre'])),main_data)
									worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_3['rep_period_deb'])),main_data)
									worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_3['rep_period_cre'])),main_data)
									worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_3['rep_open_deb']+chk_3['rep_period_deb'])),main_data)
									worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_3['rep_open_cre']+chk_3['rep_period_cre'])),main_data)

									# debit_close = chk_3['rep_open_deb']+chk_3['rep_period_deb']
									# credit_close = chk_3['rep_open_cre']+chk_3['rep_period_cre']
									# if debit_close > credit_close:
									# 	debit_bal = debit_close - credit_close
									# if  credit_close > debit_close:
									# 	credit_bal = credit_close - debit_close

									worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_3['close_debit_bal'])),main_data)
									worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_3['close_cre_bal'])),main_data)

									# deb7 = deb7 + debit_bal
									# deb8 = deb8 + credit_bal

									row += 1
									col = 0

									for chk_4 in records:
										if chk_4['levels'] == 'l4' and chk_4['parent_id'] == chk_3['id']:
											# debit_close = 0
											# credit_close = 0
											# debit_bal = 0
											# credit_bal = 0
											worksheet.write_string (row, col,str(chk_4['code']),main_data)
											worksheet.write_string (row, col+1,str(chk_4['name']),main_data)
											worksheet.write_string (row, col+2,str(chk_4['type']),main_data)
											worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_4['rep_open_deb'])),main_data)
											worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_4['rep_open_cre'])),main_data)
											worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_4['rep_period_deb'])),main_data)
											worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_4['rep_period_cre'])),main_data)
											worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_4['rep_open_deb']+chk_4['rep_period_deb'])),main_data)
											worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_4['rep_open_cre']+chk_4['rep_period_cre'])),main_data)

											# debit_close = chk_4['rep_open_deb']+chk_4['rep_period_deb']
											# credit_close = chk_4['rep_open_cre']+chk_4['rep_period_cre']
											# if debit_close > credit_close:
											# 	debit_bal = debit_close - credit_close
											# if  credit_close > debit_close:
											# 	credit_bal = credit_close - debit_close

											worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_4['close_debit_bal'])),main_data)
											worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_4['close_cre_bal'])),main_data)

											# deb7 = deb7 + debit_bal
											# deb8 = deb8 + credit_bal

											row += 1

			loc = 'A'+str(row+1)
			loc1 = 'C'+str(row+1)
			loc15 = 'D'+str(row+1)
			loc30 = 'E'+str(row+1)
			loc45 = 'F'+str(row+1)
			loc60 = 'G'+str(row+1)
			loc75 = 'H'+str(row+1)
			loc90 = 'I'+str(row+1)
			loc91 = 'J'+str(row+1)
			loc92 = 'K'+str(row+1)

			end_loc = str(loc)+':'+str(loc1)
			worksheet.merge_range(str(end_loc), 'Total' ,main_heading)
			worksheet.write_string(str(loc15),str("{0:.2f}".format(deb1)),main_heading1)
			worksheet.write_string(str(loc30),str("{0:.2f}".format(deb2)),main_heading1)
			worksheet.write_string(str(loc45),str("{0:.2f}".format(deb3)),main_heading1)
			worksheet.write_string(str(loc60),str("{0:.2f}".format(deb4)),main_heading1)
			worksheet.write_string(str(loc75),str("{0:.2f}".format(deb5)),main_heading1)
			worksheet.write_string(str(loc90),str("{0:.2f}".format(deb6)),main_heading1)
			worksheet.write_string(str(loc91),str("{0:.2f}".format(deb7)),main_heading1)
			worksheet.write_string(str(loc92),str("{0:.2f}".format(deb8)),main_heading1)
			
		if data['levels'] == '5':
			
			row = 6
			col = 0
			for chk in records:
				if chk['levels'] == 'l1':
					# debit_close = 0
					# credit_close = 0
					# debit_bal = 0
					# credit_bal = 0
					worksheet.write_string (row, col,str(chk['code']),main_data)
					worksheet.write_string (row, col+1,str(chk['name']),main_data)
					worksheet.write_string (row, col+2,str(chk['type']),main_data)
					worksheet.write_string (row, col+3,str("{0:.2f}".format(chk['rep_open_deb'])),main_data)
					worksheet.write_string (row, col+4,str("{0:.2f}".format(chk['rep_open_cre'])),main_data)
					worksheet.write_string (row, col+5,str("{0:.2f}".format(chk['rep_period_deb'])),main_data)
					worksheet.write_string (row, col+6,str("{0:.2f}".format(chk['rep_period_cre'])),main_data)
					worksheet.write_string (row, col+7,str("{0:.2f}".format(chk['rep_open_deb']+chk['rep_period_deb'])),main_data)
					worksheet.write_string (row, col+8,str("{0:.2f}".format(chk['rep_open_cre']+chk['rep_period_cre'])),main_data)

					# debit_close = chk['rep_open_deb']+chk['rep_period_deb']
					# credit_close = chk['rep_open_cre']+chk['rep_period_cre']
					# if debit_close > credit_close:
					# 	debit_bal = debit_close - credit_close
					# if  credit_close > debit_close:
					# 	credit_bal = credit_close - debit_close

					worksheet.write_string (row, col+9,str("{0:.2f}".format(chk['close_debit_bal'])),main_data)
					worksheet.write_string (row, col+10,str("{0:.2f}".format(chk['close_cre_bal'])),main_data)



					deb1 = deb1 + chk['rep_open_deb']
					deb2 = deb2 + chk['rep_open_cre']
					deb3 = deb3 + chk['rep_period_deb']
					deb4 = deb4 + chk['rep_period_cre']
					deb5 = deb5 + chk['rep_open_deb']+chk['rep_period_deb']
					deb6 = deb6 + chk['rep_open_cre']+chk['rep_period_cre']
					deb7 = deb7 + chk['close_debit_bal']
					deb8 = deb8 + chk['close_cre_bal']

					row = row + 1
					col = 0

					for chk_2 in records:
						if chk_2['levels'] == 'l2' and chk_2['parent_id'] == chk['id']:
							# debit_close = 0
							# credit_close = 0
							# debit_bal = 0
							# credit_bal = 0
							worksheet.write_string (row, col,str(chk_2['code']),main_data)
							worksheet.write_string (row, col+1,str(chk_2['name']),main_data)
							worksheet.write_string (row, col+2,str(chk_2['type']),main_data)
							worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_2['rep_open_deb'])),main_data)
							worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_2['rep_open_cre'])),main_data)
							worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_2['rep_period_deb'])),main_data)
							worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_2['rep_period_cre'])),main_data)
							worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_2['rep_open_deb']+chk_2['rep_period_deb'])),main_data)
							worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_2['rep_open_cre']+chk_2['rep_period_cre'])),main_data)

							# debit_close = chk_2['rep_open_deb']+chk_2['rep_period_deb']
							# credit_close = chk_2['rep_open_cre']+chk_2['rep_period_cre']
							# if debit_close > credit_close:
							# 	debit_bal = debit_close - credit_close
							# if  credit_close > debit_close:
							# 	credit_bal = credit_close - debit_close

							worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_2['close_debit_bal'])),main_data)
							worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_2['close_cre_bal'])),main_data)

							deb7 = deb7 + debit_bal
							deb8 = deb8 + credit_bal


							row += 1
							col = 0

							for chk_3 in records:
								if chk_3['levels'] == 'l3' and chk_3['parent_id'] == chk_2['id']:
									# debit_close = 0
									# credit_close = 0
									# debit_bal = 0
									# credit_bal = 0
									worksheet.write_string (row, col,str(chk_3['code']),main_data)
									worksheet.write_string (row, col+1,str(chk_3['name']),main_data)
									worksheet.write_string (row, col+2,str(chk_3['type']),main_data)
									worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_3['rep_open_deb'])),main_data)
									worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_3['rep_open_cre'])),main_data)
									worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_3['rep_period_deb'])),main_data)
									worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_3['rep_period_cre'])),main_data)
									worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_3['rep_open_deb']+chk_3['rep_period_deb'])),main_data)
									worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_3['rep_open_cre']+chk_3['rep_period_cre'])),main_data)

									# debit_close = chk_3['rep_open_deb']+chk_3['rep_period_deb']
									# credit_close = chk_3['rep_open_cre']+chk_3['rep_period_cre']
									# if debit_close > credit_close:
									# 	debit_bal = debit_close - credit_close
									# if  credit_close > debit_close:
									# 	credit_bal = credit_close - debit_close

									worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_3['close_debit_bal'])),main_data)
									worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_3['close_cre_bal'])),main_data)

									# deb7 = deb7 + debit_bal
									# deb8 = deb8 + credit_bal

									row += 1
									col = 0

									for chk_4 in records:
										if chk_4['levels'] == 'l4' and chk_4['parent_id'] == chk_3['id']:
											# debit_close = 0
											# credit_close = 0
											# debit_bal = 0
											# credit_bal = 0
											worksheet.write_string (row, col,str(chk_4['code']),main_data)
											worksheet.write_string (row, col+1,str(chk_4['name']),main_data)
											worksheet.write_string (row, col+2,str(chk_4['type']),main_data)
											worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_4['rep_open_deb'])),main_data)
											worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_4['rep_open_cre'])),main_data)
											worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_4['rep_period_deb'])),main_data)
											worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_4['rep_period_cre'])),main_data)
											worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_4['rep_open_deb']+chk_4['rep_period_deb'])),main_data)
											worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_4['rep_open_cre']+chk_4['rep_period_cre'])),main_data)

											# debit_close = chk_4['rep_open_deb']+chk_4['rep_period_deb']
											# credit_close = chk_4['rep_open_cre']+chk_4['rep_period_cre']
											# if debit_close > credit_close:
											# 	debit_bal = debit_close - credit_close
											# if  credit_close > debit_close:
											# 	credit_bal = credit_close - debit_close

											worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_4['close_debit_bal'])),main_data)
											worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_4['close_cre_bal'])),main_data)

											# deb7 = deb7 + debit_bal
											# deb8 = deb8 + credit_bal

											row += 1
											col = 0

											for chk_5 in records:
												if chk_5['levels'] == 'l5' and chk_5['parent_id'] == chk_4['id']:
													# debit_close = 0
													# credit_close = 0
													# debit_bal = 0
													# credit_bal = 0
													worksheet.write_string (row, col,str(chk_5['code']),main_data)
													worksheet.write_string (row, col+1,str(chk_5['name']),main_data)
													worksheet.write_string (row, col+2,str(chk_5['type']),main_data)
													worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_5['rep_open_deb'])),main_data)
													worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_5['rep_open_cre'])),main_data)
													worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_5['rep_period_deb'])),main_data)
													worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_5['rep_period_cre'])),main_data)
													worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_5['rep_open_deb']+chk_5['rep_period_deb'])),main_data)
													worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_5['rep_open_cre']+chk_5['rep_period_cre'])),main_data)

													# debit_close = chk_5['rep_open_deb']+chk_5['rep_period_deb']
													# credit_close = chk_5['rep_open_cre']+chk_5['rep_period_cre']
													# if debit_close > credit_close:
													# 	debit_bal = debit_close - credit_close
													# if  credit_close > debit_close:
													# 	credit_bal = credit_close - debit_close

													worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_5['close_debit_bal'])),main_data)
													worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_5['close_cre_bal'])),main_data)

													# deb7 = deb7 + debit_bal
													# deb8 = deb8 + credit_bal

													row += 1

			loc = 'A'+str(row+1)
			loc1 = 'C'+str(row+1)
			loc15 = 'D'+str(row+1)
			loc30 = 'E'+str(row+1)
			loc45 = 'F'+str(row+1)
			loc60 = 'G'+str(row+1)
			loc75 = 'H'+str(row+1)
			loc90 = 'I'+str(row+1)
			loc91 = 'J'+str(row+1)
			loc92 = 'K'+str(row+1)

			end_loc = str(loc)+':'+str(loc1)
			worksheet.merge_range(str(end_loc), 'Total' ,main_heading)
			worksheet.write_string(str(loc15),str("{0:.2f}".format(deb1)),main_heading1)
			worksheet.write_string(str(loc30),str("{0:.2f}".format(deb2)),main_heading1)
			worksheet.write_string(str(loc45),str("{0:.2f}".format(deb3)),main_heading1)
			worksheet.write_string(str(loc60),str("{0:.2f}".format(deb4)),main_heading1)
			worksheet.write_string(str(loc75),str("{0:.2f}".format(deb5)),main_heading1)
			worksheet.write_string(str(loc90),str("{0:.2f}".format(deb6)),main_heading1)
			worksheet.write_string(str(loc91),str("{0:.2f}".format(deb7)),main_heading1)
			worksheet.write_string(str(loc92),str("{0:.2f}".format(deb8)),main_heading1)

		if data['levels'] == '6':
			
			row = 6
			col = 0
			for chk in records:
				if chk['levels'] == 'l1':
					# debit_close = 0
					# credit_close = 0
					# debit_bal = 0
					# credit_bal = 0
					worksheet.write_string (row, col,str(chk['code']),main_data)
					worksheet.write_string (row, col+1,str(chk['name']),main_data)
					worksheet.write_string (row, col+2,str(chk['type']),main_data)
					worksheet.write_string (row, col+3,str("{0:.2f}".format(chk['rep_open_deb'])),main_data)
					worksheet.write_string (row, col+4,str("{0:.2f}".format(chk['rep_open_cre'])),main_data)
					worksheet.write_string (row, col+5,str("{0:.2f}".format(chk['rep_period_deb'])),main_data)
					worksheet.write_string (row, col+6,str("{0:.2f}".format(chk['rep_period_cre'])),main_data)
					worksheet.write_string (row, col+7,str("{0:.2f}".format(chk['rep_open_deb']+chk['rep_period_deb'])),main_data)
					worksheet.write_string (row, col+8,str("{0:.2f}".format(chk['rep_open_cre']+chk['rep_period_cre'])),main_data)

					# debit_close = chk['rep_open_deb']+chk['rep_period_deb']
					# credit_close = chk['rep_open_cre']+chk['rep_period_cre']
					# if debit_close > credit_close:
					# 	debit_bal = debit_close - credit_close
					# if  credit_close > debit_close:
					# 	credit_bal = credit_close - debit_close

					worksheet.write_string (row, col+9,str("{0:.2f}".format(chk['close_debit_bal'])),main_data)
					worksheet.write_string (row, col+10,str("{0:.2f}".format(chk['close_cre_bal'])),main_data)

					deb1 = deb1 + chk['rep_open_deb']
					deb2 = deb2 + chk['rep_open_cre']
					deb3 = deb3 + chk['rep_period_deb']
					deb4 = deb4 + chk['rep_period_cre']
					deb5 = deb5 + chk['rep_open_deb']+chk['rep_period_deb']
					deb6 = deb6 + chk['rep_open_cre']+chk['rep_period_cre']
					deb7 = deb7 + chk['close_debit_bal']
					deb8 = deb8 + chk['close_cre_bal']

					row = row + 1
					col = 0

					for chk_2 in records:
						if chk_2['levels'] == 'l2' and chk_2['parent_id'] == chk['id']:
							# debit_close = 0
							# credit_close = 0
							# debit_bal = 0
							# credit_bal = 0
							worksheet.write_string (row, col,str(chk_2['code']),main_data)
							worksheet.write_string (row, col+1,str(chk_2['name']),main_data)
							worksheet.write_string (row, col+2,str(chk_2['type']),main_data)
							worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_2['rep_open_deb'])),main_data)
							worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_2['rep_open_cre'])),main_data)
							worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_2['rep_period_deb'])),main_data)
							worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_2['rep_period_cre'])),main_data)
							worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_2['rep_open_deb']+chk_2['rep_period_deb'])),main_data)
							worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_2['rep_open_cre']+chk_2['rep_period_cre'])),main_data)

							# debit_close = chk_2['rep_open_deb']+chk_2['rep_period_deb']
							# credit_close = chk_2['rep_open_cre']+chk_2['rep_period_cre']
							# if debit_close > credit_close:
							# 	debit_bal = debit_close - credit_close
							# if  credit_close > debit_close:
							# 	credit_bal = credit_close - debit_close

							worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_2['close_debit_bal'])),main_data)
							worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_2['close_cre_bal'])),main_data)

							# deb7 = deb7 + debit_bal
							# deb8 = deb8 + credit_bal


							row += 1
							col = 0

							for chk_3 in records:
								if chk_3['levels'] == 'l3' and chk_3['parent_id'] == chk_2['id']:
									# debit_close = 0
									# credit_close = 0
									# debit_bal = 0
									# credit_bal = 0
									worksheet.write_string (row, col,str(chk_3['code']),main_data)
									worksheet.write_string (row, col+1,str(chk_3['name']),main_data)
									worksheet.write_string (row, col+2,str(chk_3['type']),main_data)
									worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_3['rep_open_deb'])),main_data)
									worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_3['rep_open_cre'])),main_data)
									worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_3['rep_period_deb'])),main_data)
									worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_3['rep_period_cre'])),main_data)
									worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_3['rep_open_deb']+chk_3['rep_period_deb'])),main_data)
									worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_3['rep_open_cre']+chk_3['rep_period_cre'])),main_data)

									# debit_close = chk_3['rep_open_deb']+chk_3['rep_period_deb']
									# credit_close = chk_3['rep_open_cre']+chk_3['rep_period_cre']
									# if debit_close > credit_close:
									# 	debit_bal = debit_close - credit_close
									# if  credit_close > debit_close:
									# 	credit_bal = credit_close - debit_close

									worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_3['close_debit_bal'])),main_data)
									worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_3['close_cre_bal'])),main_data)

									# deb7 = deb7 + debit_bal
									# deb8 = deb8 + credit_bal

									row += 1
									col = 0

									for chk_4 in records:
										if chk_4['levels'] == 'l4' and chk_4['parent_id'] == chk_3['id']:
											# debit_close = 0
											# credit_close = 0
											# debit_bal = 0
											# credit_bal = 0
											worksheet.write_string (row, col,str(chk_4['code']),main_data)
											worksheet.write_string (row, col+1,str(chk_4['name']),main_data)
											worksheet.write_string (row, col+2,str(chk_4['type']),main_data)
											worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_4['rep_open_deb'])),main_data)
											worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_4['rep_open_cre'])),main_data)
											worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_4['rep_period_deb'])),main_data)
											worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_4['rep_period_cre'])),main_data)
											worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_4['rep_open_deb']+chk_4['rep_period_deb'])),main_data)
											worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_4['rep_open_cre']+chk_4['rep_period_cre'])),main_data)

											# debit_close = chk_4['rep_open_deb']+chk_4['rep_period_deb']
											# credit_close = chk_4['rep_open_cre']+chk_4['rep_period_cre']
											# if debit_close > credit_close:
											# 	debit_bal = debit_close - credit_close
											# if  credit_close > debit_close:
											# 	credit_bal = credit_close - debit_close

											worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_4['close_debit_bal'])),main_data)
											worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_4['close_cre_bal'])),main_data)

											# deb7 = deb7 + debit_bal
											# deb8 = deb8 + credit_bal

											row += 1
											col = 0

											for chk_5 in records:
												if chk_5['levels'] == 'l5' and chk_5['parent_id'] == chk_4['id']:
													# debit_close = 0
													# credit_close = 0
													# debit_bal = 0
													# credit_bal = 0
													worksheet.write_string (row, col,str(chk_5['code']),main_data)
													worksheet.write_string (row, col+1,str(chk_5['name']),main_data)
													worksheet.write_string (row, col+2,str(chk_5['type']),main_data)
													worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_5['rep_open_deb'])),main_data)
													worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_5['rep_open_cre'])),main_data)
													worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_5['rep_period_deb'])),main_data)
													worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_5['rep_period_cre'])),main_data)
													worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_5['rep_open_deb']+chk_5['rep_period_deb'])),main_data)
													worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_5['rep_open_cre']+chk_5['rep_period_cre'])),main_data)

													# debit_close = chk_5['rep_open_deb']+chk_5['rep_period_deb']
													# credit_close = chk_5['rep_open_cre']+chk_5['rep_period_cre']
													# if debit_close > credit_close:
													# 	debit_bal = debit_close - credit_close
													# if  credit_close > debit_close:
													# 	credit_bal = credit_close - debit_close

													worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_5['close_debit_bal'])),main_data)
													worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_5['close_cre_bal'])),main_data)

													# deb7 = deb7 + debit_bal
													# deb8 = deb8 + credit_bal

													row += 1
													col = 0

													for chk_6 in records:
														if chk_6['levels'] == 'l6' and chk_6['parent_id'] == chk_5['id']:
															# debit_close = 0
															# credit_close = 0
															# debit_bal = 0
															# credit_bal = 0
															worksheet.write_string (row, col,str(chk_6['code']),main_data)
															worksheet.write_string (row, col+1,str(chk_6['name']),main_data)
															worksheet.write_string (row, col+2,str(chk_6['type']),main_data)
															worksheet.write_string (row, col+3,str("{0:.2f}".format(chk_6['rep_open_deb'])),main_data)
															worksheet.write_string (row, col+4,str("{0:.2f}".format(chk_6['rep_open_cre'])),main_data)
															worksheet.write_string (row, col+5,str("{0:.2f}".format(chk_6['rep_period_deb'])),main_data)
															worksheet.write_string (row, col+6,str("{0:.2f}".format(chk_6['rep_period_cre'])),main_data)
															worksheet.write_string (row, col+7,str("{0:.2f}".format(chk_6['rep_open_deb']+chk_6['rep_period_deb'])),main_data)
															worksheet.write_string (row, col+8,str("{0:.2f}".format(chk_6['rep_open_cre']+chk_6['rep_period_cre'])),main_data)

															# debit_close = chk_6['rep_open_deb']+chk_6['rep_period_deb']
															# credit_close = chk_6['rep_open_cre']+chk_6['rep_period_cre']
															# if debit_close > credit_close:
															# 	debit_bal = debit_close - credit_close
															# if  credit_close > debit_close:
															# 	credit_bal = credit_close - debit_close

															worksheet.write_string (row, col+9,str("{0:.2f}".format(chk_6['close_debit_bal'])),main_data)
															worksheet.write_string (row, col+10,str("{0:.2f}".format(chk_6['close_cre_bal'])),main_data)

															# deb7 = deb7 + debit_bal
															# deb8 = deb8 + credit_bal

															row += 1
															col = 0

			loc = 'A'+str(row+1)
			loc1 = 'C'+str(row+1)
			loc15 = 'D'+str(row+1)
			loc30 = 'E'+str(row+1)
			loc45 = 'F'+str(row+1)
			loc60 = 'G'+str(row+1)
			loc75 = 'H'+str(row+1)
			loc90 = 'I'+str(row+1)
			loc91 = 'J'+str(row+1)
			loc92 = 'K'+str(row+1)

			end_loc = str(loc)+':'+str(loc1)
			worksheet.merge_range(str(end_loc), 'Total' ,main_heading)
			worksheet.write_string(str(loc15),str("{0:.2f}".format(deb1)),main_heading1)
			worksheet.write_string(str(loc30),str("{0:.2f}".format(deb2)),main_heading1)
			worksheet.write_string(str(loc45),str("{0:.2f}".format(deb3)),main_heading1)
			worksheet.write_string(str(loc60),str("{0:.2f}".format(deb4)),main_heading1)
			worksheet.write_string(str(loc75),str("{0:.2f}".format(deb5)),main_heading1)
			worksheet.write_string(str(loc90),str("{0:.2f}".format(deb6)),main_heading1)
			worksheet.write_string(str(loc91),str("{0:.2f}".format(deb7)),main_heading1)
			worksheet.write_string(str(loc92),str("{0:.2f}".format(deb8)),main_heading1)


		


