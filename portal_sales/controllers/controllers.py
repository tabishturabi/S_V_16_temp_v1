# -*- coding: utf-8 -*-

from odoo import http, fields as odoo_fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
import werkzeug
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
import pytz
import collections, functools, operator
import requests

class VechialPortalSale(http.Controller):

    @http.route('/sale_individual_order/', auth='user', website=True)
    def sale_individual_order(self, **kw):
        contract_ids = False
        company = request.website.company_id
        loc_from_ids = request.env['bsg_route_waypoints'].sudo().search(
            [('company_id', '=', company.id),('branch_type','!=',False),('is_portal_hide_from_pickup','=',False),
            ('loc_branch_id','!=',False),('branch_type','in',['shipping','both'])])
        loc_to_ids = request.env['bsg_route_waypoints'].sudo().search(
            [('company_id', '=', company.id),('branch_type','!=',False),('is_portal_hide_from_to','=',False),
            ('loc_branch_id','!=',False),('branch_type','in',['pickup','both'])])
        return_loc_ids = request.env['bsg_route_waypoints'].sudo().search(
            [('company_id', '=', company.id),('branch_type','!=',False),('loc_branch_id','!=',False),('visible_on_mobile_app','=',True)])   
        # Get Payment Method
        payment_method_id = request.env['cargo_payment_method'].sudo().search(
            [('payment_type', 'in', ['cash',  'pod'])])
        default_payment_method_id = request.env['cargo_payment_method'].sudo().search(
            [('payment_type', '=', 'cash')], limit=1).id
        nationality_ids = request.env['res.country'].sudo().search([('visible_on_mobile_app','=',True)])
        default_country = request.env['res.country'].sudo().search(
            [('code', '=', 'SA'), ('phone_code', '=', '966')], limit=1).id

        values = {
            'customer': request.env.user.partner_id,
            'partner_type': request.env.user.partner_id.partner_types,
            'request_type': 'individual',
            'contract_ids': contract_ids,
            # 'cargo_sale_types' : [('local', 'Local'),('international', 'International')],
            'loc_from_ids': loc_from_ids,
            'loc_to_ids': loc_to_ids,
            'return_loc_ids' : return_loc_ids,
            'payment_method_id': payment_method_id,
            'error': {},
            'error_message': [],
            'defualt_sender_name': request.env.user.partner_id.name or '',
            'default_sender_type': request.env.user.partner_id.customer_type or '',
            'default_sender_nationality': request.env.user.partner_id.customer_nationality.id or '',
            'default_sender_id_type': request.env.user.partner_id.customer_id_type or '',
            'default_sender_id_card_no': request.env.user.partner_id.customer_id_card_no or request.env.user.partner_id.iqama_no or '',
            'default_sender_visa_no': request.env.user.partner_id.customer_visa_no or '',
            'sender_type': [('1', _('Saudi')), ('2', _('Non-Saudi')), ('3', _('Corporate'))],
            'sender_id_type': [('saudi_id_card', _('Saudi ID Card')), ('iqama', _('Iqama')), ('gcc_national', _('GCC National')),
                               ('passport', _('Passport')), ('other', _('Other'))],
            'nationality_ids': nationality_ids,
            'default_payment_method_id': default_payment_method_id,
            'default_country': default_country,
        }
        return http.request.render('portal_sales.vechicle_shipment_sale', values)

    @http.route('/sale_coorperate_order/', auth='user', website=True)
    def sale_coorperate_order(self, **kw):
        contract_ids = False
        company = request.website.company_id
        if not company.portal_create_cooreperate_orders:
            return http.request.redirect('/my/home/')
        if request.env.user.partner_id.parent_id:
            contract_ids = request.env['bsg_customer_contract'].sudo().search([('cont_customer', '=', request.env.user.partner_id.parent_id.id),
                                                                                    ('company_id', '=', company.id)])
            if not contract_ids:
                contract_ids = request.env['bsg_customer_contract'].sudo().search([('cont_customer', '=', request.env.user.partner_id.id),
                                                                                    ('company_id', '=', company.id)])
        # if not contract_ids:
        #      return http.request.render('portal_sales.vechicle_shipment_sale',{'contract_ids':contract_ids})
        # Get Locations
        loc_from_ids = request.env['bsg_route_waypoints'].sudo().search(
            [('company_id', '=', company.id)])
        loc_to_ids = request.env['bsg_route_waypoints'].sudo().search(
            [('company_id', '=', company.id)])
        # Get Payment Method
        payment_method_id = request.env['cargo_payment_method'].sudo().search(
            [('payment_type', 'in', ['cash', 'credit', 'pod'])])
        default_payment_method_id = request.env['cargo_payment_method'].sudo().search(
            [('payment_type', '=', 'credit')], limit=1).id
        nationality_ids = request.env['res.country'].sudo().search([('visible_on_mobile_app','=',True)])
        default_country = request.env['res.country'].sudo().search(
            [('code', '=', 'SA'), ('phone_code', '=', '966')], limit=1).id

        values = {
            'customer': request.env.user.partner_id.parent_id,
            'partner_type': request.env.user.partner_id.parent_id.partner_types,
            'request_type': 'coorperate',
            # 'cargo_sale_types' : [('local', 'Local'),('international', 'International')],
            'contract_ids': contract_ids,
            'loc_from_ids': loc_from_ids,
            'loc_to_ids': loc_to_ids,
            'payment_method_id': payment_method_id,
            'error': {},
            'error_message': [],
            'defualt_sender_name': request.env.user.partner_id.parent_id.name or '',
            'default_sender_type': request.env.user.partner_id.parent_id.customer_type or '',
            'default_sender_nationality': request.env.user.partner_id.parent_id.customer_nationality.id or '',
            'default_sender_id_type': request.env.user.partner_id.parent_id.customer_id_type or '',
            'default_sender_id_card_no': request.env.user.partner_id.parent_id.customer_id_card_no or request.env.user.partner_id.parent_id.iqama_no or '',
            'default_sender_visa_no': request.env.user.partner_id.parent_id.customer_visa_no or '',
            'sender_type': [('1',_('Saudi')), ('2', _('Non-Saudi')), ('3', _('Corporate'))],
            'sender_id_type': [('saudi_id_card', _('Saudi ID Card')), ('iqama', _('Iqama')), ('gcc_national', _('GCC National')),
                               ('passport', _('Passport')), ('other', _('Other'))],
            'nationality_ids': nationality_ids,
            'default_payment_method_id': default_payment_method_id,
            'default_country': default_country,

        }
        return http.request.render('portal_sales.vechicle_shipment_sale', values)


    def datetime_cus(self,field_input):
        lang = request.env['ir.qweb.field'].user_lang()
        current_datatime = odoo_fields.Datetime.now()
        strftime_format = (u"%s %s" % (lang.date_format, lang.time_format))
        field_input = field_input + ' ' +str(current_datatime.hour)+':'+str(current_datatime.minute)+':'+str(current_datatime.second)
        user_tz = pytz.timezone(request.context.get('tz') or request.env.user.tz or 'UTC')
        dt = user_tz.localize(datetime.strptime(field_input, strftime_format)).astimezone(pytz.utc)
        return dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @http.route('/sale_coorperate_order_create/', methods=['GET', 'POST'],  auth='user', website=True)
    def sale_coorperate_order_create(self, **kw):
        shipment_date = odoo_fields.Datetime.now()
        cargo_sale_type = 'local'
        company = request.website.company_id
        currency = company.currency_id.id
        vals = {}
        url = False
        loc_from = request.env['bsg_route_waypoints'].sudo().search(
            [('id', '=', kw.get('loc_from'))])
        loc_to = request.env['bsg_route_waypoints'].sudo().search(
            [('id', '=', kw.get('loc_to'))])

        if loc_from.is_international or loc_to.is_international:
            cargo_sale_type = 'international'
        else:
            cargo_sale_type = 'local'
        if cargo_sale_type == 'international' and loc_from.is_international:
            currency = loc_from.loc_branch_id.currency_id.id
        #user_timezone = int(kw.get('user_timezone'))
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
            'customer_price_list': kw.get('customer_price_list'),
            'cooperate_customer': kw.get('customer'),
            'shipment_type': kw.get('agreement_type'),
            'payment_method': kw.get('payment_method'),
            'loc_from': kw.get('loc_from'),
            'loc_to': kw.get('loc_to'),
            'note': kw.get('note'),
            'customer_contract': kw.get('customer_contract'),
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
        }
        if values['shipment_type'] == 'return':
            values['return_loc_from'] = kw.get('return_loc_from')
            values['return_loc_to'] = kw.get('return_loc_to')
        try:
            order_id = request.env['bsg_vehicle_cargo_sale'].sudo().create(values)
            vals['success_create_message'] = True
            url = order_id.sudo().get_portal_url()
        except BaseException as error:
            vals['error_message'] = True
        if url:
            return http.request.redirect(_build_url_w_params(url, vals))
        return request.redirect('/my/home/')

    @http.route('/shipment/create_new_line', auth='user', website=True)
    def sale_coorperate_order_line_create(self, **kw):
        values = {}
        url = False
        if kw.get('bsg_cargo_sale_id'):
            bsg_cargo_sale_id = request.env['bsg_vehicle_cargo_sale'].sudo().search(
                [('id', '=', kw.get('bsg_cargo_sale_id'))])
            url = bsg_cargo_sale_id.sudo().get_portal_url()
        del kw['default_cargo_service_id']
        del kw['loc_from']
        del kw['loc_to']

        if not kw['plate_no']:
            del kw['plate_no']
        if not kw['non_saudi_plate_no']:
            del kw['non_saudi_plate_no']
        if kw['tax_ids']:
            kw['tax_ids'] = str(kw['tax_ids']).strip('][').split(', ')
            kw['tax_ids'] = [(6, 0, kw['tax_ids'])]
        try:
            kw['state'] = 'registered'
            order_id = request.env['bsg_vehicle_cargo_sale_line'].sudo().create(kw)
            order_id.sudo().write({'recieved_from_customer_date': bsg_cargo_sale_id.recieved_from_customer_date})
            bsg_cargo_sale_id.sudo()._amount_all()
            bsg_cargo_sale_id.sudo()._amount_so_all()
            values['success_create_message'] = True
        except:
            values['error_message'] = False
        if url:
            return werkzeug.utils.redirect(_build_url_w_params(url, values))
        return http.request.redirect('/my/home/')



    @http.route('/shipment/edit_cargo_line', auth='user', website=True)
    def cargo_sale_order_line_edit(self, **kw):
        values = {}
        url = False
        if kw.get('bsg_cargo_sale_id'):
            bsg_cargo_sale_id = request.env['bsg_vehicle_cargo_sale'].sudo().search(
                [('id', '=', kw.get('bsg_cargo_sale_id'))])
            url = bsg_cargo_sale_id.sudo().get_portal_url()
        if kw.get('order_line_id'):
            line_id = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(
                [('id', '=', kw.get('order_line_id'))])

        del kw['default_cargo_service_id']
        del kw['loc_from']
        del kw['loc_to']
        del kw['order_line_id']
        del kw['bsg_cargo_sale_id']
        if not kw['plate_no']:
            del kw['plate_no']
        if not kw['non_saudi_plate_no']:
            del kw['non_saudi_plate_no']
        if line_id:
            if line_id.bsg_cargo_sale_id.state != 'draft':
                values['error_message'] = _(
                    "Sorry Can't Modify Confirmed Record")
            else:
                try:
                    line_id.sudo().write(kw)
                    line_id.sudo().portal_onchange_shipment_type()
                    values['success_edit_message'] = True
                except:
                    values['error_message'] = True
        if url:
            return werkzeug.utils.redirect(_build_url_w_params(url, values))

        return http.request.redirect('/my/home/')

    @http.route('/shipment/delete/', auth='user', website=True)
    def cargo_sale_order_line_delete(self, **kw):
        values = {}
        url = False
        if kw.get('order_id'):
            order_id = request.env['bsg_vehicle_cargo_sale'].sudo().search(
                [('id', '=', kw.get('order_id'))])
            url = order_id.sudo().get_portal_url()
        if kw.get('order_line_id'):
            line_id = request.env['bsg_vehicle_cargo_sale_line'].sudo().search(
                [('id', '=', kw.get('order_line_id'))])
            if line_id.bsg_cargo_sale_id.state != 'draft':
                values['delete_error_message'] = True
            else:
                try:
                    line_id.sudo().unlink()
                    values['success_delete_message'] = True
                except:
                    values['error_message'] = True
        if url:
            return werkzeug.utils.redirect(_build_url_w_params(url, values))
        return http.request.redirect('/my/home/')


    @http.route('/shipment/cancel/', auth='user', website=True)
    def cargo_sale_order_cancel(self, **kw):
        values = {}
        url = False
        if kw.get('order_id'):
            try:
                bsg_cargo_sale_id = request.env['bsg_vehicle_cargo_sale'].sudo().search(
                    [('id', '=', kw.get('order_id'))])
                url = bsg_cargo_sale_id.sudo().get_portal_url()
                if bsg_cargo_sale_id.invoice_ids:
                    if bsg_cargo_sale_id.invoice_ids.filtered(lambda s:s.state == 'paid' and s.payment_ids):
                        for line in bsg_cargo_sale_id.order_line_ids:
                            line.sudo().write({'state': 'cancel_request'})
                            if line.bsg_cargo_sale_id.receiver_mob_country_code and line.bsg_cargo_sale_id.receiver_mob_no:
                                number = str(line.bsg_cargo_sale_id.receiver_mob_country_code+line.bsg_cargo_sale_id.receiver_mob_no)
                                sms_msg = f" عميلنا العزيز، تم استلام طلبكم إلغاء إتفاقية شحن رقم {line.sale_line_rec_name} إلى {line.loc_to.loc_branch_id.branch_ar_name and line.loc_to.loc_branch_id.branch_ar_name or line.loc_to.loc_branch_id.branch_name} ، نسعد بخدمتكم"
                                self.send_sms(number,sms_msg)
                        bsg_cargo_sale_id.sudo().write({'state': 'cancel_request','cancel_reason':kw.get('cancel_reason')})
                    else:
                        for data in bsg_cargo_sale_id.invoice_ids.filtered(lambda s:s.state != 'paid'):
                            data.sudo().action_invoice_cancel()
                        for data in bsg_cargo_sale_id.invoice_ids.filtered(lambda s:s.state == 'paid' and not s.payment_ids):
                            if bsg_cargo_sale_id.refund_invoice_ids:
                                for refund_inv in bsg_cargo_sale_id.refund_invoice_ids:
                                    refund_inv.sudo().action_invoice_cancel()
                                data.sudo().action_invoice_cancel()
                        for line in bsg_cargo_sale_id.order_line_ids:
                            line.sudo().write({'state': 'cancel'})
                        bsg_cargo_sale_id.sudo().write({'state': 'cancel','cancel_reason':kw.get('cancel_reason')})
                else:
                    for line in bsg_cargo_sale_id.order_line_ids:
                            line.sudo().write({'state': 'cancel'})
                    bsg_cargo_sale_id.sudo().write({'state': 'cancel','cancel_reason':kw.get('cancel_reason')})
                values['success_cancel_message'] = True
            except:
                values['error_message'] = True
        if url:
            return werkzeug.utils.redirect(_build_url_w_params(url, values))
        return http.request.redirect('/my/home/')



    @http.route('/shipment/upgrade/', auth='user', website=True)
    def cargo_sale_order_upgrade(self, **kw):
        values = {}
        url = False
        #>>>>>>>>>>> {'597432': 'on', '597433': 'on', 'order_id': '355454', 'shipment_type': '8'}

        if kw.get('order_id'):
            try:
                lines = []
                for k in kw.keys():
                    if kw[k] == 'on':
                        lines.append(k)
                bsg_cargo_sale_id = request.env['bsg_vehicle_cargo_sale'].sudo().search(
                    [('id', '=', kw.get('order_id'))])
                url = bsg_cargo_sale_id.sudo().get_portal_url()
                if bsg_cargo_sale_id.state == 'draft':
                    for so_line in lines:
                        sale_line_id = request.env['bsg_vehicle_cargo_sale_line'].sudo().search([('id', '=', so_line)])
                        sale_line_id.sudo().write({'shipment_type': kw.get('shipment_type')})
                        sale_line_id.sudo().portal_onchange_shipment_type()
                    values['success_upgrade_message'] = True
            except:
                values['error_message'] = True
        if url:
            return werkzeug.utils.redirect(_build_url_w_params(url, values))
        return http.request.redirect('/my/home/')

    @http.route('/shipment/confirm/', auth='user', website=True)
    def cargo_sale_order_confrim(self, **kw):
        values = {}
        url = False
        if kw.get('order_id'):
            try:
                bsg_cargo_sale_id = request.env['bsg_vehicle_cargo_sale'].sudo().search(
                    [('id', '=', kw.get('order_id'))])
                url = bsg_cargo_sale_id.sudo().get_portal_url()
                if bsg_cargo_sale_id.state == 'draft' and bsg_cargo_sale_id.payment_method.payment_type == 'credit':
                        bsg_cargo_sale_id.sudo()._amount_all()
                        bsg_cargo_sale_id.sudo()._amount_so_all()
                        bsg_cargo_sale_id.sudo().confirm_btn()
                        values['success_confirm_message'] = True
            except:
                values['error_message'] = True
        if url:
            return werkzeug.utils.redirect(_build_url_w_params(url, values))
        return http.request.redirect('/my/home/')


    # @http.route('/shipment/order_edit/', auth='user',method='post', website=True)
    # def cargo_sale_order_edit(self, **kw):
    #     values = {}
    #     url = False
    #     if kw.get('order_id'):
    #         try:
    #             bsg_cargo_sale_id = request.env['bsg_vehicle_cargo_sale'].sudo().search(
    #                 [('id', '=', kw.get('order_id'))])
    #             url = bsg_cargo_sale_id.sudo().get_portal_url()
    #             if bsg_cargo_sale_id.state not in ['done','cancel']:
    #                 if kw.get('shipment_date',False):
    #                     try:
    #                         kw['shipment_date'] = self.datetime_cus(kw.get('shipment_date'))
    #                     except:
    #                         kw['shipment_date'] = odoo_fields.Datetime.now()
    #                 try:
    #                     del kw['order_id']
    #                     bsg_cargo_sale_id.sudo().write(kw)
    #                     #Update Prices
    #                     if kw.get('shipment_type'):
    #                         for so_line in bsg_cargo_sale_id.order_line_ids:
    #                             try:
    #                                 so_line.sudo().portal_onchange_shipment_type()
    #                             except:
    #                                 so_line.sudo().unlink()
    #                     values['success_edit_message'] = True
    #                 except:
    #                     values['error_message'] = True
    #         except:
    #             values['error_message'] = True
    #     if url:
    #         return werkzeug.utils.redirect(_build_url_w_params(url, values))
    #     return http.request.redirect('/my/home/')


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


class PortalVehicleSale(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PortalVehicleSale, self)._prepare_portal_layout_values()
        company = request.website.company_id
        vehicle_order_count = request.env['bsg_vehicle_cargo_sale'].sudo().search_count(
            [('customer', '=', request.env.user.partner_id.id), ('company_id', '=', company.id)])
        values['vehicle_order_count'] = vehicle_order_count
        return values

    def _prepare_portal_layout_values_so_lines(self):
        values = super(PortalVehicleSale, self)._prepare_portal_layout_values()
        company = request.website.company_id
        vehicle_order_count = request.env['bsg_vehicle_cargo_sale_line'].sudo().search_count(
            [('customer_id', '=', request.env.user.partner_id.id), ('company_id', '=', company.id)])
        values['vehicle_order_count'] = vehicle_order_count
        return values

    # ------------------------------------------------------------
    # My Shipment
    # ------------------------------------------------------------

    def _shipment_get_page_view_values(self, shipment, access_token, **kwargs):
        values = {
            'page_name': 'shipment',
            'shipment': shipment,
        }
        line_values = self._get_order_line_fields(values['shipment'])

        values = {**values, **line_values}
        if values['shipment'].state in ['draft']:
            upgrade_values = self._get_order_available_upgrade(values['shipment'])
            values['upgrade_values'] = upgrade_values
        return self._get_page_view_values(shipment, access_token, values, 'my_shipment_history', False, **kwargs)

    @http.route(['/my/shipments', '/my/shipments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_shipments(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        company = request.website.company_id
        #if not company.portal_create_individual_order:
        #    return http.request.redirect('/my/home/')
        CargoSale = request.env['bsg_vehicle_cargo_sale'].sudo()

        domain = []
        if not request.env.user.has_group('portal_sales.group_online_show_all_agreement'):
            domain = [('customer', '=', request.env.user.partner_id.id),
                    ('company_id', '=', company.id)]


        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'order_date desc'},
            'duedate': {'label': _('Amount'), 'order': 'total_so_amount desc'},
            'name': {'label': _('Number'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups(
            'bsg_vehicle_cargo_sale', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # count for pager
        shipment_count = CargoSale.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/shipments",
            url_args={'date_begin': date_begin,
                      'date_end': date_end, 'sortby': sortby},
            total=shipment_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        shipments = CargoSale.search(
            domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_shipment_history'] = shipments.ids[:100]

        values.update({
            'date': date_begin,
            'shipments': shipments,
            'page_name': 'shipment',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/shipments',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'is_cargo': True
        })
        return request.render("portal_sales.portal_my_shipments", values)

    @http.route(['/my/shipmentlines', '/my/shipmentlines/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_shipmentlines(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values_so_lines()
        company = request.website.company_id
        # if not company.portal_create_individual_order:
        #    return http.request.redirect('/my/home/')
        CargoSaleLine = request.env['bsg_vehicle_cargo_sale_line'].sudo()

        domain = []
        if not request.env.user.has_group('portal_sales.group_online_show_all_agreement'):
            domain = [('customer_id', '=', request.env.user.partner_id.id),
                      ('company_id', '=', company.id)]

        # searchbar_sortings = {
        #     'date': {'label': _('Order Date'), 'order': 'order_date desc'},
        #     'duedate': {'label': _('Amount'), 'order': 'total_so_amount desc'},
        #     'name': {'label': _('Number'), 'order': 'name desc'},
        #     'state': {'label': _('Status'), 'order': 'state'},
        # }
        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'order_date desc'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups(
            'bsg_vehicle_cargo_sale_line', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # count for pager
        shipment_count = CargoSaleLine.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/shipmentlines",
            url_args={'date_begin': date_begin,
                      'date_end': date_end, 'sortby': sortby},
            total=shipment_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        shipments = CargoSaleLine.search(
            domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_shipment_history'] = shipments.ids[:100]

        values.update({
            'date': date_begin,
            'shipments': shipments,
            'page_name': 'shipment',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/shipmentlines',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'is_cargo': True
        })
        return request.render("portal_sales.portal_my_shipmentlines", values)

    @http.route(['/my/shipments/<shipment_id>'], type='http', auth="public", website=True)
    def portal_my_shipments_detail(self, shipment_id, access_token=None, report_type=None, download=False, **kw):
        # try:
        #    shipment_sudo = self._document_check_access('bsg_vehicle_cargo_sale', shipment_id, access_token)
        # except (AccessError, MissingError):
        #    return request.redirect('/my')

        shipment_sudo = request.env['bsg_vehicle_cargo_sale'].sudo().search(
            [('id', '=', shipment_id)])

        values = self._shipment_get_page_view_values(
            shipment_sudo, access_token, **kw)
        values['error_message'] = kw.get('error_message')
        values['success_create_message'] = kw.get('success_create_message')
        return request.render("portal_sales.shipment_order_details", values)

    @http.route(['/my/shipments/new/<shipment_id>'], type='http', auth="public", website=True)
    def portal_my_shipments_new_detail(self, shipment_id, access_token=None, report_type=None, download=False, **kw):
        # try:
        #    shipment_sudo = self._document_check_access('bsg_vehicle_cargo_sale', shipment_id, access_token)
        # except (AccessError, MissingError):
        #    return request.redirect('/my')

        shipment_sudo = request.env['bsg_vehicle_cargo_sale'].sudo().search(
            [('id', '=', shipment_id), ('customer', '=', request.env.user.partner_id.id)])

        values = self._shipment_get_page_view_values(
            shipment_sudo, access_token, **kw)
        values['new'] = True

        return request.render("portal_sales.shipment_order_details", values)

    def _get_order_line_fields(self, bsg_cargo_sale_id):

        #Basic Field###########################################################
        company = request.website.company_id
        nationality_ids = request.env['res.country'].sudo().search([('visible_on_mobile_app','=',True)])
        default_country = request.env['res.country'].sudo().search(
            [('code', '=', 'SA'), ('phone_code', '=', '966')], limit=1).id
        loc_from_ids = request.env['bsg_route_waypoints'].sudo().search(
            [('company_id', '=', company.id),('branch_type','!=',False),
            ('loc_branch_id','!=',False),('branch_type','in',['shipping','both']),('visible_on_mobile_app','=',True)])
        loc_to_ids = request.env['bsg_route_waypoints'].sudo().search(
            [('company_id', '=', company.id),('branch_type','!=',False),
            ('loc_branch_id','!=',False),('branch_type','in',['pickup','both']),('visible_on_mobile_app','=',True)])
        return_loc_ids = request.env['bsg_route_waypoints'].sudo().search(
            [('company_id', '=', company.id),('branch_type','!=',False),('loc_branch_id','!=',False),('visible_on_mobile_app','=',True)])
        shipment_types = request.env['bsg.car.shipment.type'].sudo().search(
            [('company_id', '=', company.id),('is_public','=',True)])
        car_makes = request.env['bsg_car_config'].sudo().search([])
        car_models = request.env['bsg_car_model'].sudo().search([])
        years = request.env['bsg.car.year'].sudo().search([])
        car_colors = request.env['bsg_vehicle_color'].sudo().search([])
        palte_letter = [('أ', 'أ'), ('ب', 'ب'), ('ح', 'ح'), ('د', 'د'),
                        ('ر', 'ر'), ('س', 'س'), ('ص', 'ص'), ('ط', 'ط'),
                        ('ع', 'ع'), ('ق', 'ق'), ('ك', 'ك'), ('ل', 'ل'),
                        ('م', 'م'), ('ن', 'ن'), ('ه', 'هـ'), ('و', 'و'), ('ى', 'ى')]
        plate_types = request.env['bsg_plate_config'].sudo().search([])
        plate_registrations = [
            ('saudi', 'لوحة سعودية'), ('non-saudi', 'لوحة أخرى '), ('new_vehicle', 'بدون لوحة')]
        customer_price_lists = request.env['product.pricelist'].sudo().search([
        ])
        default_customer_price_list = request.env['product.pricelist'].sudo().search(
            [('default_in_portal', '=', True),'|', ('agreement_type', '=', False), ('agreement_type', '=', bsg_cargo_sale_id.shipment_type)], limit=1)
        if not default_customer_price_list or bsg_cargo_sale_id.loc_from.is_international or bsg_cargo_sale_id.loc_to.is_international or bsg_cargo_sale_id.payment_method.payment_type == 'credit':
            default_customer_price_list = request.env['product.pricelist'].sudo().search(
                [('is_public', '=', True)], limit=1)

        types = [('none', 'None'), ('pickup', 'pickup'),
                 ('delivery', 'delivery'), ('both', 'Both')]
        #End Of Basic Field###########################################################################

        #Computed And Other Field#####################################################################
        car_sizes = request.env['bsg_car_size'].sudo().search([])
        #fields.Many2one(string="Car Size",store=True, comodel_name="bsg_car_size", compute="_get_car_size")
        service_types = company.sudo().portal_service_ids
        default_cargo_service_id = company.sudo().cargo_service_id
        #ِAdd Discount
        discount = 0.0
        if default_customer_price_list and default_cargo_service_id:
            if default_customer_price_list.item_ids:
                for data in default_customer_price_list.item_ids:
                    if data.product_tmpl_id.id == default_cargo_service_id.id:
                        discount = data.percent_price
        ##############
        #End Of Computed Field########################################################################
        # Get Default Taxes:
        if bsg_cargo_sale_id.loc_from.is_international or bsg_cargo_sale_id.loc_to.is_international:
            default_tax_ids = []
        else:
            PinConfig = request.website.company_id.sudo()
            default_tax_ids = PinConfig.sudo().tax_ids.ids or company.sudo().cargo_service_id.taxes_id.ids
            default_tax_ids = []

        ##TODO: Filter PriceList By Same Way in the Odoo Backend,Pass This Domain in Search
        ##TODO: But Problem Come With shipment_type , Need To Do it In Javascript
        '''domain = ['|', ('location_domain', '!=', True), '|', ('loc_from_ids', '=', False), ('loc_from_ids', 'in', bsg_cargo_sale_id.loc_from.id),
                            '|', ('loc_to_ids', '=', False), ('loc_to_ids',
                                                                'in', bsg_cargo_sale_id.loc_to.id),
                            '|', ('partner_types', '=', False), ('partner_types',
                                                                'in', bsg_cargo_sale_id.partner_types.id),
                            '|', ('shipment_type', '=', False), ('shipment_type',
                                                                'in', shipment_type.id),
                            '|', ('date_from', '=', False), ('date_from',
                                                            '<=', bsg_cargo_sale_id.order_date),
                            '|', ('date_to', '=', False), ('date_to',
                                                            '>=', bsg_cargo_sale_id.order_date),
                            '|', ('agreement_type', '=', False), ('agreement_type', '=', bsg_cargo_sale_id.shipment_type)]'''

        line_values = {
            'shipment_types': shipment_types,
            'car_makes': car_makes,
            'car_models': car_models,
            'years': years,
            'car_colors': car_colors,
            'palte_letter': palte_letter,
            'plate_types': plate_types,
            'plate_registrations': plate_registrations,
            'customer_price_lists': customer_price_lists,
            'types': types,
            'car_sizes': car_sizes,
            'service_types': service_types,
            'default_cargo_service_id': default_cargo_service_id.id,
            'default_customer_price_list': default_customer_price_list.id,
            'default_tax_ids': default_tax_ids,
            'default_lang': request.env.context.get('lang') or 'en_US',
            'loc_from_ids': loc_from_ids,
            'loc_to_ids': loc_to_ids,
            'return_loc_ids':return_loc_ids,
            'sender_type': [('1', _('Saudi')), ('2', _('Non-Saudi')), ('3', _('Corporate'))],
            'sender_id_type': [('saudi_id_card', _('Saudi ID Card')), ('iqama', _('Iqama')), ('gcc_national', _('GCC National')),
                               ('passport', _('Passport')), ('other', _('Other'))],
            'nationality_ids': nationality_ids,
            'default_country': default_country,
            'discount':discount,
            'error': {},
            'error_message': [],
        }
        return line_values

    def _get_archive_groups(self, model, domain=None, fields=None, groupby="create_date", order="create_date desc"):
        if not model:
            return []
        if domain is None:
            domain = []
        if fields is None:
            fields = ['name', 'create_date']
        groups = []
        for group in request.env[model].sudo()._read_group_raw(domain, fields=fields, groupby=groupby, orderby=order):
            dates, label = group[groupby]
            date_begin, date_end = dates.split('/')
            groups.append({
                'date_begin': odoo_fields.Date.to_string(odoo_fields.Date.from_string(date_begin)),
                'date_end': odoo_fields.Date.to_string(odoo_fields.Date.from_string(date_end)),
                'name': label,
                'item_count': group[groupby + '_count']
            })
        return groups

    def _get_order_available_upgrade(self, bsg_cargo_sale_id):

        #Basic Field###########################################################
        upgrade_prices = []
        company = request.website.company_id
        shipment_types = request.env['bsg.car.shipment.type'].sudo().search(
            [('company_id', '=', company.id),('available_in_upgrade','=',True)])
        if shipment_types:
            for ship_type in shipment_types:
                price = []
                ship_line_price = []
                for line in bsg_cargo_sale_id.order_line_ids.filtered(lambda s:s.shipment_type.id != ship_type.id):
                    line_price = line.get_price_for_portal(ship_type.id,line.car_model.id,line.car_size.id,line.service_type.id,line.car_classfication.id,bsg_cargo_sale_id.id)
                    if len(line_price.get('error')) > 0 or line_price.get('charges',False) <= 0:
                            continue
                    elif line_price.get('charges',False) and line_price.get('charges',False) and line_price.get('charges') > line.charges:
                        del line_price['error']
                        price.append(line_price)
                        ship_line_price.append({
                            'line_id' : line,
                            'diff_price' : line_price['charges'] - line.charges
                        })
                    else:
                        continue
                if len(price) > 0 :
                    # sum the values with same keys,When More Than One Line
                    result = dict(functools.reduce(operator.add,
                            map(collections.Counter, price)))
                    upgrade_prices.append({
                        'upgrade_id' : ship_type.id ,
                        'upgrde_description_ids': ship_type.website_description_ids and ship_type.website_description_ids or False,
                        'upgrade_name' : ship_type.car_shipment_name,
                        'upgrade_price' : result,
                        'line_prices' : ship_line_price,
                        'total_diff_price' : sum([s['diff_price'] for s in ship_line_price]),
                                })
        return upgrade_prices
