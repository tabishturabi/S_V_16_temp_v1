import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import models, fields, api
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta
import sys, threading
sys.setrecursionlimit(20000)
from pytz import timezone,UTC


class BranchesVoucherXlsx(models.TransientModel):
	_name = 'report.bassami_fleet_trip_report.fleet_trip_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'

	# @api.multi
	def generate_xlsx_report(self, workbook, input_records, lines):
		data = input_records['form']
		wiz_obj = self.env['fleet.trip.report'].search([('id','=',self.env.context.get('active_id'))])


		main_heading = workbook.add_format({
			"bold": 1,
			"border": 1,
			"align": 'center',
			"valign": 'vcenter',
			"font_color": 'black',
			"bg_color": '#D3D3D3',
			'font_size': '10',
		})

		main_heading1 = workbook.add_format({
			"bold": 1,
			"border": 1,
			"align": 'right',
			"valign": 'vcenter',
			"font_color": 'black',
			"bg_color": '#D3D3D3',
			'font_size': '10',
		})

		main_heading2 = workbook.add_format({
			"bold": 1,
			"border": 1,
			"align": 'center',
			"valign": 'vcenter',
			"font_color": 'black',
			"bg_color": 'red',
			'font_size': '10',
		})

		# Create a format to use i	n the merged range.
		merge_format = workbook.add_format({
			'bold': 1,
			'border': 1,
			'align': 'center',
			'valign': 'vcenter',
			'font_size': '13',
			"font_color": 'black',
			'bg_color': '#D3D3D3'})

		main_data = workbook.add_format({
			"align": 'right',
			"valign": 'vcenter',
			'font_size': '8',
		})
		merge_format.set_shrink()
		main_heading.set_text_justlast(1)
		main_data.set_border()
		worksheet = workbook.add_worksheet('Fleet Trip Report')

		row = 3
		col = 0

		form = data['form']
		to = data['to']
		date = data['date']
		fleet_id = data['fleet_id']
		filter_type = data['filter_type']
		report_type = data['report_type']
		vehicle_type = data['vehicle_type']
		driver_code = data['driver_code']
		branch_from = data['branch_from']
		branch_to = data['branch_to']
		trip_type = data['trip_type']
		filter_date_by = data['filter_date_by']
		sa_date_condition = data['sa_date_condition']
		user_id = data['user_id']
		trip_status = data['trip_status']
		truck_load = data['truck_load']
		car_load = data['car_load']
		vehicle_group_id = data['vehicle_group_id']
		fuel_expense_type_id = data['fuel_expense_type_id']




		if form:
			form = datetime.strptime(form, '%Y-%m-%d %H:%M:%S')
			form = form + timedelta(hours=3)
		if to:
			to = datetime.strptime(to, '%Y-%m-%d %H:%M:%S')
			to = to + timedelta(hours=3)
		if date:
			date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
			date = date + timedelta(hours=3)


		final_data = []
		
		if report_type == 'fleet':
			if filter_type == 'all':
				fleets = []
				domain = []
				if vehicle_type:
					rec_names = wiz_obj.vehicle_type.mapped('display_name')
					names = ','.join(rec_names)
					worksheet.write(row, col, 'Vehicle Type', main_heading1)
					worksheet.write_string(row, col + 1,names, main_data)
					row += 1
					domain.append(('vehicle_type.id','in',vehicle_type))
				if fleet_id:
					rec_names = wiz_obj.fleet_id.mapped('display_name')
					names = ','.join(rec_names)
					worksheet.write(row, col, 'Fleets', main_heading1)
					worksheet.write_string(row, col + 1, names, main_data)
					row += 1
					domain.append(('id','in',fleet_id))
				if driver_code:
					rec_names = wiz_obj.driver_code.mapped('display_name')
					names = ','.join(rec_names)
					worksheet.write(row, col, 'Drivers', main_heading1)
					worksheet.write_string(row, col + 1, names, main_data)
					row += 1
					domain.append(('bsg_driver.id','in',driver_code))
				if branch_from:
					rec_names = wiz_obj.branch_from.mapped('display_name')
					names = ','.join(rec_names)
					worksheet.write(row, col, 'Branch From', main_heading1)
					worksheet.write_string(row, col + 1, names, main_data)
					row += 1
					domain.append(('trip_id.from_route_branch_id.id','in',branch_from))
				if user_id:
					worksheet.write(row, col, 'User', main_heading1)
					worksheet.write_string(row, col + 1, wiz_obj.user_id.display_name, main_data)
					row += 1
					domain.append(('create_uid', '=', wiz_obj.user_id.id))
				if trip_status:
					worksheet.write(row, col, 'Trip Status', main_heading1)
					worksheet.write_string(row, col + 1, wiz_obj.trip_status, main_data)
					row += 1
					domain.append(('trip_id.state', '=', trip_status))
				if truck_load:
					worksheet.write(row, col, 'Truck Load', main_heading1)
					worksheet.write_string(row, col + 1, wiz_obj.truck_load, main_data)
					row += 1
					domain.append(('trip_id.display_truck_load', '=', truck_load))
				if car_load:
					worksheet.write(row, col, 'Car Load', main_heading1)
					worksheet.write_string(row, col + 1, wiz_obj.car_load, main_data)
					row += 1
				# if vehicle_group_id:
				# 	worksheet.write(row, col, 'Vehicle Group Name', main_heading1)
				# 	worksheet.write_string(row, col + 1, wiz_obj.vehicle_group_id.display_name, main_data)
				# 	row += 1
				# 	domain.append(('', '=', vehicle_group_id))
				if fuel_expense_type_id:
					worksheet.write(row, col, 'Fuel Expense Type', main_heading1)
					worksheet.write_string(row, col + 1, wiz_obj.fuel_expense_type_id.display_name, main_data)
					row += 1
					domain.append(('trip_id.display_expense_mthod_id', '=', fuel_expense_type_id))

				if wiz_obj.trailer_sticker_no:
					worksheet.write(row, col, 'Trailer Sticker NO', main_heading1)
					worksheet.write_string(row, col + 1, wiz_obj.trailer_sticker_no.display_name, main_data)
					row += 1
					domain.append(('trailer_id', '=', wiz_obj.trailer_sticker_no.id))

				if wiz_obj.license_plate_no:
					worksheet.write(row, col, 'License Plate NO', main_heading1)
					worksheet.write_string(row, col + 1, wiz_obj.license_plate_no, main_data)
					row += 1
					domain.append(('license_plate', '=', wiz_obj.license_plate_no))

				if wiz_obj.vehicle_state_id:
					worksheet.write(row, col, 'Vehicle State', main_heading1)
					worksheet.write_string(row, col + 1, wiz_obj.vehicle_state_id.name, main_data)
					row += 1
					domain.append(('state_id', '=', wiz_obj.vehicle_state_id.id))

				if wiz_obj.driver_link == "linked":
					worksheet.write(row, col, 'Driver', main_heading1)
					worksheet.write_string(row, col + 1,"Linked", main_data)
					row += 1
					domain.append(('bsg_driver', '!=', None))
				if wiz_obj.driver_link == "unlinked":
					worksheet.write(row, col, 'Driver', main_heading1)
					worksheet.write_string(row, col + 1,"Unlinked", main_data)
					row += 1
					domain.append(('bsg_driver', '=', False))



				if branch_to:
					rec_names = wiz_obj.branch_to.mapped('display_name')
					names = ','.join(rec_names)
					worksheet.write(row, col, 'Branch To', main_heading1)
					worksheet.write_string(row, col + 1, names, main_data)
					row += 1
					fleet_vehicles = []
					vehicles_rec = self.env['fleet.vehicle'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(domain)
					for t in vehicles_rec:
						arrival_point = self.env['fleet.trip.arrival'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('trip_id.id','=',t.trip_id.id)])
						if arrival_point:
							end_arrival_to = arrival_point[-1]
							if end_arrival_to.waypoint_to.id in branch_to:
								fleet_vehicles.append(t)

				if not branch_to:
					fleet_vehicles = self.env['fleet.vehicle'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(domain)
				print('..................fleet_vehicles..............',fleet_vehicles)
				for vehicle_id in fleet_vehicles:
					if vehicle_id:
						if vehicle_id not in fleets:
							fleets.append(vehicle_id)

			for vehicle in fleets:
				print('...................vehicle...........................',vehicle)
				print('...................vehicle data type...........................',type(vehicle))
				# print('..........rec................',rec)
				# vehicles = []
				# for line in fleet_vehicles:
				# 	if line.id == rec.id:
				# 		vehicles.append(line)
				#
				# if vehicles:
				# 	vehicles = sorted(fleets, key=lambda k: k.trip_id.id)
				# 	vehicle =  (vehicles[-1])

				if car_load == "empty":
					if len(vehicle.trip_id.stock_picking_id) != 0:
						continue
				if car_load == "full":
					if len(vehicle.trip_id.stock_picking_id) <= 0:
						continue


				vech_state = ""
				start_point = ""
				end_point = ""
				start_time = ""
				act_end_time = ""
				end_time = ""
				trip_state = ""
				curr_desti = ""
				curr_arrival = ""
				driver_code = vehicle.bsg_driver.driver_code
				driver_name = vehicle.bsg_driver.name
				driver_phone = vehicle.bsg_driver.mobile_phone

				trips_point = self.env['fleet.vehicle.trip.waypoints'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('bsg_fleet_trip_id.id','=',vehicle.trip_id.id)])
				if trips_point:
					start_trip = trips_point[0]
					end_trip = trips_point[-1]

					start_point = start_trip.waypoint.loc_branch_id.branch_ar_name
					end_point = end_trip.waypoint.loc_branch_id.branch_ar_name

				arrival_point = self.env['fleet.trip.arrival'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('trip_id.id','=',vehicle.trip_id.id)])
				if arrival_point:
					arrival_point = sorted(arrival_point, key=lambda k: k.id)
					start_arrival = arrival_point[0]
					end_arrival = arrival_point[-1]

					if vehicle.trip_id.expected_start_date:
						start_time = vehicle.trip_id.expected_start_date + timedelta(hours=3)
					if start_arrival.trip_id.expected_end_date:
						act_end_time = start_arrival.trip_id.expected_end_date + timedelta(hours=3)
					if end_arrival.actual_end_time:
						end_time = end_arrival.actual_end_time + timedelta(hours=3)


				currarrival_point = self.env['fleet.trip.arrival'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('trip_id.id','=',vehicle.trip_id.id),('waypoint_to','=',vehicle.current_loc_id.id)],limit=1)
				if currarrival_point:
					curr_desti = currarrival_point.waypoint_to.route_waypoint_name
					if currarrival_point.actual_end_time:
						curr_arrival = currarrival_point.actual_end_time + timedelta(hours=3)

				trip_case = ''
				if vehicle.trip_id.trip_type == 'auto':
					trip_case = 'تخطيط تلقائي'
				if vehicle.trip_id.trip_type == 'manual':
					trip_case = 'تخطيط يدوي'
				if vehicle.trip_id.trip_type == 'local':
					trip_case = 'خدمي'

				if vehicle.state_id.name == 'Linked':
					vech_state =  "مرتبطة بمقطورة"
				elif vehicle.state_id.name == 'UnLinked':
					vech_state =  "غير مرتبطة بمقطورة"
				elif vehicle.state_id.name == 'Maintenance':
					vech_state =  "في الصيانة"
				elif vehicle.state_id.name == 'Draft':
					vech_state =  "مسوده"
				else:
					vech_state = vehicle.state_id.name


				if vehicle.trip_id.state == 'draft':
					trip_state =  "جديد"
				elif vehicle.trip_id.state == 'progress':
					trip_state =  "في الطريق"
				elif vehicle.trip_id.state == 'finished':
					trip_state =  "انتهت"
				elif vehicle.trip_id.state == 'done':
					trip_state =  "لانتهت"
				elif vehicle.trip_id.state == 'on_transit':
					trip_state =  "في ترانزيت"
				elif vehicle.trip_id.state == 'confirmed':
					trip_state =  "رحلة معتمده"
				elif vehicle.trip_id.state == 'cancelled':
					trip_state =  "رحلة ملغاه"
				else:
					trip_state = vehicle.trip_id.state

				total_fuel_amount = vehicle.trip_id.total_fuel_amount + vehicle.trip_id.add_reward_amt_frontend + vehicle.trip_id.tot_reward_amt_frontend
				total_distance = vehicle.trip_id.trip_distance + vehicle.trip_id.extra_distance
				actual_delay = "{0} Days {1} Hours ".format(0, 0)


				if end_time:
					print('................end_time.............',type(end_time))

				if end_time:
					end_time = end_time - timedelta(hours=3)
					delta = end_time - vehicle.trip_id.expected_end_date
					delta_temp = int(delta.total_seconds())
					if delta_temp < 0:
						delta_temp = abs(int(delta.total_seconds()))
						day, hours = self.get_days_hours(int(delta_temp / 3600), 0, 0)
						day = -day
						hours = -hours
						actual_delay = "{0} Days {1} Hours ".format(day, hours)
					else:
						day, hours = self.get_days_hours(int(delta_temp / 3600), 0, 0)
						actual_delay = "{0} Days {1} Hours ".format(day, hours)
				else:
					if vehicle.trip_id.expected_end_date:
						delta = datetime.now() - vehicle.trip_id.expected_end_date
						delta_temp = int(delta.total_seconds())
						if delta_temp < 0:
							delta_temp = abs(int(delta.total_seconds()))
							day, hours = self.get_days_hours(int(delta_temp / 3600), 0, 0)
							day = -day
							hours = -hours
							actual_delay = "{0} Days {1} Hours ".format(day, hours)
						else:
							day, hours = self.get_days_hours(int(delta_temp / 3600), 0, 0)
							actual_delay = "{0} Days {1} Hours ".format(day, hours)


				actual_start_datetime = False
				tz = timezone(self.env.context.get('tz') or self.env.user.tz)
				if vehicle.trip_id.actual_start_datetime:
					actual_start_datetime = UTC.localize(vehicle.trip_id.actual_start_datetime).astimezone(tz).replace(tzinfo=None)
				if end_time:
					end_time = UTC.localize(end_time).astimezone(tz).replace(tzinfo=None)


				final_data.append({
					'sticker':vehicle.taq_number,
					'driver_name':str(driver_name),
					'driver_code':str(driver_code),
					'driver_phone':driver_phone,
					'trailer_cat':vehicle.vehicle_type.vehicle_type_name,
					'vehicle_state':vech_state,
					'start_point':start_point,
					'end_point':end_point,
					'start_time':start_time,
					'act_end_time':act_end_time,
					'end_time':end_time,
					'trip_state':trip_state,
					'trip_case':trip_case,
					'curr_desti':curr_desti,
					'curr_arrival':curr_arrival,
					'trip_name':vehicle.trip_id.name,
					'trip_dis':vehicle.trip_id.trip_distance,
					'trip_extra_dis':vehicle.trip_id.extra_distance,
					'trip_total_fuel':vehicle.trip_id.total_fuel_amount,
					'trip_load':vehicle.trip_id.truck_load,
					'car_num':len(vehicle.trip_id.stock_picking_id),
					'create_user_name': vehicle.trip_id.create_uid.name,
					'create_user_code': vehicle.trip_id.create_uid.partner_id.ref,
					'actual_revenue': vehicle.trip_id.actual_revenue,
					'standard_revenue': vehicle.trip_id.standard_revenue,
					'total_fuel_expense_amount': total_fuel_amount,
					'add_reward_amt_frontend': vehicle.trip_id.add_reward_amt_frontend,
					'tot_reward_amt_frontend': vehicle.trip_id.tot_reward_amt_frontend,
					'total_distance': total_distance,
					'reason': vehicle.trip_id.reason,
					'actual_delay': actual_delay,
					'est_trip_time': vehicle.trip_id.est_trip_time,
					'actual_start_datetime': actual_start_datetime,
					'route_name': vehicle.trip_id.route_id.route_name,
					'display_expense_mthod_id': vehicle.trip_id.display_expense_mthod_id.display_name,
					'vehicle_group_name': vehicle.trip_id.vehicle_id.vehicle_group_name.display_name,
					'model_name': vehicle.trip_id.vehicle_id.model_id.display_name,
					'created_on':vehicle.trip_id.create_date,
					'vehicle_license_plate_no':vehicle.trip_id.vehicle_id.license_plate,
					'trailer_taq_no':vehicle.trip_id.trailer_id.trailer_taq_no,
					'trailer_ar_name':vehicle.trip_id.trailer_id.trailer_ar_name,
					'no_of_loading_vehicles_at_start_trip':vehicle.trip_id.trip_waypoint_ids.mapped('picked_items_count')[0] if vehicle.trip_id.trip_waypoint_ids.mapped('picked_items_count') else 0 ,
					'no_of_loading_vehicles_on_transit':vehicle.trip_id.total_cars - vehicle.trip_id.trip_waypoint_ids.mapped('picked_items_count')[0] if vehicle.trip_id.trip_waypoint_ids.mapped('picked_items_count') else 0,
					})
			worksheet.merge_range('A1:AI1', "Fleet Wise Report", merge_format)
			worksheet.merge_range('A2:AI2', " تقرير حركة الاسطول", merge_format)

			worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
			worksheet.write(row, col+1, 'Trip Seq No.', main_heading1)
			worksheet.write(row, col + 2, 'Created ON', main_heading1)
			# worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
			# worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
			worksheet.write(row, col + 3, 'Vehicle license Plate No.', main_heading1)
			worksheet.write(row, col + 4, 'Trailer Taq No', main_heading1)
			worksheet.write(row, col + 5, 'Trailer Ar Name', main_heading1)
			worksheet.write(row, col + 6, 'Employee ID', main_heading1)
			worksheet.write(row, col + 7, 'Driver Name', main_heading1)
			worksheet.write(row, col + 8, 'Driver Mobile No.', main_heading1)
			worksheet.write(row, col + 9, 'Vehicle Type', main_heading1)
			# worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
			worksheet.write(row, col + 10, 'Vehicle State', main_heading1)
			worksheet.write(row, col + 11, 'Start Branch', main_heading1)
			worksheet.write(row, col + 12, 'End Branch', main_heading1)
			# worksheet.write(row, col + 16, 'Route Name', main_heading1)
			worksheet.write(row, col + 13, 'Scheduled Start Date', main_heading1)
			worksheet.write(row, col + 14, 'Actual Start Date', main_heading1)
			worksheet.write(row, col + 15, 'Scheduled End Date', main_heading1)
			worksheet.write(row, col + 16, 'Est. Duration', main_heading1)
			worksheet.write(row, col + 17, 'Last waypoint Arrival Date', main_heading1)
			worksheet.write(row, col + 18, 'Actual Delay', main_heading1)
			worksheet.write(row, col + 19, 'Last Register Arrival Date', main_heading1)
			worksheet.write(row, col + 20, 'Vehicle Current Branch', main_heading1)
			# worksheet.write(row, col + 25, 'Truck Load', main_heading1)
			worksheet.write(row, col + 21, 'Trip Distance', main_heading1)
			worksheet.write(row, col + 22, 'Extra Distance', main_heading1)
			worksheet.write(row, col + 23, 'Reason', main_heading1)
			worksheet.write(row, col + 24, 'Total Distance', main_heading1)
			# worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
			# worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
			# worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
			# worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
			# worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
			# worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
			worksheet.write(row, col + 25, 'Total Cars', main_heading1)
			if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
				# worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
				# worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
				worksheet.write(row, col + 26, 'Trip Status', main_heading1)
				worksheet.write(row, col + 27, 'User Code', main_heading1)
				worksheet.write(row, col + 28, 'User', main_heading1)
				# worksheet.write(row, col + 42, 'No. of Payment voucher', main_heading1)
				# worksheet.write(row, col + 43, 'Payment voucher No.', main_heading1)
				# worksheet.write(row, col + 44, 'Vendor Bill No.', main_heading1)
			else:
				worksheet.write(row, col + 26, 'Trip Status', main_heading1)
				worksheet.write(row, col + 27, 'User Code', main_heading1)
				worksheet.write(row, col + 28, 'User', main_heading1)
				# worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
				# worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
				# worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
			row += 1

			worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
			worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
			worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
			# worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
			# worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
			worksheet.write(row, col + 3, 'رقم اللوحة', main_heading1)
			worksheet.write(row, col + 4, 'استيكر المقطورة', main_heading1)
			worksheet.write(row, col + 5, 'اسم المقطورة', main_heading1)
			worksheet.write(row, col + 6, 'كود السائق', main_heading1)
			worksheet.write(row, col + 7, 'إسم السائق', main_heading1)
			worksheet.write(row, col + 8, 'رقم الجوال', main_heading1)
			worksheet.write(row, col + 9, 'نوع الشاحنة', main_heading1)
			# worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
			worksheet.write(row, col + 10, 'حالة الشاحنة', main_heading1)
			worksheet.write(row, col + 11, 'فرع الإنطلاق', main_heading1)
			worksheet.write(row, col + 12, 'فرع الوصول', main_heading1)
			# worksheet.write(row, col + 16, 'خط السير', main_heading1)
			worksheet.write(row, col + 13, 'تاريخ بدء الجدولة', main_heading1)
			worksheet.write(row, col + 14, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
			worksheet.write(row, col + 15, 'تاريخ الوصول المتوقع', main_heading1)
			worksheet.write(row, col + 16, 'المدة الزمنية المتوقعة', main_heading1)
			worksheet.write(row, col + 17, 'تاريخ اخر محطة وصول', main_heading1)
			worksheet.write(row, col + 18, 'التاخير الفعلي', main_heading1)
			worksheet.write(row, col + 19, 'تاربخ اخر تسجيل وصول', main_heading1)
			worksheet.write(row, col + 20, 'الفرع الحالي لشاحنة', main_heading1)
			# worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
			worksheet.write(row, col + 21, 'مسـافة الرحــلة', main_heading1)
			worksheet.write(row, col + 22, 'مسافة أضافية', main_heading1)
			worksheet.write(row, col + 23, 'السبب', main_heading1)
			worksheet.write(row, col + 24, 'اجمالي المسافة', main_heading1)
			# worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
			# worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
			# worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
			# worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
			# worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
			# worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
			worksheet.write(row, col + 25, 'السيارات في الرحلة', main_heading1)
			if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
				# worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
				# worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
				worksheet.write(row, col + 26, 'حالة الرحلة', main_heading1)
				worksheet.write(row, col + 27, 'كود منشئ الرحلة', main_heading1)
				worksheet.write(row, col + 28, 'المستخدم', main_heading1)
				# worksheet.write(row, col + 42, 'عدد سندات الصرف للرحلة', main_heading1)
				# worksheet.write(row, col + 43, 'ارقام سند الصرف للرحلة', main_heading1)
				# worksheet.write(row, col + 44, 'ارقام فاتورة المورد', main_heading1)
			else:
				worksheet.write(row, col + 26, 'حالة الرحلة', main_heading1)
				worksheet.write(row, col + 27, 'كود منشئ الرحلة', main_heading1)
				worksheet.write(row, col + 28, 'المستخدم', main_heading1)
				# worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
				# worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
				# worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)

			worksheet.set_column('A:S', 20)

			row += 1
			col = 0
			trip_distance = 0
			extra_distance = 0
			total_distance = 0
			trip_total_fuel = 0
			total_reward_amt = 0
			additional_reward_amt = 0
			total_fuel_expense_amt = 0
			total_cars = 0
			standard_revenue = 0
			actual_revenue = 0
			if final_data:
				for rec in final_data:
					if rec['sticker']:
						worksheet.write_string(row, col, str(rec['sticker']), main_data)
					if rec['trip_name']:
						worksheet.write_string(row, col+1, str(rec['trip_name']), main_data)
					if rec['created_on']:
						worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
					# if rec['model_name']:
					# 	worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
					# if rec['vehicle_group_name']:
					# 	worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']), main_data)
					if rec['vehicle_license_plate_no']:
						worksheet.write_string(row, col + 3, str(rec['vehicle_license_plate_no']), main_data)
					if rec['trailer_taq_no']:
						worksheet.write_string(row, col + 4, str(rec['trailer_taq_no']), main_data)
					if rec['trailer_ar_name']:
						worksheet.write_string(row, col + 5, str(rec['trailer_ar_name']), main_data)
					if rec['driver_code']:
						worksheet.write_string(row, col + 6, str(rec['driver_code']), main_data)
					if rec['driver_name']:
						worksheet.write_string(row, col + 7, str(rec['driver_name']), main_data)
					if rec['driver_phone']:
						worksheet.write_string(row, col + 8, str(rec['driver_phone']), main_data)
					if rec['trailer_cat']:
						worksheet.write_string(row, col + 9, str(rec['trailer_cat']), main_data)
					# if rec['display_expense_mthod_id']:
					# 	worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']), main_data)
					if rec['vehicle_state']:
						worksheet.write_string(row, col + 10, str(rec['vehicle_state']), main_data)
					if rec['start_point']:
						worksheet.write_string(row, col + 11, str(rec['start_point']), main_data)
					if rec['end_point']:
						worksheet.write_string(row, col + 12, str(rec['end_point']), main_data)
					# if rec['route_name']:
					# 	worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
					if rec['start_time']:
						worksheet.write_string(row, col + 13, str(rec['start_time']), main_data)
					if rec['actual_start_datetime']:
						worksheet.write_string(row, col + 14, str(rec['actual_start_datetime']), main_data)
					if rec['act_end_time']:
						worksheet.write_string(row, col + 15, str(rec['act_end_time']), main_data)
					if rec['est_trip_time']:
						worksheet.write_string(row, col + 16, str(rec['est_trip_time']), main_data)
					if rec['end_time']:
						worksheet.write_string(row, col + 17, str(rec['end_time']), main_data)
					if rec['actual_delay']:
						worksheet.write_string(row, col + 18, str(rec['actual_delay']), main_data)
					if rec['curr_arrival']:
						worksheet.write_string(row, col + 19, str(rec['curr_arrival']), main_data)
					if rec['curr_desti']:
						worksheet.write_string(row, col + 20, str(rec['curr_desti']), main_data)
					# if rec['trip_load']:
					# 	worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
					if rec['trip_dis']:
						worksheet.write_number(row, col + 21, rec['trip_dis'], main_data)
						trip_distance += rec['trip_dis']
					if rec['trip_extra_dis']:
						worksheet.write_number(row, col + 22, rec['trip_extra_dis'], main_data)
						extra_distance += rec['trip_extra_dis']
					if rec['reason']:
						worksheet.write_string(row, col + 23, str(rec['reason']), main_data)
					if rec['total_distance']:
						worksheet.write_number(row, col + 24, rec['total_distance'], main_data)
						total_distance += rec['total_distance']
					# if rec['trip_total_fuel']:
					# 	worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
					# 	trip_total_fuel += rec['trip_total_fuel']
					# if rec['tot_reward_amt_frontend']:
					# 	worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'], main_data)
					# 	total_reward_amt += rec['tot_reward_amt_frontend']
					# if rec['add_reward_amt_frontend']:
					# 	worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'], main_data)
					# 	additional_reward_amt += rec['add_reward_amt_frontend']
					# if rec['total_fuel_expense_amount']:
					# 	worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'], main_data)
					# 	total_fuel_expense_amt += rec['total_fuel_expense_amount']
					# if rec['no_of_loading_vehicles_at_start_trip']:
					# 	worksheet.write_number(row, col + 34, rec['no_of_loading_vehicles_at_start_trip'], main_data)
					# if rec['no_of_loading_vehicles_on_transit']:
					# 	worksheet.write_number(row, col + 35, rec['no_of_loading_vehicles_on_transit'], main_data)
					if rec['car_num']:
						worksheet.write_number(row, col + 25, rec['car_num'], main_data)
						total_cars += rec['car_num']
					if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
						# if rec['standard_revenue']:
						# 	worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2), main_data)
						# 	standard_revenue += rec['standard_revenue']
						# if rec['actual_revenue']:
						# 	worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2), main_data)
						# 	actual_revenue += rec['actual_revenue']
						if rec['trip_state']:
							worksheet.write_string(row, col + 26, str(rec['trip_state']), main_data)
						if rec['create_user_name']:
							worksheet.write_string(row, col + 27, str(rec['create_user_code']), main_data)
						if rec['create_user_name']:
							worksheet.write_string(row, col + 28, str(rec['create_user_name']), main_data)
					else:
						if rec['trip_state']:
							worksheet.write_string(row, col + 26, str(rec['trip_state']), main_data)
						if rec['create_user_code']:
							worksheet.write_string(row, col + 27, str(rec['create_user_code']), main_data)
						if rec['create_user_name']:
							worksheet.write_string(row, col + 28, str(rec['create_user_name']), main_data)

					row += 1
				worksheet.write(row, col, 'Total', main_heading1)
				worksheet.write_number(row, col + 21, trip_distance, main_heading)
				worksheet.write_number(row, col + 22, extra_distance, main_heading)
				worksheet.write_number(row, col + 24, total_distance, main_heading)
				# worksheet.write_number(row, col + 25, trip_total_fuel, main_heading)
				# worksheet.write_number(row, col + 26, total_reward_amt, main_heading)
				# worksheet.write_number(row, col + 27, additional_reward_amt, main_heading)
				# worksheet.write_number(row, col + 28, total_fuel_expense_amt, main_heading)
				worksheet.write_number(row, col + 25, total_cars, main_heading)
				# if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
				# 	worksheet.write_number(row, col + 37, standard_revenue, main_heading)
				# 	worksheet.write_number(row, col + 38, actual_revenue, main_heading)
				row += 1

		if report_type == 'trip':

			# trips = self.env['fleet.vehicle.trip'].search([])
			domain = []
			if filter_date_by == 'scheduled_start_date':
				print('................sa_date_condition............', sa_date_condition)
				if sa_date_condition == 'is_equal_to':
					worksheet.write(row, col, 'Scheduled start date', main_heading1)
					worksheet.write(row, col + 1, '=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('expected_start_date', '=', date))
				if sa_date_condition == 'is_not_equal_to':
					worksheet.write(row, col, 'Scheduled start date', main_heading1)
					worksheet.write(row, col + 1, '!=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('expected_start_date', '!=', date))
				if sa_date_condition == 'is_after':
					worksheet.write(row, col, 'Scheduled start date', main_heading1)
					worksheet.write(row, col + 1, '>', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('expected_start_date', '>', date))
				if sa_date_condition == 'is_before':
					worksheet.write(row, col, 'Scheduled start date', main_heading1)
					worksheet.write(row, col + 1, '>', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					domain.append(('expected_start_date', '<', date))
				if sa_date_condition == 'is_after_or_equal_to':
					worksheet.write(row, col, 'Scheduled start date', main_heading1)
					worksheet.write(row, col + 1, '>', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('expected_start_date', '>=', date))
				if sa_date_condition == 'is_before_or_equal_to':
					worksheet.write(row, col, 'Scheduled start date', main_heading1)
					worksheet.write(row, col + 1, '>', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('expected_start_date', '<=', date))
				if sa_date_condition == 'is_between':
					print('...........row............', row)
					worksheet.write(row, col, 'Scheduled start date', main_heading1)
					worksheet.write(row, col + 1, 'From', main_heading1)
					worksheet.write_string(row, col + 2, str(form), main_data)
					worksheet.write(row, col + 3, 'TO', main_heading1)
					worksheet.write_string(row, col + 4, str(to), main_data)
					row += 1
					domain.append(('expected_start_date', '>', form))
					domain.append(('expected_start_date', '<', to))
				if sa_date_condition == 'is_set':
					worksheet.write(row, col, 'Scheduled start date', main_heading1)
					worksheet.write(row, col + 1, '!=', main_heading1)
					worksheet.write_string(row, col + 2, "None", main_data)
					row += 1
					domain.append(('expected_start_date', '!=', None))
				if sa_date_condition == 'is_not_set':
					worksheet.write(row, col, 'Scheduled start date', main_heading1)
					worksheet.write(row, col + 1, '=', main_heading1)
					worksheet.write_string(row, col + 2, "None", main_data)
					row += 1
					domain.append(('expected_start_date', '=', None))
			if filter_date_by == 'scheduled_end_date':
				if sa_date_condition == 'is_equal_to':
					worksheet.write(row, col, 'Scheduled end date', main_heading1)
					worksheet.write(row, col + 1, '=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('expected_end_date', '=', date))
				if sa_date_condition == 'is_not_equal_to':
					worksheet.write(row, col, 'Scheduled end date', main_heading1)
					worksheet.write(row, col + 1, '!=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('expected_end_date', '!=', date))
				if sa_date_condition == 'is_after':
					worksheet.write(row, col, 'Scheduled end date', main_heading1)
					worksheet.write(row, col + 1, '>', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('expected_end_date', '>', date))
				if sa_date_condition == 'is_before':
					worksheet.write(row, col, 'Scheduled end date', main_heading1)
					worksheet.write(row, col + 1, '<', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('expected_end_date', '<', date))
				if sa_date_condition == 'is_after_or_equal_to':
					worksheet.write(row, col, 'Scheduled end date', main_heading1)
					worksheet.write(row, col + 1, '>=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('expected_end_date', '>=', date))
				if sa_date_condition == 'is_before_or_equal_to':
					worksheet.write(row, col, 'Scheduled end date', main_heading1)
					worksheet.write(row, col + 1, '<=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('expected_end_date', '<=', date))
				if sa_date_condition == 'is_between':
					worksheet.write(row, col, 'Scheduled end date', main_heading1)
					worksheet.write(row, col + 1, 'From', main_heading1)
					worksheet.write_string(row, col + 2, str(form), main_data)
					worksheet.write(row, col + 3, 'TO', main_heading1)
					worksheet.write_string(row, col + 4, str(to), main_data)
					row += 1
					domain.append(('expected_end_date', '>', form))
					domain.append(('expected_end_date', '<', to))
				if sa_date_condition == 'is_set':
					worksheet.write(row, col, 'Scheduled end date', main_heading1)
					worksheet.write(row, col + 1, '!=', main_heading1)
					worksheet.write_string(row, col + 2, "None", main_data)
					row += 1
					domain.append(('expected_end_date', '!=', None))
				if sa_date_condition == 'is_not_set':
					worksheet.write(row, col, 'Scheduled end date', main_heading1)
					worksheet.write(row, col + 1, '=', main_heading1)
					worksheet.write_string(row, col + 2, "None", main_data)
					row += 1
					domain.append(('expected_end_date', '=', None))
			if filter_date_by == 'actual_start_date':
				if sa_date_condition == 'is_equal_to':
					worksheet.write(row, col, 'Actual start date', main_heading1)
					worksheet.write(row, col + 1, '=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('actual_start_datetime', '=', date))
				if sa_date_condition == 'is_not_equal_to':
					worksheet.write(row, col, 'Actual start date', main_heading1)
					worksheet.write(row, col + 1, '!=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('actual_start_datetime', '!=', date))
				if sa_date_condition == 'is_after':
					worksheet.write(row, col, 'Actual start date', main_heading1)
					worksheet.write(row, col + 1, '>', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('actual_start_datetime', '>', date))
				if sa_date_condition == 'is_before':
					worksheet.write(row, col, 'Actual start date', main_heading1)
					worksheet.write(row, col + 1, '<', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('actual_start_datetime', '<', date))
				if sa_date_condition == 'is_after_or_equal_to':
					worksheet.write(row, col, 'Actual start date', main_heading1)
					worksheet.write(row, col + 1, '>=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('actual_start_datetime', '>=', date))
				if sa_date_condition == 'is_before_or_equal_to':
					worksheet.write(row, col, 'Actual start date', main_heading1)
					worksheet.write(row, col + 1, '<=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('actual_start_datetime', '<=', date))
				if sa_date_condition == 'is_between':
					worksheet.write(row, col, 'Actual start date', main_heading1)
					worksheet.write(row, col + 1, 'From', main_heading1)
					worksheet.write_string(row, col + 2, str(form), main_data)
					worksheet.write(row, col + 3, 'TO', main_heading1)
					worksheet.write_string(row, col + 4, str(to), main_data)
					row += 1
					domain.append(('actual_start_datetime', '>', form))
					domain.append(('actual_start_datetime', '<', to))
				if sa_date_condition == 'is_set':
					worksheet.write(row, col, 'Actual start date', main_heading1)
					worksheet.write(row, col + 1, '!=', main_heading1)
					worksheet.write_string(row, col + 2, "None", main_data)
					row += 1
					domain.append(('actual_start_datetime', '!=', None))
				if sa_date_condition == 'is_not_set':
					worksheet.write(row, col, 'Actual start date', main_heading1)
					worksheet.write(row, col + 1, '=', main_heading1)
					worksheet.write_string(row, col + 2, "None", main_data)
					row += 1
					domain.append(('actual_start_datetime', '=', None))
			if filter_date_by == 'actual_end_date':
				if sa_date_condition == 'is_equal_to':
					worksheet.write(row, col, 'Actual end date', main_heading1)
					worksheet.write(row, col + 1, '=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('actual_end_datetime', '=', date))
				if sa_date_condition == 'is_not_equal_to':
					worksheet.write(row, col, 'Actual end date', main_heading1)
					worksheet.write(row, col + 1, '!=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					domain.append(('actual_end_datetime', '!=', date))
				if sa_date_condition == 'is_after':
					worksheet.write(row, col, 'Actual end date', main_heading1)
					worksheet.write(row, col + 1, '>', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('actual_end_datetime', '>', date))
				if sa_date_condition == 'is_before':
					worksheet.write(row, col, 'Actual end date', main_heading1)
					worksheet.write(row, col + 1, '<', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('actual_end_datetime', '<', date))
				if sa_date_condition == 'is_after_or_equal_to':
					worksheet.write(row, col, 'Actual end date', main_heading1)
					worksheet.write(row, col + 1, '>=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('actual_end_datetime', '>=', date))
				if sa_date_condition == 'is_before_or_equal_to':
					worksheet.write(row, col, 'Actual end date', main_heading1)
					worksheet.write(row, col + 1, '<=', main_heading1)
					worksheet.write_string(row, col + 2, str(date), main_data)
					row += 1
					domain.append(('actual_end_datetime', '<=', date))
				if sa_date_condition == 'is_between':
					worksheet.write(row, col, 'Actual end date', main_heading1)
					worksheet.write(row, col + 1, 'From', main_heading1)
					worksheet.write_string(row, col + 2, str(form), main_data)
					worksheet.write(row, col + 3, 'TO', main_heading1)
					worksheet.write_string(row, col + 4, str(to), main_data)
					row += 1
					domain.append(('actual_end_datetime', '>', form))
					domain.append(('actual_end_datetime', '<', to))
				if sa_date_condition == 'is_set':
					worksheet.write(row, col, 'Actual end date', main_heading1)
					worksheet.write(row, col + 1, '!=', main_heading1)
					worksheet.write_string(row, col + 2, "None", main_data)
					row += 1
					domain.append(('actual_end_datetime', '!=', None))
				if sa_date_condition == 'is_not_set':
					worksheet.write(row, col, 'Actual end date', main_heading1)
					worksheet.write(row, col + 1, '=', main_heading1)
					worksheet.write_string(row, col + 2, "None", main_data)
					row += 1
					domain.append(('actual_end_datetime', '=', None))
			if vehicle_type:
				rec_names = wiz_obj.vehicle_type.mapped('display_name')
				names = ','.join(rec_names)
				worksheet.write(row, col, 'Vehicle Type', main_heading1)
				worksheet.write_string(row, col + 1, names, main_data)
				row += 1
				domain.append(('vehicle_id.vehicle_type.id', 'in', vehicle_type))
			if fleet_id:
				rec_names = wiz_obj.fleet_id.mapped('display_name')
				names = ','.join(rec_names)
				worksheet.write(row, col, 'Fleets', main_heading1)
				worksheet.write_string(row, col + 1, names, main_data)
				row += 1
				domain.append(('vehicle_id.id', 'in', fleet_id))
			if driver_code:
				rec_names = wiz_obj.driver_code.mapped('display_name')
				names = ','.join(rec_names)
				worksheet.write(row, col, 'Drivers', main_heading1)
				worksheet.write_string(row, col + 1, names, main_data)
				row += 1
				domain.append(('driver_id.id', 'in', driver_code))
			if branch_from:
				rec_names = wiz_obj.branch_from.mapped('display_name')
				names = ','.join(rec_names)
				worksheet.write(row, col, 'Branch From', main_heading1)
				worksheet.write_string(row, col + 1, names, main_data)
				row += 1
				domain.append(('from_route_branch_id.id', 'in', branch_from))
			if user_id:
				worksheet.write(row, col, 'User', main_heading1)
				worksheet.write_string(row, col + 1, wiz_obj.user_id.display_name, main_data)
				row += 1
				domain.append(('create_uid', '=', wiz_obj.user_id.id))
			if trip_status:
				worksheet.write(row, col, 'Trip Status', main_heading1)
				worksheet.write_string(row, col + 1, wiz_obj.trip_status, main_data)
				row += 1
				domain.append(('state', '=', trip_status))
			if truck_load:
				worksheet.write(row, col, 'Truck Load', main_heading1)
				worksheet.write_string(row, col + 1, wiz_obj.truck_load, main_data)
				row += 1
				domain.append(('display_truck_load', '=', truck_load))
			if car_load:
				worksheet.write(row, col, 'Car Load', main_heading1)
				worksheet.write_string(row, col + 1, wiz_obj.car_load, main_data)
				row += 1
			# if vehicle_group_id:
			# 	worksheet.write(row, col, 'Vehicle Group Name', main_heading1)
			# 	worksheet.write_string(row, col + 1, wiz_obj.vehicle_group_id.display_name, main_data)
			# 	row += 1
			# 	domain.append(('', '=', vehicle_group_id))
			if fuel_expense_type_id:
				worksheet.write(row, col, 'Fuel Expense Type', main_heading1)
				worksheet.write_string(row, col + 1, wiz_obj.fuel_expense_type_id.display_name, main_data)
				row += 1
				domain.append(('display_expense_mthod_id', '=', fuel_expense_type_id))

			if wiz_obj.trailer_sticker_no:
				worksheet.write(row, col, 'Trailer Sticker NO', main_heading1)
				worksheet.write_string(row, col + 1, wiz_obj.trailer_sticker_no.display_name, main_data)
				row += 1
				domain.append(('trailer_id', '=', wiz_obj.trailer_sticker_no.id))

			if wiz_obj.license_plate_no:
				worksheet.write(row, col, 'License Plate NO', main_heading1)
				worksheet.write_string(row, col + 1, wiz_obj.license_plate_no, main_data)
				row += 1
				domain.append(('vehicle_id.license_plate', '=', wiz_obj.license_plate_no))

			if wiz_obj.vehicle_state_id:
				worksheet.write(row, col, 'Vehicle State', main_heading1)
				worksheet.write_string(row, col + 1, wiz_obj.vehicle_state_id.name, main_data)
				row += 1
				domain.append(('vehicle_id.state_id', '=', wiz_obj.vehicle_state_id.id))



			if branch_to:
				rec_names = wiz_obj.branch_to.mapped('display_name')
				names = ','.join(rec_names)
				worksheet.write(row, col, 'Branch To', main_heading1)
				worksheet.write_string(row, col + 1, names, main_data)
				row += 1
				trips = []
				trips_rec = self.env['fleet.vehicle.trip'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(domain, order='expected_start_date')
				for t in trips_rec:
					arrival_point = self.env['fleet.trip.arrival'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('trip_id.id','=',t.id)])
					if arrival_point:
						end_arrival_to = arrival_point[-1]
						if end_arrival_to.waypoint_to.id in branch_to:
							trips.append(t)

			if not branch_to:
				print('.............domain..............',domain)
				trips = self.env['fleet.vehicle.trip'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(domain, order='expected_start_date')
			
			for x in trips:
				if car_load == "empty":
					if len(x.stock_picking_id) != 0:
						continue
				if car_load == "full":
					if len(x.stock_picking_id) <= 0:
						continue
				curr_desti = ""
				curr_arrival = ""

				currarrival_point = self.env['fleet.trip.arrival'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('trip_id.id','=',x.id),('waypoint_to','=',x.vehicle_id.current_loc_id.id)],limit=1)
				if currarrival_point:
					curr_desti = currarrival_point.waypoint_to.route_waypoint_name
					if currarrival_point.actual_end_time:
						curr_arrival = currarrival_point.actual_end_time + timedelta(hours=3)
					# curr_arrival = currarrival_point.actual_end_time

				arrival_point = self.env['fleet.trip.arrival'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('trip_id.id','=',x.id)])
				if arrival_point:
					arrival_point = sorted(arrival_point, key=lambda k: k.id)
					start_arrival = arrival_point[0]
					end_arrival = arrival_point[-1]
					
					if x.expected_start_date:
						start_time = x.expected_start_date + timedelta(hours=3)
					else:
						start_time = " "
					if start_arrival.trip_id.expected_end_date:
						act_end_time = start_arrival.trip_id.expected_end_date + timedelta(hours=3)
					else:
						act_end_time = " "
					if end_arrival.actual_end_time:
						end_time = end_arrival.actual_end_time + timedelta(hours=3)
					else:
						end_time = ''
					branch_to = end_arrival.waypoint_to.route_waypoint_name


					# if start_arrival.actual_start_time >= form and end_time <= to:

					vech_state = ""
					start_point = ""
					end_point = ""
					trip_state = ""
					driver_code = x.driver_id.driver_code
					driver_name = x.driver_id.name
					driver_phone = x.driver_mobile_phone

					trips_point = self.env['fleet.vehicle.trip.waypoints'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('bsg_fleet_trip_id.id','=',x.id)])
					if trips_point:
						start_trip = trips_point[0]
						end_trip = trips_point[-1]

						start_point = start_trip.waypoint.loc_branch_id.branch_ar_name
						end_point = end_trip.waypoint.loc_branch_id.branch_ar_name

					if x.trip_type == 'auto':
						trip_case = 'تخطيط تلقائي'
					if x.trip_type == 'manual':
						trip_case = 'تخطيط يدوي'
					if x.trip_type == 'local':
						trip_case = 'خدمي'


					if x.vehicle_id.state_id.name == 'Linked':
						vech_state =  "مرتبطة بمقطورة"
					elif x.vehicle_id.state_id.name == 'UnLinked':
						vech_state =  "غير مرتبطة بمقطورة"
					elif x.vehicle_id.state_id.name == 'Maintenance':
						vech_state =  "في الصيانة"
					elif x.vehicle_id.state_id.name == 'Draft':
						vech_state =  "مسوده"
					else:
						vech_state = x.vehicle_id.state_id.name


					if x.state == 'draft':
						trip_state =  "جديد"
					elif x.state == 'progress':
						trip_state =  "في الطريق"
					elif x.state == 'finished':
						trip_state =  "انتهت"
					elif x.state == 'done':
						trip_state =  "انتهت"
					elif x.state == 'on_transit':
						trip_state =  "في ترانزيت"
					elif x.state == 'confirmed':
						trip_state =  "رحلة معتمده"
					elif x.state == 'cancelled':
						trip_state =  "رحلة ملغاه"
					else:
						trip_state = x.state

					total_fuel_amount = x.total_fuel_amount + x.add_reward_amt_frontend + x.tot_reward_amt_frontend
					total_distance = x.trip_distance + x.extra_distance
					actual_delay = "{0} Days {1} Hours ".format(0, 0)

					if end_time:
						end_time = end_time - timedelta(hours=3)
						delta = end_time - x.expected_end_date
						delta_temp = int(delta.total_seconds())
						if delta_temp < 0:
							delta_temp = abs(int(delta.total_seconds()))
							day, hours = self.get_days_hours(int(delta_temp / 3600), 0, 0)
							day = -day
							hours = -hours
							actual_delay = "{0} Days {1} Hours ".format(day, hours)
						else:
							day, hours = self.get_days_hours(int(delta_temp / 3600), 0, 0)
							actual_delay = "{0} Days {1} Hours ".format(day, hours)
					else:
						delta = datetime.now() - x.expected_end_date
						delta_temp = int(delta.total_seconds())
						if delta_temp < 0:
							delta_temp = abs(int(delta.total_seconds()))
							day, hours = self.get_days_hours(int(delta_temp / 3600), 0, 0)
							day = -day
							hours = -hours
							actual_delay = "{0} Days {1} Hours ".format(day, hours)
						else:
							day, hours = self.get_days_hours(int(delta_temp / 3600), 0, 0)
							actual_delay = "{0} Days {1} Hours ".format(day, hours)

					tz = timezone(self.env.context.get('tz') or self.env.user.tz)
					# Migration Note
					# if vehicle.trip_id.actual_start_datetime:
					if x.vehicle_id.trip_id.actual_start_datetime:
						actual_start_datetime = UTC.localize(x.vehicle_id.trip_id.actual_start_datetime).astimezone(tz).replace(tzinfo=None)
					if end_time:
						end_time = UTC.localize(end_time).astimezone(tz).replace(tzinfo=None)

					final_data.append({
						'sticker':x.vehicle_id.taq_number,
						'driver_name':str(driver_name),
						'driver_code':str(driver_code),
						'driver_phone':driver_phone,
						'trailer_cat':x.vehicle_id.vehicle_type.vehicle_type_name,
						'vehicle_state':vech_state,
						'start_point':start_point,
						'end_point':end_point,
						'start_time':start_time,
						'act_end_time':act_end_time,
						'end_time':end_time,
						'trip_state':trip_state,
						'trip_case':trip_case,
						'curr_desti':curr_desti,
						'curr_arrival':curr_arrival,
						'trip_name':x.name,
						'trip_dis':x.trip_distance,
						'trip_extra_dis':x.extra_distance,
						'trip_total_fuel':x.total_fuel_amount,
						'trip_load':x.truck_load,
						'car_num':len(x.stock_picking_id),
						'create_user_name':x.create_uid.name,
						'create_user_code':x.create_uid.partner_id.ref,
						'actual_revenue':x.actual_revenue,
						'standard_revenue':x.standard_revenue,
						'total_fuel_expense_amount':total_fuel_amount,
						'add_reward_amt_frontend':x.add_reward_amt_frontend,
						'tot_reward_amt_frontend':x.tot_reward_amt_frontend,
						'total_distance':total_distance,
						'reason':x.reason,
						'actual_delay':actual_delay,
						'est_trip_time':x.est_trip_time,
						'actual_start_datetime':x.actual_start_datetime,
						'route_name':x.route_id.route_name,
						'display_expense_mthod_id':x.display_expense_mthod_id.display_name,
						'vehicle_group_name':x.vehicle_id.vehicle_group_name.display_name,
						'model_name':x.vehicle_id.model_id.display_name,
						'created_on': x.create_date,
						'vehicle_license_plate_no': x.vehicle_id.license_plate,
						'trailer_taq_no': x.trailer_id.trailer_taq_no,
						'trailer_ar_name': x.trailer_id.trailer_ar_name,
						'no_of_loading_vehicles_at_start_trip': x.trip_waypoint_ids.mapped('picked_items_count')[0],
						'no_of_loading_vehicles_on_transit': x.total_cars -
															 x.trip_waypoint_ids.mapped('picked_items_count')[0],
						'display_expense_type':x.display_expense_type,
					})
			if wiz_obj.group_by == "all":
				worksheet.merge_range('A1:AI1',"Trip Report" ,merge_format)
				worksheet.merge_range('A2:AI2',"تفرير الرحلات",merge_format)

				worksheet.write(row,col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row,col+1, 'Trip Seq No.', main_heading1)
				worksheet.write(row,col+2, 'Created ON', main_heading1)
				worksheet.write(row,col+3, 'Vehicle Name', main_heading1)
				worksheet.write(row,col+4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row,col+5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row,col+6, 'Trailer Taq No', main_heading1)
				worksheet.write(row,col+7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row,col+8, 'Employee ID', main_heading1)
				worksheet.write(row,col+9, 'Driver Name', main_heading1)
				worksheet.write(row,col+10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row,col+11, 'Vehicle Type', main_heading1)
				worksheet.write(row,col+12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row,col+13, 'Vehicle State', main_heading1)
				worksheet.write(row,col+14, 'Start Branch', main_heading1)
				worksheet.write(row,col+15, 'End Branch', main_heading1)
				worksheet.write(row,col+16, 'Route Name', main_heading1)
				worksheet.write(row,col+17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row,col+18, 'Actual Start Date', main_heading1)
				worksheet.write(row,col+19, 'Scheduled End Date', main_heading1)
				worksheet.write(row,col+20, 'Est. Duration', main_heading1)
				worksheet.write(row,col+21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row,col+22, 'Actual Delay', main_heading1)
				worksheet.write(row,col+23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row,col+24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row,col+25, 'Truck Load', main_heading1)
				worksheet.write(row,col+26, 'Trip Distance', main_heading1)
				worksheet.write(row,col+27, 'Extra Distance', main_heading1)
				worksheet.write(row,col+28, 'Reason', main_heading1)
				worksheet.write(row,col+29, 'Total Distance', main_heading1)
				worksheet.write(row,col+30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row,col+31, 'Total Reward amount', main_heading1)
				worksheet.write(row,col+32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row,col+33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row,col+34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row,col+35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row,col+36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row,col+37, 'Standard Revenue', main_heading1)
					worksheet.write(row,col+38, 'Actual Revenue', main_heading1)
					worksheet.write(row,col+39, 'Trip Status', main_heading1)
					worksheet.write(row,col+40, 'User Code', main_heading1)
					worksheet.write(row,col+41, 'User', main_heading1)
					# worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					# worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					# worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					# worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					# worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					# worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row+=1


				worksheet.write(row,col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row,col+1, 'رقم الرحلة', main_heading1)
				worksheet.write(row,col+2, 'أنشئ في', main_heading1)
				worksheet.write(row,col+3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row,col+4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row,col+5, 'رقم اللوحة', main_heading1)
				worksheet.write(row,col+6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row,col+7, 'اسم المقطورة', main_heading1)
				worksheet.write(row,col+8, 'كود السائق', main_heading1)
				worksheet.write(row,col+9, 'إسم السائق', main_heading1)
				worksheet.write(row,col+10, 'رقم الجوال', main_heading1)
				worksheet.write(row,col+11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row,col+12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row,col+13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row,col+14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row,col+15, 'فرع الوصول', main_heading1)
				worksheet.write(row,col+16, 'خط السير', main_heading1)
				worksheet.write(row,col+17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row,col+18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row,col+19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row,col+20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row,col+21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row,col+22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row,col+23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row,col+24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row,col+25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row,col+26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row,col+27, 'مسافة أضافية', main_heading1)
				worksheet.write(row,col+28, 'السبب', main_heading1)
				worksheet.write(row,col+29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row,col+30, 'مصروف الطريق', main_heading1)
				worksheet.write(row,col+31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row,col+32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row,col+33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row,col+34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row,col+35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row,col+36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row,col+37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row,col+38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row,col+39, 'حالة الرحلة', main_heading1)
					worksheet.write(row,col+40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row,col+41, 'المستخدم', main_heading1)
					# worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					# worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					# worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					# worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					# worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					# worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)
				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					for rec in final_data:
						if rec['sticker']:
							worksheet.write_string (row, col,str(rec['sticker']),main_data)
						if rec['trip_name']:
							worksheet.write_string (row, col+1,str(rec['trip_name']),main_data)
						if rec['created_on']:
							worksheet.write_string (row, col+2,str(rec['created_on']),main_data)
						if rec['model_name']:
							worksheet.write_string (row, col+3,str(rec['model_name']),main_data)
						if rec['vehicle_group_name']:
							worksheet.write_string (row, col+4,str(rec['vehicle_group_name']),main_data)
						if rec['vehicle_license_plate_no']:
							worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']), main_data)
						if rec['trailer_taq_no']:
							worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
						if rec['trailer_ar_name']:
							worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
						if rec['driver_code']:
							worksheet.write_string (row, col+8,str(rec['driver_code']),main_data)
						if rec['driver_name']:
							worksheet.write_string (row, col+9,str(rec['driver_name']),main_data)
						if rec['driver_phone']:
							worksheet.write_string (row, col+10,str(rec['driver_phone']),main_data)
						if rec['trailer_cat']:
							worksheet.write_string (row, col+11,str(rec['trailer_cat']),main_data)
						if rec['display_expense_mthod_id']:
							worksheet.write_string (row, col+12,str(rec['display_expense_mthod_id']),main_data)
						if rec['vehicle_state']:
							worksheet.write_string (row, col+13,str(rec['vehicle_state']),main_data)
						if rec['start_point']:
							worksheet.write_string (row, col+14,str(rec['start_point']),main_data)
						if rec['end_point']:
							worksheet.write_string (row, col+15,str(rec['end_point']),main_data)
						if rec['route_name']:
							worksheet.write_string (row, col+16,str(rec['route_name']),main_data)
						if rec['start_time']:
							worksheet.write_string (row, col+17,str(rec['start_time']),main_data)
						if rec['actual_start_datetime']:
							worksheet.write_string (row, col+18,str(rec['actual_start_datetime']),main_data)
						if rec['act_end_time']:
							worksheet.write_string (row, col+19,str(rec['act_end_time']),main_data)
						if rec['est_trip_time']:
							worksheet.write_string (row, col+20,str(rec['est_trip_time']),main_data)
						if rec['end_time']:
							worksheet.write_string (row, col+21,str(rec['end_time']),main_data)
						if rec['actual_delay']:
							worksheet.write_string (row, col+22,str(rec['actual_delay']),main_data)
						if rec['curr_arrival']:
							worksheet.write_string (row, col+23,str(rec['curr_arrival']),main_data)
						if rec['curr_desti']:
							worksheet.write_string (row, col+24,str(rec['curr_desti']),main_data)
						if rec['trip_load']:
							worksheet.write_string (row, col+25,str(rec['trip_load']),main_data)
						if rec['trip_dis']:
							worksheet.write_number(row, col+26,rec['trip_dis'],main_data)
							trip_distance += rec['trip_dis']
						if rec['trip_extra_dis']:
							worksheet.write_number(row, col+27,rec['trip_extra_dis'],main_data)
							extra_distance += rec['trip_extra_dis']
						if rec['reason']:
							worksheet.write_string(row, col+28,str(rec['reason']),main_data)
						if rec['total_distance']:
							worksheet.write_number(row, col+29,rec['total_distance'],main_data)
							total_distance += rec['total_distance']
						if rec['trip_total_fuel']:
							worksheet.write_number (row, col+30,rec['trip_total_fuel'],main_data)
							total_fuel_expense_amount += rec['trip_total_fuel']
						if rec['tot_reward_amt_frontend']:
							worksheet.write_number (row, col+31,rec['tot_reward_amt_frontend'],main_data)
							total_reward_amt += rec['tot_reward_amt_frontend']
						if rec['add_reward_amt_frontend']:
							worksheet.write_number (row, col+32,rec['add_reward_amt_frontend'],main_data)
							additional_reward_amt += rec['add_reward_amt_frontend']
						if rec['total_fuel_expense_amount']:
							worksheet.write_number (row, col+33,rec['total_fuel_expense_amount'],main_data)
							total_fuel_expense_amt += rec['total_fuel_expense_amount']
						if rec['no_of_loading_vehicles_at_start_trip']:
							worksheet.write_number (row, col+34,rec['no_of_loading_vehicles_at_start_trip'],main_data)
						if rec['no_of_loading_vehicles_on_transit']:
							worksheet.write_number (row, col+35,rec['no_of_loading_vehicles_on_transit'],main_data)
						if rec['car_num']:
							worksheet.write_number (row, col+36,rec['car_num'],main_data)
							total_cars += rec['car_num']
						if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
							if rec['standard_revenue']:
								worksheet.write_number (row, col+37,round(rec['standard_revenue'],2),main_data)
								standard_revenue += rec['standard_revenue']
							if rec['actual_revenue']:
								worksheet.write_number (row, col+38,round(rec['actual_revenue'],2),main_data)
								actual_revenue += rec['actual_revenue']
							if rec['trip_state']:
								worksheet.write_string (row, col+39,str(rec['trip_state']),main_data)
							if rec['create_user_code']:
								worksheet.write_string (row, col+40,str(rec['create_user_code']),main_data)
							if rec['create_user_name']:
								worksheet.write_string (row, col+41,str(rec['create_user_name']),main_data)
						else:
							if rec['trip_state']:
								worksheet.write_string (row, col+37,str(rec['trip_state']),main_data)
							if rec['create_user_code']:
								worksheet.write_string (row, col+38,str(rec['create_user_code']),main_data)
							if rec['create_user_name']:
								worksheet.write_string (row, col+39,str(rec['create_user_name']),main_data)
						row += 1
					worksheet.write(row, col, 'Total', main_heading1)
					worksheet.write_number(row, col + 22, trip_distance, main_heading)
					worksheet.write_number(row, col + 23, extra_distance, main_heading)
					worksheet.write_number(row, col + 25, total_distance, main_heading)
					worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
					worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
					worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
					worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
					worksheet.write_number(row, col + 30, total_cars, main_heading)
					if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
						worksheet.write_number(row, col + 31, standard_revenue, main_heading)
						worksheet.write_number(row, col + 32, actual_revenue, main_heading)
					row += 1
			if wiz_obj.group_by == "vehicle_sticker_no":
				worksheet.merge_range('A1:AI1', "Trip Report Group By Vehicle Sticker No", merge_format)
				worksheet.merge_range('A2:AI2', "تفرير الرحلات", merge_format)

				worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row, col + 1, 'Trip Seq No.', main_heading1)
				worksheet.write(row, col + 2, 'Created ON', main_heading1)
				worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
				worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row, col + 5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row, col + 6, 'Trailer Taq No', main_heading1)
				worksheet.write(row, col + 7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row, col + 8, 'Employee ID', main_heading1)
				worksheet.write(row, col + 9, 'Driver Name', main_heading1)
				worksheet.write(row, col + 10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row, col + 11, 'Vehicle Type', main_heading1)
				worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row, col + 13, 'Vehicle State', main_heading1)
				worksheet.write(row, col + 14, 'Start Branch', main_heading1)
				worksheet.write(row, col + 15, 'End Branch', main_heading1)
				worksheet.write(row, col + 16, 'Route Name', main_heading1)
				worksheet.write(row, col + 17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row, col + 18, 'Actual Start Date', main_heading1)
				worksheet.write(row, col + 19, 'Scheduled End Date', main_heading1)
				worksheet.write(row, col + 20, 'Est. Duration', main_heading1)
				worksheet.write(row, col + 21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row, col + 22, 'Actual Delay', main_heading1)
				worksheet.write(row, col + 23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row, col + 24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row, col + 25, 'Truck Load', main_heading1)
				worksheet.write(row, col + 26, 'Trip Distance', main_heading1)
				worksheet.write(row, col + 27, 'Extra Distance', main_heading1)
				worksheet.write(row, col + 28, 'Reason', main_heading1)
				worksheet.write(row, col + 29, 'Total Distance', main_heading1)
				worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
				worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row, col + 36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
					worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
					worksheet.write(row, col + 39, 'Trip Status', main_heading1)
					worksheet.write(row, col + 40, 'User Code', main_heading1)
					worksheet.write(row, col + 41, 'User', main_heading1)
					worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row += 1

				worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
				worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
				worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row, col + 5, 'رقم اللوحة', main_heading1)
				worksheet.write(row, col + 6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row, col + 7, 'اسم المقطورة', main_heading1)
				worksheet.write(row, col + 8, 'كود السائق', main_heading1)
				worksheet.write(row, col + 9, 'إسم السائق', main_heading1)
				worksheet.write(row, col + 10, 'رقم الجوال', main_heading1)
				worksheet.write(row, col + 11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row, col + 13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row, col + 14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row, col + 15, 'فرع الوصول', main_heading1)
				worksheet.write(row, col + 16, 'خط السير', main_heading1)
				worksheet.write(row, col + 17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row, col + 18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row, col + 19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row, col + 20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row, col + 21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row, col + 22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row, col + 23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row, col + 24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row, col + 26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row, col + 27, 'مسافة أضافية', main_heading1)
				worksheet.write(row, col + 28, 'السبب', main_heading1)
				worksheet.write(row, col + 29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
				worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row, col + 36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row, col + 39, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 41, 'المستخدم', main_heading1)
					worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)
				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					sticker_no_list = []
					for data in final_data:
						if data['sticker']:
							if data['sticker'] not in sticker_no_list:
								sticker_no_list.append(data['sticker'])
					if sticker_no_list:
						for sticker_no in sticker_no_list:
							if sticker_no:
								worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
								worksheet.write_string(row, col+1,sticker_no, main_data)
								worksheet.write(row, col+2, 'كـود الشاحــنة', main_heading1)
								row += 1
								for rec in final_data:
									if rec['sticker'] == sticker_no:
										if rec['sticker']:
											worksheet.write_string(row, col, str(rec['sticker']), main_data)
										if rec['trip_name']:
											worksheet.write_string(row, col + 1, str(rec['trip_name']), main_data)
										if rec['created_on']:
											worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
										if rec['model_name']:
											worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
										if rec['vehicle_group_name']:
											worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']),
																   main_data)
										if rec['vehicle_license_plate_no']:
											worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']),
																   main_data)
										if rec['trailer_taq_no']:
											worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
										if rec['trailer_ar_name']:
											worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
										if rec['driver_code']:
											worksheet.write_string(row, col + 8, str(rec['driver_code']), main_data)
										if rec['driver_name']:
											worksheet.write_string(row, col + 9, str(rec['driver_name']), main_data)
										if rec['driver_phone']:
											worksheet.write_string(row, col + 10, str(rec['driver_phone']), main_data)
										if rec['trailer_cat']:
											worksheet.write_string(row, col + 11, str(rec['trailer_cat']), main_data)
										if rec['display_expense_mthod_id']:
											worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']),
																   main_data)
										if rec['vehicle_state']:
											worksheet.write_string(row, col + 13, str(rec['vehicle_state']), main_data)
										if rec['start_point']:
											worksheet.write_string(row, col + 14, str(rec['start_point']), main_data)
										if rec['end_point']:
											worksheet.write_string(row, col + 15, str(rec['end_point']), main_data)
										if rec['route_name']:
											worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
										if rec['start_time']:
											worksheet.write_string(row, col + 17, str(rec['start_time']), main_data)
										if rec['actual_start_datetime']:
											worksheet.write_string(row, col + 18, str(rec['actual_start_datetime']),
																   main_data)
										if rec['act_end_time']:
											worksheet.write_string(row, col + 19, str(rec['act_end_time']), main_data)
										if rec['est_trip_time']:
											worksheet.write_string(row, col + 20, str(rec['est_trip_time']), main_data)
										if rec['end_time']:
											worksheet.write_string(row, col + 21, str(rec['end_time']), main_data)
										if rec['actual_delay']:
											worksheet.write_string(row, col + 22, str(rec['actual_delay']), main_data)
										if rec['curr_arrival']:
											worksheet.write_string(row, col + 23, str(rec['curr_arrival']), main_data)
										if rec['curr_desti']:
											worksheet.write_string(row, col + 24, str(rec['curr_desti']), main_data)
										if rec['trip_load']:
											worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
										if rec['trip_dis']:
											worksheet.write_number(row, col + 26, rec['trip_dis'], main_data)
											trip_distance += rec['trip_dis']
										if rec['trip_extra_dis']:
											worksheet.write_number(row, col + 27, rec['trip_extra_dis'], main_data)
											extra_distance += rec['trip_extra_dis']
										if rec['reason']:
											worksheet.write_string(row, col + 28, str(rec['reason']), main_data)
										if rec['total_distance']:
											worksheet.write_number(row, col + 29, rec['total_distance'], main_data)
											total_distance += rec['total_distance']
										if rec['trip_total_fuel']:
											worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
											total_fuel_expense_amount += rec['trip_total_fuel']
										if rec['tot_reward_amt_frontend']:
											worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'],
																   main_data)
											total_reward_amt += rec['tot_reward_amt_frontend']
										if rec['add_reward_amt_frontend']:
											worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'],
																   main_data)
											additional_reward_amt += rec['add_reward_amt_frontend']
										if rec['total_fuel_expense_amount']:
											worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'],
																   main_data)
											total_fuel_expense_amt += rec['total_fuel_expense_amount']
										if rec['no_of_loading_vehicles_at_start_trip']:
											worksheet.write_number(row, col + 34,
																   rec['no_of_loading_vehicles_at_start_trip'],
																   main_data)
										if rec['no_of_loading_vehicles_on_transit']:
											worksheet.write_number(row, col + 35,
																   rec['no_of_loading_vehicles_on_transit'], main_data)
										if rec['car_num']:
											worksheet.write_number(row, col + 36, rec['car_num'], main_data)
											total_cars += rec['car_num']
										if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
											if rec['standard_revenue']:
												worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2),
																	   main_data)
												standard_revenue += rec['standard_revenue']
											if rec['actual_revenue']:
												worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2),
																	   main_data)
												actual_revenue += rec['actual_revenue']
											if rec['trip_state']:
												worksheet.write_string(row, col + 39, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 40, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 41, str(rec['create_user_name']),
																	   main_data)
										else:
											if rec['trip_state']:
												worksheet.write_string(row, col + 37, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 38, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 39, str(rec['create_user_name']),
																	   main_data)
										row += 1
								worksheet.write(row, col, 'Total', main_heading1)
								worksheet.write_number(row, col + 22, trip_distance, main_heading)
								worksheet.write_number(row, col + 23, extra_distance, main_heading)
								worksheet.write_number(row, col + 25, total_distance, main_heading)
								worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
								worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
								worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
								worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
								worksheet.write_number(row, col + 30, total_cars, main_heading)
								if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
									worksheet.write_number(row, col + 31, standard_revenue, main_heading)
									worksheet.write_number(row, col + 32, actual_revenue, main_heading)
								row += 1
			if wiz_obj.group_by == "driver_code":
				worksheet.merge_range('A1:AI1', "Trip Report Group By Driver Code", merge_format)
				worksheet.merge_range('A2:AI2', "تفرير الرحلات", merge_format)

				worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row, col + 1, 'Trip Seq No.', main_heading1)
				worksheet.write(row, col + 2, 'Created ON', main_heading1)
				worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
				worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row, col + 5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row, col + 6, 'Trailer Taq No', main_heading1)
				worksheet.write(row, col + 7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row, col + 8, 'Employee ID', main_heading1)
				worksheet.write(row, col + 9, 'Driver Name', main_heading1)
				worksheet.write(row, col + 10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row, col + 11, 'Vehicle Type', main_heading1)
				worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row, col + 13, 'Vehicle State', main_heading1)
				worksheet.write(row, col + 14, 'Start Branch', main_heading1)
				worksheet.write(row, col + 15, 'End Branch', main_heading1)
				worksheet.write(row, col + 16, 'Route Name', main_heading1)
				worksheet.write(row, col + 17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row, col + 18, 'Actual Start Date', main_heading1)
				worksheet.write(row, col + 19, 'Scheduled End Date', main_heading1)
				worksheet.write(row, col + 20, 'Est. Duration', main_heading1)
				worksheet.write(row, col + 21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row, col + 22, 'Actual Delay', main_heading1)
				worksheet.write(row, col + 23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row, col + 24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row, col + 25, 'Truck Load', main_heading1)
				worksheet.write(row, col + 26, 'Trip Distance', main_heading1)
				worksheet.write(row, col + 27, 'Extra Distance', main_heading1)
				worksheet.write(row, col + 28, 'Reason', main_heading1)
				worksheet.write(row, col + 29, 'Total Distance', main_heading1)
				worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
				worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row, col + 36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
					worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
					worksheet.write(row, col + 39, 'Trip Status', main_heading1)
					worksheet.write(row, col + 40, 'User Code', main_heading1)
					worksheet.write(row, col + 41, 'User', main_heading1)
					worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row += 1

				worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
				worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
				worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row, col + 5, 'رقم اللوحة', main_heading1)
				worksheet.write(row, col + 6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row, col + 7, 'اسم المقطورة', main_heading1)
				worksheet.write(row, col + 8, 'كود السائق', main_heading1)
				worksheet.write(row, col + 9, 'إسم السائق', main_heading1)
				worksheet.write(row, col + 10, 'رقم الجوال', main_heading1)
				worksheet.write(row, col + 11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row, col + 13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row, col + 14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row, col + 15, 'فرع الوصول', main_heading1)
				worksheet.write(row, col + 16, 'خط السير', main_heading1)
				worksheet.write(row, col + 17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row, col + 18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row, col + 19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row, col + 20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row, col + 21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row, col + 22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row, col + 23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row, col + 24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row, col + 26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row, col + 27, 'مسافة أضافية', main_heading1)
				worksheet.write(row, col + 28, 'السبب', main_heading1)
				worksheet.write(row, col + 29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
				worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row, col + 36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row, col + 39, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 41, 'المستخدم', main_heading1)
					worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)

				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					driver_code_list = []
					for data in final_data:
						if data['driver_code']:
							if data['driver_code'] not in driver_code_list:
								sticker_no_list.append(data['driver_code'])
					if driver_code_list:
						for driver_code in driver_code_list:
							if driver_code:
								worksheet.write(row, col, 'Driver Code', main_heading1)
								worksheet.write_string(row, col+1,driver_code, main_data)
								worksheet.write(row, col+2, 'كود السائق', main_heading1)
								row += 1
								for rec in final_data:
									if rec['driver_code'] == driver_code:
										if rec['sticker']:
											worksheet.write_string(row, col, str(rec['sticker']), main_data)
										if rec['trip_name']:
											worksheet.write_string(row, col + 1, str(rec['trip_name']), main_data)
										if rec['created_on']:
											worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
										if rec['model_name']:
											worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
										if rec['vehicle_group_name']:
											worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']),
																   main_data)
										if rec['vehicle_license_plate_no']:
											worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']),
																   main_data)
										if rec['trailer_taq_no']:
											worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
										if rec['trailer_ar_name']:
											worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
										if rec['driver_code']:
											worksheet.write_string(row, col + 8, str(rec['driver_code']), main_data)
										if rec['driver_name']:
											worksheet.write_string(row, col + 9, str(rec['driver_name']), main_data)
										if rec['driver_phone']:
											worksheet.write_string(row, col + 10, str(rec['driver_phone']), main_data)
										if rec['trailer_cat']:
											worksheet.write_string(row, col + 11, str(rec['trailer_cat']), main_data)
										if rec['display_expense_mthod_id']:
											worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']),
																   main_data)
										if rec['vehicle_state']:
											worksheet.write_string(row, col + 13, str(rec['vehicle_state']), main_data)
										if rec['start_point']:
											worksheet.write_string(row, col + 14, str(rec['start_point']), main_data)
										if rec['end_point']:
											worksheet.write_string(row, col + 15, str(rec['end_point']), main_data)
										if rec['route_name']:
											worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
										if rec['start_time']:
											worksheet.write_string(row, col + 17, str(rec['start_time']), main_data)
										if rec['actual_start_datetime']:
											worksheet.write_string(row, col + 18, str(rec['actual_start_datetime']),
																   main_data)
										if rec['act_end_time']:
											worksheet.write_string(row, col + 19, str(rec['act_end_time']), main_data)
										if rec['est_trip_time']:
											worksheet.write_string(row, col + 20, str(rec['est_trip_time']), main_data)
										if rec['end_time']:
											worksheet.write_string(row, col + 21, str(rec['end_time']), main_data)
										if rec['actual_delay']:
											worksheet.write_string(row, col + 22, str(rec['actual_delay']), main_data)
										if rec['curr_arrival']:
											worksheet.write_string(row, col + 23, str(rec['curr_arrival']), main_data)
										if rec['curr_desti']:
											worksheet.write_string(row, col + 24, str(rec['curr_desti']), main_data)
										if rec['trip_load']:
											worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
										if rec['trip_dis']:
											worksheet.write_number(row, col + 26, rec['trip_dis'], main_data)
											trip_distance += rec['trip_dis']
										if rec['trip_extra_dis']:
											worksheet.write_number(row, col + 27, rec['trip_extra_dis'], main_data)
											extra_distance += rec['trip_extra_dis']
										if rec['reason']:
											worksheet.write_string(row, col + 28, str(rec['reason']), main_data)
										if rec['total_distance']:
											worksheet.write_number(row, col + 29, rec['total_distance'], main_data)
											total_distance += rec['total_distance']
										if rec['trip_total_fuel']:
											worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
											total_fuel_expense_amount += rec['trip_total_fuel']
										if rec['tot_reward_amt_frontend']:
											worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'],
																   main_data)
											total_reward_amt += rec['tot_reward_amt_frontend']
										if rec['add_reward_amt_frontend']:
											worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'],
																   main_data)
											additional_reward_amt += rec['add_reward_amt_frontend']
										if rec['total_fuel_expense_amount']:
											worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'],
																   main_data)
											total_fuel_expense_amt += rec['total_fuel_expense_amount']
										if rec['no_of_loading_vehicles_at_start_trip']:
											worksheet.write_number(row, col + 34,
																   rec['no_of_loading_vehicles_at_start_trip'],
																   main_data)
										if rec['no_of_loading_vehicles_on_transit']:
											worksheet.write_number(row, col + 35,
																   rec['no_of_loading_vehicles_on_transit'], main_data)
										if rec['car_num']:
											worksheet.write_number(row, col + 36, rec['car_num'], main_data)
											total_cars += rec['car_num']
										if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
											if rec['standard_revenue']:
												worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2),
																	   main_data)
												standard_revenue += rec['standard_revenue']
											if rec['actual_revenue']:
												worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2),
																	   main_data)
												actual_revenue += rec['actual_revenue']
											if rec['trip_state']:
												worksheet.write_string(row, col + 39, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 40, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 41, str(rec['create_user_name']),
																	   main_data)
										else:
											if rec['trip_state']:
												worksheet.write_string(row, col + 37, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 38, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 39, str(rec['create_user_name']),
																	   main_data)
										row += 1
								worksheet.write(row, col, 'Total', main_heading1)
								worksheet.write_number(row, col + 22, trip_distance, main_heading)
								worksheet.write_number(row, col + 23, extra_distance, main_heading)
								worksheet.write_number(row, col + 25, total_distance, main_heading)
								worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
								worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
								worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
								worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
								worksheet.write_number(row, col + 30, total_cars, main_heading)
								if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
									worksheet.write_number(row, col + 31, standard_revenue, main_heading)
									worksheet.write_number(row, col + 32, actual_revenue, main_heading)
								row += 1
			if wiz_obj.group_by == "vehicle_type":
				worksheet.merge_range('A1:AI1', "Trip Report Group By Driver Code", merge_format)
				worksheet.merge_range('A2:AI2', "تفرير الرحلات", merge_format)

				worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row, col + 1, 'Trip Seq No.', main_heading1)
				worksheet.write(row, col + 2, 'Created ON', main_heading1)
				worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
				worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row, col + 5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row, col + 6, 'Trailer Taq No', main_heading1)
				worksheet.write(row, col + 7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row, col + 8, 'Employee ID', main_heading1)
				worksheet.write(row, col + 9, 'Driver Name', main_heading1)
				worksheet.write(row, col + 10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row, col + 11, 'Vehicle Type', main_heading1)
				worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row, col + 13, 'Vehicle State', main_heading1)
				worksheet.write(row, col + 14, 'Start Branch', main_heading1)
				worksheet.write(row, col + 15, 'End Branch', main_heading1)
				worksheet.write(row, col + 16, 'Route Name', main_heading1)
				worksheet.write(row, col + 17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row, col + 18, 'Actual Start Date', main_heading1)
				worksheet.write(row, col + 19, 'Scheduled End Date', main_heading1)
				worksheet.write(row, col + 20, 'Est. Duration', main_heading1)
				worksheet.write(row, col + 21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row, col + 22, 'Actual Delay', main_heading1)
				worksheet.write(row, col + 23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row, col + 24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row, col + 25, 'Truck Load', main_heading1)
				worksheet.write(row, col + 26, 'Trip Distance', main_heading1)
				worksheet.write(row, col + 27, 'Extra Distance', main_heading1)
				worksheet.write(row, col + 28, 'Reason', main_heading1)
				worksheet.write(row, col + 29, 'Total Distance', main_heading1)
				worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
				worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row, col + 36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
					worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
					worksheet.write(row, col + 39, 'Trip Status', main_heading1)
					worksheet.write(row, col + 40, 'User Code', main_heading1)
					worksheet.write(row, col + 41, 'User', main_heading1)
					worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row += 1

				worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
				worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
				worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row, col + 5, 'رقم اللوحة', main_heading1)
				worksheet.write(row, col + 6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row, col + 7, 'اسم المقطورة', main_heading1)
				worksheet.write(row, col + 8, 'كود السائق', main_heading1)
				worksheet.write(row, col + 9, 'إسم السائق', main_heading1)
				worksheet.write(row, col + 10, 'رقم الجوال', main_heading1)
				worksheet.write(row, col + 11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row, col + 13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row, col + 14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row, col + 15, 'فرع الوصول', main_heading1)
				worksheet.write(row, col + 16, 'خط السير', main_heading1)
				worksheet.write(row, col + 17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row, col + 18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row, col + 19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row, col + 20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row, col + 21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row, col + 22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row, col + 23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row, col + 24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row, col + 26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row, col + 27, 'مسافة أضافية', main_heading1)
				worksheet.write(row, col + 28, 'السبب', main_heading1)
				worksheet.write(row, col + 29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
				worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row, col + 36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row, col + 39, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 41, 'المستخدم', main_heading1)
					worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)

				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					vehicle_type_list = []
					for data in final_data:
						if data['trailer_cat']:
							if data['trailer_cat'] not in vehicle_type_list:
								vehicle_type_list.append(data['trailer_cat'])
					if vehicle_type_list:
						for vehicle_type in vehicle_type_list:
							if vehicle_type:
								worksheet.write(row, col, 'Vehicle Type', main_heading1)
								worksheet.write_string(row, col+1,vehicle_type, main_data)
								worksheet.write(row, col+2, 'نوع الشاحنة', main_heading1)
								row += 1
								for rec in final_data:
									if rec['trailer_cat'] == vehicle_type:
										if rec['sticker']:
											worksheet.write_string(row, col, str(rec['sticker']), main_data)
										if rec['trip_name']:
											worksheet.write_string(row, col + 1, str(rec['trip_name']), main_data)
										if rec['created_on']:
											worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
										if rec['model_name']:
											worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
										if rec['vehicle_group_name']:
											worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']),
																   main_data)
										if rec['vehicle_license_plate_no']:
											worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']),
																   main_data)
										if rec['trailer_taq_no']:
											worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
										if rec['trailer_ar_name']:
											worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
										if rec['driver_code']:
											worksheet.write_string(row, col + 8, str(rec['driver_code']), main_data)
										if rec['driver_name']:
											worksheet.write_string(row, col + 9, str(rec['driver_name']), main_data)
										if rec['driver_phone']:
											worksheet.write_string(row, col + 10, str(rec['driver_phone']), main_data)
										if rec['trailer_cat']:
											worksheet.write_string(row, col + 11, str(rec['trailer_cat']), main_data)
										if rec['display_expense_mthod_id']:
											worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']),
																   main_data)
										if rec['vehicle_state']:
											worksheet.write_string(row, col + 13, str(rec['vehicle_state']), main_data)
										if rec['start_point']:
											worksheet.write_string(row, col + 14, str(rec['start_point']), main_data)
										if rec['end_point']:
											worksheet.write_string(row, col + 15, str(rec['end_point']), main_data)
										if rec['route_name']:
											worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
										if rec['start_time']:
											worksheet.write_string(row, col + 17, str(rec['start_time']), main_data)
										if rec['actual_start_datetime']:
											worksheet.write_string(row, col + 18, str(rec['actual_start_datetime']),
																   main_data)
										if rec['act_end_time']:
											worksheet.write_string(row, col + 19, str(rec['act_end_time']), main_data)
										if rec['est_trip_time']:
											worksheet.write_string(row, col + 20, str(rec['est_trip_time']), main_data)
										if rec['end_time']:
											worksheet.write_string(row, col + 21, str(rec['end_time']), main_data)
										if rec['actual_delay']:
											worksheet.write_string(row, col + 22, str(rec['actual_delay']), main_data)
										if rec['curr_arrival']:
											worksheet.write_string(row, col + 23, str(rec['curr_arrival']), main_data)
										if rec['curr_desti']:
											worksheet.write_string(row, col + 24, str(rec['curr_desti']), main_data)
										if rec['trip_load']:
											worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
										if rec['trip_dis']:
											worksheet.write_number(row, col + 26, rec['trip_dis'], main_data)
											trip_distance += rec['trip_dis']
										if rec['trip_extra_dis']:
											worksheet.write_number(row, col + 27, rec['trip_extra_dis'], main_data)
											extra_distance += rec['trip_extra_dis']
										if rec['reason']:
											worksheet.write_string(row, col + 28, str(rec['reason']), main_data)
										if rec['total_distance']:
											worksheet.write_number(row, col + 29, rec['total_distance'], main_data)
											total_distance += rec['total_distance']
										if rec['trip_total_fuel']:
											worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
											total_fuel_expense_amount += rec['trip_total_fuel']
										if rec['tot_reward_amt_frontend']:
											worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'],
																   main_data)
											total_reward_amt += rec['tot_reward_amt_frontend']
										if rec['add_reward_amt_frontend']:
											worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'],
																   main_data)
											additional_reward_amt += rec['add_reward_amt_frontend']
										if rec['total_fuel_expense_amount']:
											worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'],
																   main_data)
											total_fuel_expense_amt += rec['total_fuel_expense_amount']
										if rec['no_of_loading_vehicles_at_start_trip']:
											worksheet.write_number(row, col + 34,
																   rec['no_of_loading_vehicles_at_start_trip'],
																   main_data)
										if rec['no_of_loading_vehicles_on_transit']:
											worksheet.write_number(row, col + 35,
																   rec['no_of_loading_vehicles_on_transit'], main_data)
										if rec['car_num']:
											worksheet.write_number(row, col + 36, rec['car_num'], main_data)
											total_cars += rec['car_num']
										if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
											if rec['standard_revenue']:
												worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2),
																	   main_data)
												standard_revenue += rec['standard_revenue']
											if rec['actual_revenue']:
												worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2),
																	   main_data)
												actual_revenue += rec['actual_revenue']
											if rec['trip_state']:
												worksheet.write_string(row, col + 39, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 40, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 41, str(rec['create_user_name']),
																	   main_data)
										else:
											if rec['trip_state']:
												worksheet.write_string(row, col + 37, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 38, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 39, str(rec['create_user_name']),
																	   main_data)
										row += 1
								worksheet.write(row, col, 'Total', main_heading1)
								worksheet.write_number(row, col + 22, trip_distance, main_heading)
								worksheet.write_number(row, col + 23, extra_distance, main_heading)
								worksheet.write_number(row, col + 25, total_distance, main_heading)
								worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
								worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
								worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
								worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
								worksheet.write_number(row, col + 30, total_cars, main_heading)
								if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
									worksheet.write_number(row, col + 31, standard_revenue, main_heading)
									worksheet.write_number(row, col + 32, actual_revenue, main_heading)
								row += 1
			if wiz_obj.group_by == "vehicle_group_name":
				worksheet.merge_range('A1:AI1', "Trip Report Group By Driver Code", merge_format)
				worksheet.merge_range('A2:AI2', "تفرير الرحلات", merge_format)

				worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row, col + 1, 'Trip Seq No.', main_heading1)
				worksheet.write(row, col + 2, 'Created ON', main_heading1)
				worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
				worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row, col + 5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row, col + 6, 'Trailer Taq No', main_heading1)
				worksheet.write(row, col + 7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row, col + 8, 'Employee ID', main_heading1)
				worksheet.write(row, col + 9, 'Driver Name', main_heading1)
				worksheet.write(row, col + 10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row, col + 11, 'Vehicle Type', main_heading1)
				worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row, col + 13, 'Vehicle State', main_heading1)
				worksheet.write(row, col + 14, 'Start Branch', main_heading1)
				worksheet.write(row, col + 15, 'End Branch', main_heading1)
				worksheet.write(row, col + 16, 'Route Name', main_heading1)
				worksheet.write(row, col + 17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row, col + 18, 'Actual Start Date', main_heading1)
				worksheet.write(row, col + 19, 'Scheduled End Date', main_heading1)
				worksheet.write(row, col + 20, 'Est. Duration', main_heading1)
				worksheet.write(row, col + 21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row, col + 22, 'Actual Delay', main_heading1)
				worksheet.write(row, col + 23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row, col + 24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row, col + 25, 'Truck Load', main_heading1)
				worksheet.write(row, col + 26, 'Trip Distance', main_heading1)
				worksheet.write(row, col + 27, 'Extra Distance', main_heading1)
				worksheet.write(row, col + 28, 'Reason', main_heading1)
				worksheet.write(row, col + 29, 'Total Distance', main_heading1)
				worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
				worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row, col + 36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
					worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
					worksheet.write(row, col + 39, 'Trip Status', main_heading1)
					worksheet.write(row, col + 40, 'User Code', main_heading1)
					worksheet.write(row, col + 41, 'User', main_heading1)
					worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row += 1

				worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
				worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
				worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row, col + 5, 'رقم اللوحة', main_heading1)
				worksheet.write(row, col + 6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row, col + 7, 'اسم المقطورة', main_heading1)
				worksheet.write(row, col + 8, 'كود السائق', main_heading1)
				worksheet.write(row, col + 9, 'إسم السائق', main_heading1)
				worksheet.write(row, col + 10, 'رقم الجوال', main_heading1)
				worksheet.write(row, col + 11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row, col + 13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row, col + 14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row, col + 15, 'فرع الوصول', main_heading1)
				worksheet.write(row, col + 16, 'خط السير', main_heading1)
				worksheet.write(row, col + 17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row, col + 18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row, col + 19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row, col + 20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row, col + 21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row, col + 22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row, col + 23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row, col + 24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row, col + 26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row, col + 27, 'مسافة أضافية', main_heading1)
				worksheet.write(row, col + 28, 'السبب', main_heading1)
				worksheet.write(row, col + 29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
				worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row, col + 36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row, col + 39, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 41, 'المستخدم', main_heading1)
					worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)
				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					vehicle_group_name_list = []
					for data in final_data:
						if data['vehicle_group_name']:
							if data['vehicle_group_name'] not in vehicle_group_name_list:
								sticker_no_list.append(data['vehicle_group_name'])
					if vehicle_group_name_list:
						for vehicle_group_name in vehicle_group_name_list:
							if vehicle_group_name:
								worksheet.write(row, col, 'Vehicle Group Name', main_heading1)
								worksheet.write_string(row, col+1,vehicle_group_name, main_data)
								worksheet.write(row, col+2, 'اسم مجموعة الشاحنة', main_heading1)
								row += 1
								for rec in final_data:
									if rec['vehicle_group_name'] == vehicle_group_name:
										if rec['sticker']:
											worksheet.write_string(row, col, str(rec['sticker']), main_data)
										if rec['trip_name']:
											worksheet.write_string(row, col + 1, str(rec['trip_name']), main_data)
										if rec['created_on']:
											worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
										if rec['model_name']:
											worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
										if rec['vehicle_group_name']:
											worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']),
																   main_data)
										if rec['vehicle_license_plate_no']:
											worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']),
																   main_data)
										if rec['trailer_taq_no']:
											worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
										if rec['trailer_ar_name']:
											worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
										if rec['driver_code']:
											worksheet.write_string(row, col + 8, str(rec['driver_code']), main_data)
										if rec['driver_name']:
											worksheet.write_string(row, col + 9, str(rec['driver_name']), main_data)
										if rec['driver_phone']:
											worksheet.write_string(row, col + 10, str(rec['driver_phone']), main_data)
										if rec['trailer_cat']:
											worksheet.write_string(row, col + 11, str(rec['trailer_cat']), main_data)
										if rec['display_expense_mthod_id']:
											worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']),
																   main_data)
										if rec['vehicle_state']:
											worksheet.write_string(row, col + 13, str(rec['vehicle_state']), main_data)
										if rec['start_point']:
											worksheet.write_string(row, col + 14, str(rec['start_point']), main_data)
										if rec['end_point']:
											worksheet.write_string(row, col + 15, str(rec['end_point']), main_data)
										if rec['route_name']:
											worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
										if rec['start_time']:
											worksheet.write_string(row, col + 17, str(rec['start_time']), main_data)
										if rec['actual_start_datetime']:
											worksheet.write_string(row, col + 18, str(rec['actual_start_datetime']),
																   main_data)
										if rec['act_end_time']:
											worksheet.write_string(row, col + 19, str(rec['act_end_time']), main_data)
										if rec['est_trip_time']:
											worksheet.write_string(row, col + 20, str(rec['est_trip_time']), main_data)
										if rec['end_time']:
											worksheet.write_string(row, col + 21, str(rec['end_time']), main_data)
										if rec['actual_delay']:
											worksheet.write_string(row, col + 22, str(rec['actual_delay']), main_data)
										if rec['curr_arrival']:
											worksheet.write_string(row, col + 23, str(rec['curr_arrival']), main_data)
										if rec['curr_desti']:
											worksheet.write_string(row, col + 24, str(rec['curr_desti']), main_data)
										if rec['trip_load']:
											worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
										if rec['trip_dis']:
											worksheet.write_number(row, col + 26, rec['trip_dis'], main_data)
											trip_distance += rec['trip_dis']
										if rec['trip_extra_dis']:
											worksheet.write_number(row, col + 27, rec['trip_extra_dis'], main_data)
											extra_distance += rec['trip_extra_dis']
										if rec['reason']:
											worksheet.write_string(row, col + 28, str(rec['reason']), main_data)
										if rec['total_distance']:
											worksheet.write_number(row, col + 29, rec['total_distance'], main_data)
											total_distance += rec['total_distance']
										if rec['trip_total_fuel']:
											worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
											total_fuel_expense_amount += rec['trip_total_fuel']
										if rec['tot_reward_amt_frontend']:
											worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'],
																   main_data)
											total_reward_amt += rec['tot_reward_amt_frontend']
										if rec['add_reward_amt_frontend']:
											worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'],
																   main_data)
											additional_reward_amt += rec['add_reward_amt_frontend']
										if rec['total_fuel_expense_amount']:
											worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'],
																   main_data)
											total_fuel_expense_amt += rec['total_fuel_expense_amount']
										if rec['no_of_loading_vehicles_at_start_trip']:
											worksheet.write_number(row, col + 34,
																   rec['no_of_loading_vehicles_at_start_trip'],
																   main_data)
										if rec['no_of_loading_vehicles_on_transit']:
											worksheet.write_number(row, col + 35,
																   rec['no_of_loading_vehicles_on_transit'], main_data)
										if rec['car_num']:
											worksheet.write_number(row, col + 36, rec['car_num'], main_data)
											total_cars += rec['car_num']
										if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
											if rec['standard_revenue']:
												worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2),
																	   main_data)
												standard_revenue += rec['standard_revenue']
											if rec['actual_revenue']:
												worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2),
																	   main_data)
												actual_revenue += rec['actual_revenue']
											if rec['trip_state']:
												worksheet.write_string(row, col + 39, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 40, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 41, str(rec['create_user_name']),
																	   main_data)
										else:
											if rec['trip_state']:
												worksheet.write_string(row, col + 37, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 38, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 39, str(rec['create_user_name']),
																	   main_data)
										row += 1
								worksheet.write(row, col, 'Total', main_heading1)
								worksheet.write_number(row, col + 22, trip_distance, main_heading)
								worksheet.write_number(row, col + 23, extra_distance, main_heading)
								worksheet.write_number(row, col + 25, total_distance, main_heading)
								worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
								worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
								worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
								worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
								worksheet.write_number(row, col + 30, total_cars, main_heading)
								if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
									worksheet.write_number(row, col + 31, standard_revenue, main_heading)
									worksheet.write_number(row, col + 32, actual_revenue, main_heading)
								row += 1
			if wiz_obj.group_by == "fuel_expense_type":
				worksheet.merge_range('A1:AI1', "Trip Report Group By Driver Code", merge_format)
				worksheet.merge_range('A2:AI2', "تفرير الرحلات", merge_format)

				worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row, col + 1, 'Trip Seq No.', main_heading1)
				worksheet.write(row, col + 2, 'Created ON', main_heading1)
				worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
				worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row, col + 5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row, col + 6, 'Trailer Taq No', main_heading1)
				worksheet.write(row, col + 7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row, col + 8, 'Employee ID', main_heading1)
				worksheet.write(row, col + 9, 'Driver Name', main_heading1)
				worksheet.write(row, col + 10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row, col + 11, 'Vehicle Type', main_heading1)
				worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row, col + 13, 'Vehicle State', main_heading1)
				worksheet.write(row, col + 14, 'Start Branch', main_heading1)
				worksheet.write(row, col + 15, 'End Branch', main_heading1)
				worksheet.write(row, col + 16, 'Route Name', main_heading1)
				worksheet.write(row, col + 17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row, col + 18, 'Actual Start Date', main_heading1)
				worksheet.write(row, col + 19, 'Scheduled End Date', main_heading1)
				worksheet.write(row, col + 20, 'Est. Duration', main_heading1)
				worksheet.write(row, col + 21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row, col + 22, 'Actual Delay', main_heading1)
				worksheet.write(row, col + 23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row, col + 24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row, col + 25, 'Truck Load', main_heading1)
				worksheet.write(row, col + 26, 'Trip Distance', main_heading1)
				worksheet.write(row, col + 27, 'Extra Distance', main_heading1)
				worksheet.write(row, col + 28, 'Reason', main_heading1)
				worksheet.write(row, col + 29, 'Total Distance', main_heading1)
				worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
				worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row, col + 36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
					worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
					worksheet.write(row, col + 39, 'Trip Status', main_heading1)
					worksheet.write(row, col + 40, 'User Code', main_heading1)
					worksheet.write(row, col + 41, 'User', main_heading1)
					worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row += 1

				worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
				worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
				worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row, col + 5, 'رقم اللوحة', main_heading1)
				worksheet.write(row, col + 6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row, col + 7, 'اسم المقطورة', main_heading1)
				worksheet.write(row, col + 8, 'كود السائق', main_heading1)
				worksheet.write(row, col + 9, 'إسم السائق', main_heading1)
				worksheet.write(row, col + 10, 'رقم الجوال', main_heading1)
				worksheet.write(row, col + 11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row, col + 13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row, col + 14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row, col + 15, 'فرع الوصول', main_heading1)
				worksheet.write(row, col + 16, 'خط السير', main_heading1)
				worksheet.write(row, col + 17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row, col + 18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row, col + 19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row, col + 20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row, col + 21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row, col + 22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row, col + 23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row, col + 24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row, col + 26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row, col + 27, 'مسافة أضافية', main_heading1)
				worksheet.write(row, col + 28, 'السبب', main_heading1)
				worksheet.write(row, col + 29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
				worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row, col + 36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row, col + 39, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 41, 'المستخدم', main_heading1)
					worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)
				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					display_expense_type_list = []
					for data in final_data:
						if data['display_expense_type']:
							if data['display_expense_type'] not in display_expense_type_list:
								display_expense_type_list.append(data['display_expense_type'])
					if display_expense_type_list:
						for fuel_expense_type in display_expense_type_list:
							if fuel_expense_type:
								worksheet.write(row, col, 'Fuel Expense Type', main_heading1)
								worksheet.write_string(row, col+1,fuel_expense_type, main_data)
								worksheet.write(row, col+2, 'نوع مصاريف الوقود', main_heading1)
								row += 1
								for rec in final_data:
									if rec['display_expense_type'] == fuel_expense_type:
										if rec['sticker']:
											worksheet.write_string(row, col, str(rec['sticker']), main_data)
										if rec['trip_name']:
											worksheet.write_string(row, col + 1, str(rec['trip_name']), main_data)
										if rec['created_on']:
											worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
										if rec['model_name']:
											worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
										if rec['vehicle_group_name']:
											worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']),
																   main_data)
										if rec['vehicle_license_plate_no']:
											worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']),
																   main_data)
										if rec['trailer_taq_no']:
											worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
										if rec['trailer_ar_name']:
											worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
										if rec['driver_code']:
											worksheet.write_string(row, col + 8, str(rec['driver_code']), main_data)
										if rec['driver_name']:
											worksheet.write_string(row, col + 9, str(rec['driver_name']), main_data)
										if rec['driver_phone']:
											worksheet.write_string(row, col + 10, str(rec['driver_phone']), main_data)
										if rec['trailer_cat']:
											worksheet.write_string(row, col + 11, str(rec['trailer_cat']), main_data)
										if rec['display_expense_mthod_id']:
											worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']),
																   main_data)
										if rec['vehicle_state']:
											worksheet.write_string(row, col + 13, str(rec['vehicle_state']), main_data)
										if rec['start_point']:
											worksheet.write_string(row, col + 14, str(rec['start_point']), main_data)
										if rec['end_point']:
											worksheet.write_string(row, col + 15, str(rec['end_point']), main_data)
										if rec['route_name']:
											worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
										if rec['start_time']:
											worksheet.write_string(row, col + 17, str(rec['start_time']), main_data)
										if rec['actual_start_datetime']:
											worksheet.write_string(row, col + 18, str(rec['actual_start_datetime']),
																   main_data)
										if rec['act_end_time']:
											worksheet.write_string(row, col + 19, str(rec['act_end_time']), main_data)
										if rec['est_trip_time']:
											worksheet.write_string(row, col + 20, str(rec['est_trip_time']), main_data)
										if rec['end_time']:
											worksheet.write_string(row, col + 21, str(rec['end_time']), main_data)
										if rec['actual_delay']:
											worksheet.write_string(row, col + 22, str(rec['actual_delay']), main_data)
										if rec['curr_arrival']:
											worksheet.write_string(row, col + 23, str(rec['curr_arrival']), main_data)
										if rec['curr_desti']:
											worksheet.write_string(row, col + 24, str(rec['curr_desti']), main_data)
										if rec['trip_load']:
											worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
										if rec['trip_dis']:
											worksheet.write_number(row, col + 26, rec['trip_dis'], main_data)
											trip_distance += rec['trip_dis']
										if rec['trip_extra_dis']:
											worksheet.write_number(row, col + 27, rec['trip_extra_dis'], main_data)
											extra_distance += rec['trip_extra_dis']
										if rec['reason']:
											worksheet.write_string(row, col + 28, str(rec['reason']), main_data)
										if rec['total_distance']:
											worksheet.write_number(row, col + 29, rec['total_distance'], main_data)
											total_distance += rec['total_distance']
										if rec['trip_total_fuel']:
											worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
											total_fuel_expense_amount += rec['trip_total_fuel']
										if rec['tot_reward_amt_frontend']:
											worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'],
																   main_data)
											total_reward_amt += rec['tot_reward_amt_frontend']
										if rec['add_reward_amt_frontend']:
											worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'],
																   main_data)
											additional_reward_amt += rec['add_reward_amt_frontend']
										if rec['total_fuel_expense_amount']:
											worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'],
																   main_data)
											total_fuel_expense_amt += rec['total_fuel_expense_amount']
										if rec['no_of_loading_vehicles_at_start_trip']:
											worksheet.write_number(row, col + 34,
																   rec['no_of_loading_vehicles_at_start_trip'],
																   main_data)
										if rec['no_of_loading_vehicles_on_transit']:
											worksheet.write_number(row, col + 35,
																   rec['no_of_loading_vehicles_on_transit'], main_data)
										if rec['car_num']:
											worksheet.write_number(row, col + 36, rec['car_num'], main_data)
											total_cars += rec['car_num']
										if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
											if rec['standard_revenue']:
												worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2),
																	   main_data)
												standard_revenue += rec['standard_revenue']
											if rec['actual_revenue']:
												worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2),
																	   main_data)
												actual_revenue += rec['actual_revenue']
											if rec['trip_state']:
												worksheet.write_string(row, col + 39, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 40, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 41, str(rec['create_user_name']),
																	   main_data)
										else:
											if rec['trip_state']:
												worksheet.write_string(row, col + 37, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 38, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 39, str(rec['create_user_name']),
																	   main_data)
										row += 1
								worksheet.write(row, col, 'Total', main_heading1)
								worksheet.write_number(row, col + 22, trip_distance, main_heading)
								worksheet.write_number(row, col + 23, extra_distance, main_heading)
								worksheet.write_number(row, col + 25, total_distance, main_heading)
								worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
								worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
								worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
								worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
								worksheet.write_number(row, col + 30, total_cars, main_heading)
								if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
									worksheet.write_number(row, col + 31, standard_revenue, main_heading)
									worksheet.write_number(row, col + 32, actual_revenue, main_heading)
								row += 1
			if wiz_obj.group_by == "start_branch":
				worksheet.merge_range('A1:AI1', "Trip Report Group By Driver Code", merge_format)
				worksheet.merge_range('A2:AI2', "تفرير الرحلات", merge_format)

				worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row, col + 1, 'Trip Seq No.', main_heading1)
				worksheet.write(row, col + 2, 'Created ON', main_heading1)
				worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
				worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row, col + 5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row, col + 6, 'Trailer Taq No', main_heading1)
				worksheet.write(row, col + 7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row, col + 8, 'Employee ID', main_heading1)
				worksheet.write(row, col + 9, 'Driver Name', main_heading1)
				worksheet.write(row, col + 10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row, col + 11, 'Vehicle Type', main_heading1)
				worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row, col + 13, 'Vehicle State', main_heading1)
				worksheet.write(row, col + 14, 'Start Branch', main_heading1)
				worksheet.write(row, col + 15, 'End Branch', main_heading1)
				worksheet.write(row, col + 16, 'Route Name', main_heading1)
				worksheet.write(row, col + 17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row, col + 18, 'Actual Start Date', main_heading1)
				worksheet.write(row, col + 19, 'Scheduled End Date', main_heading1)
				worksheet.write(row, col + 20, 'Est. Duration', main_heading1)
				worksheet.write(row, col + 21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row, col + 22, 'Actual Delay', main_heading1)
				worksheet.write(row, col + 23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row, col + 24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row, col + 25, 'Truck Load', main_heading1)
				worksheet.write(row, col + 26, 'Trip Distance', main_heading1)
				worksheet.write(row, col + 27, 'Extra Distance', main_heading1)
				worksheet.write(row, col + 28, 'Reason', main_heading1)
				worksheet.write(row, col + 29, 'Total Distance', main_heading1)
				worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
				worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row, col + 36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
					worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
					worksheet.write(row, col + 39, 'Trip Status', main_heading1)
					worksheet.write(row, col + 40, 'User Code', main_heading1)
					worksheet.write(row, col + 41, 'User', main_heading1)
					worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row += 1

				worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
				worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
				worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row, col + 5, 'رقم اللوحة', main_heading1)
				worksheet.write(row, col + 6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row, col + 7, 'اسم المقطورة', main_heading1)
				worksheet.write(row, col + 8, 'كود السائق', main_heading1)
				worksheet.write(row, col + 9, 'إسم السائق', main_heading1)
				worksheet.write(row, col + 10, 'رقم الجوال', main_heading1)
				worksheet.write(row, col + 11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row, col + 13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row, col + 14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row, col + 15, 'فرع الوصول', main_heading1)
				worksheet.write(row, col + 16, 'خط السير', main_heading1)
				worksheet.write(row, col + 17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row, col + 18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row, col + 19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row, col + 20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row, col + 21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row, col + 22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row, col + 23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row, col + 24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row, col + 26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row, col + 27, 'مسافة أضافية', main_heading1)
				worksheet.write(row, col + 28, 'السبب', main_heading1)
				worksheet.write(row, col + 29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
				worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row, col + 36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row, col + 39, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 41, 'المستخدم', main_heading1)
					worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)

				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					start_branch_list = []
					for data in final_data:
						if data['start_point']:
							if data['start_point'] not in start_branch_list:
								start_branch_list.append(data['start_point'])
					if start_branch_list:
						for start_branch in start_branch_list:
							if start_branch:
								worksheet.write(row, col, 'Start Branch', main_heading1)
								worksheet.write_string(row, col+1,start_branch, main_data)
								worksheet.write(row, col+2, 'فرع الإنطلاق', main_heading1)
								row += 1
								for rec in final_data:
									if rec['start_point'] == sticker_no:
										if rec['sticker']:
											worksheet.write_string(row, col, str(rec['sticker']), main_data)
										if rec['trip_name']:
											worksheet.write_string(row, col + 1, str(rec['trip_name']), main_data)
										if rec['created_on']:
											worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
										if rec['model_name']:
											worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
										if rec['vehicle_group_name']:
											worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']),
																   main_data)
										if rec['vehicle_license_plate_no']:
											worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']),
																   main_data)
										if rec['trailer_taq_no']:
											worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
										if rec['trailer_ar_name']:
											worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
										if rec['driver_code']:
											worksheet.write_string(row, col + 8, str(rec['driver_code']), main_data)
										if rec['driver_name']:
											worksheet.write_string(row, col + 9, str(rec['driver_name']), main_data)
										if rec['driver_phone']:
											worksheet.write_string(row, col + 10, str(rec['driver_phone']), main_data)
										if rec['trailer_cat']:
											worksheet.write_string(row, col + 11, str(rec['trailer_cat']), main_data)
										if rec['display_expense_mthod_id']:
											worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']),
																   main_data)
										if rec['vehicle_state']:
											worksheet.write_string(row, col + 13, str(rec['vehicle_state']), main_data)
										if rec['start_point']:
											worksheet.write_string(row, col + 14, str(rec['start_point']), main_data)
										if rec['end_point']:
											worksheet.write_string(row, col + 15, str(rec['end_point']), main_data)
										if rec['route_name']:
											worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
										if rec['start_time']:
											worksheet.write_string(row, col + 17, str(rec['start_time']), main_data)
										if rec['actual_start_datetime']:
											worksheet.write_string(row, col + 18, str(rec['actual_start_datetime']),
																   main_data)
										if rec['act_end_time']:
											worksheet.write_string(row, col + 19, str(rec['act_end_time']), main_data)
										if rec['est_trip_time']:
											worksheet.write_string(row, col + 20, str(rec['est_trip_time']), main_data)
										if rec['end_time']:
											worksheet.write_string(row, col + 21, str(rec['end_time']), main_data)
										if rec['actual_delay']:
											worksheet.write_string(row, col + 22, str(rec['actual_delay']), main_data)
										if rec['curr_arrival']:
											worksheet.write_string(row, col + 23, str(rec['curr_arrival']), main_data)
										if rec['curr_desti']:
											worksheet.write_string(row, col + 24, str(rec['curr_desti']), main_data)
										if rec['trip_load']:
											worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
										if rec['trip_dis']:
											worksheet.write_number(row, col + 26, rec['trip_dis'], main_data)
											trip_distance += rec['trip_dis']
										if rec['trip_extra_dis']:
											worksheet.write_number(row, col + 27, rec['trip_extra_dis'], main_data)
											extra_distance += rec['trip_extra_dis']
										if rec['reason']:
											worksheet.write_string(row, col + 28, str(rec['reason']), main_data)
										if rec['total_distance']:
											worksheet.write_number(row, col + 29, rec['total_distance'], main_data)
											total_distance += rec['total_distance']
										if rec['trip_total_fuel']:
											worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
											total_fuel_expense_amount += rec['trip_total_fuel']
										if rec['tot_reward_amt_frontend']:
											worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'],
																   main_data)
											total_reward_amt += rec['tot_reward_amt_frontend']
										if rec['add_reward_amt_frontend']:
											worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'],
																   main_data)
											additional_reward_amt += rec['add_reward_amt_frontend']
										if rec['total_fuel_expense_amount']:
											worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'],
																   main_data)
											total_fuel_expense_amt += rec['total_fuel_expense_amount']
										if rec['no_of_loading_vehicles_at_start_trip']:
											worksheet.write_number(row, col + 34,
																   rec['no_of_loading_vehicles_at_start_trip'],
																   main_data)
										if rec['no_of_loading_vehicles_on_transit']:
											worksheet.write_number(row, col + 35,
																   rec['no_of_loading_vehicles_on_transit'], main_data)
										if rec['car_num']:
											worksheet.write_number(row, col + 36, rec['car_num'], main_data)
											total_cars += rec['car_num']
										if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
											if rec['standard_revenue']:
												worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2),
																	   main_data)
												standard_revenue += rec['standard_revenue']
											if rec['actual_revenue']:
												worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2),
																	   main_data)
												actual_revenue += rec['actual_revenue']
											if rec['trip_state']:
												worksheet.write_string(row, col + 39, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 40, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 41, str(rec['create_user_name']),
																	   main_data)
										else:
											if rec['trip_state']:
												worksheet.write_string(row, col + 37, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 38, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 39, str(rec['create_user_name']),
																	   main_data)
										row += 1
								worksheet.write(row, col, 'Total', main_heading1)
								worksheet.write_number(row, col + 22, trip_distance, main_heading)
								worksheet.write_number(row, col + 23, extra_distance, main_heading)
								worksheet.write_number(row, col + 25, total_distance, main_heading)
								worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
								worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
								worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
								worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
								worksheet.write_number(row, col + 30, total_cars, main_heading)
								if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
									worksheet.write_number(row, col + 31, standard_revenue, main_heading)
									worksheet.write_number(row, col + 32, actual_revenue, main_heading)
								row += 1
			if wiz_obj.group_by == "end_branch":
				worksheet.merge_range('A1:AI1', "Trip Report Group By Driver Code", merge_format)
				worksheet.merge_range('A2:AI2', "تفرير الرحلات", merge_format)

				worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row, col + 1, 'Trip Seq No.', main_heading1)
				worksheet.write(row, col + 2, 'Created ON', main_heading1)
				worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
				worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row, col + 5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row, col + 6, 'Trailer Taq No', main_heading1)
				worksheet.write(row, col + 7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row, col + 8, 'Employee ID', main_heading1)
				worksheet.write(row, col + 9, 'Driver Name', main_heading1)
				worksheet.write(row, col + 10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row, col + 11, 'Vehicle Type', main_heading1)
				worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row, col + 13, 'Vehicle State', main_heading1)
				worksheet.write(row, col + 14, 'Start Branch', main_heading1)
				worksheet.write(row, col + 15, 'End Branch', main_heading1)
				worksheet.write(row, col + 16, 'Route Name', main_heading1)
				worksheet.write(row, col + 17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row, col + 18, 'Actual Start Date', main_heading1)
				worksheet.write(row, col + 19, 'Scheduled End Date', main_heading1)
				worksheet.write(row, col + 20, 'Est. Duration', main_heading1)
				worksheet.write(row, col + 21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row, col + 22, 'Actual Delay', main_heading1)
				worksheet.write(row, col + 23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row, col + 24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row, col + 25, 'Truck Load', main_heading1)
				worksheet.write(row, col + 26, 'Trip Distance', main_heading1)
				worksheet.write(row, col + 27, 'Extra Distance', main_heading1)
				worksheet.write(row, col + 28, 'Reason', main_heading1)
				worksheet.write(row, col + 29, 'Total Distance', main_heading1)
				worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
				worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row, col + 36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
					worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
					worksheet.write(row, col + 39, 'Trip Status', main_heading1)
					worksheet.write(row, col + 40, 'User Code', main_heading1)
					worksheet.write(row, col + 41, 'User', main_heading1)
					worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row += 1

				worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
				worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
				worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row, col + 5, 'رقم اللوحة', main_heading1)
				worksheet.write(row, col + 6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row, col + 7, 'اسم المقطورة', main_heading1)
				worksheet.write(row, col + 8, 'كود السائق', main_heading1)
				worksheet.write(row, col + 9, 'إسم السائق', main_heading1)
				worksheet.write(row, col + 10, 'رقم الجوال', main_heading1)
				worksheet.write(row, col + 11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row, col + 13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row, col + 14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row, col + 15, 'فرع الوصول', main_heading1)
				worksheet.write(row, col + 16, 'خط السير', main_heading1)
				worksheet.write(row, col + 17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row, col + 18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row, col + 19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row, col + 20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row, col + 21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row, col + 22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row, col + 23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row, col + 24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row, col + 26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row, col + 27, 'مسافة أضافية', main_heading1)
				worksheet.write(row, col + 28, 'السبب', main_heading1)
				worksheet.write(row, col + 29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
				worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row, col + 36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row, col + 39, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 41, 'المستخدم', main_heading1)
					worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)

				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					end_branch_list = []
					for data in final_data:
						if data['end_point']:
							if data['end_point'] not in sticker_no_list:
								sticker_no_list.append(data['end_point'])
					if end_branch_list:
						for end_branch in end_branch_list:
							if end_branch:
								worksheet.write(row, col, 'End Branch', main_heading1)
								worksheet.write_string(row, col+1,end_branch, main_data)
								worksheet.write(row, col+2, 'فرع الوصول', main_heading1)
								row += 1
								for rec in final_data:
									if rec['end_point'] == end_branch:
										if rec['sticker']:
											worksheet.write_string(row, col, str(rec['sticker']), main_data)
										if rec['trip_name']:
											worksheet.write_string(row, col + 1, str(rec['trip_name']), main_data)
										if rec['created_on']:
											worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
										if rec['model_name']:
											worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
										if rec['vehicle_group_name']:
											worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']),
																   main_data)
										if rec['vehicle_license_plate_no']:
											worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']),
																   main_data)
										if rec['trailer_taq_no']:
											worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
										if rec['trailer_ar_name']:
											worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
										if rec['driver_code']:
											worksheet.write_string(row, col + 8, str(rec['driver_code']), main_data)
										if rec['driver_name']:
											worksheet.write_string(row, col + 9, str(rec['driver_name']), main_data)
										if rec['driver_phone']:
											worksheet.write_string(row, col + 10, str(rec['driver_phone']), main_data)
										if rec['trailer_cat']:
											worksheet.write_string(row, col + 11, str(rec['trailer_cat']), main_data)
										if rec['display_expense_mthod_id']:
											worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']),
																   main_data)
										if rec['vehicle_state']:
											worksheet.write_string(row, col + 13, str(rec['vehicle_state']), main_data)
										if rec['start_point']:
											worksheet.write_string(row, col + 14, str(rec['start_point']), main_data)
										if rec['end_point']:
											worksheet.write_string(row, col + 15, str(rec['end_point']), main_data)
										if rec['route_name']:
											worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
										if rec['start_time']:
											worksheet.write_string(row, col + 17, str(rec['start_time']), main_data)
										if rec['actual_start_datetime']:
											worksheet.write_string(row, col + 18, str(rec['actual_start_datetime']),
																   main_data)
										if rec['act_end_time']:
											worksheet.write_string(row, col + 19, str(rec['act_end_time']), main_data)
										if rec['est_trip_time']:
											worksheet.write_string(row, col + 20, str(rec['est_trip_time']), main_data)
										if rec['end_time']:
											worksheet.write_string(row, col + 21, str(rec['end_time']), main_data)
										if rec['actual_delay']:
											worksheet.write_string(row, col + 22, str(rec['actual_delay']), main_data)
										if rec['curr_arrival']:
											worksheet.write_string(row, col + 23, str(rec['curr_arrival']), main_data)
										if rec['curr_desti']:
											worksheet.write_string(row, col + 24, str(rec['curr_desti']), main_data)
										if rec['trip_load']:
											worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
										if rec['trip_dis']:
											worksheet.write_number(row, col + 26, rec['trip_dis'], main_data)
											trip_distance += rec['trip_dis']
										if rec['trip_extra_dis']:
											worksheet.write_number(row, col + 27, rec['trip_extra_dis'], main_data)
											extra_distance += rec['trip_extra_dis']
										if rec['reason']:
											worksheet.write_string(row, col + 28, str(rec['reason']), main_data)
										if rec['total_distance']:
											worksheet.write_number(row, col + 29, rec['total_distance'], main_data)
											total_distance += rec['total_distance']
										if rec['trip_total_fuel']:
											worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
											total_fuel_expense_amount += rec['trip_total_fuel']
										if rec['tot_reward_amt_frontend']:
											worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'],
																   main_data)
											total_reward_amt += rec['tot_reward_amt_frontend']
										if rec['add_reward_amt_frontend']:
											worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'],
																   main_data)
											additional_reward_amt += rec['add_reward_amt_frontend']
										if rec['total_fuel_expense_amount']:
											worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'],
																   main_data)
											total_fuel_expense_amt += rec['total_fuel_expense_amount']
										if rec['no_of_loading_vehicles_at_start_trip']:
											worksheet.write_number(row, col + 34,
																   rec['no_of_loading_vehicles_at_start_trip'],
																   main_data)
										if rec['no_of_loading_vehicles_on_transit']:
											worksheet.write_number(row, col + 35,
																   rec['no_of_loading_vehicles_on_transit'], main_data)
										if rec['car_num']:
											worksheet.write_number(row, col + 36, rec['car_num'], main_data)
											total_cars += rec['car_num']
										if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
											if rec['standard_revenue']:
												worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2),
																	   main_data)
												standard_revenue += rec['standard_revenue']
											if rec['actual_revenue']:
												worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2),
																	   main_data)
												actual_revenue += rec['actual_revenue']
											if rec['trip_state']:
												worksheet.write_string(row, col + 39, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 40, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 41, str(rec['create_user_name']),
																	   main_data)
										else:
											if rec['trip_state']:
												worksheet.write_string(row, col + 37, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 38, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 39, str(rec['create_user_name']),
																	   main_data)
										row += 1
								worksheet.write(row, col, 'Total', main_heading1)
								worksheet.write_number(row, col + 22, trip_distance, main_heading)
								worksheet.write_number(row, col + 23, extra_distance, main_heading)
								worksheet.write_number(row, col + 25, total_distance, main_heading)
								worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
								worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
								worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
								worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
								worksheet.write_number(row, col + 30, total_cars, main_heading)
								if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
									worksheet.write_number(row, col + 31, standard_revenue, main_heading)
									worksheet.write_number(row, col + 32, actual_revenue, main_heading)
								row += 1
			if wiz_obj.group_by == "schedule_start_date":
				worksheet.merge_range('A1:AI1', "Trip Report Group By Driver Code", merge_format)
				worksheet.merge_range('A2:AI2', "تفرير الرحلات", merge_format)

				worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row, col + 1, 'Trip Seq No.', main_heading1)
				worksheet.write(row, col + 2, 'Created ON', main_heading1)
				worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
				worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row, col + 5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row, col + 6, 'Trailer Taq No', main_heading1)
				worksheet.write(row, col + 7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row, col + 8, 'Employee ID', main_heading1)
				worksheet.write(row, col + 9, 'Driver Name', main_heading1)
				worksheet.write(row, col + 10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row, col + 11, 'Vehicle Type', main_heading1)
				worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row, col + 13, 'Vehicle State', main_heading1)
				worksheet.write(row, col + 14, 'Start Branch', main_heading1)
				worksheet.write(row, col + 15, 'End Branch', main_heading1)
				worksheet.write(row, col + 16, 'Route Name', main_heading1)
				worksheet.write(row, col + 17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row, col + 18, 'Actual Start Date', main_heading1)
				worksheet.write(row, col + 19, 'Scheduled End Date', main_heading1)
				worksheet.write(row, col + 20, 'Est. Duration', main_heading1)
				worksheet.write(row, col + 21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row, col + 22, 'Actual Delay', main_heading1)
				worksheet.write(row, col + 23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row, col + 24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row, col + 25, 'Truck Load', main_heading1)
				worksheet.write(row, col + 26, 'Trip Distance', main_heading1)
				worksheet.write(row, col + 27, 'Extra Distance', main_heading1)
				worksheet.write(row, col + 28, 'Reason', main_heading1)
				worksheet.write(row, col + 29, 'Total Distance', main_heading1)
				worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
				worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row, col + 36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
					worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
					worksheet.write(row, col + 39, 'Trip Status', main_heading1)
					worksheet.write(row, col + 40, 'User Code', main_heading1)
					worksheet.write(row, col + 41, 'User', main_heading1)
					worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row += 1

				worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
				worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
				worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row, col + 5, 'رقم اللوحة', main_heading1)
				worksheet.write(row, col + 6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row, col + 7, 'اسم المقطورة', main_heading1)
				worksheet.write(row, col + 8, 'كود السائق', main_heading1)
				worksheet.write(row, col + 9, 'إسم السائق', main_heading1)
				worksheet.write(row, col + 10, 'رقم الجوال', main_heading1)
				worksheet.write(row, col + 11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row, col + 13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row, col + 14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row, col + 15, 'فرع الوصول', main_heading1)
				worksheet.write(row, col + 16, 'خط السير', main_heading1)
				worksheet.write(row, col + 17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row, col + 18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row, col + 19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row, col + 20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row, col + 21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row, col + 22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row, col + 23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row, col + 24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row, col + 26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row, col + 27, 'مسافة أضافية', main_heading1)
				worksheet.write(row, col + 28, 'السبب', main_heading1)
				worksheet.write(row, col + 29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
				worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row, col + 36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row, col + 39, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 41, 'المستخدم', main_heading1)
					worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)

				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					schedule_start_date_list = []
					for data in final_data:
						if data['start_time']:
							if data['start_time'] not in sticker_no_list:
								schedule_start_date_list.append(data['start_time'])
					if schedule_start_date_list:
						for schedule_start_date in schedule_start_date_list:
							if schedule_start_date:
								worksheet.write(row, col, 'Schedule Start Date', main_heading1)
								worksheet.write_string(row, col+1,schedule_start_date, main_data)
								worksheet.write(row, col+2, 'تاريخ بدء الجدولة', main_heading1)
								row += 1
								for rec in schedule_start_date:
									if rec['start_time'] == sticker_no:
										if rec['sticker']:
											worksheet.write_string(row, col, str(rec['sticker']), main_data)
										if rec['trip_name']:
											worksheet.write_string(row, col + 1, str(rec['trip_name']), main_data)
										if rec['created_on']:
											worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
										if rec['model_name']:
											worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
										if rec['vehicle_group_name']:
											worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']),
																   main_data)
										if rec['vehicle_license_plate_no']:
											worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']),
																   main_data)
										if rec['trailer_taq_no']:
											worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
										if rec['trailer_ar_name']:
											worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
										if rec['driver_code']:
											worksheet.write_string(row, col + 8, str(rec['driver_code']), main_data)
										if rec['driver_name']:
											worksheet.write_string(row, col + 9, str(rec['driver_name']), main_data)
										if rec['driver_phone']:
											worksheet.write_string(row, col + 10, str(rec['driver_phone']), main_data)
										if rec['trailer_cat']:
											worksheet.write_string(row, col + 11, str(rec['trailer_cat']), main_data)
										if rec['display_expense_mthod_id']:
											worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']),
																   main_data)
										if rec['vehicle_state']:
											worksheet.write_string(row, col + 13, str(rec['vehicle_state']), main_data)
										if rec['start_point']:
											worksheet.write_string(row, col + 14, str(rec['start_point']), main_data)
										if rec['end_point']:
											worksheet.write_string(row, col + 15, str(rec['end_point']), main_data)
										if rec['route_name']:
											worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
										if rec['start_time']:
											worksheet.write_string(row, col + 17, str(rec['start_time']), main_data)
										if rec['actual_start_datetime']:
											worksheet.write_string(row, col + 18, str(rec['actual_start_datetime']),
																   main_data)
										if rec['act_end_time']:
											worksheet.write_string(row, col + 19, str(rec['act_end_time']), main_data)
										if rec['est_trip_time']:
											worksheet.write_string(row, col + 20, str(rec['est_trip_time']), main_data)
										if rec['end_time']:
											worksheet.write_string(row, col + 21, str(rec['end_time']), main_data)
										if rec['actual_delay']:
											worksheet.write_string(row, col + 22, str(rec['actual_delay']), main_data)
										if rec['curr_arrival']:
											worksheet.write_string(row, col + 23, str(rec['curr_arrival']), main_data)
										if rec['curr_desti']:
											worksheet.write_string(row, col + 24, str(rec['curr_desti']), main_data)
										if rec['trip_load']:
											worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
										if rec['trip_dis']:
											worksheet.write_number(row, col + 26, rec['trip_dis'], main_data)
											trip_distance += rec['trip_dis']
										if rec['trip_extra_dis']:
											worksheet.write_number(row, col + 27, rec['trip_extra_dis'], main_data)
											extra_distance += rec['trip_extra_dis']
										if rec['reason']:
											worksheet.write_string(row, col + 28, str(rec['reason']), main_data)
										if rec['total_distance']:
											worksheet.write_number(row, col + 29, rec['total_distance'], main_data)
											total_distance += rec['total_distance']
										if rec['trip_total_fuel']:
											worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
											total_fuel_expense_amount += rec['trip_total_fuel']
										if rec['tot_reward_amt_frontend']:
											worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'],
																   main_data)
											total_reward_amt += rec['tot_reward_amt_frontend']
										if rec['add_reward_amt_frontend']:
											worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'],
																   main_data)
											additional_reward_amt += rec['add_reward_amt_frontend']
										if rec['total_fuel_expense_amount']:
											worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'],
																   main_data)
											total_fuel_expense_amt += rec['total_fuel_expense_amount']
										if rec['no_of_loading_vehicles_at_start_trip']:
											worksheet.write_number(row, col + 34,
																   rec['no_of_loading_vehicles_at_start_trip'],
																   main_data)
										if rec['no_of_loading_vehicles_on_transit']:
											worksheet.write_number(row, col + 35,
																   rec['no_of_loading_vehicles_on_transit'], main_data)
										if rec['car_num']:
											worksheet.write_number(row, col + 36, rec['car_num'], main_data)
											total_cars += rec['car_num']
										if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
											if rec['standard_revenue']:
												worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2),
																	   main_data)
												standard_revenue += rec['standard_revenue']
											if rec['actual_revenue']:
												worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2),
																	   main_data)
												actual_revenue += rec['actual_revenue']
											if rec['trip_state']:
												worksheet.write_string(row, col + 39, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 40, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 41, str(rec['create_user_name']),
																	   main_data)
										else:
											if rec['trip_state']:
												worksheet.write_string(row, col + 37, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 38, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 39, str(rec['create_user_name']),
																	   main_data)
										row += 1
								worksheet.write(row, col, 'Total', main_heading1)
								worksheet.write_number(row, col + 22, trip_distance, main_heading)
								worksheet.write_number(row, col + 23, extra_distance, main_heading)
								worksheet.write_number(row, col + 25, total_distance, main_heading)
								worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
								worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
								worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
								worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
								worksheet.write_number(row, col + 30, total_cars, main_heading)
								if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
									worksheet.write_number(row, col + 31, standard_revenue, main_heading)
									worksheet.write_number(row, col + 32, actual_revenue, main_heading)
								row += 1
			if wiz_obj.group_by == "schedule_end_date":
				worksheet.merge_range('A1:AI1', "Trip Report Group By Driver Code", merge_format)
				worksheet.merge_range('A2:AI2', "تفرير الرحلات", merge_format)

				worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row, col + 1, 'Trip Seq No.', main_heading1)
				worksheet.write(row, col + 2, 'Created ON', main_heading1)
				worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
				worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row, col + 5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row, col + 6, 'Trailer Taq No', main_heading1)
				worksheet.write(row, col + 7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row, col + 8, 'Employee ID', main_heading1)
				worksheet.write(row, col + 9, 'Driver Name', main_heading1)
				worksheet.write(row, col + 10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row, col + 11, 'Vehicle Type', main_heading1)
				worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row, col + 13, 'Vehicle State', main_heading1)
				worksheet.write(row, col + 14, 'Start Branch', main_heading1)
				worksheet.write(row, col + 15, 'End Branch', main_heading1)
				worksheet.write(row, col + 16, 'Route Name', main_heading1)
				worksheet.write(row, col + 17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row, col + 18, 'Actual Start Date', main_heading1)
				worksheet.write(row, col + 19, 'Scheduled End Date', main_heading1)
				worksheet.write(row, col + 20, 'Est. Duration', main_heading1)
				worksheet.write(row, col + 21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row, col + 22, 'Actual Delay', main_heading1)
				worksheet.write(row, col + 23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row, col + 24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row, col + 25, 'Truck Load', main_heading1)
				worksheet.write(row, col + 26, 'Trip Distance', main_heading1)
				worksheet.write(row, col + 27, 'Extra Distance', main_heading1)
				worksheet.write(row, col + 28, 'Reason', main_heading1)
				worksheet.write(row, col + 29, 'Total Distance', main_heading1)
				worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
				worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row, col + 36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
					worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
					worksheet.write(row, col + 39, 'Trip Status', main_heading1)
					worksheet.write(row, col + 40, 'User Code', main_heading1)
					worksheet.write(row, col + 41, 'User', main_heading1)
					worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row += 1

				worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
				worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
				worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row, col + 5, 'رقم اللوحة', main_heading1)
				worksheet.write(row, col + 6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row, col + 7, 'اسم المقطورة', main_heading1)
				worksheet.write(row, col + 8, 'كود السائق', main_heading1)
				worksheet.write(row, col + 9, 'إسم السائق', main_heading1)
				worksheet.write(row, col + 10, 'رقم الجوال', main_heading1)
				worksheet.write(row, col + 11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row, col + 13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row, col + 14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row, col + 15, 'فرع الوصول', main_heading1)
				worksheet.write(row, col + 16, 'خط السير', main_heading1)
				worksheet.write(row, col + 17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row, col + 18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row, col + 19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row, col + 20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row, col + 21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row, col + 22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row, col + 23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row, col + 24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row, col + 26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row, col + 27, 'مسافة أضافية', main_heading1)
				worksheet.write(row, col + 28, 'السبب', main_heading1)
				worksheet.write(row, col + 29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
				worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row, col + 36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row, col + 39, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 41, 'المستخدم', main_heading1)
					worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)

				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					schedule_end_date_list = []
					for data in final_data:
						if data['act_end_time']:
							if data['act_end_time'] not in schedule_end_date_list:
								sticker_no_list.append(data['act_end_time'])
					if schedule_end_date_list:
						for schedule_end_date in schedule_end_date_list:
							if schedule_end_date:
								worksheet.write(row, col, 'Schedule End Date', main_heading1)
								worksheet.write_string(row, col+1,schedule_end_date, main_data)
								worksheet.write(row, col+2, 'تاريخ الوصول المتوقع', main_heading1)
								row += 1
								for rec in final_data:
									if rec['act_end_time'] == schedule_end_date:
										if rec['sticker']:
											worksheet.write_string(row, col, str(rec['sticker']), main_data)
										if rec['trip_name']:
											worksheet.write_string(row, col + 1, str(rec['trip_name']), main_data)
										if rec['created_on']:
											worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
										if rec['model_name']:
											worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
										if rec['vehicle_group_name']:
											worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']),
																   main_data)
										if rec['vehicle_license_plate_no']:
											worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']),
																   main_data)
										if rec['trailer_taq_no']:
											worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
										if rec['trailer_ar_name']:
											worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
										if rec['driver_code']:
											worksheet.write_string(row, col + 8, str(rec['driver_code']), main_data)
										if rec['driver_name']:
											worksheet.write_string(row, col + 9, str(rec['driver_name']), main_data)
										if rec['driver_phone']:
											worksheet.write_string(row, col + 10, str(rec['driver_phone']), main_data)
										if rec['trailer_cat']:
											worksheet.write_string(row, col + 11, str(rec['trailer_cat']), main_data)
										if rec['display_expense_mthod_id']:
											worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']),
																   main_data)
										if rec['vehicle_state']:
											worksheet.write_string(row, col + 13, str(rec['vehicle_state']), main_data)
										if rec['start_point']:
											worksheet.write_string(row, col + 14, str(rec['start_point']), main_data)
										if rec['end_point']:
											worksheet.write_string(row, col + 15, str(rec['end_point']), main_data)
										if rec['route_name']:
											worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
										if rec['start_time']:
											worksheet.write_string(row, col + 17, str(rec['start_time']), main_data)
										if rec['actual_start_datetime']:
											worksheet.write_string(row, col + 18, str(rec['actual_start_datetime']),
																   main_data)
										if rec['act_end_time']:
											worksheet.write_string(row, col + 19, str(rec['act_end_time']), main_data)
										if rec['est_trip_time']:
											worksheet.write_string(row, col + 20, str(rec['est_trip_time']), main_data)
										if rec['end_time']:
											worksheet.write_string(row, col + 21, str(rec['end_time']), main_data)
										if rec['actual_delay']:
											worksheet.write_string(row, col + 22, str(rec['actual_delay']), main_data)
										if rec['curr_arrival']:
											worksheet.write_string(row, col + 23, str(rec['curr_arrival']), main_data)
										if rec['curr_desti']:
											worksheet.write_string(row, col + 24, str(rec['curr_desti']), main_data)
										if rec['trip_load']:
											worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
										if rec['trip_dis']:
											worksheet.write_number(row, col + 26, rec['trip_dis'], main_data)
											trip_distance += rec['trip_dis']
										if rec['trip_extra_dis']:
											worksheet.write_number(row, col + 27, rec['trip_extra_dis'], main_data)
											extra_distance += rec['trip_extra_dis']
										if rec['reason']:
											worksheet.write_string(row, col + 28, str(rec['reason']), main_data)
										if rec['total_distance']:
											worksheet.write_number(row, col + 29, rec['total_distance'], main_data)
											total_distance += rec['total_distance']
										if rec['trip_total_fuel']:
											worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
											total_fuel_expense_amount += rec['trip_total_fuel']
										if rec['tot_reward_amt_frontend']:
											worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'],
																   main_data)
											total_reward_amt += rec['tot_reward_amt_frontend']
										if rec['add_reward_amt_frontend']:
											worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'],
																   main_data)
											additional_reward_amt += rec['add_reward_amt_frontend']
										if rec['total_fuel_expense_amount']:
											worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'],
																   main_data)
											total_fuel_expense_amt += rec['total_fuel_expense_amount']
										if rec['no_of_loading_vehicles_at_start_trip']:
											worksheet.write_number(row, col + 34,
																   rec['no_of_loading_vehicles_at_start_trip'],
																   main_data)
										if rec['no_of_loading_vehicles_on_transit']:
											worksheet.write_number(row, col + 35,
																   rec['no_of_loading_vehicles_on_transit'], main_data)
										if rec['car_num']:
											worksheet.write_number(row, col + 36, rec['car_num'], main_data)
											total_cars += rec['car_num']
										if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
											if rec['standard_revenue']:
												worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2),
																	   main_data)
												standard_revenue += rec['standard_revenue']
											if rec['actual_revenue']:
												worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2),
																	   main_data)
												actual_revenue += rec['actual_revenue']
											if rec['trip_state']:
												worksheet.write_string(row, col + 39, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 40, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 41, str(rec['create_user_name']),
																	   main_data)
										else:
											if rec['trip_state']:
												worksheet.write_string(row, col + 37, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 38, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 39, str(rec['create_user_name']),
																	   main_data)
										row += 1
								worksheet.write(row, col, 'Total', main_heading1)
								worksheet.write_number(row, col + 22, trip_distance, main_heading)
								worksheet.write_number(row, col + 23, extra_distance, main_heading)
								worksheet.write_number(row, col + 25, total_distance, main_heading)
								worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
								worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
								worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
								worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
								worksheet.write_number(row, col + 30, total_cars, main_heading)
								if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
									worksheet.write_number(row, col + 31, standard_revenue, main_heading)
									worksheet.write_number(row, col + 32, actual_revenue, main_heading)
								row += 1
			if wiz_obj.group_by == "truck_load":
				worksheet.merge_range('A1:AI1', "Trip Report Group By Driver Code", merge_format)
				worksheet.merge_range('A2:AI2', "تفرير الرحلات", merge_format)

				worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row, col + 1, 'Trip Seq No.', main_heading1)
				worksheet.write(row, col + 2, 'Created ON', main_heading1)
				worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
				worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row, col + 5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row, col + 6, 'Trailer Taq No', main_heading1)
				worksheet.write(row, col + 7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row, col + 8, 'Employee ID', main_heading1)
				worksheet.write(row, col + 9, 'Driver Name', main_heading1)
				worksheet.write(row, col + 10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row, col + 11, 'Vehicle Type', main_heading1)
				worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row, col + 13, 'Vehicle State', main_heading1)
				worksheet.write(row, col + 14, 'Start Branch', main_heading1)
				worksheet.write(row, col + 15, 'End Branch', main_heading1)
				worksheet.write(row, col + 16, 'Route Name', main_heading1)
				worksheet.write(row, col + 17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row, col + 18, 'Actual Start Date', main_heading1)
				worksheet.write(row, col + 19, 'Scheduled End Date', main_heading1)
				worksheet.write(row, col + 20, 'Est. Duration', main_heading1)
				worksheet.write(row, col + 21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row, col + 22, 'Actual Delay', main_heading1)
				worksheet.write(row, col + 23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row, col + 24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row, col + 25, 'Truck Load', main_heading1)
				worksheet.write(row, col + 26, 'Trip Distance', main_heading1)
				worksheet.write(row, col + 27, 'Extra Distance', main_heading1)
				worksheet.write(row, col + 28, 'Reason', main_heading1)
				worksheet.write(row, col + 29, 'Total Distance', main_heading1)
				worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
				worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row, col + 36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
					worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
					worksheet.write(row, col + 39, 'Trip Status', main_heading1)
					worksheet.write(row, col + 40, 'User Code', main_heading1)
					worksheet.write(row, col + 41, 'User', main_heading1)
					worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row += 1

				worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
				worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
				worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row, col + 5, 'رقم اللوحة', main_heading1)
				worksheet.write(row, col + 6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row, col + 7, 'اسم المقطورة', main_heading1)
				worksheet.write(row, col + 8, 'كود السائق', main_heading1)
				worksheet.write(row, col + 9, 'إسم السائق', main_heading1)
				worksheet.write(row, col + 10, 'رقم الجوال', main_heading1)
				worksheet.write(row, col + 11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row, col + 13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row, col + 14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row, col + 15, 'فرع الوصول', main_heading1)
				worksheet.write(row, col + 16, 'خط السير', main_heading1)
				worksheet.write(row, col + 17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row, col + 18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row, col + 19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row, col + 20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row, col + 21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row, col + 22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row, col + 23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row, col + 24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row, col + 26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row, col + 27, 'مسافة أضافية', main_heading1)
				worksheet.write(row, col + 28, 'السبب', main_heading1)
				worksheet.write(row, col + 29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
				worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row, col + 36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row, col + 39, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 41, 'المستخدم', main_heading1)
					worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)

				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					truck_load_list = []
					for data in final_data:
						if data['trip_load']:
							if data['trip_load'] not in truck_load_list:
								truck_load_list.append(data['trip_load'])
					if truck_load_list:
						for truck_load in truck_load_list:
							if truck_load:
								worksheet.write(row, col, 'Truck Load', main_heading1)
								worksheet.write_string(row, col+1,truck_load, main_data)
								worksheet.write(row, col+2, 'حمولة الشاحنة', main_heading1)
								row += 1
								for rec in final_data:
									if rec['trip_load'] == truck_load:
										if rec['sticker']:
											worksheet.write_string(row, col, str(rec['sticker']), main_data)
										if rec['trip_name']:
											worksheet.write_string(row, col + 1, str(rec['trip_name']), main_data)
										if rec['created_on']:
											worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
										if rec['model_name']:
											worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
										if rec['vehicle_group_name']:
											worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']),
																   main_data)
										if rec['vehicle_license_plate_no']:
											worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']),
																   main_data)
										if rec['trailer_taq_no']:
											worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
										if rec['trailer_ar_name']:
											worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
										if rec['driver_code']:
											worksheet.write_string(row, col + 8, str(rec['driver_code']), main_data)
										if rec['driver_name']:
											worksheet.write_string(row, col + 9, str(rec['driver_name']), main_data)
										if rec['driver_phone']:
											worksheet.write_string(row, col + 10, str(rec['driver_phone']), main_data)
										if rec['trailer_cat']:
											worksheet.write_string(row, col + 11, str(rec['trailer_cat']), main_data)
										if rec['display_expense_mthod_id']:
											worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']),
																   main_data)
										if rec['vehicle_state']:
											worksheet.write_string(row, col + 13, str(rec['vehicle_state']), main_data)
										if rec['start_point']:
											worksheet.write_string(row, col + 14, str(rec['start_point']), main_data)
										if rec['end_point']:
											worksheet.write_string(row, col + 15, str(rec['end_point']), main_data)
										if rec['route_name']:
											worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
										if rec['start_time']:
											worksheet.write_string(row, col + 17, str(rec['start_time']), main_data)
										if rec['actual_start_datetime']:
											worksheet.write_string(row, col + 18, str(rec['actual_start_datetime']),
																   main_data)
										if rec['act_end_time']:
											worksheet.write_string(row, col + 19, str(rec['act_end_time']), main_data)
										if rec['est_trip_time']:
											worksheet.write_string(row, col + 20, str(rec['est_trip_time']), main_data)
										if rec['end_time']:
											worksheet.write_string(row, col + 21, str(rec['end_time']), main_data)
										if rec['actual_delay']:
											worksheet.write_string(row, col + 22, str(rec['actual_delay']), main_data)
										if rec['curr_arrival']:
											worksheet.write_string(row, col + 23, str(rec['curr_arrival']), main_data)
										if rec['curr_desti']:
											worksheet.write_string(row, col + 24, str(rec['curr_desti']), main_data)
										if rec['trip_load']:
											worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
										if rec['trip_dis']:
											worksheet.write_number(row, col + 26, rec['trip_dis'], main_data)
											trip_distance += rec['trip_dis']
										if rec['trip_extra_dis']:
											worksheet.write_number(row, col + 27, rec['trip_extra_dis'], main_data)
											extra_distance += rec['trip_extra_dis']
										if rec['reason']:
											worksheet.write_string(row, col + 28, str(rec['reason']), main_data)
										if rec['total_distance']:
											worksheet.write_number(row, col + 29, rec['total_distance'], main_data)
											total_distance += rec['total_distance']
										if rec['trip_total_fuel']:
											worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
											total_fuel_expense_amount += rec['trip_total_fuel']
										if rec['tot_reward_amt_frontend']:
											worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'],
																   main_data)
											total_reward_amt += rec['tot_reward_amt_frontend']
										if rec['add_reward_amt_frontend']:
											worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'],
																   main_data)
											additional_reward_amt += rec['add_reward_amt_frontend']
										if rec['total_fuel_expense_amount']:
											worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'],
																   main_data)
											total_fuel_expense_amt += rec['total_fuel_expense_amount']
										if rec['no_of_loading_vehicles_at_start_trip']:
											worksheet.write_number(row, col + 34,
																   rec['no_of_loading_vehicles_at_start_trip'],
																   main_data)
										if rec['no_of_loading_vehicles_on_transit']:
											worksheet.write_number(row, col + 35,
																   rec['no_of_loading_vehicles_on_transit'], main_data)
										if rec['car_num']:
											worksheet.write_number(row, col + 36, rec['car_num'], main_data)
											total_cars += rec['car_num']
										if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
											if rec['standard_revenue']:
												worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2),
																	   main_data)
												standard_revenue += rec['standard_revenue']
											if rec['actual_revenue']:
												worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2),
																	   main_data)
												actual_revenue += rec['actual_revenue']
											if rec['trip_state']:
												worksheet.write_string(row, col + 39, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 40, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 41, str(rec['create_user_name']),
																	   main_data)
										else:
											if rec['trip_state']:
												worksheet.write_string(row, col + 37, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 38, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 39, str(rec['create_user_name']),
																	   main_data)
										row += 1
								worksheet.write(row, col, 'Total', main_heading1)
								worksheet.write_number(row, col + 22, trip_distance, main_heading)
								worksheet.write_number(row, col + 23, extra_distance, main_heading)
								worksheet.write_number(row, col + 25, total_distance, main_heading)
								worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
								worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
								worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
								worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
								worksheet.write_number(row, col + 30, total_cars, main_heading)
								if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
									worksheet.write_number(row, col + 31, standard_revenue, main_heading)
									worksheet.write_number(row, col + 32, actual_revenue, main_heading)
								row += 1
			if wiz_obj.group_by == "trip_type":
				worksheet.merge_range('A1:AI1', "Trip Report Group By Driver Code", merge_format)
				worksheet.merge_range('A2:AI2', "تفرير الرحلات", merge_format)

				worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row, col + 1, 'Trip Seq No.', main_heading1)
				worksheet.write(row, col + 2, 'Created ON', main_heading1)
				worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
				worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row, col + 5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row, col + 6, 'Trailer Taq No', main_heading1)
				worksheet.write(row, col + 7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row, col + 8, 'Employee ID', main_heading1)
				worksheet.write(row, col + 9, 'Driver Name', main_heading1)
				worksheet.write(row, col + 10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row, col + 11, 'Vehicle Type', main_heading1)
				worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row, col + 13, 'Vehicle State', main_heading1)
				worksheet.write(row, col + 14, 'Start Branch', main_heading1)
				worksheet.write(row, col + 15, 'End Branch', main_heading1)
				worksheet.write(row, col + 16, 'Route Name', main_heading1)
				worksheet.write(row, col + 17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row, col + 18, 'Actual Start Date', main_heading1)
				worksheet.write(row, col + 19, 'Scheduled End Date', main_heading1)
				worksheet.write(row, col + 20, 'Est. Duration', main_heading1)
				worksheet.write(row, col + 21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row, col + 22, 'Actual Delay', main_heading1)
				worksheet.write(row, col + 23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row, col + 24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row, col + 25, 'Truck Load', main_heading1)
				worksheet.write(row, col + 26, 'Trip Distance', main_heading1)
				worksheet.write(row, col + 27, 'Extra Distance', main_heading1)
				worksheet.write(row, col + 28, 'Reason', main_heading1)
				worksheet.write(row, col + 29, 'Total Distance', main_heading1)
				worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
				worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row, col + 36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
					worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
					worksheet.write(row, col + 39, 'Trip Status', main_heading1)
					worksheet.write(row, col + 40, 'User Code', main_heading1)
					worksheet.write(row, col + 41, 'User', main_heading1)
					worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row += 1

				worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
				worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
				worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row, col + 5, 'رقم اللوحة', main_heading1)
				worksheet.write(row, col + 6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row, col + 7, 'اسم المقطورة', main_heading1)
				worksheet.write(row, col + 8, 'كود السائق', main_heading1)
				worksheet.write(row, col + 9, 'إسم السائق', main_heading1)
				worksheet.write(row, col + 10, 'رقم الجوال', main_heading1)
				worksheet.write(row, col + 11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row, col + 13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row, col + 14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row, col + 15, 'فرع الوصول', main_heading1)
				worksheet.write(row, col + 16, 'خط السير', main_heading1)
				worksheet.write(row, col + 17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row, col + 18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row, col + 19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row, col + 20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row, col + 21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row, col + 22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row, col + 23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row, col + 24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row, col + 26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row, col + 27, 'مسافة أضافية', main_heading1)
				worksheet.write(row, col + 28, 'السبب', main_heading1)
				worksheet.write(row, col + 29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
				worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row, col + 36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row, col + 39, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 41, 'المستخدم', main_heading1)
					worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)

				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					trip_type_list = []
					for data in final_data:
						if data['trip_case']:
							if data['trip_case'] not in trip_type_list:
								trip_type_list.append(data['trip_case'])
					if trip_type_list:
						for trip_type in trip_type_list:
							if trip_type:
								worksheet.write(row, col, 'Trip Type', main_heading1)
								worksheet.write_string(row, col+1,trip_type, main_data)
								worksheet.write(row, col+2, 'نوع الرحلة', main_heading1)
								row += 1
								for rec in final_data:
									if rec['trip_case'] == trip_type:
										if rec['sticker']:
											worksheet.write_string(row, col, str(rec['sticker']), main_data)
										if rec['trip_name']:
											worksheet.write_string(row, col + 1, str(rec['trip_name']), main_data)
										if rec['created_on']:
											worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
										if rec['model_name']:
											worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
										if rec['vehicle_group_name']:
											worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']),
																   main_data)
										if rec['vehicle_license_plate_no']:
											worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']),
																   main_data)
										if rec['trailer_taq_no']:
											worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
										if rec['trailer_ar_name']:
											worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
										if rec['driver_code']:
											worksheet.write_string(row, col + 8, str(rec['driver_code']), main_data)
										if rec['driver_name']:
											worksheet.write_string(row, col + 9, str(rec['driver_name']), main_data)
										if rec['driver_phone']:
											worksheet.write_string(row, col + 10, str(rec['driver_phone']), main_data)
										if rec['trailer_cat']:
											worksheet.write_string(row, col + 11, str(rec['trailer_cat']), main_data)
										if rec['display_expense_mthod_id']:
											worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']),
																   main_data)
										if rec['vehicle_state']:
											worksheet.write_string(row, col + 13, str(rec['vehicle_state']), main_data)
										if rec['start_point']:
											worksheet.write_string(row, col + 14, str(rec['start_point']), main_data)
										if rec['end_point']:
											worksheet.write_string(row, col + 15, str(rec['end_point']), main_data)
										if rec['route_name']:
											worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
										if rec['start_time']:
											worksheet.write_string(row, col + 17, str(rec['start_time']), main_data)
										if rec['actual_start_datetime']:
											worksheet.write_string(row, col + 18, str(rec['actual_start_datetime']),
																   main_data)
										if rec['act_end_time']:
											worksheet.write_string(row, col + 19, str(rec['act_end_time']), main_data)
										if rec['est_trip_time']:
											worksheet.write_string(row, col + 20, str(rec['est_trip_time']), main_data)
										if rec['end_time']:
											worksheet.write_string(row, col + 21, str(rec['end_time']), main_data)
										if rec['actual_delay']:
											worksheet.write_string(row, col + 22, str(rec['actual_delay']), main_data)
										if rec['curr_arrival']:
											worksheet.write_string(row, col + 23, str(rec['curr_arrival']), main_data)
										if rec['curr_desti']:
											worksheet.write_string(row, col + 24, str(rec['curr_desti']), main_data)
										if rec['trip_load']:
											worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
										if rec['trip_dis']:
											worksheet.write_number(row, col + 26, rec['trip_dis'], main_data)
											trip_distance += rec['trip_dis']
										if rec['trip_extra_dis']:
											worksheet.write_number(row, col + 27, rec['trip_extra_dis'], main_data)
											extra_distance += rec['trip_extra_dis']
										if rec['reason']:
											worksheet.write_string(row, col + 28, str(rec['reason']), main_data)
										if rec['total_distance']:
											worksheet.write_number(row, col + 29, rec['total_distance'], main_data)
											total_distance += rec['total_distance']
										if rec['trip_total_fuel']:
											worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
											total_fuel_expense_amount += rec['trip_total_fuel']
										if rec['tot_reward_amt_frontend']:
											worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'],
																   main_data)
											total_reward_amt += rec['tot_reward_amt_frontend']
										if rec['add_reward_amt_frontend']:
											worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'],
																   main_data)
											additional_reward_amt += rec['add_reward_amt_frontend']
										if rec['total_fuel_expense_amount']:
											worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'],
																   main_data)
											total_fuel_expense_amt += rec['total_fuel_expense_amount']
										if rec['no_of_loading_vehicles_at_start_trip']:
											worksheet.write_number(row, col + 34,
																   rec['no_of_loading_vehicles_at_start_trip'],
																   main_data)
										if rec['no_of_loading_vehicles_on_transit']:
											worksheet.write_number(row, col + 35,
																   rec['no_of_loading_vehicles_on_transit'], main_data)
										if rec['car_num']:
											worksheet.write_number(row, col + 36, rec['car_num'], main_data)
											total_cars += rec['car_num']
										if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
											if rec['standard_revenue']:
												worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2),
																	   main_data)
												standard_revenue += rec['standard_revenue']
											if rec['actual_revenue']:
												worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2),
																	   main_data)
												actual_revenue += rec['actual_revenue']
											if rec['trip_state']:
												worksheet.write_string(row, col + 39, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 40, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 41, str(rec['create_user_name']),
																	   main_data)
										else:
											if rec['trip_state']:
												worksheet.write_string(row, col + 37, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 38, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 39, str(rec['create_user_name']),
																	   main_data)
										row += 1
								worksheet.write(row, col, 'Total', main_heading1)
								worksheet.write_number(row, col + 22, trip_distance, main_heading)
								worksheet.write_number(row, col + 23, extra_distance, main_heading)
								worksheet.write_number(row, col + 25, total_distance, main_heading)
								worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
								worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
								worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
								worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
								worksheet.write_number(row, col + 30, total_cars, main_heading)
								if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
									worksheet.write_number(row, col + 31, standard_revenue, main_heading)
									worksheet.write_number(row, col + 32, actual_revenue, main_heading)
								row += 1
			if wiz_obj.group_by == "user":
				worksheet.merge_range('A1:AI1', "Trip Report Group By User", merge_format)
				worksheet.merge_range('A2:AI2', "تفرير الرحلات", merge_format)

				worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row, col + 1, 'Trip Seq No.', main_heading1)
				worksheet.write(row, col + 2, 'Created ON', main_heading1)
				worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
				worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row, col + 5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row, col + 6, 'Trailer Taq No', main_heading1)
				worksheet.write(row, col + 7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row, col + 8, 'Employee ID', main_heading1)
				worksheet.write(row, col + 9, 'Driver Name', main_heading1)
				worksheet.write(row, col + 10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row, col + 11, 'Vehicle Type', main_heading1)
				worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row, col + 13, 'Vehicle State', main_heading1)
				worksheet.write(row, col + 14, 'Start Branch', main_heading1)
				worksheet.write(row, col + 15, 'End Branch', main_heading1)
				worksheet.write(row, col + 16, 'Route Name', main_heading1)
				worksheet.write(row, col + 17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row, col + 18, 'Actual Start Date', main_heading1)
				worksheet.write(row, col + 19, 'Scheduled End Date', main_heading1)
				worksheet.write(row, col + 20, 'Est. Duration', main_heading1)
				worksheet.write(row, col + 21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row, col + 22, 'Actual Delay', main_heading1)
				worksheet.write(row, col + 23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row, col + 24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row, col + 25, 'Truck Load', main_heading1)
				worksheet.write(row, col + 26, 'Trip Distance', main_heading1)
				worksheet.write(row, col + 27, 'Extra Distance', main_heading1)
				worksheet.write(row, col + 28, 'Reason', main_heading1)
				worksheet.write(row, col + 29, 'Total Distance', main_heading1)
				worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
				worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row, col + 36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
					worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
					worksheet.write(row, col + 39, 'Trip Status', main_heading1)
					worksheet.write(row, col + 40, 'User Code', main_heading1)
					worksheet.write(row, col + 41, 'User', main_heading1)
					worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row += 1

				worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
				worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
				worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row, col + 5, 'رقم اللوحة', main_heading1)
				worksheet.write(row, col + 6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row, col + 7, 'اسم المقطورة', main_heading1)
				worksheet.write(row, col + 8, 'كود السائق', main_heading1)
				worksheet.write(row, col + 9, 'إسم السائق', main_heading1)
				worksheet.write(row, col + 10, 'رقم الجوال', main_heading1)
				worksheet.write(row, col + 11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row, col + 13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row, col + 14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row, col + 15, 'فرع الوصول', main_heading1)
				worksheet.write(row, col + 16, 'خط السير', main_heading1)
				worksheet.write(row, col + 17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row, col + 18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row, col + 19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row, col + 20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row, col + 21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row, col + 22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row, col + 23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row, col + 24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row, col + 26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row, col + 27, 'مسافة أضافية', main_heading1)
				worksheet.write(row, col + 28, 'السبب', main_heading1)
				worksheet.write(row, col + 29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
				worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row, col + 36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row, col + 39, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 41, 'المستخدم', main_heading1)
					worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)

				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					user_list = []
					for data in final_data:
						if data['create_user_name']:
							if data['create_user_name'] not in sticker_no_list:
								sticker_no_list.append(data['create_user_name'])
					if user_list:
						for user in user_list:
							if user:
								worksheet.write(row, col, 'User', main_heading1)
								worksheet.write_string(row, col+1,user, main_data)
								worksheet.write(row, col+2, 'المستخدم', main_heading1)
								row += 1
								for rec in final_data:
									if rec['create_user_name'] == user:
										if rec['sticker']:
											worksheet.write_string(row, col, str(rec['sticker']), main_data)
										if rec['trip_name']:
											worksheet.write_string(row, col + 1, str(rec['trip_name']), main_data)
										if rec['created_on']:
											worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
										if rec['model_name']:
											worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
										if rec['vehicle_group_name']:
											worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']),
																   main_data)
										if rec['vehicle_license_plate_no']:
											worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']),
																   main_data)
										if rec['trailer_taq_no']:
											worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
										if rec['trailer_ar_name']:
											worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
										if rec['driver_code']:
											worksheet.write_string(row, col + 8, str(rec['driver_code']), main_data)
										if rec['driver_name']:
											worksheet.write_string(row, col + 9, str(rec['driver_name']), main_data)
										if rec['driver_phone']:
											worksheet.write_string(row, col + 10, str(rec['driver_phone']), main_data)
										if rec['trailer_cat']:
											worksheet.write_string(row, col + 11, str(rec['trailer_cat']), main_data)
										if rec['display_expense_mthod_id']:
											worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']),
																   main_data)
										if rec['vehicle_state']:
											worksheet.write_string(row, col + 13, str(rec['vehicle_state']), main_data)
										if rec['start_point']:
											worksheet.write_string(row, col + 14, str(rec['start_point']), main_data)
										if rec['end_point']:
											worksheet.write_string(row, col + 15, str(rec['end_point']), main_data)
										if rec['route_name']:
											worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
										if rec['start_time']:
											worksheet.write_string(row, col + 17, str(rec['start_time']), main_data)
										if rec['actual_start_datetime']:
											worksheet.write_string(row, col + 18, str(rec['actual_start_datetime']),
																   main_data)
										if rec['act_end_time']:
											worksheet.write_string(row, col + 19, str(rec['act_end_time']), main_data)
										if rec['est_trip_time']:
											worksheet.write_string(row, col + 20, str(rec['est_trip_time']), main_data)
										if rec['end_time']:
											worksheet.write_string(row, col + 21, str(rec['end_time']), main_data)
										if rec['actual_delay']:
											worksheet.write_string(row, col + 22, str(rec['actual_delay']), main_data)
										if rec['curr_arrival']:
											worksheet.write_string(row, col + 23, str(rec['curr_arrival']), main_data)
										if rec['curr_desti']:
											worksheet.write_string(row, col + 24, str(rec['curr_desti']), main_data)
										if rec['trip_load']:
											worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
										if rec['trip_dis']:
											worksheet.write_number(row, col + 26, rec['trip_dis'], main_data)
											trip_distance += rec['trip_dis']
										if rec['trip_extra_dis']:
											worksheet.write_number(row, col + 27, rec['trip_extra_dis'], main_data)
											extra_distance += rec['trip_extra_dis']
										if rec['reason']:
											worksheet.write_string(row, col + 28, str(rec['reason']), main_data)
										if rec['total_distance']:
											worksheet.write_number(row, col + 29, rec['total_distance'], main_data)
											total_distance += rec['total_distance']
										if rec['trip_total_fuel']:
											worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
											total_fuel_expense_amount += rec['trip_total_fuel']
										if rec['tot_reward_amt_frontend']:
											worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'],
																   main_data)
											total_reward_amt += rec['tot_reward_amt_frontend']
										if rec['add_reward_amt_frontend']:
											worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'],
																   main_data)
											additional_reward_amt += rec['add_reward_amt_frontend']
										if rec['total_fuel_expense_amount']:
											worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'],
																   main_data)
											total_fuel_expense_amt += rec['total_fuel_expense_amount']
										if rec['no_of_loading_vehicles_at_start_trip']:
											worksheet.write_number(row, col + 34,
																   rec['no_of_loading_vehicles_at_start_trip'],
																   main_data)
										if rec['no_of_loading_vehicles_on_transit']:
											worksheet.write_number(row, col + 35,
																   rec['no_of_loading_vehicles_on_transit'], main_data)
										if rec['car_num']:
											worksheet.write_number(row, col + 36, rec['car_num'], main_data)
											total_cars += rec['car_num']
										if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
											if rec['standard_revenue']:
												worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2),
																	   main_data)
												standard_revenue += rec['standard_revenue']
											if rec['actual_revenue']:
												worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2),
																	   main_data)
												actual_revenue += rec['actual_revenue']
											if rec['trip_state']:
												worksheet.write_string(row, col + 39, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 40, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 41, str(rec['create_user_name']),
																	   main_data)
										else:
											if rec['trip_state']:
												worksheet.write_string(row, col + 37, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 38, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 39, str(rec['create_user_name']),
																	   main_data)
										row += 1
								worksheet.write(row, col, 'Total', main_heading1)
								worksheet.write_number(row, col + 22, trip_distance, main_heading)
								worksheet.write_number(row, col + 23, extra_distance, main_heading)
								worksheet.write_number(row, col + 25, total_distance, main_heading)
								worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
								worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
								worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
								worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
								worksheet.write_number(row, col + 30, total_cars, main_heading)
								if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
									worksheet.write_number(row, col + 31, standard_revenue, main_heading)
									worksheet.write_number(row, col + 32, actual_revenue, main_heading)
								row += 1
			if wiz_obj.group_by == "trip_status":
				worksheet.merge_range('A1:AI1', "Trip Report Group By Driver Code", merge_format)
				worksheet.merge_range('A2:AI2', "تفرير الرحلات", merge_format)

				worksheet.write(row, col, 'Vehicle Sticker', main_heading1)
				worksheet.write(row, col + 1, 'Trip Seq No.', main_heading1)
				worksheet.write(row, col + 2, 'Created ON', main_heading1)
				worksheet.write(row, col + 3, 'Vehicle Name', main_heading1)
				worksheet.write(row, col + 4, 'Vehicle Group Name', main_heading1)
				worksheet.write(row, col + 5, 'Vehicle license Plate No.', main_heading1)
				worksheet.write(row, col + 6, 'Trailer Taq No', main_heading1)
				worksheet.write(row, col + 7, 'Trailer Ar Name', main_heading1)
				worksheet.write(row, col + 8, 'Employee ID', main_heading1)
				worksheet.write(row, col + 9, 'Driver Name', main_heading1)
				worksheet.write(row, col + 10, 'Driver Mobile No.', main_heading1)
				worksheet.write(row, col + 11, 'Vehicle Type', main_heading1)
				worksheet.write(row, col + 12, 'Fuel Expense Type', main_heading1)
				worksheet.write(row, col + 13, 'Vehicle State', main_heading1)
				worksheet.write(row, col + 14, 'Start Branch', main_heading1)
				worksheet.write(row, col + 15, 'End Branch', main_heading1)
				worksheet.write(row, col + 16, 'Route Name', main_heading1)
				worksheet.write(row, col + 17, 'Scheduled Start Date', main_heading1)
				worksheet.write(row, col + 18, 'Actual Start Date', main_heading1)
				worksheet.write(row, col + 19, 'Scheduled End Date', main_heading1)
				worksheet.write(row, col + 20, 'Est. Duration', main_heading1)
				worksheet.write(row, col + 21, 'Last waypoint Arrival Date', main_heading1)
				worksheet.write(row, col + 22, 'Actual Delay', main_heading1)
				worksheet.write(row, col + 23, 'Last Register Arrival Date', main_heading1)
				worksheet.write(row, col + 24, 'Vehicle Current Branch', main_heading1)
				worksheet.write(row, col + 25, 'Truck Load', main_heading1)
				worksheet.write(row, col + 26, 'Trip Distance', main_heading1)
				worksheet.write(row, col + 27, 'Extra Distance', main_heading1)
				worksheet.write(row, col + 28, 'Reason', main_heading1)
				worksheet.write(row, col + 29, 'Total Distance', main_heading1)
				worksheet.write(row, col + 30, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 31, 'Total Reward amount', main_heading1)
				worksheet.write(row, col + 32, 'Additional Reward Amount', main_heading1)
				worksheet.write(row, col + 33, 'Total Fuel Expense Amt', main_heading1)
				worksheet.write(row, col + 34, 'Number of Loading vehicles at Start Trip', main_heading1)
				worksheet.write(row, col + 35, 'Number of Loading vehicles at transit', main_heading1)
				worksheet.write(row, col + 36, 'Total Cars', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'Standard Revenue', main_heading1)
					worksheet.write(row, col + 38, 'Actual Revenue', main_heading1)
					worksheet.write(row, col + 39, 'Trip Status', main_heading1)
					worksheet.write(row, col + 40, 'User Code', main_heading1)
					worksheet.write(row, col + 41, 'User', main_heading1)
					worksheet.write(row,col+42, 'No. of Payment voucher', main_heading1)
					worksheet.write(row,col+43, 'Payment voucher No.', main_heading1)
					worksheet.write(row,col+44, 'Vendor Bill No.', main_heading1)
				else:
					worksheet.write(row, col + 37, 'Trip Status', main_heading1)
					worksheet.write(row, col + 38, 'User Code', main_heading1)
					worksheet.write(row, col + 39, 'User', main_heading1)
					worksheet.write(row, col + 40, 'No. of Payment voucher', main_heading1)
					worksheet.write(row, col + 41, 'Payment voucher No.', main_heading1)
					worksheet.write(row, col + 42, 'Vendor Bill No.', main_heading1)
				row += 1

				worksheet.write(row, col, 'كـود الشاحــنة', main_heading1)
				worksheet.write(row, col + 1, 'رقم الرحلة', main_heading1)
				worksheet.write(row, col + 2, 'أنشئ في', main_heading1)
				worksheet.write(row, col + 3, 'اسم الشاحنة', main_heading1)
				worksheet.write(row, col + 4, 'اسم مجموعة الشاحنة', main_heading1)
				worksheet.write(row, col + 5, 'رقم اللوحة', main_heading1)
				worksheet.write(row, col + 6, 'استيكر المقطورة', main_heading1)
				worksheet.write(row, col + 7, 'اسم المقطورة', main_heading1)
				worksheet.write(row, col + 8, 'كود السائق', main_heading1)
				worksheet.write(row, col + 9, 'إسم السائق', main_heading1)
				worksheet.write(row, col + 10, 'رقم الجوال', main_heading1)
				worksheet.write(row, col + 11, 'نوع الشاحنة', main_heading1)
				worksheet.write(row, col + 12, 'نوع احتساب مصروف الطريق', main_heading1)
				worksheet.write(row, col + 13, 'حالة الشاحنة', main_heading1)
				worksheet.write(row, col + 14, 'فرع الإنطلاق', main_heading1)
				worksheet.write(row, col + 15, 'فرع الوصول', main_heading1)
				worksheet.write(row, col + 16, 'خط السير', main_heading1)
				worksheet.write(row, col + 17, 'تاريخ بدء الجدولة', main_heading1)
				worksheet.write(row, col + 18, 'تاريخ بدء الانطلاق الفعلي', main_heading1)
				worksheet.write(row, col + 19, 'تاريخ الوصول المتوقع', main_heading1)
				worksheet.write(row, col + 20, 'المدة الزمنية المتوقعة', main_heading1)
				worksheet.write(row, col + 21, 'تاريخ اخر محطة وصول', main_heading1)
				worksheet.write(row, col + 22, 'التاخير الفعلي', main_heading1)
				worksheet.write(row, col + 23, 'تاربخ اخر تسجيل وصول', main_heading1)
				worksheet.write(row, col + 24, 'الفرع الحالي لشاحنة', main_heading1)
				worksheet.write(row, col + 25, 'حمولة الشاحنة', main_heading1)
				worksheet.write(row, col + 26, 'مسـافة الرحــلة', main_heading1)
				worksheet.write(row, col + 27, 'مسافة أضافية', main_heading1)
				worksheet.write(row, col + 28, 'السبب', main_heading1)
				worksheet.write(row, col + 29, 'اجمالي المسافة', main_heading1)
				worksheet.write(row, col + 30, 'مصروف الطريق', main_heading1)
				worksheet.write(row, col + 31, 'قيمة مكافأة الحمولة', main_heading1)
				worksheet.write(row, col + 32, 'مكأفاة الحمولة الإضافية', main_heading1)
				worksheet.write(row, col + 33, 'اجمالي مصروف الطريق', main_heading1)
				worksheet.write(row, col + 34, 'عدد المركبات عند الإنطلاق', main_heading1)
				worksheet.write(row, col + 35, 'عدد المركبات المحملة ترانزيت', main_heading1)
				worksheet.write(row, col + 36, 'السيارات في الرحلة', main_heading1)
				if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
					worksheet.write(row, col + 37, 'الإيرادات المتوقعة', main_heading1)
					worksheet.write(row, col + 38, 'الإيرادات الفعلية', main_heading1)
					worksheet.write(row, col + 39, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 40, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 41, 'المستخدم', main_heading1)
					worksheet.write(row,col+42, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row,col+43, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row,col+44, 'ارقام فاتورة المورد', main_heading1)
				else:
					worksheet.write(row, col + 37, 'حالة الرحلة', main_heading1)
					worksheet.write(row, col + 38, 'كود منشئ الرحلة', main_heading1)
					worksheet.write(row, col + 39, 'المستخدم', main_heading1)
					worksheet.write(row, col + 40, 'عدد سندات الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 41, 'ارقام سند الصرف للرحلة', main_heading1)
					worksheet.write(row, col + 42, 'ارقام فاتورة المورد', main_heading1)

				worksheet.set_column('A:S', 20)

				row += 1
				col = 0
				trip_distance = 0
				extra_distance = 0
				total_distance = 0
				total_fuel_expense_amount = 0
				total_reward_amt = 0
				additional_reward_amt = 0
				total_fuel_expense_amt = 0
				total_cars = 0
				standard_revenue = 0
				actual_revenue = 0
				if final_data:
					trip_state_list = []
					for data in final_data:
						if data['trip_state']:
							if data['trip_state'] not in sticker_no_list:
								sticker_no_list.append(data['trip_state'])
					if trip_state_list:
						for trip_state in trip_state_list:
							if trip_state:
								worksheet.write(row, col, 'Trip Status', main_heading1)
								worksheet.write_string(row, col+1,trip_state, main_data)
								worksheet.write(row, col+2, 'حالة الرحلة', main_heading1)
								row += 1
								for rec in final_data:
									if rec['trip_state'] == trip_state:
										if rec['sticker']:
											worksheet.write_string(row, col, str(rec['sticker']), main_data)
										if rec['trip_name']:
											worksheet.write_string(row, col + 1, str(rec['trip_name']), main_data)
										if rec['created_on']:
											worksheet.write_string(row, col + 2, str(rec['created_on']), main_data)
										if rec['model_name']:
											worksheet.write_string(row, col + 3, str(rec['model_name']), main_data)
										if rec['vehicle_group_name']:
											worksheet.write_string(row, col + 4, str(rec['vehicle_group_name']),
																   main_data)
										if rec['vehicle_license_plate_no']:
											worksheet.write_string(row, col + 5, str(rec['vehicle_license_plate_no']),
																   main_data)
										if rec['trailer_taq_no']:
											worksheet.write_string(row, col + 6, str(rec['trailer_taq_no']), main_data)
										if rec['trailer_ar_name']:
											worksheet.write_string(row, col + 7, str(rec['trailer_ar_name']), main_data)
										if rec['driver_code']:
											worksheet.write_string(row, col + 8, str(rec['driver_code']), main_data)
										if rec['driver_name']:
											worksheet.write_string(row, col + 9, str(rec['driver_name']), main_data)
										if rec['driver_phone']:
											worksheet.write_string(row, col + 10, str(rec['driver_phone']), main_data)
										if rec['trailer_cat']:
											worksheet.write_string(row, col + 11, str(rec['trailer_cat']), main_data)
										if rec['display_expense_mthod_id']:
											worksheet.write_string(row, col + 12, str(rec['display_expense_mthod_id']),
																   main_data)
										if rec['vehicle_state']:
											worksheet.write_string(row, col + 13, str(rec['vehicle_state']), main_data)
										if rec['start_point']:
											worksheet.write_string(row, col + 14, str(rec['start_point']), main_data)
										if rec['end_point']:
											worksheet.write_string(row, col + 15, str(rec['end_point']), main_data)
										if rec['route_name']:
											worksheet.write_string(row, col + 16, str(rec['route_name']), main_data)
										if rec['start_time']:
											worksheet.write_string(row, col + 17, str(rec['start_time']), main_data)
										if rec['actual_start_datetime']:
											worksheet.write_string(row, col + 18, str(rec['actual_start_datetime']),
																   main_data)
										if rec['act_end_time']:
											worksheet.write_string(row, col + 19, str(rec['act_end_time']), main_data)
										if rec['est_trip_time']:
											worksheet.write_string(row, col + 20, str(rec['est_trip_time']), main_data)
										if rec['end_time']:
											worksheet.write_string(row, col + 21, str(rec['end_time']), main_data)
										if rec['actual_delay']:
											worksheet.write_string(row, col + 22, str(rec['actual_delay']), main_data)
										if rec['curr_arrival']:
											worksheet.write_string(row, col + 23, str(rec['curr_arrival']), main_data)
										if rec['curr_desti']:
											worksheet.write_string(row, col + 24, str(rec['curr_desti']), main_data)
										if rec['trip_load']:
											worksheet.write_string(row, col + 25, str(rec['trip_load']), main_data)
										if rec['trip_dis']:
											worksheet.write_number(row, col + 26, rec['trip_dis'], main_data)
											trip_distance += rec['trip_dis']
										if rec['trip_extra_dis']:
											worksheet.write_number(row, col + 27, rec['trip_extra_dis'], main_data)
											extra_distance += rec['trip_extra_dis']
										if rec['reason']:
											worksheet.write_string(row, col + 28, str(rec['reason']), main_data)
										if rec['total_distance']:
											worksheet.write_number(row, col + 29, rec['total_distance'], main_data)
											total_distance += rec['total_distance']
										if rec['trip_total_fuel']:
											worksheet.write_number(row, col + 30, rec['trip_total_fuel'], main_data)
											total_fuel_expense_amount += rec['trip_total_fuel']
										if rec['tot_reward_amt_frontend']:
											worksheet.write_number(row, col + 31, rec['tot_reward_amt_frontend'],
																   main_data)
											total_reward_amt += rec['tot_reward_amt_frontend']
										if rec['add_reward_amt_frontend']:
											worksheet.write_number(row, col + 32, rec['add_reward_amt_frontend'],
																   main_data)
											additional_reward_amt += rec['add_reward_amt_frontend']
										if rec['total_fuel_expense_amount']:
											worksheet.write_number(row, col + 33, rec['total_fuel_expense_amount'],
																   main_data)
											total_fuel_expense_amt += rec['total_fuel_expense_amount']
										if rec['no_of_loading_vehicles_at_start_trip']:
											worksheet.write_number(row, col + 34,
																   rec['no_of_loading_vehicles_at_start_trip'],
																   main_data)
										if rec['no_of_loading_vehicles_on_transit']:
											worksheet.write_number(row, col + 35,
																   rec['no_of_loading_vehicles_on_transit'], main_data)
										if rec['car_num']:
											worksheet.write_number(row, col + 36, rec['car_num'], main_data)
											total_cars += rec['car_num']
										if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
											if rec['standard_revenue']:
												worksheet.write_number(row, col + 37, round(rec['standard_revenue'], 2),
																	   main_data)
												standard_revenue += rec['standard_revenue']
											if rec['actual_revenue']:
												worksheet.write_number(row, col + 38, round(rec['actual_revenue'], 2),
																	   main_data)
												actual_revenue += rec['actual_revenue']
											if rec['trip_state']:
												worksheet.write_string(row, col + 39, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 40, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 41, str(rec['create_user_name']),
																	   main_data)
										else:
											if rec['trip_state']:
												worksheet.write_string(row, col + 37, str(rec['trip_state']), main_data)
											if rec['create_user_code']:
												worksheet.write_string(row, col + 38, str(rec['create_user_code']),
																	   main_data)
											if rec['create_user_name']:
												worksheet.write_string(row, col + 39, str(rec['create_user_name']),
																	   main_data)
										row += 1
								worksheet.write(row, col, 'Total', main_heading1)
								worksheet.write_number(row, col + 22, trip_distance, main_heading)
								worksheet.write_number(row, col + 23, extra_distance, main_heading)
								worksheet.write_number(row, col + 25, total_distance, main_heading)
								worksheet.write_number(row, col + 26, total_fuel_expense_amount, main_heading)
								worksheet.write_number(row, col + 27, total_reward_amt, main_heading)
								worksheet.write_number(row, col + 28, additional_reward_amt, main_heading)
								worksheet.write_number(row, col + 29, total_fuel_expense_amt, main_heading)
								worksheet.write_number(row, col + 30, total_cars, main_heading)
								if self.env.user.has_group('bsg_trip_mgmt.group_show_trip_revenue'):
									worksheet.write_number(row, col + 31, standard_revenue, main_heading)
									worksheet.write_number(row, col + 32, actual_revenue, main_heading)
								row += 1
	def get_days_hours(self,hours_count, days, hours):
		print('...............hours_count.........',hours_count)
		if hours_count <= 0:
			return days, hours
		elif hours_count >= 25:
			days += 1
			hours_count = hours_count - 24
			return self.get_days_hours(hours_count, days, hours)
		elif hours_count <= 24 and hours_count > 0:
			hours += hours_count
			hours_count = 0
			return self.get_days_hours(hours_count, days, hours)

#############################################################################################################
class BranchesVoucherXlsx(models.TransientModel):
	_name = 'report.bassami_fleet_trip_report.so_wise_revenue_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'

	# @api.multi
	def generate_xlsx_report(self, workbook, input_records, lines):


		wiz_id = self.env['so.wise.revenue'].browse(self._context.get('active_id'))
		domain = [('bsg_fleet_trip_id', '!=', False),('create_date', '>=', wiz_id.form), ('create_date', '<=', wiz_id.to)]
		if wiz_id.vehicle_type:
			domain.append(('bsg_fleet_trip_id.vehicle_id.vehicle_type', 'in', wiz_id.vehicle_type.ids))
		if wiz_id.fleet_id:
			domain.append(('bsg_fleet_trip_id.vehicle_id.id', 'in', wiz_id.fleet_id.ids))
		if wiz_id.driver_code:
			domain.append(('bsg_fleet_trip_id.driver_id.id', 'in', wiz_id.driver_code.ids))
		

		recs = self.env['fleet.vehicle.trip.pickings'].sudo().search(domain)
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
			"align": 'right',
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
			"align": 'right',
			"valign": 'vcenter',
			'font_size': '8',
			})
		merge_format.set_shrink()
		main_heading.set_text_justlast(1)
		main_data.set_border()
		worksheet = workbook.add_worksheet('Fleet Trip Report')


		worksheet.merge_range('A1:S1','Sales Report',merge_format)

		worksheet.write('A3', 'رقم السجل', main_heading1)
		worksheet.write('B3', 'رقم الاتفاقية', main_heading1)
		worksheet.write('C3', 'انشئ في', main_heading1)
		worksheet.write('D3', 'حالة السجل', main_heading1)
		worksheet.write('E3', 'فرع الشحن', main_heading1)
		worksheet.write('F3', 'فرع الوصول', main_heading1)
		worksheet.write('G3', 'نوع الشحن',  main_heading1)
		worksheet.write('H3', 'العميل', main_heading1)
		worksheet.write('I3', ' مبلغ ايراد السجل', main_heading1)
		worksheet.write('J3', 'رقم االرحلة', main_heading1)
		worksheet.write('K3', 'نوع  الرحلة', main_heading1)
		worksheet.write('L3', 'حالة الرحلة', main_heading1)
		worksheet.write('M3', 'نوع السطحة', main_heading1)
		worksheet.write('N3','رقم الشاحنة',  main_heading1)
		worksheet.write('O3', 'تاريخ الانطلاق', main_heading1)
		worksheet.write('P3', 'تاريخ الوصول', main_heading1)
		worksheet.write('Q3', 'كود السائق', main_heading1)
		worksheet.set_column('A:S', 20)
	
		row = 3
		col = 0
		for rec in recs:
			line = rec.picking_name
			trip = rec.bsg_fleet_trip_id
			tr_type  = trip.sudo().trip_type
			worksheet.write_string (row, col,str(line.sale_line_rec_name or ''),main_data)
			worksheet.write_string (row, col+1,str(line.bsg_cargo_sale_id and line.bsg_cargo_sale_id.name or ''),main_data)
			worksheet.write_string (row, col+2,str(line.order_date_date),main_data)
			worksheet.write_string (row, col+3,str(dict(line._fields['state']._description_selection(self.with_context({'lang': 'ar_AA'}).env)).get(line.state)),main_data)
			worksheet.write_string (row, col+4,str(line.loc_from.route_waypoint_name),main_data)
			worksheet.write_string (row, col+5,str(line.loc_to.route_waypoint_name),main_data)
			worksheet.write_string (row, col+6,str(line.shipment_type and line.shipment_type.car_shipment_name or ''),main_data)
			worksheet.write_string (row, col+7,str(line.customer_id.name),main_data)
			trip_revenue = 0
			# matching_trip = line.trip_history_ids.filtered(lambda l:l.fleet_trip_id and l.fleet_trip_id.id == trip.id)
			# if matching_trip:
			# 	trip_revenue = round(matching_trip[0].earned_revenue, 2)
			if tr_type != 'local':
				worksheet.write_number (row, col+8,line.charges or 0,main_data)
			else:
				worksheet.write_number (row, col+8,35.00 or 0,main_data)
			worksheet.write_string (row, col+9,str(trip.name),main_data)
			worksheet.write_string (row, col+10,str(dict(trip.sudo()._fields['trip_type']._description_selection(self.with_context({'lang': 'ar_AA'}).env)).get(tr_type)),main_data)
			worksheet.write_string (row, col+11,str(dict(trip._fields['state']._description_selection(self.with_context({'lang': 'ar_AA'}).env)).get(trip.state)),main_data)
			worksheet.write_string (row, col+13,str(trip.vehicle_id.vehicle_type.vehicle_type_name),main_data)
			worksheet.write_string (row, col+14,str(trip.vehicle_id.taq_number),main_data)
			worksheet.write_string (row, col+15,str(trip.actual_start_datetime and trip.actual_start_datetime.date() or ''),main_data)
			worksheet.write_string (row, col+16,str(trip.actual_end_datetime and trip.actual_end_datetime.date() or ''),main_data)
			worksheet.write_string (row, col+16,str(trip.driver_id.driver_code or ''),main_data)

			row += 1

		
			

	
