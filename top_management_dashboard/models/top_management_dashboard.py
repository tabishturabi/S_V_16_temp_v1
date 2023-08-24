# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import pandas as pd
from pytz import utc
from odoo import models, fields, api, _
from odoo.http import request
from odoo.tools import float_utils
import collections, functools, operator


class PaymentInherit(models.Model):
    _inherit = 'account.payment'

    @api.model
    def get_payment_voucher(self):
        receipt_vouchers_query = """
                select array_agg(payment.id),sum(payment.amount)
                from account_payment as payment 
                LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound') 
                and journal.company_id = %d"""%(self.env.user.company_id.id)
        cr = self._cr
        cr.execute(receipt_vouchers_query)
        receipt_vouchers_amount = cr.fetchall()
        portal_receipt_vouchers_query = """
                       select array_agg(payment.id),sum(payment.amount)
                       from account_payment as payment 
                       LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                       WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound')
                       and payment.journal_id in (778,794) and payment.cargo_sale_order_id is null 
                       and journal.company_id = %d"""%(self.env.user.company_id.id)
        cr = self._cr
        cr.execute(portal_receipt_vouchers_query)
        portal_receipt_vouchers_amount = cr.fetchall()
        app_receipt_vouchers_query = """
                       select array_agg(payment.id),sum(payment.amount)
                       from account_payment as payment 
                       LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                       WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound')
                       and payment.journal_id in (778,794) and payment.cargo_sale_order_id is not null 
                       and journal.company_id = %d"""%(self.env.user.company_id.id)
        cr = self._cr
        cr.execute(app_receipt_vouchers_query)
        app_receipt_vouchers_amount = cr.fetchall()
        payment_vouchers_query = """
                       select array_agg(payment.id),sum(payment.amount)
                       from account_payment as payment 
                       LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                       WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('outbound') 
                       and journal.company_id = %d"""%(self.env.user.company_id.id)
        cr = self._cr
        cr.execute(payment_vouchers_query)
        payment_vouchers_amount = cr.fetchall()

        fuel_vouchers_query ="""
                       select array_agg(payment.id),sum(payment.amount)
                       from account_payment as payment 
                       LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                       WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('outbound') 
                       and payment.fleet_trip_id is not null and journal.company_id = %d"""%(self.env.user.company_id.id)
        cr = self._cr
        cr.execute(fuel_vouchers_query)
        fuel_vouchers_amount = cr.fetchall()
        payments = {
            'receipt_vouchers_amount': receipt_vouchers_amount[0][1] if receipt_vouchers_amount[0][1] != None else 0.00,
            'receipt_vouchers_ids': receipt_vouchers_amount[0][0] if receipt_vouchers_amount[0][0] != None else [],
            'portal_receipt_vouchers_amount': portal_receipt_vouchers_amount[0][1] if portal_receipt_vouchers_amount[0][
                                                                                          1] != None else 0.00,
            'portal_receipt_vouchers_ids': portal_receipt_vouchers_amount[0][0] if portal_receipt_vouchers_amount[0][
                                                                                       0] != None else [],
            'app_receipt_vouchers_amount': app_receipt_vouchers_amount[0][1] if app_receipt_vouchers_amount[0][
                                                                                    1] != None else 0.00,
            'app_receipt_vouchers_ids': app_receipt_vouchers_amount[0][0] if app_receipt_vouchers_amount[0][
                                                                                 0] != None else [],
            'payment_vouchers_amount': payment_vouchers_amount[0][1] if payment_vouchers_amount[0][1] != None else 0.00,
            'payment_vouchers_ids': payment_vouchers_amount[0][0] if payment_vouchers_amount[0][0] != None else [],
            'fuel_vouchers_amount': fuel_vouchers_amount[0][1] if fuel_vouchers_amount[0][1] != None else 0.00,
            'fuel_vouchers_ids': fuel_vouchers_amount[0][0] if fuel_vouchers_amount[0][0] != None else [],
        }
        return payments

    @api.model
    def get_payment_voucher_by_day(self):
        today = date.today()
        receipt_vouchers_query = """
                        select array_agg(payment.id),sum(payment.amount)
                        from account_payment as payment 
                        LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                        LEFT JOIN account_move move ON payment.move_id=move.id
                        WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound')
                        and EXTRACT(DAY FROM move.date)=%d and EXTRACT(MONTH FROM move.date)=%d 
                        and EXTRACT(YEAR FROM move.date)=%d 
                        and journal.company_id = %d"""%(today.day,today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(receipt_vouchers_query)
        receipt_vouchers_amount = cr.fetchall()
        print('................receipt_vouchers_amount...........',receipt_vouchers_amount)
        portal_receipt_vouchers_query = """
                               select array_agg(payment.id),sum(payment.amount)
                               from account_payment as payment
                               LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                               LEFT JOIN account_move move ON payment.move_id=move.id
                               WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound')
                               and payment.journal_id in (778,794) and payment.cargo_sale_order_id is null 
                               and EXTRACT(DAY FROM move.date)=%d and EXTRACT(MONTH FROM move.date)=%d 
                               and EXTRACT(YEAR FROM move.date)=%d 
                               and journal.company_id = %d"""%(today.day,today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(portal_receipt_vouchers_query)
        portal_receipt_vouchers_amount = cr.fetchall()
        print('................portal_receipt_vouchers_amount...........', portal_receipt_vouchers_amount)
        app_receipt_vouchers_query = """
                               select array_agg(payment.id),sum(payment.amount)
                               from account_payment as payment
                               LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                               LEFT JOIN account_move move ON payment.move_id=move.id
                               WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound')
                               and payment.journal_id in (778,794) and payment.cargo_sale_order_id is not null 
                               and EXTRACT(DAY FROM move.date)=%d and EXTRACT(MONTH FROM move.date)=%d 
                               and EXTRACT(YEAR FROM move.date)=%d 
                               and journal.company_id = %d"""%(today.day,today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(app_receipt_vouchers_query)
        app_receipt_vouchers_amount = cr.fetchall()
        payment_vouchers_query = """
                               select array_agg(payment.id),sum(payment.amount)
                               from account_payment as payment
                               LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                               LEFT JOIN account_move move ON payment.move_id=move.id
                               WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('outbound') 
                               and EXTRACT(DAY FROM move.date)=%d and EXTRACT(MONTH FROM move.date)=%d 
                               and EXTRACT(YEAR FROM move.date)=%d 
                               and journal.company_id = %d"""%(today.day,today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(payment_vouchers_query)
        payment_vouchers_amount = cr.fetchall()

        fuel_vouchers_query = """
                               select array_agg(payment.id),sum(payment.amount)
                               from account_payment as payment
                               LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                               LEFT JOIN account_move move ON payment.move_id=move.id
                               WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('outbound') 
                               and EXTRACT(DAY FROM move.date)=%d and EXTRACT(MONTH FROM move.date)=%d 
                               and payment.fleet_trip_id is not null and EXTRACT(YEAR FROM move.date)=%d 
                               and journal.company_id = %d"""%(today.day,today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(fuel_vouchers_query)
        fuel_vouchers_amount = cr.fetchall()
        payments = {
            'receipt_vouchers_amount': receipt_vouchers_amount[0][1] if receipt_vouchers_amount[0][1] != None else 0.00,
            'receipt_vouchers_ids': receipt_vouchers_amount[0][0] if receipt_vouchers_amount[0][0] != None else [],
            'portal_receipt_vouchers_amount': portal_receipt_vouchers_amount[0][1] if portal_receipt_vouchers_amount[0][1] != None else 0.00,
            'portal_receipt_vouchers_ids': portal_receipt_vouchers_amount[0][0] if portal_receipt_vouchers_amount[0][0] != None else [],
            'app_receipt_vouchers_amount': app_receipt_vouchers_amount[0][1] if app_receipt_vouchers_amount[0][1] != None else 0.00,
            'app_receipt_vouchers_ids': app_receipt_vouchers_amount[0][0] if app_receipt_vouchers_amount[0][0] != None else [],
            'payment_vouchers_amount': payment_vouchers_amount[0][1] if payment_vouchers_amount[0][1] != None else 0.00,
            'payment_vouchers_ids': payment_vouchers_amount[0][0] if payment_vouchers_amount[0][0] != None else [],
            'fuel_vouchers_amount': fuel_vouchers_amount[0][1] if fuel_vouchers_amount[0][1] != None else 0.00,
            'fuel_vouchers_ids': fuel_vouchers_amount[0][0] if fuel_vouchers_amount[0][0] != None else [],
        }
        print('...............payments..................', payments)
        return payments


    @api.model
    def get_payment_voucher_by_week(self):
        today = date.today()
        receipt_vouchers_query = """
                                select array_agg(payment.id),sum(payment.amount)
                                from account_payment as payment
                                LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                                LEFT JOIN account_move move ON payment.move_id=move.id
                                WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound') 
                                and EXTRACT(WEEK FROM move.date)=%d 
                                and EXTRACT(YEAR FROM move.date)=%d 
                                and journal.company_id = %d""" %(today.isocalendar()[1], today.isocalendar()[0],self.env.user.company_id.id)
        cr = self._cr
        cr.execute(receipt_vouchers_query)
        receipt_vouchers_amount = cr.fetchall()
        portal_receipt_vouchers_query = """
                                       select array_agg(payment.id),sum(payment.amount)
                                       from account_payment as payment
                                       LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                                       LEFT JOIN account_move move ON payment.move_id=move.id
                                       WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound')
                                       and payment.journal_id in (778,794) and payment.cargo_sale_order_id is null 
                                       and EXTRACT(WEEK FROM move.date)=%d 
                                       and EXTRACT(YEAR FROM move.date)=%d 
                                       and journal.company_id = %d""" %(today.isocalendar()[1], today.isocalendar()[0],self.env.user.company_id.id)
        cr = self._cr
        cr.execute(portal_receipt_vouchers_query)
        portal_receipt_vouchers_amount = cr.fetchall()
        app_receipt_vouchers_query = """
                                       select array_agg(payment.id),sum(payment.amount)
                                       from account_payment as payment
                                       LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                                       LEFT JOIN account_move move ON payment.move_id=move.id
                                       WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound')
                                       and payment.journal_id in (778,794) and payment.cargo_sale_order_id is not null 
                                       and EXTRACT(WEEK FROM move.date)=%d 
                                       and EXTRACT(YEAR FROM move.date)=%d 
                                       and journal.company_id = %d""" %(today.isocalendar()[1], today.isocalendar()[0],self.env.user.company_id.id)
        cr = self._cr
        cr.execute(app_receipt_vouchers_query)
        app_receipt_vouchers_amount = cr.fetchall()
        payment_vouchers_query = """
                                       select array_agg(payment.id),sum(payment.amount)
                                       from account_payment as payment
                                       LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                                       LEFT JOIN account_move move ON payment.move_id=move.id
                                       WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('outbound') 
                                       and EXTRACT(WEEK FROM move.date)=%d 
                                       and EXTRACT(YEAR FROM move.date)=%d 
                                       and journal.company_id = %d""" %(today.isocalendar()[1], today.isocalendar()[0],self.env.user.company_id.id)
        cr = self._cr
        cr.execute(payment_vouchers_query)
        payment_vouchers_amount = cr.fetchall()
        fuel_vouchers_query = """
                                       select array_agg(payment.id),sum(payment.amount)
                                       from account_payment as payment
                                       LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                                       LEFT JOIN account_move move ON payment.move_id=move.id
                                       WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('outbound') 
                                       and payment.fleet_trip_id is not null and EXTRACT(WEEK FROM move.date)=%d 
                                       and EXTRACT(YEAR FROM move.date)=%d 
                                       and journal.company_id = %d""" %(today.isocalendar()[1], today.isocalendar()[0],self.env.user.company_id.id)
        cr = self._cr
        cr.execute(fuel_vouchers_query)
        fuel_vouchers_amount = cr.fetchall()
        payments = {
            'receipt_vouchers_amount': receipt_vouchers_amount[0][1] if receipt_vouchers_amount[0][1] != None else 0.00,
            'receipt_vouchers_ids': receipt_vouchers_amount[0][0] if receipt_vouchers_amount[0][0] != None else [],
            'portal_receipt_vouchers_amount': portal_receipt_vouchers_amount[0][1] if portal_receipt_vouchers_amount[0][
                                                                                          1] != None else 0.00,
            'portal_receipt_vouchers_ids': portal_receipt_vouchers_amount[0][0] if portal_receipt_vouchers_amount[0][
                                                                                       0] != None else [],
            'app_receipt_vouchers_amount': app_receipt_vouchers_amount[0][1] if app_receipt_vouchers_amount[0][
                                                                                    1] != None else 0.00,
            'app_receipt_vouchers_ids': app_receipt_vouchers_amount[0][0] if app_receipt_vouchers_amount[0][
                                                                                 0] != None else [],
            'payment_vouchers_amount': payment_vouchers_amount[0][1] if payment_vouchers_amount[0][1] != None else 0.00,
            'payment_vouchers_ids': payment_vouchers_amount[0][0] if payment_vouchers_amount[0][0] != None else [],
            'fuel_vouchers_amount': fuel_vouchers_amount[0][1] if fuel_vouchers_amount[0][1] != None else 0.00,
            'fuel_vouchers_ids': fuel_vouchers_amount[0][0] if fuel_vouchers_amount[0][0] != None else [],
        }
        print('...............payments..................', payments)
        return payments

    @api.model
    def get_payment_voucher_by_month(self):
        today = date.today()
        receipt_vouchers_query = """
                        select array_agg(payment.id),sum(payment.amount)
                        from account_payment as payment
                        LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                        LEFT JOIN account_move move ON payment.move_id=move.id
                        WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound') 
                        and EXTRACT(MONTH FROM move.date)=%d 
                        and EXTRACT(YEAR FROM move.date)=%d 
                        and journal.company_id = %d"""%(today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(receipt_vouchers_query)
        receipt_vouchers_amount = cr.fetchall()
        portal_receipt_vouchers_query = """
                               select array_agg(payment.id),sum(payment.amount)
                               from account_payment as payment
                               LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                               LEFT JOIN account_move move ON payment.move_id=move.id
                               WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound')
                               and payment.journal_id in (778,794) and payment.cargo_sale_order_id is null 
                               and EXTRACT(MONTH FROM move.date)=%d 
                               and EXTRACT(YEAR FROM move.date)=%d 
                               and journal.company_id = %d"""%(today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(portal_receipt_vouchers_query)
        portal_receipt_vouchers_amount = cr.fetchall()
        app_receipt_vouchers_query = """
                               select array_agg(payment.id),sum(payment.amount)
                               from account_payment as payment
                               LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                               LEFT JOIN account_move move ON payment.move_id=move.id
                               WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound')
                               and payment.journal_id in (778,794) and payment.cargo_sale_order_id is not null 
                               and EXTRACT(MONTH FROM move.date)=%d 
                               and EXTRACT(YEAR FROM move.date)=%d 
                               and journal.company_id = %d"""%(today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(app_receipt_vouchers_query)
        app_receipt_vouchers_amount = cr.fetchall()
        payment_vouchers_query = """
                               select array_agg(payment.id),sum(payment.amount)
                               from account_payment as payment
                               LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                               LEFT JOIN account_move move ON payment.move_id=move.id
                               WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('outbound') 
                               and EXTRACT(MONTH FROM move.date)=%d 
                               and EXTRACT(YEAR FROM move.date)=%d 
                               and journal.company_id = %d"""%(today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(payment_vouchers_query)
        payment_vouchers_amount = cr.fetchall()

        fuel_vouchers_query = """
                               select array_agg(payment.id),sum(payment.amount)
                               from account_payment as payment
                               LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                               LEFT JOIN account_move move ON payment.move_id=move.id
                               WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('outbound') 
                               and payment.fleet_trip_id is not null and EXTRACT(MONTH FROM move.date)=%d 
                               and EXTRACT(YEAR FROM move.date)=%d 
                               and journal.company_id = %d"""%(today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(fuel_vouchers_query)
        fuel_vouchers_amount = cr.fetchall()
        payments = {
            'receipt_vouchers_amount': receipt_vouchers_amount[0][1] if receipt_vouchers_amount[0][1] != None else 0.00,
            'receipt_vouchers_ids': receipt_vouchers_amount[0][0] if receipt_vouchers_amount[0][0] != None else [],
            'portal_receipt_vouchers_amount': portal_receipt_vouchers_amount[0][1] if portal_receipt_vouchers_amount[0][
                                                                                          1] != None else 0.00,
            'portal_receipt_vouchers_ids': portal_receipt_vouchers_amount[0][0] if portal_receipt_vouchers_amount[0][
                                                                                       0] != None else [],
            'app_receipt_vouchers_amount': app_receipt_vouchers_amount[0][1] if app_receipt_vouchers_amount[0][
                                                                                    1] != None else 0.00,
            'app_receipt_vouchers_ids': app_receipt_vouchers_amount[0][0] if app_receipt_vouchers_amount[0][
                                                                                 0] != None else [],
            'payment_vouchers_amount': payment_vouchers_amount[0][1] if payment_vouchers_amount[0][1] != None else 0.00,
            'payment_vouchers_ids': payment_vouchers_amount[0][0] if payment_vouchers_amount[0][0] != None else [],
            'fuel_vouchers_amount': fuel_vouchers_amount[0][1] if fuel_vouchers_amount[0][1] != None else 0.00,
            'fuel_vouchers_ids': fuel_vouchers_amount[0][0] if fuel_vouchers_amount[0][0] != None else [],
        }
        print('...............payments..................', payments)
        return payments

    @api.model
    def get_payment_voucher_by_year(self):
        today = date.today()
        receipt_vouchers_query = """
                                select array_agg(payment.id),sum(payment.amount)
                                from account_payment as payment
                                LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                                LEFT JOIN account_move move ON payment.move_id=move.id
                                WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound') 
                                and EXTRACT(YEAR FROM move.date)=%d 
                                and journal.company_id = %d""" % (today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(receipt_vouchers_query)
        receipt_vouchers_amount = cr.fetchall()
        portal_receipt_vouchers_query = """
                                       select array_agg(payment.id),sum(payment.amount)
                                       from account_payment as payment
                                       LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                                       LEFT JOIN account_move move ON payment.move_id=move.id
                                       WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound')
                                       and payment.journal_id in (778,794) and payment.cargo_sale_order_id is null 
                                       and EXTRACT(YEAR FROM move.date)=%d 
                                       and journal.company_id = %d""" % (today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(portal_receipt_vouchers_query)
        portal_receipt_vouchers_amount = cr.fetchall()
        app_receipt_vouchers_query = """
                                       select array_agg(payment.id),sum(payment.amount)
                                       from account_payment as payment
                                       LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                                       LEFT JOIN account_move move ON payment.move_id=move.id
                                       WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('inbound')
                                       and payment.journal_id in (778,794) and payment.cargo_sale_order_id is not null 
                                       and EXTRACT(YEAR FROM move.date)=%d 
                                       and journal.company_id = %d""" % (today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(app_receipt_vouchers_query)
        app_receipt_vouchers_amount = cr.fetchall()
        payment_vouchers_query = """
                                       select array_agg(payment.id),sum(payment.amount)
                                       from account_payment as payment
                                       LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                                       LEFT JOIN account_move move ON payment.move_id=move.id
                                       WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('outbound') 
                                       and EXTRACT(YEAR FROM move.date)=%d 
                                       and journal.company_id = %d""" % (today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(payment_vouchers_query)
        payment_vouchers_amount = cr.fetchall()

        fuel_vouchers_query = """
                                       select array_agg(payment.id),sum(payment.amount)
                                       from account_payment as payment
                                       LEFT JOIN account_journal journal ON payment.journal_id=journal.id
                                       LEFT JOIN account_move move ON payment.move_id=move.id
                                       WHERE payment.state in ('posted','sent','reconciled') and payment.payment_type in ('outbound') 
                                       and payment.fleet_trip_id is not null and EXTRACT(YEAR FROM move.date)=%d 
                                       and journal.company_id = %d""" % (today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(fuel_vouchers_query)
        fuel_vouchers_amount = cr.fetchall()
        payments = {
            'receipt_vouchers_amount': receipt_vouchers_amount[0][1] if receipt_vouchers_amount[0][1] != None else 0.00,
            'receipt_vouchers_ids': receipt_vouchers_amount[0][0] if receipt_vouchers_amount[0][0] != None else [],
            'portal_receipt_vouchers_amount': portal_receipt_vouchers_amount[0][1] if portal_receipt_vouchers_amount[0][
                                                                                          1] != None else 0.00,
            'portal_receipt_vouchers_ids': portal_receipt_vouchers_amount[0][0] if portal_receipt_vouchers_amount[0][
                                                                                       0] != None else [],
            'app_receipt_vouchers_amount': app_receipt_vouchers_amount[0][1] if app_receipt_vouchers_amount[0][
                                                                                    1] != None else 0.00,
            'app_receipt_vouchers_ids': app_receipt_vouchers_amount[0][0] if app_receipt_vouchers_amount[0][
                                                                                 0] != None else [],
            'payment_vouchers_amount': payment_vouchers_amount[0][1] if payment_vouchers_amount[0][1] != None else 0.00,
            'payment_vouchers_ids': payment_vouchers_amount[0][0] if payment_vouchers_amount[0][0] != None else [],
            'fuel_vouchers_amount': fuel_vouchers_amount[0][1] if fuel_vouchers_amount[0][1] != None else 0.00,
            'fuel_vouchers_ids': fuel_vouchers_amount[0][0] if fuel_vouchers_amount[0][0] != None else [],
        }
        print('...............payments..................', payments)
        return payments


class TMAgreementsInherit(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale_line'

    @api.model
    def get_agreements(self):
        agreements_delivered = """
                select array_agg(agreement.id),count(agreement.id)
                from bsg_vehicle_cargo_sale_line as agreement
                WHERE agreement.state in ('Delivered')
                and agreement.company_id = %d"""%(self.env.user.company_id.id)
        cr = self._cr
        cr.execute(agreements_delivered)
        agreements_delivered_amount = cr.fetchall()
        agreements_draft = """
                        select array_agg(agreement.id),count(agreement.id)
                        from bsg_vehicle_cargo_sale_line as agreement
                        WHERE agreement.state in ('confirm','on_transit')
                        and agreement.company_id = %d""" % (self.env.user.company_id.id)
        cr = self._cr
        cr.execute(agreements_draft)
        agreements_draft_amount = cr.fetchall()
        agreements = {
            'agreements_delivered_count': agreements_delivered_amount[0][1] if agreements_delivered_amount[0][1] != None else 0.00,
            'agreements_delivered_ids': agreements_delivered_amount[0][0] if agreements_delivered_amount[0][0] != None else [],
            'agreements_ready_to_ship_count': agreements_draft_amount[0][1] if agreements_draft_amount[0][1] != None else 0.00,
            'agreements_ready_to_ship_ids': agreements_draft_amount[0][0] if agreements_draft_amount[0][0] != None else [],
        }
        return agreements

class TMDTripsInherit(models.Model):
    _inherit = 'fleet.vehicle.trip'

    @api.model
    def get_all_trips(self):
        operations_trips = """
                                  select array_agg(trip.id),count(trip.id)
                                  from fleet_vehicle_trip as trip
                                  WHERE trip.state in ('progress')
                                  and trip.active=true 
                                  and trip.company_id = %d""" % (self.env.user.company_id.id)
        cr = self._cr
        cr.execute(operations_trips)
        operations_trips = cr.fetchall()
        confirmed_trips = """
                                          select array_agg(trip.id),count(trip.id)
                                          from fleet_vehicle_trip as trip
                                          WHERE trip.state in ('confirmed')
                                          and trip.active=true  
                                          and trip.company_id = %d""" % (self.env.user.company_id.id)
        cr = self._cr
        cr.execute(confirmed_trips)
        confirmed_trips = cr.fetchall()
        transit_trips = """
                                          select array_agg(trip.id),count(trip.id)
                                          from fleet_vehicle_trip as trip
                                          WHERE trip.state in ('on_transit') 
                                          and trip.active=true 
                                          and trip.company_id = %d""" % (self.env.user.company_id.id)
        cr = self._cr
        cr.execute(transit_trips)
        transit_trips = cr.fetchall()
        finished_trips = """
                        select array_agg(trip.id),count(trip.id)
                        from fleet_vehicle_trip as trip
                        WHERE trip.state in ('finished')
                        and trip.active=true 
                        and trip.company_id = %d""" % (self.env.user.company_id.id)
        cr = self._cr
        cr.execute(finished_trips)
        finished_trips = cr.fetchall()
        trips = {
            'operations_trips_amount': operations_trips[0][1] if operations_trips[0][1] != None else 0.00,
            'operations_trips_ids': operations_trips[0][0] if operations_trips[0][0] != None else [],
            'confirmed_trips_amount': confirmed_trips[0][1] if confirmed_trips[0][1] != None else 0.00,
            'confirmed_trips_ids': confirmed_trips[0][0] if confirmed_trips[0][0] != None else [],
            'transit_trips_amount': transit_trips[0][1] if transit_trips[0][1] != None else 0.00,
            'transit_trips_ids': transit_trips[0][0] if transit_trips[0][0] != None else [],
            'finished_trips_amount': finished_trips[0][1] if finished_trips[0][1] != None else 0.00,
            'finished_trips_ids': finished_trips[0][0] if finished_trips[0][0] != None else [],
        }
        return trips

    @api.model
    def get_all_trips_by_day(self):
        today = date.today()
        operations_trips = """
                                  select array_agg(trip.id),count(trip.id)
                                  from fleet_vehicle_trip as trip
                                  WHERE trip.state in ('progress') 
                                  and trip.active=true 
                                  and EXTRACT(DAY FROM trip.create_date)=%d 
                                  and EXTRACT(MONTH FROM trip.create_date)=%d 
                                  and EXTRACT(YEAR FROM trip.create_date)=%d 
                                  and trip.company_id = %d""" % (today.day,today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(operations_trips)
        operations_trips = cr.fetchall()
        confirmed_trips = """
                              select array_agg(trip.id),count(trip.id)
                              from fleet_vehicle_trip as trip
                              WHERE trip.state in ('confirmed')
                              and trip.active=true 
                              and EXTRACT(DAY FROM trip.create_date)=%d  
                              and EXTRACT(MONTH FROM trip.create_date)=%d 
                              and EXTRACT(YEAR FROM trip.create_date)=%d 
                              and trip.company_id = %d""" % (today.day,today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(confirmed_trips)
        confirmed_trips = cr.fetchall()
        transit_trips = """
                          select array_agg(trip.id),count(trip.id)
                          from fleet_vehicle_trip as trip
                          WHERE trip.state in ('on_transit') 
                          and trip.active=true 
                          and EXTRACT(DAY FROM trip.create_date)=%d 
                          and EXTRACT(MONTH FROM trip.create_date)=%d 
                          and EXTRACT(YEAR FROM trip.create_date)=%d 
                          and trip.company_id = %d""" % (today.day,today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(transit_trips)
        transit_trips = cr.fetchall()
        finished_trips = """
                            select array_agg(trip.id),count(trip.id)
                            from fleet_vehicle_trip as trip
                            WHERE trip.state in ('finished') 
                            and trip.active=true 
                            and EXTRACT(DAY FROM trip.create_date)=%d 
                            and EXTRACT(MONTH FROM trip.create_date)=%d 
                            and EXTRACT(YEAR FROM trip.create_date)=%d 
                            and trip.company_id = %d""" % (today.day,today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(finished_trips)
        finished_trips = cr.fetchall()
        trips = {
            'operations_trips_amount': operations_trips[0][1] if operations_trips[0][1] != None else 0.00,
            'operations_trips_ids': operations_trips[0][0] if operations_trips[0][0] != None else [],
            'confirmed_trips_amount': confirmed_trips[0][1] if confirmed_trips[0][1] != None else 0.00,
            'confirmed_trips_ids': confirmed_trips[0][0] if confirmed_trips[0][0] != None else [],
            'transit_trips_amount': transit_trips[0][1] if transit_trips[0][1] != None else 0.00,
            'transit_trips_ids': transit_trips[0][0] if transit_trips[0][0] != None else [],
            'finished_trips_amount': finished_trips[0][1] if finished_trips[0][1] != None else 0.00,
            'finished_trips_ids': finished_trips[0][0] if finished_trips[0][0] != None else [],
        }
        return trips

    @api.model
    def get_all_trips_by_week(self):
        today = date.today()
        operations_trips = """
                                  select array_agg(trip.id),count(trip.id)
                                  from fleet_vehicle_trip as trip
                                  WHERE trip.state in ('progress') 
                                  and trip.active=true 
                                  and EXTRACT(WEEK FROM trip.create_date)=%d 
                                  and EXTRACT(YEAR FROM trip.create_date)=%d
                                  and trip.company_id = %d""" % (today.isocalendar()[1], today.isocalendar()[0],self.env.user.company_id.id)
        cr = self._cr
        cr.execute(operations_trips)
        operations_trips = cr.fetchall()
        confirmed_trips = """
                                          select array_agg(trip.id),count(trip.id)
                                          from fleet_vehicle_trip as trip
                                          WHERE trip.state in ('confirmed') 
                                          and trip.active=true 
                                          and EXTRACT(WEEK FROM trip.create_date)=%d 
                                          and EXTRACT(YEAR FROM trip.create_date)=%d
                                          and trip.company_id = %d""" % (today.isocalendar()[1], today.isocalendar()[0],self.env.user.company_id.id)
        cr = self._cr
        cr.execute(confirmed_trips)
        confirmed_trips = cr.fetchall()
        transit_trips = """
                                          select array_agg(trip.id),count(trip.id)
                                          from fleet_vehicle_trip as trip
                                          WHERE trip.state in ('on_transit')
                                          and trip.active=true  
                                          and EXTRACT(WEEK FROM trip.create_date)=%d 
                                          and EXTRACT(YEAR FROM trip.create_date)=%d
                                          and trip.company_id = %d""" % (today.isocalendar()[1], today.isocalendar()[0],self.env.user.company_id.id)
        cr = self._cr
        cr.execute(transit_trips)
        transit_trips = cr.fetchall()
        finished_trips = """
                            select array_agg(trip.id),count(trip.id)
                            from fleet_vehicle_trip as trip
                            WHERE trip.state in ('finished')
                            and trip.active=true 
                            and EXTRACT(WEEK FROM trip.create_date)=%d 
                            and EXTRACT(YEAR FROM trip.create_date)=%d      
                            and trip.company_id = %d""" % (today.isocalendar()[1], today.isocalendar()[0],self.env.user.company_id.id)
        cr = self._cr
        cr.execute(finished_trips)
        finished_trips = cr.fetchall()
        trips = {
            'operations_trips_amount': operations_trips[0][1] if operations_trips[0][1] != None else 0.00,
            'operations_trips_ids': operations_trips[0][0] if operations_trips[0][0] != None else [],
            'confirmed_trips_amount': confirmed_trips[0][1] if confirmed_trips[0][1] != None else 0.00,
            'confirmed_trips_ids': confirmed_trips[0][0] if confirmed_trips[0][0] != None else [],
            'transit_trips_amount': transit_trips[0][1] if transit_trips[0][1] != None else 0.00,
            'transit_trips_ids': transit_trips[0][0] if transit_trips[0][0] != None else [],
            'finished_trips_amount': finished_trips[0][1] if finished_trips[0][1] != None else 0.00,
            'finished_trips_ids': finished_trips[0][0] if finished_trips[0][0] != None else [],
        }
        return trips

    @api.model
    def get_all_trips_by_month(self):
        today = date.today()
        operations_trips = """
                           select array_agg(trip.id),count(trip.id)
                           from fleet_vehicle_trip as trip
                           WHERE trip.state in ('progress') 
                           and trip.active=true 
                           and EXTRACT(MONTH FROM trip.create_date)=%d 
                           and EXTRACT(YEAR FROM trip.create_date)=%d 
                           and trip.company_id = %d""" % (today.month, today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(operations_trips)
        operations_trips = cr.fetchall()
        confirmed_trips = """
                                   select array_agg(trip.id),count(trip.id)
                                   from fleet_vehicle_trip as trip
                                   WHERE trip.state in ('confirmed') 
                                   and trip.active=true 
                                   and EXTRACT(MONTH FROM trip.create_date)=%d 
                                   and EXTRACT(YEAR FROM trip.create_date)=%d 
                                   and trip.company_id = %d""" % (today.month, today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(confirmed_trips)
        confirmed_trips = cr.fetchall()
        transit_trips = """
                                   select array_agg(trip.id),count(trip.id)
                                   from fleet_vehicle_trip as trip
                                   WHERE trip.state in ('on_transit') 
                                   and trip.active=true 
                                   and EXTRACT(MONTH FROM trip.create_date)=%d 
                                   and EXTRACT(YEAR FROM trip.create_date)=%d 
                                   and trip.company_id = %d""" % (today.month, today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(transit_trips)
        transit_trips = cr.fetchall()
        finished_trips = """
                                   select array_agg(trip.id),count(trip.id)
                                   from fleet_vehicle_trip as trip
                                   WHERE trip.state in ('finished') 
                                   and trip.active=true 
                                   and EXTRACT(MONTH FROM trip.create_date)=%d 
                                   and EXTRACT(YEAR FROM trip.create_date)=%d 
                                   and trip.company_id = %d""" % (today.month, today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(finished_trips)
        finished_trips = cr.fetchall()
        trips = {
            'operations_trips_amount': operations_trips[0][1] if operations_trips[0][1] != None else 0.00,
            'operations_trips_ids': operations_trips[0][0] if operations_trips[0][0] != None else [],
            'confirmed_trips_amount': confirmed_trips[0][1] if confirmed_trips[0][1] != None else 0.00,
            'confirmed_trips_ids': confirmed_trips[0][0] if confirmed_trips[0][0] != None else [],
            'transit_trips_amount': transit_trips[0][1] if transit_trips[0][1] != None else 0.00,
            'transit_trips_ids': transit_trips[0][0] if transit_trips[0][0] != None else [],
            'finished_trips_amount': finished_trips[0][1] if finished_trips[0][1] != None else 0.00,
            'finished_trips_ids': finished_trips[0][0] if finished_trips[0][0] != None else [],
        }
        return trips

    @api.model
    def get_all_trips_by_year(self):
        today = date.today()
        operations_trips = """
                                   select array_agg(trip.id),count(trip.id)
                                   from fleet_vehicle_trip as trip
                                   WHERE trip.state in ('progress') 
                                   and trip.active=true 
                                   and EXTRACT(YEAR FROM trip.create_date)=%d  
                                   and trip.company_id = %d""" % (today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(operations_trips)
        operations_trips = cr.fetchall()
        confirmed_trips = """
                                           select array_agg(trip.id),count(trip.id)
                                           from fleet_vehicle_trip as trip
                                           WHERE trip.state in ('confirmed') 
                                           and trip.active=true 
                                           and EXTRACT(YEAR FROM trip.create_date)=%d 
                                           and trip.company_id = %d""" % (today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(confirmed_trips)
        confirmed_trips = cr.fetchall()
        transit_trips = """
                                           select array_agg(trip.id),count(trip.id)
                                           from fleet_vehicle_trip as trip
                                           WHERE trip.state in ('on_transit') 
                                           and trip.active=true 
                                           and EXTRACT(YEAR FROM trip.create_date)=%d  
                                           and trip.company_id = %d""" % (today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(transit_trips)
        transit_trips = cr.fetchall()
        finished_trips = """
                                   select array_agg(trip.id),count(trip.id)
                                   from fleet_vehicle_trip as trip
                                   WHERE trip.state in ('finished') 
                                   and trip.active=true 
                                   and EXTRACT(YEAR FROM trip.create_date)=%d 
                                   and trip.company_id = %d""" % (today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(finished_trips)
        finished_trips = cr.fetchall()
        trips = {
            'operations_trips_amount': operations_trips[0][1] if operations_trips[0][1] != None else 0.00,
            'operations_trips_ids': operations_trips[0][0] if operations_trips[0][0] != None else [],
            'confirmed_trips_amount': confirmed_trips[0][1] if confirmed_trips[0][1] != None else 0.00,
            'confirmed_trips_ids': confirmed_trips[0][0] if confirmed_trips[0][0] != None else [],
            'transit_trips_amount': transit_trips[0][1] if transit_trips[0][1] != None else 0.00,
            'transit_trips_ids': transit_trips[0][0] if transit_trips[0][0] != None else [],
            'finished_trips_amount': finished_trips[0][1] if finished_trips[0][1] != None else 0.00,
            'finished_trips_ids': finished_trips[0][0] if finished_trips[0][0] != None else [],
        }
        return trips

class TMDVehiclesInherit(models.Model):
    _inherit = 'fleet.vehicle'

    @api.model
    def get_all_vehicles(self):
        vehicles_in_service = """
                select array_agg(vehicle.id),count(vehicle.id)
                from fleet_vehicle as vehicle 
                LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                WHERE v_state.code in ('L') 
                and vehicle.active=true
                and vehicle.company_id = %d"""%(self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_in_service)
        vehicles_in_service = cr.fetchall()
        vehicles_in_maintenance = """
                       select array_agg(vehicle.id),count(vehicle.id)
                       from fleet_vehicle as vehicle 
                       LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                       WHERE v_state.code in ('M') 
                       and vehicle.active=true
                       and vehicle.company_id = %d"""%(self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_in_maintenance)
        vehicles_in_maintenance = cr.fetchall()
        vehicles_unlinked = """
                              select array_agg(vehicle.id),count(vehicle.id)
                              from fleet_vehicle as vehicle 
                              LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                              WHERE v_state.code in ('UN') 
                              and vehicle.active=true
                              and vehicle.company_id = %d""" %(self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_unlinked)
        vehicles_unlinked = cr.fetchall()
        vehicles = {
            'vehicles_in_service_amount': vehicles_in_service[0][1] if vehicles_in_service[0][1] != None else 0.00,
            'vehicles_in_service_ids': vehicles_in_service[0][0] if vehicles_in_service[0][0] != None else [],
            'vehicles_in_maintenance_amount': vehicles_in_maintenance[0][1] if vehicles_in_maintenance[0][1] != None else 0.00,
            'vehicles_in_maintenance_ids': vehicles_in_maintenance[0][0] if vehicles_in_maintenance[0][0] != None else [],
            'vehicles_unlinked_amount': vehicles_unlinked[0][1] if vehicles_unlinked[0][1] != None else 0.00,
            'vehicles_unlinked_ids': vehicles_unlinked[0][0] if vehicles_unlinked[0][0] != None else [],
        }
        return vehicles

    @api.model
    def get_all_vehicles_by_day(self):
        today = date.today()
        vehicles_in_service = """
                   select array_agg(vehicle.id),count(vehicle.id)
                   from fleet_vehicle as vehicle 
                   LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                   WHERE v_state.code in ('L') 
                   and vehicle.active=true
                   and EXTRACT(DAY FROM vehicle.create_date)=%d and EXTRACT(MONTH FROM vehicle.create_date)=%d 
                   and EXTRACT(YEAR FROM vehicle.create_date)=%d
                   and vehicle.company_id = %d""" % (today.day,today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_in_service)
        vehicles_in_service = cr.fetchall()
        vehicles_in_maintenance = """
                          select array_agg(vehicle.id),count(vehicle.id)
                          from fleet_vehicle as vehicle 
                          LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                          WHERE v_state.code in ('M')
                          and vehicle.active=true
                          and EXTRACT(DAY FROM vehicle.create_date)=%d and EXTRACT(MONTH FROM vehicle.create_date)=%d 
                          and EXTRACT(YEAR FROM vehicle.create_date)=%d
                          and vehicle.company_id = %d""" % (today.day,today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_in_maintenance)
        vehicles_in_maintenance = cr.fetchall()
        vehicles_unlinked = """
                                 select array_agg(vehicle.id),count(vehicle.id)
                                 from fleet_vehicle as vehicle 
                                 LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                                 WHERE v_state.code in ('UN') 
                                 and vehicle.active=true
                                 and EXTRACT(DAY FROM vehicle.create_date)=%d and EXTRACT(MONTH FROM vehicle.create_date)=%d 
                                 and EXTRACT(YEAR FROM vehicle.create_date)=%d
                                 and vehicle.company_id = %d""" % (today.day,today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_unlinked)
        vehicles_unlinked = cr.fetchall()
        vehicles = {
            'vehicles_in_service_amount': vehicles_in_service[0][1] if vehicles_in_service[0][1] != None else 0.00,
            'vehicles_in_service_ids': vehicles_in_service[0][0] if vehicles_in_service[0][0] != None else [],
            'vehicles_in_maintenance_amount': vehicles_in_maintenance[0][1] if vehicles_in_maintenance[0][
                                                                                   1] != None else 0.00,
            'vehicles_in_maintenance_ids': vehicles_in_maintenance[0][0] if vehicles_in_maintenance[0][
                                                                                0] != None else [],
            'vehicles_unlinked_amount': vehicles_unlinked[0][1] if vehicles_unlinked[0][1] != None else 0.00,
            'vehicles_unlinked_ids': vehicles_unlinked[0][0] if vehicles_unlinked[0][0] != None else [],
        }
        return vehicles

    @api.model
    def get_all_vehicles_by_week(self):
        today = date.today()
        vehicles_in_service = """
                   select array_agg(vehicle.id),count(vehicle.id)
                   from fleet_vehicle as vehicle 
                   LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                   WHERE v_state.code in ('L') 
                   and vehicle.active=true
                   and EXTRACT(WEEK FROM vehicle.create_date)=%d 
                   and EXTRACT(YEAR FROM vehicle.create_date)=%d
                   and vehicle.company_id = %d""" % (today.isocalendar()[1], today.isocalendar()[0],self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_in_service)
        vehicles_in_service = cr.fetchall()
        vehicles_in_maintenance = """
                          select array_agg(vehicle.id),count(vehicle.id)
                          from fleet_vehicle as vehicle 
                          LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                          WHERE v_state.code in ('M') 
                          and vehicle.active=true
                          and EXTRACT(WEEK FROM vehicle.create_date)=%d 
                          and EXTRACT(YEAR FROM vehicle.create_date)=%d
                          and vehicle.company_id = %d""" % (today.isocalendar()[1], today.isocalendar()[0],self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_in_maintenance)
        vehicles_in_maintenance = cr.fetchall()
        vehicles_unlinked = """
                                 select array_agg(vehicle.id),count(vehicle.id)
                                 from fleet_vehicle as vehicle 
                                 LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                                 WHERE v_state.code in ('UN') 
                                 and vehicle.active=true
                                 and EXTRACT(WEEK FROM vehicle.create_date)=%d 
                                 and EXTRACT(YEAR FROM vehicle.create_date)=%d
                                 and vehicle.company_id = %d""" % (today.isocalendar()[1], today.isocalendar()[0],self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_unlinked)
        vehicles_unlinked = cr.fetchall()
        vehicles = {
            'vehicles_in_service_amount': vehicles_in_service[0][1] if vehicles_in_service[0][1] != None else 0.00,
            'vehicles_in_service_ids': vehicles_in_service[0][0] if vehicles_in_service[0][0] != None else [],
            'vehicles_in_maintenance_amount': vehicles_in_maintenance[0][1] if vehicles_in_maintenance[0][
                                                                                   1] != None else 0.00,
            'vehicles_in_maintenance_ids': vehicles_in_maintenance[0][0] if vehicles_in_maintenance[0][
                                                                                0] != None else [],
            'vehicles_unlinked_amount': vehicles_unlinked[0][1] if vehicles_unlinked[0][1] != None else 0.00,
            'vehicles_unlinked_ids': vehicles_unlinked[0][0] if vehicles_unlinked[0][0] != None else [],
        }
        return vehicles

    @api.model
    def get_all_vehicles_by_month(self):
        today = date.today()
        vehicles_in_service = """
                           select array_agg(vehicle.id),count(vehicle.id)
                           from fleet_vehicle as vehicle 
                           LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                           WHERE v_state.code in ('L') 
                           and vehicle.active=true
                           and EXTRACT(MONTH FROM vehicle.create_date)=%d 
                           and EXTRACT(YEAR FROM vehicle.create_date)=%d
                           and vehicle.company_id = %d""" % (today.month, today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_in_service)
        vehicles_in_service = cr.fetchall()
        vehicles_in_maintenance = """
                                  select array_agg(vehicle.id),count(vehicle.id)
                                  from fleet_vehicle as vehicle 
                                  LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                                  WHERE v_state.code in ('M')
                                  and vehicle.active=true
                                  and EXTRACT(MONTH FROM vehicle.create_date)=%d 
                                  and EXTRACT(YEAR FROM vehicle.create_date)=%d
                                  and vehicle.company_id = %d""" % (today.month, today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_in_maintenance)
        vehicles_in_maintenance = cr.fetchall()
        vehicles_unlinked = """
                                         select array_agg(vehicle.id),count(vehicle.id)
                                         from fleet_vehicle as vehicle 
                                         LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                                         WHERE v_state.code in ('UN') 
                                         and vehicle.active=true
                                         and EXTRACT(MONTH FROM vehicle.create_date)=%d 
                                         and EXTRACT(YEAR FROM vehicle.create_date)=%d
                                         and vehicle.company_id = %d""" % (today.month, today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_unlinked)
        vehicles_unlinked = cr.fetchall()
        vehicles = {
            'vehicles_in_service_amount': vehicles_in_service[0][1] if vehicles_in_service[0][1] != None else 0.00,
            'vehicles_in_service_ids': vehicles_in_service[0][0] if vehicles_in_service[0][0] != None else [],
            'vehicles_in_maintenance_amount': vehicles_in_maintenance[0][1] if vehicles_in_maintenance[0][
                                                                                   1] != None else 0.00,
            'vehicles_in_maintenance_ids': vehicles_in_maintenance[0][0] if vehicles_in_maintenance[0][
                                                                                0] != None else [],
            'vehicles_unlinked_amount': vehicles_unlinked[0][1] if vehicles_unlinked[0][1] != None else 0.00,
            'vehicles_unlinked_ids': vehicles_unlinked[0][0] if vehicles_unlinked[0][0] != None else [],
        }
        return vehicles

    @api.model
    def get_all_vehicles_by_year(self):
        today = date.today()
        vehicles_in_service = """
                           select array_agg(vehicle.id),count(vehicle.id)
                           from fleet_vehicle as vehicle 
                           LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                           WHERE v_state.code in ('L') 
                           and vehicle.active=true
                           and EXTRACT(YEAR FROM vehicle.create_date)=%d
                           and vehicle.company_id = %d""" % (today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_in_service)
        vehicles_in_service = cr.fetchall()
        vehicles_in_maintenance = """
                                  select array_agg(vehicle.id),count(vehicle.id)
                                  from fleet_vehicle as vehicle 
                                  LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                                  WHERE v_state.code in ('M')
                                  and vehicle.active=true
                                  and EXTRACT(YEAR FROM vehicle.create_date)=%d
                                  and vehicle.company_id = %d""" % (today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_in_maintenance)
        vehicles_in_maintenance = cr.fetchall()
        vehicles_unlinked = """
                                         select array_agg(vehicle.id),count(vehicle.id)
                                         from fleet_vehicle as vehicle 
                                         LEFT JOIN fleet_vehicle_state v_state ON vehicle.state_id=v_state.id
                                         WHERE v_state.code in ('UN') 
                                         and vehicle.active=true
                                         and EXTRACT(YEAR FROM vehicle.create_date)=%d
                                         and vehicle.company_id = %d""" % (today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(vehicles_unlinked)
        vehicles_unlinked = cr.fetchall()
        vehicles = {
            'vehicles_in_service_amount': vehicles_in_service[0][1] if vehicles_in_service[0][1] != None else 0.00,
            'vehicles_in_service_ids': vehicles_in_service[0][0] if vehicles_in_service[0][0] != None else [],
            'vehicles_in_maintenance_amount': vehicles_in_maintenance[0][1] if vehicles_in_maintenance[0][
                                                                                   1] != None else 0.00,
            'vehicles_in_maintenance_ids': vehicles_in_maintenance[0][0] if vehicles_in_maintenance[0][
                                                                                0] != None else [],
            'vehicles_unlinked_amount': vehicles_unlinked[0][1] if vehicles_unlinked[0][1] != None else 0.00,
            'vehicles_unlinked_ids': vehicles_unlinked[0][0] if vehicles_unlinked[0][0] != None else [],
        }
        return vehicles


class TMDVehiclesInherit(models.Model):
    _inherit = 'purchase.req'

    @api.model
    def get_all_purchase_reqs(self):
        purchase_requests = """
                select array_agg(purchase.id),count(purchase.id)
                from purchase_req as purchase 
                WHERE state in ('done')
                and purchase.company_id = %d"""%(self.env.user.company_id.id)
        cr = self._cr
        cr.execute(purchase_requests)
        purchase_requests = cr.fetchall()
        purchase_requests = {
            'purchase_requests_amount': purchase_requests[0][1] if purchase_requests[0][1] != None else 0.00,
            'purchase_requests_ids': purchase_requests[0][0] if purchase_requests[0][0] != None else [],
        }
        return purchase_requests

    @api.model
    def get_all_purchase_reqs_by_day(self):
        today = date.today()
        purchase_requests = """
                    select array_agg(purchase.id),count(purchase.id)
                    from purchase_req as purchase 
                    WHERE state in ('done') 
                    and EXTRACT(DAY FROM purchase.create_date)=%d and EXTRACT(MONTH FROM purchase.create_date)=%d 
                    and EXTRACT(YEAR FROM purchase.create_date)=%d
                    and purchase.company_id = %d""" % (today.day,today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(purchase_requests)
        purchase_requests = cr.fetchall()
        purchase_requests = {
            'purchase_requests_amount': purchase_requests[0][1] if purchase_requests[0][1] != None else 0.00,
            'purchase_requests_ids': purchase_requests[0][0] if purchase_requests[0][0] != None else [],
        }
        return purchase_requests

    @api.model
    def get_all_purchase_reqs_by_week(self):
        today = date.today()
        purchase_requests = """
                    select array_agg(purchase.id),count(purchase.id)
                    from purchase_req as purchase 
                    WHERE state in ('done') 
                    and EXTRACT(WEEK FROM purchase.create_date)=%d 
                    and EXTRACT(YEAR FROM purchase.create_date)=%d
                    and purchase.company_id = %d""" % (today.isocalendar()[1], today.isocalendar()[0],self.env.user.company_id.id)
        cr = self._cr
        cr.execute(purchase_requests)
        purchase_requests = cr.fetchall()
        purchase_requests = {
            'purchase_requests_amount': purchase_requests[0][1] if purchase_requests[0][1] != None else 0.00,
            'purchase_requests_ids': purchase_requests[0][0] if purchase_requests[0][0] != None else [],
        }
        return purchase_requests

    @api.model
    def get_all_purchase_reqs_by_month(self):
        today = date.today()
        purchase_requests = """
                            select array_agg(purchase.id),count(purchase.id)
                            from purchase_req as purchase 
                            WHERE state in ('done') 
                            and EXTRACT(MONTH FROM purchase.create_date)=%d 
                            and EXTRACT(YEAR FROM purchase.create_date)=%d
                            and purchase.company_id = %d""" % (today.month,today.year,self.env.user.company_id.id)
        cr = self._cr
        cr.execute(purchase_requests)
        purchase_requests = cr.fetchall()
        purchase_requests = {
            'purchase_requests_amount': purchase_requests[0][1] if purchase_requests[0][1] != None else 0.00,
            'purchase_requests_ids': purchase_requests[0][0] if purchase_requests[0][0] != None else [],
        }
        return purchase_requests

    @api.model
    def get_all_purchase_reqs_by_year(self):
        today = date.today()
        purchase_requests = """
                            select array_agg(purchase.id),count(purchase.id)
                            from purchase_req as purchase 
                            WHERE state in ('done') 
                            and EXTRACT(YEAR FROM purchase.create_date)=%d
                            and purchase.company_id = %d""" % (today.year, self.env.user.company_id.id)
        cr = self._cr
        cr.execute(purchase_requests)
        purchase_requests = cr.fetchall()
        purchase_requests = {
            'purchase_requests_amount': purchase_requests[0][1] if purchase_requests[0][1] != None else 0.00,
            'purchase_requests_ids': purchase_requests[0][0] if purchase_requests[0][0] != None else [],
        }
        return purchase_requests

class TMDEmployeesInherit(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def get_all_employees(self):
        on_job_employees = """
                select array_agg(employee.id),count(employee.id)
                from hr_employee as employee 
                WHERE state in ('on_job')
                and employee.active=true
                and employee.company_id = %d"""%(self.env.user.company_id.id)
        cr = self._cr
        cr.execute(on_job_employees)
        on_job_employees = cr.fetchall()
        on_leave_employees = """
                        select array_agg(employee.id),count(employee.id)
                        from hr_employee as employee 
                        WHERE state in ('on_leave')
                        and employee.active=true
                        and employee.company_id = %d""" % (self.env.user.company_id.id)
        cr = self._cr
        cr.execute(on_leave_employees)
        on_leave_employees = cr.fetchall()
        saudis = """
                    select count(employee.id)
                    from hr_employee as employee 
                    WHERE employee.state in ('on_leave','on_job','trail_period')
                    and employee.active=true
                    and employee.employee_type in ('citizen')
                    and employee.company_id = %d""" % (self.env.user.company_id.id)
        cr = self._cr
        cr.execute(saudis)
        saudis = cr.fetchall()
        non_saudis = """
                            select count(employee.id)
                            from hr_employee as employee 
                            WHERE employee.state in ('on_leave','on_job','trail_period')
                            and employee.active=true
                            and employee.employee_type in ('foreign')
                            and employee.company_id = %d""" % (self.env.user.company_id.id)
        cr = self._cr
        cr.execute(non_saudis)
        non_saudis = cr.fetchall()
        saudis_count = 0
        non_saudis_count = 0
        if saudis[0][0] != None:
            saudis_count = saudis[0][0]
        if non_saudis[0][0] != None:
            non_saudis_count = non_saudis[0][0]
        total_count = saudis_count + non_saudis_count
        saudization_percentage = (saudis_count/total_count)*100
        saudization_percentage = round(saudization_percentage,2)

        employees_on_trial = """
                                    select array_agg(employee.id),count(employee.id)
                                    from hr_employee as employee 
                                    WHERE employee.state in ('trail_period')
                                    and employee.active=true
                                    and employee.company_id = %d""" % (self.env.user.company_id.id)
        cr = self._cr
        cr.execute(employees_on_trial)
        employees_on_trial = cr.fetchall()


        employees = {
            'on_job_employees_amount': on_job_employees[0][1] if on_job_employees[0][1] != None else 0.00,
            'on_job_employees_ids': on_job_employees[0][0] if on_job_employees[0][0] != None else [],
            'on_leave_employees_amount': on_leave_employees[0][1] if on_leave_employees[0][1] != None else 0.00,
            'on_leave_employees_ids': on_leave_employees[0][0] if on_leave_employees[0][0] != None else [],
            'employees_on_trial_amount': employees_on_trial[0][1] if employees_on_trial[0][1] != None else 0.00,
            'employees_on_trial_ids': employees_on_trial[0][0] if employees_on_trial[0][0] != None else [],
            'saudization_percentage':saudization_percentage
        }
        return employees

class TMDDecisionsInherit(models.Model):
    _inherit = 'employees.appointment'

    @api.model
    def get_all_decisions(self):
        confirmed_decisions = """
                select array_agg(decision.id),count(decision.id)
                from employees_appointment as decision 
                WHERE state in ('approved')
                and decision.company_id = %d""" % (self.env.user.company_id.id)
        cr = self._cr
        cr.execute(confirmed_decisions)
        confirmed_decisions = cr.fetchall()
        decisions = {
            'confirmed_decisions_amount': confirmed_decisions[0][1] if confirmed_decisions[0][1] != None else 0.00,
            'confirmed_decisions_ids': confirmed_decisions[0][0] if confirmed_decisions[0][0] != None else [],
        }
        return decisions

class TMDLeavesInherit(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def get_all_leaves(self):
        all_leaves = """
                select array_agg(leave.id),count(leave.id)
                from hr_leave as leave 
                WHERE state not in ('cancel','refuse')
                """
        cr = self._cr
        cr.execute(all_leaves)
        all_leaves = cr.fetchall()
        leaves = {
            'all_leaves_amount': all_leaves[0][1] if all_leaves[0][1] != None else 0.00,
            'all_leaves_ids': all_leaves[0][0] if all_leaves[0][0] != None else [],
        }
        return leaves

class TMDEffectiveRequestsInherit(models.Model):
    _inherit = 'effect.request'

    @api.model
    def get_all_effective_requests(self):
        all_eff_requests = """
                select array_agg(request.id),count(request.id)
                from effect_request as request 
                WHERE state not in ('9')
                and request.company_id = %d""" % (self.env.user.company_id.id)
        cr = self._cr
        cr.execute(all_eff_requests)
        all_eff_requests = cr.fetchall()
        eff_requests = {
            'all_eff_requests_amount': all_eff_requests[0][1] if all_eff_requests[0][1] != None else 0.00,
            'all_eff_requests_ids': all_eff_requests[0][0] if all_eff_requests[0][0] != None else [],
        }
        return eff_requests

class TMDEffectiveRequestsInherit(models.Model):
    _inherit = 'hr.clearance'

    @api.model
    def get_all_clearances(self):
        clearances = """
                select array_agg(clearance.id),count(clearance.id)
                from hr_clearance as clearance 
                WHERE state not in ('cancel')
                and clearance.company_id = %d""" % (self.env.user.company_id.id)
        cr = self._cr
        cr.execute(clearances)
        clearances = cr.fetchall()
        clearances = {
            'all_clearances_amount': clearances[0][1] if clearances[0][1] != None else 0.00,
            'all_clearances_ids': clearances[0][0] if clearances[0][0] != None else [],
        }
        return clearances









