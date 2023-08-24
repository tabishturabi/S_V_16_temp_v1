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

class ShipmentReportDataPdf(models.AbstractModel):
	_name = 'report.bsg_cargo_sale.report_shipment_data_template_call'
	_description = "Report"

	@api.model
	def _get_report_values(self, docids, data=None):
		docs = self.env['bsg_vehicle_cargo_sale_line'].browse(docids)

		if docs.bsg_cargo_sale_id:
			cargo_id = docs.bsg_cargo_sale_id
			from_loc = docs.bsg_cargo_sale_id.loc_from.route_waypoint_name
			to_loc = docs.bsg_cargo_sale_id.loc_to.route_waypoint_name
		else:
			cargo_id = docs.bsg_cargo_return_sale_id
			from_loc = docs.bsg_cargo_return_sale_id.return_loc_from.route_waypoint_name
			to_loc = docs.bsg_cargo_return_sale_id.return_loc_to.route_waypoint_name

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
			answer_1 = round(((docs.charges) / docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate), 2)
			local_sale = str(answer_1) + ' SR'
			answer_2 = round(((docs.unit_charge) / docs.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.rate), 2)
			local_sale_unit = str(answer_2) + ' SR'

		return {
			'doc_ids': docids,
			'doc_model':'bsg_vehicle_cargo_sale_line',
			'docs': docs,
			'cargo_id': cargo_id,
			'from_loc': from_loc,
			'to_loc': to_loc,
			'international_sale_unit':international_sale_unit,
			'international_sale': international_sale,
			'international_sale_check': international_sale_check,
			'local_sale': local_sale,
			'local_sale_unit':local_sale_unit

		}


