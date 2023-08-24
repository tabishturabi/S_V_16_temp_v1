"""Part of odoo. See LICENSE file for full copyright and licensing details."""

import functools
import logging
from odoo.exceptions import AccessError
import ast
import re

from odoo import http, _, fields
from odoo.addons.restful.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
from odoo.http import request

_logger = logging.getLogger(__name__)
import base64
from datetime import datetime, date, time, timedelta
import requests

from math import cos, asin, sqrt

# def distance(lat1, lon1, lat2, lon2):
#     p = 0.017453292519943295
#     hav = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
#     return 12742 * asin(sqrt(hav))

# def closest(data, v):
#     return min(data, key=lambda p: distance(v['lat'],v['long'],p['lat'],p['long']))

# data = env['bsg_route_waypoints'].search_read([], fields=['location_long', 'location_lat'])
# tempDataList = [{'id': d['id'],'long': float(d['location_long']), 'lat':float(d['location_lat'])} for d in data]
# test = {'lat': 24.7328899, 'long':46.8192727}


class APIController(http.Controller):
    

    def get_other_service_vals(self, flag, qty, default_dict = False):
        product_id = request.env['product.product'].sudo().search([(flag, '=', True)], limit=1)
        vals = default_dict or {}
        if product_id:
            vals.update({
                'product_id': product_id.id,
                'cost':product_id.list_price * qty,
                'qty': qty,
                'tax_ids': [(6, 0, product_id.taxes_id.ids)] or False,
            })
            return vals

    def get_other_service_list(self,sale_rec, so_line, payload):
        other_service_lines = []
        other_service_common = {
            'cargo_sale_line_id': so_line.id,
            'cargo_sale_id': sale_rec.id,
            'home_location': payload.get('home_location', False),
            'pickup_location': payload.get('pickup_location', False),
        }
        if payload.get('is_home_pickup', 'false').lower() == 'true':
            other_service_vals = self.get_other_service_vals('is_home_pickup', 1, other_service_common)
            if other_service_vals:
                other_service_lines.append(other_service_vals)
        if payload.get('is_home_delivery', 'false').lower() == 'true':
            other_service_vals = self.get_other_service_vals('is_home_delivery', 1, other_service_common)
            if other_service_vals:
                other_service_lines.append(other_service_vals)
        if int(payload.get('small_boxes', 0)) > 0 :
            other_service_vals = self.get_other_service_vals('is_small_box', int(payload['small_boxes']), other_service_common)
            if other_service_vals:
                other_service_lines.append(other_service_vals)

        if int(payload.get('medium_boxes', 0))> 0:
            medium_box_product_id = request.env['product.product'].sudo().search([('is_medium_box', '=', True)], limit=1)
            other_service_vals = self.get_other_service_vals('is_medium_box', int(payload['medium_boxes']), other_service_common)
            if other_service_vals:
                other_service_lines.append(other_service_vals)
        if int(payload.get('large_boxes', 0))> 0:
            other_service_vals = self.get_other_service_vals('is_large_box', int(payload['large_boxes']), other_service_common)
            if other_service_vals:
                other_service_lines.append(other_service_vals)
        return other_service_lines

    def register_oline_payment(self, sale_rec, so_line, **payload):
        payment_id = False
        fort_id = payload.get('app_fortid', False)
        online_amount = float(payload.get('app_paid_amount', 0))
        if payload.get('app_payment_method', False) == 'credit' and online_amount > 0 and fort_id:
            acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'payfort')],limit=1)
            sale_rec = so_line.bsg_cargo_sale_id
            context = {
            'active_id': sale_rec.id,
            'show_invoice_amount': True,
            'pass_sale_order_id': sale_rec.id,
            'is_patrtially_payment': True,
            }
            inv = request.env['account.move'].search([('cargo_sale_id', '=', res.id)], limit=1)
            if not inv:
                return valid_response(data)

            payment_id = request.env['account.payment'].sudo().with_context(context).create({
                'payment_type': 'inbound',
                'partner_id': sale_rec.customer.id,
                'partner_type': 'customer',
                'journal_id': acquirer_id.journal_id.id,
                'amount': online_amount,
                'communication': sale_rec.name,
                'show_invoice_amount': True,
                'invoice_ids': [(4, inv[0].id, None)],
                'payment_method_id':1,
                'cargo_sale_line_id':so_line.id,
                'transaction_reference': sale_rec.transaction_reference,
                'app_fortid': fort_id,
            })
            payment_id.branach_ids =  False
            payment_id.action_validate_invoice_payment()
            cargo_line_pay = request.env['account.cargo.line.payment'].sudo()
            for so_line in sale_rec.mapped('order_line_ids'):
                if not so_line.is_paid and payment_id.residual_amount > 0:
                    for inv_line in inv.mapped('invoice_line_ids').filtered(lambda  s: s.cargo_sale_line_id.id == so_line.id):
                        cargo_line_pay.with_context({'without_check_amount':True}).sudo().create({
                        'cargo_sale_line_id': inv_line.cargo_sale_line_id.id,
                        'account_invoice_line_id': inv_line.id,
                        'amount': inv_line.price_total,
                        'residual': inv_line.price_total - inv_line.paid_amount,
                        'account_payment_id' : payment_id.id,
                    })
        return payment_id


    @http.route("/api/createShipmentOrder", type="http", auth="none", methods=["POST"], csrf=False)
    def create_shipment_order(self, **payload):
        headers = request.httprequest.headers
        data = []
        request_token = headers.get('access_token', False)
        if not request_token:
            return valid_response([{'status': 'error', 'message': 'Missing access token in request headers'}])
        if request_token != "access_token_770b27a4c5dea4cf116c8f5f38s749533b3071d8":
            return valid_response([{
                'status': 'error',
                'message': 'invalid Token'
                }])

        data = []
        _logger.error("/create/order+  "+str(payload))
        partner_id = str(payload.get('customer', ''))
        contract_ref = str(payload.get('contract_reference', ''))
        partner_id = partner_id.isdigit() and int(partner_id) or False
        if not isinstance(partner_id, int):
            return valid_response([{
                'status': 'error',
                'message': 'invalid customer ID'
                }])
        if not contract_ref:
            return valid_response([{
                'status': 'error',
                'message': 'invalid contract reference'
                }])

        contract_id = request.env['bsg_customer_contract'].sudo().search([('cont_customer', '=', partner_id),('contract_name', '=', contract_ref), ('state', '=', 'confirm')], limit=1)
        if not contract_id:
            return valid_response([{
                'status': 'error',
                'message': 'No running contract for the given customer ID and contract reference'
                }])
        try:
            owner_keys = ['owner_name', 'owner_id_type', 'owner_id_card_no', 'owner_nationality']
            vals = {'customer':  payload.get('customer', False), 'partner_types': 2, 'customer_contract': contract_id.id,'customer_price_list': contract_id.cont_customer.property_product_pricelist.id  or False,
                    'customer_type': 'corporate'}
            fort_id = payload.get('app_fortid', False)
            online_amount = float(payload.get('app_paid_amount', 0))
            is_credit = False
            mobile_price_list = request.env['product.pricelist'].sudo().search([('pricelist_code', '=', 'mobile_price_list')], limit=1)
            if payload.get('app_payment_method', False) == 'credit' and online_amount > 0 and fort_id:
                is_credit = True
                if mobile_price_list:
                    vals['customer_price_list']=mobile_price_list.id
            for key in owner_keys + [ 'loc_from', 'loc_to', 'receiver_name', 'receiver_type','receiver_id_type', 'receiver_nationality', 'receiver_mob_no', 'receiver_id_card_no', 'gps_location_from', 'gps_location_to', 'gps_distance', 'gps_time']:
                vals.update({
                    key: payload.get(key, False)
                })
            vals['owner_nationality'] =int(vals.get('owner_nationality', 379))
            vals['receiver_nationality'] = int(vals.get('receiver_nationality', 379))
            match = vals.get('receiver_id_card_no') and re.match(r'2[0-9]{9}', vals.get('receiver_id_card_no')) or False
            if match:
                vals['receiver_visa_no'] = vals['receiver_id_card_no']
                vals['receiver_id_card_no'] = False
            owner_match = vals.get('owner_id_card_no') and re.match(r'2[0-9]{9}', vals.get('owner_id_card_no', '')) or False
            if owner_match:
                vals['owner_visa_no'] = vals['owner_id_card_no']
                vals['owner_id_card_no'] = False
            vals['shipment_type'] = 'oneway'
            vals['payment_method'] = 5
            vals['owner_type'] = vals.get('owner_nationality', False) and int(vals['owner_nationality']) == 192 and '1' or '2'
            vals['owner_id_type'] = vals.get('owner_nationality', False) and int(vals['owner_nationality']) == 192 and 'saudi_id_card' or 'iqama'
            vals['receiver_type'] = vals.get('receiver_nationality', False) and int(vals['receiver_nationality']) == 192 and '1' or '2' 
            vals['receiver_id_type'] = vals.get('receiver_nationality', False) and int(vals['receiver_nationality']) == 192 and 'saudi_id_card' or 'iqama' 
            vals['is_from_app'] = True
            vals['is_from_contract_api'] = True
            vals['app_payment_method'] = payload.get('app_payment_method', False)
            vals['app_paid_amount'] = float(payload.get('app_paid_amount', 0))
            vals['app_fortid'] = payload.get('app_fortid', False)
            vals['transaction_reference'] = payload.get('transaction_reference', False)
            vals['qitaf_coupon'] = payload.get('coupon', False)
            vals['api_request_vals'] = str(payload)
            res = request.env['bsg_vehicle_cargo_sale'].sudo().create(vals)
            res.same_as_customer = True
            res._onchange_same_as_customer ()
            if not res.sender_nationality:
                res.sender_nationality = 379
            so_line_keys = ['shipment_type', 'car_make', 'car_model', 'plate_no', 'plate_type', 'chassis', 'year', 'car_color','palte_one', 'palte_second', 'palte_third', 'plate_no']
            line_vals = {}
            for lkey in so_line_keys:
                value =  payload.get(lkey, False)
                line_vals.update({
                    lkey: value and value.isdigit() and int(value) or value
                })
            line_vals['plate_registration'] = 'non-saudi'
            line_vals['plate_registration'] = 'new_vehicle'
            line_vals['non_saudi_plate_no'] = line_vals.get('plate_no',False) or  line_vals.get('plate_no', False)
            line_vals['plate_no'] = False
            line_vals['bsg_cargo_sale_id'] = res.id
            line_vals['service_type'] = payload.get('service_type', 1)
            bsg_config = request.env['bsg_car_config'].sudo().search([('car_maker', '=', line_vals['car_make'])])
            line_vals['car_make'] = bsg_config.id
            line_vals['is_from_app'] = True 
            line_vals['is_from_contract_api'] = True
            so_line = request.env['bsg_vehicle_cargo_sale_line'].sudo().create(line_vals)
            if is_credit:
                so_line.write({'customer_price_list':  mobile_price_list and mobile_price_list.id or 1, 'discount':mobile_price_list and mobile_price_list.item_ids and mobile_price_list.item_ids[0].percent_price or 0})
            so_line._onchange_shipment_type()
            arr_name = 'Regular'
            if so_line.shipment_type.is_satha:
                arr_name = 'Satha'

            online_amount = float(payload.get('app_paid_amount', 0))
            fort_id = payload.get('app_fortid', False)
            res.confirm_btn()
            """ No other services .. in the future might be agreed upon in customer contract and then i can use service_lines method to generate other service lines"""
            # service_lines = self.get_other_service_list(res, so_line, payload)
            # """No invoicing no copouns form credit customers: invoice will be generated from credit collection model"""
            # if service_lines:
            #     request.env['other_service_items'].sudo().create(service_lines)
            # if payload.get('coupon', False):
            #     res.with_context({'do_not_raise_exception': True}).action_get_qitaf_discount()
            # if payload.get('app_payment_method', False) == 'credit' and online_amount > 0 and fort_id:
            #     res.confirm_btn()
            #     res.state = 'registered'
            #     so_line.state = 'registered'
            # else:
            #     res.with_context({'do_not_create_invoice': True}).confirm_btn()
            res.state = 'registered'
            so_line.state = 'registered'
            so_line.recieved_from_customer_date = False
            res.recieved_from_customer_date = False
                
            data = [{
                'order_id': so_line.id,
                'order_ref': so_line.sale_line_rec_name,
            }]

            """ NO need for handling payment as this is a credit customr"""
            # if data:
            #     payment_id = self.register_oline_payment(sale_rec, so_line, payload)
            return valid_response(data)

        except Exception as e:
            se = http.serialize_exception(e)
            return invalid_response([{'status': 'error', 'message': se}])

    
    @http.route("/api/ShipmentMasterData", type="http", auth="none", methods=["GET"], csrf=False)
    def Shipment_master_data(self, **payload):
        headers = request.httprequest.headers
        data = []
        _logger.error(str(headers.keys()))
        request_token = headers.get('access_token', False)
        if not request_token:
            return valid_response([{'status': 'error', 'message': 'Missing access token in request headers'}])
        if request_token == "access_token_770b27a4c5dea4cf116c8f5f38s749533b3071d8":
            partner_id = str(payload.get('customer', ''))
            contract_ref = str(payload.get('contract_reference', ''))
            partner_id = partner_id.isdigit() and int(partner_id) or False
            if not isinstance(partner_id, int):
                return valid_response([{
                    'status': 'error',
                    'message': 'invalid customer ID'
                    }])
            if not contract_ref:
                return valid_response([{
                    'status': 'error',
                    'message': 'invalid contract reference'
                    }])

            contract_ids = request.env['bsg_customer_contract'].sudo().search([('cont_customer', '=', partner_id),('contract_name', '=', contract_ref), ('state', '=', 'confirm')], limit=1)
            if not contract_ids:
                return valid_response([{
                    'status': 'error',
                    'message': 'No running contract for the given customer ID and contract reference'
                    }])
            try:
                car_configs = request.env['bsg_car_config'].sudo().search([('visible_for_subcontract_api', '=', True)])
                car_config_ids = car_configs.sorted(key=lambda r: r.car_maker.car_make_ar_name)
                branch_ids = request.env['bsg_route_waypoints'].sudo().search([('visible_on_mobile_app', '=', True)])
                regions = branch_ids.sudo().mapped('region')
                branches_list = []
                for region in regions:
                    region_branch_ids = False
                    if region:
                        region_branch_ids = branch_ids.filtered(lambda b: b.region.id == region.id)
                    if region_branch_ids:
                        dic = {'code': region.bsg_region_code or '', 'name': region.bsg_region_name or '', 'name_ar': region.bsg_region_name_ar or ''}
                        dic['branches'] = [{'id': br.id, 'name': br.route_waypoint_name or '','name_en': br.waypoint_english_name or '', 'gps_coordinates': {
                                    'longitude': br.location_long or '',
                                    'latitude': br.location_lat or '',
                                },  'branch_type': br.is_international and 'international' or 'local',
                                    'brnach_shipment_type': br.branch_type or '',
                                    'has_satha_service': br.has_satha_service} for br in region_branch_ids]
                        branches_list.append(dic)
                car_makers = []
                for config in car_config_ids:
                    car_makers.append({
                        'car_maker_id':{'id': config.car_maker.id, 'name': config.car_maker.car_make_name or '', 'name_ar': config.car_maker.car_make_ar_name or ''},
                        'car_models': [{'car_model_id':{'id': line.car_model.id, 'name': line.car_model.car_model_en_name or '', 'name_ar': line.car_model.car_model_name or ''}, 'car_size':{'id': line.car_size.id, 'name': line.car_size.car_size_name or ''}} for line in config.car_line_ids.sorted(key=lambda l: l.car_model.car_model_name)]
                    })
                country_ids = request.env['res.country'].sudo().with_context({'lang': 'ar_001'}).search([('visible_on_mobile_app', '=', True)], order='name')
                plate_config_ids = request.env['bsg_plate_config'].sudo().search([])
                pricelists = []
                data.append({
                    'regions': branches_list,
                    'shipment_types': request.env['bsg.car.shipment.type'].sudo().search_read(domain=[], fields=['car_shipment_name', 'car_shipment_name_en']),
                    'car_makers': car_makers,
                    'payment_methods': request.env['cargo_payment_method'].sudo().search_read(domain=[], fields=['payment_method_name', 'payment_type']),
                    'vehicle_colors': request.env['bsg_vehicle_color'].sudo().search_read(domain=[], fields=['vehicle_color_name', 'vehicle_color_name_en']),
                    'car_years': request.env['bsg.car.year'].sudo().search_read(domain=[('car_year_name', '>=', 1980)], fields=['car_year_name'], order="car_year_name desc"),
                    'plate_types': [{'id': plate.id, 'name_ar': plate.plate_config_name or '', 'name_en': plate.plate_config_name_en or ''} for plate in plate_config_ids],
                    'countries' : [{'id': country_id.id, 'code': country_id.code or '', 'name': country_id.with_context({'lang': 'en_US'}).name or '', 'name_ar': country_id.with_context({'lang': 'ar_001'}).name or ''} for country_id in country_ids],
                    'id_card_types': [
                        {'code': 'saudi_id_card', 'name_en': 'Saudi National ID', 'name_ar': 'رقم الهوية الوطنية'},
                        {'code': 'iqama', 'name_en': 'Iqama', 'name_ar': 'الاقامة'},
                        {'code': 'gcc_national', 'name_en': 'GCC National', 'name_ar':  'مواطن خليجي'},
                        {'code': 'passport', 'name_en': 'Passport', 'name_ar': 'جواز السفر'},
                        {'code': 'other', 'name_en': 'Other', 'name_ar': 'غير ذلك'}
                    ],
                    'contracts':[ {
                        'reference': c.contract_name,
                        'status': 'running',
                        'customer_id': c.cont_customer.id,
                        'customer_name': c.cont_customer.name
                    } for c in contract_ids]
                    

                })
                if data:
                    return valid_response(data)
                return valid_response([])
            except AccessError as e:

                return invalid_response([{'status': 'error', 'message': 'Something went wrong'}])

        else:
            return valid_response([{
                    'status': 'error',
                    'message': 'invalid Token '
                }])

    @http.route("/api/trackShipmentOrder", type="http", auth="none", methods=["GET"], csrf=False)
    def track_ship_order(self, **payload):
        headers = request.httprequest.headers
        request_token = headers.get('access_token', False)
        if not request_token:
            data = [{'status': 'error','message': 'Missing access token in request headers'}]
        request_token = headers.get('access_token', False)
        receiver_mob_no = payload.get('receiver_mob_no', False)
        if request_token == "access_token_770b27a4c5dea4cf116c8f5f38s749533b3071d8":
            so_line_ref = payload.get('order_ref', False)
            if not so_line_ref:
                return valid_response([{
                    'status': 'error',
                    'message': 'Missing order_ref or receiver_mob_no in request params'
                }])
            receiver_mob_no = payload.get('receiver_mob_no', False)
            domain = [('sale_line_rec_name', '=', so_line_ref)]
            if receiver_mob_no:
                domain.append(('receiver_mob_no','=',receiver_mob_no))
            cargo_line = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(domain,limit=1)
            data={
                'status': 'success',
                'orders': []
            }
            if cargo_line:
                order_date = cargo_line.order_date
                if order_date:
                    order_date = order_date.strftime('%d-%B-%Y')
                data['orders'].append(
                    {   'order_ref': cargo_line.sale_line_rec_name,
                        'receiver_name': cargo_line.receiver_name,
                        'receiver_mob_no': cargo_line.receiver_mob_no,
                        'customer_name': cargo_line.customer_id.name,
                        'order_date': order_date,
                        'loc_from': cargo_line.loc_from.route_waypoint_name,
                        'loc_to': cargo_line.loc_to.route_waypoint_name,
                        'expected_delivery': cargo_line.expected_delivery,
                        'actual_delivery_date': cargo_line.bsg_cargo_sale_id.actual_deliver_date and cargo_line.bsg_cargo_sale_id.actual_deliver_date.strftime('%d-%B-%Y') or '',
                        'car_model': cargo_line.car_model.car_model_name,
                        'year': cargo_line.year.car_year_name,
                        'car_make': cargo_line.car_make.car_maker.car_make_ar_name,
                        'state': cargo_line.state,
                    }
                )
            return  valid_response([data])
        else:
            return valid_response([{
                    'status': 'error',
                    'message': 'invalid Token '
                }])