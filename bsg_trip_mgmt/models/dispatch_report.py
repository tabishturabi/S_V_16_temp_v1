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
from odoo import api, models, _
from odoo.exceptions import ValidationError
from num2words import num2words
import base64
import re

class ReportmonthDispatchReport(models.AbstractModel):
	_name = 'report.bsg_trip_mgmt.report_dispatch_template'
	_description = "Report"

	@api.model
	def _get_report_values(self, docids, data=None):
		docs = self.env['fleet.vehicle.trip'].browse(docids)
		#for rec in docs:
		#	if (rec.trip_type == 'local' and rec.state  not in ['done','finished']) or rec.state in ['draft', 'confirmed','cancelled'] :
		#		return {
		#			'doc_ids': docids,
		#			'docs': docs,
		#			'vir_docs' : docs,
		#			'vir_report' : 1,
		#			'doc_model':'fleet.vehicle.trip',
		#			'message' : _("Not allowed to print Dispatch report for this trips")
		#			}

		lines_data = []
		lines_data_cre = []
		virtual_data = []
		for x in docs:
			for y in x.stock_picking_id:
				if y.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.payment_method.payment_type == 'credit':
					result_cre = ""
					if y.picking_name:
						if y.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.customer_type == 'individual':
							result_cre = str(y.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.customer.id)+'/'+str(y.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.payment_method.id)+'/'+str(y.loc_from.id)+'/'+str(y.loc_to.id)
						else:
							result_cre = str(y.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.cooperate_customer.id)+'/'+str(y.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.payment_method.id)+'/'+str(y.loc_from.id)+'/'+str(y.loc_to.id)
						if result_cre not in lines_data:
							lines_data.append(result_cre)
							virtual_data.append(y)
				else:
					result = ""
					if y.picking_name:
						result = str(y.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.payment_method.id)+'/'+str(y.loc_from.id)+'/'+str(y.loc_to.id)

						if result not in lines_data:
							lines_data.append(result)
							virtual_data.append(y)


		vir_docs = []
		vir_report = 0
		if len(virtual_data) < 1:
			vir_report = 1
			vir_docs = docs


		active_rec = []
		def get_records(attr,attr1,attr2,attr3,attr4):
			del active_rec[:]
			for j in docs:
				for k in j.stock_picking_id:
					if k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.payment_method.payment_type == 'credit':
						if k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.customer_type == 'individual':
							if int(attr) == k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.customer.id and int(attr1) == k.loc_from.id and int(attr2) == k.loc_to.id and int(attr3) == k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.payment_method.id:
									active_rec.append(k)
						else:
							if int(attr4) == k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.cooperate_customer.id and int(attr1) == k.loc_from.id and int(attr2) == k.loc_to.id and int(attr3) == k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.payment_method.id:
									active_rec.append(k)
					else:
						if int(attr1) == k.loc_from.id and int(attr2) == k.loc_to.id and int(attr3) == k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.payment_method.id:
								active_rec.append(k)


		check_drop_loc = 0
		active_rec_drops = []
		def get_records_drop(attr,attr1,attr2,attr3,attr4):
			del active_rec_drops[:]
			check_drop_loc = 0
			for j in docs:
				for k in j.stock_picking_id:
					if k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.payment_method.payment_type == 'credit':
						if k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.customer_type == 'individual':
							if int(attr) == k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.customer.id and int(attr1) == k.loc_from.id and int(attr2) == k.loc_to.id and int(attr3) == k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.payment_method.id:
									active_rec_drops.append(k)
						else:
							if int(attr4) == k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.cooperate_customer.id and int(attr1) == k.loc_from.id and int(attr2) == k.loc_to.id and int(attr3) == k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.payment_method.id:
									active_rec_drops.append(k)
					else:
						if int(attr1) == k.loc_from.id and int(attr2) == k.loc_to.id and int(attr3) == k.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_cargo_sale_id.payment_method.id:
								active_rec_drops.append(k)

			if active_rec_drops:
				for check in active_rec_drops:
					if check.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).loc_to.id != check.picking_name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).drop_loc.id:
						check_drop_loc = 1
					else:
						pass

			return check_drop_loc



		def get_time(to):
			for d in docs:
				for e in d.route_id.waypoint_to_ids:
					if e.waypoint.id == to:
						return e.estimated_time

		users = self.env['res.users'].search([('id','=',self._uid)])
		current_user = users.name
		tot_page = len(virtual_data)

		def get_place(attr):
			place = self.env['fleet.vehicle.log.contract'].search([('vehicle_id.id','=',attr)],limit=1)
			if place:
				return place.ins_ref

		def get_date(attr):
			dated = self.env['fleet.vehicle.log.contract'].search([('vehicle_id.id','=',attr)],limit=1)
			if dated:
				return dated.expiration_date
		def get_istam(attr):
			dated = self.env['fleet.vehicle.log.contract'].search([('vehicle_id.id','=',attr)],limit=1)
			if dated:
				return dated.ishtimara_no

		
		return {
		'doc_ids': docids,
		'doc_model':'fleet.vehicle.trip',
		'data': data,
		'docs': docs,
		'lines_data': lines_data,
		'get_time': get_time,
		'virtual_data': virtual_data,
		'active_rec': active_rec,
		'get_records': get_records,
		'get_records_drop': get_records_drop,
		'current_user': current_user,
		'get_place': get_place,
		'get_date': get_date,
		'tot_page': tot_page,
		'get_istam': get_istam,
		'vir_docs': vir_docs,
		'vir_report': vir_report,
		'message' : False,
		'current_company_id' : self.env.user.company_id,
		# 'check_drop_loc': check_drop_loc,
	}

