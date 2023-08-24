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
from datetime import timedelta,datetime,date



class ReportPackageShipment(models.AbstractModel):
	_name = 'report.package_shipment_report.package_shipment_temp_id'
	_description = "Report"

	@api.model
	def _get_report_values(self, docids, data=None):
		docs = self.env['bsg_package_shipment'].browse(docids)

		def get_date(ids):
			order_date = " "
			if ids.order_date:
				order_date = ids.order_date + timedelta(hours=3)
				order_date = str(order_date)[:16]
				order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

			return order_date
	

		return {
		'doc_ids': docids,
		'doc_model':'bsg_package_shipment',
		'docs': docs,
		'get_date': get_date,
	}


