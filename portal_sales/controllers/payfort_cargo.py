# -*- coding: utf-8 -*-
import pprint
import werkzeug
import logging

from odoo.exceptions import ValidationError
from odoo.http import request, Response
from odoo import http
# Migration Note
# from odoo.addons.payment.models.payment_acquirer import ValidationError

_logger = logging.getLogger(__name__)

class PayfortPayment(http.Controller):

    @http.route('/payment/payfort/return', type='http', auth="none",methods=['GET', 'POST'], csrf=False)
    def payfort_form_redirect(self, **post):
        """ Gets the URL from payfort and redirect to that URL for payment """
        try:
            is_valid_trans = request.env['payment.transaction'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).form_feedback(post, 'payfort')
            trans = request.env['payment.transaction'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('reference', '=', post.get('merchant_reference'))])
            if is_valid_trans and trans:
                if trans.state == 'done' and  not trans.is_processed:
                    trans._post_process_after_done()
                trans.signature = post.get('signature')
            if trans and hasattr(trans, 'cargo_sale_ids') and trans.cargo_sale_ids:
                url = trans.cargo_sale_ids[0].sudo().get_portal_url()
                return werkzeug.utils.redirect(url)
            if trans and hasattr(trans, 'cargo_sale_line_ids') and trans.cargo_sale_line_ids:
                url = trans.cargo_sale_line_ids[0].sudo().get_portal_url()
                return werkzeug.utils.redirect(url)
            if trans and trans.invoice_ids and not hasattr(trans, 'cargo_sale_ids') and not hasattr(trans, 'cargo_sale_line_ids'):
                url = trans.invoice_ids[0].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_portal_url()
                return werkzeug.utils.redirect(url)
        except ValidationError:
            _logger.exception('Unable to validate the Payfort payment')
        return werkzeug.utils.redirect('/payment/process')

