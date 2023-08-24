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
from datetime import timedelta,datetime,date
import base64
import re



class ReportBxAgreement(models.AbstractModel):
	_name = 'report.bx_agreement_report.bx_agreement_report_temp'
	_description = "Report"

	@api.model
	def _get_report_values(self, docids, data=None):
		docs = self.env['transport.management'].browse(docids)

		user_data = self.env['hr.employee'].search([('user_id.id','=',docs.create_uid.id)],limit=1)
		user_code = user_data.driver_code

		voucher_amt = 0
		voucher_num = ""
		for vouc in docs.invoice_id.payment_ids:
			voucher_amt = voucher_amt + vouc.amount
			voucher_num = voucher_num +' '+str(vouc.number)

		actual_time = datetime.now() + timedelta(hours=3)
		am_pm = str(actual_time)[11:13]
		actual_time = str(actual_time)[:16]
		actual_time = datetime.strptime(actual_time, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %I:%M')
		if int(am_pm) > 12:
			actual_time = actual_time +' '+'PM'
		if int(am_pm) <= 12:
			actual_time = actual_time +' '+'AM'
			

		return {
		'doc_ids': docids,
		'doc_model':'transport.management',
		'data': data,
		'docs': docs,
		'user_code': user_code,
		'voucher_amt': voucher_amt,
		'voucher_num': voucher_num,
		'actual_time': actual_time,
		
	}


