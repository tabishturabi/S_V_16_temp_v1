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
from pytz import timezone, UTC

class BranchesLedgerReport(models.AbstractModel):
	_name = 'report.bassami_branches_legder.branches_basami_report'

	@api.model
	def _get_report_values(self, docids, data=None):
		model = self.env.context.get('active_model')
		record_wizard = self.env[model].browse(self.env.context.get('active_id'))


		date_form = record_wizard.date_form
		form = record_wizard.form
		print_by = record_wizard.print_by
		date_to = record_wizard.date_to
		to = record_wizard.to
		state = record_wizard.state
		journal_id = record_wizard.journal_id
		user_id = record_wizard.user_id
		user_type = record_wizard.user_type
		with_fc = record_wizard.with_fc
		currency_id = record_wizard.currency_id
		string_date = str(form)
		year = string_date[:4]
		head = "Branches Ledger"

		tz = timezone(self.env.context.get('tz') or self.env.user.tz)

		if date_form:
			from_date_tz = UTC.localize(date_form).astimezone(tz)

		if date_to:
			to_date_tz = UTC.localize(date_to).astimezone(tz)

		if user_type == 'all':
			branches = []
			curr_users = self.env['res.users'].search([('id','=',self._uid)])
			for b in curr_users.user_branch_id:
				branches.append(b)

			branch_ids = []
			users = []
			users = self.env['res.users'].search([]).ids

		if user_type == 'specific':
			users_rec = []
			users = []
			for u in user_id:
				users.append(u.id)

		accounts = []
		accounts.append(journal_id.default_account_id.id)
		accounts.append(journal_id.default_account_id.id)

		main_data = []
		trans = []
		opentrans = []

		if record_wizard.print_by:
			date_form = from_date_tz
			form = from_date_tz
			date_to = to_date_tz
			to = to_date_tz
		else:
			date_form = record_wizard.form
			form = record_wizard.form
			date_to = record_wizard.to
			to = record_wizard.to

		if user_type == 'specific':
			if state != 'all':
				trans = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('account_id.id','in',accounts),('move_id.state','=',state),('create_uid.id','in',users)])
			if state == 'all':
				trans = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('account_id.id','in',accounts),('create_uid.id','in',users)])

		if user_type == 'all':
			if state != 'all':
				trans = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('account_id.id','in',accounts),('move_id.state','=',state)])
			if state == 'all':
				trans = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('account_id.id','in',accounts)])
		if  with_fc and currency_id:
			trans = trans.filtered(lambda s: s.currency_id.id == currency_id.id)


		if user_type == 'all':
			if state != 'all':
				opentrans = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','in',accounts),('move_id.state','=',state)])


			if state == 'all':
				opentrans = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','in',accounts)])

		if user_type == 'specific':
			if state != 'all':
				opentrans = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','in',accounts),('move_id.state','=',state),('create_uid.id','in',users)])


			if state == 'all':
				opentrans = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','in',accounts),('create_uid.id','in',users)])
		if  with_fc and currency_id:
			opentrans = opentrans.filtered(lambda s: s.currency_id.id == currency_id.id)


		curences = set(trans.mapped('currency_id') + opentrans.mapped('currency_id'))
		currency_total_dict = []
		for curr in curences:
			currency_total_dict.append({
				'name' : curr.name,
				'initial': sum(opentrans.filtered(lambda s: s.currency_id.id == curr.id).mapped('amount_currency')),
				'move' : sum(trans.filtered(lambda s: s.currency_id.id == curr.id).mapped('amount_currency')),
				'final' : sum(opentrans.filtered(lambda s: s.currency_id.id == curr.id).mapped('amount_currency')) +
							sum(trans.filtered(lambda s: s.currency_id.id == curr.id).mapped('amount_currency')),
			})
		if self.env.user.company_id.currency_id:
			com_currency_init = sum(opentrans.filtered(lambda s: not s.currency_id.id).mapped('debit'))-sum(opentrans.filtered(lambda s: not s.currency_id.id).mapped('credit'))
			com_currency_move = sum(trans.filtered(lambda s: not s.currency_id.id).mapped('debit'))-sum(trans.filtered(lambda s: not s.currency_id.id).mapped('credit'))
			currency_total_dict.append({
				'name' : self.env.user.company_id.currency_id.name,
				'initial':com_currency_init ,
				'move' : com_currency_move,
				'final' : com_currency_init + com_currency_move,
			})
		if trans:
			trans = sorted(trans, key=lambda k: k.move_id.date)
			trans = sorted(trans, key=lambda k: k.move_id.create_date)

		cre = 0
		deb = 0
		opening = 0
		currency_opening = sum(opentrans.mapped('amount_currency'))
		for opened in opentrans:
			cre = cre + opened.credit
			deb = deb + opened.debit

		opening = deb - cre

		if opening > 0 or len(trans) > 0:
			main_data.append({
                    'name':journal_id.name,
                    'opening':opening,
                    'cre': cre,
					'deb': deb,
					'currency_opening':currency_opening,
					'company_currency':self.env.user.company_id.currency_id.name,
                    'trans':trans,
                    })


		if record_wizard.print_by:
			date_form = from_date_tz
			form = False
			date_to = to_date_tz
			to = False
		else:
			date_form = False
			form = record_wizard.form
			date_to = False
			to = record_wizard.to

		return {
			'doc_ids': docids,
			'doc_model':'account.journal',
			'date_form': date_form,
			'form': form,
			'date_to': date_to,
			'print_by': print_by,
			'to': to,
			'year': year,
			'state': state,
			'head': head,
			'journal_id': journal_id,
			'main_data': main_data,
			'with_fc':with_fc,
			'currency_tot' : currency_total_dict,
		}

		# return report_obj.render('partner_ledger_sugar.partner_ledger_report', docargs)
