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
from odoo import models, fields, api
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class CargoSalelineReportXlsx(models.TransientModel):
	_name = 'report.cargosaleline_details_report.cargos_details_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'

	# @api.multi
	def generate_xlsx_report(self, workbook, input_records, lines):
		data = input_records['form']

		table_name = "bsg_vehicle_cargo_sale_line"
		self.env.cr.execute("select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,chassis_no,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one,charges_stored, final_price_stored, invoice_state_stored,receiver_name,receiver_mob_no FROM "+table_name+" ")
		result = self._cr.fetchall()
		bsg_cargo_lines = pd.DataFrame(list(result))
		bsg_cargo_lines = bsg_cargo_lines.rename(columns={0: 'self_id',1: 'order_date',2: 'loc_from_branch_id',3: 'loc_to',4: 'create_uid',5: 'bsg_cargo_sale_id',6: 'payment_method',7: 'customer_id',8: 'chassis_no',9: 'state',10: 'fleet_trip_id',11: 'loc_from',12: 'pickup_loc',13: 'car_model',14: 'year',15: 'car_color',16: 'sale_line_rec_name',17: 'expected_delivery',18: 'add_to_cc',19: 'plate_no',20: 'car_make',21: 'palte_one',22: 'charges_stored',23: 'final_price_stored',24: 'invoice_state_stored',25: 'receiver_name',26: 'receiver_mob_no'})

		bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'] >= data['form']) & (bsg_cargo_lines['order_date'] <= data['to'])]

		
		if data['branch_type'] == 'specific':
			branches = []
			for b in data['ship_loc']:
				branches.append(b)

			bsg_cargo_lines = bsg_cargo_lines[bsg_cargo_lines['loc_from_branch_id'].isin(branches)]

		if data['branch_type_to'] == 'specific':
			branches_to = []
			for b in data['drop_loc']:
				branches_to.append(b)

			bsg_cargo_lines = bsg_cargo_lines[bsg_cargo_lines['loc_to'].isin(branches_to)]

		if data['user_type'] == 'specific':
			users = []
			for b in data['users']:
				users.append(b)

			bsg_cargo_lines = bsg_cargo_lines[bsg_cargo_lines['create_uid'].isin(users)]

		if data['pay_case'] == 'paid':


			bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['invoice_state_stored'] == 'paid')]

			

		if data['pay_case'] == 'not_paid':

			bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['invoice_state_stored'] != 'paid')]


			
		if data['payment_method_filter'] == 'specific':
			payment_methods = []
			for pay in data['payment_method_ids']:
				payment_methods.append(pay)

			bsg_cargo_lines = bsg_cargo_lines[bsg_cargo_lines['payment_method'].isin(payment_methods)]

		if data['customer_filter'] == 'specific':
			cust_ids = []
			for pay in data['customer_ids']:
				cust_ids.append(pay)

			bsg_cargo_lines = bsg_cargo_lines[bsg_cargo_lines['customer_id'].isin(cust_ids)]


		if data['state'] != 'all':

			bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] == data['state'])]

		if data['trip_type'] != 'all':

			trip_frame_table = "fleet_vehicle_trip"
			self.env.cr.execute("select id,trip_type FROM "+trip_frame_table+" ")
			result_trip_frame_table = self._cr.fetchall()
			trip_frame = pd.DataFrame(list(result_trip_frame_table))
			trip_frame = trip_frame.rename(columns={0: 'trip_id',1: 'trip_type'})


			trip_frame = trip_frame.loc[(trip_frame['trip_type'] == data['trip_type'])]
			bsg_cargo_lines = pd.merge(bsg_cargo_lines,trip_frame,  how='left', left_on='fleet_trip_id', right_on ='trip_id')

			bsg_cargo_lines = bsg_cargo_lines[bsg_cargo_lines.trip_id.notnull()]

		if data['g_state'] == 'posted':
			trip_frame_history = "bsg_sale_line_trip_history"
			self.env.cr.execute("select id,trip_type,cargo_sale_line_id FROM "+trip_frame_history+" ")
			result_trip_frame_history = self._cr.fetchall()
			trip_history = pd.DataFrame(list(result_trip_frame_history))
			trip_history = trip_history.rename(columns={0: 'trip_his_id',1: 'trip_his_type',2: 'cargo_sale_line_id'})

			trip_history = trip_history.sort_values(by=['cargo_sale_line_id','trip_his_id'])
			trip_history = trip_history.drop_duplicates(subset='cargo_sale_line_id', keep="last")
			bsg_cargo_lines = pd.merge(bsg_cargo_lines,trip_history,  how='left', left_on='self_id', right_on ='cargo_sale_line_id')

			bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines.cargo_sale_line_id.notnull())]

		if data['g_state'] == 'non_posted':
			trip_frame_history = "bsg_sale_line_trip_history"
			self.env.cr.execute("select id,trip_type,cargo_sale_line_id FROM "+trip_frame_history+" ")
			result_trip_frame_history = self._cr.fetchall()
			trip_history = pd.DataFrame(list(result_trip_frame_history))
			trip_history = trip_history.rename(columns={0: 'trip_his_id',1: 'trip_his_type',2: 'cargo_sale_line_id'})

			trip_history = trip_history.sort_values(by=['cargo_sale_line_id','trip_his_id'])
			trip_history = trip_history.drop_duplicates(subset='cargo_sale_line_id', keep="last")
			bsg_cargo_lines = pd.merge(bsg_cargo_lines,trip_history,  how='left', left_on='self_id', right_on ='cargo_sale_line_id')

			bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines.cargo_sale_line_id.isnull())]
			
		if data['cargo_sale_type'] == 'local':

			bsg_cargo_table = "bsg_vehicle_cargo_sale"
			self.env.cr.execute("select id,cargo_sale_type FROM "+bsg_cargo_table+" ")
			result_bsg_cargo_table = self._cr.fetchall()
			bsg_cargo = pd.DataFrame(list(result_bsg_cargo_table))
			bsg_cargo = bsg_cargo.rename(columns={0: 'bsg_cargo_id',1: 'cargo_sale_type'})
			bsg_cargo = bsg_cargo.loc[(bsg_cargo['cargo_sale_type'] == 'local')]
			
			bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_cargo,  how='left', left_on='bsg_cargo_sale_id', right_on ='bsg_cargo_id')

			bsg_cargo_lines = bsg_cargo_lines[bsg_cargo_lines.bsg_cargo_id.notnull()]

		if data['cargo_sale_type'] == 'international':

			bsg_cargo_table = "bsg_vehicle_cargo_sale"
			self.env.cr.execute("select id,cargo_sale_type FROM "+bsg_cargo_table+" ")
			result_bsg_cargo_table = self._cr.fetchall()
			bsg_cargo = pd.DataFrame(list(result_bsg_cargo_table))
			bsg_cargo = bsg_cargo.rename(columns={0: 'bsg_cargo_id',1: 'cargo_sale_type'})
			bsg_cargo = bsg_cargo.loc[(bsg_cargo['cargo_sale_type'] == 'international')]
			
			bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_cargo,  how='left', left_on='bsg_cargo_sale_id', right_on ='bsg_cargo_id')

			bsg_cargo_lines = bsg_cargo_lines[bsg_cargo_lines.bsg_cargo_id.notnull()]

		
		bsg_cargo_table = "bsg_vehicle_cargo_sale"
		self.env.cr.execute("select id,name,shipment_type,partner_types,cargo_invoice_to,state,total_amount FROM "+bsg_cargo_table+" ")
		result_bsg_cargo_table = self._cr.fetchall()
		bsg_cargo = pd.DataFrame(list(result_bsg_cargo_table))
		bsg_cargo = bsg_cargo.rename(columns={0: 'bsg_cargo_id_final',1: 'bsg_cargosale_name',2: 'bsg_shipment_type',3: 'bsg_partner_type',4: 'cargo_invoice_to',5: 'bsg_state',6: 'total_amount'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_cargo,  how='left', left_on='bsg_cargo_sale_id', right_on ='bsg_cargo_id_final')


		bsg_customer_table = "res_partner"
		self.env.cr.execute("select id,name FROM "+bsg_customer_table+" ")
		result_bsg_customer = self._cr.fetchall()
		bsg_customer_frame = pd.DataFrame(list(result_bsg_customer))
		bsg_customer_frame = bsg_customer_frame.rename(columns={0: 'bsg_customer_id',1: 'bsg_customer_name'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_customer_frame,  how='left', left_on='customer_id', right_on ='bsg_customer_id')

		bsg_inv_to_table = "res_partner"
		self.env.cr.execute("select id,name FROM "+bsg_inv_to_table+" ")
		result_bsg_inv_to = self._cr.fetchall()
		bsg_inv_to_frame = pd.DataFrame(list(result_bsg_inv_to))
		bsg_inv_to_frame = bsg_inv_to_frame.rename(columns={0: 'invoice_to_id',1: 'invoice_to_name'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_inv_to_frame,  how='left', left_on='cargo_invoice_to', right_on ='invoice_to_id')

		bsg_partner_type_table = "partner_type"
		self.env.cr.execute("select id,name FROM "+bsg_partner_type_table+" ")
		result_bsg_partner_type = self._cr.fetchall()
		bsg_partner_type_frame = pd.DataFrame(list(result_bsg_partner_type))
		bsg_partner_type_frame = bsg_partner_type_frame.rename(columns={0: 'bsg_partner_type_id',1: 'bsg_partnertype_name'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_partner_type_frame,  how='left', left_on='bsg_partner_type', right_on ='bsg_partner_type_id')


		loc_from_frame_table = "bsg_route_waypoints"
		self.env.cr.execute("select id,route_waypoint_name FROM "+loc_from_frame_table+" ")
		result_loc_from_frame = self._cr.fetchall()
		loc_from_frame = pd.DataFrame(list(result_loc_from_frame))
		loc_from_frame = loc_from_frame.rename(columns={0: 'bsg_loc_from_id',1: 'bsg_loc_from_name'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,loc_from_frame,  how='left', left_on='loc_from', right_on ='bsg_loc_from_id')

		loc_to_frame_table = "bsg_route_waypoints"
		self.env.cr.execute("select id,route_waypoint_name FROM "+loc_to_frame_table+" ")
		result_loc_to_frame = self._cr.fetchall()
		loc_to_frame = pd.DataFrame(list(result_loc_to_frame))
		loc_to_frame = loc_to_frame.rename(columns={0: 'bsg_loc_to_id',1: 'bsg_loc_to_name'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,loc_to_frame,  how='left', left_on='loc_to', right_on ='bsg_loc_to_id')

		loc_pickup_frame_table = "bsg_route_waypoints"
		self.env.cr.execute("select id,route_waypoint_name FROM "+loc_pickup_frame_table+" ")
		result_loc_pickup_frame = self._cr.fetchall()
		loc_pickup_frame = pd.DataFrame(list(result_loc_pickup_frame))
		loc_pickup_frame = loc_pickup_frame.rename(columns={0: 'bsg_loc_to_id',1: 'bsg_loc_pickup_name'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,loc_pickup_frame,  how='left', left_on='pickup_loc', right_on ='bsg_loc_to_id')

		payment_frame_table = "cargo_payment_method"
		self.env.cr.execute("select id,payment_method_name FROM "+payment_frame_table+" ")
		result_payment_frame = self._cr.fetchall()
		payment_frame = pd.DataFrame(list(result_payment_frame))
		payment_frame = payment_frame.rename(columns={0: 'bsg_pay_method_id',1: 'bsg_pay_method_name'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,payment_frame,  how='left', left_on='payment_method', right_on ='bsg_pay_method_id')

		car_model_frame_table = "bsg_car_model"
		self.env.cr.execute("select id,car_model_name FROM "+car_model_frame_table+" ")
		result_car_model_frame = self._cr.fetchall()
		car_model_frame = pd.DataFrame(list(result_car_model_frame))
		car_model_frame = car_model_frame.rename(columns={0: 'car_model_id',1: 'car_model_name'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,car_model_frame,  how='left', left_on='car_model', right_on ='car_model_id')

		car_year_frame_table = "bsg_car_year"
		self.env.cr.execute("select id,car_year_name FROM "+car_year_frame_table+" ")
		result_car_year_frame = self._cr.fetchall()
		car_year_frame = pd.DataFrame(list(result_car_year_frame))
		car_year_frame = car_year_frame.rename(columns={0: 'car_year_id',1: 'car_year_name'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,car_year_frame,  how='left', left_on='year', right_on ='car_year_id')

		car_color_frame_table = "bsg_vehicle_color"
		self.env.cr.execute("select id,vehicle_color_name FROM "+car_color_frame_table+" ")
		result_car_color_frame = self._cr.fetchall()
		car_color_frame = pd.DataFrame(list(result_car_color_frame))
		car_color_frame = car_color_frame.rename(columns={0: 'car_color_id',1: 'vehicle_color_name'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,car_color_frame,  how='left', left_on='car_color', right_on ='car_color_id')

		bsg_trip_frame_table = "fleet_vehicle_trip"
		self.env.cr.execute("select id,state,name,create_uid,vehicle_id,expected_end_date FROM "+bsg_trip_frame_table+" ")
		result_bsg_trip_frame = self._cr.fetchall()
		bsg_trip_frame = pd.DataFrame(list(result_bsg_trip_frame))
		bsg_trip_frame = bsg_trip_frame.rename(columns={0: 'bsg_trip_id',1: 'bsg_trip_state',2: 'bsg_trip_name',3: 'bsg_trip_create_uid',4: 'trip_vehicle_id',5: 'expected_end_date'})

		bsgtrip_frame_history = "bsg_sale_line_trip_history"
		self.env.cr.execute("select id,trip_type,cargo_sale_line_id,fleet_trip_id FROM "+bsgtrip_frame_history+" ")
		bsgresult_trip_frame_history = self._cr.fetchall()
		bsgtrip_history = pd.DataFrame(list(bsgresult_trip_frame_history))
		bsgtrip_history = bsgtrip_history.rename(columns={0: 'bsgtrip_his_id',1: 'bsgtrip_his_type',2: 'bsgcargo_sale_line_id',3: 'fleet_trip_id_his'})

		bsgtrip_history = bsgtrip_history.sort_values(by=['bsgcargo_sale_line_id','bsgtrip_his_id'])
		bsgtrip_history = bsgtrip_history.drop_duplicates(subset='bsgcargo_sale_line_id', keep="last")
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsgtrip_history,  how='left', left_on='self_id', right_on ='bsgcargo_sale_line_id')

		bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_trip_frame,  how='left', left_on='fleet_trip_id_his', right_on ='bsg_trip_id')

		bsg_vehicle_frame_table = "fleet_vehicle"
		self.env.cr.execute("select id,current_loc_id,current_branch_id,taq_number FROM "+bsg_vehicle_frame_table+" ")
		result_bsg_vehicle_frame = self._cr.fetchall()
		bsg_vehicle_frame = pd.DataFrame(list(result_bsg_vehicle_frame))
		bsg_vehicle_frame = bsg_vehicle_frame.rename(columns={0: 'bsg_vehicle_id',1: 'bsg_vehicle_loc_name',2: 'bsg_vehicle_branch_name',3: 'taq_number'})

		bsg_arrival_frame_table = "fleet_trip_arrival_line"
		self.env.cr.execute("select id,delivery_id,actual_start_time,drawer_no FROM "+bsg_arrival_frame_table+" ")
		result_bsg_arrival_frame = self._cr.fetchall()
		bsg_arrival_frame = pd.DataFrame(list(result_bsg_arrival_frame))
		bsg_arrival_frame = bsg_arrival_frame.rename(columns={0: 'bsg_trip_id',1: 'trip_arrival_id',2: 'trip_arrival_start_time',3: 'drawer_no'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_arrival_frame,  how='left', left_on='bsg_cargo_id_final', right_on ='trip_arrival_id')

		report_history_frame_table = "report_history_delivery"
		self.env.cr.execute("select cargo_so_line_id,dr_print_no,dr_user_id,dr_print_date FROM "+report_history_frame_table+" ")
		result_report_history_frame = self._cr.fetchall()
		report_history_frame = pd.DataFrame(list(result_report_history_frame))
		report_history_frame = report_history_frame.rename(columns={0: 'cargo_so_line_id',1: 'dr_print_no',2: 'dr_user_id',3: 'dr_print_date'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,report_history_frame,  how='left', left_on='self_id', right_on ='cargo_so_line_id')

		account_inv_frame_table = "account_invoice"
		self.env.cr.execute("select id,cargo_sale_id,date_invoice,create_uid,number,amount_total FROM "+account_inv_frame_table+" where cargo_sale_id is not null ")
		result_account_inv_frame = self._cr.fetchall()
		account_inv_frame = pd.DataFrame(list(result_account_inv_frame))
		account_inv_frame = account_inv_frame.rename(columns={0: 'invoice_id',1: 'cargo_sale_id',2: 'date_invoice',3: 'inv_create_uid',4: 'inv_number',5: 'amount_total'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,account_inv_frame,  how='left', left_on='bsg_cargo_id_final', right_on ='cargo_sale_id')

		account_pay_frame_table = "account_payment"
		self.env.cr.execute("select id,name,amount,payment_date,create_uid,cargo_sale_order_id,branch_ids FROM "+account_pay_frame_table+" where cargo_sale_order_id is not null ")
		result_account_pay_frame = self._cr.fetchall()
		account_pay_frame = pd.DataFrame(list(result_account_pay_frame))
		account_pay_frame = account_pay_frame.rename(columns={0: 'voucher_id',4: 'voucher_create_uid',1: 'voucher_number',2: 'voucher_amount',5: 'voucher_sale_order_id',3: 'payment_date',6: 'branch_ids'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,account_pay_frame,  how='left', left_on='bsg_cargo_id_final', right_on ='voucher_sale_order_id')

		branches_frame_table = "bsg_branches_bsg_branches"
		self.env.cr.execute("select id,branch_ar_name FROM "+branches_frame_table+" ")
		result_branches_frame = self._cr.fetchall()
		branches_frame = pd.DataFrame(list(result_branches_frame))
		branches_frame = branches_frame.rename(columns={0: 'bsg_branch_id',1: 'bsg_branch_name'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,branches_frame,  how='left', left_on='branch_ids', right_on ='bsg_branch_id')

		bsg_cargo_lines = pd.merge(bsg_cargo_lines,bsg_vehicle_frame,  how='left', left_on='trip_vehicle_id', right_on ='bsg_vehicle_id')

		branch_veh_frame_table = "bsg_branches_bsg_branches"
		self.env.cr.execute("select id,branch_ar_name FROM "+branch_veh_frame_table+" ")
		result_branch_veh_frame = self._cr.fetchall()
		branch_veh_frame = pd.DataFrame(list(result_branch_veh_frame))
		branch_veh_frame = branch_veh_frame.rename(columns={0: 'bsg_veh_branch_id',1: 'bsg_veh_branch_name'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,branch_veh_frame,  how='left', left_on='bsg_vehicle_branch_name', right_on ='bsg_veh_branch_id')

		carconfig_frame_table = "bsg_car_config"
		self.env.cr.execute("select id,car_maker FROM "+carconfig_frame_table+" ")
		result_carconfig_frame = self._cr.fetchall()
		carconfig_frame = pd.DataFrame(list(result_carconfig_frame))
		carconfig_frame = carconfig_frame.rename(columns={0: 'car_config_id',1: 'car_make_id'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,carconfig_frame,  how='left', left_on='car_make', right_on ='car_config_id')

		carconfiglines_frame_table = "bsg_car_line"
		self.env.cr.execute("select id,car_config_id,car_model,car_size FROM "+carconfiglines_frame_table+" ")
		result_carconfiglines_frame = self._cr.fetchall()
		carconfiglines_frame = pd.DataFrame(list(result_carconfiglines_frame))
		carconfiglines_frame = carconfiglines_frame.rename(columns={0: 'car_configline_id',1: 'car_configrelated_id',2: 'car_modelline_id',3: 'car_sizeline_id'})

		bsg_cargo_lines = pd.merge(bsg_cargo_lines,carconfiglines_frame,  how='left', left_on=['car_make','car_model'], right_on =['car_configrelated_id','car_modelline_id'])

		carsize_frame_table = "bsg_car_size"
		self.env.cr.execute("select id,car_size_name FROM "+carsize_frame_table+" ")
		result_carsize_frame = self._cr.fetchall()
		carsize_frame = pd.DataFrame(list(result_carsize_frame))
		carsize_frame = carsize_frame.rename(columns={0: 'car_size_id',1: 'car_size_name'})

		bsg_cargo_lines = pd.merge(bsg_cargo_lines,carsize_frame,  how='left', left_on='car_sizeline_id', right_on ='car_size_id')

		car_maker_frame_table = "bsg_car_make"
		self.env.cr.execute("select id,car_make_name,car_make_ar_name FROM "+car_maker_frame_table+" ")
		result_car_maker_frame = self._cr.fetchall()
		car_maker_frame = pd.DataFrame(list(result_car_maker_frame))
		car_maker_frame = car_maker_frame.rename(columns={0: 'car_maker_id',1: 'car_make_name',2: 'car_make_ar_name'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,car_maker_frame,  how='left', left_on='car_make_id', right_on ='car_maker_id')

		fleet_arrival_frame_table = "fleet_trip_arrival"
		self.env.cr.execute("select id,actual_end_time,trip_id FROM "+fleet_arrival_frame_table+" ")
		result_fleet_arrival_frame = self._cr.fetchall()
		fleet_arrival_frame = pd.DataFrame(list(result_fleet_arrival_frame))
		fleet_arrival_frame = fleet_arrival_frame.rename(columns={0: 'arrival_screen_id',1: 'arrival_screen_time',2: 'arrival_screenrelated_id'})
		temp_arrival_frame = pd.merge(bsg_trip_frame,fleet_arrival_frame,  how='left', left_on='bsg_trip_id', right_on ='arrival_screenrelated_id')

		temp_arrival_frame = temp_arrival_frame.sort_values(by=['bsg_trip_id','arrival_screen_id'])
		temp_arrival_frame = temp_arrival_frame.drop_duplicates(subset='bsg_trip_id', keep="last")
		temp_arrival_frame = temp_arrival_frame[['bsg_trip_id','arrival_screen_time']]
		temp_arrival_frame = temp_arrival_frame.rename(columns={'bsg_trip_id': 'bsg_trip_screen_id'})
		bsg_cargo_lines = pd.merge(bsg_cargo_lines,temp_arrival_frame,  how='left', left_on='fleet_trip_id', right_on ='bsg_trip_screen_id')

		bsg_cargo_lines = bsg_cargo_lines.sort_values(by='order_date')
		bsg_cargo_lines = bsg_cargo_lines.drop_duplicates(subset='sale_line_rec_name', keep="first")


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
		worksheet = workbook.add_worksheet('Cargo Sale Line Details Report')

		branches_from = " "
		if data['branch_type'] == 'specific':
			branches_to_ids = self.env['bsg_branches.bsg_branches'].search([('id','in',data['ship_loc'])])
			for a in branches_to_ids:
				branches_from = branches_from +','+ str(a.branch_ar_name)
		else:
			branches_from = "All"

		branches_to = " "
		if data['branch_type_to'] == 'specific':
			branches_drop_ids = self.env['bsg_route_waypoints'].search([('id','in',data['drop_loc'])])
			for b in branches_drop_ids:
				branches_to = branches_to +','+ str(b.route_waypoint_name)
		else:
			branches_to = "All"

		pay_method_name = " "
		if data['payment_method_filter'] == 'specific':
			pay_ids = self.env['cargo_payment_method'].search([('id','in',data['payment_method_ids'])])
			for c in pay_ids:
				pay_method_name = pay_method_name +','+ str(c.payment_method_name)
		else:
			pay_method_name = "All"

		customers_name = " "
		if data['customer_filter'] == 'specific':
			cust_ids = self.env['res.partner'].search([('id','in',data['customer_ids'])])
			for d in cust_ids:
				customers_name = customers_name +','+ str(d.name)
		else:
			customers_name = "All"

		user_name = " "
		if data['user_type'] == 'specific':
			user_ids = self.env['res.users'].search([('id','in',data['users'])])
			for e in user_ids:
				user_name = user_name +','+ str(e.name)
		else:
			user_name = "All"



		if data['report_type'] == '01':
			report_type = 'بوسيلة‬ الدفع‬'
			worksheet.merge_range('A1:M1','Cargo Sale Line Details Report',merge_format)
			worksheet.write('A2', 'Date From', main_heading)
			worksheet.write('B2', str(data['form']), main_data)
			worksheet.write('D2', 'Drop Location', main_heading)
			worksheet.write('E2', str(branches_to), main_data)
			worksheet.write('A3', 'Date To', main_heading)
			worksheet.write('B3', str(data['to']), main_data)
			worksheet.write('D3', 'Shipping Location', main_heading)
			worksheet.write('E3', str(branches_from), main_data)
			worksheet.write('A4', 'Payment State', main_heading)
			worksheet.write('B4', str(data['pay_case']), main_data)
			worksheet.write('D4', 'Payment Method', main_heading)
			worksheet.write('E4', str(pay_method_name), main_data)
			worksheet.write('A5', 'Customer', main_heading)
			worksheet.write('B5', str(customers_name), main_data)
			worksheet.write('D5', 'Cargo Sale Type', main_heading)
			worksheet.write('E5', str(data['cargo_sale_type']), main_data)
			worksheet.write('A6', 'Trip Type', main_heading)
			worksheet.write('B6', str(data['trip_type']), main_data)
			worksheet.write('D6', 'Cargo Sale Line State', main_heading)
			worksheet.write('E6', str(data['state']), main_data)
			worksheet.write('A7', 'Invoice State', main_heading)
			worksheet.write('B7', str(data['inv_state']), main_data)
			worksheet.write('D7', 'User', main_heading)
			worksheet.write('E7', str(user_name), main_data)
			worksheet.write('A8', 'Report Type', main_heading)
			worksheet.write('B8', str(report_type), main_data)

			worksheet.set_column('A:M', 20)
			
			worksheet.write('A10', '‫السيارة‬ ‫شحن‬ ‫حالة‬', main_heading1)
			worksheet.write('B10', '‫المستخدم‬ ‫كود‬', main_heading1)
			worksheet.write('C10', '‫المستخدم‬', main_heading1)
			worksheet.write('D10', '‫‫رقم‬ الفاتورة‬', main_heading1)
			worksheet.write('E10', '‫السداد‬ ‫حالة‬', main_heading1)
			worksheet.write('F10', '‫المسدد‬', main_heading1)
			worksheet.write('G10', '‫الشحن‬ ‫رسوم‬', main_heading1)
			worksheet.write('H10', '‫الدفع‬ ‫طريقة‬', main_heading1)
			worksheet.write('I10', '‫الى‬ ‫مشحونة‬', main_heading1)
			worksheet.write('J10', '‫اللوحة‬ ‫رقم‬', main_heading1)
			worksheet.write('K10', '‫العميل‬ ‫اسم‬', main_heading1)
			worksheet.write('L10', '‫الطلب‬ ‫تاريخ‬', main_heading1)
			worksheet.write('M10', '‫المبيعات‬ ‫سجل‬ ‫رقم‬', main_heading1)

			worksheet.write('A11', '‫Cargo Sale Line state', main_heading1)
			worksheet.write('B11', '‫User Cod', main_heading1)
			worksheet.write('C11', '‫User', main_heading1)
			worksheet.write('D11', '‫Invoice No.', main_heading1)
			worksheet.write('E11', '‫Payment State', main_heading1)
			worksheet.write('F11', 'Receipt', main_heading1)
			worksheet.write('G11', '‫Charges', main_heading1)
			worksheet.write('H11', 'Payment Method', main_heading1)
			worksheet.write('I11', '‫To', main_heading1)
			worksheet.write('J11', 'Plate No', main_heading1)
			worksheet.write('K11', '‫Customer', main_heading1)
			worksheet.write('L11', '‫Order Date', main_heading1)
			worksheet.write('M11', '‫Cargo Sale Line No', main_heading1)


			row = 11
			col = 0

			
			if data['inv_state'] == 'with_invoice':

				payment_method_ids = self.env['cargo_payment_method'].search([('payment_type','in',('cash','pod'))]).ids

				payment_method_credit = self.env['cargo_payment_method'].search([('payment_type','=','credit')]).ids

				one_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_ids) & bsg_cargo_lines['invoice_state_stored'].isin(['open','paid'])]

				two_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_credit) & (bsg_cargo_lines['add_to_cc'] == True)]

				finalframe = [one_bsg_frame, two_bsg_frame]
				finalframe = pd.concat(finalframe)

				for index,line in finalframe.iterrows():
					users_name = " "
					users_code = " "
					if line['create_uid'] > 0:
						users_name_ids = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['create_uid']))
						users_name = users_name_ids.name
						users_code = users_name_ids.login

					order_date = " "
					if line['order_date']:
						order_date = line['order_date'] + timedelta(hours=3)
						order_date = str(order_date)[:16]
						order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

					voucher_no = " "
					voucher_amt = 0
					voucher_date = " "
					voucher_user = " "
					voucher_user_cod = " "
					if line['invoice_id'] > 0:
						invoice_ids = self.env['account.invoice'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['invoice_id']))
						if invoice_ids:
							if invoice_ids.payment_ids:
								for vouc in invoice_ids.payment_ids:
									if voucher_no == " ":
										voucher_no = str(vouc.name)
									else:
										voucher_no = voucher_no +' , '+ str(vouc.name)
									voucher_amt = voucher_amt + vouc.amount
									if voucher_date == " ":
										voucher_date = str(vouc.payment_date)
									else:
										voucher_date = voucher_date+' , '+ str(vouc.payment_date)
									if voucher_user == " ":
										voucher_user = str(vouc.create_uid.name)
									else:
										voucher_user = voucher_user +' , '+ str(vouc.create_uid.name)
									if voucher_user_cod == " ":
										voucher_user_cod = str(vouc.create_uid.login)
									else:
										voucher_user_cod = voucher_user_cod +' , '+ str(vouc.create_uid.login)


					worksheet.write_string (row, col,str(line['state']),main_data)
					worksheet.write_string (row, col+1,str(users_code),main_data)
					worksheet.write_string (row, col+2,str(users_name),main_data)
					worksheet.write_string (row, col+3,str(voucher_no),main_data)
					worksheet.write_string (row, col+4,str(line['invoice_state_stored']),main_data)
					worksheet.write_string (row, col+5,str(voucher_amt),main_data)
					worksheet.write_string (row, col+6,str(line['charges_stored']),main_data)
					worksheet.write_string (row, col+7,str(line['bsg_pay_method_name']),main_data)
					worksheet.write_string (row, col+8,str(line['bsg_loc_to_name']),main_data)
					worksheet.write_string (row, col+9,str(line['plate_no']),main_data)
					worksheet.write_string (row, col+10,str(line['bsg_customer_name']),main_data)
					worksheet.write_string (row, col+11,str(order_date),main_data)
					worksheet.write_string (row, col+12,str(line['sale_line_rec_name']),main_data)


					row += 1


			if data['inv_state'] == 'without_invoice':

				payment_method_ids = self.env['cargo_payment_method'].search([('payment_type','in',('cash','pod'))]).ids

				payment_method_credit = self.env['cargo_payment_method'].search([('payment_type','=','credit')]).ids

				one_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_ids) & bsg_cargo_lines['invoice_state_stored'].isnull()]

				two_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_credit) & (bsg_cargo_lines['add_to_cc'] == False)]

				finalframe = [one_bsg_frame, two_bsg_frame]
				finalframe = pd.concat(finalframe)

				for index,line in finalframe.iterrows():
					users_name = " "
					users_code = " "
					if line['create_uid'] > 0:
						users_name_ids = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['create_uid']))
						users_name = users_name_ids.name
						users_code = users_name_ids.login

					order_date = " "
					if line['order_date']:
						order_date = line['order_date'] + timedelta(hours=3)
						order_date = str(order_date)[:16]
						order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

					voucher_no = " "
					voucher_amt = 0
					voucher_date = " "
					voucher_user = " "
					voucher_user_cod = " "
					if line['invoice_id'] > 0:
						invoice_ids = self.env['account.invoice'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['invoice_id']))
						if invoice_ids:
							if invoice_ids.payment_ids:
								for vouc in invoice_ids.payment_ids:
									if voucher_no == " ":
										voucher_no = str(vouc.name)
									else:
										voucher_no = voucher_no +' , '+ str(vouc.name)
									voucher_amt = voucher_amt + vouc.amount
									if voucher_date == " ":
										voucher_date = str(vouc.payment_date)
									else:
										voucher_date = voucher_date+' , '+ str(vouc.payment_date)
									if voucher_user == " ":
										voucher_user = str(vouc.create_uid.name)
									else:
										voucher_user = voucher_user +' , '+ str(vouc.create_uid.name)
									if voucher_user_cod == " ":
										voucher_user_cod = str(vouc.create_uid.login)
									else:
										voucher_user_cod = voucher_user_cod +' , '+ str(vouc.create_uid.login)


					worksheet.write_string (row, col,str(line['state']),main_data)
					worksheet.write_string (row, col+1,str(users_code),main_data)
					worksheet.write_string (row, col+2,str(users_name),main_data)
					worksheet.write_string (row, col+3,str(voucher_no),main_data)
					worksheet.write_string (row, col+4,str(line['invoice_state_stored']),main_data)
					worksheet.write_string (row, col+5,str(voucher_amt),main_data)
					worksheet.write_string (row, col+6,str(line['charges_stored']),main_data)
					worksheet.write_string (row, col+7,str(line['bsg_pay_method_name']),main_data)
					worksheet.write_string (row, col+8,str(line['bsg_loc_to_name']),main_data)
					worksheet.write_string (row, col+9,str(line['plate_no']),main_data)
					worksheet.write_string (row, col+10,str(line['bsg_customer_name']),main_data)
					worksheet.write_string (row, col+11,str(order_date),main_data)
					worksheet.write_string (row, col+12,str(line['sale_line_rec_name']),main_data)


					row += 1


			if data['inv_state'] == 'all':

				for index,line in bsg_cargo_lines.iterrows():
					users_name = " "
					users_code = " "
					if line['create_uid'] > 0:
						users_name_ids = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['create_uid']))
						users_name = users_name_ids.name
						users_code = users_name_ids.login

					order_date = " "
					if line['order_date']:
						order_date = line['order_date'] + timedelta(hours=3)
						order_date = str(order_date)[:16]
						order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

					voucher_no = " "
					voucher_amt = 0
					voucher_date = " "
					voucher_user = " "
					voucher_user_cod = " "
					if line['invoice_id'] > 0:
						invoice_ids = self.env['account.invoice'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['invoice_id']))
						if invoice_ids:
							if invoice_ids.payment_ids:
								for vouc in invoice_ids.payment_ids:
									if voucher_no == " ":
										voucher_no = str(vouc.name)
									else:
										voucher_no = voucher_no +' , '+ str(vouc.name)
									voucher_amt = voucher_amt + vouc.amount
									if voucher_date == " ":
										voucher_date = str(vouc.payment_date)
									else:
										voucher_date = voucher_date+' , '+ str(vouc.payment_date)
									if voucher_user == " ":
										voucher_user = str(vouc.create_uid.name)
									else:
										voucher_user = voucher_user +' , '+ str(vouc.create_uid.name)
									if voucher_user_cod == " ":
										voucher_user_cod = str(vouc.create_uid.login)
									else:
										voucher_user_cod = voucher_user_cod +' , '+ str(vouc.create_uid.login)


					worksheet.write_string (row, col,str(line['state']),main_data)
					worksheet.write_string (row, col+1,str(users_code),main_data)
					worksheet.write_string (row, col+2,str(users_name),main_data)
					worksheet.write_string (row, col+3,str(voucher_no),main_data)
					worksheet.write_string (row, col+4,str(line['invoice_state_stored']),main_data)
					worksheet.write_string (row, col+5,str(voucher_amt),main_data)
					worksheet.write_string (row, col+6,str(line['charges_stored']),main_data)
					worksheet.write_string (row, col+7,str(line['bsg_pay_method_name']),main_data)
					worksheet.write_string (row, col+8,str(line['bsg_loc_to_name']),main_data)
					worksheet.write_string (row, col+9,str(line['plate_no']),main_data)
					worksheet.write_string (row, col+10,str(line['bsg_customer_name']),main_data)
					worksheet.write_string (row, col+11,str(order_date),main_data)
					worksheet.write_string (row, col+12,str(line['sale_line_rec_name']),main_data)


					row += 1

				
		if data['report_type'] == '02':
			report_type = 'المرحلة‬ ‫وغير‬ ‫المرحلة‬'
			worksheet.merge_range('A1:P1','Cargo Sale Line Details Report',merge_format)
			worksheet.merge_range('A1:M1','Cargo Sale Line Details Report',merge_format)
			worksheet.write('A2', 'Date From', main_heading)
			worksheet.write('B2', str(data['form']), main_data)
			worksheet.write('D2', 'Drop Location', main_heading)
			worksheet.write('E2', str(branches_to), main_data)
			worksheet.write('A3', 'Date To', main_heading)
			worksheet.write('B3', str(data['to']), main_data)
			worksheet.write('D3', 'Shipping Location', main_heading)
			worksheet.write('E3', str(branches_from), main_data)
			worksheet.write('A4', 'Payment State', main_heading)
			worksheet.write('B4', str(data['pay_case']), main_data)
			worksheet.write('D4', 'Payment Method', main_heading)
			worksheet.write('E4', str(pay_method_name), main_data)
			worksheet.write('A5', 'Customer', main_heading)
			worksheet.write('B5', str(customers_name), main_data)
			worksheet.write('D5', 'Cargo Sale Type', main_heading)
			worksheet.write('E5', str(data['cargo_sale_type']), main_data)
			worksheet.write('A6', 'Trip Type', main_heading)
			worksheet.write('B6', str(data['trip_type']), main_data)
			worksheet.write('D6', 'Cargo Sale Line State', main_heading)
			worksheet.write('E6', str(data['state']), main_data)
			worksheet.write('A7', 'Invoice State', main_heading)
			worksheet.write('B7', str(data['inv_state']), main_data)
			worksheet.write('D7', 'User', main_heading)
			worksheet.write('E7', str(user_name), main_data)
			worksheet.write('A8', 'Report Type', main_heading)
			worksheet.write('B8', str(report_type), main_data)

			worksheet.set_column('A:P', 20)
			
			worksheet.write('A10', '‫‫الترانزيت‬ ‫فرع‬', main_heading1)
			worksheet.write('B10', '‫‫السيارة‬ ‫شحن‬ ‫حالة‬', main_heading1)
			worksheet.write('C10', '‫‫الدرج‬ ‫رقم‬', main_heading1)
			worksheet.write('D10', '‫‫الفعلي‬ ‫الوصول‬', main_heading1)
			worksheet.write('E10', '‫‫الشحن‬ ‫تاريخ‬', main_heading1)
			worksheet.write('F10', '‫متوقع‬ ‫وصول‬', main_heading1)
			worksheet.write('G10', '‫‫الشاحنة‬ ‫نوع‬', main_heading1)
			worksheet.write('H10', '‫‫الشاحنة‬ ‫رقم‬', main_heading1)
			worksheet.write('I10', '‫‫‫رقم الرحلة', main_heading1)
			worksheet.write('J10', '‫‫الى‬ ‫مشحونة‬', main_heading1)
			worksheet.write('K10', '‫‫من‬ ‫مشحونة‬', main_heading1)
			worksheet.write('L10', '‫‫شاسيه‬ ‫رقم‬', main_heading1)
			worksheet.write('M10', '‫‫اللوحة‬ ‫رقم‬', main_heading1)
			worksheet.write('N10', '‫‫العميل‬ ‫اسم‬', main_heading1)
			worksheet.write('O10', '‫‫الطلب‬ ‫تاريخ‬', main_heading1)
			worksheet.write('P10', '‫المبيعات‬ ‫سجل‬ ‫رقم‬', main_heading1)

			worksheet.write('A11', '‫Pickup Location', main_heading1)
			worksheet.write('B11', '‫Cargo Sale Line state', main_heading1)
			worksheet.write('C11', '‫Drawer NO.', main_heading1)
			worksheet.write('D11', 'Delivery Date', main_heading1)
			worksheet.write('E11', '‫Trip Start Time', main_heading1)
			worksheet.write('F11', '‫Scheduled End Date', main_heading1)
			worksheet.write('G11', 'Vehicle Type', main_heading1)
			worksheet.write('H11', 'Vehicle ID', main_heading1)
			worksheet.write('I11', 'Trip ID', main_heading1)
			worksheet.write('J11', '‫To', main_heading1)
			worksheet.write('K11', 'From', main_heading1)
			worksheet.write('L11', 'Chasis No', main_heading1)
			worksheet.write('M11', 'Plate No', main_heading1)
			worksheet.write('N11', '‫Customer', main_heading1)
			worksheet.write('O11', '‫Order Date', main_heading1)
			worksheet.write('P11', '‫Cargo Sale Line No', main_heading1)


			row = 11
			col = 0

			if data['inv_state'] == 'with_invoice':

				payment_method_ids = self.env['cargo_payment_method'].search([('payment_type','in',('cash','pod'))]).ids

				payment_method_credit = self.env['cargo_payment_method'].search([('payment_type','=','credit')]).ids

				one_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_ids) & bsg_cargo_lines['invoice_state_stored'].isin(['open','paid'])]

				two_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_credit) & (bsg_cargo_lines['add_to_cc'] == True)]

				finalframe = [one_bsg_frame, two_bsg_frame]
				finalframe = pd.concat(finalframe)

				for index,line in finalframe.iterrows():
					users_name = " "
					users_code = " "
					if line['create_uid'] > 0:
						users_name_ids = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['create_uid']))
						users_name = users_name_ids.name
						users_code = users_name_ids.login

					order_date = " "
					if line['order_date']:
						order_date = line['order_date'] + timedelta(hours=3)
						order_date = str(order_date)[:16]
						order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

					expected_delivery = " "
					if line['expected_delivery']:
						expected_delivery = line['expected_delivery'] + timedelta(hours=3)
						expected_delivery = str(expected_delivery)
						expected_delivery = datetime.strptime(expected_delivery, '%Y-%m-%d').strftime('%d/%m/%Y')

					vehicle_type_name = " "
					if line['trip_vehicle_id']:
						veh_ids = self.env['fleet.vehicle'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['trip_vehicle_id']))
						vehicle_type_name = veh_ids.vehicle_type.vehicle_type_name

					voucher_no = " "
					voucher_amt = 0
					voucher_date = " "
					voucher_user = " "
					voucher_user_cod = " "
					if line['invoice_id'] > 0:
						invoice_ids = self.env['account.invoice'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['invoice_id']))
						if invoice_ids:
							if invoice_ids.payment_ids:
								for vouc in invoice_ids.payment_ids:
									if voucher_no == " ":
										voucher_no = str(vouc.name)
									else:
										voucher_no = voucher_no +' , '+ str(vouc.name)
									voucher_amt = voucher_amt + vouc.amount
									if voucher_date == " ":
										voucher_date = str(vouc.payment_date)
									else:
										voucher_date = voucher_date+' , '+ str(vouc.payment_date)
									if voucher_user == " ":
										voucher_user = str(vouc.create_uid.name)
									else:
										voucher_user = voucher_user +' , '+ str(vouc.create_uid.name)
									if voucher_user_cod == " ":
										voucher_user_cod = str(vouc.create_uid.login)
									else:
										voucher_user_cod = voucher_user_cod +' , '+ str(vouc.create_uid.login)

					worksheet.write_string (row, col,str(line['bsg_loc_pickup_name']),main_data)
					worksheet.write_string (row, col+1,str(line['state']),main_data)
					worksheet.write_string (row, col+2,str(line['drawer_no']),main_data)
					worksheet.write_string (row, col+3,str(expected_delivery),main_data)
					worksheet.write_string (row, col+4,str(line['trip_arrival_start_time']),main_data)
					worksheet.write_string (row, col+5,str(line['expected_end_date']),main_data)
					# worksheet.write_string (row, col+6,str(rec.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).fleet_trip_id.vehicle_id.vehicle_type.vehicle_type_name),main_data)
					worksheet.write_string (row, col+6,str(vehicle_type_name),main_data)
					worksheet.write_string (row, col+7,str(line['taq_number']),main_data)
					worksheet.write_string (row, col+8,str(line['bsg_trip_name']),main_data)
					worksheet.write_string (row, col+9,str(line['bsg_loc_to_name']),main_data)
					worksheet.write_string (row, col+10,str(line['bsg_loc_from_name']),main_data)
					worksheet.write_string (row, col+11,str(line['chassis_no']),main_data)
					worksheet.write_string (row, col+12,str(line['plate_no']),main_data)
					worksheet.write_string (row, col+13,str(line['bsg_customer_name']),main_data)
					worksheet.write_string (row, col+14,str(order_date),main_data)
					worksheet.write_string (row, col+15,str(line['sale_line_rec_name']),main_data)

					row += 1

			if data['inv_state'] == 'without_invoice':

				payment_method_ids = self.env['cargo_payment_method'].search([('payment_type','in',('cash','pod'))]).ids

				payment_method_credit = self.env['cargo_payment_method'].search([('payment_type','=','credit')]).ids

				one_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_ids) & bsg_cargo_lines['invoice_state_stored'].isnull()]

				two_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_credit) & (bsg_cargo_lines['add_to_cc'] == False)]

				finalframe = [one_bsg_frame, two_bsg_frame]
				finalframe = pd.concat(finalframe)

				for index,line in finalframe.iterrows():
					users_name = " "
					users_code = " "
					if line['create_uid'] > 0:
						users_name_ids = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['create_uid']))
						users_name = users_name_ids.name
						users_code = users_name_ids.login

					order_date = " "
					if line['order_date']:
						order_date = line['order_date'] + timedelta(hours=3)
						order_date = str(order_date)[:16]
						order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

					expected_delivery = " "
					if line['expected_delivery']:
						expected_delivery = line['expected_delivery'] + timedelta(hours=3)
						expected_delivery = str(expected_delivery)
						expected_delivery = datetime.strptime(expected_delivery, '%Y-%m-%d').strftime('%d/%m/%Y')

					vehicle_type_name = " "
					if line['trip_vehicle_id']:
						veh_ids = self.env['fleet.vehicle'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['trip_vehicle_id']))
						vehicle_type_name = veh_ids.vehicle_type.vehicle_type_name

					voucher_no = " "
					voucher_amt = 0
					voucher_date = " "
					voucher_user = " "
					voucher_user_cod = " "
					if line['invoice_id'] > 0:
						invoice_ids = self.env['account.invoice'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['invoice_id']))
						if invoice_ids:
							if invoice_ids.payment_ids:
								for vouc in invoice_ids.payment_ids:
									if voucher_no == " ":
										voucher_no = str(vouc.name)
									else:
										voucher_no = voucher_no +' , '+ str(vouc.name)
									voucher_amt = voucher_amt + vouc.amount
									if voucher_date == " ":
										voucher_date = str(vouc.payment_date)
									else:
										voucher_date = voucher_date+' , '+ str(vouc.payment_date)
									if voucher_user == " ":
										voucher_user = str(vouc.create_uid.name)
									else:
										voucher_user = voucher_user +' , '+ str(vouc.create_uid.name)
									if voucher_user_cod == " ":
										voucher_user_cod = str(vouc.create_uid.login)
									else:
										voucher_user_cod = voucher_user_cod +' , '+ str(vouc.create_uid.login)

					worksheet.write_string (row, col,str(line['bsg_loc_pickup_name']),main_data)
					worksheet.write_string (row, col+1,str(line['state']),main_data)
					worksheet.write_string (row, col+2,str(line['drawer_no']),main_data)
					worksheet.write_string (row, col+3,str(expected_delivery),main_data)
					worksheet.write_string (row, col+4,str(line['trip_arrival_start_time']),main_data)
					worksheet.write_string (row, col+5,str(line['expected_end_date']),main_data)
					# worksheet.write_string (row, col+6,str(rec.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).fleet_trip_id.vehicle_id.vehicle_type.vehicle_type_name),main_data)
					worksheet.write_string (row, col+6,str(vehicle_type_name),main_data)
					worksheet.write_string (row, col+7,str(line['taq_number']),main_data)
					worksheet.write_string (row, col+8,str(line['bsg_trip_name']),main_data)
					worksheet.write_string (row, col+9,str(line['bsg_loc_to_name']),main_data)
					worksheet.write_string (row, col+10,str(line['bsg_loc_from_name']),main_data)
					worksheet.write_string (row, col+11,str(line['chassis_no']),main_data)
					worksheet.write_string (row, col+12,str(line['plate_no']),main_data)
					worksheet.write_string (row, col+13,str(line['bsg_customer_name']),main_data)
					worksheet.write_string (row, col+14,str(order_date),main_data)
					worksheet.write_string (row, col+15,str(line['sale_line_rec_name']),main_data)

					row += 1

			if data['inv_state'] == 'all':

				for index,line in bsg_cargo_lines.iterrows():
					users_name = " "
					users_code = " "
					if line['create_uid'] > 0:
						users_name_ids = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['create_uid']))
						users_name = users_name_ids.name
						users_code = users_name_ids.login

					order_date = " "
					if line['order_date']:
						order_date = line['order_date'] + timedelta(hours=3)
						order_date = str(order_date)[:16]
						order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

					expected_delivery = " "
					if line['expected_delivery']:
						expected_delivery = line['expected_delivery'] + timedelta(hours=3)
						expected_delivery = str(expected_delivery)
						expected_delivery = datetime.strptime(expected_delivery, '%Y-%m-%d').strftime('%d/%m/%Y')

					vehicle_type_name = " "
					if line['trip_vehicle_id'] > 0:
						veh_ids = self.env['fleet.vehicle'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['trip_vehicle_id']))
						vehicle_type_name = veh_ids.vehicle_type.vehicle_type_name

					voucher_no = " "
					voucher_amt = 0
					voucher_date = " "
					voucher_user = " "
					voucher_user_cod = " "
					if line['invoice_id'] > 0:
						invoice_ids = self.env['account.invoice'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['invoice_id']))
						if invoice_ids:
							if invoice_ids.payment_ids:
								for vouc in invoice_ids.payment_ids:
									if voucher_no == " ":
										voucher_no = str(vouc.name)
									else:
										voucher_no = voucher_no +' , '+ str(vouc.name)
									voucher_amt = voucher_amt + vouc.amount
									if voucher_date == " ":
										voucher_date = str(vouc.payment_date)
									else:
										voucher_date = voucher_date+' , '+ str(vouc.payment_date)
									if voucher_user == " ":
										voucher_user = str(vouc.create_uid.name)
									else:
										voucher_user = voucher_user +' , '+ str(vouc.create_uid.name)
									if voucher_user_cod == " ":
										voucher_user_cod = str(vouc.create_uid.login)
									else:
										voucher_user_cod = voucher_user_cod +' , '+ str(vouc.create_uid.login)

					worksheet.write_string (row, col,str(line['bsg_loc_pickup_name']),main_data)
					worksheet.write_string (row, col+1,str(line['state']),main_data)
					worksheet.write_string (row, col+2,str(line['drawer_no']),main_data)
					worksheet.write_string (row, col+3,str(expected_delivery),main_data)
					worksheet.write_string (row, col+4,str(line['trip_arrival_start_time']),main_data)
					worksheet.write_string (row, col+5,str(line['expected_end_date']),main_data)
					# worksheet.write_string (row, col+6,str(rec.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).fleet_trip_id.vehicle_id.vehicle_type.vehicle_type_name),main_data)
					worksheet.write_string (row, col+6,str(vehicle_type_name),main_data)
					worksheet.write_string (row, col+7,str(line['taq_number']),main_data)
					worksheet.write_string (row, col+8,str(line['bsg_trip_name']),main_data)
					worksheet.write_string (row, col+9,str(line['bsg_loc_to_name']),main_data)
					worksheet.write_string (row, col+10,str(line['bsg_loc_from_name']),main_data)
					worksheet.write_string (row, col+11,str(line['chassis_no']),main_data)
					worksheet.write_string (row, col+12,str(line['plate_no']),main_data)
					worksheet.write_string (row, col+13,str(line['bsg_customer_name']),main_data)
					worksheet.write_string (row, col+14,str(order_date),main_data)
					worksheet.write_string (row, col+15,str(line['sale_line_rec_name']),main_data)

					row += 1

			
		if data['report_type'] == '03':
			report_type = 'المسلمة‬ ‫وغير‬ ‫المسلمة‬'
			worksheet.merge_range('A1:P1','Cargo Sale Line Details Report',merge_format)
			worksheet.merge_range('A1:M1','Cargo Sale Line Details Report',merge_format)
			worksheet.write('A2', 'Date From', main_heading)
			worksheet.write('B2', str(data['form']), main_data)
			worksheet.write('D2', 'Drop Location', main_heading)
			worksheet.write('E2', str(branches_to), main_data)
			worksheet.write('A3', 'Date To', main_heading)
			worksheet.write('B3', str(data['to']), main_data)
			worksheet.write('D3', 'Shipping Location', main_heading)
			worksheet.write('E3', str(branches_from), main_data)
			worksheet.write('A4', 'Payment State', main_heading)
			worksheet.write('B4', str(data['pay_case']), main_data)
			worksheet.write('D4', 'Payment Method', main_heading)
			worksheet.write('E4', str(pay_method_name), main_data)
			worksheet.write('A5', 'Customer', main_heading)
			worksheet.write('B5', str(customers_name), main_data)
			worksheet.write('D5', 'Cargo Sale Type', main_heading)
			worksheet.write('E5', str(data['cargo_sale_type']), main_data)
			worksheet.write('A6', 'Trip Type', main_heading)
			worksheet.write('B6', str(data['trip_type']), main_data)
			worksheet.write('D6', 'Cargo Sale Line State', main_heading)
			worksheet.write('E6', str(data['state']), main_data)
			worksheet.write('A7', 'Invoice State', main_heading)
			worksheet.write('B7', str(data['inv_state']), main_data)
			worksheet.write('D7', 'User', main_heading)
			worksheet.write('E7', str(user_name), main_data)
			worksheet.write('A8', 'Report Type', main_heading)
			worksheet.write('B8', str(report_type), main_data)

			worksheet.set_column('A:P', 20)
			
			worksheet.write('A10', '‫‫كود المستخدم', main_heading1)
			worksheet.write('B10', '‫‫المستخدم', main_heading1)
			worksheet.write('C10', '‫‫تاريخ اذن خروج', main_heading1)
			worksheet.write('D10', '‫‫رقم اذن خروج', main_heading1)
			worksheet.write('E10', '‫‫رقم الدرج', main_heading1)
			worksheet.write('F10', '‫الوصول الفعلي', main_heading1)
			worksheet.write('G10', '‫‫رقم الرحلة', main_heading1)
			worksheet.write('H10', '‫‫طريقة الدفع', main_heading1)
			worksheet.write('I10', '‫‫مشحونة الى', main_heading1)
			worksheet.write('J10', '‫‫‫مشحونة من', main_heading1)
			worksheet.write('K10', '‫‫رقم اللوحة', main_heading1)
			worksheet.write('L10', '‫‫جوال المستلم', main_heading1)
			worksheet.write('M10', '‫‫اسم المستلم', main_heading1)
			worksheet.write('N10', '‫‫تاريخ الطلب', main_heading1)
			worksheet.write('O10', '‫‫رقم سجل المبيعات', main_heading1)
			

			worksheet.write('A11', '‫User Cod', main_heading1)
			worksheet.write('B11', '‫User', main_heading1)
			worksheet.write('C11', '‫ ', main_heading1)
			worksheet.write('D11', ' ', main_heading1)
			worksheet.write('E11', '‫Drawer NO.', main_heading1)
			worksheet.write('F11', 'Delivery Date', main_heading1)
			worksheet.write('G11', 'Payment Method', main_heading1)
			worksheet.write('H11', 'Trip ID', main_heading1)
			worksheet.write('I11', '‫To', main_heading1)
			worksheet.write('J11', 'From', main_heading1)
			worksheet.write('K11', 'Plate No', main_heading1)
			worksheet.write('L11', 'Receiver Mobile No.', main_heading1)
			worksheet.write('M11', 'Receiver Name', main_heading1)
			worksheet.write('N11', '‫Order Date', main_heading1)
			worksheet.write('O11', '‫Cargo Sale Line No', main_heading1)


			row = 11
			col = 0

			if data['inv_state'] == 'with_invoice':

				payment_method_ids = self.env['cargo_payment_method'].search([('payment_type','in',('cash','pod'))]).ids

				payment_method_credit = self.env['cargo_payment_method'].search([('payment_type','=','credit')]).ids

				one_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_ids) & bsg_cargo_lines['invoice_state_stored'].isin(['open','paid'])]

				two_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_credit) & (bsg_cargo_lines['add_to_cc'] == True)]

				finalframe = [one_bsg_frame, two_bsg_frame]
				finalframe = pd.concat(finalframe)

				for index,line in finalframe.iterrows():
					users_name = " "
					users_code = " "
					if line['create_uid'] > 0:
						users_name_ids = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['create_uid']))
						users_name = users_name_ids.name
						users_code = users_name_ids.login

					order_date = " "
					if line['order_date']:
						order_date = line['order_date'] + timedelta(hours=3)
						order_date = str(order_date)[:16]
						order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

					expected_delivery = " "
					if line['expected_delivery']:
						expected_delivery = line['expected_delivery'] + timedelta(hours=3)
						expected_delivery = str(expected_delivery)
						expected_delivery = datetime.strptime(expected_delivery, '%Y-%m-%d').strftime('%d/%m/%Y')

					voucher_no = " "
					voucher_amt = 0
					voucher_date = " "
					voucher_user = " "
					voucher_user_cod = " "
					if line['invoice_id'] > 0:
						invoice_ids = self.env['account.invoice'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['invoice_id']))
						if invoice_ids:
							if invoice_ids.payment_ids:
								for vouc in invoice_ids.payment_ids:
									if voucher_no == " ":
										voucher_no = str(vouc.name)
									else:
										voucher_no = voucher_no +' , '+ str(vouc.name)
									voucher_amt = voucher_amt + vouc.amount
									if voucher_date == " ":
										voucher_date = str(vouc.payment_date)
									else:
										voucher_date = voucher_date+' , '+ str(vouc.payment_date)
									if voucher_user == " ":
										voucher_user = str(vouc.create_uid.name)
									else:
										voucher_user = voucher_user +' , '+ str(vouc.create_uid.name)
									if voucher_user_cod == " ":
										voucher_user_cod = str(vouc.create_uid.login)
									else:
										voucher_user_cod = voucher_user_cod +' , '+ str(vouc.create_uid.login)

					worksheet.write_string (row, col,str(users_code),main_data)
					worksheet.write_string (row, col+1,str(users_name),main_data)
					worksheet.write_string (row, col+2,str(' '),main_data)
					worksheet.write_string (row, col+3,str(' '),main_data)
					worksheet.write_string (row, col+4,str(line['drawer_no']),main_data)
					worksheet.write_string (row, col+5,str(expected_delivery),main_data)
					
					worksheet.write_string (row, col+6,str(line['bsg_pay_method_name']),main_data)
					worksheet.write_string (row, col+7,str(line['bsg_trip_name']),main_data)
					worksheet.write_string (row, col+8,str(line['bsg_loc_to_name']),main_data)
					worksheet.write_string (row, col+9,str(line['bsg_loc_from_name']),main_data)
					worksheet.write_string (row, col+10,str(line['plate_no']),main_data)
					worksheet.write_string (row, col+11,str(line['receiver_mob_no']),main_data)
					worksheet.write_string (row, col+12,str(line['receiver_name']),main_data)
					worksheet.write_string (row, col+13,str(order_date),main_data)
					worksheet.write_string (row, col+14,str(line['sale_line_rec_name']),main_data)

					row += 1

			if data['inv_state'] == 'without_invoice':

				payment_method_ids = self.env['cargo_payment_method'].search([('payment_type','in',('cash','pod'))]).ids

				payment_method_credit = self.env['cargo_payment_method'].search([('payment_type','=','credit')]).ids

				one_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_ids) & bsg_cargo_lines['invoice_state_stored'].isnull()]

				two_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_credit) & (bsg_cargo_lines['add_to_cc'] == False)]

				finalframe = [one_bsg_frame, two_bsg_frame]
				finalframe = pd.concat(finalframe)

				for index,line in finalframe.iterrows():
					users_name = " "
					users_code = " "
					if line['create_uid'] > 0:
						users_name_ids = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['create_uid']))
						users_name = users_name_ids.name
						users_code = users_name_ids.login

					order_date = " "
					if line['order_date']:
						order_date = line['order_date'] + timedelta(hours=3)
						order_date = str(order_date)[:16]
						order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

					expected_delivery = " "
					if line['expected_delivery']:
						expected_delivery = line['expected_delivery'] + timedelta(hours=3)
						expected_delivery = str(expected_delivery)
						expected_delivery = datetime.strptime(expected_delivery, '%Y-%m-%d').strftime('%d/%m/%Y')

					voucher_no = " "
					voucher_amt = 0
					voucher_date = " "
					voucher_user = " "
					voucher_user_cod = " "
					if line['invoice_id'] > 0:
						invoice_ids = self.env['account.invoice'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['invoice_id']))
						if invoice_ids:
							if invoice_ids.payment_ids:
								for vouc in invoice_ids.payment_ids:
									if voucher_no == " ":
										voucher_no = str(vouc.name)
									else:
										voucher_no = voucher_no +' , '+ str(vouc.name)
									voucher_amt = voucher_amt + vouc.amount
									if voucher_date == " ":
										voucher_date = str(vouc.payment_date)
									else:
										voucher_date = voucher_date+' , '+ str(vouc.payment_date)
									if voucher_user == " ":
										voucher_user = str(vouc.create_uid.name)
									else:
										voucher_user = voucher_user +' , '+ str(vouc.create_uid.name)
									if voucher_user_cod == " ":
										voucher_user_cod = str(vouc.create_uid.login)
									else:
										voucher_user_cod = voucher_user_cod +' , '+ str(vouc.create_uid.login)

					worksheet.write_string (row, col,str(users_name),main_data)
					worksheet.write_string (row, col+1,str(users_code),main_data)
					worksheet.write_string (row, col+2,str(' '),main_data)
					worksheet.write_string (row, col+3,str(' '),main_data)
					worksheet.write_string (row, col+4,str(line['drawer_no']),main_data)
					worksheet.write_string (row, col+5,str(expected_delivery),main_data)
					
					worksheet.write_string (row, col+6,str(line['bsg_pay_method_name']),main_data)
					worksheet.write_string (row, col+7,str(line['bsg_trip_name']),main_data)
					worksheet.write_string (row, col+8,str(line['bsg_loc_to_name']),main_data)
					worksheet.write_string (row, col+9,str(line['bsg_loc_from_name']),main_data)
					worksheet.write_string (row, col+10,str(line['plate_no']),main_data)
					worksheet.write_string (row, col+11,str(line['receiver_mob_no']),main_data)
					worksheet.write_string (row, col+12,str(line['receiver_name']),main_data)
					worksheet.write_string (row, col+13,str(order_date),main_data)
					worksheet.write_string (row, col+14,str(line['sale_line_rec_name']),main_data)

					row += 1

			if data['inv_state'] == 'all':

				for index,line in bsg_cargo_lines.iterrows():
					users_name = " "
					users_code = " "
					if line['create_uid'] > 0:
						users_name_ids = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['create_uid']))
						users_name = users_name_ids.name
						users_code = users_name_ids.login

					order_date = " "
					if line['order_date']:
						order_date = line['order_date'] + timedelta(hours=3)
						order_date = str(order_date)[:16]
						order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

					expected_delivery = " "
					if line['expected_delivery']:
						expected_delivery = line['expected_delivery'] + timedelta(hours=3)
						expected_delivery = str(expected_delivery)
						expected_delivery = datetime.strptime(expected_delivery, '%Y-%m-%d').strftime('%d/%m/%Y')

					voucher_no = " "
					voucher_amt = 0
					voucher_date = " "
					voucher_user = " "
					voucher_user_cod = " "
					if line['invoice_id'] > 0:
						invoice_ids = self.env['account.invoice'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['invoice_id']))
						if invoice_ids:
							if invoice_ids.payment_ids:
								for vouc in invoice_ids.payment_ids:
									if voucher_no == " ":
										voucher_no = str(vouc.name)
									else:
										voucher_no = voucher_no +' , '+ str(vouc.name)
									voucher_amt = voucher_amt + vouc.amount
									if voucher_date == " ":
										voucher_date = str(vouc.payment_date)
									else:
										voucher_date = voucher_date+' , '+ str(vouc.payment_date)
									if voucher_user == " ":
										voucher_user = str(vouc.create_uid.name)
									else:
										voucher_user = voucher_user +' , '+ str(vouc.create_uid.name)
									if voucher_user_cod == " ":
										voucher_user_cod = str(vouc.create_uid.login)
									else:
										voucher_user_cod = voucher_user_cod +' , '+ str(vouc.create_uid.login)

					worksheet.write_string (row, col,str(users_name),main_data)
					worksheet.write_string (row, col+1,str(users_code),main_data)
					worksheet.write_string (row, col+2,str(' '),main_data)
					worksheet.write_string (row, col+3,str(' '),main_data)
					worksheet.write_string (row, col+4,str(line['drawer_no']),main_data)
					worksheet.write_string (row, col+5,str(expected_delivery),main_data)
					
					worksheet.write_string (row, col+6,str(line['bsg_pay_method_name']),main_data)
					worksheet.write_string (row, col+7,str(line['bsg_trip_name']),main_data)
					worksheet.write_string (row, col+8,str(line['bsg_loc_to_name']),main_data)
					worksheet.write_string (row, col+9,str(line['bsg_loc_from_name']),main_data)
					worksheet.write_string (row, col+10,str(line['plate_no']),main_data)
					worksheet.write_string (row, col+11,str(line['receiver_mob_no']),main_data)
					worksheet.write_string (row, col+12,str(line['receiver_name']),main_data)
					worksheet.write_string (row, col+13,str(order_date),main_data)
					worksheet.write_string (row, col+14,str(line['sale_line_rec_name']),main_data)

					row += 1
		

		if data['report_type'] == '04':
			report_type = 'القيمة‬ ‫بإجمالي‬'
			worksheet.merge_range('A1:M1','Cargo Sale Line Details Report',merge_format)
			worksheet.merge_range('A1:M1','Cargo Sale Line Details Report',merge_format)
			worksheet.write('A2', 'Date From', main_heading)
			worksheet.write('B2', str(data['form']), main_data)
			worksheet.write('D2', 'Drop Location', main_heading)
			worksheet.write('E2', str(branches_to), main_data)
			worksheet.write('A3', 'Date To', main_heading)
			worksheet.write('B3', str(data['to']), main_data)
			worksheet.write('D3', 'Shipping Location', main_heading)
			worksheet.write('E3', str(branches_from), main_data)
			worksheet.write('A4', 'Payment State', main_heading)
			worksheet.write('B4', str(data['pay_case']), main_data)
			worksheet.write('D4', 'Payment Method', main_heading)
			worksheet.write('E4', str(pay_method_name), main_data)
			worksheet.write('A5', 'Customer', main_heading)
			worksheet.write('B5', str(customers_name), main_data)
			worksheet.write('D5', 'Cargo Sale Type', main_heading)
			worksheet.write('E5', str(data['cargo_sale_type']), main_data)
			worksheet.write('A6', 'Trip Type', main_heading)
			worksheet.write('B6', str(data['trip_type']), main_data)
			worksheet.write('D6', 'Cargo Sale Line State', main_heading)
			worksheet.write('E6', str(data['state']), main_data)
			worksheet.write('A7', 'Invoice State', main_heading)
			worksheet.write('B7', str(data['inv_state']), main_data)
			worksheet.write('D7', 'User', main_heading)
			worksheet.write('E7', str(user_name), main_data)
			worksheet.write('A8', 'Report Type', main_heading)
			worksheet.write('B8', str(report_type), main_data)

			worksheet.set_column('A:M', 20)
			
			worksheet.write('A10', '‫السيارة‬ ‫شحن‬ ‫حالة‬', main_heading1)
			worksheet.write('B10', '‫المتبقي', main_heading1)
			worksheet.write('C10', 'المسدد', main_heading1)
			worksheet.write('D10', '‫الاجمالي', main_heading1)
			worksheet.write('E10', '‫الخدمات الاخرى', main_heading1)
			worksheet.write('F10', 'رسوم الارضيات', main_heading1)
			worksheet.write('G10', '‫الشحن‬ ‫رسوم‬', main_heading1)
			worksheet.write('H10', '‫الدفع‬ ‫طريقة‬', main_heading1)
			worksheet.write('I10', '‫الى‬ ‫مشحونة‬', main_heading1)
			worksheet.write('J10', '‫اللوحة‬ ‫رقم‬', main_heading1)
			worksheet.write('K10', '‫العميل‬ ‫اسم‬', main_heading1)
			worksheet.write('L10', '‫الطلب‬ ‫تاريخ‬', main_heading1)
			worksheet.write('M10', '‫المبيعات‬ ‫سجل‬ ‫رقم‬', main_heading1)

			worksheet.write('A11', '‫Cargo Sale Line state', main_heading1)
			worksheet.write('B11', '‫Remaining Balance', main_heading1)
			worksheet.write('C11', 'Receipt', main_heading1)
			worksheet.write('D11', '‫Total Amount', main_heading1)
			worksheet.write('E11', '‫Other Service', main_heading1)
			worksheet.write('F11', 'Demurrage Charges', main_heading1)
			worksheet.write('G11', '‫Charges', main_heading1)
			worksheet.write('H11', 'Payment Method', main_heading1)
			worksheet.write('I11', '‫To', main_heading1)
			worksheet.write('J11', 'Plate No', main_heading1)
			worksheet.write('K11', '‫Customer', main_heading1)
			worksheet.write('L11', '‫Order Date', main_heading1)
			worksheet.write('M11', '‫Cargo Sale Line No', main_heading1)


			row = 11
			col = 0

			if data['inv_state'] == 'with_invoice':

				payment_method_ids = self.env['cargo_payment_method'].search([('payment_type','in',('cash','pod'))]).ids

				payment_method_credit = self.env['cargo_payment_method'].search([('payment_type','=','credit')]).ids

				one_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_ids) & bsg_cargo_lines['invoice_state_stored'].isin(['open','paid'])]

				two_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_credit) & (bsg_cargo_lines['add_to_cc'] == True)]

				finalframe = [one_bsg_frame, two_bsg_frame]
				finalframe = pd.concat(finalframe)

				for index,line in finalframe.iterrows():
					users_name = " "
					users_code = " "
					if line['create_uid'] > 0:
						users_name_ids = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['create_uid']))
						users_name = users_name_ids.name
						users_code = users_name_ids.login

					order_date = " "
					if line['order_date']:
						order_date = line['order_date'] + timedelta(hours=3)
						order_date = str(order_date)[:16]
						order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

					expected_delivery = " "
					if line['expected_delivery']:
						expected_delivery = line['expected_delivery'] + timedelta(hours=3)
						expected_delivery = str(expected_delivery)
						expected_delivery = datetime.strptime(expected_delivery, '%Y-%m-%d').strftime('%d/%m/%Y')

					voucher_no = " "
					voucher_amt = 0
					voucher_date = " "
					voucher_user = " "
					voucher_user_cod = " "
					if line['invoice_id'] > 0:
						invoice_ids = self.env['account.invoice'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['invoice_id']))
						if invoice_ids:
							if invoice_ids.payment_ids:
								for vouc in invoice_ids.payment_ids:
									if voucher_no == " ":
										voucher_no = str(vouc.name)
									else:
										voucher_no = voucher_no +' , '+ str(vouc.name)
									voucher_amt = voucher_amt + vouc.amount
									if voucher_date == " ":
										voucher_date = str(vouc.payment_date)
									else:
										voucher_date = voucher_date+' , '+ str(vouc.payment_date)
									if voucher_user == " ":
										voucher_user = str(vouc.create_uid.name)
									else:
										voucher_user = voucher_user +' , '+ str(vouc.create_uid.name)
									if voucher_user_cod == " ":
										voucher_user_cod = str(vouc.create_uid.login)
									else:
										voucher_user_cod = voucher_user_cod +' , '+ str(vouc.create_uid.login)

					worksheet.write_string (row, col,str(line['state']),main_data)

					worksheet.write_string (row, col+1,str(line['amount_total']-voucher_amt),main_data)
					worksheet.write_string (row, col+2,str(voucher_amt),main_data)

					worksheet.write_string (row, col+3,str(line['total_amount']),main_data)
					worksheet.write_string (row, col+4,str('total_service_amount'),main_data)
					worksheet.write_string (row, col+5,str(line['final_price_stored']),main_data)
					worksheet.write_string (row, col+6,str(line['charges_stored']),main_data)
					worksheet.write_string (row, col+7,str(line['bsg_pay_method_name']),main_data)
					worksheet.write_string (row, col+8,str(line['bsg_loc_to_name']),main_data)
					worksheet.write_string (row, col+9,str(line['plate_no']),main_data)
					worksheet.write_string (row, col+10,str(line['bsg_customer_name']),main_data)
					worksheet.write_string (row, col+11,str(order_date),main_data)
					worksheet.write_string (row, col+12,str(line['sale_line_rec_name']),main_data)

					row += 1

			if data['inv_state'] == 'without_invoice':

				payment_method_ids = self.env['cargo_payment_method'].search([('payment_type','in',('cash','pod'))]).ids

				payment_method_credit = self.env['cargo_payment_method'].search([('payment_type','=','credit')]).ids

				one_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_ids) & bsg_cargo_lines['invoice_state_stored'].isnull()]

				two_bsg_frame = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (bsg_cargo_lines['state'] != 'draft') & (bsg_cargo_lines['bsg_state'] != 'cancel') & (bsg_cargo_lines['bsg_state'] != 'draft') & bsg_cargo_lines['payment_method'].isin(payment_method_credit) & (bsg_cargo_lines['add_to_cc'] == False)]

				finalframe = [one_bsg_frame, two_bsg_frame]
				finalframe = pd.concat(finalframe)

				for index,line in finalframe.iterrows():
					users_name = " "
					users_code = " "
					if line['create_uid'] > 0:
						users_name_ids = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['create_uid']))
						users_name = users_name_ids.name
						users_code = users_name_ids.login

					order_date = " "
					if line['order_date']:
						order_date = line['order_date'] + timedelta(hours=3)
						order_date = str(order_date)[:16]
						order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

					expected_delivery = " "
					if line['expected_delivery']:
						expected_delivery = line['expected_delivery'] + timedelta(hours=3)
						expected_delivery = str(expected_delivery)
						expected_delivery = datetime.strptime(expected_delivery, '%Y-%m-%d').strftime('%d/%m/%Y')

					voucher_no = " "
					voucher_amt = 0
					voucher_date = " "
					voucher_user = " "
					voucher_user_cod = " "
					if line['invoice_id'] > 0:
						invoice_ids = self.env['account.invoice'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['invoice_id']))
						if invoice_ids:
							if invoice_ids.payment_ids:
								for vouc in invoice_ids.payment_ids:
									if voucher_no == " ":
										voucher_no = str(vouc.name)
									else:
										voucher_no = voucher_no +' , '+ str(vouc.name)
									voucher_amt = voucher_amt + vouc.amount
									if voucher_date == " ":
										voucher_date = str(vouc.payment_date)
									else:
										voucher_date = voucher_date+' , '+ str(vouc.payment_date)
									if voucher_user == " ":
										voucher_user = str(vouc.create_uid.name)
									else:
										voucher_user = voucher_user +' , '+ str(vouc.create_uid.name)
									if voucher_user_cod == " ":
										voucher_user_cod = str(vouc.create_uid.login)
									else:
										voucher_user_cod = voucher_user_cod +' , '+ str(vouc.create_uid.login)

					worksheet.write_string (row, col,str(line['state']),main_data)

					worksheet.write_string (row, col+1,str(line['amount_total']-voucher_amt),main_data)
					worksheet.write_string (row, col+2,str(voucher_amt),main_data)

					worksheet.write_string (row, col+3,str(line['total_amount']),main_data)
					worksheet.write_string (row, col+4,str('total_service_amount'),main_data)
					worksheet.write_string (row, col+5,str(line['final_price_stored']),main_data)
					worksheet.write_string (row, col+6,str(line['charges_stored']),main_data)
					worksheet.write_string (row, col+7,str(line['bsg_pay_method_name']),main_data)
					worksheet.write_string (row, col+8,str(line['bsg_loc_to_name']),main_data)
					worksheet.write_string (row, col+9,str(line['plate_no']),main_data)
					worksheet.write_string (row, col+10,str(line['bsg_customer_name']),main_data)
					worksheet.write_string (row, col+11,str(order_date),main_data)
					worksheet.write_string (row, col+12,str(line['sale_line_rec_name']),main_data)

					row += 1

			if data['inv_state'] == 'all':

				for index,line in bsg_cargo_lines.iterrows():
					users_name = " "
					users_code = " "
					if line['create_uid'] > 0:
						users_name_ids = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['create_uid']))
						users_name = users_name_ids.name
						users_code = users_name_ids.login

					order_date = " "
					if line['order_date']:
						order_date = line['order_date'] + timedelta(hours=3)
						order_date = str(order_date)[:16]
						order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

					expected_delivery = " "
					if line['expected_delivery']:
						expected_delivery = line['expected_delivery'] + timedelta(hours=3)
						expected_delivery = str(expected_delivery)
						expected_delivery = datetime.strptime(expected_delivery, '%Y-%m-%d').strftime('%d/%m/%Y')

					voucher_no = " "
					voucher_amt = 0
					voucher_date = " "
					voucher_user = " "
					voucher_user_cod = " "
					if line['invoice_id'] > 0:
						invoice_ids = self.env['account.invoice'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(line['invoice_id']))
						if invoice_ids:
							if invoice_ids.payment_ids:
								for vouc in invoice_ids.payment_ids:
									if voucher_no == " ":
										voucher_no = str(vouc.name)
									else:
										voucher_no = voucher_no +' , '+ str(vouc.name)
									voucher_amt = voucher_amt + vouc.amount
									if voucher_date == " ":
										voucher_date = str(vouc.payment_date)
									else:
										voucher_date = voucher_date+' , '+ str(vouc.payment_date)
									if voucher_user == " ":
										voucher_user = str(vouc.create_uid.name)
									else:
										voucher_user = voucher_user +' , '+ str(vouc.create_uid.name)
									if voucher_user_cod == " ":
										voucher_user_cod = str(vouc.create_uid.login)
									else:
										voucher_user_cod = voucher_user_cod +' , '+ str(vouc.create_uid.login)

					worksheet.write_string (row, col,str(line['state']),main_data)

					worksheet.write_string (row, col+1,str(line['amount_total']-voucher_amt),main_data)
					worksheet.write_string (row, col+2,str(voucher_amt),main_data)

					worksheet.write_string (row, col+3,str(line['total_amount']),main_data)
					worksheet.write_string (row, col+4,str('total_service_amount'),main_data)
					worksheet.write_string (row, col+5,str(line['final_price_stored']),main_data)
					worksheet.write_string (row, col+6,str(line['charges_stored']),main_data)
					worksheet.write_string (row, col+7,str(line['bsg_pay_method_name']),main_data)
					worksheet.write_string (row, col+8,str(line['bsg_loc_to_name']),main_data)
					worksheet.write_string (row, col+9,str(line['plate_no']),main_data)
					worksheet.write_string (row, col+10,str(line['bsg_customer_name']),main_data)
					worksheet.write_string (row, col+11,str(order_date),main_data)
					worksheet.write_string (row, col+12,str(line['sale_line_rec_name']),main_data)

					row += 1



							

	
