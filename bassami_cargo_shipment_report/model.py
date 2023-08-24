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
import re
class BranchesLedgerReport(models.AbstractModel):
	_name = 'report.bassami_cargo_shipment_report.cargo_shipment_report'


	

	@api.model
	def _get_report_values(self, docids, data=None):
		model = self.env.context.get('active_model')
		record_wizard = self.env[model].browse(self.env.context.get('active_id'))

		
		form = record_wizard.form
		to = record_wizard.to
		loc_from = record_wizard.loc_from
		loc_to = record_wizard.loc_to
		customer_id = record_wizard.customer_id
		payment_method_ids = record_wizard.payment_method_ids
		cc_invoice = record_wizard.cc_invoice
		invoice_status = record_wizard.invoice_status
		report_type = record_wizard.report_type
		cargo_sale_type = record_wizard.cargo_sale_type
		create_uid = record_wizard.user_id
		partner_type_ids = []
		# sale_line_state_ids = record_wizard.sale_line_state_ids
		state = record_wizard.state
		# partner_type_ids = self.env['partner.type']search([('is_custoemer','=', True),('is_dealer', '=', True)])
		report_num = 0

		credit_rec = 0
		credit_amt = 0
		credit_amt_without_tax = 0
		credit_amt_with_tax = 0
		cash_rec = 0
		cash_amt_without_tax = 0
		cash_amt_with_tax = 0
		on_delivery_rec = 0
		on_delivery_amt = 0
		on_delivery_amt_without_tax = 0
		on_delivery_amt_with_tax = 0
		lines_total_with_tax = 0
		lines_total_without_tax = 0
		revenue_total_cars = 0
		revenue_total_amount = 0
		grouped_by_date = {}
		posted_total_cars =0.0
		posted_total_revenue =0.0
		unposted_total_cars =0.0
		unposted_total_revenue =0.0
		total_number_of_cars = 0
		en_arbic_weekday= {
				'Friday': 'الجمعة',
				'Saturday':'السبت',
				'Sunday':'الأحد',
				'Monday':'الاثنين',
				'Tuesday':'الثلاثاء',
				'Wednesday':'الأربعاء',
				'Thursday': 'الخميس'
			}

		domain = [('order_date', '>=', form), ('order_date', '<=', to), ('state', 'not in', ['cancel']),('bsg_cargo_sale_id.state', 'not in', ['draft','cancel'])]
		if loc_from:
			domain.append(('loc_from','=',loc_from.id))
		if loc_to:
			domain.append(('loc_to','=',loc_to.id))
		if report_type == 'summary':
			if state == 'shipped':
				domain.append(('state','not in', ['draft','confirm', 'cancel']))
			elif state == 'unshipped':
				domain.append(('state','in', ['draft','confirm']))
			else:
				domain.append(('state','!=', 'cancel'))
			report_num = 2
			trans = self.env['bsg_vehicle_cargo_sale_line'].search(domain, order='order_date')
			if cargo_sale_type and trans:
				trans = trans.filtered(lambda tr: tr.bsg_cargo_sale_id.cargo_sale_type == cargo_sale_type)
			if payment_method_ids and trans:
				trans = trans.filtered(lambda tr: tr.payment_method.id in payment_method_ids.ids)

			if trans:
				cash_sale_ids = trans.filtered(lambda order: order.bsg_cargo_sale_id.payment_method.payment_type == 'cash')
				credit_sale_ids = trans.filtered(lambda order: order.bsg_cargo_sale_id.payment_method.payment_type == 'credit')
				on_delivery_sale_ids = trans.filtered(lambda order: order.bsg_cargo_sale_id.payment_method.payment_type == 'pod')
				cash_rec, cash_amt_without_tax,cash_amt_with_tax = len(cash_sale_ids), sum(cash_sale_ids.mapped('total_without_tax')),sum(cash_sale_ids.mapped('charges'))
				credit_rec, credit_amt_without_tax, credit_amt_with_tax = len(credit_sale_ids), sum(credit_sale_ids.mapped('total_without_tax')), sum(credit_sale_ids.mapped('charges'))
				on_delivery_rec, on_delivery_amt_without_tax, on_delivery_amt_with_tax = len(on_delivery_sale_ids), sum(on_delivery_sale_ids.mapped('total_without_tax')), sum(on_delivery_sale_ids.mapped('charges'))

		if report_type == 'detail':
			if create_uid:
				domain.append(('create_uid', '=', create_uid.id))
			if state == 'shipped':
				domain.append(('state','not in', ['draft','confirm', 'cancel']))
			elif state == 'unshipped':
				domain.append(('state','in', ['draft','confirm']))
			else:
				domain.append(('state','!=', 'cancel'))
			report_num = 1
			domain = customer_id and domain.append(('customer_id','=', customer_id.id)) or domain
			domain = cc_invoice and domain.append(('add_to_cc', '=', cc_invoice == 'invoiced' and True or False)) or domain
			trans = self.env['bsg_vehicle_cargo_sale_line'].search(domain, order='order_date')
			trans = trans.filtered(lambda line: line.cargo_sale_state != 'draft')
			if cargo_sale_type:
				trans = trans.filtered(lambda line: line.bsg_cargo_sale_id.cargo_sale_type == cargo_sale_type)
			if payment_method_ids:
				trans = trans.filtered(lambda line: line.payment_method.id in payment_method_ids.ids)
			if invoice_status:
				if invoice_status == 'paid':
					trans = trans.filtered(lambda line: line.invoie_state == 'paid')
				else:
					trans = trans.filtered(lambda line: line.invoie_state != 'paid')
			if trans:
				lines_total_with_tax = sum(trans.mapped('charges'))
				lines_total_without_tax = sum(trans.mapped('total_without_tax'))
			total_number_of_cars = len(trans)

		if report_type == 'revenue':
			report_num = 3
			# domain.append(('cargo_sale_state','not in', ['draft', 'cancel']))
			# domain.append(('state', '!=', 'cancel'))
			# domain.append(('shipment_type','not in',[2,10,32,33]))
			domain = customer_id and domain.append(('customer_id','=', customer_id.id)) or domain
			domain = cc_invoice and domain.append(('add_to_cc', '=', cc_invoice == 'invoiced' and True or False)) or domain
			trans = self.env['bsg_vehicle_cargo_sale_line'].search(domain, order='order_date_date')
			if cargo_sale_type:
				trans = trans.filtered(lambda line: line.bsg_cargo_sale_id.cargo_sale_type == cargo_sale_type)
			if payment_method_ids:
				trans = trans.filtered(lambda line: line.payment_method.id in payment_method_ids.ids)
			mapped_date = trans.mapped('order_date_date')
			date_list = sorted(set(mapped_date), key=mapped_date.index)
			grouped_by_date = {}
			trans = trans.filtered(lambda tr: tr.state != 'cancel' and not re.match('\*',tr.sale_line_rec_name))
			for date in date_list:
				order_lines = trans.filtered(lambda line: line.order_date_date == date)
				posted_lines = order_lines.filtered(lambda ln: ln.state != 'draft')
				unposted_lines = order_lines.filtered(lambda l: l.state == 'draft')
				# posted_lines = order_lines.filtered(lambda ln: ln.fleet_trip_id and ln.fleet_trip_id.trip_type != 'local')
				# unposted_lines = order_lines.filtered(lambda l: not l.fleet_trip_id and l.state != 'cancel' and not re.match('\*',l.sale_line_rec_name))
				# grouped_by_partner_type = {}
				# for partner_type_id in partner_type_ids:
				# 	lines = order_lines.filtered(lambda line: line.bsg_cargo_sale_id.partner_types.id == partner_type_id.id)
				# 	grouped_by_partner_type[partner_type_id.name] = {
				# 		'total_day_no_cars': len(lines),
				# 		'total_day_revenue': lines and sum(lines.mapped('total_without_tax')) or 0.0
				# 	}

				# 'grouped_by_partner_type': grouped_by_partner_type,
				date_key = en_arbic_weekday[date.strftime('%A',)]+date.strftime(', %d-%m-%Y',)
				unposted_no_cars = len(unposted_lines)
				unposted_day_renenue = unposted_lines and sum(unposted_lines.mapped('total_without_tax')) or 0.0
				posted_no_cars = len(posted_lines)
				posted_day_renenue = posted_lines and sum(posted_lines.mapped('total_without_tax')) or 0.0
				posted_total_cars+=posted_no_cars
				posted_total_revenue+=posted_day_renenue
				unposted_total_cars += unposted_no_cars
				unposted_total_revenue += unposted_day_renenue
				grouped_by_date[date_key] = {
					'unposted_no_cars': unposted_no_cars,
					'unposted_day_renenue': unposted_day_renenue,
					'posted_no_cars': posted_no_cars,
					'posted_day_renenue': posted_day_renenue,
					'total_day_no_cars': len(order_lines),
					'total_day_revenue': sum(order_lines.mapped('total_without_tax'))
					}


			revenue_total_cars = len(trans)
			revenue_total_amount = sum(trans.mapped('total_without_tax'))

				# order_lines = trans.filtered(lambda line: line.order_date_date = date)
				# lines_1 =  order_lines.filtered(lambda line: line.bsg_cargo_sale_id.partner_types.id = 1)
				# lines_2 =  order_lines.filtered(lambda line: line.bsg_cargo_sale_id.partner_types.id = 2)
				# lines_3 =  order_lines.filtered(lambda line: line.bsg_cargo_sale_id.partner_types.id = 3)
				# lines_5 =  order_lines.filtered(lambda line: line.bsg_cargo_sale_id.partner_types.id = 5)
				# grouped_by_date[date] = {
				# 	'grouped_by_partner_type':{
				# 		'1': {
				# 			'no_cars':len(len(lines_1))
				# 			'revenue':sum(lines_1.mapped('total_without_tax'))
				# 		},
				# 		'2': {
				# 			'no_cars':len(len(lines_2))
				# 			'revenue':sum(lines_2.mapped('total_without_tax'))
				# 		}
				# 		'3': {
				# 			'no_cars':len(len(lines_3))
				# 			'revenue':sum(lines_3.mapped('total_without_tax'))
				# 		}
				# 		'5': {
				# 			'no_cars':len(len(lines_5)
				# 			'revenue':sum(lines_5.mapped('total_without_tax'))
				# 		}
				# 	},
				# 	'total_day_no_cars':len(order_lines),
				# 	'total_day_revenue':sum(order_lines.mapped('total_without_tax'))

				# }
					

			# if trans:
			# 	lines_total_with_tax = sum(trans.mapped('charges'))
			# 	lines_total_without_tax = sum(trans.mapped('total_without_tax'))
		return {
			'doc_ids': docids,
			'doc_model':'bsg_vehicle_cargo_sale',
			'form': en_arbic_weekday[form.date().strftime('%A',)]+form.date().strftime(', %d-%m-%Y',),
			'to': en_arbic_weekday[to.date().strftime('%A',)]+to.date().strftime(', %d-%m-%Y',),
			'loc_from': loc_from,
			'loc_to': loc_to,
			'payment_methods':payment_method_ids and ' / '.join([method.payment_method_name for method in payment_method_ids]) or False,
			'cargo_sale_type':dict(record_wizard._fields['cargo_sale_type'].selection).get(record_wizard.cargo_sale_type),
			'states': state and dict(record_wizard._fields['state'].selection).get(record_wizard.state) or 'All',
			'invoice_status':dict(record_wizard._fields['invoice_status'].selection).get(record_wizard.invoice_status),
			'credit_rec': credit_rec,
			'credit_amt_without_tax': credit_amt_without_tax,
			'credit_amt_with_tax': credit_amt_with_tax,
			'cash_rec': cash_rec,
			'cash_amt_without_tax': cash_amt_without_tax,
			'cash_amt_with_tax': cash_amt_with_tax,
			'on_delivery_rec': on_delivery_rec,
			'on_delivery_amt_without_tax': on_delivery_amt_without_tax,
			'on_delivery_amt_with_tax': on_delivery_amt_with_tax,
			'lines_total_without_tax': lines_total_without_tax,
			'lines_total_with_tax': lines_total_with_tax,
			'report_num': report_num,
			'trans': trans,
			'customer_id': customer_id,
			'grouped_by_date':grouped_by_date,
			'posted_total_cars':posted_total_cars,
			'posted_total_revenue': posted_total_revenue,
			'unposted_total_cars': unposted_total_cars,
			'unposted_total_revenue': unposted_total_revenue,
			'revenue_total_cars': revenue_total_cars,
			'revenue_total_amount': revenue_total_amount,
			'total_number_of_cars':total_number_of_cars,
			'en_arbic_weekday':en_arbic_weekday,
			# 'partner_type_ids':partner_type_ids

		}
