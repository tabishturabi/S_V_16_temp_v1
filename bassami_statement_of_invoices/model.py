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
from num2words import num2words

class PartnerLedgerReport(models.AbstractModel):
    _name = 'report.bassami_statement_of_invoices.partner_ledger_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        record_wizard = self.env[model].browse(self.env.context.get('active_id'))

        
        partner_ids = record_wizard.partner_ids
        date_from = record_wizard.date_from
        date_to = record_wizard.date_to
        customer_ids = record_wizard.customer_ids
        all_invoices = record_wizard.all_invoices
        has_invoice = record_wizard.has_invoice

        rec_acts = []
        arabic_rec = self.env['account.account'].search([('user_type_id.name', '=','المدين')])
        if arabic_rec:
          for j in arabic_rec:
            if j.id not in rec_acts:
              rec_acts.append(j.id)

        eng_rec = self.env['account.account'].search([('user_type_id.name', '=','Receivable')])
        if eng_rec:
          for k in eng_rec:
            if k.id not in rec_acts:
              rec_acts.append(k.id)

        pay_acts = []
        arabic_pay = self.env['account.account'].search([('user_type_id.name', '=','الدائن')])
        if arabic_pay:
          for l in arabic_pay:
            if l.id not in pay_acts:
              pay_acts.append(l.id)

        eng_pay = self.env['account.account'].search([('user_type_id.name', '=','Payable')])
        if eng_pay:
          for m in eng_pay:
            if m.id not in pay_acts:
              pay_acts.append(m.id)


        all_partner_ids = []
        if not has_invoice:
            all_partner_ids.append(partner_ids)
        else:
            check_data_1 = []
            if all_invoices:
                check_data_1 = self.env['account.move'].search([('invoice_date', '>=', date_from), ('invoice_date', '<=', date_to),
                                                  ('partner_id', '=', partner_ids.id),
                                                  ('move_type', '=', 'out_invoice'),
                                                  ('payment_state', 'in', ['unpaid','paid'])])
            else:
                check_data_1 = self.env['account.move'].search([('invoice_date', '>=', date_from), ('invoice_date', '<=', date_to),
                                                  ('partner_id', '=', partner_ids.id),
                                                  ('move_type', '=', 'out_invoice'),
                                                  ('payment_state', 'in', ['unpaid','paid']),
                                                  ('credit_collection_id', '!=',False)])
            if check_data_1:
                all_partner_ids.append(partner_ids)

        if customer_ids:
            if not has_invoice:
                for rec in customer_ids:
                    all_partner_ids.append(rec)
            else:
                for rec in customer_ids:
                    check_data_2 = []
                    if all_invoices:
                        check_data_2 = self.env['account.move'].search([('invoice_date', '>=', date_from), ('invoice_date', '<=', date_to),
                                                          ('partner_id', '=', rec.id),
                                                          ('move_type', '=', 'out_invoice'),
                                                          ('payment_state', 'in', ['unpaid','paid'])])
                    else:
                        check_data_2 = self.env['account.move'].search([('invoice_date', '>=', date_from), ('invoice_date', '<=', date_to),
                                                          ('partner_id', '=', rec.id),
                                                          ('move_type', '=', 'out_invoice'),
                                                          ('payment_state', 'in', ['unpaid','paid']),
                                                          ('credit_collection_id', '!=',False)])
                    if check_data_2:
                        all_partner_ids.append(rec)

        if not customer_ids:
            if not has_invoice:
                for rec in partner_ids.child_ids:
                    all_partner_ids.append(rec)
            else:
                for rec in partner_ids.child_ids:
                    check_data_3 = []
                    if all_invoices:
                        check_data_3 = self.env['account.move'].search([('invoice_date', '>=', date_from), ('invoice_date', '<=', date_to),
                                                          ('partner_id', '=', rec.id),
                                                          ('move_type', '=', 'out_invoice'),
                                                          ('payment_state', 'in', ['unpaid','paid'])])
                    else:
                        check_data_3 = self.env['account.move'].search([('invoice_date', '>=', date_from), ('invoice_date', '<=', date_to),
                                                          ('partner_id', '=', rec.id),
                                                          ('move_type', '=', 'out_invoice'),
                                                          ('payment_state', 'in', ['unpaid','paid']),
                                                          ('credit_collection_id', '!=',False)])
                    if check_data_3:
                        all_partner_ids.append(rec)


        main_data = []
        for p in all_partner_ids:
            domain = []
            if all_invoices:
                domain += [('invoice_date', '>=', date_from), ('invoice_date', '<=', date_to),
                                                  ('partner_id', '=', p.id),
                                                  ('move_type', '=', 'out_invoice'),
                                                  ('payment_state', 'in', ['unpaid','paid'])]
            else:
                domain += [('invoice_date', '>=', date_from), ('invoice_date', '<=', date_to),
                                                  ('partner_id', '=', p.id),
                                                  ('move_type', '=', 'out_invoice'),
                                                  ('payment_state', 'in', ['unpaid','paid']),
                                                  ('credit_collection_id', '!=',False)]
            InvoicesObj = self.env['account.move'].search(domain)

            entries_before = self.env['account.move.line'].search([
                ('move_id.date','<',date_from),
                ('partner_id.id','=',p.id),
                '|',('account_id.id','in',rec_acts),
                ('account_id.id','in',pay_acts)])

            prev_ent_debit = 0
            prev_ent_credit = 0

            for i in entries_before:
                prev_ent_debit = prev_ent_debit + i.debit
                prev_ent_credit = prev_ent_credit + i.credit

            real_open_bal = prev_ent_debit - prev_ent_credit


            entries = self.env['account.move.line'].search([
                ('move_id.date','>=',date_from),
                ('move_id.date','<=',date_to),
                ('partner_id.id','=',p.id),
                '|',
                ('account_id.id','in',rec_acts),
                ('account_id.id','in',pay_acts)])

            debits = 0
            credits = 0
            for x in entries:
                debits = debits + x.debit
                credits = credits + x.credit

            opening_bal = debits - credits


            main_data.append({
                'name': p.name,
                'street': p.street,
                'phone': p.phone,
                'city': p.city,
                'country': p.country_id.name,
                'parent_id': p.parent_id.name,
                'vat': p.vat,
                'enteries': InvoicesObj,
                'real_open_bal':real_open_bal,
                'opening_bal': opening_bal,
                'closing_bal':(opening_bal + real_open_bal),
                })


        def number_to_spell(attrb):
            round_num = round(attrb,2)
            word = num2words(round_num)
            word = word.title() + " " + "SAR Only"
            return word

        def getname():
            name = self.env['res.users'].search([('id', '=', self._uid)]).name
            return name
            
       
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': all_partner_ids,
            'date':date.today(),
            'number_to_spell':number_to_spell,
            'getname':getname,
            'date_from': date_from,
            'date_to': date_to,
            'main_data': main_data,
        }