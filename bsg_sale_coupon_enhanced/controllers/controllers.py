# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from datetime import datetime, timedelta
import werkzeug
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.exceptions import UserError, ValidationError
from odoo import _



class WebsiteSale(WebsiteSale):


    @http.route('/cargo/bassami_coupon_apply', auth='user', website=True)
    def check_promo_code(self, **kw):
        url = False
        values = {}
        coupon = kw.get('promo',False)
        cargo_id = kw.get('shipment',False)
        used = False
        if coupon and cargo_id:
            cargo_id = request.env['bsg_vehicle_cargo_sale'].sudo().search([('id', '=', cargo_id)])
            url = cargo_id.sudo().get_portal_url()
            if not cargo_id.loc_from.is_international and not cargo_id.loc_to.is_international:
                try:
                    coupon_status = request.env['sale.loyalty.coupon.wizard'].sudo().cargo_apply_coupon(cargo_id, coupon)
                    if coupon_status.get('not_found'):
                        request.session['error_promo_code'] = coupon_status['not_found']
                    elif coupon_status.get('error'):
                        request.session['error_promo_code'] = coupon_status['error']
                except: 
                    request.session['error_promo_code'] = _("Can't Proceed Promo Code Now,Try Later")    
            else:
                values['error_promo_code'] = _("Can't Use Coupon With Your Shipment Type")  
        if url:
            return werkzeug.utils.redirect(_build_url_w_params(url, values))        
        return http.request.redirect('/my/home/')


    def _recompute_coupon_lines(self):
        order = request.website.sale_get_order()
        order.recompute_coupon_lines()
        request.session['last_coupon_update'] = datetime.utcnow()

    def _update_website_sale_coupon(self, **post):
        order = request.website.sale_get_order()
        order.recompute_discounts()
        free_shipping_lines = order._get_free_shipping_lines()
        currency = order.currency_id
        result = {}
        if free_shipping_lines:
            amount_free_shipping = sum(free_shipping_lines.mapped('price_subtotal'))
            result.update({
                'new_amount_delivery': self._format_amount(0.0, currency),
                'new_amount_untaxed': self._format_amount(order.amount_untaxed, currency),
                'new_amount_tax': self._format_amount(order.amount_tax, currency),
                'new_amount_total': self._format_amount(order.amount_total, currency),
                'new_amount_order_discounted': self._format_amount(order.reward_amount - amount_free_shipping, currency)
            })
        return result

    @http.route(['/shipment/remove_bassami_promo_code/<shipment_id>'], type='http', auth="user", website=True)
    def portal_shipments_remove_coupon(self, shipment_id, access_token=None, **kw):
        url = False
        values = {}
        if shipment_id:
            cargo_id = request.env['bsg_vehicle_cargo_sale'].sudo().search([('id', '=', shipment_id)])
            url = cargo_id.sudo().get_portal_url()
            if cargo_id._cargo_is_global_discount_already_applied():
                try:
                    cargo_id.sudo().remove_cargo_coupon()
                    request.session['error_promo_code'] = _("Promo Code successfully removed")    
                except UserError as e:
                    values['error_promo_code'] = e.name or e.value 
                except:
                       values['error_message'] = True     

        if url:
            return werkzeug.utils.redirect(_build_url_w_params(url, values))        
        return http.request.redirect('/my/home/')
