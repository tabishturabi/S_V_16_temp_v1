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

class VoucherHistoryReport(models.AbstractModel):
	_name = 'report.vouchers_history_report.vouchers_history_temp_id'

	@api.model
	def _get_report_values(self, docids, data=None):
		model = self.env.context.get('active_model')
		record_wizard = self.env[model].browse(self.env.context.get('active_id'))

		
		form = record_wizard.form
		to = record_wizard.to
		branch_ids = record_wizard.branch_ids
		report_type = record_wizard.report_type
		branch_filter = record_wizard.branch_filter
		head = "Voucher History Report"

		branch_id = []
		for rec in branch_ids:
			branch_id.append(rec.id)

		if branch_filter == 'specific':
			if report_type == 'all':
				types = "All Voucher"
				records = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('branch_ids.id','in',branch_id)])

			if report_type == 'rec':
				types = "Receipt Voucher"
				records = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('branch_ids.id','in',branch_id),('payment_type','=','inbound')])

			if report_type == 'pay':
				types = "Payment Voucher"
				records = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('branch_ids.id','in',branch_id),('payment_type','=','outbound')])

			if report_type == 'trans':
				types = "Internal Transfer"
				records = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('branch_ids.id','in',branch_id),('is_internal_transfer','=',True),])


		if branch_filter == 'all':
			if report_type == 'all':
				types = "All Voucher"
				records = self.env['account.payment'].search([('date','>=',form),('date','<=',to)])

			if report_type == 'rec':
				types = "Receipt Voucher"
				records = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('payment_type','=','inbound')])

			if report_type == 'pay':
				types = "Payment Voucher"
				records = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('payment_type','=','outbound')])

			if report_type == 'trans':
				types = "Internal Transfer"
				records = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('is_internal_transfer','=',True),])


		all_data = []
		if records:
			for rec in records:
				create_date = rec.create_date + timedelta(hours=3)
				history = 'Created : '+ str(create_date)
				for mess in rec.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).message_ids:
					new_message = ""
					for track in mess.tracking_value_ids:
						if track.field == 'state':
							timed = mess.date + timedelta(hours=3)
							new_message = 'User : '+ str(mess.author_id.name) +' , '+ "Time : " + str(timed) +' , '+'Message : '+ str(track.old_value_char)+' --> '+ str(track.new_value_char)
							if history:
								history = history + ' / '+new_message
							else:
								history = new_message


			
				all_data.append({
					'date':rec.date,
					'name':rec.name,
					'partner':rec.partner_id.name,
					'amount':rec.amount,
					'history':history,
				})


			

		
		return {
			'doc_ids': docids,
			'doc_model':'account.payment',
			'form': form,
			'to': to,
			'head': head,
			'types': types,
			'records': records,
			'all_data': all_data,
		}