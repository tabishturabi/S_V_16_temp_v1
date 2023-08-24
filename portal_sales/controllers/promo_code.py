# -*- coding: utf-8 -*-

from odoo import http, fields as odoo_fields, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
import werkzeug
from odoo.addons.portal.controllers.portal import _build_url_w_params

import requests

class PortalSalePrormCode(http.Controller):

    @http.route('/cargo/check_promo_code/', auth='user', website=True)
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
                qitaf_base_url, qitaf_token, qitaf_user_key = cargo_id.sudo().get_qitaf_config()
                headers = {
                        'Authorization': 'Bearer %s'%qitaf_token,
                        'Content-Type': 'application/json',}

                data = '{ "apiName": "couponDetails", "userKey": "%s", "language": "en", "param": { "coupon": "%s" } }'%(qitaf_user_key, coupon)
                try:
                    response = requests.post(qitaf_base_url, headers=headers, data=data)
                    if response.status_code == 200:
                        res = response.json()['response']
                        if res['status'] == 200:
                            if res['result']['discountType'] == 'percent':
                                for line in cargo_id.order_line_ids:
                                    if line.shipment_type.is_coupon_applicable:
                                        #Check if line precent discount value less than Qitaf discount
                                        if line.discount < float(res['result']['discountValue']):
                                            default_customer_price_list = request.env['product.pricelist'].sudo().search(
                                                        [('is_public', '=', True)], limit=1)
                                            line.discount = float(res['result']['discountValue'])
                                            line.customer_price_list = default_customer_price_list.id
                                            used = True
                                        else:
                                            values['have_more_discount'] = True    
                                    else:
                                        values['code_can_not_use'] = True
                            else:
                                for line in cargo_id.order_line_ids:
                                    if line.shipment_type.is_coupon_applicable:
                                        #Check if line discount value less than Qitaf discount
                                        if line.fixed_discount < float(res['result']['discountValue']):
                                            default_customer_price_list = request.env['product.pricelist'].sudo().search(
                                                        [('is_public', '=', True)], limit=1)
                                            line.fixed_discount = float(res['result']['discountValue'])
                                            line.customer_price_list = default_customer_price_list.id
                                            used = True
                                        else:    
                                            values['have_more_discount'] = True    
                                    else:
                                        values['code_can_not_use'] = True
                            if used:            
                                cargo_id.sudo().write({'qitaf_coupon':coupon, 'coupon_readonly': True})                   
                        else:
                            values['code_not_available'] = True
                            
                    else:
                        values['code_not_check'] = True
                except: 
                    values['code_not_check'] = True    
            else:
                values['code_can_not_use'] = True
        if url:
            return werkzeug.utils.redirect(_build_url_w_params(url, values))        
        return http.request.redirect('/my/home/')


    @http.route(['/shipment/remove_promo_code/<shipment_id>'], type='http', auth="public", website=True)
    def portal_shipments_remove_coupon(self, shipment_id, access_token=None, **kw):
        url = False
        values = {}
        if shipment_id:
            cargo_id = request.env['bsg_vehicle_cargo_sale'].sudo().search([('id', '=', shipment_id)])
            url = cargo_id.sudo().get_portal_url()
            if cargo_id.qitaf_coupon:
                try:
                    cargo_id.sudo().write({'qitaf_coupon':False, 'coupon_readonly': False})
                    for line in cargo_id.order_line_ids:
                        line.discount = 0
                        line.portal_onchange_shipment_type()
                    values['remove_code_message'] = True    
                except:
                       values['error_message'] = True 

        if url:
            return werkzeug.utils.redirect(_build_url_w_params(url, values))        
        return http.request.redirect('/my/home/')    
