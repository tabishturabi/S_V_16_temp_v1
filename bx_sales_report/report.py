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


class BxSalesReportXlsx(models.TransientModel):
	_name = 'report.bx_sales_report.bx_sales_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'

	# @api.multi
	def generate_xlsx_report(self, workbook, input_records, lines):
		data = input_records['form']

		table_name = "transport_management"
		self.env.cr.execute("select id,order_date,payment_method,state,total_amount,form_transport,to_transport,create_uid,customer,transportation_no,total_before_taxes,tax_amount FROM "+table_name+" ")
		result = self._cr.fetchall()
		transport_lines = pd.DataFrame(list(result))
		transport_lines = transport_lines.rename(columns={0: 'self_id',1: 'order_date',2: 'payment_method',3: 'state',4: 'total_amount',5: 'form_transport',6: 'to_transport',7: 'create_uid',8: 'customer',9: 'transportation_no',10: 'total_before_taxes',11: 'tax_amount'})

		bsg_customer_table = "res_partner"
		self.env.cr.execute("select id,name FROM "+bsg_customer_table+" ")
		result_bsg_customer = self._cr.fetchall()
		bsg_customer_frame = pd.DataFrame(list(result_bsg_customer))
		bsg_customer_frame = bsg_customer_frame.rename(columns={0: 'bsg_customer_id',1: 'bsg_customer_name'})
		transport_lines = pd.merge(transport_lines,bsg_customer_frame,  how='left', left_on='customer', right_on ='bsg_customer_id')

		payment_frame_table = "cargo_payment_method"
		self.env.cr.execute("select id,payment_method_name FROM "+payment_frame_table+" ")
		result_payment_frame = self._cr.fetchall()
		payment_frame = pd.DataFrame(list(result_payment_frame))
		payment_frame = payment_frame.rename(columns={0: 'bsg_pay_method_id',1: 'bsg_pay_method_name'})
		transport_lines = pd.merge(transport_lines,payment_frame,  how='left', left_on='payment_method', right_on ='bsg_pay_method_id')

		loc_from_frame_table = "bsg_route_waypoints"
		self.env.cr.execute("select id,route_waypoint_name FROM "+loc_from_frame_table+" ")
		result_loc_from_frame = self._cr.fetchall()
		loc_from_frame = pd.DataFrame(list(result_loc_from_frame))
		loc_from_frame = loc_from_frame.rename(columns={0: 'bsg_loc_from_id',1: 'bsg_loc_from_name'})
		transport_lines = pd.merge(transport_lines,loc_from_frame,  how='left', left_on='form_transport', right_on ='bsg_loc_from_id')

		loc_to_frame_table = "bsg_route_waypoints"
		self.env.cr.execute("select id,route_waypoint_name FROM "+loc_to_frame_table+" ")
		result_loc_to_frame = self._cr.fetchall()
		loc_to_frame = pd.DataFrame(list(result_loc_to_frame))
		loc_to_frame = loc_to_frame.rename(columns={0: 'bsg_loc_to_id',1: 'bsg_loc_to_name'})
		transport_lines = pd.merge(transport_lines,loc_to_frame,  how='left', left_on='to_transport', right_on ='bsg_loc_to_id')


		transport_lines = transport_lines.loc[(transport_lines['state'] != 'cancel')]

		if data['state']:
			transport_lines = transport_lines.loc[(transport_lines['state'] == data['state'])]

		if data['customer_ids']:
			transport_lines = transport_lines.loc[(transport_lines['customer'].isin(data['customer_ids']))]

		if data['branch_ids']:
			branch_ids = []
			for x in data['branch_ids']:
				way_points = self.env['bsg_route_waypoints'].search([('loc_branch_id.id','=',x)],limit=1)
				if way_points:
					branch_ids.append(way_points.id)

			transport_lines = transport_lines.loc[(transport_lines['form_transport'].isin(branch_ids))]

		if data['branch_ids_to']:
			transport_lines = transport_lines.loc[(transport_lines['to_transport'].isin(data['branch_ids_to']))]

		if data['users']:
			transport_lines = transport_lines.loc[(transport_lines['create_uid'].isin(data['users']))]

		if data['payment_method_ids']:
			transport_lines = transport_lines.loc[(transport_lines['payment_method'].isin(data['payment_method_ids']))]

		if data['from_bx'] and data['to_bx']:
			from_bx = int(data['from_bx'][0])
			to_bx = int(data['to_bx'][0])

			transport_lines = transport_lines.loc[(transport_lines['self_id'] >= from_bx) & (transport_lines['self_id'] <= to_bx)]

		transport_lines['date'] = transport_lines['order_date'].astype(str)
		transport_lines['counter'] = 1

		if data['date_type'] == "is equal to":
			transport_lines = transport_lines.loc[(transport_lines['date'] == (data['date']))]
		if data['date_type'] == "is not equal to":
			transport_lines = transport_lines.loc[(transport_lines['date'] != data['date'])]
		if data['date_type'] == "is after":
			transport_lines = transport_lines.loc[(transport_lines['date'] > data['date'])]
		if data['date_type'] == "is before":
			transport_lines = transport_lines.loc[(transport_lines['date'] < data['date'])]
		if data['date_type'] == "is after or equal to":
			transport_lines = transport_lines.loc[(transport_lines['date'] >= data['date'])]
		if data['date_type'] == "is before or equal to":
			transport_lines = transport_lines.loc[(transport_lines['date'] <= data['date'])]
		if data['date_type'] == "is between":
			transport_lines = transport_lines.loc[(transport_lines['date'] >= data['form']) & (transport_lines['date'] <= data['to'])]
		if data['date_type'] == "is set":
			transport_lines = transport_lines.loc[(transport_lines.order_date.notnull())]
		if data['date_type'] == "is not set":
			transport_lines = transport_lines.loc[(transport_lines.order_date.isnull())]
		
	
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
		worksheet = workbook.add_worksheet('Bx Sales Report')

		letters = list(string.ascii_uppercase)


		if data['report_mode'] == 'Bx Sales Detail Report':

			worksheet.merge_range('A1:J1',"Bx Sales Details Report",merge_format)
			worksheet.merge_range('A2:J2',"تقرير تفصيلي لمبيعات نقل البضائع",merge_format)

			worksheet.write('A4', 'رقم الرحلة', main_heading1)
			worksheet.write('B4', 'التاريخ', main_heading1)
			worksheet.write('C4',  'اسم العميل', main_heading1)
			worksheet.write('D4',  'طريقة الدفع', main_heading1)
			worksheet.write('E4',  'فرع الشحن', main_heading1)
			worksheet.write('F4',  'فرع الوصول', main_heading1)
			worksheet.write('G4',  'قيمة الاتفاقية الضريبة', main_heading1)
			worksheet.write('H4',  'أجمالي الضريبة', main_heading1)
			worksheet.write('I4',  'اجمالي الاتفاقية', main_heading1)
			worksheet.write('J4',  'الحالة', main_heading1)
			
			worksheet.write('A5',  'Bx Agreement', main_heading1)
			worksheet.write('B5',  'Date', main_heading1)
			worksheet.write('C5',  'Customer Name', main_heading1)
			worksheet.write('D5',  'Payment Method', main_heading1)
			worksheet.write('E5',  'From Branch', main_heading1)
			worksheet.write('F5',  'To Branch', main_heading1)
			worksheet.write('G5',  'Total Invoice Amt Before Tax', main_heading1)
			worksheet.write('H5',  'Total Tax Amt', main_heading1)
			worksheet.write('I5',  'Total Invoice Amt', main_heading1)
			worksheet.write('J5',  'State', main_heading1)
			
			worksheet.set_column('A:AB', 15)


			tot_b_t = 0
			tot_t = 0
			tot_amt = 0
			

			row = 5
			col = 0
			transport_lines = transport_lines.sort_values(by='order_date')
			for index,rec in transport_lines.iterrows():

				worksheet.write_string (row, col+0,str(rec['transportation_no']),main_data)
				worksheet.write_string (row, col+1,str(rec['order_date']),main_data)
				worksheet.write_string (row, col+2,str(rec['bsg_customer_name']),main_data)
				worksheet.write_string (row, col+3,str(rec['bsg_pay_method_name']),main_data)
				worksheet.write_string (row, col+4,str(rec['bsg_loc_from_name']),main_data)
				worksheet.write_string (row, col+5,str(rec['bsg_loc_to_name']),main_data)
				worksheet.write_string (row, col+6,str(rec['total_before_taxes']),main_data)
				worksheet.write_string (row, col+7,str(rec['tax_amount']),main_data)
				worksheet.write_string (row, col+8,str(rec['total_amount']),main_data)
				worksheet.write_string (row, col+9,str(rec['state']),main_data)

				tot_b_t = tot_b_t + rec['total_before_taxes']
				tot_t = tot_t + rec['tax_amount']
				tot_amt = tot_amt + rec['total_amount']
			
				row+=1

			loc = 'A'+str(row+1)
			loc1 = 'F'+str(row+1)
			loc2 = 'G'+str(row+1)
			loc3 = 'H'+str(row+1)
			loc4 = 'I'+str(row+1)
			loc5 = 'J'+str(row+1)
				
			end_loc = str(loc)+':'+str(loc1)
			worksheet.merge_range(str(end_loc), 'Grand Total' ,main_heading)
			worksheet.write_string(str(loc2),str("{0:.2f}".format(tot_b_t)),main_heading1)
			worksheet.write_string(str(loc3),str("{0:.2f}".format(tot_t)),main_heading1)
			worksheet.write_string(str(loc4),str("{0:.2f}".format(tot_amt)),main_heading1)
			worksheet.write_string(str(loc5),str(" "),main_heading1)

		if data['report_mode'] == 'Bx Branch Sales Summary Report':

			worksheet.merge_range('A1:J1',"Bx Branch Sales Summary Report",merge_format)
			worksheet.merge_range('A2:J2',"تقرير اجمالي إيرادات نقل البضاع بحسب الفروع",merge_format)

			
			unique_branch = transport_lines.form_transport.unique()

			worksheet.write('A4', 'اسم الفرع', main_heading1)
			worksheet.write('B4', 'قيمه اتفاقيات مرحله', main_heading1)
			worksheet.write('C4',  'عدد اتفاقيات مرحله', main_heading1)
			worksheet.write('D4',  'قيمه اتفاقيات غير مرحله', main_heading1)
			worksheet.write('E4',  'عدد اتفاقيات غير مرحله', main_heading1)
			worksheet.write('F4',  'اجمالي عدد اتفاقيات الشحن', main_heading1)
			worksheet.write('G4',  'اجمالي قيمه الاتفاقيات', main_heading1)
			worksheet.write('H4',  'المستهدف الشهري', main_heading1)
			worksheet.write('I4',  'نسبه تحقيق المستهدف', main_heading1)
			
			worksheet.write('A5',  'Branch Name', main_heading1)
			worksheet.write('B5',  'Tot Invoice Amt Before Tax Posted', main_heading1)
			worksheet.write('C5',  'No. Bx Agreement Posted', main_heading1)
			worksheet.write('D5',  'Tot Invoice Amt Before Tax Unposted', main_heading1)
			worksheet.write('E5',  'No. Bx Agreement Unposted', main_heading1)
			worksheet.write('F5',  'Total No. for Agreements', main_heading1)
			worksheet.write('G5',  'Total Amt for Agreements', main_heading1)
			worksheet.write('H5',  'Sales Target', main_heading1)
			worksheet.write('I5',  '% Sales Target', main_heading1)
			
			worksheet.set_column('A:AB', 15)


			tot_pos_num = 0
			tot_pos_amt = 0
			tot_unpos_num = 0
			tot_unpos_amt = 0
			tot_num = 0
			tot_amt = 0
			

			row = 5
			col = 0
			for rec in unique_branch:

				branch_data = self.env['bsg_route_waypoints'].search([('id','=',int(rec))],limit=1)
				branch_name = branch_data.route_waypoint_name

				posted_data = transport_lines.loc[(transport_lines['state'].isin(['fuel_voucher','receive_pod','done'])) & (transport_lines['form_transport'] == rec)]
				posted_data = posted_data.groupby(['form_transport'],as_index = False).sum()
				posted_amt = 0
				posted_numz = 0
				if len(posted_data) > 0:
					for index,line in posted_data.iterrows():
						posted_amt = line['total_before_taxes']
						posted_numz = line['counter']


				unposted_data = transport_lines.loc[(transport_lines['state'].isin(['confirm','issue_bill','vendor_trip'])) & (transport_lines['form_transport'] == rec)]
				unposted_data = unposted_data.groupby(['form_transport'],as_index = False).sum()
				unposted_amt = 0
				unposted_numz = 0
				if len(unposted_data) > 0:
					for index,line in unposted_data.iterrows():
						unposted_amt = line['total_before_taxes']
						unposted_numz = line['counter']


				all_data = transport_lines.loc[(transport_lines['form_transport'] == rec)]
				all_data = all_data.groupby(['form_transport'],as_index = False).sum()
				all_amt = 0
				all_numz = 0
				if len(all_data) > 0:
					for index,line in all_data.iterrows():
						all_amt = line['total_before_taxes']
						all_numz = line['counter']


				worksheet.write_string (row, col+0,str(branch_name),main_data)
				worksheet.write_string (row, col+1,str(posted_amt),main_data)
				worksheet.write_string (row, col+2,str(posted_numz),main_data)
				worksheet.write_string (row, col+3,str(unposted_amt),main_data)
				worksheet.write_string (row, col+4,str(unposted_numz),main_data)
				worksheet.write_string (row, col+5,str(all_amt),main_data)
				worksheet.write_string (row, col+6,str(all_numz),main_data)
				worksheet.write_string (row, col+7,str(''),main_data)
				worksheet.write_string (row, col+8,str(''),main_data)

				tot_pos_amt = tot_pos_amt + posted_amt
				tot_pos_num = tot_pos_num + posted_numz
				tot_unpos_amt = tot_unpos_amt + unposted_amt
				tot_unpos_num = tot_unpos_num + unposted_numz
				tot_amt = tot_amt + (all_amt)
				tot_num = tot_num + (all_numz)
			
				row+=1

			loc = 'A'+str(row+1)
			loc1 = 'B'+str(row+1)
			loc2 = 'C'+str(row+1)
			loc3 = 'D'+str(row+1)
			loc4 = 'E'+str(row+1)
			loc5 = 'F'+str(row+1)
			loc6 = 'G'+str(row+1)
			loc7 = 'H'+str(row+1)
			loc8 = 'I'+str(row+1)
				
			worksheet.write_string(str(loc),str("Grand Total"),main_heading1)
			worksheet.write_string(str(loc1),str("{0:.2f}".format(tot_pos_amt)),main_heading1)
			worksheet.write_string(str(loc2),str("{0:.2f}".format(tot_pos_num)),main_heading1)
			worksheet.write_string(str(loc3),str("{0:.2f}".format(tot_unpos_amt)),main_heading1)
			worksheet.write_string(str(loc4),str("{0:.2f}".format(tot_unpos_num)),main_heading1)
			worksheet.write_string(str(loc5),str("{0:.2f}".format(tot_amt)),main_heading1)
			worksheet.write_string(str(loc6),str("{0:.2f}".format(tot_num)),main_heading1)
			worksheet.write_string(str(loc7),str(" "),main_heading1)
			worksheet.write_string(str(loc8),str(" "),main_heading1)

		if data['report_mode'] == 'Bx User Sales Summary Report':

			worksheet.merge_range('A1:J1',"Bx User Sales Summary Report",merge_format)
			worksheet.merge_range('A2:J2',"تقرير اجمالي إيرادات نقل البضاع بحسب المستخدم",merge_format)

			
			unique_users = transport_lines.create_uid.unique()

			worksheet.write('A4', 'اسم المستخدم', main_heading1)
			worksheet.write('B4', 'قيمه اتفاقيات مرحله', main_heading1)
			worksheet.write('C4',  'عدد اتفاقيات مرحله', main_heading1)
			worksheet.write('D4',  'قيمه اتفاقيات غير مرحله', main_heading1)
			worksheet.write('E4',  'عدد اتفاقيات غير مرحله', main_heading1)
			worksheet.write('F4',  'اجمالي عدد اتفاقيات الشحن', main_heading1)
			worksheet.write('G4',  'اجمالي قيمه الاتفاقيات', main_heading1)
			worksheet.write('H4',  'المستهدف الشهري', main_heading1)
			worksheet.write('I4',  'نسبه تحقيق المستهدف', main_heading1)
			
			worksheet.write('A5',  'User Name', main_heading1)
			worksheet.write('B5',  'Tot Invoice Amt Before Tax Posted', main_heading1)
			worksheet.write('C5',  'No. Bx Agreement Posted', main_heading1)
			worksheet.write('D5',  'Tot Invoice Amt Before Tax Unposted', main_heading1)
			worksheet.write('E5',  'No. Bx Agreement Unposted', main_heading1)
			worksheet.write('F5',  'Total No. for Agreements', main_heading1)
			worksheet.write('G5',  'Total Amt for Agreements', main_heading1)
			worksheet.write('H5',  'Sales Target', main_heading1)
			worksheet.write('I5',  '% Sales Target', main_heading1)
			
			worksheet.set_column('A:AB', 15)


			tot_pos_num = 0
			tot_pos_amt = 0
			tot_unpos_num = 0
			tot_unpos_amt = 0
			tot_num = 0
			tot_amt = 0
			

			row = 5
			col = 0
			for rec in unique_users:

				user_data = self.env['res.users'].search([('id','=',int(rec))],limit=1)
				user_name = user_data.name

				posted_data = transport_lines.loc[(transport_lines['state'].isin(['fuel_voucher','receive_pod','done'])) & (transport_lines['create_uid'] == rec)]
				posted_data = posted_data.groupby(['create_uid'],as_index = False).sum()
				posted_amt = 0
				posted_numz = 0
				if len(posted_data) > 0:
					for index,line in posted_data.iterrows():
						posted_amt = line['total_before_taxes']
						posted_numz = line['counter']


				unposted_data = transport_lines.loc[(transport_lines['state'].isin(['confirm','issue_bill','vendor_trip'])) & (transport_lines['create_uid'] == rec)]
				unposted_data = unposted_data.groupby(['create_uid'],as_index = False).sum()
				unposted_amt = 0
				unposted_numz = 0
				if len(unposted_data) > 0:
					for index,line in unposted_data.iterrows():
						unposted_amt = line['total_before_taxes']
						unposted_numz = line['counter']

				all_data = transport_lines.loc[(transport_lines['create_uid'] == rec)]
				all_data = all_data.groupby(['create_uid'],as_index = False).sum()
				all_amt = 0
				all_numz = 0
				if len(all_data) > 0:
					for index,line in all_data.iterrows():
						all_amt = line['total_before_taxes']
						all_numz = line['counter']

				worksheet.write_string (row, col+0,str(user_name),main_data)
				worksheet.write_string (row, col+1,str(posted_amt),main_data)
				worksheet.write_string (row, col+2,str(posted_numz),main_data)
				worksheet.write_string (row, col+3,str(unposted_amt),main_data)
				worksheet.write_string (row, col+4,str(unposted_numz),main_data)
				worksheet.write_string (row, col+5,str(all_amt),main_data)
				worksheet.write_string (row, col+6,str(all_numz),main_data)
				worksheet.write_string (row, col+7,str(''),main_data)
				worksheet.write_string (row, col+8,str(''),main_data)

				tot_pos_amt = tot_pos_amt + posted_amt
				tot_pos_num = tot_pos_num + posted_numz
				tot_unpos_amt = tot_unpos_amt + unposted_amt
				tot_unpos_num = tot_unpos_num + unposted_numz
				tot_amt = tot_amt + all_amt
				tot_num = tot_num + all_numz
			
				row+=1

			loc = 'A'+str(row+1)
			loc1 = 'B'+str(row+1)
			loc2 = 'C'+str(row+1)
			loc3 = 'D'+str(row+1)
			loc4 = 'E'+str(row+1)
			loc5 = 'F'+str(row+1)
			loc6 = 'G'+str(row+1)
			loc7 = 'H'+str(row+1)
			loc8 = 'I'+str(row+1)
				
			worksheet.write_string(str(loc),str("Grand Total"),main_heading1)
			worksheet.write_string(str(loc1),str("{0:.2f}".format(tot_pos_amt)),main_heading1)
			worksheet.write_string(str(loc2),str("{0:.2f}".format(tot_pos_num)),main_heading1)
			worksheet.write_string(str(loc3),str("{0:.2f}".format(tot_unpos_amt)),main_heading1)
			worksheet.write_string(str(loc4),str("{0:.2f}".format(tot_unpos_num)),main_heading1)
			worksheet.write_string(str(loc5),str("{0:.2f}".format(tot_amt)),main_heading1)
			worksheet.write_string(str(loc6),str("{0:.2f}".format(tot_num)),main_heading1)
			worksheet.write_string(str(loc7),str(" "),main_heading1)
			worksheet.write_string(str(loc8),str(" "),main_heading1)

		if data['report_mode'] == 'Bx Customer Sales Summary Report':

			worksheet.merge_range('A1:J1',"Bx Customer Sales Summary Report",merge_format)
			worksheet.merge_range('A2:J2',"تقرير اجمالي إيرادات نقل البضاع بحسب العميل",merge_format)

			
			unique_cust = transport_lines.customer.unique()

			worksheet.write('A4', 'اسم العميل', main_heading1)
			worksheet.write('B4', 'قيمه اتفاقيات مرحله', main_heading1)
			worksheet.write('C4',  'عدد اتفاقيات مرحله', main_heading1)
			worksheet.write('D4',  'قيمه اتفاقيات غير مرحله', main_heading1)
			worksheet.write('E4',  'عدد اتفاقيات غير مرحله', main_heading1)
			worksheet.write('F4',  'اجمالي عدد اتفاقيات الشحن', main_heading1)
			worksheet.write('G4',  'اجمالي قيمه الاتفاقيات', main_heading1)
			worksheet.write('H4',  'المستهدف الشهري', main_heading1)
			worksheet.write('I4',  'نسبه تحقيق المستهدف', main_heading1)
			
			worksheet.write('A5',  'Customer Name', main_heading1)
			worksheet.write('B5',  'Tot Invoice Amt Before Tax Posted', main_heading1)
			worksheet.write('C5',  'No. Bx Agreement Posted', main_heading1)
			worksheet.write('D5',  'Tot Invoice Amt Before Tax Unposted', main_heading1)
			worksheet.write('E5',  'No. Bx Agreement Unposted', main_heading1)
			worksheet.write('F5',  'Total No. for Agreements', main_heading1)
			worksheet.write('G5',  'Total Amt for Agreements', main_heading1)
			worksheet.write('H5',  'Sales Target', main_heading1)
			worksheet.write('I5',  '% Sales Target', main_heading1)
			
			worksheet.set_column('A:AB', 15)


			tot_pos_num = 0
			tot_pos_amt = 0
			tot_unpos_num = 0
			tot_unpos_amt = 0
			tot_num = 0
			tot_amt = 0
			

			row = 5
			col = 0
			for rec in unique_cust:

				cust_data = self.env['res.partner'].search([('id','=',int(rec))],limit=1)
				cust_name = cust_data.name

				posted_data = transport_lines.loc[(transport_lines['state'].isin(['fuel_voucher','receive_pod','done'])) & (transport_lines['customer'] == rec)]
				posted_data = posted_data.groupby(['customer'],as_index = False).sum()
				posted_amt = 0
				posted_numz = 0
				if len(posted_data) > 0:
					for index,line in posted_data.iterrows():
						posted_amt = line['total_before_taxes']
						posted_numz = line['counter']


				unposted_data = transport_lines.loc[(transport_lines['state'].isin(['confirm','issue_bill','vendor_trip'])) & (transport_lines['customer'] == rec)]
				unposted_data = unposted_data.groupby(['customer'],as_index = False).sum()
				unposted_amt = 0
				unposted_numz = 0
				if len(unposted_data) > 0:
					for index,line in unposted_data.iterrows():
						unposted_amt = line['total_before_taxes']
						unposted_numz = line['counter']


				all_data = transport_lines.loc[(transport_lines['customer'] == rec)]
				all_data = all_data.groupby(['customer'],as_index = False).sum()
				all_amt = 0
				all_numz = 0
				if len(all_data) > 0:
					for index,line in all_data.iterrows():
						all_amt = line['total_before_taxes']
						all_numz = line['counter']

				worksheet.write_string (row, col+0,str(cust_name),main_data)
				worksheet.write_string (row, col+1,str(posted_amt),main_data)
				worksheet.write_string (row, col+2,str(posted_numz),main_data)
				worksheet.write_string (row, col+3,str(unposted_amt),main_data)
				worksheet.write_string (row, col+4,str(unposted_numz),main_data)
				worksheet.write_string (row, col+5,str(all_amt),main_data)
				worksheet.write_string (row, col+6,str(all_numz),main_data)
				worksheet.write_string (row, col+7,str(''),main_data)
				worksheet.write_string (row, col+8,str(''),main_data)

				tot_pos_amt = tot_pos_amt + posted_amt
				tot_pos_num = tot_pos_num + posted_numz
				tot_unpos_amt = tot_unpos_amt + unposted_amt
				tot_unpos_num = tot_unpos_num + unposted_numz
				tot_amt = tot_amt + all_amt
				tot_num = tot_num + all_numz
			
				row+=1

			loc = 'A'+str(row+1)
			loc1 = 'B'+str(row+1)
			loc2 = 'C'+str(row+1)
			loc3 = 'D'+str(row+1)
			loc4 = 'E'+str(row+1)
			loc5 = 'F'+str(row+1)
			loc6 = 'G'+str(row+1)
			loc7 = 'H'+str(row+1)
			loc8 = 'I'+str(row+1)
				
			worksheet.write_string(str(loc),str("Grand Total"),main_heading1)
			worksheet.write_string(str(loc1),str("{0:.2f}".format(tot_pos_amt)),main_heading1)
			worksheet.write_string(str(loc2),str("{0:.2f}".format(tot_pos_num)),main_heading1)
			worksheet.write_string(str(loc3),str("{0:.2f}".format(tot_unpos_amt)),main_heading1)
			worksheet.write_string(str(loc4),str("{0:.2f}".format(tot_unpos_num)),main_heading1)
			worksheet.write_string(str(loc5),str("{0:.2f}".format(tot_amt)),main_heading1)
			worksheet.write_string(str(loc6),str("{0:.2f}".format(tot_num)),main_heading1)
			worksheet.write_string(str(loc7),str(" "),main_heading1)
			worksheet.write_string(str(loc8),str(" "),main_heading1)

		if data['report_mode'] == 'Bx Period Sales Summary Report':

			if data['period_group'] == 'day':

				worksheet.merge_range('A1:J1',"Bx Period Sales Summary Report By Day",merge_format)
				worksheet.merge_range('A2:J2',"تقرير اجمالي إيرادات نقل البضاع بحسب اليوم",merge_format)

				transport_lines = transport_lines.sort_values(by='order_date')
				unique_date = transport_lines.date.unique()

				worksheet.write('A4', 'التاريخ', main_heading1)
				worksheet.write('B4', 'قيمه اتفاقيات مرحله', main_heading1)
				worksheet.write('C4',  'عدد اتفاقيات مرحله', main_heading1)
				worksheet.write('D4',  'قيمه اتفاقيات غير مرحله', main_heading1)
				worksheet.write('E4',  'عدد اتفاقيات غير مرحله', main_heading1)
				worksheet.write('F4',  'اجمالي عدد اتفاقيات الشحن', main_heading1)
				worksheet.write('G4',  'اجمالي قيمه الاتفاقيات', main_heading1)
				worksheet.write('H4',  'المستهدف الشهري', main_heading1)
				worksheet.write('I4',  'نسبه تحقيق المستهدف', main_heading1)
				
				worksheet.write('A5',  'Date', main_heading1)
				worksheet.write('B5',  'Tot Invoice Amt Before Tax Posted', main_heading1)
				worksheet.write('C5',  'No. Bx Agreement Posted', main_heading1)
				worksheet.write('D5',  'Tot Invoice Amt Before Tax Unposted', main_heading1)
				worksheet.write('E5',  'No. Bx Agreement Unposted', main_heading1)
				worksheet.write('F5',  'Total No. for Agreements', main_heading1)
				worksheet.write('G5',  'Total Amt for Agreements', main_heading1)
				worksheet.write('H5',  'Sales Target', main_heading1)
				worksheet.write('I5',  '% Sales Target', main_heading1)
				
				worksheet.set_column('A:AB', 15)


				tot_pos_num = 0
				tot_pos_amt = 0
				tot_unpos_num = 0
				tot_unpos_amt = 0
				tot_num = 0
				tot_amt = 0
				

				row = 5
				col = 0
				for rec in unique_date:

					# cust_data = self.env['res.partner'].search([('id','=',int(rec))],limit=1)
					# cust_name = cust_data.name

					posted_data = transport_lines.loc[(transport_lines['state'].isin(['fuel_voucher','receive_pod','done'])) & (transport_lines['date'] == rec)]
					posted_data = posted_data.groupby(['date'],as_index = False).sum()
					posted_amt = 0
					posted_numz = 0
					if len(posted_data) > 0:
						for index,line in posted_data.iterrows():
							posted_amt = line['total_before_taxes']
							posted_numz = line['counter']


					unposted_data = transport_lines.loc[(transport_lines['state'].isin(['confirm','issue_bill','vendor_trip'])) & (transport_lines['date'] == rec)]
					unposted_data = unposted_data.groupby(['date'],as_index = False).sum()
					unposted_amt = 0
					unposted_numz = 0
					if len(unposted_data) > 0:
						for index,line in unposted_data.iterrows():
							unposted_amt = line['total_before_taxes']
							unposted_numz = line['counter']

					all_data = transport_lines.loc[(transport_lines['date'] == rec)]
					all_data = all_data.groupby(['date'],as_index = False).sum()
					all_amt = 0
					all_numz = 0
					if len(all_data) > 0:
						for index,line in all_data.iterrows():
							all_amt = line['total_before_taxes']
							all_numz = line['counter']

					worksheet.write_string (row, col+0,str(rec),main_data)
					worksheet.write_string (row, col+1,str(posted_amt),main_data)
					worksheet.write_string (row, col+2,str(posted_numz),main_data)
					worksheet.write_string (row, col+3,str(unposted_amt),main_data)
					worksheet.write_string (row, col+4,str(unposted_numz),main_data)
					worksheet.write_string (row, col+5,str(all_amt),main_data)
					worksheet.write_string (row, col+6,str(all_numz),main_data)
					worksheet.write_string (row, col+7,str(''),main_data)
					worksheet.write_string (row, col+8,str(''),main_data)

					tot_pos_amt = tot_pos_amt + posted_amt
					tot_pos_num = tot_pos_num + posted_numz
					tot_unpos_amt = tot_unpos_amt + unposted_amt
					tot_unpos_num = tot_unpos_num + unposted_numz
					tot_amt = tot_amt + all_amt
					tot_num = tot_num + all_numz
				
					row+=1

				loc = 'A'+str(row+1)
				loc1 = 'B'+str(row+1)
				loc2 = 'C'+str(row+1)
				loc3 = 'D'+str(row+1)
				loc4 = 'E'+str(row+1)
				loc5 = 'F'+str(row+1)
				loc6 = 'G'+str(row+1)
				loc7 = 'H'+str(row+1)
				loc8 = 'I'+str(row+1)
					
				worksheet.write_string(str(loc),str("Grand Total"),main_heading1)
				worksheet.write_string(str(loc1),str("{0:.2f}".format(tot_pos_amt)),main_heading1)
				worksheet.write_string(str(loc2),str("{0:.2f}".format(tot_pos_num)),main_heading1)
				worksheet.write_string(str(loc3),str("{0:.2f}".format(tot_unpos_amt)),main_heading1)
				worksheet.write_string(str(loc4),str("{0:.2f}".format(tot_unpos_num)),main_heading1)
				worksheet.write_string(str(loc5),str("{0:.2f}".format(tot_amt)),main_heading1)
				worksheet.write_string(str(loc6),str("{0:.2f}".format(tot_num)),main_heading1)
				worksheet.write_string(str(loc7),str(" "),main_heading1)
				worksheet.write_string(str(loc8),str(" "),main_heading1)

			if data['period_group'] == 'month':

				worksheet.merge_range('A1:J1',"Bx Period Sales Summary Report By Month",merge_format)
				worksheet.merge_range('A2:J2',"تقرير اجمالي إيرادات نقل البضاع بحسب الشهر",merge_format)

				transport_lines['month_date'] = transport_lines['date'].astype(str).str[:7]
				unique_month = transport_lines.month_date.unique()

				worksheet.write('A4', 'التاريخ', main_heading1)
				worksheet.write('B4', 'قيمه اتفاقيات مرحله', main_heading1)
				worksheet.write('C4',  'عدد اتفاقيات مرحله', main_heading1)
				worksheet.write('D4',  'قيمه اتفاقيات غير مرحله', main_heading1)
				worksheet.write('E4',  'عدد اتفاقيات غير مرحله', main_heading1)
				worksheet.write('F4',  'اجمالي عدد اتفاقيات الشحن', main_heading1)
				worksheet.write('G4',  'اجمالي قيمه الاتفاقيات', main_heading1)
				worksheet.write('H4',  'المستهدف الشهري', main_heading1)
				worksheet.write('I4',  'نسبه تحقيق المستهدف', main_heading1)
				
				worksheet.write('A5',  'Date', main_heading1)
				worksheet.write('B5',  'Tot Invoice Amt Before Tax Posted', main_heading1)
				worksheet.write('C5',  'No. Bx Agreement Posted', main_heading1)
				worksheet.write('D5',  'Tot Invoice Amt Before Tax Unposted', main_heading1)
				worksheet.write('E5',  'No. Bx Agreement Unposted', main_heading1)
				worksheet.write('F5',  'Total No. for Agreements', main_heading1)
				worksheet.write('G5',  'Total Amt for Agreements', main_heading1)
				worksheet.write('H5',  'Sales Target', main_heading1)
				worksheet.write('I5',  '% Sales Target', main_heading1)
				
				worksheet.set_column('A:AB', 15)


				tot_pos_num = 0
				tot_pos_amt = 0
				tot_unpos_num = 0
				tot_unpos_amt = 0
				tot_num = 0
				tot_amt = 0
				

				row = 5
				col = 0
				for rec in unique_month:

					# cust_data = self.env['res.partner'].search([('id','=',int(rec))],limit=1)
					# cust_name = cust_data.name

					posted_data = transport_lines.loc[(transport_lines['state'].isin(['fuel_voucher','receive_pod','done'])) & (transport_lines['month_date'] == rec)]
					posted_data = posted_data.groupby(['month_date'],as_index = False).sum()
					posted_amt = 0
					posted_numz = 0
					if len(posted_data) > 0:
						for index,line in posted_data.iterrows():
							posted_amt = line['total_before_taxes']
							posted_numz = line['counter']


					unposted_data = transport_lines.loc[(transport_lines['state'].isin(['confirm','issue_bill','vendor_trip'])) & (transport_lines['month_date'] == rec)]
					unposted_data = unposted_data.groupby(['month_date'],as_index = False).sum()
					unposted_amt = 0
					unposted_numz = 0
					if len(unposted_data) > 0:
						for index,line in unposted_data.iterrows():
							unposted_amt = line['total_before_taxes']
							unposted_numz = line['counter']


					all_data = transport_lines.loc[(transport_lines['month_date'] == rec)]
					print (all_data)
					print ("00000000000000")
					all_data = all_data.groupby(['month_date'],as_index = False).sum()
					all_amt = 0
					all_numz = 0
					if len(all_data) > 0:
						for index,line in all_data.iterrows():
							all_amt = line['total_before_taxes']
							all_numz = line['counter']


					worksheet.write_string (row, col+0,str(rec),main_data)
					worksheet.write_string (row, col+1,str(posted_amt),main_data)
					worksheet.write_string (row, col+2,str(posted_numz),main_data)
					worksheet.write_string (row, col+3,str(unposted_amt),main_data)
					worksheet.write_string (row, col+4,str(unposted_numz),main_data)
					worksheet.write_string (row, col+5,str(all_amt),main_data)
					worksheet.write_string (row, col+6,str(all_numz),main_data)
					worksheet.write_string (row, col+7,str(''),main_data)
					worksheet.write_string (row, col+8,str(''),main_data)

					tot_pos_amt = tot_pos_amt + posted_amt
					tot_pos_num = tot_pos_num + posted_numz
					tot_unpos_amt = tot_unpos_amt + unposted_amt
					tot_unpos_num = tot_unpos_num + unposted_numz
					tot_amt = tot_amt + all_amt
					tot_num = tot_num + all_numz
				
					row+=1

				loc = 'A'+str(row+1)
				loc1 = 'B'+str(row+1)
				loc2 = 'C'+str(row+1)
				loc3 = 'D'+str(row+1)
				loc4 = 'E'+str(row+1)
				loc5 = 'F'+str(row+1)
				loc6 = 'G'+str(row+1)
				loc7 = 'H'+str(row+1)
				loc8 = 'I'+str(row+1)
					
				worksheet.write_string(str(loc),str("Grand Total"),main_heading1)
				worksheet.write_string(str(loc1),str("{0:.2f}".format(tot_pos_amt)),main_heading1)
				worksheet.write_string(str(loc2),str("{0:.2f}".format(tot_pos_num)),main_heading1)
				worksheet.write_string(str(loc3),str("{0:.2f}".format(tot_unpos_amt)),main_heading1)
				worksheet.write_string(str(loc4),str("{0:.2f}".format(tot_unpos_num)),main_heading1)
				worksheet.write_string(str(loc5),str("{0:.2f}".format(tot_amt)),main_heading1)
				worksheet.write_string(str(loc6),str("{0:.2f}".format(tot_num)),main_heading1)
				worksheet.write_string(str(loc7),str(" "),main_heading1)
				worksheet.write_string(str(loc8),str(" "),main_heading1)

			if data['period_group'] == 'year':

				worksheet.merge_range('A1:J1',"Bx Period Sales Summary Report By Year",merge_format)
				worksheet.merge_range('A2:J2',"تقرير اجمالي إيرادات نقل البضاع بحسب سنوي",merge_format)

				transport_lines['year_date'] = transport_lines['date'].astype(str).str[:4]
				unique_year = transport_lines.year_date.unique()

				worksheet.write('A4', 'التاريخ', main_heading1)
				worksheet.write('B4', 'قيمه اتفاقيات مرحله', main_heading1)
				worksheet.write('C4',  'عدد اتفاقيات مرحله', main_heading1)
				worksheet.write('D4',  'قيمه اتفاقيات غير مرحله', main_heading1)
				worksheet.write('E4',  'عدد اتفاقيات غير مرحله', main_heading1)
				worksheet.write('F4',  'اجمالي عدد اتفاقيات الشحن', main_heading1)
				worksheet.write('G4',  'اجمالي قيمه الاتفاقيات', main_heading1)
				worksheet.write('H4',  'المستهدف الشهري', main_heading1)
				worksheet.write('I4',  'نسبه تحقيق المستهدف', main_heading1)
				
				worksheet.write('A5',  'Date', main_heading1)
				worksheet.write('B5',  'Tot Invoice Amt Before Tax Posted', main_heading1)
				worksheet.write('C5',  'No. Bx Agreement Posted', main_heading1)
				worksheet.write('D5',  'Tot Invoice Amt Before Tax Unposted', main_heading1)
				worksheet.write('E5',  'No. Bx Agreement Unposted', main_heading1)
				worksheet.write('F5',  'Total No. for Agreements', main_heading1)
				worksheet.write('G5',  'Total Amt for Agreements', main_heading1)
				worksheet.write('H5',  'Sales Target', main_heading1)
				worksheet.write('I5',  '% Sales Target', main_heading1)
				
				worksheet.set_column('A:AB', 15)


				tot_pos_num = 0
				tot_pos_amt = 0
				tot_unpos_num = 0
				tot_unpos_amt = 0
				tot_num = 0
				tot_amt = 0
				

				row = 5
				col = 0
				for rec in unique_year:

					# cust_data = self.env['res.partner'].search([('id','=',int(rec))],limit=1)
					# cust_name = cust_data.name

					posted_data = transport_lines.loc[(transport_lines['state'].isin(['fuel_voucher','receive_pod','done'])) & (transport_lines['year_date'] == rec)]
					posted_data = posted_data.groupby(['year_date'],as_index = False).sum()
					posted_amt = 0
					posted_numz = 0
					if len(posted_data) > 0:
						for index,line in posted_data.iterrows():
							posted_amt = line['total_before_taxes']
							posted_numz = line['counter']


					unposted_data = transport_lines.loc[(transport_lines['state'].isin(['confirm','issue_bill','vendor_trip'])) & (transport_lines['year_date'] == rec)]
					unposted_data = unposted_data.groupby(['year_date'],as_index = False).sum()
					unposted_amt = 0
					unposted_numz = 0
					if len(unposted_data) > 0:
						for index,line in unposted_data.iterrows():
							unposted_amt = line['total_before_taxes']
							unposted_numz = line['counter']


					all_data = transport_lines.loc[(transport_lines['year_date'] == rec)]
					all_data = all_data.groupby(['year_date'],as_index = False).sum()
					all_amt = 0
					all_numz = 0
					if len(all_data) > 0:
						for index,line in all_data.iterrows():
							all_amt = line['total_before_taxes']
							all_numz = line['counter']

					worksheet.write_string (row, col+0,str(rec),main_data)
					worksheet.write_string (row, col+1,str(posted_amt),main_data)
					worksheet.write_string (row, col+2,str(posted_numz),main_data)
					worksheet.write_string (row, col+3,str(unposted_amt),main_data)
					worksheet.write_string (row, col+4,str(unposted_numz),main_data)
					worksheet.write_string (row, col+5,str(all_amt),main_data)
					worksheet.write_string (row, col+6,str(all_numz),main_data)
					worksheet.write_string (row, col+7,str(''),main_data)
					worksheet.write_string (row, col+8,str(''),main_data)

					tot_pos_amt = tot_pos_amt + posted_amt
					tot_pos_num = tot_pos_num + posted_numz
					tot_unpos_amt = tot_unpos_amt + unposted_amt
					tot_unpos_num = tot_unpos_num + unposted_numz
					tot_amt = tot_amt + all_amt
					tot_num = tot_num + all_numz
				
					row+=1

				loc = 'A'+str(row+1)
				loc1 = 'B'+str(row+1)
				loc2 = 'C'+str(row+1)
				loc3 = 'D'+str(row+1)
				loc4 = 'E'+str(row+1)
				loc5 = 'F'+str(row+1)
				loc6 = 'G'+str(row+1)
				loc7 = 'H'+str(row+1)
				loc8 = 'I'+str(row+1)
					
				worksheet.write_string(str(loc),str("Grand Total"),main_heading1)
				worksheet.write_string(str(loc1),str("{0:.2f}".format(tot_pos_amt)),main_heading1)
				worksheet.write_string(str(loc2),str("{0:.2f}".format(tot_pos_num)),main_heading1)
				worksheet.write_string(str(loc3),str("{0:.2f}".format(tot_unpos_amt)),main_heading1)
				worksheet.write_string(str(loc4),str("{0:.2f}".format(tot_unpos_num)),main_heading1)
				worksheet.write_string(str(loc5),str("{0:.2f}".format(tot_amt)),main_heading1)
				worksheet.write_string(str(loc6),str("{0:.2f}".format(tot_num)),main_heading1)
				worksheet.write_string(str(loc7),str(" "),main_heading1)
				worksheet.write_string(str(loc8),str(" "),main_heading1)
			

			

				
			

	
