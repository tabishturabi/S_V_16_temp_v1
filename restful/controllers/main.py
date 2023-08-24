"""Part of odoo. See LICENSE file for full copyright and licensing details."""

import functools
import hashlib
import logging
from odoo.exceptions import AccessError
import re
# from translate import Translator

from odoo import http, fields
from odoo.addons.restful.common import (
    invalid_response,
    valid_response,
)
from odoo.http import request

import base64
from datetime import datetime, timedelta
import requests


_logger = logging.getLogger(__name__)

ORDERSTATEMAPPING = {
        'draft': 1,
        'registered': 2,
        'confirm': 3,
        'awaiting': 4,
        'shipped': 5,
        'on_transit': 6,
        'Delivered': 7,
        'done': 8,
        'released': 9,
        'cancel': 10,
        'cancel_request':11
}
def validate_token(func):
    """."""
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get("access_token")
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = (
            request.env["api.access_token"].sudo().search([("token", "=", access_token)], order="id DESC", limit=1)
        )
        #
        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response("access_token", "token seems to have expired or invalid", 401)

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        request.session.session_token = ''
        return func(self, *args, **kwargs)

    return wrap


_routes = ["/api/<model>", "/api/<model>/<id>", "/api/<model>/<id>/<action>"]


class APIController(http.Controller):
    # """."""

    @validate_token
    @http.route("/api/getCarSizes", type="http", auth="none", methods=["GET"], csrf=False)
    def get_car_sizes(self, **payload):
        try:
            data = request.env['bsg_car_size'].sudo().search_read(
                        domain=[], fields=['car_size_name']
                    )
            if data:
                return valid_response(data)
            return invalid_response(
                "invalid object model", "No records found"
            )
        except AccessError as e:

            return invalid_response("Error: ", str(e))

    @validate_token
    @http.route("/api/getProductPricelists", type="http", auth="none", methods=["GET"], csrf=False)
    def get_product_pricelists(self, **payload):
        data = []
            
        recs = request.env['product.pricelist'].sudo().search([])
        for rec in recs:
            data.append({
                'id':rec.id,
                'name': rec.name,
                'pricelist_code': rec.pricelist_code,
                'discount_method': rec.item_ids and rec.item_ids[0].compute_price,
                'discount_amount': rec.item_ids and (rec.item_ids[0].compute_price == 'percentage' and rec.item_ids[0].percent_price) or rec.item_ids[0].fixed_price ,
            })
        return valid_response(data)

    @validate_token
    @http.route("/api/getShipmentTypes", type="http", auth="none", methods=["GET"], csrf=False)
    def get_shipment_types(self, **payload):
        try:
            data = request.env['bsg.car.shipment.type'].sudo().search_read(
                        domain=[], fields=['car_shipment_name', 'car_shipment_name_en']
                    )
            if data:
                return valid_response(data)
            return invalid_response(
                "invalid object model", "No records found"
            )
        except AccessError as e:

            return invalid_response("Error: ", str(e))

    @validate_token
    @http.route("/api/getBranches", type="http", auth="none", methods=["GET"], csrf=False)
    def get_branches(self, **payload):
        try:
            data = request.env['bsg_route_waypoints'].sudo().search_read(
                        domain=[], fields=['route_waypoint_name']
                    )
            if data:
                return valid_response(data)
            return invalid_response(
                "invalid object model", "No records found"
            )
        except AccessError as e:

            return invalid_response("Error: ", str(e))


    @validate_token
    @http.route("/api/getCarMakers", type="http", auth="none", methods=["GET"], csrf=False)
    def get_car_makers(self, **payload):
        try:
            data = request.env['bsg_car_make'].sudo().search_read(
                        domain=[], fields=['car_make_ar_name']
                    )
            if data:
                return valid_response(data)
            return invalid_response(
                "invalid", "No records founMd"
            )
        except AccessError as e:

            return invalid_response("Error: ", str(e))

    
    @validate_token
    @http.route("/api/getCarModels", type="http", auth="none", methods=["GET"], csrf=False)
    def get_car_models(self, **payload):
        try:
            car_model = payload.get('car_model', False)
            data = False
            if car_model:
                data = request.env['bsg_car_model'].sudo().search_read(
                            domain=[('car_maker_id', '=', int(car_model))], fields=['route_waypoint_name']
                        )
            if data:
                return valid_response(data)
            return invalid_response(
                "invalid object model", "No records found"
            )
        except AccessError as e:

            return invalid_response("Error: ", str(e))

    def get_order_info(self, record):
        data = []
        bsg_cargo_sale_id = record.bsg_cargo_sale_id
        if record: 
            other_services = [
                {'service': line.product_id.name or '', 
                'cost': line.cost+line.tax_amount or 0, 
                'qty': line.qty or 0,
                'home_location': line.home_location or '', 
                'pickup_location': line.pickup_location or '',
                'taxes': sum(line.tax_ids.mapped('amount'))} 
                for line in bsg_cargo_sale_id.other_service_line_ids
            ]
            invoice_ids = bsg_cargo_sale_id.invoice_ids
            other_service_invoice = request.env['account.move'].sudo().search([('invoice_origin','=', bsg_cargo_sale_id.name),('is_other_service_invoice','=',True)])
            if other_service_invoice:
                invoice_ids += other_service_invoice
            if invoice_ids:
                total_amount = sum(invoice_ids.mapped('amount_total'))
                due_amount = sum(invoice_ids.mapped('amount_residual'))
                paid_amount = total_amount - due_amount
            else:
                total_amount = bsg_cargo_sale_id.total_so_amount
                due_amount = total_amount
                paid_amount = 0
                
            data.append({
                'order_ref': record.sale_line_rec_name or '',
                'sender_name': bsg_cargo_sale_id.sender_name or '',
                'receiver_name': bsg_cargo_sale_id.receiver_name or '',
                'receiver_phone': bsg_cargo_sale_id.receiver_mob_no or '',
                'plate_nmuber': record.non_saudi_plate_no or record.general_plate_no or '',
                'service_type': record.shipment_type.car_shipment_name or '',
                # 'shipment_type': record.shipment_type.car_shipment_name,
                'car_maker': {'id': record.car_make.car_maker.id or 0 , 'name':record.car_make.car_maker.car_make_name or '', 'name_ar':record.car_make.car_maker.car_make_ar_name or ''},
                'car_model': {'id': record.car_model.id or 0 ,'name': record.car_model.car_model_en_name or '', 'name_ar':record.car_model.car_model_name or ''},
                'loc_from': {'id': bsg_cargo_sale_id.loc_from.id or 0 ,'name': bsg_cargo_sale_id.loc_from.route_waypoint_name or '', 'name_en': bsg_cargo_sale_id.loc_from.waypoint_english_name or '', 'has_satha_service': bsg_cargo_sale_id.loc_from.has_satha_service or ''},
                'loc_to': {'id': bsg_cargo_sale_id.loc_to.id or 0 , 'name': bsg_cargo_sale_id.loc_to.route_waypoint_name or '', 'name_en': bsg_cargo_sale_id.loc_to.waypoint_english_name or '', 'has_satha_service': bsg_cargo_sale_id.loc_to.has_satha_service or ''},
                'gps_location_from': bsg_cargo_sale_id.gps_location_from or '',
                'gps_location_to': bsg_cargo_sale_id.gps_location_to or '',
                'gps_distance': bsg_cargo_sale_id.gps_distance or '',
                'gps_time': bsg_cargo_sale_id.gps_time or '',
                'order_date': bsg_cargo_sale_id.order_date and bsg_cargo_sale_id.order_date.strftime('%d-%B-%Y') or '',
                'expected_delivery_date': record.expected_delivery and record.expected_delivery.strftime('%d-%B-%Y') or '',
                'min_days':bsg_cargo_sale_id.expected_delivery_days or 0,
                'min_hrs':bsg_cargo_sale_id.expected_hours or 0, 
                'max_days':bsg_cargo_sale_id.est_max_no_delivery_days or 0,
                'max_hrs':bsg_cargo_sale_id.est_max_no_hours or 0,
                'actual_delivery_date': bsg_cargo_sale_id.actual_deliver_date and bsg_cargo_sale_id.actual_deliver_date.strftime('%d-%B-%Y') or '',
                'other_services': other_services, 
                'transaction_reference':bsg_cargo_sale_id.transaction_reference or '',
                'total_amount':bsg_cargo_sale_id.total_so_amount,
                'due_amount': bsg_cargo_sale_id.total_so_amount - paid_amount,
                'paid_amount': paid_amount,
                'collected_amount': sum(request.env['driver.cash.credit.collection'].sudo().search([('cargo_sale_line_id', '=', record.id), ('state', '=', 'draft')]).mapped('collected_amount')),
                'state': record.state,
            })
        return data

    @validate_token
    @http.route("/api/get_order", type="http", auth="none", methods=["GET"], csrf=False)
    def get_order(self, **payload):
        # try:
        order_number = payload.get('order_ref', False)
        data = []
        if order_number:
            record = request.env['bsg_vehicle_cargo_sale_line'].sudo().search([('sale_line_rec_name', '=', order_number)], limit=1)
            data = self.get_order_info(record)
        return valid_response(data)

    @validate_token
    @http.route("/api/get_signature", type="http", auth="none", methods=["GET"], csrf=False)
    def get_signature(self, **payload):
        command = payload.get('command', False)
        amount = payload.get('amount', False)
        currency = payload.get('currency', False)
        language = payload.get('language', False)
        customer_email = payload.get('customer_email', False)
        #order_description = payload.get('order_description', False)
        merchant_reference = payload.get('merchant_reference', False)

        # data = []
        # private_key = rsa.generate_private_key(
        #     public_exponent=65537,
        #     key_size=2048,
        #     backend=default_backend()
        # )
        payment_acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'payfort')], limit=1)
        access_code = payment_acquirer_id.access_code
        merchant_identifier = payment_acquirer_id.merchant_identifier
        sha_type = payment_acquirer_id.sha_type
        request_phrase = payment_acquirer_id.request_phrase
        #response_phrase = payment_acquirer_id.response_phrase

        # # Sign a message using the key
        sha_string = f"{request_phrase}access_code={access_code}amount={amount}command={command}currency={currency}customer_email={customer_email}language={language}merchant_identifier={merchant_identifier}merchant_reference={merchant_reference}{request_phrase}"
        # message = bytes(sha_string, 'utf-8')
        if sha_type == "sha_256":
            # signature = private_key.sign(
            #     message,
            #     padding.PSS(
            #         mgf=padding.MGF1(hashes.SHA256()),
            #         salt_length=padding.PSS.MAX_LENGTH
            #     ),
            #     hashes.SHA256()
            # )
            signature = hashlib.sha256(sha_string.encode())
            signature = signature.hexdigest()
            return valid_response(signature)
        if sha_type == "sha_512":
            # signature = private_key.sign(
            #     message,
            #     padding.PSS(
            #         mgf=padding.MGF1(hashes.SHA512()),
            #         salt_length=padding.PSS.MAX_LENGTH
            #     ),
            #     hashes.SHA512()
            # )
            signature = hashlib.sha512(sha_string.encode())
            signature = signature.hexdigest()
            return valid_response(signature)

    @validate_token
    @http.route("/api/sdk_token_signature", type="http", auth="none", methods=["GET"], csrf=False)
    def sdk_token_signature(self, **payload):
        service_command = payload.get('service_command', False)
        device_id = payload.get('device_id', False)
        language = payload.get('language', False)


        # data = []
        # private_key = rsa.generate_private_key(
        #     public_exponent=65537,
        #     key_size=2048,
        #     backend=default_backend()
        # )
        payment_acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'payfort')], limit=1)
        # if payment_acquirer_id:
        access_code = payment_acquirer_id.access_code
        merchant_identifier = payment_acquirer_id.merchant_identifier
        sha_type = payment_acquirer_id.sha_type
        request_phrase = payment_acquirer_id.request_phrase
        #response_phrase = payment_acquirer_id.response_phrase

        # # Sign a message using the key

        sha_string = f"{request_phrase}access_code={access_code}device_id={device_id}language={language}merchant_identifier={merchant_identifier}service_command={service_command}{request_phrase}"
        # message = bytes(sha_string, 'utf-8')
        if sha_type == "sha_256":
            # signature = private_key.sign(
            #     message,
            #     padding.PSS(
            #         mgf=padding.MGF1(hashes.SHA256()),
            #         salt_length=padding.PSS.MAX_LENGTH
            #     ),
            #     hashes.SHA256()
            # )
            signature = hashlib.sha256(sha_string.encode())
            signature = signature.hexdigest()
            return valid_response(signature)
        if sha_type == "sha_512":
            # signature = private_key.sign(
            #     message,
            #     padding.PSS(
            #         mgf=padding.MGF1(hashes.SHA512()),
            #         salt_length=padding.PSS.MAX_LENGTH
            #     ),
            #     hashes.SHA512()
            # )
            signature = hashlib.sha512(sha_string.encode())
            signature = signature.hexdigest()
            return valid_response(signature)

    @validate_token
    @http.route("/api/get_order_references", type="http", auth="none", methods=["POST"], csrf=False)
    def get_order_refes(self, **payload):
        app_ref = payload.get('app_ref', False)
        _logger.error("/get_order_references+  "+str(payload), app_ref)
        data = []
        if app_ref:
            record = request.env['bsg_vehicle_cargo_sale_line'].sudo().search([('bsg_cargo_sale_id.transaction_reference', '=', app_ref)], limit=1)
            if record:
                data = [{'app_order_ref': rec.bsg_cargo_sale_id.transaction_reference, 'odoo_order_ref': rec.sale_line_rec_name, 'state': rec.state} for rec in record]       
        return valid_response(data)

    @validate_token
    @http.route("/api/cancel_order", type="http", auth="none", methods=["GET"], csrf=False)
    def cancel_order(self, **payload):
        # try:
        order_number = payload.get('order_ref', False)
        data = []
        if order_number:
            record = request.env['bsg_vehicle_cargo_sale_line'].sudo().search([('sale_line_rec_name', '=', order_number)], limit=1)
            if record:
                invoice_ids = request.env['account.move'].sudo().search([('cargo_sale_id', '=', record.sudo().bsg_cargo_sale_id.id), ('state', 'in', ['open', 'paid'])], limit=1)
                if not invoice_ids:
                    record.sudo().state = 'cancel'
                    record.sudo().bsg_cargo_sale_id.state = 'cancel' 
                    data.append({'status':'cancel'})
                else:
                    record.sudo().state = 'cancel_request'
                    record.sudo().bsg_cargo_sale_id.state = 'cancel_request' 
                    data.append({'status':'cancel_request'})
        return valid_response(data)

    @validate_token
    @http.route("/api/getPriceData", type="http", auth="none", methods=["GET"], csrf=False)
    def get_price_data(self, **payload):
        data = []
        try:
            car_configs = request.env['bsg_car_config'].sudo().search([('visible_on_mobile_app', '=', True)])
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
                                'has_satha_service': br.has_satha_service,
                                'address': br.loc_branch_id.street or '',
                                'weekly_working_hours': br.loc_branch_id.weekly_working_hours or '',
                                'friday_working_hours': br.loc_branch_id.friday_working_hours or '',
                                'phone': br.loc_branch_id.branch_phone or '',
                                'allowed_shipment_types':[{'id':ship.id,'allowed_car_shipment_name':ship.car_shipment_name,'allowed_car_shipment_name_en':ship.car_shipment_name_en} for ship in br.allowed_shipment_types if ship]} for br in region_branch_ids]
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
            pricelist_ids = request.env['product.pricelist'].sudo().search([])
            for pricelist in pricelist_ids:
                pricelists.append({
                    'id':pricelist.id,
                    'name': pricelist.name or '',
                    'pricelist_code': pricelist.pricelist_code or '',
                    'discount_method': pricelist.item_ids and pricelist.item_ids[0].compute_price or '',
                    'discount_amount': pricelist.item_ids and (pricelist.item_ids[0].compute_price == 'percentage' and pricelist.item_ids[0].percent_price) or pricelist.item_ids[0].fixed_price ,
                })
            data.append({
                'regions': branches_list,
                # 'car_sizes': request.env['bsg_car_size'].search_read(domain=[], fields=['car_size_name']),
                'pricelists': pricelists,
                'shipment_types': request.env['bsg.car.shipment.type'].sudo().search_read(domain=[], fields=['car_shipment_name', 'car_shipment_name_en','is_public']),
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
                'app_version': request.env['andriod.app.version'].sudo().search([], limit=1).name or ''

            })
            if data:
                return valid_response(data)
            return invalid_response(
                "invalid object model", "No records found"
            )
        except AccessError as e:

            return invalid_response("Error: ", str(e))

    @validate_token
    @http.route("/api/find_create_customer", type="http", auth="none", methods=["POST"], csrf=False)
    def find_create_customer(self, **payload):
        try:
            if not payload.get('customer_national_id', False):
                return valid_response([])
            partner_id = request.env['res.partner'].search(['|',('iqama_no', '=', payload.get('customer_national_id', False)),('customer_id_card_no', '=', payload.get('customer_national_id', False))], limit=1)
            phone = payload.get('customer_phone', False)
            id_card = payload['customer_national_id']
            new_id_card = payload.get('new_customer_national_id', False)
            country_ref =  int(payload.get('nationality_id', 379))
            nationality_id = request.env['res.country'].sudo().search([('id', '=', country_ref)], limit=1)
            nationality_id = nationality_id and nationality_id.id or False
            vals = {
                'customer_type': id_card.startswith('1') and '1' or '2',
                'partner_types': 5

            }
            if payload.get('customer_name', False):
               vals['name'] = payload['customer_name']
            if phone:
               vals['mobile'] = phone
            if new_id_card:
                if  new_id_card.startswith('1'):
                    vals.update({
                            'customer_type':'1',
                            'customer_id_card_no': new_id_card,
                            'customer_id_type': 'saudi_id_card',
                            'customer_nationality': 192,
                        })

                else:
                    vals.update({
                        'customer_type': '2',
                        'iqama_no': new_id_card,
                        'customer_id_type': 'iqama',

                    })
                    if nationality_id:
                        vals.update({
                            'customer_nationality': int(nationality_id)
                        })
            else:
                if id_card.startswith('1'):
                    vals.update({
                            'customer_type':'1',
                            'customer_id_card_no': id_card,
                            'customer_id_type': 'saudi_id_card',
                            'customer_nationality': 192,
                        })
                else:
                    vals.update({
                        'customer_type': '2',
                        'iqama_no': id_card,
                        'customer_id_type': 'iqama',

                    })
                    if nationality_id:
                        vals.update({
                            'customer_nationality': int(nationality_id)
                        })
            

            if not partner_id:
                partner_id = request.env['res.partner'].create(vals)
                partner_id._onchange_partner_types()
            else:
                request.env['res.partner'].write(vals)
                partner_id._onchange_partner_types()
            if partner_id.id == 0:
                domain = ['&','|',('iqama_no', '=', payload.get('customer_national_id', False)),('customer_id_card_no', '=', payload.get('customer_national_id', False)),('active','=', False)]
                partner_id = request.env['res.partner'].search(domain, limit=1)
                partner_id.active = True
                data = [{ 'customer_id': partner_id.id }]
            else:
                data = [{ 'customer_id': partner_id.id }]
            return valid_response(data)
        except Exception as e:
            se = http.serialize_exception(e)
            request.env['api.log'].sudo().create({
                'endpoint': '/api/find_create_customer',
                'request_payload': str(payload),
                'exception_message': se,
            })
            return invalid_response("Error: ", se)

    @validate_token
    @http.route("/api/create_new_ticket", type="http", auth="none", methods=["POST"], csrf=False)
    def create_new_ticket(self, **payload):
        try:
            if not payload.get('subject', False):
                return valid_response([])
            subject = payload.get('subject', False)
            customer_id = payload.get('customer_id', False)
            description = payload.get('description', False)
            _logger.error("/create new ticket customer id ........................+  " + str(customer_id))
            _logger.error("/create new ticket customer id .type ........................+  " + str(type(customer_id)))
            vals = {
                'team_id': 13,
                'partner_id': int(customer_id),
                'name': subject,
                'description': description
            }
            ticket_id = request.env['helpdesk.ticket'].sudo().create(vals)
            data = [{
                'ticket_id': ticket_id.id
            }]
            return valid_response(data)
        except Exception as e:
            se = http.serialize_exception(e)
            request.env['api.log'].sudo().create({
                'endpoint': '/api/create_new_ticket',
                'request_payload': str(payload),
                'exception_message': se,
            })
            return invalid_response("Error: ", se)
    
    @validate_token
    @http.route("/api/add_other_services", type="http", auth="none", methods=["POST"], csrf=False)
    def add_other_services(self, **payload):
        try:
            record=False
            data = []
            order_number = payload.get('order_ref', False)
            if order_number:
                record = request.env['bsg_vehicle_cargo_sale_line'].sudo().search([('sale_line_rec_name', '=', order_number)], limit=1)
            if record:
                bsg_cargo_sale_id = record.bsg_cargo_sale_id

                other_service_lines = []
                exisiting_service = bsg_cargo_sale_id.other_service_line_ids
                arr_name = 'Regular'
                if record.shipment_type.is_satha:
                    arr_name = 'Satha'
                if payload.get('is_home_pickup', 'false').lower() == 'true':
                    home_pickup_line = exisiting_service.filtered(lambda l: l.product_id.is_home_pickup)
                    if not home_pickup_line:
                        home_pickup_product_id = request.env['product.product'].sudo().search([('is_home_pickup', '=', True), ('attribute_value_ids.name', '=', arr_name)], limit=1)
                        if home_pickup_product_id:
                            other_service_lines.append({
                                'cargo_sale_line_id': record.id,
                                'product_id': home_pickup_product_id.id,
                                'cost':home_pickup_product_id.lst_price,
                                'qty':1,
                                'home_location': payload.get('home_location', False),
                                'pickup_location': payload.get('pickup_location', False),
                                'tax_ids': [(6, 0, home_pickup_product_id.taxes_id.ids)] or False,
                                'cargo_sale_id': bsg_cargo_sale_id.id
                            })
                    else:
                        home_pickup_line.sudo().write({
                            'cargo_sale_line_id': record.id,
                            'home_location': payload.get('home_location', home_pickup_line[0].home_location),
                            'pickup_location': payload.get('pickup_location', home_pickup_line[0].pickup_location),
                        })
                    if record.shipment_type.is_satha and record.loc_from.loc_branch_id.contact_numbers:
                        try:
                            message = "تم انشاء اتفاقيه سطحه (استلام من العميل) رقم: %s من %s الى %s جوال المستلم %s" %(record.sale_line_rec_name, record.loc_from.route_waypoint_name, record.loc_to.route_waypoint_name, record.receiver_mob_no)
                            self.send_sms(record.loc_from.loc_branch_id.contact_numbers, message)
                        except Exception as e:
                            print(e)
                if payload.get('is_home_delivery', 'false').lower() == 'true':
                    is_home_delivery_line = exisiting_service.filtered(lambda l: l.product_id.is_home_delivery)
                    if not is_home_delivery_line:
                        home_delivery_product_id = request.env['product.product'].sudo().search([('is_home_delivery', '=', True), ('attribute_value_ids.name', '=', arr_name)], limit=1)
                        if home_delivery_product_id:
                            other_service_lines.append({
                                'cargo_sale_line_id': record.id,
                                'product_id': home_delivery_product_id.id,
                                'cost':home_delivery_product_id.lst_price,
                                'qty': 1,
                                'home_location': payload.get('home_location', False),
                                'pickup_location': payload.get('pickup_location', False),
                                'tax_ids': [(6, 0, home_delivery_product_id.taxes_id.ids)] or False,
                                'cargo_sale_id': bsg_cargo_sale_id.id
                            })
                    else:
                        is_home_delivery_line.sudo().write({
                            'cargo_sale_line_id': record.id,
                            'home_location': payload.get('home_location', is_home_delivery_line[0].home_location),
                            'pickup_location': payload.get('pickup_location', is_home_delivery_line[0].pickup_location),
                        })
                    if record.shipment_type.is_satha and record.loc_to.loc_branch_id.contact_numbers:
                        try:
                            message = "تم انشاء اتفاقيه سطحه (توصيل للمنزل) رقم: %s من %s الى %s جوال المستلم %s" %(record.sale_line_rec_name, record.loc_from.route_waypoint_name, record.loc_to.route_waypoint_name, record.receiver_mob_no)
                            self.send_sms(record.loc_to.loc_branch_id.contact_numbers, message)
                        except Exception as e:
                            print(e)

                if int(payload.get('small_boxes', 0)) > 0 :
                    is_small_box_line = exisiting_service.filtered(lambda l: l.product_id.is_small_box)
                    if not is_small_box_line:
                        small_box_product_id = request.env['product.product'].sudo().search([('is_small_box', '=', True)], limit=1)
                        if small_box_product_id:
                            other_service_lines.append({
                                'cargo_sale_line_id': record.id,
                                'product_id': small_box_product_id.id,
                                'cost':small_box_product_id.lst_price * int(payload['small_boxes']),
                                'qty': int(payload['small_boxes']),
                                'home_location': payload.get('home_location', False),
                                'pickup_location': payload.get('pickup_location', False),
                                'tax_ids': [(6, 0, small_box_product_id.taxes_id.ids)] or False,
                                'cargo_sale_id': bsg_cargo_sale_id.id
                            })
                    else:
                        is_small_box_line.sudo().write({
                            'cargo_sale_line_id': record.id,
                            'cost': is_small_box_line[0].product_id.lst_price * int(payload['small_boxes']),
                            'qty': int(payload['small_boxes']),
                            'home_location': payload.get('home_location', is_small_box_line[0].home_location),
                            'pickup_location': payload.get('pickup_location', is_small_box_line[0].pickup_location),
                        })
                if  int(payload.get('medium_boxes', 0))> 0:
                    is_medium_box_line = exisiting_service.filtered(lambda l: l.product_id.is_medium_box)
                    if not is_medium_box_line:
                        medium_box_product_id = request.env['product.product'].sudo().search([('is_medium_box', '=', True)], limit=1)
                        if medium_box_product_id:
                            other_service_lines.append({
                                'cargo_sale_line_id': record.id,
                                'product_id': medium_box_product_id.id,
                                'cost':medium_box_product_id.lst_price * int(payload['medium_boxes']),
                                'qty': int(payload['medium_boxes']),
                                'home_location': payload.get('home_location', False),
                                'pickup_location': payload.get('pickup_location', False),
                                'tax_ids': [(6, 0, medium_box_product_id.taxes_id.ids)] or False,
                                'cargo_sale_id': bsg_cargo_sale_id.id
                            })
                    else:
                        is_medium_box_line.sudo().write({
                            'cargo_sale_line_id': record.id,
                            'cost': is_medium_box_line[0].product_id.lst_price * int(payload['medium_boxes']),
                            'qty': int(payload['medium_boxes']),
                            'home_location': payload.get('home_location', is_medium_box_line[0].home_location),
                            'pickup_location': payload.get('pickup_location', is_medium_box_line[0].pickup_location),
                        })


                if  int(payload.get('large_boxes', 0)) > 0:
                    is_large_box_line = exisiting_service.filtered(lambda l: l.product_id.is_large_box)
                    if not is_large_box_line:
                        large_box_product_id = request.env['product.product'].sudo().search([('is_large_box', '=', True)], limit=1)
                        if large_box_product_id:
                            other_service_lines.append({
                                'cargo_sale_line_id': record.id,
                                'product_id': large_box_product_id.id,
                                'cost':large_box_product_id.lst_price * int(payload['large_boxes']),
                                'qty': int(payload['large_boxes']),
                                'home_location': payload.get('home_location', False),
                                'pickup_location': payload.get('pickup_location', False),
                                'tax_ids': [(6, 0, large_box_product_id.taxes_id.ids)] or False,
                                'cargo_sale_id': bsg_cargo_sale_id.id
                            })
                    else:
                        is_large_box_line.sudo().write({
                            'cargo_sale_line_id': record.id,
                            'cost': is_large_box_line[0].product_id.lst_price * int(payload['large_boxes']),
                            'qty': int(payload['large_boxes']),
                            'home_location': payload.get('home_location', is_large_box_line[0].home_location),
                            'pickup_location': payload.get('pickup_location', is_large_box_line[0].pickup_location),
                        })
                        
                if other_service_lines:
                    request.env['other_service_items'].sudo().create(other_service_lines)
                    online_amount = float(payload.get('app_paid_amount', 0))
                    if payload.get('app_payment_method', False) == 'credit' and online_amount > 0:
                        invoice_ids = request.env['account.move'].sudo().search([('cargo_sale_id', '=', bsg_cargo_sale_id.id), ('state', 'in', ['open', 'paid'])])
                        if not invoice_ids:
                            bsg_cargo_sale_id.with_context({'do_not_create_invoice': False}).invoice_create_validate()
                            invoice_ids = request.env['account.move'].sudo().search([('cargo_sale_id', '=', bsg_cargo_sale_id.id)])
                        else:
                            invoice_ids = bsg_cargo_sale_id.create_other_serive_invoice()
                        acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'payfort')],limit=1)
                        if invoice_ids:
                            context = {
                                'active_id': bsg_cargo_sale_id.id,
                                'show_invoice_amount': True,
                                'pass_sale_order_id': bsg_cargo_sale_id.id,
                                'is_patrtially_payment': True,
                            # 'default_cargo_sale_order_id': self.id,
                            }
                            branch_ids = acquirer_id.journal_id.branches
                            payment_id = request.env['account.payment'].sudo().with_context(context).create({
                                'payment_type': 'inbound',
                                'partner_id': bsg_cargo_sale_id.customer.id,
                                'partner_type': 'customer',
                                'journal_id': acquirer_id.journal_id.id,
                                'amount': online_amount,
                                'communication': bsg_cargo_sale_id.name,
                                'show_invoice_amount': True,
                                'invoice_ids':  [(6, 0,  invoice_ids.ids)],
                                'payment_method_id':1,
                                'cargo_sale_line_id':record.id,
                                'branch_ids':  branch_ids and branch_ids[0].id or False,
                                'app_fortid': payload.get('app_fortid', False),
                                'provider_tag': payload.get('provider_tag', False),
                            })
                            payment_id.action_validate_invoice_payment()
                            cargo_line_pay = request.env['account.cargo.line.payment'].sudo()
                            for so_line in bsg_cargo_sale_id.mapped('order_line_ids'):
                                    if not so_line.is_paid and payment_id.residual_amount > 0:
                                        for inv_line in invoice_ids.mapped('invoice_line_ids').filtered(lambda  s: s.cargo_sale_line_id.id == so_line.id):
                                            cargo_line_pay.with_context({'without_check_amount':True}).sudo().create({
                                            'cargo_sale_line_id': inv_line.cargo_sale_line_id.id,
                                            'account_invoice_line_id': inv_line.id,
                                            'amount': inv_line.price_total,
                                            'residual': inv_line.price_total - inv_line.paid_amount,
                                            'account_payment_id' : payment_id.id,
                                        })
                    else:
                        pass
                data = self.get_order_info(record)
            return valid_response(data)
        except Exception as e:
            se = http.serialize_exception(e)
            request.env['api.log'].sudo().create({
                'endpoint': '/api/add_other_services',
                'request_payload': str(payload),
                'exception_message': se,
            })
            return invalid_response("Error: ", se)
      
    @validate_token
    @http.route("/api/register_payment", type="http", auth="none", methods=["GET"], csrf=False)
    def register_payment(self, **payload):
        try:
            order_number = payload.get('order_ref', False)
            online_amount = float(payload.get('app_paid_amount', 0))
            wallet_amount = float(payload.get('wallet_amount', 0))
            fort_id = payload.get('app_fortid', False)
            #app_payment_method = payload.get('app_payment_method', False)
            
            data = []
            _logger.warning("............ API Register Payment ........")
            _logger.warning("............ API Register Payment Order Number........ %s" % str(order_number))
            _logger.warning("............ API Register Payment Online Amount........ %s" % str(online_amount))
            _logger.warning("............ API Register Payment Wallet Amount........ %s" % str(wallet_amount))
            _logger.warning("............ API Register Payment Fort ID........ %s" % str(fort_id))

            if order_number and fort_id and online_amount > 0:
                record = request.env['bsg_vehicle_cargo_sale_line'].sudo().search([('sale_line_rec_name', '=', order_number)], limit=1)
                if record.unit_charge <= 0:
                    record._onchange_shipment_type()
                if record:
                    sale_rec = record.bsg_cargo_sale_id
                    context = {
                    'active_id': sale_rec.id,
                    'show_invoice_amount': True,
                    'pass_sale_order_id': sale_rec.id,
                    'is_patrtially_payment': True,
                    # 'default_cargo_sale_order_id': self.id,
                    }
                    invoice_ids = request.env['account.move'].sudo().search([('cargo_sale_id', '=', sale_rec.id)])
                    if not invoice_ids:
                        sale_rec.with_context({'do_not_create_invoice': False}).invoice_create_validate()
                        invoice_ids = request.env['account.move'].sudo().search([('cargo_sale_id', '=', sale_rec.id)])
                    sale_rec.recieved_from_customer_date = False
                    record.recieved_from_customer_date = False
                    acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'payfort')],limit=1)
                    payment_id = request.env['account.payment'].sudo().with_context(context).create({
                        'payment_type': 'inbound',
                        'partner_id': sale_rec.customer.id,
                        'partner_type': 'customer',
                        'journal_id': acquirer_id.journal_id.id,
                        'amount': online_amount,
                        'communication': sale_rec.name,
                        'show_invoice_amount': True,
                        'invoice_ids': [(6, 0, invoice_ids.ids)],
                        'payment_method_id':1,
                        'cargo_sale_line_id':record.id,
                        'transaction_reference': sale_rec.transaction_reference,
                        'app_fortid': fort_id,
                        'tamara_reference_id': payload.get('tamara_reference_id', False),
                        'provider_tag': payload.get('provider_tag', False),
                    })
                    payment_id.branach_ids =  False
                    payment_id.action_validate_invoice_payment()
                    request.env['payment.transaction'].sudo().create({
                        'app_fortid':fort_id,
                        'tamara_reference_id': payload.get('tamara_reference_id', False),
                        'cargo_sale_ids': [(6, 0, [sale_rec.id])],
                        'amount': online_amount,
                        'partner_id': sale_rec.customer.id,
                        'date': fields.Date.today(),
                        'acquirer_id':acquirer_id.id,
                        'currency_id': 153,
                        'state':'done',
                        'payment_id': payment_id.id,
                        'is_processed': True,
                        'acquirer_reference': payload.get('authorization_code', False)
                    })
                    cargo_line_pay = request.env['account.cargo.line.payment'].sudo()
                    for so_line in sale_rec.mapped('order_line_ids'):
                            if not so_line.is_paid and payment_id.residual_amount > 0:
                                for inv_line in invoice_ids.mapped('invoice_line_ids').filtered(lambda  s: s.cargo_sale_line_id.id == so_line.id):
                                    cargo_line_pay.with_context({'without_check_amount':True}).sudo().create({
                                    'cargo_sale_line_id': inv_line.cargo_sale_line_id.id,
                                    'account_invoice_line_id': inv_line.id,
                                    'amount': inv_line.price_total,
                                    'residual': inv_line.price_total - inv_line.paid_amount,
                                    'account_payment_id' : payment_id.id,
                                })

                    sale_rec.write({
                        'app_payment_method': payload.get('app_payment_method', False),
                        'app_paid_amount': online_amount,
                        'app_fortid': fort_id,
                    })
                    data.append({
                        'paid_amount': online_amount
                    })

            if order_number and wallet_amount > 0:
                record = request.env['bsg_vehicle_cargo_sale_line'].sudo().search([('sale_line_rec_name', '=', order_number)], limit=1)
                if record.unit_charge <= 0:
                    record._onchange_shipment_type()
                if record:
                    sale_rec = record.bsg_cargo_sale_id
                    context = {
                    'active_id': sale_rec.id,
                    'show_invoice_amount': True,
                    'pass_sale_order_id': sale_rec.id,
                    'is_patrtially_payment': True,
                    # 'default_cargo_sale_order_id': self.id,
                    }
                    invoice_ids = request.env['account.move'].sudo().search([('cargo_sale_id', '=', sale_rec.id)])
                    
                    if not invoice_ids:
                        sale_rec.with_context({'do_not_create_invoice': False}).invoice_create_validate()
                        invoice_ids = request.env['account.move'].sudo().search([('cargo_sale_id', '=', sale_rec.id)])
                    sale_rec.recieved_from_customer_date = False
                    record.recieved_from_customer_date = False
                    acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'payfort')],limit=1)
                    payment_id = request.env['account.payment'].sudo().with_context(context).create({
                        'payment_type': 'inbound',
                        'partner_id': sale_rec.customer.id,
                        'partner_type': 'customer',
                        'journal_id': acquirer_id.journal_id.id,
                        'amount': wallet_amount,
                        'communication': sale_rec.name,
                        'show_invoice_amount': True,
                        'invoice_ids': [(6, 0, invoice_ids.ids)],
                        'payment_method_id':1,
                        'cargo_sale_line_id':record.id,
                        'transaction_reference': sale_rec.transaction_reference,
                        'app_fortid': 'Walt-'+payload.get('wallet_transcation_ref', ''),
                        'provider_tag': payload.get('provider_tag', False),
                    })
                    payment_id.branach_ids =  False
                    payment_id.action_validate_invoice_payment()
                    cargo_line_pay = request.env['account.cargo.line.payment'].sudo()
                    for so_line in sale_rec.mapped('order_line_ids'):
                            if not so_line.is_paid and payment_id.residual_amount > 0:
                                for inv_line in invoice_ids.mapped('invoice_line_ids').filtered(lambda  s: s.cargo_sale_line_id.id == so_line.id):
                                    cargo_line_pay.with_context({'without_check_amount':True}).sudo().create({
                                    'cargo_sale_line_id': inv_line.cargo_sale_line_id.id,
                                    'account_invoice_line_id': inv_line.id,
                                    'amount': inv_line.price_total,
                                    'residual': inv_line.price_total - inv_line.paid_amount,
                                    'account_payment_id' : payment_id.id,
                                })
                    sale_rec.write({
                        'app_payment_method': payload.get('app_payment_method', False),
                        'app_paid_amount': wallet_amount,
                        'app_fortid': fort_id,
                    })
                    data.append({
                        'paid_amount': wallet_amount
                    })
                    if record.state == 'registered':
                        sale_rec.state = 'registered'            

            return valid_response(data)
        except Exception as e:
            se = http.serialize_exception(e)
            request.env['api.log'].sudo().create({
                'endpoint': '/api/register_payment',
                'request_payload': str(payload),
                'exception_message': se,
            })
            return invalid_response("Error: ", se)
            
    def send_sms(self, rendered_sms_to, sms_rendered_content):

        sms_rendered_content_msg = ''.join(['{:04x}'.format(ord(byte)).upper() for byte in sms_rendered_content])
        sms_obj = request.env['send.mobile.sms.template'].sudo()
        send_url = sms_obj._default_api_url()
        username = sms_obj._default_username()
        password = sms_obj._default_password()
        send_link = send_url.replace('{username}',username).replace('{password}',password).\
        replace('{sender}','Albassami').replace('{numbers}',rendered_sms_to).replace('{message}',sms_rendered_content_msg)
        response = requests.request("GET", url = send_link).text
        request.env['sms_track'].sudo().sms_track_create(False, sms_rendered_content_msg, rendered_sms_to, response, False )
        return True

    @validate_token
    @http.route("/api/create_order", type="http", auth="none", methods=["POST"], csrf=False)
    def pos_create_order(self, **payload):
        data = []
        _logger.info("/create_order   "+str(payload))
        try:
            payment_id = False
            owner_keys = ['owner_name', 'owner_id_type', 'owner_id_card_no', 'owner_nationality']
            vals = {'customer':  payload.get('customer', False), 'partner_types': 5, 'customer_price_list':1,
                    'customer_type': 'individual'}
            fort_id = payload.get('app_fortid', False)
            online_amount = float(payload.get('app_paid_amount', 0))
            wallet_amount = float(payload.get('wallet_amount', 0))
            
            loc_from  = request.env['bsg_route_waypoints'].sudo().browse(int(payload.get('loc_from')))
            loc_to  = request.env['bsg_route_waypoints'].sudo().browse(int(payload.get('loc_to')))
            is_international =  loc_from.is_international or  loc_to.is_international
            #pricelist_code = payload.get('pricelist_code', 'mobile_price_list')
            pricelist_code = payload.get('pricelist_code', 'Public_Pricelist')
            price_list = request.env['product.pricelist'].sudo().search([('pricelist_code', '=', pricelist_code)], limit=1)
            _logger.info("price_list   "+str(price_list))
            if payload.get('app_payment_method', False) == 'credit' and online_amount > 0 and fort_id:
                if  not is_international and price_list:
                    vals['customer_price_list'] = price_list.id
            for key in owner_keys + ['payment_method', 'loc_from', 'loc_to', 'receiver_name', 'receiver_type','receiver_id_type', 'receiver_nationality', 'receiver_mob_no', 'receiver_id_card_no', 'gps_location_from', 'gps_location_to', 'gps_distance', 'gps_time']:
                vals.update({
                    key: payload.get(key, False)
                })
            vals['owner_nationality'] =int(vals.get('owner_nationality', 379))
            vals['receiver_nationality'] = int(vals.get('receiver_nationality', 379))
            match = re.match(r'2[0-9]{9}', vals.get('receiver_id_card_no'))
            if match:
                vals['receiver_visa_no'] = vals['receiver_id_card_no']
                vals['receiver_id_card_no'] = False
            owner_match = re.match(r'2[0-9]{9}', vals.get('owner_id_card_no', ''))
            if owner_match:
                vals['owner_visa_no'] = vals['owner_id_card_no']
                vals['owner_id_card_no'] = False
            vals['shipment_type'] = payload.get('tripway', False)
            vals['payment_method'] = payload.get("payment_method",7)
            vals['owner_type'] = vals.get('owner_nationality', False) and int(vals['owner_nationality']) == 192 and '1' or '2'
            vals['owner_id_type'] = vals.get('owner_nationality', False) and int(vals['owner_nationality']) == 192 and 'saudi_id_card' or 'iqama'
            vals['receiver_type'] = vals.get('receiver_nationality', False) and int(vals['receiver_nationality']) == 192 and '1' or '2' 
            vals['receiver_id_type'] = vals.get('receiver_nationality', False) and int(vals['receiver_nationality']) == 192 and 'saudi_id_card' or 'iqama' 
            vals['is_from_app'] = True
            vals['app_payment_method'] = payload.get('app_payment_method', False)
            vals['app_paid_amount'] = float(payload.get('app_paid_amount', 0))
            vals['app_fortid'] = payload.get('app_fortid', False)
            vals['transaction_reference'] = payload.get('transaction_reference', False)
            vals['qitaf_coupon'] = not is_international and payload.get('coupon', False) or False
            vals['api_request_vals'] = str(payload)
            res = request.env['bsg_vehicle_cargo_sale'].sudo().create(vals)
            res.same_as_customer = True
            res._onchange_same_as_customer ()
            if not res.receiver_nationality:
                res.sender_nationality = 379
            payload['chassis'] =  payload.get('chassis','').replace('A','أ').replace('B','ب').replace('J','ح').replace('D','د').replace('R','ر').replace('S','س').replace('X','ص').replace('T','ط').replace('E','ع').replace('G','ق').replace('K','ك').replace('L','ل').replace('Z','م').replace('N','ن').replace('H','ه').replace('U','و').replace('V','ى')
            so_line_keys = ['shipment_type', 'car_make', 'car_model', 'plate_no', 'plate_type', 'chassis', 'year', 'car_color','palte_one', 'palte_second', 'palte_third', 'non_saudi_plate_no']
            line_vals = {}
            for lkey in so_line_keys:
                value =  payload.get(lkey, False)
                line_vals.update({
                    lkey: value and value.isdigit() and int(value) or value
                })
            line_vals['plate_registration'] = 'non-saudi'
            is_all_digits = all([p.isdigit() for p in list(str(line_vals.get('non_saudi_plate_no','')).replace(' ',''))])
            if line_vals.get('plate_type') in [2,3,4,5,6,7] and line_vals.get('non_saudi_plate_no', False) and not is_all_digits:
                line_vals['plate_registration'] = 'saudi'
                full_plate = line_vals['non_saudi_plate_no'].replace(' ','').replace('A','أ').replace('B','ب').replace('J','ح').replace('D','د').replace('R','ر').replace('S','س').replace('X','ص').replace('T','ط').replace('E','ع').replace('G','ق').replace('K','ك').replace('L','ل').replace('Z','م').replace('N','ن').replace('H','ه').replace('U','و').replace('V','ى')
                plate_list = list(full_plate)
                line_vals['palte_one'] = payload.get('palte_one')
                line_vals['palte_second'] = payload.get('palte_second')
                line_vals['palte_third'] = payload.get('palte_third')
                line_vals['plate_no'] = payload.get('plate_no')
            elif line_vals.get('plate_type') in [8,9,10]:
                line_vals['plate_registration'] = 'non-saudi'
                line_vals['non_saudi_plate_no'] = line_vals.get('non_saudi_plate_no', False) or line_vals.get('plate_no', False)
                line_vals['plate_no'] = False
            else:
                line_vals['plate_registration'] = 'new_vehicle'
                line_vals['non_saudi_plate_no'] = line_vals.get('non_saudi_plate_no',False) or  line_vals.get('plate_no', False)
                line_vals['plate_no'] = False
            line_vals['bsg_cargo_sale_id'] = res.id
            line_vals['service_type'] = payload.get('service_type', 1)
            bsg_config = request.env['bsg_car_config'].sudo().search([('car_maker', '=', line_vals['car_make'])])
            line_vals['car_make'] = bsg_config.id
            line_vals['is_from_app'] = True
            if not(res.loc_from.is_international or res.loc_to.is_international):
                line_vals['tax_ids'] =  [(6, 0, request.env.user.company_id.tax_ids.ids)] 
            without_calculate_pric = False    
            if payload.get('price', False):
                line_vals['unit_charge'] = float(payload.get('price', 0))  
                if line_vals['unit_charge'] > 0:
                    without_calculate_pric = True
            so_line = request.env['bsg_vehicle_cargo_sale_line'].sudo().with_context({'without_calculate_pric':without_calculate_pric}).create(line_vals)
            if not payload.get('price', False):
                so_line._onchange_shipment_type()
            if not is_international and price_list:
                #line_vals.update({'customer_price_list':  price_list and price_list.id or 1, 'discount':15})
                so_line.write({'customer_price_list':  price_list and price_list.id or 1, 'discount':price_list and price_list.item_ids and price_list.item_ids[0].percent_price or 0})
            if not payload.get('price', False):
                so_line._onchange_shipment_type()
            arr_name = 'Regular'
            if so_line.shipment_type.is_satha:
                arr_name = 'Satha'
            other_service_lines = []
            sms_sent = False
            if so_line.shipment_type.is_satha:
                sms_sent = True
                if  loc_from.loc_branch_id.contact_numbers:
                    try:
                        message = "تم انشاء اتفاقيه سطحه (استلام من العميل) رقم: %s من %s الى %s جوال المستلم %s" %(so_line.sale_line_rec_name, loc_from.route_waypoint_name, loc_to.route_waypoint_name, so_line.receiver_mob_no)
                        self.send_sms(loc_from.loc_branch_id.contact_numbers, message)
                    except Exception as e:
                        print(e)
            if payload.get('is_home_pickup', 'false').lower() == 'true':
                home_pickup_product_id = request.env['product.product'].sudo().search([('is_home_pickup', '=', True), ('attribute_value_ids.name', '=', arr_name)], limit=1)
                if home_pickup_product_id:
                    other_service_lines.append({
                        'cargo_sale_line_id': so_line.id,
                        'product_id': home_pickup_product_id.id,
                        'cost':home_pickup_product_id.lst_price,
                        'qty':1,
                        'home_location': payload.get('home_location', False),
                        'pickup_location': payload.get('pickup_location', False),
                        'tax_ids': [(6, 0, home_pickup_product_id.taxes_id.ids)] or False,
                        'cargo_sale_id': res.id
                    })

                if not sms_sent and loc_from.loc_branch_id.contact_numbers:
                    try:
                        message = "تم انشاء اتفاقيه سطحه (استلام من العميل) رقم: %s من %s الى %s جوال المستلم %s" %(so_line.sale_line_rec_name, loc_from.route_waypoint_name, loc_to.route_waypoint_name, so_line.receiver_mob_no)
                        self.send_sms(loc_from.loc_branch_id.contact_numbers, message)
                    except Exception as e:
                        print(e)
            if payload.get('is_home_delivery', 'false').lower() == 'true':
                home_delivery_product_id = request.env['product.product'].sudo().search([('is_home_delivery', '=', True), ('attribute_value_ids.name', '=', arr_name)], limit=1)
                if home_delivery_product_id:
                    other_service_lines.append({
                        'cargo_sale_line_id': so_line.id,
                        'product_id': home_delivery_product_id.id,
                        'cost':home_delivery_product_id.lst_price,
                        'qty': 1,
                        'home_location': payload.get('home_location', False),
                        'pickup_location': payload.get('pickup_location', False),
                        'tax_ids': [(6, 0, home_delivery_product_id.taxes_id.ids)] or False,
                        'cargo_sale_id': res.id
                    })
                    
                    if not sms_sent and loc_to.loc_branch_id.contact_numbers:
                        try:
                            message = "تم انشاء اتفاقيه سطحه (توصيل للمنزل) رقم: %s من %s الى %s جوال المستلم %s" %(so_line.sale_line_rec_name, loc_from.route_waypoint_name, loc_to.route_waypoint_name, so_line.receiver_mob_no)
                            self.send_sms(loc_to.loc_branch_id.contact_numbers, message)
                        except Exception as e:
                            print(e)
            if int(payload.get('small_boxes', 0)) > 0 :
                small_box_product_id = request.env['product.product'].sudo().search([('is_small_box', '=', True)], limit=1)
                if small_box_product_id:
                    other_service_lines.append({
                        'cargo_sale_line_id': so_line.id,
                        'product_id': small_box_product_id.id,
                        'cost':small_box_product_id.lst_price * int(payload['small_boxes']),
                        'qty': int(payload['small_boxes']),
                        'home_location': payload.get('home_location', False),
                        'pickup_location': payload.get('pickup_location', False),
                        'tax_ids': [(6, 0, small_box_product_id.taxes_id.ids)] or False,
                        'cargo_sale_id': res.id
                    })

            if  int(payload.get('medium_boxes', 0))> 0:
                medium_box_product_id = request.env['product.product'].sudo().search([('is_medium_box', '=', True)], limit=1)
                if medium_box_product_id:
                    other_service_lines.append({
                        'cargo_sale_line_id': so_line.id,
                        'product_id': medium_box_product_id.id,
                        'cost':medium_box_product_id.lst_price * int(payload['medium_boxes']),
                        'qty': int(payload['medium_boxes']),
                        'home_location': payload.get('home_location', False),
                        'pickup_location': payload.get('pickup_location', False),
                        'tax_ids': [(6, 0, medium_box_product_id.taxes_id.ids)] or False,
                        'cargo_sale_id': res.id
                    })

            if  int(payload.get('large_boxes', 0)) > 0:
                large_box_product_id = request.env['product.product'].sudo().search([('is_large_box', '=', True)], limit=1)
                if large_box_product_id:
                    other_service_lines.append({
                        'cargo_sale_line_id': so_line.id,
                        'product_id': large_box_product_id.id,
                        'cost':large_box_product_id.lst_price * int(payload['large_boxes']),
                        'qty': int(payload['large_boxes']),
                        'home_location': payload.get('home_location', False),
                        'pickup_location': payload.get('pickup_location', False),
                        'tax_ids': [(6, 0, large_box_product_id.taxes_id.ids)] or False,
                        'cargo_sale_id': res.id
                    })
            online_amount = float(payload.get('app_paid_amount', 0))
            fort_id = payload.get('app_fortid', False)
            if other_service_lines:
                request.env['other_service_items'].sudo().create(other_service_lines)
            if payload.get('coupon', False):
                res.with_context({'do_not_raise_exception': True}).action_get_qitaf_discount()
            if (payload.get('app_payment_method', False) == 'credit' and online_amount > 0 and fort_id) or (payload.get('wallet_transcation_ref', False) and wallet_amount > 0) or payload.get('tamara_reference_id', False):
                res.confirm_btn()
                res.state = 'registered'
                so_line.state = 'registered'
            else:
                res.with_context({'do_not_create_invoice': True}).confirm_btn()
                res.state = 'registered'
                so_line.state = 'registered'
            so_line.recieved_from_customer_date = False
            res.recieved_from_customer_date = False
                
            data = [{
                'order_id': so_line.id,
                'order_ref': so_line.sale_line_rec_name,
                'track_tiny_url': so_line.track_tiny_url
            }]
            if data:
                if payload.get('app_payment_method', False) == 'credit' and online_amount > 0 and fort_id or payload.get('tamara_reference_id', False):
                    provider = payload.get('provider', 'payfort')
                    acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', provider)],limit=1)
                    sale_rec = so_line.bsg_cargo_sale_id
                    context = {
                      'active_id': sale_rec.id,
                      'show_invoice_amount': True,
                      'pass_sale_order_id': sale_rec.id,
                      'is_patrtially_payment': True,
                    }
                    inv = request.env['account.move'].sudo().search([('cargo_sale_id', '=', res.id)], limit=1)
                    _logger.error("/get_create_order payment data before invoice check........................+  " + str(data))
                    if inv:
                        _logger.warning("............Create order invoice is ........ %s" %inv)
                    if not inv:
                        _logger.error("/get_create_order payment data under invoice check........................+  " + str(
                                data))
                        trans_id = request.env['payment.transaction'].sudo().create({
                            'app_fortid': fort_id,
                            'tamara_reference_id': payload.get('tamara_reference_id', False),
                            'cargo_sale_ids': [(6, 0, [res.id])],
                            'amount': online_amount,
                            'partner_id': sale_rec.customer.id,
                            'date': fields.Date.today(),
                            'acquirer_id': acquirer_id.id,
                            'currency_id': 153,
                            'state': 'done',
                            'payment_id': payment_id.id if payment_id else False,
                            'is_processed': True,
                            'acquirer_reference': payload.get('authorization_code', False)
                        })
                        data = [{
                            'order_id': so_line.id,
                            'order_ref': so_line.sale_line_rec_name,
                            'invoice_id':inv,
                            'transaction_id':trans_id
                        }]
                        return valid_response(data)

                    _logger.warning("............Create order partner_id is ........ %s"%sale_rec.customer.id)
                    _logger.warning("............Create order journal_id is ........ %s"%acquirer_id.journal_id.id)
                    _logger.warning("............Create order online_amount is ........ %s"%online_amount)
                    _logger.warning("............Create order communication is ........ %s"%sale_rec.name)
                    _logger.warning("............Create order invoice_ids is ........ %s"%inv[0].id if inv else 'Create order invoice_ids is None')
                    payment_method_id_log = request.env['account.payment.method'].sudo().search(['&',('payment_type', '=', 'inbound'),('name','=','Electronic')], limit=1).id or  3
                    _logger.warning("............Create order payment_method_id is ........ %s"%payment_method_id_log)
                    _logger.warning("............Create order cargo_sale_line_id is ........ %s"%so_line.id)
                    _logger.warning("............Create order transaction_reference is ........ %s"%sale_rec.transaction_reference)
                    _logger.warning("............Create order app_fortid is ........ %s"%fort_id)
                    _logger.warning("............Create order tamara_reference_id is ........ %s"%payload.get('tamara_reference_id', False))
                    _logger.warning("............Create order provider_tag is ........ %s"%payload.get('provider_tag', False))

                    if online_amount > 0:
                      payment_id = request.env['account.payment'].sudo().with_context(context).create({
                          'payment_type': 'inbound',
                          'partner_id': sale_rec.customer.id,
                          'partner_type': 'customer',
                          'journal_id': acquirer_id.journal_id.id,
                          'amount': online_amount,
                          'communication': sale_rec.name,
                          'show_invoice_amount': True,
                          'invoice_ids': [(4, inv[0].id, None)],
                          'payment_method_id': request.env['account.payment.method'].sudo().search(['&',('payment_type', '=', 'inbound'),('name','=','Electronic')], limit=1).id or  3,
                          'cargo_sale_line_id':so_line.id,
                          'transaction_reference': sale_rec.transaction_reference,
                          'app_fortid': fort_id,
                          'tamara_reference_id': payload.get('tamara_reference_id', False),
                          'provider_tag': payload.get('provider_tag', False),
                      })
                      _logger.warning("............Create order payment id is ........ %s" %payment_id)
                      payment_id.branach_ids =  False
                      payment_id.action_validate_invoice_payment()
                      trans_id = request.env['payment.transaction'].sudo().create({
                      'app_fortid':fort_id,
                      'tamara_reference_id': payload.get('tamara_reference_id', False),
                      'cargo_sale_ids': [(6, 0, [res.id])],
                      'amount': online_amount,
                      'partner_id': sale_rec.customer.id,
                      'date': fields.Date.today(),
                      'acquirer_id':acquirer_id.id,
                      'currency_id': 153,
                      'state':'done',
                      'payment_id': payment_id.id,
                      'is_processed': True,
                      'acquirer_reference': payload.get('authorization_code', False)
                      })
                      if payload.get('tamara_reference_id', False):
                        trans_id.write({'is_tamara': True, 'tamara_transaction_ids': [(6, 0, [res.id])]})
                      payment_id.payment_transaction_id = trans_id.id
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
            
            
            if (payload.get('wallet_transcation_ref', False) and wallet_amount > 0):
                provider = payload.get('provider', 'payfort')
                acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', provider)],limit=1)
                sale_rec = so_line.bsg_cargo_sale_id
                context = {
                'active_id': sale_rec.id,
                'show_invoice_amount': True,
                'pass_sale_order_id': sale_rec.id,
                'is_patrtially_payment': True,
                }
                inv = request.env['account.move'].sudo().search([('cargo_sale_id', '=', res.id)], limit=1)
                if not inv:
                    return valid_response(data)

                payment_id = request.env['account.payment'].sudo().with_context(context).create({
                    'payment_type': 'inbound',
                    'partner_id': sale_rec.customer.id,
                    'partner_type': 'customer',
                    'journal_id': acquirer_id.journal_id.id,
                    'amount': wallet_amount,
                    'communication': sale_rec.name,
                    'show_invoice_amount': True,
                    'invoice_ids': [(4, inv[0].id, None)],
                    'payment_method_id': request.env['account.payment.method'].sudo().search(['&',('payment_type', '=', 'inbound'),('name','=','Electronic')], limit=1).id or  3,
                    'cargo_sale_line_id':so_line.id,
                    'transaction_reference': sale_rec.transaction_reference ,
                    'app_fortid': 'Walt'+payload.get('wallet_transcation_ref', ''),
                    'tamara_reference_id': payload.get('tamara_reference_id', False),
                    'provider_tag': payload.get('provider_tag', False),
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
            if not payment_id and online_amount > 0:
                provider = payload.get('provider', 'payfort')
                acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', provider)], limit=1)
                sale_rec = so_line.bsg_cargo_sale_id
                context = {
                    'active_id': sale_rec.id,
                    'show_invoice_amount': True,
                    'pass_sale_order_id': sale_rec.id,
                    'is_patrtially_payment': True,
                }
                payment_id = request.env['account.payment'].sudo().with_context(context).create({
                    'payment_type': 'inbound',
                    'partner_id': sale_rec.customer.id,
                    'partner_type': 'customer',
                    'journal_id': acquirer_id.journal_id.id,
                    'amount': online_amount,
                    'communication': sale_rec.name,
                    'show_invoice_amount': True,
                    'invoice_ids': [(4, inv[0].id, None)],
                    'payment_method_id': request.env['account.payment.method'].sudo().search(
                        ['&', ('payment_type', '=', 'inbound'), ('name', '=', 'Electronic')], limit=1).id or 3,
                    'cargo_sale_line_id': so_line.id,
                    'transaction_reference': sale_rec.transaction_reference,
                    'app_fortid': fort_id,
                    'tamara_reference_id': payload.get('tamara_reference_id', False),
                    'provider_tag': payload.get('provider_tag', False),
                })
                payment_id.branach_ids = False
                # payment_id.action_validate_invoice_payment()
                trans_id = request.env['payment.transaction'].sudo().create({
                    'app_fortid': fort_id,
                    'tamara_reference_id': payload.get('tamara_reference_id', False),
                    'cargo_sale_ids': [(6, 0, [res.id])],
                    'amount': online_amount,
                    'partner_id': sale_rec.customer.id,
                    'date': fields.Date.today(),
                    'acquirer_id': acquirer_id.id,
                    'currency_id': 153,
                    'state': 'done',
                    'payment_id': payment_id.id,
                    'is_processed': True,
                    'acquirer_reference': payload.get('authorization_code', False)
                })
                if payload.get('tamara_reference_id', False):
                    trans_id.write({'is_tamara': True, 'tamara_transaction_ids': [(6, 0, [res.id])]})
                payment_id.payment_transaction_id = trans_id.id
                cargo_line_pay = request.env['account.cargo.line.payment'].sudo()
                for so_line in sale_rec.mapped('order_line_ids'):
                    if not so_line.is_paid and payment_id.residual_amount > 0:
                        for inv_line in inv.mapped('invoice_line_ids').filtered(
                                lambda s: s.cargo_sale_line_id.id == so_line.id):
                            cargo_line_pay.with_context({'without_check_amount': True}).sudo().create({
                                'cargo_sale_line_id': inv_line.cargo_sale_line_id.id,
                                'account_invoice_line_id': inv_line.id,
                                'amount': inv_line.price_total,
                                'residual': inv_line.price_total - inv_line.paid_amount,
                                'account_payment_id': payment_id.id,
                            })
            if so_line.state == 'registered':
                res.state = 'registered'
            _logger.error("/get_create_order payment data logs down the invoice..............  ")
            _logger.error("/get_create_order payment data........................+  "+str(data))
            return valid_response(data)
        except Exception as e:
            se = http.serialize_exception(e)
            request.env['api.log'].sudo().create({
                'endpoint': '/api/create_order',
                'request_payload': str(payload),
                'exception_message': se,
            })
            return invalid_response("Error: ", se)

    @validate_token
    @http.route("/api/create_order_chatbot", type="http", auth="none", methods=["POST"], csrf=False)
    def chat_bot_create_order(self, **payload):
        data = []
        _logger.info("/create_order   " + str(payload))
        try:
            payment_id = False
            owner_keys = ['owner_name', 'owner_id_type', 'owner_id_card_no', 'owner_nationality']
            vals = {'customer': payload.get('customer', False), 'partner_types': 5, 'customer_price_list': 1,
                    'customer_type': 'individual'}
            fort_id = payload.get('app_fortid', False)
            online_amount = float(payload.get('app_paid_amount', 0))
            wallet_amount = float(payload.get('wallet_amount', 0))

            loc_from = request.env['bsg_route_waypoints'].sudo().browse(int(payload.get('loc_from')))
            loc_to = request.env['bsg_route_waypoints'].sudo().browse(int(payload.get('loc_to')))
            is_international = loc_from.is_international or loc_to.is_international
            # pricelist_code = payload.get('pricelist_code', 'mobile_price_list')
            pricelist_code = payload.get('pricelist_code', 'Public_Pricelist')
            price_list = request.env['product.pricelist'].sudo().search([('pricelist_code', '=', pricelist_code)],
                                                                        limit=1)
            _logger.info("price_list   " + str(price_list))
            if payload.get('app_payment_method', False) == 'credit' and online_amount > 0 and fort_id:
                if not is_international and price_list:
                    vals['customer_price_list'] = price_list.id
            for key in owner_keys + ['payment_method', 'loc_from', 'loc_to', 'receiver_name', 'receiver_type',
                                     'receiver_id_type', 'receiver_nationality', 'receiver_mob_no',
                                     'receiver_id_card_no',
                                     'gps_location_from', 'gps_location_to', 'gps_distance', 'gps_time']:
                vals.update({
                    key: payload.get(key, False)
                })
            vals['owner_nationality'] = int(vals.get('owner_nationality', 379))
            vals['receiver_nationality'] = int(vals.get('receiver_nationality', 379))
            match = re.match(r'2[0-9]{9}', vals.get('receiver_id_card_no'))
            if match:
                vals['receiver_visa_no'] = vals['receiver_id_card_no']
                vals['receiver_id_card_no'] = False
            owner_match = re.match(r'2[0-9]{9}', vals.get('owner_id_card_no', ''))
            if owner_match:
                vals['owner_visa_no'] = vals['owner_id_card_no']
                vals['owner_id_card_no'] = False
            vals['shipment_type'] = payload.get('tripway', False)
            vals['payment_method'] = payload.get("payment_method", 7)
            vals['owner_type'] = vals.get('owner_nationality', False) and int(
                vals['owner_nationality']) == 192 and '1' or '2'
            vals['owner_id_type'] = vals.get('owner_nationality', False) and int(
                vals['owner_nationality']) == 192 and 'saudi_id_card' or 'iqama'
            vals['receiver_type'] = vals.get('receiver_nationality', False) and int(
                vals['receiver_nationality']) == 192 and '1' or '2'
            vals['receiver_id_type'] = vals.get('receiver_nationality', False) and int(
                vals['receiver_nationality']) == 192 and 'saudi_id_card' or 'iqama'
            vals['is_from_app'] = True
            vals['app_payment_method'] = payload.get('app_payment_method', False)
            vals['app_paid_amount'] = float(payload.get('app_paid_amount', 0))
            vals['app_fortid'] = payload.get('app_fortid', False)
            vals['transaction_reference'] = payload.get('transaction_reference', False)
            vals['qitaf_coupon'] = not is_international and payload.get('coupon', False) or False
            vals['api_request_vals'] = str(payload)
            res = request.env['bsg_vehicle_cargo_sale'].sudo().create(vals)
            res.same_as_customer = True
            res._onchange_same_as_customer()
            if not res.receiver_nationality:
                res.sender_nationality = 379
            payload['chassis'] = payload.get('chassis', '').replace('A', 'أ').replace('B', 'ب').replace('J',
                                                                                                        'ح').replace(
                'D', 'د').replace('R', 'ر').replace('S', 'س').replace('X', 'ص').replace('T', 'ط').replace('E',
                                                                                                          'ع').replace(
                'G', 'ق').replace('K', 'ك').replace('L', 'ل').replace('Z', 'م').replace('N', 'ن').replace('H',
                                                                                                          'ه').replace(
                'U', 'و').replace('V', 'ى')
            so_line_keys = ['shipment_type', 'car_make', 'car_model', 'plate_no', 'plate_type', 'chassis', 'year',
                            'car_color', 'palte_one', 'palte_second', 'palte_third', 'non_saudi_plate_no']
            line_vals = {}
            for lkey in so_line_keys:
                value = payload.get(lkey, False)
                line_vals.update({
                    lkey: value and value.isdigit() and int(value) or value
                })
            line_vals['plate_registration'] = 'non-saudi'
            is_all_digits = all(
                [p.isdigit() for p in list(str(line_vals.get('non_saudi_plate_no', '')).replace(' ', ''))])
            if line_vals.get('plate_type') in [2, 3, 4, 5, 6, 7] and line_vals.get('non_saudi_plate_no',
                                                                                   False) and not is_all_digits:
                line_vals['plate_registration'] = 'saudi'
                full_plate = line_vals['non_saudi_plate_no'].replace(' ', '').replace('A', 'أ').replace('B',
                                                                                                        'ب').replace(
                    'J', 'ح').replace('D', 'د').replace('R', 'ر').replace('S', 'س').replace('X', 'ص').replace('T',
                                                                                                              'ط').replace(
                    'E', 'ع').replace('G', 'ق').replace('K', 'ك').replace('L', 'ل').replace('Z', 'م').replace('N',
                                                                                                              'ن').replace(
                    'H', 'ه').replace('U', 'و').replace('V', 'ى')
                plate_list = list(full_plate)
                line_vals['palte_one'] = payload.get('palte_one')
                line_vals['palte_second'] = payload.get('palte_second')
                line_vals['palte_third'] = payload.get('palte_third')
                line_vals['plate_no'] = payload.get('plate_no')
            elif line_vals.get('plate_type') in [8, 9, 10]:
                line_vals['plate_registration'] = 'non-saudi'
                line_vals['non_saudi_plate_no'] = line_vals.get('non_saudi_plate_no', False) or line_vals.get(
                    'plate_no',
                    False)
                line_vals['plate_no'] = False
            else:
                line_vals['plate_registration'] = 'new_vehicle'
                line_vals['non_saudi_plate_no'] = line_vals.get('non_saudi_plate_no', False) or line_vals.get(
                    'plate_no',
                    False)
                line_vals['plate_no'] = False
            line_vals['bsg_cargo_sale_id'] = res.id
            line_vals['service_type'] = payload.get('service_type', 1)
            bsg_config = request.env['bsg_car_config'].sudo().search([('car_maker', '=', line_vals['car_make'])])
            line_vals['car_make'] = bsg_config.id
            line_vals['is_from_app'] = True
            if not (res.loc_from.is_international or res.loc_to.is_international):
                line_vals['tax_ids'] = [(6, 0, request.env.user.company_id.tax_ids.ids)]
            without_calculate_pric = False
            if payload.get('price', False):
                line_vals['unit_charge'] = float(payload.get('price', 0))
                if line_vals['unit_charge'] > 0:
                    without_calculate_pric = True
            so_line = request.env['bsg_vehicle_cargo_sale_line'].sudo().with_context(
                {'without_calculate_pric': without_calculate_pric}).create(line_vals)
            if not payload.get('price', False):
                so_line._onchange_shipment_type()
            if not is_international and price_list:
                # line_vals.update({'customer_price_list':  price_list and price_list.id or 1, 'discount':15})
                so_line.write({'customer_price_list': price_list and price_list.id or 1,
                               'discount': price_list and price_list.item_ids and price_list.item_ids[
                                   0].percent_price or 0})
            if not payload.get('price', False):
                so_line._onchange_shipment_type()
            arr_name = 'Regular'
            if so_line.shipment_type.is_satha:
                arr_name = 'Satha'
            other_service_lines = []
            sms_sent = False
            if so_line.shipment_type.is_satha:
                sms_sent = True
                if loc_from.loc_branch_id.contact_numbers:
                    try:
                        message = "تم انشاء اتفاقيه سطحه (استلام من العميل) رقم: %s من %s الى %s جوال المستلم %s" % (
                            so_line.sale_line_rec_name, loc_from.route_waypoint_name, loc_to.route_waypoint_name,
                            so_line.receiver_mob_no)
                        self.send_sms(loc_from.loc_branch_id.contact_numbers, message)
                    except Exception as e:
                        print(e)
            if payload.get('is_home_pickup', 'false').lower() == 'true':
                home_pickup_product_id = request.env['product.product'].sudo().search(
                    [('is_home_pickup', '=', True), ('attribute_value_ids.name', '=', arr_name)], limit=1)
                if home_pickup_product_id:
                    other_service_lines.append({
                        'cargo_sale_line_id': so_line.id,
                        'product_id': home_pickup_product_id.id,
                        'cost': home_pickup_product_id.lst_price,
                        'qty': 1,
                        'home_location': payload.get('home_location', False),
                        'pickup_location': payload.get('pickup_location', False),
                        'tax_ids': [(6, 0, home_pickup_product_id.taxes_id.ids)] or False,
                        'cargo_sale_id': res.id
                    })

                if not sms_sent and loc_from.loc_branch_id.contact_numbers:
                    try:
                        message = "تم انشاء اتفاقيه سطحه (استلام من العميل) رقم: %s من %s الى %s جوال المستلم %s" % (
                            so_line.sale_line_rec_name, loc_from.route_waypoint_name, loc_to.route_waypoint_name,
                            so_line.receiver_mob_no)
                        self.send_sms(loc_from.loc_branch_id.contact_numbers, message)
                    except Exception as e:
                        print(e)
            if payload.get('is_home_delivery', 'false').lower() == 'true':
                home_delivery_product_id = request.env['product.product'].sudo().search(
                    [('is_home_delivery', '=', True), ('attribute_value_ids.name', '=', arr_name)], limit=1)
                if home_delivery_product_id:
                    other_service_lines.append({
                        'cargo_sale_line_id': so_line.id,
                        'product_id': home_delivery_product_id.id,
                        'cost': home_delivery_product_id.lst_price,
                        'qty': 1,
                        'home_location': payload.get('home_location', False),
                        'pickup_location': payload.get('pickup_location', False),
                        'tax_ids': [(6, 0, home_delivery_product_id.taxes_id.ids)] or False,
                        'cargo_sale_id': res.id
                    })

                    if not sms_sent and loc_to.loc_branch_id.contact_numbers:
                        try:
                            message = "تم انشاء اتفاقيه سطحه (توصيل للمنزل) رقم: %s من %s الى %s جوال المستلم %s" % (
                                so_line.sale_line_rec_name, loc_from.route_waypoint_name, loc_to.route_waypoint_name,
                                so_line.receiver_mob_no)
                            self.send_sms(loc_to.loc_branch_id.contact_numbers, message)
                        except Exception as e:
                            print(e)
            if int(payload.get('small_boxes', 0)) > 0:
                small_box_product_id = request.env['product.product'].sudo().search([('is_small_box', '=', True)],
                                                                                    limit=1)
                if small_box_product_id:
                    other_service_lines.append({
                        'cargo_sale_line_id': so_line.id,
                        'product_id': small_box_product_id.id,
                        'cost': small_box_product_id.lst_price * int(payload['small_boxes']),
                        'qty': int(payload['small_boxes']),
                        'home_location': payload.get('home_location', False),
                        'pickup_location': payload.get('pickup_location', False),
                        'tax_ids': [(6, 0, small_box_product_id.taxes_id.ids)] or False,
                        'cargo_sale_id': res.id
                    })

            if int(payload.get('medium_boxes', 0)) > 0:
                medium_box_product_id = request.env['product.product'].sudo().search([('is_medium_box', '=', True)],
                                                                                     limit=1)
                if medium_box_product_id:
                    other_service_lines.append({
                        'cargo_sale_line_id': so_line.id,
                        'product_id': medium_box_product_id.id,
                        'cost': medium_box_product_id.lst_price * int(payload['medium_boxes']),
                        'qty': int(payload['medium_boxes']),
                        'home_location': payload.get('home_location', False),
                        'pickup_location': payload.get('pickup_location', False),
                        'tax_ids': [(6, 0, medium_box_product_id.taxes_id.ids)] or False,
                        'cargo_sale_id': res.id
                    })

            if int(payload.get('large_boxes', 0)) > 0:
                large_box_product_id = request.env['product.product'].sudo().search([('is_large_box', '=', True)],
                                                                                    limit=1)
                if large_box_product_id:
                    other_service_lines.append({
                        'cargo_sale_line_id': so_line.id,
                        'product_id': large_box_product_id.id,
                        'cost': large_box_product_id.lst_price * int(payload['large_boxes']),
                        'qty': int(payload['large_boxes']),
                        'home_location': payload.get('home_location', False),
                        'pickup_location': payload.get('pickup_location', False),
                        'tax_ids': [(6, 0, large_box_product_id.taxes_id.ids)] or False,
                        'cargo_sale_id': res.id
                    })
            online_amount = float(payload.get('app_paid_amount', 0))
            fort_id = payload.get('app_fortid', False)
            if other_service_lines:
                request.env['other_service_items'].sudo().create(other_service_lines)
            if payload.get('coupon', False):
                res.with_context({'do_not_raise_exception': True}).action_get_qitaf_discount()
            if (payload.get('app_payment_method', False) == 'credit' and online_amount > 0 and fort_id) or (
                    payload.get('wallet_transcation_ref', False) and wallet_amount > 0) or payload.get(
                'tamara_reference_id', False):
                # res.confirm_btn()
                res.state = 'draft'
                so_line.state = 'draft'
            else:
                # res.with_context({'do_not_create_invoice': True}).confirm_btn()
                res.state = 'draft'
                so_line.state = 'draft'
            so_line.recieved_from_customer_date = False
            res.recieved_from_customer_date = False

            data = [{
                'order_id': so_line.id,
                'order_ref': so_line.sale_line_rec_name,
                'track_tiny_url': so_line.track_tiny_url
            }]
            if data:
                if payload.get('app_payment_method',
                               False) == 'credit' and online_amount > 0 and fort_id or payload.get(
                        'tamara_reference_id', False):
                    provider = payload.get('provider', 'payfort')
                    acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', provider)], limit=1)
                    sale_rec = so_line.bsg_cargo_sale_id
                    context = {
                        'active_id': sale_rec.id,
                        'show_invoice_amount': True,
                        'pass_sale_order_id': sale_rec.id,
                        'is_patrtially_payment': True,
                    }
                    inv = request.env['account.move'].sudo().search([('cargo_sale_id', '=', res.id)], limit=1)
                    if not inv:
                        trans_id = request.env['payment.transaction'].sudo().create({
                            'app_fortid': fort_id,
                            'tamara_reference_id': payload.get('tamara_reference_id', False),
                            'cargo_sale_ids': [(6, 0, [res.id])],
                            'amount': online_amount,
                            'partner_id': sale_rec.customer.id,
                            'date': fields.Date.today(),
                            'acquirer_id': acquirer_id.id,
                            'currency_id': 153,
                            'state': 'done',
                            'payment_id': payment_id.id if payment_id else False,
                            'is_processed': True,
                            'acquirer_reference': payload.get('authorization_code', False)
                        })
                        data = [{
                            'order_id': so_line.id,
                            'order_ref': so_line.sale_line_rec_name,
                            'invoice_id': inv,
                            'transaction_id': trans_id
                        }]
                        return valid_response(data)
                    payment_method_id_log = request.env['account.payment.method'].sudo().search(
                        ['&', ('payment_type', '=', 'inbound'), ('name', '=', 'Electronic')], limit=1).id or 3
                    if online_amount > 0:
                        payment_id = request.env['account.payment'].sudo().with_context(context).create({
                            'payment_type': 'inbound',
                            'partner_id': sale_rec.customer.id,
                            'partner_type': 'customer',
                            'journal_id': acquirer_id.journal_id.id,
                            'amount': online_amount,
                            'communication': sale_rec.name,
                            'show_invoice_amount': True,
                            'invoice_ids': [(4, inv[0].id, None)],
                            'payment_method_id': request.env['account.payment.method'].sudo().search(
                                ['&', ('payment_type', '=', 'inbound'), ('name', '=', 'Electronic')], limit=1).id or 3,
                            'cargo_sale_line_id': so_line.id,
                            'transaction_reference': sale_rec.transaction_reference,
                            'app_fortid': fort_id,
                            'tamara_reference_id': payload.get('tamara_reference_id', False),
                            'provider_tag': payload.get('provider_tag', False),
                        })
                        _logger.warning("............Create order payment id is ........ %s" % payment_id)
                        payment_id.branach_ids = False
                        payment_id.action_validate_invoice_payment()
                        trans_id = request.env['payment.transaction'].sudo().create({
                            'app_fortid': fort_id,
                            'tamara_reference_id': payload.get('tamara_reference_id', False),
                            'cargo_sale_ids': [(6, 0, [res.id])],
                            'amount': online_amount,
                            'partner_id': sale_rec.customer.id,
                            'date': fields.Date.today(),
                            'acquirer_id': acquirer_id.id,
                            'currency_id': 153,
                            'state': 'done',
                            'payment_id': payment_id.id,
                            'is_processed': True,
                            'acquirer_reference': payload.get('authorization_code', False)
                        })
                        if payload.get('tamara_reference_id', False):
                            trans_id.write({'is_tamara': True, 'tamara_transaction_ids': [(6, 0, [res.id])]})
                        payment_id.payment_transaction_id = trans_id.id
                        cargo_line_pay = request.env['account.cargo.line.payment'].sudo()
                        for so_line in sale_rec.mapped('order_line_ids'):
                            if not so_line.is_paid and payment_id.residual_amount > 0:
                                for inv_line in inv.mapped('invoice_line_ids').filtered(
                                        lambda s: s.cargo_sale_line_id.id == so_line.id):
                                    cargo_line_pay.with_context({'without_check_amount': True}).sudo().create({
                                        'cargo_sale_line_id': inv_line.cargo_sale_line_id.id,
                                        'account_invoice_line_id': inv_line.id,
                                        'amount': inv_line.price_total,
                                        'residual': inv_line.price_total - inv_line.paid_amount,
                                        'account_payment_id': payment_id.id,
                                    })

            if (payload.get('wallet_transcation_ref', False) and wallet_amount > 0):
                provider = payload.get('provider', 'payfort')
                acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', provider)], limit=1)
                sale_rec = so_line.bsg_cargo_sale_id
                context = {
                    'active_id': sale_rec.id,
                    'show_invoice_amount': True,
                    'pass_sale_order_id': sale_rec.id,
                    'is_patrtially_payment': True,
                }
                inv = request.env['account.move'].sudo().search([('cargo_sale_id', '=', res.id)], limit=1)
                if not inv:
                    return valid_response(data)

                payment_id = request.env['account.payment'].sudo().with_context(context).create({
                    'payment_type': 'inbound',
                    'partner_id': sale_rec.customer.id,
                    'partner_type': 'customer',
                    'journal_id': acquirer_id.journal_id.id,
                    'amount': wallet_amount,
                    'communication': sale_rec.name,
                    'show_invoice_amount': True,
                    'invoice_ids': [(4, inv[0].id, None)],
                    'payment_method_id': request.env['account.payment.method'].sudo().search(
                        ['&', ('payment_type', '=', 'inbound'), ('name', '=', 'Electronic')], limit=1).id or 3,
                    'cargo_sale_line_id': so_line.id,
                    'transaction_reference': sale_rec.transaction_reference,
                    'app_fortid': 'Walt' + payload.get('wallet_transcation_ref', ''),
                    'tamara_reference_id': payload.get('tamara_reference_id', False),
                    'provider_tag': payload.get('provider_tag', False),
                })
                payment_id.branach_ids = False
                payment_id.action_validate_invoice_payment()
                cargo_line_pay = request.env['account.cargo.line.payment'].sudo()
                for so_line in sale_rec.mapped('order_line_ids'):
                    if not so_line.is_paid and payment_id.residual_amount > 0:
                        for inv_line in inv.mapped('invoice_line_ids').filtered(
                                lambda s: s.cargo_sale_line_id.id == so_line.id):
                            cargo_line_pay.with_context({'without_check_amount': True}).sudo().create({
                                'cargo_sale_line_id': inv_line.cargo_sale_line_id.id,
                                'account_invoice_line_id': inv_line.id,
                                'amount': inv_line.price_total,
                                'residual': inv_line.price_total - inv_line.paid_amount,
                                'account_payment_id': payment_id.id,
                            })
            if not payment_id and online_amount > 0:
                provider = payload.get('provider', 'payfort')
                acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', provider)], limit=1)
                sale_rec = so_line.bsg_cargo_sale_id
                context = {
                    'active_id': sale_rec.id,
                    'show_invoice_amount': True,
                    'pass_sale_order_id': sale_rec.id,
                    'is_patrtially_payment': True,
                }
                payment_id = request.env['account.payment'].sudo().with_context(context).create({
                    'payment_type': 'inbound',
                    'partner_id': sale_rec.customer.id,
                    'partner_type': 'customer',
                    'journal_id': acquirer_id.journal_id.id,
                    'amount': online_amount,
                    'communication': sale_rec.name,
                    'show_invoice_amount': True,
                    'invoice_ids': [(4, inv[0].id, None)],
                    'payment_method_id': request.env['account.payment.method'].sudo().search(
                        ['&', ('payment_type', '=', 'inbound'), ('name', '=', 'Electronic')], limit=1).id or 3,
                    'cargo_sale_line_id': so_line.id,
                    'transaction_reference': sale_rec.transaction_reference,
                    'app_fortid': fort_id,
                    'tamara_reference_id': payload.get('tamara_reference_id', False),
                    'provider_tag': payload.get('provider_tag', False),
                })
                payment_id.branach_ids = False
                # payment_id.action_validate_invoice_payment()
                trans_id = request.env['payment.transaction'].sudo().create({
                    'app_fortid': fort_id,
                    'tamara_reference_id': payload.get('tamara_reference_id', False),
                    'cargo_sale_ids': [(6, 0, [res.id])],
                    'amount': online_amount,
                    'partner_id': sale_rec.customer.id,
                    'date': fields.Date.today(),
                    'acquirer_id': acquirer_id.id,
                    'currency_id': 153,
                    'state': 'done',
                    'payment_id': payment_id.id,
                    'is_processed': True,
                    'acquirer_reference': payload.get('authorization_code', False)
                })
                if payload.get('tamara_reference_id', False):
                    trans_id.write({'is_tamara': True, 'tamara_transaction_ids': [(6, 0, [res.id])]})
                payment_id.payment_transaction_id = trans_id.id
                cargo_line_pay = request.env['account.cargo.line.payment'].sudo()
                for so_line in sale_rec.mapped('order_line_ids'):
                    if not so_line.is_paid and payment_id.residual_amount > 0:
                        for inv_line in inv.mapped('invoice_line_ids').filtered(
                                lambda s: s.cargo_sale_line_id.id == so_line.id):
                            cargo_line_pay.with_context({'without_check_amount': True}).sudo().create({
                                'cargo_sale_line_id': inv_line.cargo_sale_line_id.id,
                                'account_invoice_line_id': inv_line.id,
                                'amount': inv_line.price_total,
                                'residual': inv_line.price_total - inv_line.paid_amount,
                                'account_payment_id': payment_id.id,
                            })
            if so_line.state == 'draft':
                res.state = 'registered'
            return valid_response(data)
        except Exception as e:
            se = _http.serialize_exception(e)
            request.env['api.log'].sudo().create({
                'endpoint': '/api/create_order',
                'request_payload': str(payload),
                'exception_message': se,
            })
            return invalid_response("Error: ", se)

    @http.route("/api/getCarsToShip", type="http", auth="none", methods=["GET"], csrf=False)
    def get_cars_to_ship(self, **payload):
        try:
            national_id = payload.get('national_id', False)
            data = []
            if national_id:
                #('sale_order_state','in',['done','pod','registered'])
                recs = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(['|',('bsg_cargo_sale_id.sender_id_card_no', '=', national_id),
                                        ('bsg_cargo_sale_id.sender_visa_no', '=', national_id),('payment_method.payment_type', 'in', ['cash', 'pod']),
                                        ('state','in',['registered']),
                                        ('added_to_trip','=',False),
                                        ('fleet_trip_id','=',False)])
                recs  = recs.filtered(lambda r: not any(r.bsg_cargo_sale_id.other_service_line_ids.mapped('product_id.is_home_pickup')))
                for rec in recs:
                    vals = {'id': rec.id, 'sale_line_rec_name': rec.sale_line_rec_name,  'plate_no': rec.non_saudi_plate_no or rec.general_plate_no, 'shipment_type': rec.shipment_type.car_shipment_name}
                    if rec.loc_from:
                        vals['loc_from'] = { 'id': rec.loc_from.id, 'name': rec.loc_from.route_waypoint_name, 'name_en':rec.loc_from.waypoint_english_name, 'has_satha_service': rec.loc_from.has_satha_service, 'gps_coordinates':{
                            'longitude': rec.loc_from.loc_branch_id.branch_long ,
                            'latitude': rec.loc_from.loc_branch_id.branch_lat
                        }}
                    if rec.loc_to:
                        vals['loc_to'] = { 'id': rec.loc_to.id, 'name': rec.loc_to.route_waypoint_name,'name_en':rec.loc_to.waypoint_english_name,'has_satha_service': rec.loc_to.has_satha_service, 'gps_coordinates':{
                            'longitude': rec.loc_to.loc_branch_id.branch_long ,
                            'latitude': rec.loc_to.loc_branch_id.branch_lat
                        }}
                    vals['state'] = rec.state
                    vals['order_date'] =  rec.bsg_cargo_sale_id.order_date and rec.bsg_cargo_sale_id.order_date.strftime('%d-%B-%Y') or ''
                    vals['receiver_id_card_no'] = rec.bsg_cargo_sale_id.receiver_id_card_no or rec.bsg_cargo_sale_id.receiver_visa_no or ''
                    vals['receiver_id_type'] = rec.bsg_cargo_sale_id.receiver_id_type or ''
                    vals['customer_nationality'] = rec.bsg_cargo_sale_id.receiver_nationality and rec.bsg_cargo_sale_id.receiver_nationality.id or ''



                    data.append(vals) 
            return valid_response(data)
            return invalid_response(
                "invalid object model", "No records found"
            )
        except AccessError as e:


            return invalid_response("Error: ", str(e))

    @http.route("/api/getOrderLines", type="http", auth="none", methods=["GET"], csrf=False)
    def get_order_lines(self, **payload):
        try:
            order_ref = payload.get('order_ref', False)
            receiver_mob_no = payload.get('receiver_mob_no', False)
            data = []
            recs = False
            if order_ref:
                recs = request.env['bsg_vehicle_cargo_sale_line'].sudo().search([('sale_line_rec_name', '=', order_ref),('payment_method.payment_type', 'in', ['cash', 'pod']), ('state', 'not in', ['done', 'cancel','released'])], limit=1)
            if receiver_mob_no:
                recs = request.env['bsg_vehicle_cargo_sale_line'].sudo().search([
                    ('bsg_cargo_sale_id.receiver_mob_no','=',receiver_mob_no),('payment_method.payment_type', 'in', ['cash', 'pod']),
                    ('state', 'not in', ['done', 'cancel','released'])
                ])
            if recs:
                for rec in recs:
                    data.append({
                        'order_ref': rec.sale_line_rec_name,
                        'customer': {
                            'id': rec.customer_id.id,
                            'name': rec.customer_id.name,
                        },
                        'plate': rec.general_plate_no
                    })  
            return valid_response(data)
        except AccessError as e:

            return invalid_response("Error: ", str(e))


    @http.route("/api/ExitPermition", type="http", auth="none", methods=["GET"], csrf=False)
    def get_order_lines_exit_permition(self, **payload):
        try:
            order_ref = payload.get('order_ref', False)
            exit_by = payload.get('exit_by', False)
            receiver_mob_no = payload.get('receiver_mob_no', False)
            data = []
            recs = False
            if order_ref:
                recs = request.env['bsg_vehicle_cargo_sale_line'].sudo().search([('sale_line_rec_name', '=', order_ref), ('state', 'not in', ['cancel'])], limit=1)
            if receiver_mob_no:
                recs = request.env['bsg_vehicle_cargo_sale_line'].sudo().search([
                    ('bsg_cargo_sale_id.receiver_mob_no','=',receiver_mob_no), ('state', 'not in', ['cancel'])
                ])

            if recs and exit_by:
                if recs.delivery_report_history_ids:
                    recs.delivery_report_history_ids.update({"exit_by": exit_by,"exit_date": datetime.now()})
                else:
                    recs.delivery_report_history_ids.create({
                      "exit_by": exit_by,
                      "exit_date": datetime.now(),
                      "dr_user_id": request.env.user.id,
                      "dr_print_date": datetime.now(),
                      "number": 1,
                      "act_receiver_name": request.env.user.partner_id.name,
                      "cargo_so_line_id": recs.id
                      })
                data.append({
                        'order_ref': recs.sale_line_rec_name,
                        'customer': {
                            'id': recs.customer_id.id,
                            'name': recs.customer_id.name,
                        },
                        'delivery_report_history_ids': {
                              "dr_user_id": recs.delivery_report_history_ids.dr_user_id.id,
                              "dr_print_date": recs.delivery_report_history_ids.dr_print_date,
                              "number": recs.delivery_report_history_ids.number,
                              "act_receiver_name": recs.delivery_report_history_ids.act_receiver_name,
                        },
                    })
            return valid_response(data)
        except Exception as e:
            return invalid_response("Error: ", str(e))



    @http.route("/api/getOrderLinesAll", type="http", auth="none", methods=["GET"], csrf=False)
    def get_order_lines_all(self, **payload):
        try:
            order_ref = payload.get('order_ref', False)
            receiver_mob_no = payload.get('receiver_mob_no', False)
            data = []
            recs = False
            if order_ref:
                recs = request.env['bsg_vehicle_cargo_sale_line'].sudo().search([('sale_line_rec_name', '=', order_ref), ('state', 'not in', ['cancel'])], limit=1)
            if receiver_mob_no:
                recs = request.env['bsg_vehicle_cargo_sale_line'].sudo().search([
                    ('bsg_cargo_sale_id.receiver_mob_no','=',receiver_mob_no), ('state', 'not in', ['cancel'])
                ])
            if recs:
                data.append({
                    'order_ref': recs.sale_line_rec_name,
                    'customer': {
                        'id': recs.customer_id.id,
                        'name': recs.customer_id.name,
                    },
                    'plate': recs.general_plate_no,
                    'car_make': recs.car_make.car_maker.car_make_name,
                    'car_model': recs.car_model.car_model_name,
                    'state': recs.state,
                })
                if recs.delivery_report_history_ids:
                    data[0].update({
                        'delivery_report_history_ids': {
                              "dr_user_id": recs.delivery_report_history_ids.dr_user_id.name,
                              "dr_print_date": recs.delivery_report_history_ids.dr_print_date,
                              "number": recs.delivery_report_history_ids.number,
                              "act_receiver_name": recs.delivery_report_history_ids.act_receiver_name,
                        },
                    })
            return valid_response(data)
        except AccessError as e:
            return invalid_response("Error: ", str(e))



    @http.route("/api/getCarsAll", type="http", auth="none", methods=["GET"], csrf=False)
    def get_cars_to_all(self, **payload):
        try:
            national_id = payload.get('national_id', False)
            data = []
            if national_id:
                recs = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(['|',('bsg_cargo_sale_id.sender_id_card_no', '=', national_id),
                                        ('bsg_cargo_sale_id.sender_visa_no', '=', national_id),('payment_method.payment_type', 'in', ['cash', 'pod'])])
                for rec in recs:
                    vals = {'id': rec.id, 'sale_line_rec_name': rec.sale_line_rec_name, 'plate_no':rec.non_saudi_plate_no or rec.general_plate_no, 'shipment_type': rec.shipment_type.car_shipment_name}
                    if rec.loc_from:
                        vals['loc_from'] = { 'id': rec.loc_from.id, 'name': rec.loc_from.route_waypoint_name,'name_en':rec.loc_from.waypoint_english_name, 'has_satha_service': rec.loc_from.has_satha_service, 'gps_coordinates':{
                            'longitude': rec.loc_from.loc_branch_id.branch_long ,
                            'latitude': rec.loc_from.loc_branch_id.branch_lat
                        }}
                    if rec.loc_to:
                        vals['loc_to'] = { 'id': rec.loc_to.id, 'name': rec.loc_to.route_waypoint_name, 'name_en':rec.loc_to.waypoint_english_name, 'has_satha_service': rec.loc_to.has_satha_service, 'gps_coordinates':{
                            'longitude': rec.loc_to.loc_branch_id.branch_long ,
                            'latitude': rec.loc_to.loc_branch_id.branch_lat
                        }}
                    vals['state'] = rec.state
                    vals['is_paid'] = rec.is_paid
                    vals['order_date'] =  rec.bsg_cargo_sale_id.order_date and rec.bsg_cargo_sale_id.order_date.strftime('%d-%B-%Y') or ''
                    data.append(vals) 
            return valid_response(data)
            return invalid_response(
                "invalid object model", "No records found"
            )
        except AccessError as e:

            return invalid_response("Error: ", str(e))


    @http.route("/api/getCarsDOB", type="http", auth="none", methods=["GET"], csrf=False)
    def get_cars_dob(self, **payload):
        try:
            national_id = payload.get('national_id', False)
            receiver_mob_no = payload.get('receiver_mob_no', False)
            data = []            
            if national_id and not receiver_mob_no:
                recs = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(['|',('bsg_cargo_sale_id.sender_id_card_no', '=', national_id),
                                        ('bsg_cargo_sale_id.sender_visa_no', '=', national_id),('payment_method.payment_type', 'in', ['cash', 'pod']),
                                        ('state', 'not in', ['draft', 'cancel','done'])])
            elif receiver_mob_no and not national_id:
                recs = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(['|',('bsg_cargo_sale_id.sender_id_card_no', '=', national_id),
                                        ('bsg_cargo_sale_id.receiver_mob_no','=',receiver_mob_no),('payment_method.payment_type', 'in', ['cash', 'pod']),
                                        ('state', 'not in', ['draft', 'cancel','done'])])
            elif receiver_mob_no and national_id:
                recs = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(['|',('bsg_cargo_sale_id.sender_id_card_no', '=', national_id),
                                        '|', ('bsg_cargo_sale_id.sender_visa_no', '=', national_id),('bsg_cargo_sale_id.receiver_mob_no','=',receiver_mob_no),
                                        ('payment_method.payment_type', 'in', ['cash', 'pod']),
                                        ('state', 'not in', ['draft', 'cancel','done'])])
            else:
                recs = False

            if recs:
                recs  = recs.filtered(lambda r: not any(r.bsg_cargo_sale_id.other_service_line_ids.mapped('product_id.is_home_delivery')))
                for rec in recs:
                    vals = {'id': rec.id, 'sale_line_rec_name': rec.sale_line_rec_name,  'plate_no': rec.non_saudi_plate_no or rec.general_plate_no, 'shipment_type': rec.shipment_type.car_shipment_name}
                    if rec.loc_from:
                        vals['loc_from'] = { 'id': rec.loc_from.id, 'name': rec.loc_from.route_waypoint_name,'name_en':rec.loc_from.waypoint_english_name,'has_satha_service': rec.loc_from.has_satha_service, 'gps_coordinates':{
                            'longitude': rec.loc_from.loc_branch_id.branch_long ,
                            'latitude': rec.loc_from.loc_branch_id.branch_lat
                        }}
                    if rec.loc_to:
                        vals['loc_to'] = { 'id': rec.loc_to.id, 'name': rec.loc_to.route_waypoint_name, 'name_en':rec.loc_to.waypoint_english_name, 'has_satha_service': rec.loc_to.has_satha_service, 'gps_coordinates':{
                            'longitude': rec.loc_to.loc_branch_id.branch_long ,
                            'latitude': rec.loc_to.loc_branch_id.branch_lat
                        }}
                    vals['state'] = rec.state
                    vals['order_date'] =  rec.bsg_cargo_sale_id.order_date and rec.bsg_cargo_sale_id.order_date.strftime('%d-%B-%Y') or ''
                    vals['order_date'] =  rec.bsg_cargo_sale_id.order_date and rec.bsg_cargo_sale_id.order_date.strftime('%d-%B-%Y') or ''
                    vals['receiver_id_card_no'] = rec.bsg_cargo_sale_id.receiver_id_card_no or rec.bsg_cargo_sale_id.receiver_visa_no or ''
                    vals['receiver_id_type'] = rec.bsg_cargo_sale_id.receiver_id_type or ''
                    vals['customer_nationality'] = rec.bsg_cargo_sale_id.receiver_nationality and rec.bsg_cargo_sale_id.receiver_nationality.id or ''
                    data.append(vals)            
            return valid_response(data)
        except AccessError as e:
            return invalid_response("Error: ", str(e))

    def _get_car_size(self, car_make, car_model):
        car_size = False
        car_classfication = False
        for car_line in car_make.car_line_ids:
            if car_line.car_model.id == car_model:
                car_size = car_line.car_size.id
                car_classfication = car_line.car_classfication.id
                break
        return car_size, car_classfication

    @validate_token
    @http.route("/api/getPrice", type="http", auth="none", methods=["GET"], csrf=False)
    def get_price(self, **payload):
        data = []
        try:

            service_product_id = int(payload.get('service_type', 1))
            domain = [('service_type', '=', service_product_id)]
            car_size = False
            # for key, val in payload.items():
            #     if key in ['shipment_date', 'service_type', 'car_model', 'car_make', 'car_size']:
            #         continue
            #     if val and val.isdigit():
            #         domain.append((key,'=', int(val)))
            #     else:
            #         domain.append((key,'=', val))
            # [*payload] + 
            fieldss = ['customer_type', 'service_type', 'car_size', 'car_classfication', 'waypoint_from', 'waypoint_to', 'price', 'addtional_price']
            # if payload.get('car_make', False) and payload.get('car_model', False):
            car_size = False
            shipment_type = request.env['bsg.car.shipment.type'].sudo().browse(int(payload['shipment_type']))
            if not shipment_type.is_normal:
                car_size = shipment_type.car_size.id
                domain.append(('car_size','=', car_size))
            else:
                bsg_config = request.env['bsg_car_config'].sudo().search([('car_maker', '=', int(payload.get('car_make')))])
                car_size, car_class = self._get_car_size(bsg_config, int(payload.get('car_model')))
                if car_size:
                    domain.append(('car_size','=', car_size))
                if car_class:
                    domain.append(('car_classfication','=', car_class))
            # if not car_size:
            #     car_size = payload.get('car_size', False)
            domain+=[
                ('price_config_id.waypoint_from', '=', int( payload['waypoint_from'])),
                ('price_config_id.waypoint_to', '=',  int(payload['waypoint_to'])),
                ('price_config_id.customer_type', '=', payload['customer_type'])
            ]
            data = request.env['bsg_price_line'].sudo().search_read(
                        domain=domain, fields=fieldss
                    )
                    
            date_res= request.env['bsg_vehicle_cargo_sale_line'].get_expected_delivery_date(payload['waypoint_from'] ,payload['waypoint_to'], car_size, payload['shipment_date'], shipment_type.id)
            
            if data:
                data = [data[0]]
                taxes = 0
                waypoint_boj = request.env['bsg_route_waypoints']
                waypoint_from = waypoint_boj.sudo().browse(int( payload['waypoint_from']))
                waypoint_to = waypoint_boj.sudo().browse(int( payload['waypoint_to']))
                if not waypoint_from.is_international and not waypoint_to.is_international:
                    taxes = sum(request.env['product.template'].sudo().browse(service_product_id).mapped('taxes_id.amount'))
                    
                if waypoint_from.is_international and waypoint_from.loc_branch_id.currency_id != request.env.user.company_id.currency_id:
                    request.env.user.company_id.currency_id._convert(
                    data[0]['price'],  waypoint_from.loc_branch_id.currency_id, request.env.user.company_id, fields.Datetime.now())
                elif waypoint_to.is_international and  waypoint_to.loc_branch_id.currency_id != request.env.user.company_id.currency_id:
                    request.env.user.company_id.currency_id._convert(
                    data[0]['price'],  waypoint_to.loc_branch_id.currency_id, request.env.user.company_id, fields.Datetime.now())

                data[0].update({
                    'taxes': taxes
                })
                data[0].update(
                    date_res
                )
                data[0]['waypoint_from'] = waypoint_from.sudo().read(['route_waypoint_name', 'has_satha_service'])[0]
                data[0]['waypoint_to'] = waypoint_to.sudo().read(['route_waypoint_name', 'has_satha_service'])[0]
                arr_name = 'Regular'
                if shipment_type.is_satha:
                    arr_name = 'Satha'
                delivery_pickup_product_ids = request.env['product.product'].sudo().search([
                    ('attribute_value_ids.name', '=', arr_name),
                    '|',('is_home_pickup', '=', True),
                    ('is_home_delivery', '=', True)], limit=2)
                product_ids = request.env['product.product'].sudo().search([
                    '|',('is_small_box', '=', True),
                    '|',('is_medium_box', '=', True), ('is_large_box', '=', True)], limit=3)
                product_ids += delivery_pickup_product_ids
                other_services = []
                for product in product_ids:
                    other_services.append({
                        'name': product.name,
                        'price': product.lst_price,
                        'taxes': sum(product.taxes_id.mapped('amount')),
                    })
                
                data[0].update(
                    {
                        'other_services': other_services
                    }
                    )
            # if data:
            return valid_response(data)
        except AccessError as e:
            _logger.error(e)
            return  valid_response(data)

    @validate_token
    @http.route("/api/getPriceAll", type="http", auth="none", methods=["GET"], csrf=False)
    def get_price_all(self, **payload):
        all_data = []
        try:
            service_product_id = int(payload.get('service_type', 1))
            domain = [('service_type', '=', service_product_id)]
            car_size = False
            # for key, val in payload.items():
            #     if key in ['shipment_date', 'service_type', 'car_model', 'car_make', 'car_size']:
            #         continue
            #     if val and val.isdigit():
            #         domain.append((key,'=', int(val)))
            #     else:
            #         domain.append((key,'=', val))
            # [*payload] +
            fieldss = ['customer_type', 'service_type', 'car_size', 'car_classfication', 'waypoint_from', 'waypoint_to',
                       'price', 'addtional_price']
            # if payload.get('car_make', False) and payload.get('car_model', False):
            car_size = False
            shipment_types = request.env['bsg.car.shipment.type'].sudo().search([('is_public', '=', True)])
            for shipment_type in shipment_types:
                _logger.error(
                    "/getPriceAll shipment type........................+  " + str(shipment_type))
                data = []
                shipment_type_features = []
                if not shipment_type.is_normal:
                    car_size = shipment_type.car_size.id
                    domain.append(('car_size', '=', car_size))
                else:
                    bsg_config = request.env['bsg_car_config'].sudo().search(
                        [('car_maker', '=', int(payload.get('car_make')))])
                    car_size, car_class = self._get_car_size(bsg_config, int(payload.get('car_model')))
                    if car_size:
                        domain.append(('car_size', '=', car_size))
                    if car_class:
                        domain.append(('car_classfication', '=', car_class))
                # if not car_size:
                #     car_size = payload.get('car_size', False)

                domain += [
                    ('price_config_id.waypoint_from', '=', int(payload['waypoint_from'])),
                    ('price_config_id.waypoint_to', '=', int(payload['waypoint_to'])),
                    ('price_config_id.customer_type', '=', payload['customer_type'])
                ]
                data = request.env['bsg_price_line'].sudo().search_read(
                    domain=domain, fields=fieldss
                )
                _logger.error(
                    "/getPriceAll price line data........................+  " + str(data))

                exp_delivery_date_status = request.env['bsg_vehicle_cargo_sale_line'].sudo().set_exp_delivery_date_json(
                    loc_from=payload['waypoint_from'],
                    loc_to=payload['waypoint_to'],
                    shipment_type=shipment_type.id,
                    car_size=car_size,
                    shipment_date=payload['shipment_date'])
                if data:
                    data = [data[0]]
                    taxes = 0
                    waypoint_boj = request.env['bsg_route_waypoints']
                    waypoint_from = waypoint_boj.sudo().browse(int(payload['waypoint_from']))
                    waypoint_to = waypoint_boj.sudo().browse(int(payload['waypoint_to']))
                    if not waypoint_from.is_international and not waypoint_to.is_international:
                        taxes = sum(
                            request.env['product.template'].sudo().browse(service_product_id).mapped('taxes_id.amount'))

                    if waypoint_from.is_international and waypoint_from.loc_branch_id.currency_id != request.env.user.company_id.currency_id:
                        request.env.user.company_id.currency_id._convert(
                            data[0]['price'], waypoint_from.loc_branch_id.currency_id, request.env.user.company_id,
                            fields.Datetime.now())
                    elif waypoint_to.is_international and waypoint_to.loc_branch_id.currency_id != request.env.user.company_id.currency_id:
                        request.env.user.company_id.currency_id._convert(
                            data[0]['price'], waypoint_to.loc_branch_id.currency_id, request.env.user.company_id,
                            fields.Datetime.now())

                    data[0].update({
                        'taxes': taxes
                    })
                    data[0].update(
                        {'expected_delivery': exp_delivery_date_status.get('expected_delivery'),
                         'est_no_delivery_days': exp_delivery_date_status.get('est_no_delivery_days'),
                         'est_max_no_delivery_days': exp_delivery_date_status.get('est_max_no_delivery_days')
                         }
                    )
                    if shipment_type.website_description_ids:
                        for feature in shipment_type.website_description_ids:
                            shipment_type_features.append({'description':feature.name or ''})

                    data[0].update(
                        {'shipment_type_ar': shipment_type.car_shipment_name or '',
                         'shipment_type_en': shipment_type.car_shipment_name_en or '',
                         'descriptions': shipment_type_features
                         }
                    )
                    data[0]['waypoint_from'] = waypoint_from.sudo().read(['route_waypoint_name', 'has_satha_service'])[
                        0]
                    data[0]['waypoint_to'] = waypoint_to.sudo().read(['route_waypoint_name', 'has_satha_service'])[0]
                    arr_name = 'Regular'
                    if shipment_type.is_satha:
                        arr_name = 'Satha'
                    delivery_pickup_product_ids = request.env['product.product'].sudo().search([
                        ('attribute_value_ids.name', '=', arr_name),
                        '|', ('is_home_pickup', '=', True),
                        ('is_home_delivery', '=', True)], limit=2)
                    product_ids = request.env['product.product'].sudo().search([
                        '|', ('is_small_box', '=', True),
                        '|', ('is_medium_box', '=', True), ('is_large_box', '=', True)], limit=3)
                    product_ids += delivery_pickup_product_ids
                    other_services = []
                    for product in product_ids:
                        other_services.append({
                            'name': product.name,
                            'price': product.lst_price,
                            'taxes': sum(product.taxes_id.mapped('amount')),
                        })

                    data[0].update(
                        {
                            'other_services': other_services
                        }
                    )
                    all_data.append(data[0])
                    _logger.error(
                        "/getPriceAll all data........................+  " + str(all_data))
            # if data:
            return valid_response(all_data)
        except AccessError as e:
            _logger.error(e)
            return valid_response(data)

    @http.route("/api/AvayaTrackShipment", type="http", auth="none", methods=["GET"], csrf=False)
    def avaya_track_shipment(self, **payload):
        headers = request.httprequest.headers
        request_token = headers.get('access_token', False)
        if request_token != 'access_token_770b43dsdsuu55f116dsdsdsd749533b3071d8': #test toekn
            return valid_response( [{'status': 0}])
        so_line_ref = payload.get('order_ref', False)
        data = [{'status': 0}]
        if so_line_ref:
            domain = [('sale_line_rec_name', '=', so_line_ref)]
            cargo_line = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(domain,limit=1)
            if cargo_line:
                data[0]['status'] = ORDERSTATEMAPPING.get(cargo_line.state)
        return valid_response(data)

    @validate_token
    @http.route("/api/driverTrips", type="http", auth="none", methods=["GET"], csrf=False)
    def get_driver_trips(self, **payload):
        partner_id = payload.get('partner_id', False)
        data = []
        if partner_id:
            domain = [('driver_id.partner_id', '=', int(partner_id))]
            trip_ids = request.env['fleet.vehicle.trip'].sudo().search(domain)
            if len(trip_ids) > 5:
                trip_ids = trip_ids[-5:]
            if trip_ids:
                for trip_id in trip_ids:
                    if trip_id:
                        data.append(
                            {'id': trip_id.id,
                             'reference':trip_id.name or '',
                             'start_branch': trip_id.start_branch.display_name or '',
                             'schedule_start_date': trip_id.expected_start_date or '',
                             'route': trip_id.route_id.display_name or '',
                             'state': trip_id.state,
                             }
                        )
        return valid_response(data)

    @validate_token
    @http.route("/api/tripDetails", type="http", auth="none", methods=["GET"], csrf=False)
    def get_trip_details(self, **payload):
        payload_trip_id = payload.get('trip_id', False)
        data = []
        if payload_trip_id:
            domain = [('id', '=', int(payload_trip_id))]
            trip_id = request.env['fleet.vehicle.trip'].sudo().search(domain, limit=1)
            if trip_id:
                stock_pickings = []
                if trip_id.stock_picking_id:
                    for picking in trip_id.stock_picking_id:
                        if picking:
                            stock_pickings.append({
                                'reference': picking.picking_name.display_name or '',
                                'loc_from': picking.loc_from.display_name or '',
                                'loc_to': picking.loc_to.display_name or '',
                                'car_make': picking.picking_name.car_make.display_name or '',
                                'car_model': picking.picking_name.car_model.display_name or '',
                                'chassis_no': picking.picking_name.chassis_no,
                                'plate_no': "%s%s%s%s " % (
                                picking.picking_name.plate_no, picking.picking_name.palte_one,
                                picking.picking_name.palte_second,
                                picking.picking_name.palte_third) if picking.picking_name.plate_no else ''
                            })
                data.append(
                    {
                        'start_branch': trip_id.start_branch.display_name or '',
                        'schedule_start_date': trip_id.expected_start_date or '',
                        'route': trip_id.route_id.display_name or '',
                        'state': trip_id.state,
                        'trip_lines': stock_pickings
                    }
                )
        return valid_response(data)

    @validate_token
    @http.route("/api/getMyTicket", type="http", auth="none", methods=["GET"], csrf=False)
    def get_my_helpdesk_ticket(self, **payload):
        customer_mobile = payload.get('mobile_no', False)
        data = []
        _logger.error("............my ticket api in customer mobile above.......... " + str(payload))
        _logger.error("............my ticket api in customer mobile above.......... " + str(customer_mobile))
        if customer_mobile:
            _logger.error("............my ticket api in customer mobile below.......... " + str(customer_mobile))
            domain = [('customer_mobile', '=', str(customer_mobile))]
            ticket_ids = request.env['helpdesk.ticket'].sudo().search(domain, limit=5)
            _logger.error("............my ticket api in ticket_ids.......... " + str(ticket_ids))
            if ticket_ids:
                for ticket_id in ticket_ids:
                    data.append(
                        {'ticket_id': ticket_id.id,
                         'subject': ticket_id.name,
                         'status': ticket_id.stage_id.name,
                         }
                    )
        return valid_response(data)

    @validate_token
    @http.route("/api/getTicketDetails", type="http", auth="none", methods=["GET"], csrf=False)
    def get_ticket_details(self, **payload):
        ticket_id = payload.get('ticket_id', False)
        data = []
        _logger.error("............my ticket api in payload above.......... " + str(payload))
        _logger.error("............my ticket api in ticket_id above.......... " + str(ticket_id))
        if ticket_id:
            _logger.error("............my ticket api in customer mobile below.......... " + str(ticket_id))
            domain = [('id', '=', int(ticket_id))]
            ticket_ids = request.env['helpdesk.ticket'].sudo().search(domain)
            _logger.error("............my ticket api in ticket_ids.......... " + str(ticket_ids))
            if ticket_ids:
                for ticket_id in ticket_ids:
                    ticket_arabic_label = ''
                    if ticket_id.stage_id.name:
                        _logger.error("............my ticket api in ticket_ids.......... " + str(ticket_id.stage_id.name))
                        stage_translation = request.env['ir.translation'].search(
                            [('lang', '=', 'ar_001'), ('source', '=', ticket_id.stage_id.name),
                             ('name', '=', 'helpdesk.stage,name')], limit=1)
                        _logger.error("............my ticket api in ticket_ids.......... " + str(stage_translation))
                        if stage_translation:
                            ticket_arabic_label = stage_translation.value
                    data.append({
                        'ticket_id': ticket_id.id,
                        'date': ticket_id.create_date.strftime('%d-%m-%Y'),
                        'topic': ticket_id.name or '',
                        'description': ticket_id.description or '',
                        'agent_response': ticket_id.user_last_response or '',
                        'stage_id':ticket_id.stage_id.id,
                        'stage_en_label':ticket_id.stage_id.name,
                        'stage_ar_label':ticket_arabic_label,
                         }
                    )
        return valid_response(data)


    @validate_token
    @http.route("/api/testPayload", type="http", auth="none", methods=["GET"], csrf=False)
    def testPayload(self, **payload):
        mob_no = payload.get('mobile_no', False)
        data=[]
        if mob_no:
            data.append({
                'mob_no':mob_no
            })
        return valid_response(data)


    @validate_token
    @http.route("/api/trackShipment", type="http", auth="none", methods=["GET"], csrf=False)
    def track_ship_status(self, **payload):
        so_line_ref = payload.get('order_ref', False)
        receiver_mob_no = payload.get('receiver_mob_no', False)
        domain = [('sale_line_rec_name', '=', so_line_ref)]
        data = []
        if so_line_ref:
            if receiver_mob_no:
                domain.append(('receiver_mob_no','=',receiver_mob_no))
            cargo_line = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(domain,limit=1)
            if cargo_line:
                order_date = cargo_line.order_date
                if order_date:
                    order_date = order_date.strftime('%d-%B-%Y')
                data.append(
                    {   'order_ref': cargo_line.sale_line_rec_name,
                        'receiver_name': cargo_line.receiver_name,
                        'receiver_mob_no': cargo_line.receiver_mob_no,
                        'customer_name': cargo_line.customer_id.name,
                        'order_date': order_date,
                        'loc_from': cargo_line.loc_from.route_waypoint_name,
                        'loc_to': cargo_line.loc_to.route_waypoint_name,
                        'expected_delivery': cargo_line.expected_delivery,
                        'car_model': cargo_line.car_model.car_model_name,
                        'year': cargo_line.year.car_year_name,
                        'car_make': cargo_line.car_make.car_maker.car_make_ar_name,
                        'state': cargo_line.state,
                        'est_no_delivery_days':cargo_line.est_no_delivery_days,
                        'est_max_no_delivery_days':cargo_line.est_max_no_delivery_days,
                    }
                )
        return valid_response(data)
        
    @validate_token
    @http.route("/api/paymentGetway/payfort/credentials", type="http", auth="none", methods=["GET"], csrf=False)
    def get_acquirers(self, **payload):
        acquirer_ids = request.env['payment.acquirer'].sudo().search_read(
            domain=[('provider', '=', 'payfort')],
            fields=['provider', 'environment', 'merchant_identifier', 'access_code', 'sha_type', 'request_phrase', 'response_phrase'],
            limit=1
            )
        acquirer_ids[0]['sha_type'] = acquirer_ids[0]['sha_type'].upper()
        return valid_response(acquirer_ids)

    @validate_token
    @http.route("/api/paymentGetway/payfort/postTransactionData", type="http", auth="none", methods=["POST"], csrf=False)
    def postTransactionData(self, **payload):
        return valid_response([])
    
    @validate_token
    @http.route("/api/driver/cash_collect", type="http", auth="none", methods=["POST"], csrf=False)
    def driver_cash_collect(self, **payload):
        so_line_ref = payload.get('order_ref', False)
        domain = [('sale_line_rec_name', '=', so_line_ref)]
        cargo_line = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(domain,limit=1)
        data = []
        if cargo_line:
            vals = {}
            for lkey in ['driver_id', 'customer_id', 'cargo_sale_line_id', 'collection_method']:
                value =  payload.get(lkey, False)
                vals.update({
                    lkey: value and value.isdigit() and int(value) or value
                })
            vals['collected_amount'] = float(payload.get('collected_amount', 0))
            vals['cargo_sale_line_id'] = cargo_line.id
            if vals:
                res = request.env['driver.cash.credit.collection'].sudo().create(vals)
                data = res.sudo().read( ['collection_reference', 'collection_method', 'collected_amount', 'state'])[0]
        return valid_response(data)

    @validate_token
    @http.route("/api/create_inspection", type="http", auth="none", methods=["POST"], csrf=False)
    def create_incpection(self, **payload):
        so_line_ref = payload.get('order_ref', False)
        plate_no = payload.get('plate_no', False)
        chassis_no = payload.get('chassis_no', False)
        odoo_id =  payload.get('odoo_id', False)
        cargo_line = False
        bsg_cargo_sale_id = False
        if plate_no:
            p = plate_no.replace(' ', '')
            p_num = [n for n in p if n.isdigit()]
            p_ch = [c for c in p if not c.isdigit()]
            if p_num and p_ch:
                p_ch.reverse()
                plate_no = ''.join(p_num)+' '+ ' '.join(p_ch)
        ins_vals = {
            'plate_no': plate_no,
            'chassis_no': chassis_no,
            'odoo_id': odoo_id and request.env['hr.employee'].sudo().search([('id', '=', int(odoo_id))], limit=1) and odoo_id or False
        }
        if so_line_ref:
            domain = [('sale_line_rec_name', '=', so_line_ref)]
            cargo_line = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(domain,limit=1)
            bsg_cargo_sale_id = cargo_line.bsg_cargo_sale_id
            ins_vals.update({'cargo_sale_id': bsg_cargo_sale_id.id,'cargo_sale_line_id': cargo_line.id,
                        'customer': bsg_cargo_sale_id.customer.id,
                       'branch_from': bsg_cargo_sale_id.loc_from.id,
                       'branch_to': bsg_cargo_sale_id.loc_to.id,
                      })
        if bsg_cargo_sale_id and bsg_cargo_sale_id.loc_from.loc_branch_id and bsg_cargo_sale_id.create_uid.user_branch_id:
             ins_vals['branch_ids']=  [(6, 0, [bsg_cargo_sale_id.loc_from.loc_branch_id.id, bsg_cargo_sale_id.create_uid.user_branch_id.id])]
        inspection_id = request.env['bassami.inspection'].sudo().create(ins_vals)
        attachment_top_id = inspection_id.create_or_write_image(inspection_id.attachment_top_id, base64.b64encode(payload.get('top').read()), 'TopScrren') 
        attachment_left_id = inspection_id.create_or_write_image(inspection_id.attachment_left_id, base64.b64encode(payload.get('left').read()), 'LeftScrren') 
        attachment_right_id =inspection_id.create_or_write_image(inspection_id.attachment_right_id, base64.b64encode(payload.get('right').read()), 'RightScrren')
        attachment_bottom_id =inspection_id.create_or_write_image(inspection_id.attachment_bottom_id, base64.b64encode(payload.get('bottom').read()), 'BottomScrren') 
        vals = {
            'attachment_top_id' : attachment_top_id,
            'attachment_left_id': attachment_left_id,
            'attachment_right_id': attachment_right_id,
            'attachment_bottom_id': attachment_bottom_id,
        }
        if payload.get('digital_signature', False):
            vals.update({'digital_signature': base64.b64encode(payload.get('signature').read())})
        inspection_id.write(vals)
        # other_image_keys = [key for key in payload.keys() if key.startswith('additional_image')]
        attached_files = request.httprequest.files.getlist('additional_images')
        for other_image in attached_files:
            attachment = inspection_id.create_or_write_image(False, base64.b64encode(other_image.read()), False)
            inspection_id.write({'attachment_ids':[(4, attachment)],'count':inspection_id.count + 1})
        data = inspection_id.sudo().read(['name'])[0]
        return valid_response(data)
    

    @validate_token
    @http.route("/api/car_inspection_data", type="http", auth="none", methods=["POST"], csrf=False)
    def car_inspection_data(self, **payload):
        inspection_id = request.env['bassami.inspection'].sudo().search([('name', '=', payload.get('inspection_ref'))], limit=1)
        vals = {}
        data = []
        if inspection_id:
            if 'car_inspection_image' in payload.keys():
                car_inpection_image = base64.b64encode(payload.get('car_inspection_image', False).read())
                vals ['attachment_car_image_id'] = inspection_id.create_or_write_image(inspection_id.attachment_car_image_id, car_inpection_image, 'marked_car_image')
            for k in ['hail_scratches', 'small_scratches', 'spare_tire', 'media_player', 'remote_control']:
                vals [k] = payload.get(k, 'False').lower() in ['true', True] and True or False
            vals['plate_number'] = payload.get('plate_number', False)
            if vals:
                inspection_id.sudo().write(vals)
                data = inspection_id.sudo().read(['name'])[0]
        return valid_response(data)

    @validate_token
    @http.route("/api/car_inspection_signature", type="http", auth="none", methods=["POST"], csrf=False)
    def car_inspection_signature(self, **payload):
        inspection_id = request.env['bassami.inspection'].sudo().search([('name', '=', payload.get('inspection_ref'))], limit=1)
        vals = {}
        data = []
        if inspection_id:
            if 'car_inspection_signature' in payload.keys():
                car_inpection_signature = base64.b64encode(payload.get('car_inspection_signature', False).read())
                if car_inpection_signature:
                    vals ['digital_signature'] = car_inpection_signature
                    vals['state'] = 'underprocess'
            if vals:
                inspection_id.sudo().write(vals)
                data = inspection_id.sudo().read(['name'])[0]
        return valid_response(data)

    @validate_token
    @http.route("/api/add_image_note", type="http", auth="none", methods=["POST"], csrf=False)
    def add_image_note(self, **payload):
        inspection_id = request.env['bassami.inspection'].sudo().search([('name', '=', payload.get('inspection_ref'))], limit=1)
        vals = {}
        data = []
        if inspection_id:
            if 'image' in payload.keys():
                image = base64.b64encode(payload.get('image', False).read())
                if image:
                    vals['inspection_id'] = inspection_id.id
                    vals['image'] = image
                    vals['note'] = payload.get('note', False)
                    vals['user_name'] = payload.get('user_name', False)
            if vals:
                request.env['inspection.note.line'].sudo().create(vals)
                data = inspection_id.sudo().read(['name'])[0]
        return valid_response(data)
    
    @validate_token
    @http.route("/api/car_inspection_view", type="http", auth="none", methods=["POST"], csrf=False)
    def car_inspection_veiw(self, **payload):
        inspection_id = request.env['bassami.inspection'].sudo().search([('cargo_sale_line_id.sale_line_rec_name', '=', payload.get('order_ref'))], limit=1,order="create_date desc")
        data = []
        vals={}
        if inspection_id:
            vals['inspection_ref'] = inspection_id.name
            vals['order_ref'] = inspection_id.cargo_sale_line_id.sale_line_rec_name
            vals.update(inspection_id.read(['plate_number', 'hail_scratches', 'small_scratches', 'spare_tire', 'media_player', 'remote_control'])[0])
            vals['odoo_id'] = inspection_id.odoo_id and inspection_id.odoo_id.id or 0
            for k in ['top', 'left', 'right', 'bottom', 'car_inspection_image', 'car_inspection_signature']:
                vals[k] = False
            if inspection_id.attachment_top_id and inspection_id.attachment_top_id.datas:
                vals['top'] = inspection_id.attachment_top_id.datas.decode()
            if inspection_id.attachment_left_id and inspection_id.attachment_left_id.datas:
                vals['left'] = inspection_id.attachment_left_id.datas.decode()
            if inspection_id.attachment_right_id and inspection_id.attachment_right_id.datas:
                vals['right'] = inspection_id.attachment_right_id.datas.decode()
            if inspection_id.attachment_bottom_id and inspection_id.attachment_bottom_id.datas:
                vals['bottom'] = inspection_id.attachment_bottom_id.datas.decode()
            if inspection_id.attachment_car_image_id and inspection_id.attachment_car_image_id.datas:
                vals['car_inspection_image'] = inspection_id.attachment_car_image_id.datas.decode()
            if inspection_id.digital_signature:
                vals['car_inspection_signature'] = inspection_id.digital_signature.decode()
            other_images = []
            if inspection_id.attachment_ids:
                for attachment in inspection_id.attachment_ids:
                    if attachment.datas:
                        other_images.append(attachment.datas.decode())
            for note in inspection_id.note_line_ids:
                other_images.append(note.image.decode())
            vals['other_images'] = other_images
        if vals:
            data.append(vals)
        return valid_response(data)

    @validate_token
    @http.route("/api/change_trip_state", type="http", auth="none", methods=["POST"], csrf=False)
    def change_trip_state(self, **payload):
        trip_ref =  payload.get('trip_ref', False)
        trip_state =  payload.get('trip_state', False)
        if trip_ref and trip_state:
            trip_id = request.env['fleet.vehicle.trip'].sudo().search([('name', '=', trip_ref)])
            trip_id.sudo().write({'state': trip_state})
            return valid_response([{
                            'trip_ref': trip_id.name
                        }])
        else:
            return valid_response([])


    @validate_token
    @http.route("/api/create_trip", type="http", auth="none", methods=["POST"], csrf=False)
    def create_trip(self, **payload):
        so_line_ref = payload.get('order_ref', False)
        driver_code = payload.get('driver_code', False)
        location_id = payload.get('location_id', False)
        vehicle_code = payload.get('vehicle_code', False)
       
        data = []
        if so_line_ref and driver_code and location_id:
            so_domain = [('sale_line_rec_name', '=', so_line_ref)]
            cargo_line = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(so_domain,limit=1)
            if cargo_line:
                local_route_id = request.env['bsg_route'].sudo().search([('waypoint_from','=', int(location_id))])
                local_route_id = local_route_id.filtered(lambda w: 921 in w.waypoint_to_ids.mapped('waypoint.id'))
                driver_id = request.env['hr.employee'].search([('driver_code','=',driver_code), ('company_id','=',1)], limit=1)
                vehcile_id = request.env['fleet.vehicle'].search([('taq_number','=',vehicle_code), ('company_id','=',1)], limit=1)
                if local_route_id and driver_id and vehcile_id:
                    trip_id = request.env['fleet.vehicle.trip'].sudo().create({
                        'trip_type': 'local',
                        'route_id': local_route_id[0].id,
                        'vehicle_id': vehcile_id.id,        
                        'driver_id': driver_id.id,
                        'expected_start_date':  fields.Datetime.now(),
                        'expected_end_date': fields.Datetime.now() + timedelta(hours=local_route_id[0].estimated_time)

                    })
                    trip_id.total_capacity = 2
                    trip_id.sudo()._onchange_route_id()
                    if trip_id.name == '/':
                        trip_id.name = request.env['ir.sequence'].sudo().with_context(force_company=request.env.user.company_id.id).next_by_code('bsg_fleet_vehicle_trip_sq_code')
                    cargo_line.bsg_cargo_sale_id.sudo().create_trip_picking(
                        cargo_line,
                        cargo_line.loc_from,
                        cargo_line.loc_to,
                        trip_id
                    )
                    if trip_id:
                        data.append({
                            'trip_ref': trip_id.name
                        })
                    trip_id.confim_data()
        return valid_response(data)    
    
    def process_qitaf_coupon(self, qitaf_coupon,lang="ar"):

        coupon = qitaf_coupon
        qitaf_base_url, qitaf_token, qitaf_user_key = 'https://coponey.com/api/ecommerce/', 'VeJpLjQPTGqHMB0R3t2r1mE48yY5xDuFa7XSKhof', 'hnsEgvUlKQrDqCVuXMZ6AePaj'
        headers = {
                'Authorization': 'Bearer %s'%qitaf_token,
                'Content-Type': 'application/json',}

        data = '{ "apiName": "couponDetails", "userKey": "%s", "language": "%s", "param": { "coupon": "%s" } }'%(qitaf_user_key,lang, coupon)
        response = requests.post(qitaf_base_url, headers=headers, data=data)
        return response.json()['response']

    @validate_token
    @http.route("/api/processCoupon", type="http", auth="none", methods=["GET"], csrf=False)
    def process_coupon(self, **payload):
        is_qitaf = payload.get('is_qitaf', False)
        coupon = payload.get('coupon', False)
        lang = payload.get("language","ar")
        if is_qitaf and coupon:
            return valid_response(self.process_qitaf_coupon(coupon,lang))
        else:
            return valid_response([])
            
    @validate_token
    @http.route("/api/print_order", type="http", auth="none", methods=["GET"], csrf=False)
    def print_order(self, **payload):
        so_line_ref = payload.get('order_ref', False)
        if so_line_ref:
            so_domain = [('sale_line_rec_name', '=', so_line_ref)]
            cargo_line = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(so_domain,limit=1)
            if cargo_line:
                attachment_id = request.env.ref('bsg_cargo_sale.report_shipment_report').sudo().with_context(
                        {'active_id': cargo_line.id}).render_qweb_pdf([cargo_line.id])[0]
                return request.make_response(
                   attachment_id,
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', 'attachment; filename=%s.pdf;'%cargo_line.sale_line_rec_name)
                    ]
                )
        return valid_response([])









