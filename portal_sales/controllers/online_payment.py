from werkzeug.urls import url_encode
import logging
from odoo import http, _
from odoo.addons.portal.controllers.portal import _build_url_w_params
# Migration Note
# from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

_logger = logging.getLogger(__name__)


class PaymentPortal(http.Controller):

    @route('/shipment/pay/<int:shipment_id>/form_tx', type='json', auth="public", website=True)
    def shipment_pay_form(self, acquirer_id, shipment_id, save_token=False, access_token=None, **kwargs):
        """ Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button on the payment
        form.

        :return html: form containing all values related to the acquirer to
                      redirect customers to the acquirer website """
        cargo_sudo = request.env['bsg_vehicle_cargo_sale'].sudo().browse(shipment_id)
        if not cargo_sudo:
            return False

        try:
            acquirer_id = int(acquirer_id)
        except:
            return False

        if request.env.user._is_public():
            save_token = False # we avoid to create a token for the public user

        success_url = kwargs.get(
            'success_url', "%s?%s" % (cargo_sudo.access_url, url_encode({'access_token': access_token}) if access_token else '')
        )
        vals = {
            'acquirer_id': acquirer_id,
            'return_url': success_url,
            #'reference' : cargo_sudo.name, 
        }

        if save_token:
            vals['type'] = 'form_save'

        transaction = cargo_sudo._create_payment_transaction(vals)
        PaymentProcessing.add_payment_transaction(transaction)
        transaction.sudo().tamara_transaction_ids.write({"state": 'registered'})

        return transaction.render_cargo_button(
            cargo_sudo,
            submit_txt=_('Pay & Confirm'),
            render_values={
                'type': 'form_save' if save_token else 'form',
                'alias_usage': _('If we store your payment information on our server, subscription payments will be made automatically.'),
            }
        )

    @http.route('/shipment/pay/<int:shipment_id>/s2s_token_tx', type='http', auth='public', website=True)
    def shipment_pay_token(self, shipment_id, pm_id=None, **kwargs):
        """ Use a token to perform a s2s transaction """
        error_url = kwargs.get('error_url', '/my')
        access_token = kwargs.get('access_token')
        params = {}
        if access_token:
            params['access_token'] = access_token

        cargo_sudo = request.env['bsg_vehicle_cargo_sale'].sudo().browse(shipment_id).exists()
        if not cargo_sudo:
            params['error'] = 'pay_cargo_invalid_doc'
            return request.redirect(_build_url_w_params(error_url, params))

        success_url = kwargs.get(
            'success_url', "%s?%s" % (cargo_sudo.access_url, url_encode({'access_token': access_token}) if access_token else '')
        )
        try:
            token = request.env['payment.token'].sudo().browse(int(pm_id))
        except (ValueError, TypeError):
            token = False
        token_owner = cargo_sudo.customer if request.env.user._is_public() else request.env.user.partner_id
        if not token or token.partner_id != token_owner:
            params['error'] = 'pay_cargo_invalid_token'
            return request.redirect(_build_url_w_params(error_url, params))

        vals = {
            'payment_token_id': token.id,
            'type': 'server2server',
            'return_url': _build_url_w_params(success_url, params),
        }

        tx = cargo_sudo._create_payment_transaction(vals)
        PaymentProcessing.add_payment_transaction(tx)

        params['success'] = 'pay_cargo'
        _logger.info("--payfort_form_values_after_Return--%r---",str(tx.state))
        return request.redirect('/payment/process')

class PortalVehicleSale(CustomerPortal):


    def _shipment_get_page_view_values(self, shipment, access_token, **kwargs):
        values = super(PortalVehicleSale, self)._shipment_get_page_view_values(shipment, access_token, **kwargs)
        payment_inputs = request.env['payment.provider']._get_compatible_providers(company_id=shipment.company_id.id,partner_id=shipment.customer.id,amount=shipment.total_amount)
        # if not connected (using public user), the method _get_available_payment_input will return public user tokens
        is_public_user = request.env.user._is_public()
        if is_public_user:
            # we should not display payment tokens owned by the public user
            payment_inputs.pop('pms', None)
            token_count = request.env['payment.token'].sudo().search_count([('acquirer_id.company_id', '=', shipment.company_id.id),
                                                                      ('partner_id', '=', shipment.customer.id),
                                                                    ])
            values['existing_token'] = token_count > 0
        payment_inputs_vals = {
            'providers': payment_inputs,
            'transaction_route': '/payment/transaction',
            'landing_route': '/my/payment_method',
            'pms': request.env['payment.token'].search([
                ('partner_id', '=', shipment.customer.id),
                ('provider_id', 'in', payment_inputs.ids)]),
        }
        values.update(payment_inputs_vals)
        # if the current user is connected we set partner_id to his partner otherwise we set it as the invoice partner
        # we do this to force the creation of payment tokens to the correct partner and avoid token linked to the public user
        values['partner_id'] = shipment.customer if is_public_user else request.env.user.partner_id,
        return values
