#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, models
from num2words import num2words
import base64
import re


class inspectionReportPdf(models.AbstractModel):
	_name = 'report.bsg_cargo_sale.report_inspection_template_call'
	_description = "Report"

	@api.model
	def _get_report_values(self, docids, data=None):
		docs = self.env['bsg_vehicle_cargo_sale_line'].browse(docids)

		print('kashifffffffffffffff: ', docs.bsg_cargo_sale_id)
		print('Raiiiiiiiiiiiiiii: ', docs.bsg_cargo_sale_id.name)

		pictures_data = {
			'top': False,
			'bottom': False,
			'left': False,
			'right': False,
			'car_image': False,
		}
		if docs:
			inspection_id = self.env['bassami.inspection'].search(
				[('cargo_sale_line_id', '=', docs.id)], limit=1)

			print("cargo line id ", docs.sale_line_rec_name)
			print("inspection id", inspection_id.cargo_sale_line_id)

			if len(inspection_id) == 1:
				if inspection_id.attachment_top_binary != None:
					pictures_data['top'] = inspection_id.attachment_top_binary
				if inspection_id.attachment_bottom_id_binary != None:
					pictures_data['bottom'] = inspection_id.attachment_bottom_id_binary
				if inspection_id.attachment_left_binary != None:
					pictures_data['left'] = inspection_id.attachment_left_binary
				if inspection_id.attachment_right_binary != None:
					pictures_data['right'] = inspection_id.attachment_right_binary
				if inspection_id.attachment_car_image_binary != None:
					pictures_data['car_image'] = inspection_id.attachment_car_image_binary

		lang_id = 0
		user_id = self.env['res.users'].search([('id', '=', self._uid)])
		if user_id.lang != 'en_US':
			lang_id = 1

		if docs.bsg_cargo_sale_id:
			cargo_id = docs.bsg_cargo_sale_id
			from_loc = docs.bsg_cargo_sale_id.loc_from.route_waypoint_name
			to_loc = docs.bsg_cargo_sale_id.loc_to.route_waypoint_name
		else:
			cargo_id = docs.bsg_cargo_return_sale_id
			from_loc = docs.bsg_cargo_return_sale_id.return_loc_from.route_waypoint_name
			to_loc = docs.bsg_cargo_return_sale_id.return_loc_to.route_waypoint_name

		other_service = " "
		local_service = " "
		other_service_check = 0
		if docs.bsg_cargo_sale_id.other_service_line_ids:
			other_service_check = 1
			for serv in docs.bsg_cargo_sale_id.other_service_line_ids:
				if other_service == " ":
					if docs.bsg_cargo_sale_id.loc_from.loc_branch_id.branch_operation == 'international' and docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id:
						answer = round(((
													serv.cost + serv.tax_amount) /(docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate > 0 and docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate or 1)),
									   2)
						other_service = str(answer) + ' SR ' + str(serv.product_id.name)
						local_service = str(serv.cost + serv.tax_amount) + ' ' + str(
							docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.symbol)
					else:
						other_service = str(str(serv.product_id.name) + ' ' + str(serv.cost + serv.tax_amount))
				else:
					answer = round(((
												serv.cost + serv.tax_amount) /(docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate > 0 and docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate or 1)),
								   2)
					other_service = other_service + ' , ' + str(answer) + ' SR ' + str(serv.product_id.name)
					local_service = local_service + ' , ' + str(serv.cost + serv.tax_amount) + ' ' + str(
						docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.symbol)

		international_sale = " "
		international_sale_unit = " "
		local_sale = " "
		local_sale_unit = " "
		international_sale_check = 0
		if docs.bsg_cargo_sale_id.loc_from.loc_branch_id.branch_operation == 'international' and docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id:
			international_sale_check = 1
			international_sale_unit = str(docs.unit_charge) + ' ' + str(
				docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.symbol)
			international_sale = str(docs.charges) + ' ' + str(
				docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.symbol)
			answer_1 = round(((docs.charges) / (docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate > 0 and docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate or 1)), 2)
			local_sale = str(answer_1) + ' SR'
			answer_2 = round(((docs.unit_charge) /(docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate > 0 and docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate or 1)), 2)
			local_sale_unit = str(answer_2) + ' SR'

		return {
			'doc_ids': docids,
			'doc_model': 'bsg_vehicle_cargo_sale_line',
			'docs': docs,
			'lang_id': lang_id,
			'cargo_id': cargo_id,
			'from_loc': from_loc,
			'to_loc': to_loc,
			'other_service': other_service,
			'other_service_check': other_service_check,
			'international_sale': international_sale,
			'international_sale_unit': international_sale_unit,
			'international_sale_check': international_sale_check,
			'local_sale': local_sale,
			'local_sale_unit': local_sale_unit,
			'local_service': local_service,
			'image_cargo': pictures_data,
		}


class ShipmentReportPdf(models.AbstractModel):
	_name = 'report.bsg_cargo_sale.report_shipment_template_call'
	_description = "Report"

	@api.model
	def _get_report_values(self, docids, data=None):
		docs = self.env['bsg_vehicle_cargo_sale_line'].browse(docids)

	
		lang_id = 0
		user_id = self.env['res.users'].search([('id','=',self._uid)])
		if user_id.lang != 'en_US':
			lang_id = 1

		if docs.bsg_cargo_sale_id:
			cargo_id = docs.bsg_cargo_sale_id
			from_loc = docs.bsg_cargo_sale_id.loc_from.route_waypoint_name
			to_loc = docs.bsg_cargo_sale_id.loc_to.route_waypoint_name
		else:
			cargo_id = docs.bsg_cargo_return_sale_id
			from_loc = docs.bsg_cargo_return_sale_id.return_loc_from.route_waypoint_name
			to_loc = docs.bsg_cargo_return_sale_id.return_loc_to.route_waypoint_name

		other_service = " "
		local_service = " "
		other_service_check = 0
		if docs.bsg_cargo_sale_id.other_service_line_ids:
			other_service_check = 1
			for serv in docs.bsg_cargo_sale_id.other_service_line_ids:
				if other_service == " ":
					if docs.bsg_cargo_sale_id.loc_from.loc_branch_id.branch_operation == 'international' and docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id:
						answer = round(((serv.cost+serv.tax_amount)/(docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate > 0 and docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate or 1)), 2)
						other_service = str(answer) + ' SR ' + str(serv.product_id.name)
						local_service = str(serv.cost+serv.tax_amount)+' '+ str(docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.symbol)
					else:
						other_service = str(str(serv.product_id.name)+' '+str(serv.cost+serv.tax_amount))  
				else:
					answer = round(((serv.cost+serv.tax_amount)/(docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate > 0 and docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate or 1)), 2)
					other_service = other_service +' , '+str(answer)+ ' SR ' + str(serv.product_id.name)
					local_service = local_service +' , '+str(serv.cost+serv.tax_amount)+' '+ str(docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.symbol)



		international_sale = " "
		international_sale_unit = " "
		local_sale = " "
		local_sale_unit = " "
		international_sale_check = 0
		if docs.bsg_cargo_sale_id.loc_from.loc_branch_id.branch_operation == 'international' and docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id:
			international_sale_check = 1
			international_sale_unit = str(docs.unit_charge) + ' ' + str(
				docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.symbol)
			international_sale = str(docs.charges)+' '+ str(docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.symbol)
			answer_1 = round(((docs.charges)/(docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate > 0 and docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate or 1)), 2)
			local_sale = str(answer_1) + ' SR' 
			answer_2 = round(((docs.unit_charge) / (docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate > 0 and docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate or 1)), 2)
			local_sale_unit = str(answer_2) + ' SR'



		return {
		'doc_ids': docids,
		'doc_model':'bsg_vehicle_cargo_sale_line',
		'docs': docs,
		'lang_id': lang_id,
		'cargo_id': cargo_id,
		'from_loc': from_loc,
		'to_loc': to_loc,
		'other_service': other_service,
		'other_service_check': other_service_check,
		'international_sale': international_sale,
		'international_sale_unit':international_sale_unit,
		'international_sale_check': international_sale_check,
		'local_sale': local_sale,
		'local_sale_unit':local_sale_unit,
		'local_service': local_service,
	}