# -*- coding: utf-8 -*-

from odoo import models, fields, api

class VehiclePerformanceReport(models.AbstractModel):
	_name = 'report.bsg_trip_mgmt.vehicle_performance_report_template'
	_description = 'Vehicle Performace Report'
	
	
	@api.model
	def _get_report_values(self, docids, data=None):

		model = self.env.context.get('active_model')
		record_wizard = self.env[model].browse(self.env.context.get('active_id'))
		date_from = record_wizard.date_from
		date_to = record_wizard.date_to
		linked_vehicle_ids = self.env['fleet.vehicle'].search([('state_id.name','=', 'Linked'), ('company_id', '=', self.env.user.company_id.id)])
		all_trips_ids = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',date_from),('expected_start_date','<=',date_to),('vehicle_id', 'in', linked_vehicle_ids.ids)])
		# in_service_vehicles_count = len(linked_vehicle_ids)
		total_vehicles_in_service_count = 0
		total_trips_count = 0
		total_so_lines_count = 0
		total_revenue = 0
		total_distance = 0

		vehicle_type_ids = linked_vehicle_ids.mapped('vehicle_type')
		grouped_by_vehicle_type = {}
		for vehicle_type in vehicle_type_ids:
			vehicle_ids = linked_vehicle_ids.filtered(lambda v: v.vehicle_type.id == vehicle_type.id)
			vehicles_in_service_count = len(vehicle_ids)
			trip_ids = all_trips_ids.filtered(lambda tr: tr.vehicle_id.id in vehicle_ids.ids)
			tripes_count = len(trip_ids)
			stock_picking_ids = trip_ids.mapped('stock_picking_id')
			so_lines_count = len(stock_picking_ids)
			revenue = round(sum([line.picking_name.total_without_tax for line in stock_picking_ids]))
			distance = round(sum(trip_ids.mapped('trip_distance')))

			total_vehicles_in_service_count += vehicles_in_service_count
			total_trips_count += tripes_count
			total_so_lines_count += so_lines_count
			total_revenue += revenue
			total_distance += distance

			grouped_by_vehicle_type[vehicle_type.vehicle_type_name] = {
				'vehicles_in_service_count': vehicles_in_service_count,
				'tripes_count': tripes_count,
				'so_lines_count': so_lines_count,
				'revenue': revenue,
				'distance': distance
			}
		return {
			'doc_ids': docids,
			'doc_model':'fleet.vehicle.trip',
			'date_from': date_from,
			'date_to': date_to,
			'grouped_by_vehicle_type': grouped_by_vehicle_type,
			'total_vehicles_in_service_count':total_vehicles_in_service_count,
			'total_trips_count': total_trips_count,
			'total_distance': total_distance,
			'total_so_lines_count': total_so_lines_count,
			'total_revenue': total_revenue,
			


		}






class VehiclePerformanceReportWizard(models.TransientModel):
	_name = 'vehicle.performance.report.wizard'
	_description = "Vehicle Performace Report"
	
	date_from = fields.Date('Date From', required=True)
	date_to = fields.Date('Date To', required=True)
	
	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['date_from','date_to'])[0]
		return self._print_report(data)
		
		
	def _print_report(self, data):
		data['form'].update(self.read(['date_from','date_to'])[0])
		return self.env.ref('bsg_trip_mgmt.vehicle_performance_report').report_action(self, data=data)

