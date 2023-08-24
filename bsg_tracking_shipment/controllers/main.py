# -*- coding: utf-8 -*-
 
from odoo import fields, http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as df
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from datetime import datetime
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

class AuthSignupInherit(AuthSignupHome):
    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password', 'customer_id_card_no', 'phone') }
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

class TrackingShipment(http.Controller):
    
    @http.route(['/track-shipment'], type='http', auth="public", website=True)
    def TrackShip(self, message=None,so_id=None,rec_mo=None,default_captach_site=None, **kw):
        values = {}
        lang = 'en_US'
        # lang = request._context.get('lang')
        if lang == 'en_US':
            if so_id and rec_mo:
                cargo_line = request.env['bsg_vehicle_cargo_sale_line'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('sale_line_rec_name','=',so_id),('receiver_mob_no','in',[rec_mo, rec_mo[-9:]])],limit=1)
                if cargo_line:
                    values['shipment'] = cargo_line
                    #Add Payment Values
                    if cargo_line.getting_portal_due_amount():
                        
                        payment_inputs = request.env['payment.provider'].sudo().search([])
                        payment_inputs = payment_inputs[0]
                        # payment_inputs = request.env['payment.provider']._get_available_payment_input(company=cargo_line.bsg_cargo_sale_id.company_id)
                        # if not connected (using public user), the method _get_available_payment_input will return public user tokens
                        is_public_user = request.env.user._is_public()
                        if is_public_user:
                            # we should not display payment tokens owned by the public user
                            payment_inputs.pop('pms', None)
                            token_count = request.env['payment.token'].sudo().search_count([('acquirer_id.company_id', '=', cargo_line.bsg_cargo_sale_id.company_id.id),
                                                                                    ('partner_id', '=', cargo_line.bsg_cargo_sale_id.customer.id),
                                                                                    ])
                            values['existing_token'] = token_count > 0
                        # values.update(payment_inputs)
                        # if the current user is connected we set partner_id to his partner otherwise we set it as the invoice partner
                        # we do this to force the creation of payment tokens to the correct partner and avoid token linked to the public user
                        values['partner_id'] = cargo_line.bsg_cargo_sale_id.customer if is_public_user else request.env.user.partner_id
                    values['rec_name'] = cargo_line.receiver_name
                    values['recevier_mo'] = cargo_line.receiver_mob_no
                    
                    values['sale_id'] = cargo_line.sale_line_rec_name
                    x = cargo_line.order_date
                    if x:
                        values['ord_date'] = x.strftime('%d-%B-%Y')
                    values['order_date'] = cargo_line.order_date
                    values['loc_to'] = cargo_line.loc_to.route_waypoint_name
                    values['loc_from'] = cargo_line.loc_from.route_waypoint_name
                    values['customer_id'] = cargo_line.customer_id.name
                    values['expected_delivery'] = cargo_line.expected_delivery
                    values['car_model'] = cargo_line.car_model.car_model_name
                    values['year'] = cargo_line.year.car_year_name
                    values['loc_from'] = cargo_line.loc_from.route_waypoint_name
                    values['car_make'] = cargo_line.car_make.car_maker.car_make_ar_name
                    values['state'] = cargo_line.state
                    values['shipment_date'] = cargo_line.shipment_date
                    values['est_no_delivery_days'] = cargo_line.est_no_delivery_days
                    values['est_max_no_delivery_days'] = cargo_line.est_max_no_delivery_days
                    return request.render("bsg_tracking_shipment.track_shipment_details_view",{'values':values})
                else:
                    values.update({'message':'Something is Wrong'})
                    default_captach_site = request.env['ir.config_parameter'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_param('bsg_tracking_shipment.default_recaptcha_key_site')
                    default_captach_secret = request.env['ir.config_parameter'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_param('bsg_tracking_shipment.default_recaptcha_key_secret')
                    values['default_captach_site'] = default_captach_site
                    values['default_captach_secret'] = default_captach_secret
                    return request.render("bsg_tracking_shipment.track_shipment_view", values)
#                     return request.redirect('/track-shipment'+'?message=something is wrong')
            default_captach_site = request.env['ir.config_parameter'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_param('bsg_tracking_shipment.default_recaptcha_key_site')
            default_captach_secret = request.env['ir.config_parameter'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_param('bsg_tracking_shipment.default_recaptcha_key_secret')
            values['default_captach_site'] = default_captach_site
            values['default_captach_secret'] = default_captach_secret
            return request.render("bsg_tracking_shipment.track_shipment_view", values)
        elif lang == 'ar_AA':
            if so_id and rec_mo:
                cargo_line = request.env['bsg_vehicle_cargo_sale_line'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('sale_line_rec_name','=',so_id),('receiver_mob_no','in',[rec_mo, rec_mo[-9:]])],limit=1)
                if cargo_line:
                    values['shipment'] = cargo_line
                    #Add Payment Values
                    if cargo_line.getting_portal_due_amount():
                        
                        payment_inputs = request.env['payment.acquirer']._get_available_payment_input(company=cargo_line.bsg_cargo_sale_id.company_id)
                        # if not connected (using public user), the method _get_available_payment_input will return public user tokens
                        is_public_user = request.env.user._is_public()
                        if is_public_user:
                            # we should not display payment tokens owned by the public user
                            payment_inputs.pop('pms', None)
                            token_count = request.env['payment.token'].sudo().search_count([('acquirer_id.company_id', '=', cargo_line.bsg_cargo_sale_id.company_id.id),
                                                                                    ('partner_id', '=', cargo_line.bsg_cargo_sale_id.customer.id),
                                                                                    ])
                            values['existing_token'] = token_count > 0
                        values.update(payment_inputs)
                        # if the current user is connected we set partner_id to his partner otherwise we set it as the invoice partner
                        # we do this to force the creation of payment tokens to the correct partner and avoid token linked to the public user
                        values['partner_id'] = cargo_line.bsg_cargo_sale_id.customer if is_public_user else request.env.user.partner_id
                    values['rec_name'] = cargo_line.receiver_name
                    values['recevier_mo'] = cargo_line.receiver_mob_no
                    values['sale_id'] = cargo_line.sale_line_rec_name
                    x = cargo_line.order_date
                    if x:
                        values['ord_date'] = x.strftime('%d-%B-%Y')
                    values['order_date'] = cargo_line.order_date
                    values['loc_to'] = cargo_line.loc_to.route_waypoint_name
                    values['loc_from'] = cargo_line.loc_from.route_waypoint_name
                    values['customer_id'] = cargo_line.customer_id.name
                    values['expected_delivery'] = cargo_line.expected_delivery
                    values['car_model'] = cargo_line.car_model.car_model_name
                    values['year'] = cargo_line.year.car_year_name
                    values['loc_from'] = cargo_line.loc_from.route_waypoint_name
                    values['car_make'] = cargo_line.car_make.car_maker.car_make_ar_name
                    values['state'] = cargo_line.state
                    values['shipment_date'] = cargo_line.shipment_date
                    values['est_no_delivery_days'] = cargo_line.est_no_delivery_days
                    values['est_max_no_delivery_days'] = cargo_line.est_max_no_delivery_days
                    return request.render("bsg_tracking_shipment.track_shipment_ar_details_view",{'values':values})
                else:
                    values.update({'message':'هناك شئ غير صحيح'})
                    default_captach_site = request.env['ir.config_parameter'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_param('bsg_tracking_shipment.default_recaptcha_key_site')
                    default_captach_secret = request.env['ir.config_parameter'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_param('bsg_tracking_shipment.default_recaptcha_key_secret')
                    values['default_captach_site'] = default_captach_site
                    values['default_captach_secret'] = default_captach_secret
                    return request.render("bsg_tracking_shipment.track_shipment_view", values)
            default_captach_site = request.env['ir.config_parameter'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_param('bsg_tracking_shipment.default_recaptcha_key_site')
            default_captach_secret = request.env['ir.config_parameter'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_param('bsg_tracking_shipment.default_recaptcha_key_secret')
            values['default_captach_site'] = default_captach_site
            values['default_captach_secret'] = default_captach_secret
            return request.render("bsg_tracking_shipment.track_shipment_ar_view", values)
            
    
    @http.route(['/track-shipment/process'], type='http', auth="public",method=['post'], website=True,csrf_token=True)
    def TrackShipProcess(self, id=None, **kw):
        values = {}
        if kw.get('so_no') and kw.get('rec_mo'):
            return request.redirect('/track-shipment?so_id='+kw.get('so_no')+'&rec_mo='+kw.get('rec_mo'))


    @http.route(['/my/shipment/line/<line_id>'], type='http', auth="public", website=True)
    def SaleOrderLine(self, line_id=None, **kw):
        if line_id:
            cargo_line = request.env['bsg_vehicle_cargo_sale_line'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id','=',line_id)])
            return request.redirect('/track-shipment?so_id='+str(cargo_line.sale_line_rec_name)+'&rec_mo='+str(cargo_line.receiver_mob_no))
        else:
            return http.request.redirect('my/home/')

    @http.route(['/customer_info/process'], type='http', auth="user", website=True)
    def post_customer_info(self, message=None,default_captach_site=None, **kw):
        values = {}
        customer_keys = ['package_type','customer_name', 'customer_phone', 'customer_id_number', 'customer_email']
        # if all (key in kw.keys() for key in customer_keys):
        #     pass
        values = {
            'name': request.env.user.name,
            'phone': request.env.user.phone,
            'id_number': request.env.user.customer_id_card_no,
            'email':request.env.user.email,
            'package':kw.get('package_type', False)
        }
            # request.env['natinal.day.customer'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create(vals)
        lang = request._context.get('lang')
        if lang == 'en_US':               
            default_captach_site = request.env['ir.config_parameter'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_param('bsg_tracking_shipment.default_recaptcha_key_site')
            default_captach_secret = request.env['ir.config_parameter'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_param('bsg_tracking_shipment.default_recaptcha_key_secret')
            values['default_captach_site'] = default_captach_site
            values['default_captach_secret'] = default_captach_secret
            return request.render("bsg_tracking_shipment.customer_info_form_en", values)
        elif lang == 'ar_AA':
            default_captach_site = request.env['ir.config_parameter'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_param('bsg_tracking_shipment.default_recaptcha_key_site')
            default_captach_secret = request.env['ir.config_parameter'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_param('bsg_tracking_shipment.default_recaptcha_key_secret')
            values['default_captach_site'] = default_captach_site
            values['default_captach_secret'] = default_captach_secret
            return request.render("bsg_tracking_shipment.customer_info_form_ar", values)

    @http.route(['/package/payment'], type='http', auth="user", website=True)
    def package_payment_redirect(self, **kw):
        # customer_keys = ['package_type','customer_name', 'customer_phone', 'customer_id_number', 'customer_email']
        # vals = {
        #         'name': kw.get('customer_name', False),
        #         'phone': kw.get('customer_phone', False),
        #         'customer_id_card_no': kw.get('customer_id_number', False),
        #         'email': kw.get('customer_email','a@x.com'),
        #         'partner_types':17
        #     }
        partner_id = request.env.user.partner_id
        partner_id.partner_types = 17
        partner_id._onchange_partner_types()
        package = kw.get('package_type', '190_pack')
        if package == '190_pack':
            product_id = request.env['product.product'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('default_code', '=', 'pack_190')], limit=1)
        else:
            product_id = request.env['product.product'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('default_code', '=', 'pack_90')], limit=1)
        journal_id = request.env['account.invoice'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).default_get(['journal_id'])['journal_id']
        kw.get('package_type', False)
        invoice_vals = {
            'type': 'out_invoice',
            'parent_customer_id': partner_id.id,
            'partner_shipping_id': partner_id.id,
            'partner_id': partner_id.id,
            'journal_id': journal_id,
            'company_id': 1,
        }
        invocie_id = request.env['account.invoice'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).create(invoice_vals)
        invoice_line_vals = {
            'name': product_id.name,
            'product_id': product_id.id,
            'account_id': 4272,
            'price_unit': product_id.lst_price,
            'quantity': 1,
            'invoice_line_tax_ids': [(6, 0, product_id.taxes_id.ids)],
            'invoice_id': invocie_id.id,
        }
        request.env['account.invoice.line'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).create(invoice_line_vals)
        invocie_id.sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).compute_taxes()
        invocie_id.sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).action_invoice_open()
        url = invocie_id.sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).get_portal_url()
        return request.redirect(url)


    
