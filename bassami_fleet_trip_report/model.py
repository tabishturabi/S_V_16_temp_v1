#-*- coding:utf-8 -*-
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

class TripFleetBassamiReport(models.AbstractModel):
	_name = 'report.bassami_fleet_trip_report.fleet_trip_report'

	@api.model
	def _get_report_values(self, docids, data=None):
		model = self.env.context.get('active_model')
		# record_wizard = self.env[self.model].browse(self.env.context.get('active_id'))
		wiz_obj = self.env['fleet.trip.report'].search([('id', '=', self.env.context.get('active_id'))])
		print('..................wiz_obj.........',wiz_obj)
		print_date = wiz_obj.print_date

		
		# form = record_wizard.form
		# to = record_wizard.to
		# fleet_id = record_wizard.fleet_id
		# filter_type = record_wizard.filter_type
		# report_type = record_wizard.report_type
		# vehicle_type = record_wizard.vehicle_type
		# driver_code = record_wizard.driver_code
		# branch_from = record_wizard.branch_from
		# branch_to = record_wizard.branch_to
		# trip_type = record_wizard.trip_type
		print('..................data..........data..................', data)
		form = wiz_obj.form
		# data['form']
		to = wiz_obj.to
		# data['to']
		date = wiz_obj.date
		# data['date']
		fleet_id = wiz_obj.fleet_id
		# data['fleet_id']
		filter_type = wiz_obj.filter_type
		# data['filter_type']
		report_type = wiz_obj.report_type
		# data['report_type']
		vehicle_type = wiz_obj.vehicle_type
		# data['vehicle_type']
		driver_code = wiz_obj.driver_code
		# data['driver_code']
		branch_from = wiz_obj.branch_from
		# data['branch_from']
		branch_to = wiz_obj.branch_to
		# data['branch_to']
		trip_type = wiz_obj.trip_type
		# data['trip_type']
		filter_date_by = wiz_obj.filter_date_by
		# data['filter_date_by']
		sa_date_condition = wiz_obj.sa_date_condition
		# data['sa_date_condition']
		user_id = wiz_obj.user_id
		# data['user_id']
		trip_status = wiz_obj.trip_status
		# data['trip_status']
		truck_load = wiz_obj.truck_load
		# data['truck_load']
		car_load = wiz_obj.car_load
		# data['car_load']
		vehicle_group_id = wiz_obj.vehicle_group_id
		# data['vehicle_group_id']
		fuel_expense_type_id = wiz_obj.fuel_expense_type_id
		# data['fuel_expense_type_id']
		head = "Fleet Trips"


		if form:
			form = form + timedelta(hours=3)
		if to:
			to = to + timedelta(hours=3)

		# order_date = str(order_date)[:16]
		# order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

		final_data = []
		
		if report_type == 'fleet':
			if filter_type == 'all':
				fleets = []
				domain = []
				print('..................report_type..........report_type..................',report_type)
			# 	if form:
			# 		domain.append(('expected_start_date','>=',form))
			# 	if to:
			# 		domain.append(('expected_start_date','<=',to))
			# 	if vehicle_type:
			# 		domain.append(('vehicle_id.vehicle_type.id','in',vehicle_type.ids))
			# 	if fleet_id:
			# 		domain.append(('vehicle_id.id','in',fleet_id.ids))
			# 	if driver_code:
			# 		domain.append(('driver_id.id','in',driver_code.ids))
			# 	if branch_from:
			# 		domain.append(('from_route_branch_id.id','in',branch_from.ids))
			#
			# 	if branch_to:
			# 		fleet_trips = []
			# 		trips_rec = self.env['fleet.vehicle.trip'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(domain, order='expected_start_date')
			# 		for t in trips_rec:
			# 			arrival_point = self.env['fleet.trip.arrival'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('trip_id.id','=',t.id)])
			# 			end_arrival_to = arrival_point[-1]
			# 			if end_arrival_to.waypoint_to.id in branch_to.ids:
			# 				fleet_trips.append(t)
			#
			# 	if not branch_to:
			# 		fleet_trips = self.env['fleet.vehicle.trip'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(domain, order='expected_start_date')
			#
			# 	for f in fleet_trips:
			# 		if f.vehicle_id:
			# 			if f.vehicle_id not in fleets:
			# 				fleets.append(f.vehicle_id)
			#
			# for rec in fleets:
			# 	trips = []
			# 	for line in fleet_trips:
			# 		if line.vehicle_id.id == rec.id:
			# 			trips.append(line)
			#
			# 	if trips:
			# 		trips = sorted(trips, key=lambda k: k.id)
			# 		trips =  (trips[-1])
			#
			# 		vech_state = ""
			# 		start_point = ""
			# 		end_point = ""
			# 		start_time = ""
			# 		act_end_time = ""
			# 		end_time = ""
			# 		trip_state = ""
			# 		curr_desti = ""
			# 		curr_arrival = ""
			# 		driver_code = rec.bsg_driver.driver_code
			# 		driver_name = rec.bsg_driver.name
			#
			# 		trips_point = self.env['fleet.vehicle.trip.waypoints'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('bsg_fleet_trip_id.id','=',trips.id)])
			# 		if trips_point:
			# 			start_trip = trips_point[0]
			# 			end_trip = trips_point[-1]
			#
			# 			start_point = start_trip.waypoint.loc_branch_id.branch_ar_name
			# 			end_point = end_trip.waypoint.loc_branch_id.branch_ar_name
			#
			# 		arrival_point = self.env['fleet.trip.arrival'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('trip_id.id','=',trips.id)])
			# 		if arrival_point:
			# 			arrival_point = sorted(arrival_point, key=lambda k: k.id)
			# 			start_arrival = arrival_point[0]
			# 			end_arrival = arrival_point[-1]
			#
			# 			# start_time = trips.expected_start_date
			# 			# act_end_time = start_arrival.trip_id.expected_end_date
			# 			# end_time = end_arrival.actual_end_time
			#
			# 			if trips.expected_start_date:
			# 				start_time = trips.expected_start_date + timedelta(hours=3)
			# 			if start_arrival.trip_id.expected_end_date:
			# 				act_end_time = start_arrival.trip_id.expected_end_date + timedelta(hours=3)
			# 			if end_arrival.actual_end_time:
			# 				end_time = end_arrival.actual_end_time + timedelta(hours=3)
			#
			# 		currarrival_point = self.env['fleet.trip.arrival'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('trip_id.id','=',trips.id),('waypoint_to','=',trips.vehicle_id.current_loc_id.id)],limit=1)
			# 		if currarrival_point:
			# 			curr_desti = currarrival_point.waypoint_to.route_waypoint_name
			# 			# curr_arrival = currarrival_point.actual_end_time
			# 			if currarrival_point.actual_end_time:
			# 				curr_arrival = currarrival_point.actual_end_time + timedelta(hours=3)
			#
			#
			# 		if rec.state_id.name == 'Linked':
			# 			vech_state =  "مرتبطة بمقطورة"
			# 		elif rec.state_id.name == 'UnLinked':
			# 			vech_state =  "غير مرتبطة بمقطورة"
			# 		elif rec.state_id.name == 'Maintenance':
			# 			vech_state =  "في الصيانة"
			# 		elif rec.state_id.name == 'Draft':
			# 			vech_state =  "مسوده"
			# 		else:
			# 			vech_state = rec.state_id.name
			#
			# 		if trips.state == 'draft':
			# 			trip_state =  "جديد"
			# 		elif trips.state == 'progress':
			# 			trip_state =  "في الطريق"
			# 		elif trips.state == 'finished':
			# 			trip_state =  "انتهت"
			# 		elif trips.state == 'done':
			# 			trip_state =  "انتهت"
			# 		elif trips.state == 'on_transit':
			# 			trip_state =  "في ترانزيت"
			# 		elif trips.state == 'confirmed':
			# 			trip_state =  "رحلة معتمده"
			# 		elif trips.state == 'cancelled':
			# 			trip_state =  "رحلة ملغاه"
			# 		else:
			# 			trip_state = trips.state
				if vehicle_type:
					domain.append(('vehicle_type.id', 'in', vehicle_type.ids))
				if fleet_id:
					domain.append(('id', 'in', fleet_id.ids))
				if driver_code:
					domain.append(('bsg_driver.id', 'in', driver_code.ids))
				if branch_from:
					domain.append(('trip_id.start_branch.id', 'in', branch_from.ids))
				if user_id:
					domain.append(('create_uid', '=', wiz_obj.user_id.id))
				if trip_status:
					domain.append(('trip_id.state', '=', trip_status))
				if truck_load:
					domain.append(('trip_id.display_truck_load', '=', truck_load))
				# if car_load:
				# 	worksheet.write(row, col, 'Car Load', main_heading1)
				# 	worksheet.write_string(row, col + 1, wiz_obj.car_load, main_data)
				# 	row += 1
				# if vehicle_group_id:
				# 	worksheet.write(row, col, 'Vehicle Group Name', main_heading1)
				# 	worksheet.write_string(row, col + 1, wiz_obj.vehicle_group_id.display_name, main_data)
				# 	row += 1
				# 	domain.append(('', '=', vehicle_group_id))
				if fuel_expense_type_id:
					domain.append(('trip_id.display_expense_mthod_id', '=', fuel_expense_type_id.id))

				if wiz_obj.trailer_sticker_no:
					domain.append(('trailer_id', '=', wiz_obj.trailer_sticker_no.id))

				if wiz_obj.license_plate_no:
					domain.append(('license_plate', '=', wiz_obj.license_plate_no))

				if wiz_obj.vehicle_state_id:
					domain.append(('state_id', '=', wiz_obj.vehicle_state_id.id))

				if wiz_obj.driver_link == "linked":
					domain.append(('bsg_driver', '!=', None))
				if wiz_obj.driver_link == "unlinked":
					domain.append(('bsg_driver', '=', False))

				if branch_to:
					fleet_vehicles = []
					vehicles_rec = self.env['fleet.vehicle'].sudo().with_context(
						force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
						domain)
					for t in vehicles_rec:
						arrival_point = self.env['fleet.trip.arrival'].sudo().with_context(
							force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
							[('trip_id.id', '=', t.trip_id.id)])
						if arrival_point:
							end_arrival_to = arrival_point[-1]
							if end_arrival_to.waypoint_to.id in branch_to.ids:
								fleet_vehicles.append(t)

				if not branch_to:
					fleet_vehicles = self.env['fleet.vehicle'].sudo().with_context(
						force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
						domain)
				print('..................fleet_vehicles..............', fleet_vehicles)
				for vehicle_id in fleet_vehicles:
					if vehicle_id:
						if vehicle_id not in fleets:
							fleets.append(vehicle_id)

			for vehicle in fleets:
				print('...................vehicle...........................', vehicle)
				print('...................vehicle data type...........................', type(vehicle))
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

				trips_point = self.env['fleet.vehicle.trip.waypoints'].sudo().with_context(
					force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
					[('bsg_fleet_trip_id.id', '=', vehicle.trip_id.id)])
				if trips_point:
					start_trip = trips_point[0]
					end_trip = trips_point[-1]

					start_point = start_trip.waypoint.loc_branch_id.branch_ar_name
					end_point = end_trip.waypoint.loc_branch_id.branch_ar_name

				arrival_point = self.env['fleet.trip.arrival'].sudo().with_context(
					force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
					[('trip_id.id', '=', vehicle.trip_id.id)])
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

				currarrival_point = self.env['fleet.trip.arrival'].sudo().with_context(
					force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
					[('trip_id.id', '=', vehicle.trip_id.id), ('waypoint_to', '=', vehicle.current_loc_id.id)], limit=1)
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
					vech_state = "مرتبطة بمقطورة"
				elif vehicle.state_id.name == 'UnLinked':
					vech_state = "غير مرتبطة بمقطورة"
				elif vehicle.state_id.name == 'Maintenance':
					vech_state = "في الصيانة"
				elif vehicle.state_id.name == 'Draft':
					vech_state = "مسوده"
				else:
					vech_state = vehicle.state_id.name

				if vehicle.trip_id.state == 'draft':
					trip_state = "جديد"
				elif vehicle.trip_id.state == 'progress':
					trip_state = "في الطريق"
				elif vehicle.trip_id.state == 'finished':
					trip_state = "انتهت"
				elif vehicle.trip_id.state == 'done':
					trip_state = "لانتهت"
				elif vehicle.trip_id.state == 'on_transit':
					trip_state = "في ترانزيت"
				elif vehicle.trip_id.state == 'confirmed':
					trip_state = "رحلة معتمده"
				elif vehicle.trip_id.state == 'cancelled':
					trip_state = "رحلة ملغاه"
				else:
					trip_state = vehicle.trip_id.state

				total_fuel_amount = vehicle.trip_id.total_fuel_amount + vehicle.trip_id.add_reward_amt_frontend + vehicle.trip_id.tot_reward_amt_frontend
				total_distance = vehicle.trip_id.trip_distance + vehicle.trip_id.extra_distance
				actual_delay = "{0} Days {1} Hours ".format(0, 0)

				# if end_time:
				# 	print('................end_time.............', type(end_time))
				#
				# if end_time:
				# 	end_time = end_time - timedelta(hours=3)
				# 	delta = end_time - vehicle.trip_id.expected_end_date
				# 	delta_temp = int(delta.total_seconds())
				# 	if delta_temp < 0:
				# 		delta_temp = abs(int(delta.total_seconds()))
				# 		day, hours = self.get_days_hours(int(delta_temp / 3600), 0, 0)
				# 		day = -day
				# 		hours = -hours
				# 		actual_delay = "{0} Days {1} Hours ".format(day, hours)
				# 	else:
				# 		day, hours = self.get_days_hours(int(delta_temp / 3600), 0, 0)
				# 		actual_delay = "{0} Days {1} Hours ".format(day, hours)
				# else:
				# 	if vehicle.trip_id.expected_end_date:
				# 		delta = datetime.now() - vehicle.trip_id.expected_end_date
				# 		delta_temp = int(delta.total_seconds())
				# 		if delta_temp < 0:
				# 			delta_temp = abs(int(delta.total_seconds()))
				# 			day, hours = self.get_days_hours(int(delta_temp / 3600), 0, 0)
				# 			day = -day
				# 			hours = -hours
				# 			actual_delay = "{0} Days {1} Hours ".format(day, hours)
				# 		else:
				# 			day, hours = self.get_days_hours(int(delta_temp / 3600), 0, 0)
				# 			actual_delay = "{0} Days {1} Hours ".format(day, hours)

				final_data.append({
					'sticker':vehicle.taq_number,
					'driver_name':str(driver_name),
					'driver_code':str(driver_code),
					'trip_creator':vehicle.trip_id.create_uid.display_name,
					'driver_mobile_phone': vehicle.trip_id.driver_mobile_phone,
					'trip_type': vehicle.trip_id.trip_type,
					'total_cars': vehicle.trip_id.total_cars,
					'current_branch': vehicle.current_branch_id.branch_ar_name,
					'trailer_cat':vehicle.vehicle_type.vehicle_type_name,
					'vehicle_state':vech_state,
					'start_point':start_point,
					'end_point':end_point,
					'start_time':start_time,
					'act_end_time':act_end_time,
					'end_time':end_time,
					'trip_state':trip_state,
					'curr_desti':curr_desti,
					'curr_arrival':curr_arrival,
					'trip_name':vehicle.trip_id.name,
					'trip_dis':vehicle.trip_id.trip_distance,
					'trip_extra_dis':vehicle.trip_id.extra_distance,
					'trip_total_fuel':vehicle.trip_id.total_fuel_amount,
					'trip_load':vehicle.trip_id.truck_load,
					})

		if report_type == 'trip':

			domain = []
			# if form:
			# 	domain.append(('expected_start_date','>=',form))
			# if to:
			# 	domain.append(('expected_start_date','<=',to))
			# if vehicle_type:
			# 	domain.append(('vehicle_id.vehicle_type.id','in',vehicle_type.ids))
			# if fleet_id:
			# 	domain.append(('vehicle_id.id','in',fleet_id.ids))
			# if driver_code:
			# 	domain.append(('driver_id.id','in',driver_code.ids))
			# if branch_from:
			# 	domain.append(('from_route_branch_id.id','in',branch_from.ids))
			if filter_date_by == 'scheduled_start_date':
				if sa_date_condition == 'is_equal_to':
					domain.append(('expected_start_date', '=', date))
				if sa_date_condition == 'is_not_equal_to':
					domain.append(('expected_start_date', '!=', date))
				if sa_date_condition == 'is_after':
					domain.append(('expected_start_date', '>', date))
				if sa_date_condition == 'is_before':
					domain.append(('expected_start_date', '<', date))
				if sa_date_condition == 'is_after_or_equal_to':
					domain.append(('expected_start_date', '>=', date))
				if sa_date_condition == 'is_before_or_equal_to':
					domain.append(('expected_start_date', '<=', date))
				if sa_date_condition == 'is_between':
					domain.append(('expected_start_date', '>', form))
					domain.append(('expected_start_date', '<', to))
				if sa_date_condition == 'is_set':
					domain.append(('expected_start_date', '!=', None))
				if sa_date_condition == 'is_not_set':
					domain.append(('expected_start_date', '=', None))
			if filter_date_by == 'scheduled_end_date':
				if sa_date_condition == 'is_equal_to':
					domain.append(('expected_end_date', '=', date))
				if sa_date_condition == 'is_not_equal_to':
					domain.append(('expected_end_date', '!=', date))
				if sa_date_condition == 'is_after':
					domain.append(('expected_end_date', '>', date))
				if sa_date_condition == 'is_before':
					domain.append(('expected_end_date', '<', date))
				if sa_date_condition == 'is_after_or_equal_to':
					domain.append(('expected_end_date', '>=', date))
				if sa_date_condition == 'is_before_or_equal_to':
					domain.append(('expected_end_date', '<=', date))
				if sa_date_condition == 'is_between':
					domain.append(('expected_end_date', '>', form))
					domain.append(('expected_end_date', '<', to))
				if sa_date_condition == 'is_set':
					domain.append(('expected_end_date', '!=', None))
				if sa_date_condition == 'is_not_set':
					domain.append(('expected_end_date', '=', None))
			if filter_date_by == 'actual_start_date':
				if sa_date_condition == 'is_equal_to':
					domain.append(('actual_start_datetime', '=', date))
				if sa_date_condition == 'is_not_equal_to':
					domain.append(('actual_start_datetime', '!=', date))
				if sa_date_condition == 'is_after':
					domain.append(('actual_start_datetime', '>', date))
				if sa_date_condition == 'is_before':
					domain.append(('actual_start_datetime', '<', date))
				if sa_date_condition == 'is_after_or_equal_to':
					domain.append(('actual_start_datetime', '>=', date))
				if sa_date_condition == 'is_before_or_equal_to':
					domain.append(('actual_start_datetime', '<=', date))
				if sa_date_condition == 'is_between':
					domain.append(('actual_start_datetime', '>', form))
					domain.append(('actual_start_datetime', '<', to))
				if sa_date_condition == 'is_set':
					domain.append(('actual_start_datetime', '!=', None))
				if sa_date_condition == 'is_not_set':
					domain.append(('actual_start_datetime', '=', None))
			if filter_date_by == 'actual_end_date':
				if sa_date_condition == 'is_equal_to':
					domain.append(('actual_end_datetime', '=', date))
				if sa_date_condition == 'is_not_equal_to':
					domain.append(('actual_end_datetime', '!=', date))
				if sa_date_condition == 'is_after':
					domain.append(('actual_end_datetime', '>', date))
				if sa_date_condition == 'is_before':
					domain.append(('actual_end_datetime', '<', date))
				if sa_date_condition == 'is_after_or_equal_to':
					domain.append(('actual_end_datetime', '>=', date))
				if sa_date_condition == 'is_before_or_equal_to':
					domain.append(('actual_end_datetime', '<=', date))
				if sa_date_condition == 'is_between':
					domain.append(('actual_end_datetime', '>', form))
					domain.append(('actual_end_datetime', '<', to))
				if sa_date_condition == 'is_set':
					domain.append(('actual_end_datetime', '!=', None))
				if sa_date_condition == 'is_not_set':
					domain.append(('actual_end_datetime', '=', None))
			if vehicle_type:
				domain.append(('vehicle_type.id', 'in', vehicle_type.ids))
			if fleet_id:
				domain.append(('id', 'in', fleet_id.ids))
			if driver_code:
				domain.append(('bsg_driver.id', 'in', driver_code.ids))
			if branch_from:
				domain.append(('start_branch.id', 'in', branch_from.ids))
			if user_id:
				domain.append(('create_uid', '=', wiz_obj.user_id.id))
			if trip_status:
				domain.append(('trip_id.state', '=', trip_status))
			if truck_load:
				domain.append(('trip_id.display_truck_load', '=', truck_load))
			# if car_load:
			# 	worksheet.write(row, col, 'Car Load', main_heading1)
			# 	worksheet.write_string(row, col + 1, wiz_obj.car_load, main_data)
			# 	row += 1
			# if vehicle_group_id:
			# 	worksheet.write(row, col, 'Vehicle Group Name', main_heading1)
			# 	worksheet.write_string(row, col + 1, wiz_obj.vehicle_group_id.display_name, main_data)
			# 	row += 1
			# 	domain.append(('', '=', vehicle_group_id))
			if fuel_expense_type_id:
				domain.append(('trip_id.display_expense_mthod_id', '=', fuel_expense_type_id.id))

			if wiz_obj.trailer_sticker_no:
				domain.append(('trailer_id', '=', wiz_obj.trailer_sticker_no.id))

			if wiz_obj.license_plate_no:
				domain.append(('license_plate', '=', wiz_obj.license_plate_no))

			if wiz_obj.vehicle_state_id:
				domain.append(('vehicle_id.state_id', '=', wiz_obj.vehicle_state_id.id))

			if wiz_obj.driver_link == "linked":
				domain.append(('bsg_driver', '!=', None))
			if wiz_obj.driver_link == "unlinked":
				domain.append(('bsg_driver', '=', False))

			if branch_to:
				trips = []
				trips_rec = self.env['fleet.vehicle.trip'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(domain, order='expected_start_date')
				for t in trips_rec:
					arrival_point = self.env['fleet.trip.arrival'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('trip_id.id','=',t.id)])
					if arrival_point:
						end_arrival_to = arrival_point[-1]
						if end_arrival_to.waypoint_to.id in branch_to.ids:
							trips.append(t)

			if not branch_to:
				trips = self.env['fleet.vehicle.trip'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(domain, order='expected_start_date')

			for x in trips:
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


					# start_time = x.expected_start_date
					# act_end_time = start_arrival.trip_id.expected_end_date
					# end_time = end_arrival.actual_end_time

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
						end_time = " "


					# if start_arrival.actual_start_time >= form and end_time <= to:

					vech_state = ""
					start_point = ""
					end_point = ""
					trip_state = ""
					driver_code = x.vehicle_id.bsg_driver.driver_code
					driver_name = x.vehicle_id.bsg_driver.name

					trips_point = self.env['fleet.vehicle.trip.waypoints'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('bsg_fleet_trip_id.id','=',x.id)])
					if trips_point:
						start_trip = trips_point[0]
						end_trip = trips_point[-1]

						start_point = start_trip.waypoint.loc_branch_id.branch_ar_name
						end_point = end_trip.waypoint.loc_branch_id.branch_ar_name


					if x.vehicle_id.state_id.name == 'Linked':
						vech_state =  "مرتبطة بمقطورة"
					elif x.vehicle_id.state_id.name == 'Unlinked':
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

					final_data.append({
						'sticker':x.vehicle_id.taq_number,
						'driver_name':str(driver_name),
						'driver_code':str(driver_code),
						'trip_creator': x.create_uid.display_name,
						'driver_mobile_phone': x.driver_mobile_phone,
						'trip_type': x.trip_type,
						'total_cars': x.total_cars,
						'current_branch': x.vehicle_id.current_branch_id.branch_ar_name,
						'trailer_cat':x.vehicle_id.vehicle_type.vehicle_type_name,
						'vehicle_state':vech_state,
						'start_point':start_point,
						'end_point':end_point,
						'start_time':start_time,
						'act_end_time':act_end_time,
						'end_time':end_time,
						'trip_state':trip_state,
						'curr_desti':curr_desti,
						'curr_arrival':curr_arrival,
						'trip_name':x.name,
						'trip_dis':x.trip_distance,
						'trip_extra_dis':x.extra_distance,
						'trip_total_fuel':x.total_fuel_amount,
						'trip_load':x.truck_load,
						})

			
		return {
			'doc_ids': docids,
			'doc_model':'fleet.vehicle',
			'form': form,
			'to': to,
			'head': head,
			'print_by':self.env.user.display_name,
			'print_date':print_date,
			'final_data': final_data,
		}

		# return report_obj.render('partner_ledger_sugar.partner_ledger_report', docargs)