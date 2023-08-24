# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
import hashlib

from odoo import api, fields, models, _
# from odoo.addons.payment.models.payment_acquirer import ValidationError

from urllib.parse import urlparse,urljoin
from odoo.tools.float_utils import float_round
import requests


import logging
_logger = logging.getLogger(__name__)

# https://albassami-staging-1388719.dev.odoo.com/website_payment/pay?reference=11111&amount=100&acquirer_id=11&order_id=3#
def _payfort_generate_signature(values,request_phrase, sha_type):
    keys = values.keys()
    keys = sorted(keys)
    sign = ""
    for k in keys:
        sign = sign + k + "=" +str(values[k])
    sign = request_phrase + sign + request_phrase
    sha_sign = ''
    if sha_type == 'sha_256':
        sha_sign = hashlib.sha256(sign.encode('utf-8')).hexdigest()
    else:
        sha_sign = hashlib.sha512(sign.encode('utf-8')).hexdigest()
    return sha_sign

class AccountInvoice(models.Model):
    _inherit = 'account.move'
    
    trans_id = fields.Many2one('payment.transaction', string='Transaction')
    show_trans_refund_button = fields.Boolean(compute="compute_show_trans_refund_button", store=True)

    @api.depends('ref','reversed_entry_id.payment_ids.payment_transaction_id.is_refunded','state', 'move_type', 'reversed_entry_id')
    def compute_show_trans_refund_button(self):
        for rec in self:
            show_trans_refund_button = False
            if rec.move_type == 'out_refund' and rec.reversed_entry_id:
                trans_id = rec.reversed_entry_id.payment_ids.mapped('payment_transaction_id')
                show_trans_refund_button = trans_id and not trans_id[0].is_refunded and rec.state == 'posted' or False
            rec.show_trans_refund_button = show_trans_refund_button
        

    
    def refund_transaction(self):
        for rec in self:
            if rec.type == 'out_refund' and rec.refund_invoice_id:
                trans_id = rec.refund_invoice_id.payment_ids.mapped('payment_transaction_id')
                if trans_id and not trans_id[0].is_refunded:
                    trans_id[0].with_context({'amount': self.amount_residual}).refund_transaction()
                    payment = self.env['account.payment'].with_context({'active_model': 'account.move', 'active_id':rec.id, 'default_amount': rec.amount_residual}).create(
                        {'payment_type': 'outbound', 
                        'partner_id': rec.partner_id.id,
                        'partner_type': 'customer', 
                        'invoice_ids': [(6, 0, [rec.id])],
                        'payment_method_id':1,
                        'app_fortid': trans_id[0].refund_trans_reference, 
                        'journal_id': rec.company_id.online_journal_id.id
                        }
                    )
                    payment.action_validate_invoice_payment()
                else:
                    raise ValidationError( not trans_id and "No Transaction Found" or "Transaction already refunded")
            
        return True

class AcquirerPayfort(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('payfort', 'Payfort')], ondelete={'payfort': 'set default'})
    access_code = fields.Char(string='Access Code', required_if_provider='payfort')
    merchant_identifier = fields.Char(string='Merchant Identifier', required_if_provider='payfort')
    sha_type = fields.Selection([('sha_256', 'SHA-256'),('sha_512', 'SHA-512')], required_if_provider='payfort',  default='sha_256')
    request_phrase = fields.Char('Request Phrase', groups='base.group_user',required_if_provider='payfort', help='Request Phrase of Payfort')
    response_phrase = fields.Char('Response Phrase', groups='base.group_user',required_if_provider='payfort', help='Response Phrase of Payfort')

    @api.model
    def _get_payfort_urls(self, environment): 
        """ PayFort URLS """
        if environment == 'prod':
            if self._context.get('is_refund', False):
                return {
                    'payfort_form_url': 'https://paymentservices.payfort.com/FortAPI/paymentApi'
                }
            return {
                'payfort_form_url': 'https://checkout.PayFort.com/FortAPI/paymentPage',
            }
        else:
            if self._context.get('is_refund', False):
                return {
                    'payfort_form_url': 'https://sbpaymentservices.payfort.com/FortAPI/paymentApi',
                }
            return {
                'payfort_form_url': 'https://sbcheckout.PayFort.com/FortAPI/paymentPage',
            }

    def filterRequestValues(self, values):
        merchant_reference = values.get('merchant_reference')
        if merchant_reference and '/' in merchant_reference:
            values['merchant_reference'] = '-'.join(merchant_reference.split('/'))
        return values

    
    def payfort_form_generate_values(self, values):
        _logger.info("--payfort_form_values---payfort_form_generate_values")
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        payfort_form_values = dict(values)
        if values['reference'] :
            payfort_tx_values = {
                'command': "PURCHASE",
                'customer_email': values['partner_email'] or values['reference'] + '@albassami.com',
                'amount' : int(float_round(values['amount'] * 100, 2)),
                'currency' :values['currency'].name,
                'customer_name': values['partner_name'],
                'merchant_reference' : values['reference'],
                'access_code' : self.access_code,
                'merchant_identifier' : self.merchant_identifier,
                'language' :'en' ,
                'eci': 'ECOMMERCE',
            }

            payfort_tx_values = self.filterRequestValues(payfort_tx_values)

            payfort_tx_values['return_url'] = '%s' % urljoin(base_url,'/payment/payfort/return')
            payfort_tx_values['signature'] = _payfort_generate_signature(payfort_tx_values,self.request_phrase, self.sha_type)
            payfort_tx_values['tx_url'] = self._get_payfort_urls(self.environment)['payfort_form_url']
            payfort_form_values.update(payfort_tx_values)
            payfort_form_values.update({'reference': payfort_tx_values.get('merchant_reference')})
            _logger.info("--payfort_form_values--%r---",payfort_form_values)
        else:
            _logger.info("--NO refernece values---values-----")
        return payfort_form_values


    
    def payfort_get_form_action_url(self):
        return self._get_payfort_urls(self.environment)['payfort_form_url']

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    is_refunded = fields.Boolean('Is Refunded', readonly=True) #TODO @GAGA reflect partial and fully refunded transactions amount == refunded_amount
    refund_trans_reference = fields.Char('Refund Transaction Reference', readonly=True)
    refunded_amount = fields.Char('Refunded Amount', readonly=True)

    
    def refund_transaction(self):
        amount = float(self._context.get('amount', 0))
        acquirer_id = self.acquirer_id
        url = acquirer_id.with_context({'is_refund': True}).payfort_get_form_action_url()
        # headers = {'Content-Type': 'application/json'}
        vals = {
            'command': 'REFUND',
            'access_code': acquirer_id.access_code,
            'merchant_identifier': acquirer_id.merchant_identifier,
            'merchant_reference':self.reference,
            'amount': int(float_round((amount or self.amount) * 100, 2)) ,
            'currency': self.currency_id and  self.currency_id.name or 'SAR',
            'language': 'en',
            'fort_id': self.app_fortid ,
            'order_description': "Refund for order %s  / %s"%(self.cargo_sale_ids and self.cargo_sale_ids[0].name or '',self.reference or '')
        }
        vals['signature'] = _payfort_generate_signature(vals,acquirer_id.request_phrase, acquirer_id.sha_type)
        response = requests.post(url, json=vals)
        if response.status_code == 200:
            res = response.json()
            if res['status'] == '06':
                self.write({'is_refunded': True,'refunded_amount':self.amount, 'refund_trans_reference':res['fort_id']})
                return True
            else:
                raise ValidationError("Refund not processed : [ %s ] %s"%(res['status'], res['response_message']))
        else:
            raise ValidationError("Refund not processed: HTTP Status Code: %s"%str(response.status_code))

        return True

    @api.model
    def _payfort_form_get_tx_from_data(self, data):
        if data.get('merchant_reference'):

            # Fix in case of invoice
            # Matching the transaction reference with the reference send to the merchant
            # reference_arr = data.get('merchant_reference').split('-')
            # reference = '/'.join(reference_arr[:-1]) + '-' + reference_arr[-1]
            reference = data.get('merchant_reference')
            if not reference:
                error_msg = _(
                    'payfort: received data with missing '
                    'reference (%s)') % (reference)
                _logger.info(error_msg)
                raise ValidationError(error_msg)
            transaction = self.search([('reference', '=', reference)])
            if not transaction:
                error_msg = (_('payfort: received data for reference %s; no '
                                'order found') % (reference))
                raise ValidationError(error_msg)
            elif len(transaction) > 1:
                error_msg = (_('payfort: received data for reference %s; '
                                'multiple orders found') % (reference))
                raise ValidationError(error_msg)
            return transaction


    def _payfort_form_get_invalid_parameters(self, data):
        invalid_parameters, acquirer = [], self.acquirer_id
        if float(data.get('amount')) != int(float_round(self.amount*100, 2)):
            invalid_parameters.append(('Amount', float(data.get('amount')), float_round(self.amount * 100, 2)))
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(('Currency Code', data.get('currency'), self.currency_id.name))

        response_signature = data.pop('signature')
        signature = _payfort_generate_signature(data,acquirer.response_phrase, acquirer.sha_type)

        if response_signature != signature:
            invalid_parameters.append(('response_signature', response_signature, signature))
        return invalid_parameters

    
    def _payfort_form_validate(self, data):
        res = {}
        if data.get('status') == '14':
            _logger.info(
                'Validated payfort payment for tx %s: '
                'set as done' % (self.reference))
            res.update(
                date=data.get('payment_date', fields.datetime.now()),
                acquirer_reference=data.get('authorization_code')
                )
            self.write(res)
            self._set_transaction_done()
            return True
        else:
            error = 'Received unrecognized data for payfort payment %s, set as error' % (self.reference)
            if data.get('response_message',False):
                #Add Error Cause
                error += str(data.get('response_message'))
            _logger.info(error)
            res.update(
                date=data.get('payment_date', fields.datetime.now()),
                state_message=error)
            self._set_transaction_error(msg=error)
            self.write(res)
            return False

    
    def _prepare_account_payment_vals(self):
        self.ensure_one()
        return {
            'amount': self.amount,
            'payment_type': 'inbound' if self.amount > 0 else 'outbound',
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_type': 'customer',
            'invoice_ids': [(6, 0, self.invoice_ids.filtered(lambda inv: inv.state == 'open').ids)],
            'journal_id': self.acquirer_id.journal_id.id,
            'company_id': self.acquirer_id.company_id.id,
            'payment_method_id': self.env.ref('payment.account_payment_method_electronic_in').id,
            'payment_token_id': self.payment_token_id and self.payment_token_id.id or None,
            'payment_transaction_id': self.id,
            'communication': self.reference,
        }

class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['tamara'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
        return res
