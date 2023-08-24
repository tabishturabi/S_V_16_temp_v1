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

class GeneralLedgerReport(models.AbstractModel):
	_name = 'report.bassami_general_legder.general_basami_report'

	@api.model
	def _get_report_values(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		record_wizard = self.env[self.model].browse(self.env.context.get('active_id'))

		
		form = record_wizard.form
		to = record_wizard.to
		state = record_wizard.state
		account_id = record_wizard.account_id
		string_date = str(form)
		year = string_date[:4]
		head = "General Ledger"
		with_fc = record_wizard.with_fc
		currency_id = record_wizard.currency_id
		
		if state != 'all':
			trans = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('account_id.id','=',account_id.id),('move_id.state','=',state)])

		if state == 'all':
			trans = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('account_id.id','=',account_id.id)])
		
		if  with_fc and currency_id:
			trans = trans.filtered(lambda s: s.currency_id.id == currency_id.id)

		if state != 'all':
			opentrans = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','=',account_id.id),('move_id.state','=',state)])

		if state == 'all':
			opentrans = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','=',account_id.id)])
		
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

	
		cre = 0
		deb = 0
		opening = 0
		currency_opening = sum(opentrans.mapped('amount_currency'))
		for opened in opentrans:
			cre = cre + opened.credit
			deb = deb + opened.debit


		opening = deb - cre
			
			
		return {
			'doc_ids': docids,
			'doc_model':'account.payment',
			'form': form,
			'to': to,
			'year': year,
			'trans': trans,
			'state': state,
			'head': head,
			'account_id': account_id,
			'opening': opening,
			'cre': cre,
			'deb': deb,
			'currency_opening':currency_opening,
			'company_currency':self.env.user.company_id.currency_id.name,
			'with_fc':with_fc,
			'currency_tot' : currency_total_dict,
		}

		# return report_obj.render('partner_ledger_sugar.partner_ledger_report', docargs)
