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


class ReportCustomerInvoice(models.AbstractModel):
	_name = 'report.bassami_customer_invoices.customer_invoice_report_temp'
	_description = "Report"

	@api.model
	def _get_report_values(self, docids, data=None):
		docs = self.env['account.move'].browse(docids)

		lang_id = 0
		user_id = self.env['res.users'].search([('id','=',self._uid)])
		if user_id.lang != 'en_US':
			lang_id = 1

		type_id = 0
		if docs.move_type == 'in_invoice':
			type_id = 1
		

		return {
		'doc_ids': docids,
		'doc_model':'account.move',
		'data': data,
		'docs': docs,
		'lang_id': lang_id,
		'type_id': type_id,
		
	}


