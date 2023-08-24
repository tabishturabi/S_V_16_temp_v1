# -*- coding:utf-8 -*-
########################################################################################
########################################################################################
##                                                                                    ##
##    OpenERP, Open Source Management Solution                                        ##
##    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved       ##
##                                                                                    ##
##    This program is free software: you can redistribute it and/or modify            ##
##    it under the terms of the GNU Affero General Public License as published by     ##
##    the Free Software Foundation, either version 3 of the License, or               ##
##    (at your option) any later version.                                             ##
##                                                                                    ##
##    This program is distributed in the hope that it will be useful,                 ##
##    but WITHOUT ANY WARRANTY; without even the implied warranty of                  ##
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   ##
##    GNU Affero General Public License for more details.                             ##
##                                                                                    ##
##    You should have received a copy of the GNU Affero General Public License        ##
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.           ##
##                                                                                    ##
########################################################################################
########################################################################################

from odoo import api, models, fields
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning
import pandas as pd



class BxProductivityPdf(models.AbstractModel):
	_name = 'report.bx_productivity_reports.bx_productivity_pdf'

	@api.model
	def _get_report_values(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		record_wizard = self.env[self.model].browse(self.env.context.get('active_id'))

		form = record_wizard.form
		to = record_wizard.to
		branch_ids = record_wizard.branch_ids
		branch_ids_to = record_wizard.branch_ids_to
		users = record_wizard.users
		customer_ids = record_wizard.customer_ids
		from_bx = record_wizard.from_bx
		to_bx = record_wizard.to_bx
		truck_load = record_wizard.truck_load
		period_group = record_wizard.period_group
		fleet_type_transport = record_wizard.fleet_type_transport
		state = record_wizard.state
		employee_state = record_wizard.employee_state
		date = record_wizard.date
		date_type = record_wizard.date_type
		report_mode = record_wizard.report_mode
		is_between = record_wizard.is_between
		others = record_wizard.others


		def get_sum(bsg_driver_id, transport_lines):
			all_data = transport_lines.loc[(transport_lines['bsg_driver']) == bsg_driver_id]

			all_data = all_data.groupby(['bsg_driver'], as_index=False).sum()
			data_dict = {}
			for index, line in all_data.iterrows():
				data_dict['all_amt'] = line['total_before_taxes']
				data_dict['all_numz'] = line['counter']
				data_dict['distance_trip'] = line['trip_distance']
				data_dict['ex_distance'] = line['extra_distance']
				data_dict['tot_distance'] = line['total_distance']
				data_dict['tot_fuel_amount'] = line['total_fuel_amount']
				data_dict['tot_reward_amount'] = line['total_reward_amount']
				data_dict['tot_amount'] = line['total_amount']
			return data_dict
		def get_sum_by_user(user_name_id, transport_lines):
			all_data = transport_lines.loc[(transport_lines['create_uid']) == user_name_id]

			all_data = all_data.groupby(['create_uid'], as_index=False).sum()
			data_dict = {}
			for index, line in all_data.iterrows():
				data_dict['total_before_taxes'] = line['total_before_taxes']
				data_dict['counter']  = line['counter']
				data_dict['trip_distance']  = line['trip_distance']
				data_dict['extra_distance']  = line['extra_distance']
				data_dict['total_distance']  = line['total_distance']
				data_dict['total_fuel_amount']  = line['total_fuel_amount']
				data_dict['total_reward_amount']  = line['total_reward_amount']
				data_dict['total_amount']  = line['total_amount']

			return data_dict


		table_name = "transport_management"
		self.env.cr.execute(
			"select id,order_date,payment_method,state,total_amount,form_transport,to_transport,create_uid,customer,"
			"transportation_no,total_before_taxes,tax_amount,"
			"total_distance,transportation_vehicle,driver_number,total_fuel_amount,total_reward_amount,transportation_driver,trip_distance,extra_distance,driver,route_id,fleet_type_transport FROM " + table_name + " ")
		result = self._cr.fetchall()
		transport_lines = pd.DataFrame(list(result))
		transport_lines = transport_lines.rename(
			columns={0: 'self_id', 1: 'order_date', 2: 'payment_method', 3: 'state', 4: 'total_amount',
					 5: 'form_transport', 6: 'to_transport', 7: 'create_uid', 8: 'customer', 9: 'transportation_no',
					 10: 'total_before_taxes', 11: 'tax_amount',12:'total_distance', 13:'transportation_vehicle',
					 14:'driver_number', 15:'total_fuel_amount', 16:'total_reward_amount',
					 17:'transportation_driver', 18:'trip_distance', 19:'extra_distance', 20:'driver', 21:'route_id', 22:'fleet_type_transport'})

		bsg_customer_table = "res_partner"
		self.env.cr.execute("select id,name FROM " + bsg_customer_table + " ")
		result_bsg_customer = self._cr.fetchall()
		bsg_customer_frame = pd.DataFrame(list(result_bsg_customer))
		bsg_customer_frame = bsg_customer_frame.rename(columns={0: 'bsg_customer_id', 1: 'bsg_customer_name'})
		transport_lines = pd.merge(transport_lines, bsg_customer_frame, how='left', left_on='customer',
								   right_on='bsg_customer_id')

		payment_frame_table = "cargo_payment_method"
		self.env.cr.execute("select id,payment_method_name FROM " + payment_frame_table + " ")
		result_payment_frame = self._cr.fetchall()
		payment_frame = pd.DataFrame(list(result_payment_frame))
		payment_frame = payment_frame.rename(columns={0: 'bsg_pay_method_id', 1: 'bsg_pay_method_name'})
		transport_lines = pd.merge(transport_lines, payment_frame, how='left', left_on='payment_method',
								   right_on='bsg_pay_method_id')

		loc_from_frame_table = "bsg_route_waypoints"
		self.env.cr.execute("select id,route_waypoint_name FROM " + loc_from_frame_table + " ")
		result_loc_from_frame = self._cr.fetchall()
		loc_from_frame = pd.DataFrame(list(result_loc_from_frame))
		loc_from_frame = loc_from_frame.rename(columns={0: 'bsg_loc_from_id', 1: 'bsg_loc_from_name'})
		transport_lines = pd.merge(transport_lines, loc_from_frame, how='left', left_on='form_transport',
								   right_on='bsg_loc_from_id')

		loc_to_frame_table = "bsg_route_waypoints"
		self.env.cr.execute("select id,route_waypoint_name FROM " + loc_to_frame_table + " ")
		result_loc_to_frame = self._cr.fetchall()
		loc_to_frame = pd.DataFrame(list(result_loc_to_frame))
		loc_to_frame = loc_to_frame.rename(columns={0: 'bsg_loc_to_id', 1: 'bsg_loc_to_name'})
		transport_lines = pd.merge(transport_lines, loc_to_frame, how='left', left_on='to_transport',
								   right_on='bsg_loc_to_id')
		#
		fleet_vehicle_table = "fleet_vehicle"
		self.env.cr.execute("select bsg_driver,vehicle_type,vehicle_status,taq_number FROM " + fleet_vehicle_table + " ")
		result_fleet_vehicle = self._cr.fetchall()
		fleet_vehicle_frame = pd.DataFrame(list(result_fleet_vehicle))
		fleet_vehicle_frame = fleet_vehicle_frame.rename(columns={0: 'bsg_driver', 1: 'vehicle_type', 2: 'vehicle_status', 3: 'taq_number'})
		transport_lines = pd.merge(transport_lines, fleet_vehicle_frame, how='left', left_on='driver',
								   right_on='bsg_driver')

		transport_lines = transport_lines.loc[(transport_lines['state'] != 'cancel')]
		transport_lines = transport_lines.loc[(transport_lines['state'].isin(['fuel_voucher', 'receive_pod', 'done']))]

		if state:
			transport_lines = transport_lines.loc[(transport_lines['state'] == state)]


		if customer_ids:
			transport_lines = transport_lines.loc[(transport_lines['customer'].isin(customer_ids.ids))]

		if branch_ids:
			branches_ids = []
			for x in branch_ids:
				way_points = self.env['bsg_route_waypoints'].search([('loc_branch_id.id', '=', x)], limit=1)
				if way_points:
					branches_ids.append(way_points.id)

			transport_lines = transport_lines.loc[(transport_lines['form_transport'].isin(branches_ids))]

		if branch_ids_to:
			transport_lines = transport_lines.loc[(transport_lines['to_transport'].isin(branch_ids_to))]

		if users:
			transport_lines = transport_lines.loc[(transport_lines['create_uid'].isin(users))]


		transport_lines['date'] = transport_lines['order_date'].astype(str)
		transport_lines['counter'] = 1
		if fleet_type_transport:
			transport_lines = transport_lines.loc[(transport_lines['fleet_type_transport'] == (fleet_type_transport))]
		if truck_load:
			transport_lines = transport_lines.loc[(transport_lines['truck_load'] == (truck_load))]
		if truck_load:
			transport_lines = transport_lines.loc[(transport_lines['truck_load'] == (truck_load))]
		if date_type == "is equal to":
			transport_lines = transport_lines.loc[(transport_lines['date'] == (date))]
		if date_type == "is not equal to":
			transport_lines = transport_lines.loc[(transport_lines['date'] != date)]
		if date_type == "is after":
			transport_lines = transport_lines.loc[(transport_lines['date'] > date)]
		if date_type == "is before":
			transport_lines = transport_lines.loc[(transport_lines['date'] < date)]
		if date_type == "is after or equal to":
			transport_lines = transport_lines.loc[(transport_lines['date'] >= date)]
		if date_type == "is before or equal to":
			transport_lines = transport_lines.loc[(transport_lines['date'] <= date)]
		if date_type == "is between":
			transport_lines = transport_lines.loc[
				(transport_lines['date'] >= form) & (transport_lines['date'] <= to)]
		if date_type == "is set":
			transport_lines = transport_lines.loc[(transport_lines.order_date.notnull())]
		if date_type == "is not set":
			transport_lines = transport_lines.loc[(transport_lines.order_date.isnull())]

		total_bx = 0
		total_bxx = 0
		tripp_distance = 0
		extr_distance = 0
		totl_distance = 0
		total_distance = 0
		total_fuel_amount = 0
		total_reward_amount = 0
		total_amount = 0

		total_before_taxes = 0
		total_distance = 0
		total_fuel_amount = 0
		total_reward_amount = 0
		total_amount = 0


		# Bx Vehicle Type Summary Report
		tot_bx = 0
		tot_invc_amt = 0
		tot_trip = 0
		tot_extra = 0
		tott_distance = 0
		tot_fuel_amt = 0
		tot_rewrd_amt = 0
		tot_amt = 0

		# Bx Driver Summary Report
		tot_pos_num = 0
		tot_pos_amt = 0
		tot_unpos_num = 0
		tot_unpos_amt = 0
		tot_dis_num = 0
		tot_fuel_num = 0
		tot_rwrd_num = 0
		tot_all_num = 0

		# Bx User Summary Report
		tot_count = 0
		tot_count_bx = 0
		tot_count_trip = 0
		tot_count_extra = 0
		tot_count_tot = 0
		tot_count_fuel = 0
		tot_count_rwrd = 0
		tot_count_amt = 0

		# Bx Productivity Summary Report
		tot_bx = 0
		tot_invc_amt = 0
		tot_trip_amt = 0
		tot_extra_amt = 0
		tot_distance_amt = 0
		tot_fuel_amt = 0
		tot_rewrd_amt = 0
		tot_amt = 0


		main_data = []
		report_type_num = 0
		head = 0

		if not report_mode:
			report_type_num = 6
			head = 'Bx Vehicle productivity Summery Report'

			unique_bx = transport_lines.taq_number.unique()
			#
			for rec in list(unique_bx):
				all_data = transport_lines.loc[(transport_lines['taq_number']) == rec]

				all_data = all_data.groupby(['taq_number'], as_index=False).sum()

				if len(all_data) > 0:
					for index, line in all_data.iterrows():
						all_amt = line['total_before_taxes']
						all_numz = line['counter']
						distance_trip = line['trip_distance']
						ex_distance = line['extra_distance']
						tot_distance = line['total_distance']
						tot_fuel_amount = line['total_fuel_amount']
						tot_reward_amount = line['total_reward_amount']

				trans_vehicle = self.env['fleet.vehicle'].search([('taq_number', '=', rec)], limit=1)

				main_data.append({
					'taq_number': trans_vehicle.taq_number,
					'vehicle_type_name': trans_vehicle.vehicle_type.vehicle_type_name,
					'vehicle_status_name': trans_vehicle.vehicle_status.vehicle_status_name,
					'driver_code': trans_vehicle.driver_code,
					'bsg_driver': trans_vehicle.bsg_driver.name,
					'transportation_no': all_numz,
					'total_before_taxes': all_amt,
					'trip_distance': distance_trip,
					'extra_distance': ex_distance,
					'total_distance': tot_distance,
					# 'extra_distance_amt': extra_distance_amt,
					'total_fuel_amount': tot_fuel_amount,
					'total_reward_amount': tot_reward_amount,
					'total_amount': (tot_fuel_amount + tot_reward_amount),

				})

				total_bx = total_bx + all_numz
				total_bxx = total_bxx + all_amt
				tripp_distance = tripp_distance + distance_trip
				extr_distance = extr_distance + ex_distance
				totl_distance = totl_distance + tot_distance
				total_fuel_amount = total_fuel_amount + tot_fuel_amount
				total_reward_amount = total_reward_amount + tot_reward_amount
				total_amount = total_amount + (tot_fuel_amount + tot_reward_amount)

		if report_mode == 'Bx Vehicle productivity Detail Report':
			report_type_num = 1
			head = 'Bx Vehicle productivity Detail Report'

			transport_lines = transport_lines.sort_values(by='order_date')
			transport_lines = transport_lines.sort_values(by='taq_number')
			for index, rec in transport_lines.iterrows():
				trans_vehicle = self.env['transport.management'].browse(rec.self_id).transportation_vehicle
				trans_route = self.env['bsg_route'].browse(int(rec['route_id'])).route_name

				main_data.append({
					'taq_number':trans_vehicle.taq_number,
					'vehicle_type_name':trans_vehicle.vehicle_type.vehicle_type_name,
					'vehicle_status_name':trans_vehicle.vehicle_status.vehicle_status_name,
					'driver_code':trans_vehicle.driver_code,
					'bsg_driver':trans_vehicle.bsg_driver.name,
					'transportation_no':rec['transportation_no'],
					'route_id':trans_route,
					'total_before_taxes':rec['total_before_taxes'],
					'total_distance':rec['total_distance'],
					'total_fuel_amount':rec['total_fuel_amount'],
					'total_reward_amount':rec['total_reward_amount'],
					'total_amount':rec['total_fuel_amount'] + rec['total_reward_amount'],
				})

				total_before_taxes = total_before_taxes + rec['total_before_taxes']
				total_distance = total_distance + rec['total_distance']
				total_fuel_amount = total_fuel_amount + rec['total_fuel_amount']
				total_reward_amount = total_reward_amount + rec['total_reward_amount']
				total_amount = total_amount + rec['total_amount']


		if report_mode == 'Bx Vehicle Type Summary Report':
			report_type_num = 2
			head = 'Bx Vehicle Type Summary Report'

			unique_type = transport_lines.fleet_type_transport.unique()

			for rec in list(unique_type):
				all_data = transport_lines.loc[(transport_lines['fleet_type_transport'] == rec)]
				all_data = all_data.groupby(['fleet_type_transport'], as_index=False).sum()

				all_amt = 0
				all_numz = 0
				distance_trip = 0
				ex_distance = 0
				tot_distance = 0
				tot_fuel_amount = 0
				tot_reward_amount = 0
				extra_distance_amt = 0
				tot_amount = 0

				if len(all_data) > 0:
					for index, line in all_data.iterrows():
						all_amt = line['total_before_taxes']
						all_numz = line['counter']
						distance_trip = line['trip_distance']
						ex_distance = line['extra_distance']
						tot_distance = line['total_distance']
						tot_fuel_amount = line['total_fuel_amount']
						tot_reward_amount = line['total_reward_amount']
						tot_amount = line['total_amount']
				s_vehicle = self.env['fleet.vehicle'].search([('vehicle_type', '=', rec)], limit=1)

				main_data.append({
					'vehicle_type':s_vehicle.vehicle_type.display_name,
					'vehicle_type_name':all_numz,
					'vehicle_status_name':all_amt,
					'driver_number':distance_trip,
					'bsg_driver':ex_distance,
					'transportation_no':tot_distance,
					'total_before_taxes':tot_fuel_amount,
					'total_distance':tot_reward_amount,
					'total_fuel_amount':tot_amount,
				})

				tot_bx = tot_bx + all_numz
				tot_invc_amt = tot_invc_amt + all_amt
				tot_trip = tot_trip + distance_trip
				tot_extra = tot_extra + ex_distance
				tott_distance = tott_distance + tot_distance
				tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
				tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
				tot_amt = tot_amt + tot_amount


		if report_mode == 'Bx Driver Summary Report':
			report_type_num = 3
			head = 'Bx Driver Summary Report'

			bsg_driver_list = []
			transport_lines = transport_lines.sort_values(by='order_date')
			for index, rec in transport_lines.iterrows():

				trans_vehicle = self.env['transport.management'].browse(rec.self_id).transportation_vehicle
				trans_driver = self.env['transport.management'].browse(rec.self_id).transportation_driver
				if trans_vehicle.bsg_driver.id not in bsg_driver_list:
					sum = get_sum(trans_vehicle.bsg_driver.id,transport_lines)


					main_data.append({
						'driver_code':trans_driver.driver_code,
						'bsg_driver':trans_vehicle.bsg_driver.name,
						'bsgjoining_date':trans_driver.bsgjoining_date,
						'employee_state':trans_driver.employee_state,
						'taq_number':trans_vehicle.taq_number,
						'vehicle_type_name':trans_vehicle.vehicle_type.vehicle_type_name,
						'vehicle_status_name':trans_vehicle.vehicle_status.vehicle_status_name,
						'all_numz':sum['all_numz'],
						'all_amt':sum['all_amt'],
						'distance_trip':sum['distance_trip'],
						'ex_distance':sum['ex_distance'],
						'tot_distance':sum['tot_distance'],
						'tot_fuel_amount':sum['tot_fuel_amount'],
						'tot_reward_amount':sum['tot_reward_amount'],
						'tot_amount':sum['tot_amount'],
					})

					bsg_driver_list.append(trans_vehicle.bsg_driver.id)

					tot_pos_amt = tot_pos_amt + sum['all_numz']
					tot_pos_num = tot_pos_num + sum['all_amt']
					tot_unpos_amt = tot_unpos_amt + sum['distance_trip']
					tot_unpos_num = tot_unpos_num + sum['ex_distance']
					tot_dis_num = tot_dis_num + sum['tot_distance']
					tot_fuel_num = tot_fuel_num + sum['tot_fuel_amount']
					tot_rwrd_num = tot_rwrd_num + sum['tot_reward_amount']
					tot_all_num = tot_all_num + sum['tot_amount']


		if report_mode == 'Bx User Summary Report':
			report_type_num = 4
			head = 'Bx User Summary Report'

			user_name_list = []
			transport_lines = transport_lines.sort_values(by='order_date')
			for index, rec in transport_lines.iterrows():

				trans_driver = self.env['transport.management'].browse(rec.self_id).transportation_driver
				id_x = self.env['transport.management'].browse(rec.self_id).create_uid.id
				if id_x not in user_name_list:

					sum = get_sum_by_user(id_x,transport_lines)

					main_data.append({
						'driver_code':trans_driver.driver_code,
						'create_uid':self.env['transport.management'].browse(rec.self_id).create_uid.name,
						'bsgjoining_date':trans_driver.bsgjoining_date,
						'employee_state':trans_driver.employee_state,
						'branch_ar_name':trans_driver.branch_id.branch_ar_name,
						'counter':sum['counter'],
						'total_before_taxes':sum['total_before_taxes'],
						'trip_distance':sum['trip_distance'],
						'extra_distance':sum['extra_distance'],
						'total_distance':sum['total_distance'],
						'total_fuel_amount':sum['total_fuel_amount'],
						'total_reward_amount':sum['total_reward_amount'],
						'total_amount':sum['total_amount'],

					})

					user_name_list.append(id_x)

					tot_count = tot_count + sum['counter'] 
					tot_count_bx = tot_count_bx + sum['total_before_taxes'] 
					tot_count_trip = tot_count_trip + sum['trip_distance'] 
					tot_count_extra = tot_count_extra + sum['extra_distance'] 
					tot_count_tot = tot_count_tot + sum['total_distance'] 
					tot_count_fuel = tot_count_fuel + sum['total_fuel_amount'] 
					tot_count_rwrd = tot_count_rwrd + sum['total_reward_amount'] 
					tot_count_amt = tot_count_amt + sum['total_amount'] 


		if report_mode == 'Bx Productivity Summary Loading Date Report':
			report_type_num = 5
			head = 'Bx Productivity Summary Loading Date Report'

			if period_group == 'day':

				transport_lines = transport_lines.sort_values(by='order_date')
				unique_date = transport_lines.date.unique()

				for rec in unique_date:

					all_data = transport_lines.loc[(transport_lines['date'] == rec)]
					all_data = all_data.groupby(['date'], as_index=False).sum()

					all_amt = 0
					posted_numz = 0
					tot_trip = 0
					tot_extra = 0
					tot_distance = 0
					tot_fuel_amount = 0
					tot_reward_amount = 0
					tot_amount = 0

					if len(all_data) > 0:
						for index, line in all_data.iterrows():
							all_amt = line['total_before_taxes']
							posted_numz = line['counter']
							tot_trip = line['trip_distance']
							tot_extra = line['extra_distance']
							tot_distance = line['total_distance']
							tot_fuel_amount = line['total_fuel_amount']
							tot_reward_amount = line['total_reward_amount']
							tot_amount = line['total_amount']


					main_data.append({
						'date':line['date'],
						'posted_numz':posted_numz,
						'all_amt':all_amt,
						'tot_trip':tot_trip,
						'tot_extra':tot_extra,
						'tot_distance':tot_distance,
						'tot_fuel_amount':tot_fuel_amount,
						'tot_reward_amount':tot_reward_amount,
						'tot_amount':tot_amount,

					})

					tot_bx = tot_bx + posted_numz
					tot_invc_amt = tot_invc_amt + all_amt
					tot_trip_amt = tot_trip_amt + tot_trip
					tot_extra_amt = tot_extra_amt + tot_extra
					tot_distance_amt = tot_distance_amt + tot_distance
					tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
					tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
					tot_amt = tot_amt + tot_amount

			if period_group == 'month':

				transport_lines['month_date'] = transport_lines['date'].astype(str).str[:7]
				unique_month = transport_lines.month_date.unique()

				for rec in unique_month:

					all_data = transport_lines.loc[(transport_lines['month_date'] == rec)]
					all_data = all_data.groupby(['month_date'], as_index=False).sum()

					all_amt = 0
					posted_numz = 0
					tot_trip = 0
					tot_extra = 0
					tot_distance = 0
					tot_fuel_amount = 0
					tot_reward_amount = 0
					tot_amount = 0

					if len(all_data) > 0:
						for index, line in all_data.iterrows():
							all_amt = line['total_before_taxes']
							posted_numz = line['counter']
							tot_trip = line['trip_distance']
							tot_extra = line['extra_distance']
							tot_distance = line['total_distance']
							tot_fuel_amount = line['total_fuel_amount']
							tot_reward_amount = line['total_reward_amount']
							tot_amount = line['total_amount']

					main_data.append({
						'date':line['month_date'],
						'posted_numz':posted_numz,
						'all_amt':all_amt,
						'tot_trip':tot_trip,
						'tot_extra':tot_extra,
						'tot_distance':tot_distance,
						'tot_fuel_amount':tot_fuel_amount,
						'tot_reward_amount':tot_reward_amount,
						'tot_amount':tot_amount,

					})

					tot_bx = tot_bx + posted_numz
					tot_invc_amt = tot_invc_amt + all_amt
					tot_trip_amt = tot_trip_amt + tot_trip
					tot_extra_amt = tot_extra_amt + tot_extra
					tot_distance_amt = tot_distance_amt + tot_distance
					tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
					tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
					tot_amt = tot_amt + tot_amount

			if period_group == 'year':

				transport_lines['year_date'] = transport_lines['date'].astype(str).str[:4]
				unique_year = transport_lines.year_date.unique()

				for rec in unique_year:

					all_data = transport_lines.loc[(transport_lines['year_date'] == rec)]
					all_data = all_data.groupby(['year_date'], as_index=False).sum()

					all_amt = 0
					posted_numz = 0
					tot_trip = 0
					tot_extra = 0
					tot_distance = 0
					tot_fuel_amount = 0
					tot_reward_amount = 0
					tot_amount = 0

					if len(all_data) > 0:
						for index, line in all_data.iterrows():
							all_amt = line['total_before_taxes']
							posted_numz = line['counter']
							tot_trip = line['trip_distance']
							tot_extra = line['extra_distance']
							tot_distance = line['total_distance']
							tot_fuel_amount = line['total_fuel_amount']
							tot_reward_amount = line['total_reward_amount']
							tot_amount = line['total_amount']


					main_data.append({
						'date':line['year_date'],
						'posted_numz':posted_numz,
						'all_amt':all_amt,
						'tot_trip':tot_trip,
						'tot_extra':tot_extra,
						'tot_distance':tot_distance,
						'tot_fuel_amount':tot_fuel_amount,
						'tot_reward_amount':tot_reward_amount,
						'tot_amount':tot_amount,

					})

					tot_bx = tot_bx + posted_numz
					tot_invc_amt = tot_invc_amt + all_amt
					tot_trip_amt = tot_trip_amt + tot_trip
					tot_extra_amt = tot_extra_amt + tot_extra
					tot_distance_amt = tot_distance_amt + tot_distance
					tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
					tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
					tot_amt = tot_amt + tot_amount


		return {
			'doc_ids': docids,
			'doc_model': 'fleet.vehicle.trip',
			'report_mode': report_mode,
			'main_data': main_data,
			'tot_bx': tot_bx,
			'tot_invc_amt': tot_invc_amt,
			'tot_trip': tot_trip,
			'tot_extra': tot_extra,
			'tott_distance': tott_distance,
			'tot_fuel_amt': tot_fuel_amt,
			'tot_rewrd_amt': tot_rewrd_amt,
			'tot_amt': tot_amt,
			'tot_pos_num': tot_pos_num,
			'tot_pos_amt': tot_pos_amt,
			'tot_unpos_num': tot_unpos_num,
			'tot_unpos_amt': tot_unpos_amt,
			'tot_dis_num': tot_dis_num,
			'tot_fuel_num': tot_fuel_num,
			'tot_rwrd_num': tot_rwrd_num,
			'tot_all_num': tot_all_num,
			'tot_count': tot_count,
			'tot_count_bx': tot_count_bx,
			'tot_count_trip': tot_count_trip,
			'tot_count_extra': tot_count_extra,
			'tot_count_tot': tot_count_tot,
			'tot_count_fuel': tot_count_fuel,
			'tot_count_rwrd': tot_count_rwrd,
			'tot_count_amt': tot_count_amt,
			'tot_invc_amt': tot_invc_amt,
			'tot_trip_amt': tot_trip_amt,
			'tot_extra_amt': tot_extra_amt,
			'tot_distance_amt': tot_distance_amt,
			'tot_fuel_amt': tot_fuel_amt,
			'tot_rewrd_amt': tot_rewrd_amt,
			'report_type_num': report_type_num,
			'head': head,
			'total_before_taxes': total_before_taxes,
			'total_distance': total_distance,
			'total_fuel_amount': total_fuel_amount,
			'total_reward_amount': total_reward_amount,
			'total_amount': total_amount,
			'total_bx': total_bx,
			'total_bxx': total_bxx,
			'tripp_distance': tripp_distance,
			'extr_distance': extr_distance,
			'totl_distance': totl_distance,
			'total_fuel_amount': total_fuel_amount,
			'total_reward_amount': total_reward_amount,
			'total_amount': total_amount,
		}

