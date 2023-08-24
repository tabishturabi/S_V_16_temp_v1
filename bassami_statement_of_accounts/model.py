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
import re
import pandas as pd
import numpy as np
import psycopg2 as pg
import pandas.io.sql as psql
from odoo import api, models, fields
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning

class PartnerLedgerReport(models.AbstractModel):
	_name = 'report.bassami_statement_of_accounts.partner_ledger_report'

	@api.model
	def _get_report_values(self, docids, data=None):
		model = self.env.context.get('active_model')
		record_wizard = self.env[model].browse(self.env.context.get('active_id'))

		
		form = record_wizard.form
		to = record_wizard.to
		entry_type = record_wizard.entry_type
		customer_type = record_wizard.customer_type
		account_ids = record_wizard.account_ids
		account_type = record_wizard.account_type
		partner_types = record_wizard.partner_types
		with_details = record_wizard.with_details
		for_emp = record_wizard.for_emp
		sort_details = record_wizard.sort_details
		branch_ids = record_wizard.branch_ids
		partner_types_ids = []
		partner_types_name = " "
		for p in partner_types:
			partner_types_ids.append(p.id)
			partner_types_name = str(partner_types_name) +' '+ str(p.name)
		branches_ids = []
		for b in branch_ids:
			branches_ids.append(b.id)
		details = 0

		enteries_type = " "
		if entry_type == 'all':
			enteries_type = "All Enteries"
		else:
			enteries_type = "Posted Enteries"

		account_type_name = " "

		if not partner_types:
			if customer_type != 'all':
				partner_ids = record_wizard.partner_ids.ids
				partner_id_recs = record_wizard.partner_ids
			if customer_type == 'all':
				partner_id_recs = self.env['res.partner'].search([])
				partner_ids = partner_id_recs.ids

		if partner_types:
			if customer_type != 'all':
				partner_ids = record_wizard.partner_ids.ids
				partner_id_recs = record_wizard.partner_ids
			if customer_type == 'all':
				partner_id_recs = self.env['res.partner'].search([('partner_types.id','in',partner_types_ids)])
				partner_ids = partner_id_recs.ids


		act_ids = []
		if account_ids and account_type == 'others':
			account_type_name = "Others"
			act_ids += record_wizard.account_ids.ids
			# for act in record_wizard.account_ids:
			# 	act_ids.append(act.id)
		if not account_ids and account_type == 'others':
			account_type_name = "Others"
			all_acts = self.env['account.account'].search([])
			act_ids += all_acts.ids
			# for act in all_acts:
			# 	act_ids.append(act.id)
		if account_type == 'receive':
			account_type_name = "Receivable"
			if not partner_types:
				all_acts = self.env['account.account'].search([('user_type_id','=','Receivable')])
				act_ids += all_acts.ids
				# for act in all_acts:
				# 	act_ids.append(act.id)
			else:
				all_acts = self.env['partner.type'].search([('id','in',partner_types_ids)])
				act_ids += all_acts.mapped('accont_rec.id')
				# for act in all_acts:
				# 	act_ids.append(act.accont_rec.id)
				
		if account_type == 'pay':
			account_type_name = "Payable"
			if not partner_types:
				all_acts = self.env['account.account'].search([('user_type_id','=','Payable')])
				act_ids += all_acts.ids
			# 	for act in all_acts:
			# 		act_ids.append(act.id)
			else:
				all_acts = self.env['partner.type'].search([('id','in',partner_types_ids)])
				act_ids += all_acts.mapped('accont_payable.id')
				# for act in all_acts:
				# 	act_ids.append(act.accont_payable.id)

		partner_ids_str = len(partner_ids) == 1 and "(%s)" %partner_ids[0] or  str(tuple(partner_ids))
		table_name = "account_account"
		act_ids_str = len(act_ids) == 1 and "(%s)" %act_ids[0] or  str(tuple(act_ids))
		self.env.cr.execute("select id,user_type_id,name,code,levels,parent_id FROM "+table_name+" where id in %s" %act_ids_str)
		result = self._cr.fetchall()
		all_acts_frame = pd.DataFrame(list(result))
		all_acts_frame = all_acts_frame.rename(columns={0: 'act_id',1: 'act_user_type_id',2: 'act_name',3: 'act_code',4: 'act_levels',5: 'act_parent_id'})

		move_line_table = "account_move_line"
		self.env.cr.execute("select id,account_id,date,debit,credit,move_id,partner_id,bsg_branches_id,name FROM "+move_line_table+" where account_id in %s and partner_id in %s" %(act_ids_str, partner_ids_str))
		move_line_result = self._cr.fetchall()
		period_acts = pd.DataFrame(list(move_line_result))
		open_acts = pd.DataFrame(list(move_line_result))

		period_acts = period_acts.rename(columns={0: 'line_id',1: 'move_act_id',2: 'move_date',3: 'period_debit',4: 'period_credit',5: 'move_id',6: 'partner_id',7: 'bsg_branches_id',8: 'label'})

		open_acts = open_acts.rename(columns={0: 'open_line_id',1: 'open_move_act_id',2: 'open_move_date',3: 'open_period_debit',4: 'open_period_credit',5: 'open_move_id',6: 'open_partner_id',7: 'open_bsg_branches_id'})


		move_table = "account_move"
		mv_ids = [ mv[5] for mv in move_line_result ]
		if mv_ids:
			move_ids_str = len(mv_ids) == 1 and "(%s)" %mv_ids[0] or str(tuple(mv_ids))
			self.env.cr.execute("select id,state,name FROM "+move_table+" where id in %s " %move_ids_str)
			move_result = self._cr.fetchall()
			move_frame = pd.DataFrame(list(move_result))
			move_frame = move_frame.rename(columns={0: 'form_id',1: 'move_state',2: 'move_name'})

			period_acts = pd.merge(period_acts, move_frame, how='left', left_on='move_id', right_on='form_id')
			open_acts = pd.merge(open_acts, move_frame, how='left', left_on='open_move_id', right_on='form_id')


		cust_table = "res_partner"
		self.env.cr.execute("select id,name,street,phone,city,vat,parent_id,function,ref FROM "+cust_table+ " ")
		# where id in %s" %partner_ids_str)
		cust_result = self._cr.fetchall()
		cust_frame = pd.DataFrame(list(cust_result))
		# cust_frame = cust_frame[cust_frame[6].notnull()]
		parent_frame = pd.DataFrame(list(cust_result))
		# parent_frame = parent_frame[parent_frame[6].isnull()] 

		cust_frame = cust_frame.rename(columns={0: 'cust_id',1: 'cust_name',2: 'street',3: 'phone',4: 'city',5: 'vat',6: 'cust_parent_id',7:'function',8:'ref'})
		parent_frame = parent_frame.rename(columns={0: 'parent_id',1: 'parent_name'})

		# if not parent_frame.empty:
		cust_frame = pd.merge(cust_frame,parent_frame,  how='left', left_on='cust_parent_id', right_on ='parent_id')



		if not period_acts.empty:
			if entry_type == 'all':
				period_acts = period_acts.loc[(period_acts['move_date'] >= form) & (period_acts['move_date'] <= to) & (period_acts['partner_id'].isin(partner_ids))]
			if entry_type == 'posted':
				period_acts = period_acts.loc[(period_acts['move_date'] >= form) & (period_acts['move_date'] <= to) & (period_acts['move_state'] == 'posted') & (period_acts['partner_id'].isin(partner_ids))]
			if branch_ids:
				period_acts = period_acts[period_acts['bsg_branches_id'].isin(branches_ids)]				
		if not open_acts.empty:
			if entry_type == 'all':
				open_acts = open_acts.loc[(open_acts['open_move_date'] < form) & (open_acts['open_partner_id'].isin(partner_ids))]
			if entry_type == 'posted':
				open_acts = open_acts.loc[(open_acts['open_move_date'] < form) & (open_acts['move_state'] == 'posted') & (open_acts['open_partner_id'].isin(partner_ids))]
			if branch_ids:
				open_acts = open_acts[open_acts['open_bsg_branches_id'].isin(branches_ids)]
		

		
		details_period_acts = period_acts
		final_frame = []
		if not period_acts.empty:
			details_period_acts = pd.merge(details_period_acts,all_acts_frame,  how='left', left_on='move_act_id', right_on ='act_id')
		if not period_acts.empty:
			period_acts = period_acts.groupby(['partner_id'],as_index = False).sum()
		if not open_acts.empty:	
			open_acts = open_acts.groupby(['open_partner_id'],as_index = False).sum()

		if len(period_acts) >= len(open_acts) and not period_acts.empty:
			final_frame = pd.merge(period_acts,open_acts,  how='left', left_on='partner_id', right_on ='open_partner_id')
			final_frame = pd.merge(final_frame,cust_frame,  how='left', left_on='partner_id', right_on ='cust_id')
			final_frame = final_frame.fillna(0)
		if len(period_acts) < len(open_acts) and not open_acts.empty:
			final_frame = pd.merge(open_acts,period_acts,  how='left', left_on='open_partner_id', right_on ='partner_id')
			final_frame = pd.merge(final_frame,cust_frame,  how='left', left_on='open_partner_id', right_on ='cust_id')
			final_frame = final_frame.fillna(0)
		


		main_data = []

		if not with_details:
			details = 2
			if len(final_frame):
				for q,r in final_frame.iterrows():

					real_open_bal = r['open_period_debit'] - r['open_period_credit']
					debits = r['period_debit']
					credits = r['period_credit']
					closing_bal = (real_open_bal + debits) - credits

					if real_open_bal or debits or credits > 0:

						parent_name = " "
						if r['parent_name'] != 0:
							parent_name = r['parent_name']

						phone = " "
						if r['phone'] != 0:
							phone = r['phone']

						street = " "
						if r['street'] != 0:
							street = r['street']

						vat = " "
						if r['vat'] != 0:
							vat = r['vat']

						function = " "
						if r['function'] !=0:
							function = r['function']

						ref = " "	
						if r['ref'] != 0:
							ref = r['ref']

						main_data.append({
							'name': r['cust_name'],
							'street': street,
							'phone': phone,
							'city': r['city'],
							'parent_id': parent_name,
							'function':function,
							'ref':ref,
							'vat': vat,
							'real_open_bal':real_open_bal,
							'debit': debits,
							'credit': credits,
							'closing_bal':closing_bal,
							})

		else:

			details = 1
			if len(final_frame):
				for q,r in final_frame.iterrows():

					enteries = []
					enteries_frame = details_period_acts.loc[(details_period_acts['partner_id'] == r['partner_id'])]
					if sort_details:
						enteries_frame = enteries_frame.sort_values(by='act_code')
					else:
						enteries_frame = enteries_frame.sort_values(by='move_date')

					for i,j in enteries_frame.iterrows():
						enteries.append({
							'date': j['move_date'],
							'debit': j['period_debit'],
							'credit': j['period_credit'],
							'label': j['label'],
							'move_name': j['move_name'],
							'act_name': j['act_name'],
							'act_code': j['act_code'],
							})

					real_open_bal = r['open_period_debit'] - r['open_period_credit']
					debits = r['period_debit']
					credits = r['period_credit']
					closing_bal = (real_open_bal + debits) - credits

					if real_open_bal or debits or credits > 0:

						parent_name = " "
						if r['parent_name'] != 0:
							parent_name = r['parent_name']

						phone = " "
						if r['phone'] != 0:
							phone = r['phone']

						street = " "
						if r['street'] != 0:
							street = r['street']

						vat = " "
						if r['vat'] != 0:
								vat = r['vat']

						function = " "
						if r['function'] !=0:
							function = r['function']

						ref = " "
						if r['ref'] !=0:
							ref = r['ref']
								
						main_data.append({
							'name': r['cust_name'],
							'street': street,
							'phone': phone,
							'city': r['city'],
							'parent_id': parent_name,
							'function':function,
							'ref':ref,
							'vat': vat,
							'enteries': enteries,
							'real_open_bal':real_open_bal,
							'debit': 0,
							'credit': 0,
							'closing_bal':0,
							})



		real_open_bal_tot = 0
		debits_tot = 0
		credits_tot = 0
		closing_bal_tot = 0
		for tot in main_data:
			real_open_bal_tot = real_open_bal_tot + tot['real_open_bal']
			debits_tot = debits_tot + tot['debit']
			credits_tot = credits_tot + tot['credit']
			closing_bal_tot = closing_bal_tot + tot['closing_bal']

		def get_cargo_ids(attr):
			len_check = 50 * int(attr)
			if len(main_data) <= len_check:
				start_range = int(len_check - 50)
				return main_data[start_range:]
			if len(main_data) > len_check:
				start_range = int(len_check - 50)
				return main_data[start_range:len_check]

		check_loops = len(main_data) % 50


		runing_loop = 1
		exact_loop = 1
		if main_data:
			runing_loop = int(len(main_data)) / 50
			int_value = int(runing_loop)
			if runing_loop > int_value:
				exact_loop = int_value + 1
			else:
				exact_loop = int_value


		page_numz = []
		for ex in range(exact_loop):
			page_numz.append(ex+1)

		if len(main_data) < 1:
			partner_ids = self.env['res.partner'].sudo().browse(partner_ids)
			for partner in partner_ids:
				main_data.append({
								'name': partner.name,
								'street': partner.street,
								'phone': partner.phone,
								'city': partner.city,
								'parent_id': partner.parent_id.name,
								'function':partner.function,
								'ref':partner.ref,
								'vat': partner.vat,
								'enteries': [],
								'real_open_bal':0,
								'debit': 0,
								'credit': 0,
								'closing_bal':0,
								})
		
		return {
			'doc_ids': docids,
			'doc_model':'res.partner',
			'form': form,
			'to': to,
			'main_data': main_data,
			'details': details,
			'page_numz': page_numz,
			'exact_loop': exact_loop,
			'get_cargo_ids': get_cargo_ids,
			'real_open_bal_tot': real_open_bal_tot,
			'debits_tot': debits_tot,
			'credits_tot': credits_tot,
			'closing_bal_tot': closing_bal_tot,
			'partner_types_name': partner_types_name,
			'enteries_type': enteries_type,
			'account_type_name': account_type_name,
			'for_emp':for_emp,
			'current_user_id': record_wizard.env.user
		}

