# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import json
import werkzeug
import logging
from datetime import date, datetime

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params

_logger = logging.getLogger(__name__)


class PaymentTamaraController(http.Controller):
    success_url = '/payment/tamara/success'
    failure_url = '/payment/tamara/failure'
    cancel_url = '/payment/tamara/cancel'
    notification_url = '/payment/tamara/notification'
    webhook_url = '/payment/tamara/webhook'
    # webhook_test = '/test'

    @http.route([success_url], type='http', auth='public', csrf=False)
    def payment_checkout_tamara_return(self, *args, **kwargs):
        try:
            is_valid_trans = request.env['payment.transaction'].sudo().with_context(
                force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).form_feedback(
                kwargs, 'tamara')
            trans = request.env['payment.transaction'].sudo().with_context(force_company=request.env.user.company_id.id,
                                                                           company_id=request.env.user.company_id.id).search(
                [('reference', '=', kwargs.get('reference'))])
            params = {}
            trans.state = 'done'
            if is_valid_trans and trans:
                if trans.state == 'done' and not trans.is_processed:
                    trans._post_process_after_done()
                trans.signature = kwargs.get('signature')
            if trans and hasattr(trans, 'tamara_transaction_ids') and trans.tamara_transaction_ids:
                url = trans.tamara_transaction_ids[0].sudo().get_portal_url()
                params['success'] = 'pay_cargo'
                trans.sudo().tamara_transaction_ids.write({"state": 'registered'})
                return werkzeug.utils.redirect(_build_url_w_params(url, params))
            if trans and hasattr(trans, 'cargo_sale_line_ids') and trans.cargo_sale_line_ids:
                url = trans.cargo_sale_line_ids[0].sudo().get_portal_url()
                params['success'] = 'pay_cargo'
                trans.sudo().tamara_transaction_ids.write({"state": 'registered'})
                return werkzeug.utils.redirect(_build_url_w_params(url, params))
            if trans and trans.invoice_ids and not hasattr(trans, 'tamara_transaction_ids') and not hasattr(trans,
                                                                                                            'cargo_sale_line_ids'):
                url = trans.invoice_ids[0].sudo().with_context(force_company=request.env.user.company_id.id,
                                                               company_id=request.env.user.company_id.id).get_portal_url()
                params['success'] = 'pay_cargo'
                trans.sudo().tamara_transaction_ids.write({"state": 'registered'})
                return werkzeug.utils.redirect(_build_url_w_params(url, params))
        except ValidationError:
            _logger.exception('Unable to validate the Tamara payment')
        return werkzeug.utils.redirect('/payment/process')

    # @http.route([webhook_test], method=['POST'], type='http', auth='public', csrf=False)
    # def payment_webhook_test(self, *args, **kwargs):
    #     print("PPPPPPPPPPPPPPPPPPPPP")
    #     return werkzeug.utils.redirect('/web?debug=1#id=1059287&action=1382&model=bsg_vehicle_cargo_sale&view_type=form&menu_id=178')

    @http.route([failure_url, cancel_url], type='http', auth='public', csrf=False)
    def payment_checkout_tamara_return_failure_cancel(self, *args, **kwargs):
        try:
            trans = request.env['payment.transaction'].sudo().with_context(force_company=request.env.user.company_id.id,
                                                                           company_id=request.env.user.company_id.id).search(
                [('reference', '=', kwargs.get('reference'))])
            if trans and trans.invoice_ids:
                trans.invoice_ids.state = 'draft'
                trans.state = 'draft'
        except ValidationError:
            _logger.exception('Unable to validate the Tamara payment')
        return werkzeug.utils.redirect('/payment/process')

    @http.route([notification_url], type='json', auth='public', method=['POST'], csrf=False)
    def payment_checkout_tamara_notification(self, *args, **kwargs):
        _logger.info('Tamara: Entering Notification with post data %s', )

    @http.route([webhook_url], type='json', auth='public', method=['POST'], csrf=False)
    def payment_webhook_tamara_notification(self, *args, **kwargs):
        cargo_sale_id = False
        # if request.httprequest.headers.environ.get('HTTP_SECRET_KEY') == "":
        _logger.info(
            'Tamara: %%%%%%%%%%%%%%%%%%%%%%% WEBHOOK Data %%%%%%%%%%%%%% ' + str(request.httprequest.args) + str(
                json.loads(request.httprequest.data)))
        _logger.info('Tamara: %%%%%%%%%%%%%%%%%%%%%%% WEBHOOK %%%%%%%%%%%%%%' + str(args) + str(kwargs))
        if request.jsonrequest.get('order_reference_id'):
            _logger.info('Tamara: %%%%%%%%%%%%%%%%%%%%%%% WEBHOOK 2 %%%%%%%%%%%%%%' + str(request.jsonrequest))
            cargo_sale_id = request.jsonrequest.get('order_reference_id')
        if request.jsonrequest.get('event_type') == 'order_captured' and cargo_sale_id:
            _logger.info('Tamara: %%%%%%%%%%%%%%%%%%%%%%% WEBHOOK 3 %%%%%%%%%%%%%%')
            cargo_sale_id = request.env['bsg_vehicle_cargo_sale'].sudo().browse(int(cargo_sale_id))
            cargo_sale_id.is_paid_by_tamra = True
            vals_payment = cargo_sale_id.register_payment_tamara_instore()
            tamara_acquirer = request.env.ref('payment_tamara.tamara_payment_connect', False)
            if tamara_acquirer:
                vals_payment['journal_id'] = tamara_acquirer.journal_id.id
            else:
                vals_payment['journal_id'] = 794
            vals_payment['amount'] = request.jsonrequest.get('data').get('captured_amount').get('amount')
            vals_payment['payment_method_id'] = request.env.ref('payment.account_payment_method_electronic_in').id
            payment_id = request.env['account.payment'].sudo().create(vals_payment)
            payment_id._oncahnge_journal_destination()
            payment_id.transaction_reference = request.jsonrequest.get('order_reference_id')
            payment_id.tamara_reference_id = request.jsonrequest.get('order_id')
            payment_id.provider_tag = "Tamara Instore"
            payment_id.operation_number = request.jsonrequest.get('tamara_order_id')
            payment_id.cargo_sale_line_order_ids = cargo_sale_id.order_line_ids
            payment_id._onchange_cargo_sale_line_order_ids()
            payment_id.action_validate_invoice_payment()
            _logger.info('Tamara: %%%%%%%%%%%%%%%%%%%%%%% WEBHOOK 4 %%%%%%%%%%%%%%  ' + str(payment_id.id))
            tax_invoice_id = request.env['account.move'].sudo().search(
                [('move_type', '=', 'out_invoice'), ('payment_type', '=', 'paid'),
                 ('cargo_sale_id', '=', cargo_sale_id.id)],limit=1)
            cargo_sale_id.sudo().tamara_transaction_ids.create(
                {'date': datetime.now(), 'is_tamara': True, 'currency_id': cargo_sale_id.currency_id.id,
                 'acquirer_id': tamara_acquirer.id, 'app_fortid': request.jsonrequest.get('order_id'),
                 'app_paid_amount': request.jsonrequest.get('data').get('captured_amount').get('amount'),
                 'amount': request.jsonrequest.get('data').get('captured_amount').get('amount'),
                 'tamara_reference_id': request.jsonrequest.get('order_reference_id'),
                 'is_paid_by_tamra': True, 'transaction_reference': request.jsonrequest.get('order_number'),
                 "state": 'done',
                 'tamara_transaction_ids': [(6, 0, cargo_sale_id.ids)]})
            base_url = request.env['ir.config_parameter'].sudo(
            ).get_param('web.base.url')
            # base_url = "https://www.albassamitransport.com" for production use
            report_url = base_url + '/my/tamara/invoice/pdf/'+str(tax_invoice_id.id)
            number = '966' + cargo_sale_id.tamara_payment_sms_mobile_no
            sms_msg = " عزيزنا العميل نشكر لك إختيارك البسامي الدولية ويمكنك الإطلاع على فاتورة مشترياتك من الرابط "+ report_url

            request.env['cargo.sale.tamara.wiz'].sudo().send_sms_tamara(number, sms_msg)
            _logger.info('Tamara: %%%%%%%%%%%%%%%%%%%%%%% WEBHOOK 5 %%%%%%%%%%%%%%  ' + str(sms_msg))


    @http.route(['/my/tamara/invoice/pdf/<int:inv_id>'], type='http', auth="public", website=True)
    def portal_my_test_report(self, inv_id):
        pdf, _ = request.env.ref('qr_code_invoice_app.account_invoices_zakat_tax_authority').sudo().render_qweb_pdf([inv_id])
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
