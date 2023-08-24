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
from odoo import api, models ,_
from num2words import num2words
import base64
import re
from datetime import date
from datetime import date, timedelta
import datetime
from odoo.tools import float_round
from odoo.exceptions import UserError,ValidationError

class ReportmonthTripReport(models.AbstractModel):
	_name = 'report.bsg_trip_mgmt.report_arrival_template_call'
	_description = "Report"

	@api.model
	def _get_report_values(self, docids, data=None):
		docs = self.env['fleet.vehicle.trip'].browse(docids)
		for rec in docs:
			if (rec.trip_type == 'local' and rec.state != 'finished') or rec.state in ['draft', 'confirmed','cancelled'] :
				return {
					'doc_ids': docids,
					'docs': docs,
					'doc_model':'fleet.vehicle.trip',
					'message' : _("لايمكن طباعة مصروف الطريق إلا بعد بدء الرحلــه وفي حال كانت الرحلة خدمي لابد من عمل انهاء للرحلة")
					}	
		
		odoo_one = 0
		odoo_two = 0
		arrival_one = 0
		arrival_two = 0
		start_time = " "
		arrival_timed = " "
		for x in docs:
			for y in x.bsg_trip_arrival_ids:
				odoo_one = y.odoometer
				arrival_one = y.actual_start_time
				break
			for z in x.bsg_trip_arrival_ids:
				odoo_two = z.odoometer
				if z.actual_end_time:
					arrival_two = z.actual_end_time

		if arrival_two != 0 and arrival_one != 0:
			arrival_timed = arrival_two-arrival_one

		if arrival_one != 0:
			string_time = str(arrival_one)
			start_time = str(string_time[:10])

		def get_cars(ids):
			count = 0
			for x in docs:
				for y in x.stock_picking_id:
					if y.group_name == ids:
						count = count + 1

			return count

		def get_cars_lost():
			count = 0
			for lost in docs:
				for i in lost.bsg_trip_arrival_ids:
					for j in i.arrival_line_ids:
						if not j.parking_check:
							count = count + 1

			return count

		def get_so_amt(ids):
			count = 0
			for x in docs:
				for y in x.stock_picking_id:
					if y.id == ids:
						# y.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.shipment_type = 'oneway'
						if y.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.shipment_type == 'return':
							count = ((y.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.total_amount-y.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.tax_amount_total)) / 2
						else:
							count = (y.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.total_amount-y.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.tax_amount_total)

			return count


		users = self.env['res.users'].search([('id','=',self._uid)])
		current_user = users.name

		today = date.today()


		search_ids = self.env['account.payment'].search([('is_pay_trip_money','=',True),('fleet_trip_id','=',docs.id)],limit=1)

		fuel_expense = 0
		tax_ids = False 
		if search_ids:
			if search_ids.invoice_ids:
				tax_ids =  search_ids.invoice_ids[0].invoice_line_ids[0].invoice_line_tax_ids
		if not tax_ids:
			fule_product = self.env['product.product'].search([('is_fuel_expense','=',True)],limit=1)
			tax_ids = fule_product.supplier_taxes_id
		tax_amount = sum(tax_ids.mapped('amount'))
		# if docs.display_expense_type in ['km', 'hybrid']:
		# 	fuel_expense = docs.total_fuel_amount
		# else:
		fuel_expense = docs.total_fuel_amount
			
		rounding_config = self.env.user.company_id
		if rounding_config:
			cash_rounding_id = rounding_config.sudo().cash_rounding_id
			fuel_expense = float_round(fuel_expense, precision_rounding=cash_rounding_id.rounding, rounding_method=cash_rounding_id.rounding_method)
		else:
			fuel_expense =round(fuel_expense)
		
		# def get_po(attr):
		# 	amt = 0
		# 	po = self.env['purchase.order.line'].search([('product_id.id','=',attr),('order_id.state','=',('draft','sent'))])
		# 	for x in po:
		# 		amt = amt + x.product_qty
		# 	return amt



		return {
		'doc_ids': docids,
		'doc_model':'fleet.vehicle.trip',
		'data': data,
		'docs': docs,
		'odoo_one': odoo_one,
		'odoo_two': odoo_two,
		'arrival_timed': arrival_timed,
		'start_time': start_time,
		'get_cars': get_cars,
		'get_so_amt': get_so_amt,
		'current_user': current_user,
		'get_cars_lost': get_cars_lost,
		'today': today,
		'search_ids': search_ids,
		'fuel_expense': fuel_expense,
		'tax_amount': tax_amount,
		'message' : False,
	}


