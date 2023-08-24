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

class voucherLedgerReport(models.AbstractModel):
	_name = 'report.bassami_vouchers_report.voucher_basami_report'

	@api.model
	def _get_report_values(self, docids, data=None):
		model = self.env.context.get('active_model')
		record_wizard = self.env[model].browse(self.env.context.get('active_id'))

		
		form = record_wizard.form
		to = record_wizard.to
		user_id = record_wizard.user_id
		report_type = record_wizard.report_type
		user_type = record_wizard.user_type
		state = record_wizard.state
		string_date = str(form)
		year = string_date[:4]
		head = ""
		rec_pays = []
		user_id = record_wizard.user_id
		journal_id = record_wizard.journal_id

		# check = 0
		# if report_type == 'rec' or report_type == 'pay' or report_type == 'all':
		# 	check = 1
		# if report_type == 'trans':
		# 	check = 2
		# 	head = "Transfer Voucher"


		branches = []
		branches_data = []
		if user_type == 'all':
			# branches = self.env['bsg_branches.bsg_branches'].search([])
			# for data in self.env['bsg_branches.bsg_branches'].search([]):
			# 	branches.append(data.id)
			# 	branches_data.append(data)

			branch_ids = []
			branches_data = []
			curr_users = self.env['res.users'].search([('id','=',self._uid)])
			for b in curr_users.user_branch_id:
				branch_ids.append(b.id)
				branches_data.append(b)

		if user_type == 'specific':
			# for bra in branch_ids:
			# 	branches.append(bra.id)
			# 	branches_data.append(bra)

			users_rec = []
			users = []
			for u in user_id:
				users.append(u.id)
				users_rec.append(u)

			branch_ids = []
			branches_data = []
			for u in users_rec:
				for b in u.user_branch_ids:
					if b.id not in branch_ids:
						branch_ids.append(b.id)
					if b not in branches_data:
						branches_data.append(b)

		main_data = []
		# for rec in branches:
		# 	in_data = []
		if report_type == 'all':
			head = "All Voucher"
			if user_type == 'all':
				if state == 'all':
					
					if journal_id:			
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('journal_id','=',journal_id.id)])	
				
					if not journal_id:
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to)])	
				else:
					
					if journal_id:							
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('journal_id','=',journal_id.id),('state','=',state)])	
					
					if not journal_id:
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('state','=',state)])

			if user_type == 'specific':

				if state == 'all':
					
					if journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('date','>=',form),('date','<=',to),('journal_id','=',journal_id.id)])
				
					if not journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('date','>=',form),('date','<=',to)])
				else:
					
					if journal_id:							
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('date','>=',form),('date','<=',to),('journal_id','=',journal_id.id),('state','=',state)])
					
					if not journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('date','>=',form),('date','<=',to),('state','=',state)])
								
					
		elif report_type == 'rec':
			head = "Receipt Voucher"

			if user_type == 'all':

				if state == 'all':
					
					if journal_id:
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('payment_type','=','inbound'),('journal_id','=',journal_id.id)])
					
					if not journal_id:
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('payment_type','=','inbound')])	
				else:

					if not journal_id:
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('payment_type','=','inbound'),('state','=',state)])

					if journal_id:							
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('payment_type','=','inbound'),('state','=',state),('journal_id','=',journal_id.id)])

			if user_type == 'specific':
				
				if state == 'all':
					
					if journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('date','>=',form),('date','<=',to),('payment_type','=','inbound'),('journal_id','=',journal_id.id)])
					
					if not journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('date','>=',form),('date','<=',to),('payment_type','=','inbound')])
				else:

					if not journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('date','>=',form),('date','<=',to),('payment_type','=','inbound'),('state','=',state)])

					if journal_id:							
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('date','>=',form),('date','<=',to),('payment_type','=','inbound'),('state','=',state),('journal_id','=',journal_id.id)])


		elif report_type == 'pay':
			head = "Payment Voucher"
			if user_type == 'all':
				if state == 'all':
					if not journal_id:
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('payment_type','=','outbound')])

					if journal_id:
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('payment_type','=','outbound'),('journal_id','=',journal_id.id)])

				else:

					if not journal_id:
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('payment_type','=','outbound'),('state','=',state)])

					if journal_id:
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('payment_type','=','outbound'),('state','=',state),('journal_id','=',journal_id.id)])

			if user_type == 'specific':
				if state == 'all':
					if not journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('payment_type','=','outbound')])

					if journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('payment_type','=','outbound'),('journal_id','=',journal_id.id)])

				else:

					if not journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('payment_type','=','outbound'),('state','=',state)])

					if journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('payment_type','=','outbound'),('state','=',state),('journal_id','=',journal_id.id)])


		elif report_type == 'trans':
			head = "Internal Transfer"
			if user_type == 'all':
				if state == 'all':
					if not journal_id:
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),'is_internal_transfer','=',True])

					if journal_id:
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('is_internal_transfer','=',True),('journal_id','=',journal_id.id)])

				else:

					if not journal_id:
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('is_internal_transfer','=',True),('state','=',state)])

					if journal_id:
						rec_pays = self.env['account.payment'].search([('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('is_internal_transfer','=',True),('state','=',state),('journal_id','=',journal_id.id)])

			if user_type == 'specific':
				if state == 'all':
					if not journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('is_internal_transfer','=',True),])

					if journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('is_internal_transfer','=',True),('journal_id','=',journal_id.id)])

				else:

					if not journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('is_internal_transfer','=',True),('state','=',state)])

					if journal_id:
						rec_pays = self.env['account.payment'].search([('create_uid','in',user_id.ids),('branch_ids.id','in',branch_ids),('date','>=',form),('date','<=',to),('is_internal_transfer','=',True),('state','=',state),('journal_id','=',journal_id.id)])


		branches_rec_data = []
		if rec_pays:
			for br_ids in rec_pays:
				if br_ids.branch_ids not in branches_rec_data:
					branches_rec_data.append(br_ids.branch_ids)



		main_data = []
		rec_pays_data = []
		for rec in branches_rec_data:
			in_data = []
			if rec_pays:
				for data_pays in rec_pays:
					if data_pays.branch_ids.id == rec.id:
						if rec.id not in rec_pays_data:
							for data in rec_pays:
								in_data.append({
									'date':data.date,
									'amount':data.amount,
									'ref':data.collectionre,
									'label':data.journal_id.name,
									'partner':data.partner_id.name,
									'user':data.create_uid.name,
									'voucher':data.name,
									'branch_name' : data.branch_ids.branch_ar_name,
									})
								rec_pays_data.append(rec.id)

							main_data.append({
									'branch':rec.branch_ar_name,
									'in_data':in_data,
									})
		# main_data = list(set(main_data))
		# trans = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('is_internal_transfer','=',True),('state','=',state),('branch_ids.id','in',branch_ids),('journal_id','=',journal_id.id)])

			
			
		return {
			'doc_ids': docids,
			'doc_model':'account.payment',
			'form': form,
			'to': to,
			'year': year,
			'main_data': main_data,
			'head': head,
			'state': state,
			'company_id': self.env.user.company_id,
		}

		# return report_obj.render('partner_ledger_sugar.partner_ledger_report', docargs)