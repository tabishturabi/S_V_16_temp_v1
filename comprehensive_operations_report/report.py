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
from odoo import models, fields, api , _
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class TrialBalanceReportXlsx(models.TransientModel):
	_name = 'report.comprehensive_operations_report.comp_operat_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'

	# @api.multi
	def generate_xlsx_report(self, workbook, input_records, lines):
		data = input_records['form']

		table_name = "bsg_vehicle_cargo_sale_line as cargo_sale_line , bsg_vehicle_cargo_sale as cargo_sale_order , res_partner as res_partner \
			,partner_type as partner_type ,bsg_route_waypoints as from_bsg_route_waypoints,bsg_route_waypoints as to_bsg_route_waypoints \
			,cargo_payment_method as cargo_payment_method , bsg_car_model as bsg_car_model , bsg_car_year as bsg_car_year , bsg_car_config as bsg_car_config\
			,bsg_car_line as bsg_car_line , bsg_car_size as bsg_car_size ,res_partner as res_partner_user, res_users as res_users,bsg_car_shipment_type as car_shipment_type"
		state_cond = ''
		if data['so_line_state'] == 'paid':
			state_cond = 'and cargo_sale_line.is_paid = true'
		if data['so_line_state'] == 'unpaid':
			state_cond = 'and cargo_sale_line.is_paid = false'

		sale_order_state_cond = "and sale_order_state in ('done','pod','Delivered','confirm')"		
		if data['sale_order_state'] == 'confirm':
			sale_order_state_cond = "and cargo_sale_line.sale_order_state = 'confirm'"
		elif data['sale_order_state'] == 'pod':
			sale_order_state_cond = "and cargo_sale_line.sale_order_state = 'pod'"
		elif data['sale_order_state'] == 'done':
			sale_order_state_cond = "and cargo_sale_line.sale_order_state = 'done'"
		elif data['sale_order_state'] == 'Delivered':
			sale_order_state_cond = "and cargo_sale_line.sale_order_state = 'Delivered'"

		sale_line_state_cond = ''
		if data['state'] != 'all':
			sale_line_state_cond = f"and cargo_sale_line.state in ('{data['state']}')"


		invoice_state_cond = ''
		if data['pay_case'] == 'paid':
			invoice_state_cond = "and cargo_sale_line.invoice_state_stored = 'paid'"
		elif data['pay_case'] == 'not_paid':
			invoice_state_cond = "and cargo_sale_line.invoice_state_stored != 'paid'"

		
		user_cond = ''
		if data['user_type'] == 'specific':
			users = len(data['users']) == 1 and "(%s)" %data['users'][0] or  str(tuple(data['users']))
			user_cond = f"and cargo_sale_line.create_uid in {users})"


		loc_from_branch_cond = ''
		if data['branch_type'] == 'specific':
			branches = len(data['ship_loc']) == 1 and "(%s)" %data['ship_loc'][0] or  str(tuple(data['ship_loc']))
			loc_from_branch_cond = f"and cargo_sale_line.loc_from in {branches}" 

		loc_to_branch_cond = ''
		if data['branch_type_to'] == 'specific':
			branches_to = len(data['drop_loc']) == 1 and "(%s)" %data['drop_loc'][0] or  str(tuple(data['drop_loc']))
			loc_to_branch_cond = f"and cargo_sale_line.loc_to in {branches_to}"

		payment_method_cond = ''
		if data['payment_method_filter'] == 'specific':
			payment_methods = len(data['payment_method_ids']) == 1 and "(%s)" %data['payment_method_ids'][0] or  str(tuple(data['payment_method_ids']))
			payment_method_cond = f"and cargo_sale_line.payment_method in {payment_methods}"

		customer_id_cond = ''
		if data['customer_filter'] == 'specific':
			cust_ids = len(data['customer_ids']) == 1 and "(%s)" %data['customer_ids'][0] or  str(tuple(data['customer_ids']))
			customer_id_cond = f"and cargo_sale_line.customer_id in {cust_ids}"

		cargo_type_cond = ''
		if data['cargo_sale_type'] == 'local':
			cargo_type_cond = "and cargo_sale_order.cargo_sale_type = 'local'"
		if data['cargo_sale_type'] == 'international':
			cargo_type_cond = "and cargo_sale_order.cargo_sale_type = 'international'"

		self.env.cr.execute("select cargo_sale_line.id as sale_line_id,cargo_sale_line.order_date as sale_line_order_date,cargo_sale_line.loc_from_branch_id as sale_line_loc_from_branch_id,cargo_sale_line.loc_to as sale_line_loc_to\
			,cargo_sale_line.create_uid as sale_line_create_uid,cargo_sale_line.bsg_cargo_sale_id as sale_line_bsg_cargo_sale_id,cargo_sale_line.payment_method as sale_line_payment_method,cargo_sale_line.customer_id as sale_line_customer_id,cargo_sale_line.chassis_no as sale_line_chassis_no,cargo_sale_line.state as sale_line_state\
			,cargo_sale_line.fleet_trip_id as sale_line_fleet_trip_id,cargo_sale_line.loc_from as sale_line_loc_from,cargo_sale_line.pickup_loc as sale_line_pickup_loc,cargo_sale_line.car_model as sale_line_car_model,cargo_sale_line.year as sale_line_year,cargo_sale_line.car_color as sale_line_car_color\
			,cargo_sale_line.sale_line_rec_name as sale_line_sale_line_rec_name,cargo_sale_line.expected_delivery as sale_line_expected_delivery,cargo_sale_line.add_to_cc as sale_line_add_to_cc,cargo_sale_line.plate_no as sale_line_plate_no,cargo_sale_line.car_make as sale_line_car_make\
			,cargo_sale_line.palte_one as sale_line_palte_one,cargo_sale_line.charges_stored as sale_line_charges_stored, cargo_sale_line.final_price_stored as sale_line_final_price_stored, cargo_sale_line.invoice_state_stored as sale_line_invoice_state_stored\
			,cargo_sale_line.credit_collection_id as sale_line_credit_collection_id,cargo_sale_line.sale_order_state as sale_line_sale_order_state,cargo_sale_line.is_paid as sale_line_is_paid,cargo_sale_line.delivery_date as sale_line_delivery_date\
			,cargo_sale_order.id as cargo_sale_order_id,cargo_sale_order.name as cargo_sale_order_name,cargo_sale_order.shipment_type as cargo_sale_order_shipment_type,cargo_sale_order.partner_types as cargo_sale_order_partner_types,cargo_sale_order.cargo_invoice_to as cargo_sale_order_cargo_invoice_to\
			,res_partner.id as res_partner_id,res_partner.name as res_partner_name \
			,partner_type.id as partner_type_id,partner_type.name as partner_type_name\
			,from_bsg_route_waypoints.id as loc_from_bsg_route_waypoints_id,from_bsg_route_waypoints.route_waypoint_name as loc_from_bsg_route_waypoints_name\
			,to_bsg_route_waypoints.id as loc_to_bsg_route_waypoints_id,to_bsg_route_waypoints.route_waypoint_name as loc_to_bsg_route_waypoints_name	\
			,cargo_payment_method.id as cargo_payment_method_id,cargo_payment_method.payment_method_name as cargo_payment_method_name,bsg_car_model.id as bsg_car_model_id,bsg_car_model.car_model_name as bsg_car_model_name\
			,bsg_car_year.id as bsg_car_year_id,bsg_car_year.car_year_name as bsg_car_year_name , bsg_car_config.id as bsg_car_config_id,bsg_car_config.car_maker as bsg_car_config_name\
			,bsg_car_line.id as bsg_car_line_id,bsg_car_line.car_config_id as bsg_car_line_car_config_id,bsg_car_line.car_model as bsg_car_line_car_model,bsg_car_line.car_size as bsg_car_line_car_size\
			,bsg_car_size.id as bsg_car_size_id,bsg_car_size.car_size_name as bsg_car_size_name ,res_partner_user.name as res_users_name, res_users.login as res_users_login,cargo_sale_order.receiver_name as so_receiver_name\
			,car_shipment_type.car_shipment_name as so_line_car_shipment_name FROM "+table_name+" where cargo_sale_line.company_id = %s and cargo_sale_line.sale_line_rec_name NOT LIKE '%%P%%' and cargo_sale_line.order_date between '%s' and  '%s'\
			and cargo_sale_line.bsg_cargo_sale_id = cargo_sale_order.id and cargo_sale_line.customer_id = res_partner.id \
			and cargo_sale_order.partner_types = partner_type.id and cargo_sale_line.shipment_type = car_shipment_type.id \
			and cargo_sale_line.loc_from = from_bsg_route_waypoints.id and cargo_sale_line.loc_to = to_bsg_route_waypoints.id\
			and cargo_sale_line.payment_method = cargo_payment_method.id and cargo_sale_line.car_model = bsg_car_model.id\
			and cargo_sale_line.year = bsg_car_year.id and cargo_sale_line.car_make = bsg_car_config.id \
			and cargo_sale_line.car_make = bsg_car_line.car_config_id and cargo_sale_line.car_model = bsg_car_line.car_model\
			and cargo_sale_line.create_uid = res_users.id and res_partner_user.id = res_users.partner_id\
			and  bsg_car_line.car_size = bsg_car_size.id\
			 %s %s %s %s %s %s %s %s %s %s order by cargo_sale_line.order_date;\
			"%(self.env.user.company_id.id,str(data['form']),str(data['to']),str(state_cond),str(sale_order_state_cond),str(sale_line_state_cond),\
				str(invoice_state_cond),str(user_cond),str(loc_from_branch_cond),str(loc_to_branch_cond),str(payment_method_cond),str(customer_id_cond),str(cargo_type_cond)))
		result = self._cr.fetchall()
		if len(result) < 1:
			merge_format = workbook.add_format({
			'bold': 1,
			'border': 1,
			'align': 'center',
			'valign': 'vcenter',
			'font_size': '13',
			"font_color":'black',
			'bg_color': '#D3D3D3'})
			worksheet = workbook.add_worksheet('Comprehensive Operations Report')
			worksheet.merge_range('A1:S1','No Record Found',merge_format)
			return worksheet
		bsg_cargo_lines = pd.DataFrame(list(result))
		bsg_cargo_lines = bsg_cargo_lines.rename(columns={0: 'self_id',1: 'order_date',2: 'loc_from_branch_id',3: 'loc_to',4: 'create_uid'\
		,5:'bsg_cargo_sale_id',6: 'payment_method',7: 'customer_id',8: 'chassis_no',9: 'state',10: 'fleet_trip_id',11: 'loc_from'\
		,12: 'pickup_loc',13: 'car_model',14: 'year',15: 'car_color',16: 'sale_line_rec_name',17: 'expected_delivery',18: 'add_to_cc'\
		,19: 'plate_no',20: 'car_make',21: 'palte_one',22: 'charges_stored',23: 'final_price_stored',24: 'invoice_state_stored'\
		,25:'credit_collection_id',26:'sale_order_state',27:'is_so_paid',28:'delivery_date'\
		,29: 'bsg_cargo_id_final',30: 'bsg_cargosale_name',31: 'bsg_shipment_type',32: 'bsg_partner_type',33: 'cargo_invoice_to'\
		,34: 'bsg_customer_id',35: 'bsg_customer_name',36: 'bsg_partner_type_id',37: 'bsg_partnertype_name'\
		,38: 'bsg_loc_from_id',39: 'bsg_loc_from_name',40: 'bsg_loc_to_id',41: 'bsg_loc_to_name',42: 'bsg_pay_method_id',43: 'bsg_pay_method_name'\
		,44: 'car_model_id',45: 'car_model_name',46: 'car_year_id',47: 'car_year_name',48: 'car_config_id',49: 'car_make_id'\
		,50: 'car_configline_id',51: 'car_configrelated_id',52: 'car_modelline_id',53: 'car_sizeline_id'\
		,54: 'car_size_id',55: 'car_size_name',56:'res_users_name',57:'res_users_login',58:'so_receiver_name',59:'so_line_car_shipment_name'})

			# bsg_cargo_inv_table = "bsg_vehicle_cargo_sale"
			# self.env.cr.execute("select id FROM "+bsg_cargo_inv_table+" where state != 'draft' ")
			# result_bsg_cargo_inv_table = self._cr.fetchall()

			# bsg_cargo_inv = pd.DataFrame(list(result_bsg_cargo_inv_table))

			# bsg_cargo_inv = bsg_cargo_inv.rename(columns={0: 'bsg_cargo_id_inv'})

			# bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_cargo_inv,  how='left', left_on='bsg_cargo_sale_id', right_on ='bsg_cargo_id_inv')

			# inv_frame_table = "account_invoice"
			# self.env.cr.execute("select id,state,cargo_sale_id FROM "+inv_frame_table+" ")
			# result_inv_frame_table = self._cr.fetchall()

			# inv_frame = pd.DataFrame(list(result_inv_frame_table))
			# inv_frame = inv_frame.rename(columns={0: 'invoice_id',1: 'inv_state',2: 'cargo_sale_id'})
			# inv_frame = inv_frame.loc[(inv_frame['inv_state'] == 'paid')]


			# bsg_cargo_lines = pd.merge(bsg_cargo_lines,inv_frame,  how='left', left_on='bsg_cargo_id_inv', right_on ='cargo_sale_id')

			# bsg_cargo_lines = bsg_cargo_lines[bsg_cargo_lines.invoice_id.notnull()]


			# bsg_cargo_inv_table = "bsg_vehicle_cargo_sale"
			# self.env.cr.execute("select id FROM "+bsg_cargo_inv_table+" where state != 'draft' ")
			# result_bsg_cargo_inv_table = self._cr.fetchall()

			# bsg_cargo_inv = pd.DataFrame(list(result_bsg_cargo_inv_table))

			# bsg_cargo_inv = bsg_cargo_inv.rename(columns={0: 'bsg_cargo_id_inv'})

			# bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_cargo_inv,  how='left', left_on='bsg_cargo_sale_id', right_on ='bsg_cargo_id_inv')

			# inv_frame_table = "account_invoice"
			# self.env.cr.execute("select id,state,cargo_sale_id FROM "+inv_frame_table+" ")
			# result_inv_frame_table = self._cr.fetchall()

			# inv_frame = pd.DataFrame(list(result_inv_frame_table))
			# inv_frame = inv_frame.rename(columns={0: 'invoice_id',1: 'inv_state',2: 'cargo_sale_id'})
			# inv_frame = inv_frame.loc[(inv_frame['inv_state'] != 'paid')]


			# bsg_cargo_lines = pd.merge(bsg_cargo_lines,inv_frame,  how='left', left_on='bsg_cargo_id_inv', right_on ='cargo_sale_id')

			# bsg_cargo_lines = bsg_cargo_lines[bsg_cargo_lines.invoice_id.notnull()]





		'''if data['trip_type'] != 'all':

			trip_frame_table = "fleet_vehicle_trip"
			self.env.cr.execute("select id,trip_type FROM "+trip_frame_table+" where company_id = %s"%self.env.user.company_id.id)
			result_trip_frame_table = self._cr.fetchall()
			trip_frame = pd.DataFrame(list(result_trip_frame_table))
			trip_frame = trip_frame.rename(columns={0: 'trip_id',1: 'trip_type'})


			trip_frame = trip_frame.loc[(trip_frame['trip_type'] == data['trip_type'])]
			bsg_cargo_lines = pd.merge(bsg_cargo_lines,trip_frame,  how='left', left_on='fleet_trip_id', right_on ='trip_id')

			bsg_cargo_lines = bsg_cargo_lines[bsg_cargo_lines.trip_id.notnull()]'''

			
		'''if data['cargo_sale_type'] == 'local':

			bsg_cargo_table = "bsg_vehicle_cargo_sale"
			self.env.cr.execute("select id,cargo_sale_type FROM "+bsg_cargo_table+" where company_id = %s"%self.env.user.company_id.id)
			result_bsg_cargo_table = self._cr.fetchall()
			bsg_cargo = pd.DataFrame(list(result_bsg_cargo_table))
			bsg_cargo = bsg_cargo.rename(columns={0: 'bsg_cargo_id',1: 'cargo_sale_type'})
			bsg_cargo = bsg_cargo.loc[(bsg_cargo['cargo_sale_type'] == 'local')]
			
			bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_cargo,  how='left', left_on='bsg_cargo_sale_id', right_on ='bsg_cargo_id')

			bsg_cargo_lines = bsg_cargo_lines[bsg_cargo_lines.bsg_cargo_id.notnull()]

		if data['cargo_sale_type'] == 'international':

			bsg_cargo_table = "bsg_vehicle_cargo_sale"
			self.env.cr.execute("select id,cargo_sale_type FROM "+bsg_cargo_table+" where company_id = %s"%self.env.user.company_id.id)
			result_bsg_cargo_table = self._cr.fetchall()
			bsg_cargo = pd.DataFrame(list(result_bsg_cargo_table))
			bsg_cargo = bsg_cargo.rename(columns={0: 'bsg_cargo_id',1: 'cargo_sale_type'})
			bsg_cargo = bsg_cargo.loc[(bsg_cargo['cargo_sale_type'] == 'international')]
			
			bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_cargo,  how='left', left_on='bsg_cargo_sale_id', right_on ='bsg_cargo_id')

			bsg_cargo_lines = bsg_cargo_lines[bsg_cargo_lines.bsg_cargo_id.notnull()]'''

		# bsg_inv_to_table = "res_partner"
		# self.env.cr.execute("select id,name FROM "+bsg_inv_to_table+" ")
		# result_bsg_inv_to = self._cr.fetchall()
		# bsg_inv_to_frame = pd.DataFrame(list(result_bsg_inv_to))
		# bsg_inv_to_frame = bsg_inv_to_frame.rename(columns={0: 'invoice_to_id',1: 'invoice_to_name'})
		# bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_inv_to_frame,  how='left', left_on='cargo_invoice_to', right_on ='invoice_to_id')

		# loc_pickup_frame_table = "bsg_route_waypoints"
		# self.env.cr.execute("select id,route_waypoint_name FROM "+loc_pickup_frame_table+" ")
		# result_loc_pickup_frame = self._cr.fetchall()
		# loc_pickup_frame = pd.DataFrame(list(result_loc_pickup_frame))
		# loc_pickup_frame = loc_pickup_frame.rename(columns={0: 'bsg_loc_to_id',1: 'bsg_loc_pickup_name'})
		# bsg_cargo_lines = pd.merge(bsg_cargo_lines,loc_pickup_frame,  how='left', left_on='pickup_loc', right_on ='bsg_loc_to_id')


		'''bsg_trip_frame_table = "fleet_vehicle_trip"
		self.env.cr.execute("select id,state,name,create_uid,vehicle_id,expected_end_date FROM "+bsg_trip_frame_table+" where company_id = %s"%self.env.user.company_id.id)
		result_bsg_trip_frame = self._cr.fetchall()
		bsg_trip_frame = pd.DataFrame(list(result_bsg_trip_frame))
		bsg_trip_frame = bsg_trip_frame.rename(columns={0: 'bsg_trip_id',1: 'bsg_trip_state',2: 'bsg_trip_name',3: 'bsg_trip_create_uid',4: 'trip_vehicle_id',5: 'expected_end_date'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_trip_frame,  how='left', left_on='fleet_trip_id', right_on ='bsg_trip_id')'''


		report_history_frame_table = "report_history_delivery"
		self.env.cr.execute("select cargo_so_line_id,dr_print_no,dr_user_id,dr_print_date FROM "+report_history_frame_table+" ")
		result_report_history_frame = self._cr.fetchall()
		report_history_frame = pd.DataFrame(list(result_report_history_frame))
		report_history_frame = report_history_frame.rename(columns={0: 'cargo_so_line_id',1: 'dr_print_no',2: 'dr_user_id',3: 'dr_print_date'})
		print('report_history_frame..........................',report_history_frame)
		if not report_history_frame.empty:
			report_history_frame = report_history_frame.sort_values(by='cargo_so_line_id')
			report_history_frame = report_history_frame.drop_duplicates(subset='cargo_so_line_id',keep="first")
			bsg_cargo_lines = pd.merge(bsg_cargo_lines,report_history_frame,  how='left', left_on='self_id', right_on ='cargo_so_line_id')

		# account_inv_frame_table = "account_invoice"
		# self.env.cr.execute("select id,cargo_sale_id,invoice_date,create_uid,number FROM "+account_inv_frame_table+" where cargo_sale_id is not null ")
		# result_account_inv_frame = self._cr.fetchall()
		# account_inv_frame = pd.DataFrame(list(result_account_inv_frame))
		# account_inv_frame = account_inv_frame.rename(columns={0: 'invoice_id',1: 'cargo_sale_id',2: 'invoice_date',3: 'inv_create_uid',4: 'inv_number'})
		# bsg_cargo_lines = pd.merge(bsg_cargo_lines,account_inv_frame,  how='left', left_on='bsg_cargo_id_final', right_on ='cargo_sale_id')

		# account_pay_frame_table = "account_payment"
		# self.env.cr.execute("select id,name,amount,payment_date,create_uid,cargo_sale_order_id,branch_ids FROM "+account_pay_frame_table+" where cargo_sale_order_id is not null ")
		# result_account_pay_frame = self._cr.fetchall()
		# account_pay_frame = pd.DataFrame(list(result_account_pay_frame))
		# account_pay_frame = account_pay_frame.rename(columns={0: 'voucher_id',4: 'voucher_create_uid',1: 'voucher_number',2: 'voucher_amount',5: 'voucher_sale_order_id',3: 'payment_date',6: 'branch_ids'})
		# bsg_cargo_lines = pd.merge(bsg_cargo_lines,account_pay_frame,  how='left', left_on='bsg_cargo_id_final', right_on ='voucher_sale_order_id')

		# branches_frame_table = "bsg_branches_bsg_branches"
		# self.env.cr.execute("select id,branch_ar_name FROM "+branches_frame_table+" ")
		# result_branches_frame = self._cr.fetchall()
		# branches_frame = pd.DataFrame(list(result_branches_frame))
		# branches_frame = branches_frame.rename(columns={0: 'bsg_branch_id',1: 'bsg_branch_name'})
		# bsg_cargo_lines = pd.merge(bsg_cargo_lines,branches_frame,  how='left', left_on='branch_ids', right_on ='bsg_branch_id')
		#
		# bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_vehicle_frame,  how='left', left_on='trip_vehicle_id', right_on ='bsg_vehicle_id')
		#
		# branch_veh_frame_table = "bsg_branches_bsg_branches"
		# self.env.cr.execute("select id,branch_ar_name FROM "+branch_veh_frame_table+" ")
		# result_branch_veh_frame = self._cr.fetchall()
		# branch_veh_frame = pd.DataFrame(list(result_branch_veh_frame))
		# branch_veh_frame = branch_veh_frame.rename(columns={0: 'bsg_veh_branch_id',1: 'bsg_veh_branch_name'})
		# bsg_cargo_lines = pd.merge(bsg_cargo_lines,branch_veh_frame,  how='left', left_on='bsg_vehicle_branch_name', right_on ='bsg_veh_branch_id')





		# car_maker_frame_table = "bsg_car_make"
		# self.env.cr.execute("select id,car_make_name,car_make_ar_name FROM "+car_maker_frame_table+" ")
		# result_car_maker_frame = self._cr.fetchall()
		# car_maker_frame = pd.DataFrame(list(result_car_maker_frame))
		# car_maker_frame = car_maker_frame.rename(columns={0: 'car_maker_id',1: 'car_make_name',2: 'car_make_ar_name'})
		# bsg_cargo_lines = pd.merge(bsg_cargo_lines,car_maker_frame,  how='left', left_on='car_make_id', right_on ='car_maker_id')

		'''fleet_arrival_frame_table = "fleet_trip_arrival"
		self.env.cr.execute("select id,actual_end_time,trip_id FROM "+fleet_arrival_frame_table+" ")
		result_fleet_arrival_frame = self._cr.fetchall()
		fleet_arrival_frame = pd.DataFrame(list(result_fleet_arrival_frame))
		fleet_arrival_frame = fleet_arrival_frame.rename(columns={0: 'arrival_screen_id',1: 'arrival_screen_time',2: 'arrival_screenrelated_id'})
		temp_arrival_frame = pd.merge(bsg_trip_frame,fleet_arrival_frame,  how='left', left_on='bsg_trip_id', right_on ='arrival_screenrelated_id')

		temp_arrival_frame = temp_arrival_frame.sort_values(by=['bsg_trip_id','arrival_screen_id'])
		temp_arrival_frame = temp_arrival_frame.drop_duplicates(subset='bsg_trip_id', keep="last")
		temp_arrival_frame = temp_arrival_frame[['bsg_trip_id','arrival_screen_time']]
		temp_arrival_frame = temp_arrival_frame.rename(columns={'bsg_trip_id': 'bsg_trip_screen_id'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,temp_arrival_frame,  how='left', left_on='fleet_trip_id', right_on ='bsg_trip_screen_id')'''

		if not data['with_summary']:
			invoice_line_table = "account_move_line as account_invoice_line,account_move as account_invoice"


						
			self.env.cr.execute(
				"select account_invoice_line.id,account_invoice_line.name,account_invoice_line.cargo_sale_line_id\
				,account_invoice_line.price_total,account_invoice_line.paid_amount,account_invoice_line.move_id\
				,account_invoice_line.is_paid ,account_invoice.id as account_invoice_id\
				,account_invoice.name as account_invoice_number,account_invoice.invoice_origin as account_invoice_origin,account_invoice.move_type as account_invoice_type\
				,account_invoice_line.is_other_service_line,account_invoice_line.is_demurrage_line \
				FROM "+invoice_line_table+" where account_invoice_line.company_id = %s and  account_invoice_line.move_id = account_invoice.id and account_invoice_line.cargo_sale_line_id in %s"%(self.env.user.company_id.id,tuple(bsg_cargo_lines['self_id'])))

			invoice_lines_data = self._cr.fetchall()
			invoice_lines = pd.DataFrame(list(invoice_lines_data))
			invoice_lines = invoice_lines.rename(
				columns={0: 'invoice_line_id', 1: 'inv_line_description', 2: 'inv_line_cargo_sale_line_id',
						 3: 'inv_price_total', 4: 'inv_paid_amount',5:'account_invoice_id',6:'inv_line_is_paid',
						 7: 'account_invoice_id', 8: 'account_invoice_ref', 9: 'account_invoice_origin',
						 10: 'account_invoice_type', 11: 'inv_line_is_other_service_line', 12: 'inv_line_is_demurrage_line'})


			payments_table = "account_cargo_line_payment"
			self.env.cr.execute(
				"select id,account_invoice_line_id,account_payment_id,amount FROM "+payments_table+" ")
			payments_lines_data = self._cr.fetchall()
			payments_lines = pd.DataFrame(list(payments_lines_data))
			payments_lines = payments_lines.rename(
				columns={0:'payment_id',1:'payment_invoice_line_id' ,2:'account_payment_id', 3:'payment_amount'})

			account_payment_table = "account_payment"
			self.env.cr.execute(
				"select id,payment_type,amount FROM "+account_payment_table+" ")
			account_payment_data = self._cr.fetchall()
			account_payment_frame = pd.DataFrame(list(account_payment_data))
			account_payment_frame = account_payment_frame.rename(
				columns={0: 'account_payment_id',1: 'account_payment_type',2: 'account_payment_amount'})
			payments_lines = pd.merge(payments_lines, account_payment_frame, how='left', left_on='account_payment_id',
									   right_on='account_payment_id')
			invoice_lines = pd.merge(invoice_lines,payments_lines, how='left', left_on='invoice_line_id',
									  right_on='payment_invoice_line_id')
			bsg_cargo_lines = pd.merge(bsg_cargo_lines,invoice_lines, how='left', left_on='self_id',
									 right_on='inv_line_cargo_sale_line_id')
			if data['invoicep_line_filter'] == 'paid':
				bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['inv_line_is_paid'] == True)]

			if data['invoicep_line_filter'] == 'unpaid':
				bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['inv_line_is_paid'] == False)]

		if data['with_cc']:
			credit_collection_table = "credit_customer_collection"
			self.env.cr.execute(
				"select id,name FROM " + credit_collection_table + " ")
			credit_collection_data = self._cr.fetchall()
			credit_collection_frame = pd.DataFrame(list(credit_collection_data))
			credit_collection_frame = credit_collection_frame.rename(
				columns={0: 'credit_collection_id', 1: 'credit_collection_name'})
			bsg_cargo_lines = pd.merge(bsg_cargo_lines, credit_collection_frame, how='left', left_on='credit_collection_id',
									   right_on='credit_collection_id')






		# bsg_cargo_lines = pd.merge(bsg_cargo_lines,invoice_frame, how='left', left_on='self_id',
		# 						   right_on='inv_cargo_sale_line_id')

		# bsg_cargo_lines = bsg_cargo_lines.sort_values(by='order_date')
		# bsg_cargo_lines = bsg_cargo_lines.drop_duplicates(subset='sale_line_rec_name', keep="first")

			
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
		worksheet = workbook.add_worksheet('Comprehensive Operations Report')


		worksheet.merge_range('A1:S1','Comprehensive Operations Report',merge_format)
		# worksheet.merge_range('A2:M2','معلومات الاتفاقية',main_heading)
		# worksheet.merge_range('A3:M3','Cargo Sale Information',main_heading)
		# worksheet.merge_range('N2:Z2','معلومات السيارة',main_heading)
		# worksheet.merge_range('N3:Z3','Car Information',main_heading)
		# worksheet.merge_range('AA2:AG2','معلومات الرحلة',main_heading)
		# worksheet.merge_range('AA3:AG3','Trip Information',main_heading)
		# worksheet.merge_range('AH2:AL2','السندات الادارية',main_heading)
		# worksheet.merge_range('AH3:AL3','Management Voucher',main_heading)
		# worksheet.merge_range('AM2:AR2','سندات القبض',main_heading)
		# worksheet.merge_range('AM3:AR3','Receipt Voucher',main_heading)
		# worksheet.merge_range('AS2:AW2','الفواتير',main_heading)
		# worksheet.merge_range('AS3:AW3','Invoices',main_heading)

		worksheet.set_column('A:M', 20)
		worksheet.set_column('N:Z', 18)
		worksheet.set_column('AA:AG', 20)
		worksheet.set_column('AH:AL', 18)
		worksheet.set_column('AM:AR', 20)
		worksheet.set_column('AS:AW', 20)
		worksheet.freeze_panes(3, 0)
		worksheet.freeze_panes(4, 0)
		worksheet.freeze_panes(5, 0)

		worksheet.write('A4', 'التاريخ', main_heading1)
		worksheet.write('B4', 'اسم العميل', main_heading1)
		worksheet.write('C4', 'نوع العميل', main_heading1)
		worksheet.write('D4', 'رقم الاتفاقية', main_heading1)
		worksheet.write('E4', 'فرع الشحن', main_heading1)
		worksheet.write('F4', 'فرع الوصول', main_heading1)
		worksheet.write('G4', 'تاريخ الوصول المتوقع', main_heading1)
		worksheet.write('H4', 'تاريخ الوصول الفعلي ', main_heading1)
		worksheet.write('I4', 'مبلغ الاتفاقية', main_heading1)
		worksheet.write('J4', 'طريقة الدفع', main_heading1)
		worksheet.write('K4', 'المستخدم', main_heading1)
		worksheet.write('L4', 'كود المستخدم', main_heading1)
		worksheet.write('M4', 'رقم سجل البمعات', main_heading1)
		worksheet.write('N4', 'حالة شحن السيارة', main_heading1)
		worksheet.write('O4', 'اسم المتلقي', main_heading1)
		worksheet.write('P4', 'رقم اللوحة', main_heading1)
		worksheet.write('Q4', 'رقم الشاسيه', main_heading1)
		worksheet.write('R4', 'موديل السيارة', main_heading1)
		worksheet.write('S4', 'حجم السيارة', main_heading1)
		worksheet.write('T4', 'نوع الشحن', main_heading1)
		worksheet.write('U4', 'السنة', main_heading1)
		if not data['with_summary']:
			worksheet.write('V4', 'رقم الفاتورة', main_heading1)
			worksheet.write('W4', 'وصف الفاتورة', main_heading1)
			worksheet.write('X4', 'قيمة الفاتورة', main_heading1)
			worksheet.write('Y4', 'فاتورة مرتجع', main_heading1)
			worksheet.write('Z4', 'فاتورة خدمات', main_heading1)
			worksheet.write('AA4', 'فاتورة أرضيات', main_heading1)
			worksheet.write('AB4', 'حالة الفاتورة', main_heading1)
			worksheet.write('AC4', 'رقم السند', main_heading1)
			worksheet.write('AD4', 'نوع السند', main_heading1)
			worksheet.write('AE4', 'إجمالي قيمة السند', main_heading1)
			worksheet.write('AF4', 'المسدد من السند علي السجل', main_heading1)
			worksheet.write('AG4', 'مرجع إشعار الخصم/الاتفاقية', main_heading1)
			worksheet.write('AH4', 'رقم اذن الخروج', main_heading1)
			worksheet.write('AI4', 'تاريخ اذن الخروج', main_heading1)
			worksheet.write('AJ4', 'حال السجل', main_heading1)
			if data['with_cc']:
				worksheet.write('AK4', 'الفاتورة المجمعة', main_heading1)
		else:
			worksheet.write('V4', 'رقم اذن الخروج', main_heading1)
			worksheet.write('W4', 'تاريخ اذن الخروج', main_heading1)
			worksheet.write('X4', 'حال السجل', main_heading1)
			if data['with_cc']:
				worksheet.write('Y4', 'الفاتورة المجمعة', main_heading1)

		worksheet.write('A5', 'Date', main_heading1)
		worksheet.write('B5', 'Partner', main_heading1)
		worksheet.write('C5', 'Partner Type', main_heading1)
		worksheet.write('D5', 'Cargo Sale Number', main_heading1)
		worksheet.write('E5', 'From', main_heading1)
		worksheet.write('F5', 'To', main_heading1)
		worksheet.write('G5', 'Expected Delivery Date', main_heading1)
		worksheet.write('H5', 'Delivery Date', main_heading1)
		worksheet.write('I5', 'Amount', main_heading1)
		worksheet.write('J5', 'Payment Method', main_heading1)
		worksheet.write('K5', 'User', main_heading1)
		worksheet.write('L5', 'User Cod', main_heading1)
		worksheet.write('M5', 'Cargo Sale Line NO.', main_heading1)
		worksheet.write('N5', 'Cargo Sale Line State', main_heading1)
		worksheet.write('O5', 'Receiver Name', main_heading1)
		worksheet.write('P5', 'Plate No', main_heading1)
		worksheet.write('Q5', 'Chasis No', main_heading1)
		worksheet.write('R5', 'Model', main_heading1)
		worksheet.write('S5', 'Car Size', main_heading1)
		worksheet.write('T5', 'Shipment Type', main_heading1)
		worksheet.write('U5', 'Year', main_heading1)
		if not data['with_summary']:
			worksheet.write('V5', 'Invoice Reference', main_heading1)
			worksheet.write('W5', 'Invoice Description', main_heading1)
			worksheet.write('X5', 'Invoice Amount with Taxes', main_heading1)
			worksheet.write('Y5', 'Is Refund', main_heading1)
			worksheet.write('Z5', 'Is Other Service', main_heading1)
			worksheet.write('AA5', 'Is Demurrage', main_heading1)
			worksheet.write('AB5', 'Is Paid ', main_heading1)
			worksheet.write('AC5', 'Voucher Number', main_heading1)
			worksheet.write('AD5', 'Voucher Type', main_heading1)
			worksheet.write('AE5', 'Voucher Total Amount', main_heading1)
			worksheet.write('AF5', 'Paid Amount', main_heading1)
			worksheet.write('AG5', 'Reference ', main_heading1)
			worksheet.write('AH5', 'Release Number', main_heading1)
			worksheet.write('AI5', 'Release Date', main_heading1)
			worksheet.write('AJ5', 'SO state', main_heading1)
			if data['with_cc']:
				worksheet.write('AK5', 'Collection Number', main_heading1)
		else:
			worksheet.write('V5', 'Release Number', main_heading1)
			worksheet.write('W5', 'Release Date', main_heading1)
			worksheet.write('X5', 'SO state', main_heading1)
			if data['with_cc']:
				worksheet.write('Y5', 'Collection Number', main_heading1)





		row = 5
		col = 0
		for index,line in bsg_cargo_lines.iterrows():

			order_date = " "
			if line['order_date']:
				order_date = line['order_date'] + timedelta(hours=3)
				order_date = str(order_date)[:16]
				order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')


			users_name = " "
			users_code = " "
			if line['create_uid'] > 0:
				#users_name_ids = self.env['res.users'].sudo().browse(int(line['create_uid']))
				users_name = line['res_users_name']
				users_code = line['res_users_login']

			is_so_paid = " "
			if line['self_id'] > 0:
				#so_line_id = self.env['bsg_vehicle_cargo_sale_line'].sudo().browse(int(line['self_id']))
				if line['is_so_paid']:
					is_so_paid = "Paid"
				else:
					is_so_paid = "Unpaid"

			if not data['with_summary']:
				is_paid = " "
				is_refund = " "
				is_other_service_line = " "
				is_demurrage_line = " "
				if line['invoice_line_id'] > 0:
					#invoice_line_ids = self.env['account.move.line'].sudo().browse(int(line['invoice_line_id']))
					if line['inv_line_is_paid']:
						is_paid = "True"
					else:
						is_paid = "False"
					if line['account_invoice_type'] in ('out_refund','in_refund'):
						is_refund = "True"
					else:
						is_refund = "False"
					if line['inv_line_is_other_service_line']:
						is_other_service_line = "True"
					else:
						is_other_service_line = "False"
					if line['inv_line_is_demurrage_line']:
						is_demurrage_line = "True"
					else:
						is_demurrage_line = "False"
					
					

			# trip_users_name = " "
			# trip_users_code = " "
			# if line['bsg_trip_create_uid'] > 0:
			# 	trip_users_ids = self.env['res.users'].sudo().browse(int(line['bsg_trip_create_uid']))
			# 	trip_users_name = trip_users_ids.name
			# 	trip_users_code = trip_users_ids.login
			#
			# report_users_name = " "
			# report_users_code = " "
			# if line['dr_user_id'] > 0:
			# 	report_users_ids = self.env['res.users'].sudo().browse(int(line['dr_user_id']))
			# 	report_users_name = report_users_ids.name
			# 	report_users_code = report_users_ids.login
			#
			# inv_users_name = " "
			# inv_users_code = " "
			# if line['inv_create_uid'] > 0:
			# 	inv_users_ids = self.env['res.users'].sudo().browse(int(line['inv_create_uid']))
			# 	inv_users_name = inv_users_ids.name
			# 	inv_users_code = inv_users_ids.login
			#
			# vouc_users_name = " "
			# vouc_users_code = " "
			# if line['voucher_create_uid'] > 0:
			# 	vouc_users_ids = self.env['res.users'].sudo().browse(int(line['voucher_create_uid']))
			# 	vouc_users_name = vouc_users_ids.name
			# 	vouc_users_code = vouc_users_ids.login

			# voucher_no = " "
			# voucher_amt = 0
			# voucher_date = " "
			# voucher_user = " "
			# voucher_user_cod = " "
			# if line['invoice_id'] > 0:
			# 	invoice_ids = self.env['account.move'].sudo().browse(int(line['invoice_id']))
			# 	if invoice_ids:
			# 		if invoice_ids.payment_ids:
			# 			for vouc in invoice_ids.payment_ids:
			# 				if voucher_no == " ":
			# 					voucher_no = str(vouc.name)
			# 				else:
			# 					voucher_no = voucher_no +' , '+ str(vouc.name)
			# 				voucher_amt = voucher_amt + vouc.amount
			# 				if voucher_date == " ":
			# 					voucher_date = str(vouc.payment_date)
			# 				else:
			# 					voucher_date = voucher_date+' , '+ str(vouc.payment_date)
			# 				if voucher_user == " ":
			# 					voucher_user = str(vouc.create_uid.name)
			# 				else:
			# 					voucher_user = voucher_user +' , '+ str(vouc.create_uid.name)
			# 				if voucher_user_cod == " ":
			# 					voucher_user_cod = str(vouc.create_uid.login)
			# 				else:
			# 					voucher_user_cod = voucher_user_cod +' , '+ str(vouc.create_uid.login)



			# shipment_type = ' '
			# if line['bsg_shipment_type'] == 'oneway':
			# 	shipment_type = 'شحن عادي'
			# if line['bsg_shipment_type'] == 'return':
			# 	shipment_type = 'جولة'
			#
			# expected_delivery = " "
			# if line['expected_delivery']:
			# 	expected_delivery = line['expected_delivery'] + timedelta(hours=3)
			# 	expected_delivery = str(expected_delivery)
			# 	expected_delivery = datetime.strptime(expected_delivery, '%Y-%m-%d').strftime('%d/%m/%Y')

			# actual_start_time = line['trip_arrival_start_time']
			# if '-' in actual_start_time:
			# 	actual_start_time = line['trip_arrival_start_time'] + timedelta(hours=3)
			# 	actual_start_time = str(actual_start_time)[:16]
			# 	actual_start_time = datetime.strptime(actual_start_time, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

			# scheduled_arrival_date = " "
			# scheduled_arrival_date = line['expected_end_date']
			# if '-' in scheduled_arrival_date:
			# 	scheduled_arrival_date = line['expected_end_date'] + timedelta(hours=3)
			# 	scheduled_arrival_date = str(scheduled_arrival_date)[:16]
			# 	scheduled_arrival_date = datetime.strptime(scheduled_arrival_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')




			# add_to_cc = ' '
			# if line['add_to_cc'] == True:
			# 	add_to_cc = 'True'
			# if line['add_to_cc'] == False:
			# 	add_to_cc = 'False'


			# actual_end_time = " "
			# if rec.sudo().fleet_trip_id.bsg_trip_arrival_ids:
			# 	last_arrival = rec.sudo().fleet_trip_id.bsg_trip_arrival_ids[-1]
			# 	if last_arrival.actual_end_time:
			# 		actual_end_time = last_arrival.actual_end_time + timedelta(hours=3)
			# 		actual_end_time = str(actual_end_time)[:16]
			# 		actual_end_time = datetime.strptime(actual_end_time, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

			# sale_line_id = self.env['bsg_vehicle_cargo_sale_line'].sudo().browse(int(line['self_id']))
			# charges = 0
			# if sale_line_id.car_make and sale_line_id.car_model:
			# 	charges = sale_line_id.unit_charge * (1.0 - sale_line_id.discount / 100.0)
			# 	charges = charges + sale_line_id.additional_ship_amount
			# 	if sale_line_id.tax_ids:
			# 		currency = sale_line_id.bsg_cargo_sale_id.currency_id or None
			# 		quantity = 1
			# 		product = sale_line_id.service_type.product_variant_id
			# 		taxes = sale_line_id.tax_ids.compute_all((charges + sale_line_id.amount_with_satah), currency,
			# 												 quantity,
			# 												 product=product, partner=sale_line_id.customer_id)
			# 		charges = taxes['total_included']
			# 	if sale_line_id.bsg_cargo_sale_id.company_currency_id.id != sale_line_id.bsg_cargo_sale_id.currency_id.id:
			# 		original_charges = sale_line_id.bsg_cargo_sale_id.currency_id._convert(
			# 			charges, sale_line_id.bsg_cargo_sale_id.company_currency_id, self.env.user.company_id,
			# 			sale_line_id.bsg_cargo_sale_id.order_date)
			# 	else:
			# 		original_charges = charges
			# if line['loc_from']:
				# is_international = self.env['bsg_route_waypoints'].sudo().browse(int(line['loc_from'])).is_international
				# charges = original_charges if is_international else line['charges_stored']
				# charges = line['charges_stored']
			payment_id = self.env['account.payment'].search([('id','=',int(line['account_payment_id']))],limit=1)
			worksheet.write_string(row, col, str(order_date), main_data)
			worksheet.write_string(row, col + 1, str(line['bsg_customer_name']), main_data)
			worksheet.write_string(row, col + 2, str(line['bsg_partnertype_name']), main_data)
			worksheet.write_string(row, col + 3, str(line['bsg_cargosale_name']), main_data)
			worksheet.write_string(row, col + 4, str(line['bsg_loc_from_name']), main_data)
			worksheet.write_string(row, col + 5, str(line['bsg_loc_to_name']), main_data)
			worksheet.write_string(row, col + 6, str(line['expected_delivery']), main_data)
			worksheet.write_string(row, col + 7, str(line['delivery_date']), main_data)
			worksheet.write_string(row, col + 8, str(line['charges_stored']), main_data)
			worksheet.write_string(row, col + 9, str(line['bsg_pay_method_name']), main_data)
			worksheet.write_string(row, col + 10, str(users_name), main_data)
			worksheet.write_string(row, col + 11, str(users_code), main_data)
			worksheet.write_string(row, col + 12, str(line['sale_line_rec_name']), main_data)
			worksheet.write_string(row, col + 13, str(line['state']), main_data)
			worksheet.write_string(row, col + 14, str(line['so_receiver_name']), main_data)
			worksheet.write_string(row, col + 15, str(line['plate_no']), main_data)
			worksheet.write_string(row, col + 16, str(line['chassis_no']), main_data)
			worksheet.write_string(row, col + 17, str(line['car_model_name']), main_data)
			worksheet.write_string(row, col + 18, str(line['car_size_name']), main_data)
			worksheet.write_string(row, col + 19, str(line['so_line_car_shipment_name']), main_data)
			worksheet.write_string(row, col + 20, str(line['car_year_name']), main_data)
			if not data['with_summary']:
				worksheet.write_string(row, col + 21, str(line['account_invoice_ref']), main_data)
				worksheet.write_string(row, col + 22, str(line['inv_line_description']), main_data)
				worksheet.write_string(row, col + 23, str(line['inv_price_total']), main_data)
				worksheet.write_string(row, col + 24, str(is_refund), main_data)
				worksheet.write_string(row, col + 25, str(is_other_service_line), main_data)
				worksheet.write_string(row, col + 26, str(is_demurrage_line), main_data)
				worksheet.write_string(row, col + 27, str(is_paid), main_data)
				worksheet.write_string(row, col + 28, str(payment_id.name), main_data)
				worksheet.write_string(row, col + 29, str(line['account_payment_type']), main_data)
				worksheet.write_string(row, col + 30, str(line['account_payment_amount']), main_data)
				worksheet.write_string(row, col + 31, str(line['payment_amount']), main_data)
				worksheet.write_string(row, col + 32, str(line['account_invoice_origin']), main_data)
				if line['dr_print_no']:
					worksheet.write_string(row, col + 33, str(line['dr_print_no']), main_data)
				worksheet.write_string(row, col + 34, str(line['dr_print_date']), main_data)
				worksheet.write_string(row, col + 35, str(is_so_paid), main_data)
				if data['with_cc']:
					worksheet.write_string(row, col + 36, str(line['credit_collection_name']), main_data)
				row += 1
			else:
				worksheet.write_string(row, col + 21, str(line['dr_print_no']), main_data)
				worksheet.write_string(row, col + 22, str(line['dr_print_date']), main_data)
				worksheet.write_string(row, col + 23, str(is_so_paid), main_data)
				if data['with_cc']:
					worksheet.write_string(row, col + 24, str(line['credit_collection_name']), main_data)
				row += 1

# dr_print_date = " "
			# if rec.sudo().delivery_report_history_ids:
			# 	delivery_report = rec.sudo().delivery_report_history_ids[0]
			# 	if delivery_report.dr_print_date:
			# 		dr_print_date = delivery_report.dr_print_date + timedelta(hours=3)
			# 		dr_print_date = str(dr_print_date)[:16]
			# 		dr_print_date = datetime.strptime(dr_print_date, '%Y-%m-%d %H:%M').strftime('%m/%d/%y %H:%M')

			# 	worksheet.write_string (row, col+33,str(delivery_report.dr_print_no),main_data)
			# 	worksheet.write_string (row, col+34,str(' '),main_data)
			# 	worksheet.write_string (row, col+35,str(dr_print_date),main_data)
			# 	worksheet.write_string (row, col+36,str(delivery_report.dr_user_id.name),main_data)
			# 	worksheet.write_string (row, col+37,str(delivery_report.dr_user_id.login),main_data)
			# else:



			# if rec.sudo().bsg_cargo_sale_id.invoice_ids:
			# 	inv_num =  ""
			# 	inv_user = ""
			# 	inv_user_cod = ""
			# 	for inv in rec.sudo().bsg_cargo_sale_id.invoice_ids:
			# 		inv_date = inv_date +' '+ str(inv.invoice_date)
			# 		inv_num = inv_num +' '+ str(inv.number)
			# 		inv_user = inv_user +' '+ str(inv.create_uid.name)
			# 		inv_user_cod = inv_user +' '+ str(inv.create_uid.login)
			# 		voucher_no = ""
			# 		voucher_amt = 0
			# 		voucher_date = ""
			# 		voucher_branch = ""
			# 		voucher_user = ""
			# 		voucher_user_cod = ""
			# 		if inv.payment_ids:
			# 			for vouc in inv.payment_ids:
			# 				voucher_no = voucher_no +' '+ str(vouc.name)
			# 				voucher_amt = voucher_amt + vouc.amount
			# 				voucher_date = voucher_date+' '+ str(vouc.payment_date)
			# 				voucher_branch = voucher_branch +' '+ str(vouc.branch_ids.branch_ar_name)
			# 				voucher_user = voucher_user +' '+ str(vouc.create_uid.name)
			# 				voucher_user_cod = voucher_user_cod +' '+ str(vouc.create_uid.login)

			# 	worksheet.write_string (row, col+38,str(voucher_no),main_data)
			# 	worksheet.write_string (row, col+39,str(voucher_amt),main_data)
			# 	worksheet.write_string (row, col+40,str(voucher_date),main_data)
			# 	worksheet.write_string (row, col+41,str(voucher_branch),main_data)
			# 	worksheet.write_string (row, col+42,str(voucher_user),main_data)
			# 	worksheet.write_string (row, col+43,str(voucher_user_cod),main_data)

			# 	worksheet.write_string (row, col+44,str(inv_date),main_data)
			# 	worksheet.write_string (row, col+45,str(inv_num),main_data)
			# 	worksheet.write_string (row, col+46,str(inv_user),main_data)
			# 	worksheet.write_string (row, col+47,str(inv_user_cod),main_data)
			# 	worksheet.write_string (row, col+48,str(add_to_cc),main_data)

				# invoice_ids = []
				# count = 0
				# for inv in rec.sudo().bsg_cargo_sale_id.invoice_ids:
				# 	if inv.payment_ids:
				# 		invoice_ids.append(inv)
				# 		count = 1
				# 		break
				# if count == 0:
				# 	invoice_ids = rec.sudo().bsg_cargo_sale_id.invoice_ids[0]

				# voucher_no = "-"
				# voucher_amt = 0
				# voucher_date = "-"
				# voucher_branch = "-"
				# voucher_user = "-"
				# voucher_user_cod = "-"
				# for vouc in invoice_ids:
				# 	if vouc.payment_ids:
				# 		pay_ids = vouc.payment_ids[0]
				# 		voucher_no = pay_ids.name
				# 		voucher_amt = pay_ids.amount
				# 		voucher_date = pay_ids.payment_date
				# 		voucher_branch = pay_ids.branch_ids.branch_ar_name
				# 		voucher_user = pay_ids.create_uid.name
				# 		voucher_user_cod = pay_ids.create_uid.login

				# 	worksheet.write_string (row, col+38,str(voucher_no),main_data)
				# 	worksheet.write_string (row, col+39,str(voucher_amt),main_data)
				# 	worksheet.write_string (row, col+40,str(voucher_date),main_data)
				# 	worksheet.write_string (row, col+41,str(voucher_branch),main_data)
				# 	worksheet.write_string (row, col+42,str(voucher_user),main_data)
				# 	worksheet.write_string (row, col+43,str(voucher_user_cod),main_data)

				# 	worksheet.write_string (row, col+44,str(vouc.invoice_date),main_data)
				# 	worksheet.write_string (row, col+45,str(vouc.number),main_data)
				# 	worksheet.write_string (row, col+46,str(vouc.create_uid.name),main_data)
				# 	worksheet.write_string (row, col+47,str(vouc.create_uid.login),main_data)
				# 	worksheet.write_string (row, col+48,str(add_to_cc),main_data)
			# else:

			# 	worksheet.write_string (row, col+38,str(' '),main_data)
			# 	worksheet.write_string (row, col+39,str(' '),main_data)
			# 	worksheet.write_string (row, col+40,str(' '),main_data)
			# 	worksheet.write_string (row, col+41,str(' '),main_data)
			# 	worksheet.write_string (row, col+42,str(' '),main_data)
			# 	worksheet.write_string (row, col+43,str(' '),main_data)

			# 	worksheet.write_string (row, col+44,str(' '),main_data)
			# 	worksheet.write_string (row, col+45,str(' '),main_data)
			# 	worksheet.write_string (row, col+46,str(' '),main_data)
			# 	worksheet.write_string (row, col+47,str(' '),main_data)
			# 	worksheet.write_string (row, col+48,str(add_to_cc),main_data)

			
			
		# 	loc = 'A'+str(row+1)
		# 	loc1 = 'C'+str(row+1)
		# 	loc15 = 'D'+str(row+1)
		# 	loc30 = 'E'+str(row+1)
		# 	loc45 = 'F'+str(row+1)
		# 	loc60 = 'G'+str(row+1)
		# 	loc75 = 'H'+str(row+1)
		# 	loc90 = 'I'+str(row+1)

		# 	end_loc = str(loc)+':'+str(loc1)
		# 	worksheet.merge_range(str(end_loc), 'Total' ,main_heading)
		# 	worksheet.write_string(str(loc15),str(deb1),main_heading1)
		# 	worksheet.write_string(str(loc30),str(deb2),main_heading1)
		# 	worksheet.write_string(str(loc45),str(deb3),main_heading1)
		# 	worksheet.write_string(str(loc60),str(deb4),main_heading1)
		# 	worksheet.write_string(str(loc75),str(deb5),main_heading1)
		# 	worksheet.write_string(str(loc90),str(deb6),main_heading1)

				
			

	
