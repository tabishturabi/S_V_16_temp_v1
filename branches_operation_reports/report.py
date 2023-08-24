import os
import xlsxwriter
from datetime import date
from datetime import date,datetime, timedelta
import datetime
import time
import re
import pandas as pd
import numpy as np
import psycopg2 as pg
import pandas.io.sql as psql
import getpass
from odoo import models, fields, api, tools ,_
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config , ustr
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta
import string
from pytz import timezone, UTC
import babel


class TBsgOptReportXlsx(models.TransientModel):
	_name = 'report.branches_operation_reports.bsg_operations_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'

	# @api.multi
	def generate_xlsx_report(self, workbook, input_records, lines):
		data = input_records['form']
		tz = timezone(self.env.context.get('tz') or self.env.user.tz)
		table_name = "bsg_vehicle_cargo_sale_line"
		self.env.cr.execute("select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,chassis_no,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one,charges_stored, final_price_stored, invoice_state_stored,revenue_type,shipment_type,sale_order_state FROM "+table_name+" ")
		result = self._cr.fetchall()
		bsg_cargo_lines = pd.DataFrame(list(result))
		bsg_cargo_lines = bsg_cargo_lines.rename(columns={0: 'self_id',1: 'order_date',2: 'loc_from_branch_id',3: 'loc_to',4: 'create_uid',5: 'bsg_cargo_sale_id',6: 'payment_method',7: 'customer_id',8: 'chassis_no',9: 'state',10: 'fleet_trip_id',11: 'loc_from',12: 'pickup_loc',13: 'car_model',14: 'year',15: 'car_color',16: 'sale_line_rec_name',17: 'expected_delivery',18: 'add_to_cc',19: 'plate_no',20: 'car_make',21: 'palte_one',22: 'charges_stored',23: 'final_price_stored',24: 'invoice_state_stored',25: 'revenue_type',26: 'shipment_type',27:'sale_order_state'})
		
		#bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['active'] == True)]
		
		bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel')]
		#bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['sale_order_state']).isin(['done','pod','Delivered'])]
		bsg_cargo_lines['month_date'] = (pd.to_datetime(bsg_cargo_lines['order_date']).dt.tz_localize(UTC).dt.tz_convert(tz)).astype(str).str[:7]
		bsg_cargo_lines['counter'] = 1

		
		branch_ids = []
		if data['branch_ids']:
			branch_ids = data['branch_ids']
		else:
			branch_ids = self.env['bsg_branches.bsg_branches'].search([]).ids

		user_ids = []
		if data['users']:
			user_ids = data['users']	
		curr_month = str(str(data['year'][-1])+'-'+str(data['months']))
		get_print_date = fields.Date.from_string(str(data['year'][-1])+'-'+str(data['months']+'-'+'01'))
		print_date = ustr(babel.dates.format_date(date=get_print_date, format='MMMM y', locale='ar'))
		#copy so before month filtter ,to get delivery report , may so line deliver in other month
		bsg_cars_for_deliver = bsg_cargo_lines
		
		bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['month_date'] == curr_month) & (bsg_cargo_lines['loc_from_branch_id'].isin(branch_ids))]
		
		if data['details']:
			if len(user_ids) > 0:
				bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['create_uid'].isin(user_ids))]
		
		history_frame_table = "report_history_delivery"
		self.env.cr.execute("select id,cargo_so_line_id FROM "+history_frame_table+" ")
		result_history_frame_table = self._cr.fetchall()
		history_frame = pd.DataFrame(list(result_history_frame_table))
		history_frame = history_frame.rename(columns={0: 'delivery_id',1: 'cargo_so_line_id'})

		history_frame = history_frame.sort_values(by=['cargo_so_line_id','delivery_id'])
		history_frame = history_frame.drop_duplicates(subset='cargo_so_line_id', keep="last")

		bsg_cargo_lines = pd.merge(bsg_cargo_lines,history_frame,  how='left', left_on='self_id', right_on ='cargo_so_line_id')
		route_frame_table = "bsg_route_waypoints"
		self.env.cr.execute("select id,is_port,is_international,is_internal FROM "+route_frame_table+" ")
		result_route_frame_table = self._cr.fetchall()
		route_frame = pd.DataFrame(list(result_route_frame_table))
		route_frame = route_frame.rename(columns={0: 'loc_to_id',1: 'is_port',2: 'is_international',3: 'is_internal'})

		bsg_cargo_lines = pd.merge(bsg_cargo_lines,route_frame,  how='left', left_on='loc_to', right_on ='loc_to_id')
		shipmwnt_frame_table = "bsg_car_shipment_type"
		self.env.cr.execute("select id,is_normal,is_vip,is_satha FROM "+shipmwnt_frame_table+" ")
		result_shipmwnt_frame_table = self._cr.fetchall()
		shipmwnt_frame = pd.DataFrame(list(result_shipmwnt_frame_table))
		shipmwnt_frame = shipmwnt_frame.rename(columns={0: 'ship_id',1: 'is_normal',2: 'is_vip',3: 'is_satha'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,shipmwnt_frame,  how='left', left_on='shipment_type', right_on ='ship_id')
		trip_frame_table = "fleet_vehicle_trip"
		self.env.cr.execute("select id,trip_type,create_uid FROM "+trip_frame_table+" ")
		result_trip_frame_table = self._cr.fetchall()
		trip_frame = pd.DataFrame(list(result_trip_frame_table))
		trip_frame = trip_frame.rename(columns={0: 'trip_id',1: 'trip_type',2: 'trip_user'})
		trip_frame_data = trip_frame
		trip_frame = trip_frame.loc[(trip_frame['trip_type'] != 'local')]
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,trip_frame,  how='left', left_on='fleet_trip_id', right_on ='trip_id')
		trip_frame_history = "bsg_sale_line_trip_history"
		self.env.cr.execute("select id,trip_type,cargo_sale_line_id FROM "+trip_frame_history+" ")
		result_trip_frame_history = self._cr.fetchall()
		trip_history = pd.DataFrame(list(result_trip_frame_history))
		trip_history = trip_history.rename(columns={0: 'trip_his_id',1: 'trip_his_type',2: 'cargo_sale_line_id'})
		trip_history = trip_history.loc[(trip_history['trip_his_type'] != 'local')]
		trip_history = trip_history.sort_values(by=['cargo_sale_line_id','trip_his_id'])
		trip_history = trip_history.drop_duplicates(subset='cargo_sale_line_id', keep="last")
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,trip_history,  how='left', left_on='self_id', right_on ='cargo_sale_line_id')
		

		bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines.trip_id.notnull()) | (bsg_cargo_lines.cargo_sale_line_id.notnull())]
		bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines.revenue_type.notnull())]
		

		#For Get Count Of Delivery
		self.env.cr.execute("select id,dr_user_id,dr_print_date,cargo_so_line_id FROM "+history_frame_table+" ")
		result_history_report_frame_table = self._cr.fetchall()
		history_report_frame = pd.DataFrame(list(result_history_report_frame_table))
		history_report_frame = history_report_frame.rename(columns={0: 'report_id',1: 'user_id',2:'print_date',3:'cargo_so_line_id'})
		history_report_frame['month_date'] = (pd.to_datetime(history_report_frame['print_date']).dt.tz_localize(UTC).dt.tz_convert(tz)).astype(str).str[:7]
		history_report_frame = history_report_frame.loc[(history_report_frame['month_date'] == curr_month)]
		bicking_table = "fleet_vehicle_trip_pickings"
		self.env.cr.execute("select id,picking_name,active,create_uid FROM "+bicking_table+" ")
		bicking_table_frame_table = self._cr.fetchall()
		bicking_table_frame = pd.DataFrame(list(bicking_table_frame_table))
		bicking_table_frame = bicking_table_frame.rename(columns={0: 'picking_id',1:'cargo_so_line_id',2:'active',3: 'user_id'})
		bicking_table_frame = bicking_table_frame.loc[(bicking_table_frame['active'] == True)]
		
		if not data['details']:
			gr_month_wise = bsg_cargo_lines.groupby(['loc_from_branch_id','revenue_type'],as_index = False).sum()

		else:

			gr_month_wise = bsg_cargo_lines.groupby(['create_uid','revenue_type'],as_index = False).sum()
			gr_pay_wise = bsg_cargo_lines.groupby(['create_uid','payment_method'],as_index = False).sum()



		unique_branch = gr_month_wise.loc_from_branch_id.unique()
		unique_branches = bsg_cargo_lines.loc_from_branch_id.unique()
		#unique_branches = pd.unique(bsg_cargo_lines[['loc_from_branch_id', 'loc_to']].values.ravel('K'))

		# unique_users = gr_month_wise.create_uid.unique()
		unique_type = gr_month_wise.revenue_type.unique()

	
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
		worksheet = workbook.add_worksheet('التقرير  الاول :  تقرير اجمالي ايرادات الفروع الشهريه ')

		letters = list(string.ascii_uppercase)


		if not data['details']:

			worksheet.merge_range('A1:J1',str(" التقرير  الاول :  تقرير اجمالي ايرادات الفروع الشهريه "+ "/" +  print_date),merge_format)
			worksheet.write('A3', 'نسبه تحقيق المستهدف', main_heading)
			worksheet.write('B3', 'المستهدف', main_heading)
			worksheet.merge_range('C3:D3','الاجمالي',main_heading)
			worksheet.merge_range('E3:F3','ايرادات الشركات',main_heading)
			worksheet.merge_range('G3:H3','ايرادات الافراد',main_heading)
			worksheet.write('J3', 'اسم الفرع', main_heading)
			worksheet.write('I3', 'كود الفرع', main_heading)
			worksheet.write('A4', '', main_heading1)
			worksheet.write('B4', '', main_heading1)
			worksheet.write('C4', 'القيمه', main_heading1)
			worksheet.write('D4', 'عدد الاتفاقيات', main_heading1)
			worksheet.write('E4', 'القيمه', main_heading1)
			worksheet.write('F4', 'عدد الاتفاقيات', main_heading1)
			worksheet.write('G4', 'القيمه', main_heading1)
			worksheet.write('H4', 'عدد الاتفاقيات', main_heading1)
			worksheet.write('I4', '', main_heading1)
			worksheet.write('J4', '', main_heading1)
			
			

			worksheet.set_column('A:J', 13)

			tot_target = 0
			tot_g_amt = 0
			tot_g_numz = 0
			inv_g_amt = 0
			inv_g_numz = 0
			cop_g_amt = 0
			cop_g_numz = 0


			row = 4
			col = 0
			for rec in unique_branch:
				
				branch_data = self.env['bsg_branches.bsg_branches'].search([('id','=',int(rec))],limit=1)
				branch_name = branch_data.branch_ar_name
				branch_code = branch_data.location_code

				worksheet.write_string (row, col+9,str(branch_name),main_data)
				worksheet.write_string (row, col+8,str(branch_code),main_data)

				checking_data = bsg_cargo_lines.loc[(bsg_cargo_lines['loc_from_branch_id'] == rec)]

				cop_data = gr_month_wise.loc[(gr_month_wise['revenue_type'] == 'corporate') & (gr_month_wise['loc_from_branch_id'] == rec)]
				indv_data = gr_month_wise.loc[(gr_month_wise['revenue_type'] == 'individual') & (gr_month_wise['loc_from_branch_id'] == rec)]

				branch_tot_num = 0
				branch_tot_amt = 0 

				if len(indv_data) > 0:
					for index,line in indv_data.iterrows():
						worksheet.write_string (row, col+6,str(round(line['charges_stored'],2)),main_data)
						worksheet.write_string (row, col+7,str(line['counter']),main_data)
						branch_tot_amt = branch_tot_amt + line['charges_stored']
						branch_tot_num = branch_tot_num + line['counter']
						inv_g_amt = inv_g_amt + line['charges_stored']
						inv_g_numz = inv_g_numz + line['counter']
				else:
					worksheet.write_string (row, col+7,str('0'),main_data)
					worksheet.write_string (row, col+6,str('0'),main_data)

				if len(cop_data) > 0:
					for index,line in cop_data.iterrows():
						worksheet.write_string (row, col+4,str(round(line['charges_stored'],2)),main_data)
						worksheet.write_string (row, col+5,str(line['counter']),main_data)
						branch_tot_amt = branch_tot_amt + line['charges_stored']
						branch_tot_num = branch_tot_num + line['counter']
						cop_g_amt = cop_g_amt + line['charges_stored']
						cop_g_numz = cop_g_numz + line['counter']
				else:
					worksheet.write_string (row, col+5,str('0'),main_data)
					worksheet.write_string (row, col+4,str('0'),main_data)


				worksheet.write_string (row, col+2,str(round(branch_tot_amt,2)),main_data)
				worksheet.write_string (row, col+3,str(branch_tot_num),main_data)

				branch_target = self.env['bsg_branch_sales_target_lines'].search([('bsg_br_sl_tr_id.financial_year.id','in',data['year']),('customer_type','in',['individual','corporate'])])
				branch_target = branch_target.filtered(lambda l: branch_data in l.bsg_br_sl_tr_id.bsg_sl_tr_br_id and l.bsg_br_sl_tr_id.bsg_sl_tr_br_id[0].id)
				target = branch_target.mapped('bsg_br_sl_tr_for_tar')
				target = sum(target)
				
				worksheet.write_string (row, col+1,str(target),main_data)
				if target > 0:
					percent_achived = float((branch_tot_amt * 100) / target)
				else:
					percent_achived = 0
				percent_achived = round(percent_achived,2)

				worksheet.write_string (row, col,str(percent_achived),main_data)

				tot_target = tot_target + target
				tot_g_amt = tot_g_amt + branch_tot_amt
				tot_g_numz = tot_g_numz + branch_tot_num
				
				row = row + 1


			loc = 'A'+str(row+1)
			loc92 = 'B'+str(row+1)
			loc1 = 'C'+str(row+1)
			loc15 = 'D'+str(row+1)
			loc30 = 'E'+str(row+1)
			loc45 = 'F'+str(row+1)
			loc60 = 'G'+str(row+1)
			loc75 = 'H'+str(row+1)
			loc90 = 'I'+str(row+1)
			loc91 = 'J'+str(row+1)

			if tot_target > 0:
				percent_achived_tot = float((tot_g_amt * 100) / tot_target)
			else:
				percent_achived_tot = 0

			percent_achived_tot = round(percent_achived_tot,2)
			
			end_loc = str(loc90)+':'+str(loc91)
			worksheet.merge_range(str(end_loc), 'اجمالي عام' ,main_heading)
			worksheet.write_string(str(loc),str("{0:.2f}".format(percent_achived_tot)),main_heading1)
			worksheet.write_string(str(loc92),str("{0:.2f}".format(tot_target)),main_heading1)
			worksheet.write_string(str(loc1),str("{0:.2f}".format(tot_g_amt)),main_heading1)
			worksheet.write_string(str(loc15),str("{0:.2f}".format(tot_g_numz)),main_heading1)
			worksheet.write_string(str(loc30),str("{0:.2f}".format(cop_g_amt)),main_heading1)
			worksheet.write_string(str(loc45),str("{0:.2f}".format(cop_g_numz)),main_heading1)
			worksheet.write_string(str(loc60),str("{0:.2f}".format(inv_g_amt)),main_heading1)
			worksheet.write_string(str(loc75),str("{0:.2f}".format(inv_g_numz)),main_heading1)

		if data['details']:

			worksheet.merge_range('A1:I1',str(" التقرير  الاول :  تقرير اجمالي ايرادات الفروع الشهريه "+ "/" +  print_date),merge_format)

			#worksheet.merge_range('D3:K3','عملاء الأفراد',main_heading)
			#worksheet.merge_range('L3:S3','عملاء الشـركات',main_heading)
			#worksheet.merge_range('T3:Y3','عملاء الأفراد',main_heading)
			#worksheet.merge_range('Z3:AE3','عملاء الشركات',main_heading)
			#worksheet.merge_range('AF3:AG3','عملاء أفراد',main_heading)
			#worksheet.merge_range('AH3:AI3','عملاء الشركات',main_heading)


			#worksheet.merge_range('D4:E4','نقدي',main_heading)
			#worksheet.merge_range('F4:G4','الدفع عند الإستلام',main_heading)
			#worksheet.merge_range('H4:I4','على الحساب',main_heading)
			#worksheet.merge_range('J4:K4','الإجمالي',main_heading)

			#worksheet.merge_range('L4:M4','نقدي',main_heading)
			#worksheet.merge_range('N4:O4','الدفع عند الإستلام',main_heading)
			#worksheet.merge_range('P4:Q4','على الحساب',main_heading)
			#worksheet.merge_range('R4:S4','الإجمالي',main_heading)

			#worksheet.write('T4', 'عادي', main_heading2)
			#worksheet.write('U4', 'دولي', main_heading2)
			#worksheet.write('V4', 'سطحه خاصة', main_heading2)
			#worksheet.write('W4', 'نقل مميز', main_heading2)
			#worksheet.write('X4', 'ميناء', main_heading2)
			#worksheet.write('Y4', 'داخلي', main_heading2)
			#worksheet.write('Z4', 'عادي', main_heading2)
			#worksheet.write('AA4', 'دولي', main_heading2)
			#worksheet.write('AB4', 'سطحه خاصة', main_heading2)
			#worksheet.write('AC4', 'نقل مميز', main_heading2)
			#worksheet.write('AD4', 'ميناء', main_heading2)
			#worksheet.write('AE4', 'داخلي', main_heading2)
			#worksheet.write('AF4', 'إذن الخروج', main_heading2)
			#worksheet.write('AG4', 'السجلات المرحله', main_heading2)
			#worksheet.write('AH4', 'إذن الخروج', main_heading2)
			#worksheet.write('AI4', 'السجلات المرحله', main_heading2)
			
			#worksheet.write('A5', 'الفرع', main_heading2)
			#worksheet.write('B5', 'كود الموظف', main_heading2)
			#worksheet.write('C5', 'اسم الموظف', main_heading2)
			#worksheet.write('D5', 'عدد', main_heading2)
			#worksheet.write('E5', 'مبلغ', main_heading2)
			#worksheet.write('F5', 'عدد', main_heading2)
			#worksheet.write('G5', 'مبلغ', main_heading2)
			#worksheet.write('H5', 'عدد', main_heading2)
			#worksheet.write('I5', 'مبلغ', main_heading2)
			#worksheet.write('J5', 'عدد', main_heading2)
			#worksheet.write('K5', 'مبلغ', main_heading2)
			#worksheet.write('L5', 'عدد', main_heading2)
			#worksheet.write('M5', 'مبلغ', main_heading2)
			#worksheet.write('N5', 'عدد', main_heading2)
			#worksheet.write('O5', 'مبلغ', main_heading2)
			#worksheet.write('P5', 'عدد', main_heading2)
			#worksheet.write('Q5', 'مبلغ', main_heading2)
			#worksheet.write('R5', 'عدد', main_heading2)
			#worksheet.write('S5', 'مبلغ', main_heading2)
			#worksheet.write('T5', 'العدد', main_heading2)
			#worksheet.write('U5', 'العدد', main_heading2)
			#worksheet.write('V5', 'العدد', main_heading2)
			#worksheet.write('W5', 'العدد', main_heading2)
			#worksheet.write('X5', 'العدد', main_heading2)
			#worksheet.write('Y5', 'العدد', main_heading2)
			#worksheet.write('Z5', 'العدد', main_heading2)
			#worksheet.write('AA5', 'العدد', main_heading2)
			#worksheet.write('AB5', 'العدد', main_heading2)
			#worksheet.write('AC5', 'العدد', main_heading2)
			#worksheet.write('AD5', 'العدد', main_heading2)
			#worksheet.write('AE5', 'العدد', main_heading2)
			#worksheet.write('AF5', 'العدد', main_heading2)
			#worksheet.write('AG5', 'العدد', main_heading2)
			#worksheet.write('AH5', 'العدد', main_heading2)
			#worksheet.write('AI5', 'العدد', main_heading2)

			worksheet.set_column('A:AI5', 13)
			# print (unique_users)
			# print (gr_month_wise)

			row = 2
			col = 0

			for b in unique_branches:



				#Header>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
				worksheet.merge_range('D'+str(row+1)+':K'+str(row+1),'عملاء الأفراد',main_heading)
				worksheet.merge_range('L'+str(row+1)+':S'+str(row+1),'عملاء الشـركات',main_heading)
				worksheet.merge_range('T'+str(row+1)+':Y'+str(row+1),'عملاء الأفراد',main_heading)
				worksheet.merge_range('Z'+str(row+1)+':AE'+str(row+1),'عملاء الشركات',main_heading)
				worksheet.merge_range('AF'+str(row+1)+':AG'+str(row+1),'عملاء أفراد',main_heading)
				worksheet.merge_range('AH'+str(row+1)+':AI'+str(row+1),'عملاء الشركات',main_heading)


				worksheet.merge_range('D'+str(row+2)+':E'+str(row+2),'نقدي',main_heading)
				worksheet.merge_range('F'+str(row+2)+':G'+str(row+2),'الدفع عند الإستلام',main_heading)
				worksheet.merge_range('H'+str(row+2)+':I'+str(row+2),'على الحساب',main_heading)
				worksheet.merge_range('J'+str(row+2)+':K'+str(row+2),'الإجمالي',main_heading)

				worksheet.merge_range('L'+str(row+2)+':M'+str(row+2),'نقدي',main_heading)
				worksheet.merge_range('N'+str(row+2)+':O'+str(row+2),'الدفع عند الإستلام',main_heading)
				worksheet.merge_range('P'+str(row+2)+':Q'+str(row+2),'على الحساب',main_heading)
				worksheet.merge_range('R'+str(row+2)+':S'+str(row+2),'الإجمالي',main_heading)

				worksheet.write('T'+str(row+2), 'عادي', main_heading2)
				worksheet.write('U'+str(row+2), 'دولي', main_heading2)
				worksheet.write('V'+str(row+2), 'سطحه خاصة', main_heading2)
				worksheet.write('W'+str(row+2), 'نقل مميز', main_heading2)
				worksheet.write('X'+str(row+2), 'ميناء', main_heading2)
				worksheet.write('Y'+str(row+2), 'داخلي', main_heading2)
				worksheet.write('Z'+str(row+2), 'عادي', main_heading2)
				worksheet.write('AA'+str(row+2), 'دولي', main_heading2)
				worksheet.write('AB'+str(row+2), 'سطحه خاصة', main_heading2)
				worksheet.write('AC'+str(row+2), 'نقل مميز', main_heading2)
				worksheet.write('AD'+str(row+2), 'ميناء', main_heading2)
				worksheet.write('AE'+str(row+2), 'داخلي', main_heading2)
				worksheet.write('AF'+str(row+2), 'إذن الخروج', main_heading2)
				worksheet.write('AG'+str(row+2), 'السجلات المرحله', main_heading2)
				worksheet.write('AH'+str(row+2), 'إذن الخروج', main_heading2)
				worksheet.write('AI'+str(row+2), 'السجلات المرحله', main_heading2)
				
				worksheet.write('A'+str(row+3), 'الفرع', main_heading2)
				worksheet.write('B'+str(row+3), 'كود الموظف', main_heading2)
				worksheet.write('C'+str(row+3), 'اسم الموظف', main_heading2)
				worksheet.write('D'+str(row+3), 'عدد', main_heading2)
				worksheet.write('E'+str(row+3), 'مبلغ', main_heading2)
				worksheet.write('F'+str(row+3), 'عدد', main_heading2)
				worksheet.write('G'+str(row+3), 'مبلغ', main_heading2)
				worksheet.write('H'+str(row+3), 'عدد', main_heading2)
				worksheet.write('I'+str(row+3), 'مبلغ', main_heading2)
				worksheet.write('J'+str(row+3), 'عدد', main_heading2)
				worksheet.write('K'+str(row+3), 'مبلغ', main_heading2)
				worksheet.write('L'+str(row+3), 'عدد', main_heading2)
				worksheet.write('M'+str(row+3), 'مبلغ', main_heading2)
				worksheet.write('N'+str(row+3), 'عدد', main_heading2)
				worksheet.write('O'+str(row+3), 'مبلغ', main_heading2)
				worksheet.write('P'+str(row+3), 'عدد', main_heading2)
				worksheet.write('Q'+str(row+3), 'مبلغ', main_heading2)
				worksheet.write('R'+str(row+3), 'عدد', main_heading2)
				worksheet.write('S'+str(row+3), 'مبلغ', main_heading2)
				worksheet.write('T'+str(row+3), 'العدد', main_heading2)
				worksheet.write('U'+str(row+3), 'العدد', main_heading2)
				worksheet.write('V'+str(row+3), 'العدد', main_heading2)
				worksheet.write('W'+str(row+3), 'العدد', main_heading2)
				worksheet.write('X'+str(row+3), 'العدد', main_heading2)
				worksheet.write('Y'+str(row+3), 'العدد', main_heading2)
				worksheet.write('Z'+str(row+3), 'العدد', main_heading2)
				worksheet.write('AA'+str(row+3), 'العدد', main_heading2)
				worksheet.write('AB'+str(row+3), 'العدد', main_heading2)
				worksheet.write('AC'+str(row+3), 'العدد', main_heading2)
				worksheet.write('AD'+str(row+3), 'العدد', main_heading2)
				worksheet.write('AE'+str(row+3), 'العدد', main_heading2)
				worksheet.write('AF'+str(row+3), 'العدد', main_heading2)
				worksheet.write('AG'+str(row+3), 'العدد', main_heading2)
				worksheet.write('AH'+str(row+3), 'العدد', main_heading2)
				worksheet.write('AI'+str(row+3), 'العدد', main_heading2)

				branch_data = self.env['bsg_branches.bsg_branches'].search([('id','=',int(b))],limit=1)
				branch_name = branch_data.branch_ar_name
				branch_code = branch_data.location_code
				users_data = bsg_cargo_lines.loc[(bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines.create_uid.notnull())]
				unique_users = users_data.create_uid.unique()

				worksheet.write_string (row+3, col+0,str(branch_name),main_heading1)
				# worksheet.write_string (row, col+1,str(branch_code),main_heading1)

				row = row + 4
				col = 0

				for rec in unique_users:
					
					emp_data = self.env['hr.employee'].search([('user_id','=',int(rec))],limit=1)
					emp_name = emp_data.name
					emp_code = emp_data.driver_code
					emp_job = emp_data.job_id.name

					payment_method_cash = self.env['cargo_payment_method'].search([('payment_type','=','cash')]).ids
					payment_method_credit = self.env['cargo_payment_method'].search([('payment_type','=','credit')]).ids
					payment_method_pod = self.env['cargo_payment_method'].search([('payment_type','=','pod')]).ids

					# checking_data = bsg_cargo_lines.loc[(bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b)]

					# unique_ids = checking_data.self_id.unique()
					# unique_ids = unique_ids.tolist()

					# related_inv = self.env['bsg_vehicle_cargo_sale_line'].search([('id','in',unique_ids),('revenue_type','=','individual')])
					# tot_inv = related_inv.mapped('total_without_tax')
					# tot_inv = sum(tot_inv)

					# related_cop = self.env['bsg_vehicle_cargo_sale_line'].search([('id','in',unique_ids),('revenue_type','=','corporate')])
					# tot_cop = related_cop.mapped('total_without_tax')bassami_modules
					# tot_cop = sum(tot_cop)
					#print("11>>>>>>>>>>>>>>>",bsg_cargo_lines['self_id'].tolist())
					co_user_records = bsg_cars_for_deliver.loc[(bsg_cars_for_deliver['revenue_type'] == 'corporate') & (bsg_cars_for_deliver['loc_to'] == b)]
					inv_user_records = bsg_cars_for_deliver.loc[(bsg_cars_for_deliver['revenue_type'] == 'individual') & (bsg_cars_for_deliver['loc_to'] == b)]
					
					#history_report_frame = history_report_frame.loc[(history_report_frame['cargo_so_line_id'].isin(bsg_cars_for_deliver['self_id'].tolist()))]

					indv_data = history_report_frame.loc[(history_report_frame['user_id'] == rec) & (history_report_frame['cargo_so_line_id'].isin(inv_user_records['self_id'].tolist()))]
					cop_data = history_report_frame.loc[(history_report_frame['user_id'] == rec) & (history_report_frame['cargo_so_line_id'].isin(co_user_records['self_id'].tolist()))]

					indv_data_picking = bicking_table_frame.loc[(bicking_table_frame['user_id'] == rec) & (bicking_table_frame['cargo_so_line_id'].isin(inv_user_records['self_id'].tolist()))]
					cop_data_picking = bicking_table_frame.loc[(bicking_table_frame['user_id'] == rec) & (bicking_table_frame['cargo_so_line_id'].isin(co_user_records['self_id'].tolist()))]					

					#indv_data = bsg_cargo_lines.loc[(bsg_cargo_lines['revenue_type'] == 'individual') & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines.cargo_so_line_id.notnull()) & (bsg_cargo_lines['loc_from_branch_id'] == b)]

					#cop_data = bsg_cargo_lines.loc[(bsg_cargo_lines['revenue_type'] == 'corporate') & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines.cargo_so_line_id.notnull()) & (bsg_cargo_lines['loc_from_branch_id'] == b)]

					cash_data_inv_amt = 0 
					pod_data_inv_amt = 0
					credit_data_inv_amt = 0

					cash_data_inv = bsg_cargo_lines.loc[(bsg_cargo_lines['payment_method'].isin(payment_method_cash)) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'individual')]
					if len(cash_data_inv) > 0:
						for index,line in cash_data_inv.iterrows():
							cash_data_inv_amt = cash_data_inv_amt + line['charges_stored']

					pod_data_inv = bsg_cargo_lines.loc[(bsg_cargo_lines['payment_method'].isin(payment_method_pod)) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'individual')]
					if len(pod_data_inv) > 0:
						for index,line in pod_data_inv.iterrows():
							pod_data_inv_amt = pod_data_inv_amt + line['charges_stored']

					credit_data_inv = bsg_cargo_lines.loc[(bsg_cargo_lines['payment_method'].isin(payment_method_credit)) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'individual')]
					if len(credit_data_inv) > 0:
						for index,line in credit_data_inv.iterrows():
							credit_data_inv_amt = credit_data_inv_amt + line['charges_stored']


					cash_data_cop_amt = 0 
					pod_data_cop_amt = 0
					credit_data_cop_amt = 0


					cash_data_cop = bsg_cargo_lines.loc[(bsg_cargo_lines['payment_method'].isin(payment_method_cash)) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'corporate')]
					if len(cash_data_cop) > 0:
						for index,line in cash_data_cop.iterrows():
							cash_data_cop_amt = cash_data_cop_amt + line['charges_stored']

					pod_data_cop = bsg_cargo_lines.loc[(bsg_cargo_lines['payment_method'].isin(payment_method_pod)) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'corporate')]
					if len(pod_data_cop) > 0:
						for index,line in pod_data_cop.iterrows():
							pod_data_cop_amt = pod_data_cop_amt + line['charges_stored']

					credit_data_cop = bsg_cargo_lines.loc[(bsg_cargo_lines['payment_method'].isin(payment_method_credit)) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'corporate')]
					if len(credit_data_cop) > 0:
						for index,line in credit_data_cop.iterrows():
							credit_data_cop_amt = credit_data_cop_amt + line['charges_stored']


					is_normal = bsg_cargo_lines.loc[(bsg_cargo_lines['is_normal'] == True) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'individual')]
					is_international = bsg_cargo_lines.loc[(bsg_cargo_lines['is_international'] == True) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'individual')]
					is_satha = bsg_cargo_lines.loc[(bsg_cargo_lines['is_satha'] == True) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'individual')]
					is_vip = bsg_cargo_lines.loc[(bsg_cargo_lines['is_vip'] == True) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'individual')]
					is_port = bsg_cargo_lines.loc[(bsg_cargo_lines['is_port'] == True) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'individual')]
					is_internal = bsg_cargo_lines.loc[(bsg_cargo_lines['is_internal'] == True) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'individual')]

					is_normal_cop = bsg_cargo_lines.loc[(bsg_cargo_lines['is_normal'] == True) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'corporate')]
					is_international_cop = bsg_cargo_lines.loc[(bsg_cargo_lines['is_international'] == True) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'corporate')]
					is_satha_cop = bsg_cargo_lines.loc[(bsg_cargo_lines['is_satha'] == True) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'corporate')]
					is_vip_cop = bsg_cargo_lines.loc[(bsg_cargo_lines['is_vip'] == True) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'corporate')]
					is_port_cop = bsg_cargo_lines.loc[(bsg_cargo_lines['is_port'] == True) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'corporate')]
					is_internal_cop = bsg_cargo_lines.loc[(bsg_cargo_lines['is_internal'] == True) & (bsg_cargo_lines['create_uid'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'corporate')]


					local_trip = trip_frame_data.loc[(trip_frame_data['trip_type'] == 'local') & (trip_frame_data['trip_user'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b)]
					man_trip = trip_frame_data.loc[(trip_frame_data['trip_type'] == 'manual') & (trip_frame_data['trip_user'] == rec) & (bsg_cargo_lines['loc_from_branch_id'] == b)]
					
					worksheet.write_string (row, col+1,str(emp_code),main_data)
					worksheet.write_string (row, col+2,str(emp_name),main_data)
					worksheet.write_string (row, col+3,str(len(cash_data_inv)),main_data)
					worksheet.write_string (row, col+4,str("{0:.2f}".format(cash_data_inv_amt)),main_data)
					worksheet.write_string (row, col+5,str(len(pod_data_inv)),main_data)
					worksheet.write_string (row, col+6,str("{0:.2f}".format(pod_data_inv_amt)),main_data)
					worksheet.write_string (row, col+7,str(len(credit_data_inv)),main_data)
					worksheet.write_string (row, col+8,str("{0:.2f}".format(credit_data_inv_amt)),main_data)
					worksheet.write_string (row, col+9,str(len(cash_data_inv)+len(pod_data_inv)+len(credit_data_inv)),main_data)
					worksheet.write_string (row, col+10,str("{0:.2f}".format(cash_data_inv_amt+pod_data_inv_amt+credit_data_inv_amt)),main_data)
					worksheet.write_string (row, col+11,str(len(cash_data_cop)),main_data)
					worksheet.write_string (row, col+12,str("{0:.2f}".format(cash_data_cop_amt)),main_data)
					worksheet.write_string (row, col+13,str(len(pod_data_cop)),main_data)
					worksheet.write_string (row, col+14,str("{0:.2f}".format(pod_data_cop_amt)),main_data)
					worksheet.write_string (row, col+15,str(len(credit_data_cop)),main_data)
					worksheet.write_string (row, col+16,str("{0:.2f}".format(credit_data_cop_amt)),main_data)
					worksheet.write_string (row, col+17,str(len(cash_data_cop)+len(pod_data_cop)+len(credit_data_cop)),main_data)
					worksheet.write_string (row, col+18,str("{0:.2f}".format(cash_data_cop_amt+pod_data_cop_amt+credit_data_cop_amt)),main_data)
					worksheet.write_string (row, col+19,str(len(is_normal)),main_data)
					worksheet.write_string (row, col+20,str(len(is_international)),main_data)
					worksheet.write_string (row, col+21,str(len(is_satha)),main_data)
					worksheet.write_string (row, col+22,str(len(is_vip)),main_data)
					worksheet.write_string (row, col+23,str(len(is_port)),main_data)
					worksheet.write_string (row, col+24,str(len(is_internal)),main_data)
					worksheet.write_string (row, col+25,str(len(is_normal_cop)),main_data)
					worksheet.write_string (row, col+26,str(len(is_international_cop)),main_data)
					worksheet.write_string (row, col+27,str(len(is_satha_cop)),main_data)
					worksheet.write_string (row, col+28,str(len(is_vip_cop)),main_data)
					worksheet.write_string (row, col+29,str(len(is_port_cop)),main_data)
					worksheet.write_string (row, col+30,str(len(is_internal_cop)),main_data)
					worksheet.write_string (row, col+31,str(len(indv_data)),main_data)
					worksheet.write_string (row, col+32,str(len(indv_data_picking)),main_data)
					worksheet.write_string (row, col+33,str(len(cop_data)),main_data)
					worksheet.write_string (row, col+34,str(len(cop_data_picking)),main_data)
					

					row = row + 1

				branch_target_inv = self.env['bsg_branch_sales_target_lines'].search([('bsg_br_sl_tr_id.financial_year.id','in',data['year']),('customer_type','in',['individual'])])
				branch_target_inv = branch_target_inv.filtered(lambda l: branch_data in l.bsg_br_sl_tr_id.bsg_sl_tr_br_id and l.bsg_br_sl_tr_id.bsg_sl_tr_br_id[0].id)
				branch_target_inv = branch_target_inv.mapped('bsg_br_sl_tr_for_tar')
				branch_target_inv = sum(branch_target_inv)

				branch_amt_inv = bsg_cargo_lines.loc[(bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'individual')]
				branch_target_inv_ach = 0
				gr_branch_wise = branch_amt_inv.groupby(['loc_from_branch_id'],as_index = False).sum()
				if len(gr_branch_wise) > 0:
					for index,line in gr_branch_wise.iterrows():
						branch_target_inv_ach = branch_target_inv_ach + line['charges_stored']

				if branch_target_inv > 0:
					percent_achived = float((branch_target_inv_ach * 100) / branch_target_inv)
				else:
					percent_achived = 0
				percent_achived = round(percent_achived,2)

				branch_target_cop = self.env['bsg_branch_sales_target_lines'].search([('bsg_br_sl_tr_id.financial_year.id','in',data['year']),('customer_type','in',['corporate'])])
				branch_target_cop = branch_target_cop.filtered(lambda l: branch_data in l.bsg_br_sl_tr_id.bsg_sl_tr_br_id and l.bsg_br_sl_tr_id.bsg_sl_tr_br_id[0].id)
				branch_target_cop = branch_target_cop.mapped('bsg_br_sl_tr_for_tar')
				branch_target_cop = sum(branch_target_cop)

				branch_amt_cop = bsg_cargo_lines.loc[(bsg_cargo_lines['loc_from_branch_id'] == b) & (bsg_cargo_lines['revenue_type'] == 'corporate')]
				branch_target_cop_ach = 0
				gr_branch_wise_cop = branch_amt_cop.groupby(['loc_from_branch_id'],as_index = False).sum()
				if len(gr_branch_wise_cop) > 0:
					for index,line in gr_branch_wise_cop.iterrows():
						branch_target_cop_ach = branch_target_cop_ach + line['charges_stored']

				if branch_target_cop > 0:
					percent_achived_cop = float((branch_target_cop_ach * 100) / branch_target_cop)
				else:
					percent_achived_cop = 0
				percent_achived_cop = round(percent_achived_cop,2)

				if (branch_target_inv+branch_target_cop) > 0:
					percent_achived_tot = float(((branch_target_inv_ach+branch_target_cop_ach) * 100) / (branch_target_inv+branch_target_cop))
				else:
					percent_achived_tot = 0
				percent_achived_tot = round(percent_achived_tot,2)

				loc = 'D'+str(row+1)
				loc1 = 'E'+str(row+1)
				loc2 = 'F'+str(row+1)
				loc3 = 'G'+str(row+1)
				loc4 = 'H'+str(row+1)
				loc5 = 'I'+str(row+1)
				loc6 = 'J'+str(row+1)
				loc7 = 'K'+str(row+1)
				loc8 = 'L'+str(row+1)
				loc9 = 'M'+str(row+1)
				loc10 = 'N'+str(row+1)
				loc11 = 'O'+str(row+1)
				loc12 = 'P'+str(row+1)
				loc13 = 'Q'+str(row+1)
				loc14 = 'R'+str(row+1)
				loc15 = 'S'+str(row+1)
				loc16 = 'T'+str(row+1)
				loc17 = 'U'+str(row+1)

				worksheet.write(str(loc), str('الإيراد الفعلي أفراد') ,main_heading)
				worksheet.write(str(loc1), str("{0:.2f}".format(branch_target_inv_ach)),main_heading)
				worksheet.write(str(loc2), str('المستهدف أفراد') ,main_heading)
				worksheet.write(str(loc3), str("{0:.2f}".format(branch_target_inv)) ,main_heading)
				worksheet.write(str(loc4), str('نسبة التحقيق أفراد') ,main_heading)
				worksheet.write(str(loc5), str("{0:.2f}".format(percent_achived)) ,main_heading)
				worksheet.write(str(loc6), str('الإيراد الفعلي شركات') ,main_heading)
				worksheet.write(str(loc7), str("{0:.2f}".format(branch_target_cop_ach)) ,main_heading)
				worksheet.write(str(loc8), str('المستهدف شركات') ,main_heading)
				worksheet.write(str(loc9), str("{0:.2f}".format(branch_target_cop)) ,main_heading)
				worksheet.write(str(loc10), str('نسبة التحقيق شركات') ,main_heading)
				worksheet.write(str(loc11), str("{0:.2f}".format(percent_achived_cop)) ,main_heading)
				worksheet.write(str(loc12), str('الإجمالي للأفراد والشركات') ,main_heading)
				worksheet.write(str(loc13), str("{0:.2f}".format(branch_target_inv_ach+branch_target_cop_ach)) ,main_heading)
				worksheet.write(str(loc14), str('المستهدف الإجمالي') ,main_heading)
				worksheet.write(str(loc15), str("{0:.2f}".format(branch_target_inv+branch_target_cop)) ,main_heading)
				worksheet.write(str(loc16), str('نسبة التحقيق الإجمالية') ,main_heading)
				worksheet.write(str(loc17), str("{0:.2f}".format(percent_achived_tot)) ,main_heading)
				row += 2
