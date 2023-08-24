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

class BranchesvoucherLedgerReport(models.AbstractModel):
	_name = 'report.budget_reconciliation_report.budget_recon_temp_id'

	@api.model
	def _get_report_values(self, docids, data=None):
		model = self.env.context.get('active_model')
		record_wizard = self.env[model].browse(self.env.context.get('active_id'))

		
		form = record_wizard.form
		to = record_wizard.to
		branch_ids = record_wizard.branch_ids
		report_type = record_wizard.report_type
		with_budget = record_wizard.with_budget
		without_budget = record_wizard.without_budget
		head = "Budget Reconciliation Report"
		types = " "

		branch_id = []
		for rec in branch_ids:
			branch_id.append(rec.id)


		if report_type == 'all':
			records = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','!=',False),('state','not in',('draft','cancelled','reversal_entry')),('payment_type','in',('inbound'),('is_internal_transfer','=',True))])

		if report_type == 'specific':
			records = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','!=',False),('branch_ids.id','in',branch_id),('state','not in',('draft','cancelled','reversal_entry')),('payment_type','in',('inbound'),('is_internal_transfer','=',True))])

		budget_num = []
		for x in records:
			if x.budget_number:
				if x.budget_number not in budget_num:
					budget_num.append(x.budget_number)

		
		main_data = []
		for y in budget_num:
			budget_data = []
			budget_recs = []
			balance = 0
			if not without_budget and not with_budget:
				types = " "
				if report_type == 'all':
					budget_recs = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','=',y),('state','not in',('draft','cancelled','reversal_entry')),('payment_type','in',('inbound'),('is_internal_transfer','=',True))],orde='date')

				if report_type == 'specific':
					budget_recs = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','=',y),('branch_ids.id','in',branch_id),('state','not in',('draft','cancelled','reversal_entry')),('payment_type','in',('inbound'),('is_internal_transfer','=',True))],order='date')

			if without_budget and with_budget:
				types = " "
				if report_type == 'all':
					budget_recs = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','=',y),('state','not in',('draft','cancelled','reversal_entry')),('payment_type','in',('inbound'),('is_internal_transfer','=',True))],order='date')

				if report_type == 'specific':
					budget_recs = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','=',y),('branch_ids.id','in',branch_id),('state','not in',('draft','cancelled','reversal_entry')),('payment_type','in',('inbound'),('is_internal_transfer','=',True))],order='date')

			if with_budget and not without_budget:
				types = "With Budget Created"
				if report_type == 'all':
					budget_trans = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','=',y),('state','not in',('draft','cancelled','reversal_entry')),('is_internal_transfer','=',True),])
					if budget_trans:
						budget_recs = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','=',y),('state','not in',('draft','cancelled','reversal_entry')),('payment_type','in',('inbound'),('is_internal_transfer','=',True))],order='date')

				if report_type == 'specific':
					budget_trans = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','=',y),('branch_ids.id','in',branch_id),('state','not in',('draft','cancelled','reversal_entry')),('is_internal_transfer','=',True),])
					if budget_trans:
						budget_recs = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','=',y),('branch_ids.id','in',branch_id),('state','not in',('draft','cancelled','reversal_entry')),('payment_type','in',('inbound'),('is_internal_transfer','=',True))],order='date')

			if without_budget and not with_budget:
				types = "Without Budget Created"
				if report_type == 'all':
					budget_trans = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','=',y),('state','not in',('draft','cancelled','reversal_entry')),('is_internal_transfer','=',True),])
					if budget_trans:
						pass
					else:
						budget_recs = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','=',y),('state','not in',('draft','cancelled','reversal_entry')),('payment_type','in',('inbound'),('is_internal_transfer','=',True))],order='date')

				if report_type == 'specific':
					budget_trans = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','=',y),('branch_ids.id','in',branch_id),('state','not in',('draft','cancelled','reversal_entry')),('is_internal_transfer','=',True),])
					if budget_trans:
						pass
					else:
						budget_recs = self.env['account.payment'].search([('date','>=',form),('date','<=',to),('budget_number','=',y),('branch_ids.id','in',branch_id),('state','not in',('draft','cancelled','reversal_entry')),('payment_type','in',('inbound'),('is_internal_transfer','=',True))],order='date')

			if budget_recs:
				for bud in budget_recs:
					debit = 0
					credit = 0
					if bud.payment_type == 'inbound':
						debit = bud.amount
					if bud.is_internal_transfer:
						credit = bud.amount
					balance = balance + debit - credit 
					budget_data.append({
						'date':bud.date,
						'name':bud.name,
						'op_num':bud.operation_number,
						'budget_no':bud.budget_number,
						'branch_name':bud.branch_ids.branch_ar_name,
						'debit':debit,
						'credit':credit,
						'balance':balance,
					})


			if len(budget_data) > 0:
				main_data.append({
					'name': y,
					'budget_data':budget_data,
					})

		
		return {
			'doc_ids': docids,
			'doc_model':'account.payment',
			'form': form,
			'to': to,
			'head': head,
			'records': records,
			'main_data': main_data,
			'types': types,
			'branch_ids': branch_ids,
		}