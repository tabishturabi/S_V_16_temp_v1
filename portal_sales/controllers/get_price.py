# -*- coding: utf-8 -*-

from odoo import http, fields as odoo_fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError ,ValidationError
import werkzeug
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
import pytz 
import collections, functools, operator
import requests
import logging
_logger = logging.getLogger(__name__)

class shipmentGetPrice(CustomerPortal):

    @http.route("/shipments/get_so_line_form", type='http', auth="public", website=True)
    def portal_cargo_sale_line_form(self):
        # Basic Field###########################################################
        company = request.website.company_id
        plate_vals = ['أ', 'ب', 'ح', 'د', 'ر', 'س', 'ص', 'ط', 'ع', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ى']

        values = {
            'plate_vals': plate_vals,
            'default_lang': request.env.context.get('lang') or 'en_US',
            'error': {},
            'error_message': [],
        }
        return request.render("portal_sales.cargo_sale_line_form", values)

    @http.route("/shipment/get_so_line", type='http', auth="public", website=True)
    def portal_so_line_submit(self, **kw):
        values = {}
        company = request.website.company_id
        _logger.error("/so line spec logs........ ........................+  " + str(kw))
        agreement = kw.get('agreement',False)
        chasis_no = kw.get('chasis_no',False)
        plate_no = kw.get('plate_no',False)
        plate_one = kw.get('plate_one',False)
        plate_second = kw.get('plate_second',False)
        plate_third = kw.get('plate_third',False)
        _logger.error("//so line spec logs agreement .type ........................+  " + str(type(agreement)))
        CargoSaleLine = request.env['bsg_vehicle_cargo_sale_line'].sudo()
        domain = []

        if agreement:
            domain.append(('sale_line_rec_name', '=', agreement))
        if chasis_no:
            domain.append(('chassis_no', '=', chasis_no))
        if plate_no:
            domain.append(('plate_no', '=', plate_no))
        if plate_one:
            domain.append(('palte_one', '=', plate_one))
        if plate_second:
            domain.append(('palte_second', '=', plate_second))
        if plate_third:
            domain.append(('palte_third', '=', plate_third))
        shipments = []
        _logger.error("//so line spec logs domain ........................+  " + str(domain))
        if domain:
            domain.append(('company_id', '=', company.id))
            domain.append(('customer_id', '=', request.env.user.partner_id.id))

            shipments = CargoSaleLine.search(domain)
        _logger.error("//so line spec logs shipments ........................+  " + str(shipments))
        values.update({
            'shipments': shipments,
        })
        return request.render("portal_sales.portal_specific_shipmentlines", values)

    @http.route("/shipments/get_price_form", type='http', auth="public", website=True)
    def portal_shipment_price_form(self):
                #Basic Field###########################################################
        company = request.website.company_id
        loc_from_ids = request.env['bsg_route_waypoints'].sudo().search(
            [('company_id', '=', company.id),('branch_type','!=',False),
            ('loc_branch_id','!=',False),('branch_type','in',['shipping','both']),('visible_on_mobile_app','=',True)])
        loc_to_ids = request.env['bsg_route_waypoints'].sudo().search(
            [('company_id', '=', company.id),('branch_type','!=',False),
            ('loc_branch_id','!=',False),('branch_type','in',['pickup','both']),('visible_on_mobile_app','=',True)])
    
        car_makes = request.env['bsg_car_config'].sudo().search([])
        car_models = request.env['bsg_car_model'].sudo().search([])
        car_sizes = request.env['bsg_car_size'].sudo().search([])

        values = {
            'car_makes': car_makes,
            'car_models': car_models,
            'car_sizes': car_sizes,
            'default_lang': request.env.context.get('lang') or 'en_US',
            'loc_from_ids': loc_from_ids,
            'loc_to_ids': loc_to_ids,
            'error': {},
            'error_message': [],
        }
        return request.render("portal_sales.vechicle_shipment_price_form",values)

    @http.route("/shipment/get_price", type='http', auth="public", website=True)
    def portal_shipment_price_submit(self,**kw):
        customer_id = request.env.user and request.env.user.partner_id.id or False
        company = request.website.company_id        
        loc_from = kw.get('loc_from',False)
        loc_to = kw.get('loc_to',False)
        car_model = kw.get('car_model',False)
        car_make = kw.get('car_make',False)
        customer_phone = kw.get('customer_phone','')
        customer_email = kw.get('customer_email','')
        if loc_from and loc_to and car_model and car_make:
            loc_from_rec = request.env['bsg_route_waypoints'].sudo().browse(int(loc_from))
            loc_to_rec = request.env['bsg_route_waypoints'].sudo().browse(int(loc_to))
            lead_name =  str(_("From ") + str(loc_from_rec.waypoint_english_name) + _(" To ") + str(loc_to_rec.waypoint_english_name) + _(" In ") + str(odoo_fields.Datetime.now()))
            if 'ar' in request.env.context.get('lang'):
                lead_name =  str(_("From ") + str(loc_from_rec.route_waypoint_name) + _(" To ") + str(loc_to_rec.route_waypoint_name) + _(" In ") + str(odoo_fields.Datetime.now()))
            try:
                lead_id = request.env['crm.lead'].sudo().create({
                    'name' :lead_name,
                    'loc_from': loc_from ,
                    'loc_to': loc_to ,
                    'car_model': car_model ,
                    'car_make': car_make ,
                    'email_from': customer_email,
                    'phone': customer_phone,
                    'partner_id': customer_id,
                    'partner_type': 'individual',
                    'company_id': company.id
                })
                return request.redirect(f"/shipment/get_price_leads/{lead_id.id}")
            except:
                return http.request.redirect('/my/home/')    
        return http.request.redirect('/my/home/') 

    # @http.route(['''/shipment/get_price_leads/<int:lead>''','''/shipment/get_price_leads/<int:lead>/page/<int:page>'''], type='http', auth="public",method="post", website=True)
    # def portal_shipment_lead_prices(self,page=0,lead=False,**kw):
    #     company = request.website.company_id
    #     partner_type = 'individual'
    #     values = []
    #     if lead:
    #         lead_id = request.env['crm.lead'].sudo().search([('id','=',lead)],limit=1)
    #         if lead_id:
    #             loc_from = lead_id.loc_from.id
    #             loc_to = lead_id.loc_to.id
    #             car_model = lead_id.car_model.id
    #             car_size = lead_id.car_size.id
    #
    #             values = request.env['bsg_vehicle_cargo_sale'].sudo().get_all_shipment_price_for_portal(\
    #                 company.id,partner_type,loc_from,loc_to,car_model,car_size)
    #     if len(values) < 1:
    #         return request.render("portal_sales.vechicle_shipment_show_prices",{
    #         'price_error': _("No Price Found For Your Request"),
    #         })
    #     else:
    #         url = f"/shipment/get_price_leads/{lead}"
    #         pager = portal_pager(url=url, total=len(values), page=page, step=6, scope=7, url_args=kw)
    #         offset = pager['offset']
    #         values = values[offset: offset + 6]
    #         return request.render("portal_sales.vechicle_shipment_show_prices",{
    #             'prices': values,
    #             'lead_id': lead_id,
    #             'default_lang': request.env.context.get('lang') or 'en_US',
    #             'pager': pager,
    #             })

    # @http.route('/create_sale_order_lead_form/', auth='user',method="post", website=True,csrf=False)
    # def create_sale_order_lead_form(self, **kw):
    #     company = request.website.company_id
    #
    #
    #     default_payment_method_id = request.env['cargo_payment_method'].sudo().search(
    #         [('payment_type', '=', 'cash')], limit=1).id
    #     nationality_ids = request.env['res.country'].sudo().search([('visible_on_mobile_app','=',True)])
    #     default_country = request.env['res.country'].sudo().search(
    #         [('code', '=', 'SA'), ('phone_code', '=', '966')], limit=1).id
    #     lead_id = kw.get('lead_id',False)
    #     agreement_type = kw.get('agreement_type',False)
    #     shipment_type_id = kw.get('shipment_type',False)
    #     shipment_type = request.env['bsg.car.shipment.type'].sudo().search(
    #         [('id', '=', shipment_type_id)])
    #     lead_id = request.env['crm.lead'].sudo().search([('id','=',lead_id)],limit=1)
    #
    #     years = request.env['bsg.car.year'].sudo().search([])
    #     car_colors = request.env['bsg_vehicle_color'].sudo().search([])
    #     palte_letter = [('أ', 'أ'), ('ب', 'ب'), ('ح', 'ح'), ('د', 'د'),
    #                     ('ر', 'ر'), ('س', 'س'), ('ص', 'ص'), ('ط', 'ط'),
    #                     ('ع', 'ع'), ('ق', 'ق'), ('ك', 'ك'), ('ل', 'ل'),
    #                     ('م', 'م'), ('ن', 'ن'), ('ه', 'هـ'), ('و', 'و'), ('ى', 'ى')]
    #     plate_types = request.env['bsg_plate_config'].sudo().search([])
    #     plate_registrations = [
    #         ('saudi', 'لوحة سعودية'), ('non-saudi', 'لوحة أخرى '), ('new_vehicle', 'بدون لوحة')]
    #
    #     values = {
    #         'customer': request.env.user.partner_id,
    #         'partner_type': request.env.user.partner_id.partner_types,
    #         'request_type': 'individual',
    #         'error': {},
    #         'error_message': [],
    #         'defualt_sender_name': request.env.user.partner_id.name or '',
    #         'default_sender_type': request.env.user.partner_id.customer_type or '',
    #         'default_sender_nationality': request.env.user.partner_id.customer_nationality.id or '',
    #         'default_sender_id_type': request.env.user.partner_id.customer_id_type or '',
    #         'default_sender_id_card_no': request.env.user.partner_id.customer_id_card_no or request.env.user.partner_id.iqama_no or '',
    #         'default_sender_visa_no': request.env.user.partner_id.customer_visa_no or '',
    #         'sender_type': [('1', _('Saudi')), ('2', _('Non-Saudi')), ('3', _('Corporate'))],
    #         'sender_id_type': [('saudi_id_card', _('Saudi ID Card')), ('iqama', _('Iqama')), ('gcc_national', _('GCC National')),
    #                            ('passport', _('Passport')), ('other', _('Other'))],
    #         'nationality_ids': nationality_ids,
    #         'default_payment_method_id': default_payment_method_id,
    #         'default_country': default_country,
    #         'lead_id': lead_id,
    #         'agreement_type':agreement_type,
    #         'shipment_type':shipment_type,
    #         'default_lang': request.env.context.get('lang') or 'en_US',
    #         'years': years,
    #         'car_colors': car_colors,
    #         'palte_letter': palte_letter,
    #         'plate_types': plate_types,
    #         'plate_registrations': plate_registrations,
    #     }
    #     return http.request.render('portal_sales.create_shipment_sale_lead_form', values)

    @http.route("/cargo_orders/get_car_size", type='json', auth="public", website=True)
    def get_car_size(self, car_model, car_config_id, **post):
        values = {'car_size':False}
        if car_model and car_config_id:
            car_line = request.env['bsg_car_line'].sudo().search([('car_model','=',car_model),('car_config_id','=',car_config_id)],limit=1)
            if car_line:
                values['car_size'] = car_line.car_size.id
        return values        



    def datetime_cus(self,field_input):
        lang = request.env['ir.qweb.field'].user_lang()
        current_datatime = odoo_fields.Datetime.now()
        strftime_format = (u"%s %s" % (lang.date_format, lang.time_format))
        field_input = field_input + ' ' +str(current_datatime.hour)+':'+str(current_datatime.minute)+':'+str(current_datatime.second)
        user_tz = pytz.timezone(request.context.get('tz') or request.env.user.tz or 'UTC')
        dt = user_tz.localize(datetime.strptime(field_input, strftime_format)).astimezone(pytz.utc)
        return dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)




    @http.route('/sale_order_create_from_lead/', auth='user', website=True)
    def create_sale_order_from_lead(self, **kw):
        vals = {}
        url = False

        lead_id = kw.get('lead_id',False) 
        agreement_type = kw.get('agreement_type',False) 
        shipment_type_id = kw.get('shipment_type',False) 
        shipment_type = request.env['bsg.car.shipment.type'].sudo().search(
            [('id', '=', shipment_type_id)])    
        lead_id = request.env['crm.lead'].sudo().search([('id','=',lead_id)],limit=1)
        if shipment_type and lead_id:
            shipment_date = odoo_fields.Datetime.now()
            cargo_sale_type = 'local'
            company = request.website.company_id
            currency = company.currency_id.id
            loc_from = lead_id.loc_from
            loc_to = lead_id.loc_to
            partner_type = lead_id.partner_type

            if loc_from.is_international or loc_to.is_international:
                cargo_sale_type = 'international'
            else:
                cargo_sale_type = 'local'
            if cargo_sale_type == 'international' and loc_from.is_international:
                currency = loc_from.loc_branch_id.currency_id.id
            try:
                shipment_date = self.datetime_cus(kw.get('shipment_date'))
            except:    
                shipment_date = odoo_fields.Datetime.now()    

        
        values = {
            'partner_types': kw.get('partner_types'),
            'cargo_sale_type': cargo_sale_type,
            'currency_id': currency,
            'company_id': company.id,
            'customer': kw.get('customer'),
            'cooperate_customer': kw.get('customer'),
            'shipment_type': kw.get('agreement_type'),
            'payment_method': kw.get('default_payment_method_id'),
            'loc_from': loc_from.id,
            'loc_to': loc_to.id,
            'note': kw.get('customer'),
            #'customer_contract': kw.get('customer_contract'),
            'same_as_customer': True and kw.get('sender_default') == 'on' or False,
            'sender_name': kw.get('sender_name'),
            'sender_type': kw.get('sender_type'),
            'sender_nationality': kw.get('sender_nationality'),
            'sender_id_type': kw.get('sender_id_type'),
            'sender_id_card_no': kw.get('sender_id_card_no'),
            'sender_visa_no': kw.get('sender_visa_no'),
            'same_as_sender': True and kw.get('owner_default') == 'on' or False,
            'owner_name': kw.get('owner_name'),
            'owner_type': kw.get('owner_type'),
            'owner_nationality': kw.get('owner_nationality'),
            'owner_id_type': kw.get('owner_id_type'),
            'owner_id_card_no': kw.get('owner_id_card_no'),
            'owner_visa_no': kw.get('owner_visa_no'),
            'same_as_owner': True and kw.get('receiver_default') == 'on' or False,
            'receiver_name': kw.get('receiver_name'),
            'receiver_type': kw.get('receiver_type'),
            'receiver_nationality': kw.get('receiver_nationality'),
            'receiver_id_type': kw.get('receiver_id_type'),
            'receiver_id_card_no': kw.get('receiver_id_card_no'),
            'receiver_visa_no': kw.get('receiver_visa_no'),
            'receiver_mob_no': kw.get('receiver_mob_no'),
            'no_of_copy': kw.get('no_of_copy'),
            'shipment_date':shipment_date,
            'recieved_from_customer_date' :shipment_date,
            'is_from_portal' : True,
            'lead_id' :lead_id.id,
        }
        if values['shipment_type'] == 'return':
            values['return_loc_from'] = kw.get('return_loc_from')
            values['return_loc_to'] = kw.get('return_loc_to')
        try:
            order_id = request.env['bsg_vehicle_cargo_sale'].sudo().create(values)
            if order_id:
                url = order_id.sudo().get_portal_url()
                try:
                    self.create_sale_order_line_from_lead(order_id,lead_id,kw)
                    lead_id.sudo().write({'type' :'opportunity'})
                    lead_id.sudo().action_set_won_rainbowman()
                    vals['success_create_message'] = True
                except:
                    values['error_message'] = True
            
        except BaseException as error:
            vals['error_message'] = True
        if url:
            return http.request.redirect(_build_url_w_params(url, vals))
        return request.redirect('/my/home/')        

    def create_sale_order_line_from_lead(self,order_id,lead_id,kw):
        values = {}
        url = False
        company = request.website.company_id
        if order_id:

            values['car_make'] = lead_id.car_make.id
            values['car_model'] = lead_id.car_model.id
            values['car_size'] = lead_id.car_size.id
            values['car_classfication'] = lead_id.car_classfication.id

            values['bsg_cargo_sale_id'] = order_id.id
            values['shipment_type'] = kw.get('shipment_type')
            values['year'] = kw.get('year')
            
            values['car_color'] = kw.get('car_color')
            
            values['plate_registration'] = kw.get('plate_registration')
            values['plate_type'] = kw.get('plate_type')
            values['palte_one'] = kw.get('palte_one')
            values['palte_second'] = kw.get('palte_second')
            values['palte_third'] = kw.get('palte_third')
            if kw.get('plate_no',False):
                values['plate_no'] = kw.get('plate_no')
            if kw.get('non_saudi_plate_no',False):
                values['non_saudi_plate_no'] = kw.get('non_saudi_plate_no')
            values['chassis_no'] = kw.get('chassis_no')

            default_customer_price_list = request.env['product.pricelist'].sudo().search(
            [('default_in_portal', '=', True),'|', ('agreement_type', '=', False), ('agreement_type', '=', order_id.shipment_type)], limit=1)
            if not default_customer_price_list or order_id.loc_from.is_international or order_id.loc_to.is_international:
                default_customer_price_list = request.env['product.pricelist'].sudo().search(
                    [('is_public', '=', True)], limit=1)
            values['customer_price_list'] = default_customer_price_list.id        

            default_cargo_service_id = company.sudo().cargo_service_id
            values['service_type'] = default_cargo_service_id.id

            #ِAdd Discount 
            discount = 0.0
            if default_customer_price_list and default_cargo_service_id:
                if default_customer_price_list.item_ids:
                    for data in default_customer_price_list.item_ids:
                        if data.product_tmpl_id.id == default_cargo_service_id.id:
                            discount = data.percent_price
            values['discount'] = discount          

            # Get Default Taxes:
            default_tax_ids = False
            if order_id.loc_from.is_international or order_id.loc_to.is_international:
                default_tax_ids = False
            else:
                PinConfig = request.website.company_id.sudo()
                default_tax_ids = PinConfig.sudo().tax_ids.ids or company.sudo().cargo_service_id.taxes_id.ids                
            if default_tax_ids:
                values['tax_ids'] = [(6, 0, default_tax_ids)]

            try:
                pice_values = request.env['bsg_vehicle_cargo_sale_line'].sudo().get_price_for_portal(
                    int(values['shipment_type']),values['car_model'],values['car_size'],values['service_type'],values['car_classfication'],
                    order_id.id,values['discount']
                )
                values.update(pice_values)
                line_id = request.env['bsg_vehicle_cargo_sale_line'].sudo().create(values)
                line_id.sudo().write({'recieved_from_customer_date': order_id.recieved_from_customer_date})
                order_id.sudo()._amount_all()
                order_id.sudo()._amount_so_all()
                return True
            except:
                raise ValidationError("Can't Create Order Line")
        else:
                raise ValidationError("No Order Id")        
        