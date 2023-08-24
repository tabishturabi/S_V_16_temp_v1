import hashlib

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError

from urllib.parse import urlparse,urljoin
from odoo.tools.float_utils import float_round
import requests


import logging
_logger = logging.getLogger(__name__)

def _alrajhi_generate_signature(values,request_phrase, sha_type):
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


class Acquireralrajhi(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('alrajhi', 'alrajhi')])
    alrajhi_access_code = fields.Char(string='Access Code', required_if_provider='alrajhi')
    alrajhi_merchant_identifier = fields.Char(string='Merchant Identifier', required_if_provider='alrajhi')
    alrajhi_sha_type = fields.Selection([('sha_256', 'SHA-256'),('sha_512', 'SHA-512')], required_if_provider='alrajhi',  default='sha_256')
    alrajhi_request_phrase = fields.Char('Request Phrase', groups='base.group_user',required_if_provider='alrajhi', help='Request Phrase of alrajhi')
    alrajhi_response_phrase = fields.Char('Response Phrase', groups='base.group_user',required_if_provider='alrajhi', help='Response Phrase of alrajhi')

    @api.model
    def _get_alrajhi_urls(self, environment): 
        """ alrajhi URLS """
        if environment == 'prod':
            if self._context.get('is_refund', False):
                return {
                    'alrajhi_form_url': 'https://paymentservices.alrajhi.com/FortAPI/paymentApi'
                }
            return {
                'alrajhi_form_url': 'https://checkout.alrajhi.com/FortAPI/paymentPage',
            }
        else:
            if self._context.get('is_refund', False):
                return {
                    'alrajhi_form_url': 'https://sbpaymentservices.alrajhi.com/FortAPI/paymentApi',
                }
            return {
                'alrajhi_form_url': 'https://sbcheckout.alrajhi.com/FortAPI/paymentPage',
            }

    def filterRequestValues(self, values):
        merchant_reference = values.get('merchant_reference')
        if merchant_reference and '/' in merchant_reference:
            values['merchant_reference'] = '-'.join(merchant_reference.split('/'))
        return values

    @api.multi
    def alrajhi_form_generate_values(self, values):
        _logger.info("--alrajhi_form_values---alrajhi_form_generate_values")
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        alrajhi_form_values = dict(values)
        if values['reference'] :
            alrajhi_tx_values = {
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

            alrajhi_tx_values = self.filterRequestValues(alrajhi_tx_values)

            alrajhi_tx_values['return_url'] = '%s' % urljoin(base_url,'/payment/alrajhi/return')
            alrajhi_tx_values['signature'] = _alrajhi_generate_signature(alrajhi_tx_values,self.request_phrase, self.sha_type)
            alrajhi_tx_values['tx_url'] = self._get_alrajhi_urls(self.environment)['alrajhi_form_url']
            alrajhi_form_values.update(alrajhi_tx_values)
            alrajhi_form_values.update({'reference': alrajhi_tx_values.get('merchant_reference')})
            _logger.info("--alrajhi_form_values--%r---",alrajhi_form_values)
        else:
            _logger.info("--NO refernece values---values-----")
        return alrajhi_form_values


    @api.multi
    def alrajhi_get_form_action_url(self):
        return self._get_alrajhi_urls(self.environment)['alrajhi_form_url']

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'


    @api.model
    def _alrajhi_form_get_tx_from_data(self, data):
        if data.get('merchant_reference'):

            # Fix in case of invoice
            # Matching the transaction reference with the reference send to the merchant
            # reference_arr = data.get('merchant_reference').split('-')
            # reference = '/'.join(reference_arr[:-1]) + '-' + reference_arr[-1]
            reference = data.get('merchant_reference')
            if not reference:
                error_msg = _(
                    'alrajhi: received data with missing '
                    'reference (%s)') % (reference)
                _logger.info(error_msg)
                raise ValidationError(error_msg)
            transaction = self.search([('reference', '=', reference)])
            if not transaction:
                error_msg = (_('alrajhi: received data for reference %s; no '
                                'order found') % (reference))
                raise ValidationError(error_msg)
            elif len(transaction) > 1:
                error_msg = (_('alrajhi: received data for reference %s; '
                                'multiple orders found') % (reference))
                raise ValidationError(error_msg)
            return transaction


    def _alrajhi_form_get_invalid_parameters(self, data):
        invalid_parameters, acquirer = [], self.acquirer_id
        if float(data.get('amount')) != int(float_round(self.amount*100, 2)):
            invalid_parameters.append(('Amount', float(data.get('amount')), float_round(self.amount * 100, 2)))
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(('Currency Code', data.get('currency'), self.currency_id.name))

        response_signature = data.pop('signature')
        signature = _alrajhi_generate_signature(data,acquirer.response_phrase, acquirer.sha_type)

        if response_signature != signature:
            invalid_parameters.append(('response_signature', response_signature, signature))
        return invalid_parameters

    @api.multi
    def _alrajhi_form_validate(self, data):
        res = {}
        if data.get('status') == '14':
            _logger.info(
                'Validated alrajhi payment for tx %s: '
                'set as done' % (self.reference))
            res.update(
                date=data.get('payment_date', fields.datetime.now()),
                acquirer_reference=data.get('authorization_code')
                )
            self.write(res)
            self._set_transaction_done()
            return True
        else:
            error = 'Received unrecognized data for alrajhi payment %s, set as error' % (self.reference)
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

    @api.multi
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
