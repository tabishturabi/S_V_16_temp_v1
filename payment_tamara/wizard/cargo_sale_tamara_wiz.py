# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import json
from odoo import api, fields, models, _
import requests
from odoo.exceptions import UserError, ValidationError
import time
from odoo.http import request

_logger = logging.getLogger(__name__)


class CargoSaleLineTamaraWiz(models.TransientModel):
    _name = "cargo.sale.tamara.wiz"
    _description = "Cargo Sale Line Tamara Wizard"

    @api.model
    def default_get(self, fields):
        res = super(CargoSaleLineTamaraWiz, self).default_get(fields)
        sale_id = self.env.context.get('active_id')
        cargo_sale = self.env['bsg_vehicle_cargo_sale'].browse(sale_id)
        res.update({'is_tamara_checkout': cargo_sale.is_tamara_checkout,
                    'is_tamara_call_second': cargo_sale.is_tamara_call_second,
                    'is_paid_by_tamra': cargo_sale.is_paid_by_tamra,
                    'amount': cargo_sale.total_amount,
                    'cargo_sale_id': cargo_sale.id,
                    'currency_id': cargo_sale.currency_id.id})
        return res

    amount = fields.Monetary(string='Total Amount')
    mobile = fields.Char(string='Mobile')
    order_id = fields.Char(string='Order id')
    url = fields.Char(string='Url', default='https://checkout-sandbox.tamara.co/checkout/')
    currency_id = fields.Many2one('res.currency', string="Currency", track_visibility=True)
    cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale', string="Cargo Sale")
    result = fields.Text(string="Result")
    card_details = fields.Text(string="Test Card Details", default="Card No. 4242 4242 4242 4242 --- Expiry Date. 01/99 ------- CVV. 100")
    is_paid_by_tamra = fields.Boolean("Tamara Paid",default=False)
    is_tamara_checkout = fields.Boolean("Tamara Checkout Sent",default=False)
    sender_mob_country_code = fields.Selection([('966', '966'), ('971', '+971'), ('962', '+962'), ('968', '+968')],
                                               string='Sender Mobile Code', default='966')
    is_tamara_call_second = fields.Boolean("Tamara Call Second")
    tamara_payment_sms_mobile_no = fields.Char('Tamara Payment SmS Mobile No.', readonly=True)
    
    def pay_via_tamara(self):
        tamara_acquirer = request.env.ref('payment_tamara.tamara_payment_connect', False)
        if not tamara_acquirer.tamara_instore_header:
            raise ValidationError(_('Please set authorization token on Tamara payment acquirer'))
        if not tamara_acquirer.tamara_instore_api_end:
            raise ValidationError(_('Please set instore end api call on Tamara payment acquirer'))
        if self.mobile and len(self.mobile) > 0:
            if len(self.mobile) != 9:
                raise ValidationError(_('Type customer mobile# in this format 966xxxxxxxxx (example 966555123456)'))
        tot_amount = sum(self.env['account.move'].search(
            [('move_type', '=', 'out_invoice'), ('payment_state', '!=', 'paid'), ('cargo_sale_id', '=', self.cargo_sale_id.id)]).mapped('amount_residual'))
        if tot_amount < 100 or tot_amount > 2000:
            raise ValidationError(_("Amount should be greater than 100 or less than 2000 to pay via Tamara"))

        HEADERS = {
            'Authorization': 'Bearer ' + tamara_acquirer.tamara_instore_header,
            'Content-Type': 'application/json',
        }
        items_list = []
        for rec in self.cargo_sale_id.order_line_ids:
            items_list.append({
                    "reference_id": rec.sale_line_rec_name,
                    "type": rec.type,
                    "name": rec.display_name,
                    "sku": rec.service_type_name,
                    "image_url": "https://www.example.com/product.jpg",
                    "quantity": 1,
                    "unit_price": {
                        "amount": str(rec.charges),
                        "currency": "SAR"
                    },
                    "discount_amount": {
                        "amount": str(rec.discount_price),
                        "currency": "SAR"
                    },
                    "tax_amount": {
                        "amount": str(rec.tax_amount),
                        "currency": "SAR"
                    },
                    "total_amount": {
                        "amount": str(rec.final_price),
                        "currency": "SAR"
                    }
                })
        vals = {
            "total_amount": {
                "amount": str(tot_amount),
                "currency": "SAR"
            },
            "phone_number": self.mobile,
            "order_reference_id": str(self.cargo_sale_id.id),
            "order_number": str(self.cargo_sale_id.name),
            "payment_type": "PAY_BY_INSTALMENTS",
            "items":items_list,
                "additional_data": {
                "store_code": "Store code A"
            },
            "locale": "ar_SA"
        }
        response = requests.post(url=tamara_acquirer.tamara_instore_api_end, headers=HEADERS,
                                 data=json.dumps(vals))
        _logger.info("Tamara A")

        if response.status_code == 200:
            if not self.cargo_sale_id.is_tamara_checkout and not self.cargo_sale_id.is_tamara_call_second:
                self.cargo_sale_id.is_tamara_checkout = True
            else:
                self.cargo_sale_id.is_tamara_call_second = True
            self.cargo_sale_id.tamara_payment_sms_mobile_no = self.mobile
            json_data = json.loads(response.text)
            _logger.info(json_data.get('order_id'))
            _logger.info(json_data.get('checkout_id'))
            print(json_data.get('checkout_id'))
            # timeout = time.time() + 60 * 50  # 5 minutes from now
            # number = '966' + str(self.mobile)
            # sms_msg = " عزيزي العميل استخدم الرابط التالي لإكمال الدفع بواسطة تمارا "+"https://checkout-sandbox.tamara.co/checkout/"+json_data.get('checkout_id')
            # self.send_sms_tamara(number, sms_msg)
            # while True:
            #     test = 0
            #     if test == 5 or time.time() > timeout:
            #         break
            #     test = test - 1
            #     _logger.info("Tamara C")
            # get_order_response = requests.get(
                # url="https://api-sandbox.tamara.co/orders/" + json_data.get('order_id'), headers=HEADERS)
            # if get_order_response.status_code == 200:
            #     return_obj = json.loads(get_order_response.text)
            #     if return_obj.get('status') == 'fully_captured':
            #         self.cargo_sale_id.is_paid_by_tamra = True
            #         print("Success")
            #         vals_payment = self.cargo_sale_id.register_payment_tamara_instore()
            #         tamara_acquirer = self.env.ref('payment_tamara.tamara_payment_connect', False)
            #         if tamara_acquirer:
            #             vals_payment['journal_id'] = tamara_acquirer.journal_id.id
            #         else:
            #             vals_payment['journal_id'] = 724
            #         vals_payment['payment_method_id'] = 1
            #         payment_id = self.env['account.payment'].create(vals_payment)
            #         payment_id._oncahnge_journal_destination()
            #         payment_id.operation_number = "Tamara test"
            #         payment_id.action_validate_invoice_payment()
            #         return {
            #                 'type': 'ir.actions.act_window',
            #                 'name': 'Success Wizard',
            #                 'view_mode': 'form',
            #                 'view_type': 'form',
            #                 'res_model': 'cargo.sale.tamara.wiz',
            #                 'target': 'new',
            #                 'view_id': self.env.ref('payment_tamara.cargo_sale_tamara_wiz_success').id,
            #
            #             }
            # else:
            #     _logger.error("%s", str(response.text or response))
        else:
            _logger.error("%s", str(response.text or response))

    
    def check_status(self):
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def send_sms_tamara(self, rendered_sms_to, sms_rendered_content):
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
