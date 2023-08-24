# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#################################################################################
import pprint
import werkzeug
import logging


from odoo.http import request, Response
from odoo import http
# from odoo.addons.payment.models.payment_acquirer import ValidationError

_logger = logging.getLogger(__name__)

#class PayfortPayment(http.Controller):

    #@http.route('/payment/payfort/return', type='http', auth="none",methods=['GET', 'POST'], csrf=False)
    #def payfort_form_redirect(self, **post):
    #    """ Gets the URL from payfort and redirect to that URL for payment """
    #    _logger.info(
    #        'Beginning form_feedback with post data %s', pprint.pformat(post))
    #    _logger.info('payfort: validated data')
    #    try:
    #        is_valid_trans = request.env['payment.transaction'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).form_feedback(post, 'payfort')
    #        trans = request.env['payment.transaction'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('reference', '=', post.get('merchant_reference'))])
    #        if is_valid_trans and trans:
    #            if trans.state == 'done' and  not trans.is_processed:
    #                trans._post_process_after_done()
    #        if trans and trans.invoice_ids:
    #            url = trans.invoice_ids[0].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_portal_url()
    #            return werkzeug.utils.redirect(url)
    #    except ValidationError:
    #        _logger.exception('Unable to validate the Payfort payment')
    #    return werkzeug.utils.redirect('/payment/process')

    #@http.route('/payment/payfort/notify', type='http', auth='none', methods=['POST'], csrf=False)
    #def payfort_notify(self, **post):
    #    """ Payfort Notify. """
    #    _logger.info(
    #        'Beginning Payfort form_feedback with post data from notify url %s', pprint.pformat(post))
    #    try:
    #        res = request.env['payment.transaction'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).form_feedback(post, 'payfort')
    #    except ValidationError:
    #        _logger.exception('Unable to validate the Payfort payment')
    #    return Response(status=200)
