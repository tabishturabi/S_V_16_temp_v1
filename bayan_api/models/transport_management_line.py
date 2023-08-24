from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError
from datetime import datetime
import logging
import json
import requests

from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)

class TransportManagementLine(models.Model):
    _inherit = 'transport.management.line'

    waybill_id = fields.Char(string='Bayan Waybill ID', related="transport_bayan_way_bill_line_id.waybill_id")
    bayan_config_active = fields.Boolean(string="Is Bayan Config Active", compute="_compute_baya_config_id")
    transport_bayan_way_bill_line_id = fields.Many2one('way.bill.line', track_visibility=True, string="Way Bill ID")
    way_bill_line_state = fields.Selection([('closed', 'Closed'), ('cancelled', 'Cancelled')],
                                           string="Bayan Status", track_visibility=True,
                                           related='transport_bayan_way_bill_line_id.state')
    transport_bayan_goods_type_id = fields.Many2one('bayan.good.type.config', track_visibility=True, string="Goods Type")


    
    def action_close_waybill(self):
        bayan_config = self.env.ref('bayan_api.bayan_config_settings_data')
        if bayan_config and bayan_config.is_transport:
            if self.waybill_id:
                bayan_config_settings = self.env.ref('bayan_api.bayan_config_settings_data')
                headers = {'app_id': bayan_config_settings.bayan_app_id, 'app_key': bayan_config_settings.bayan_app_key,
                           'client_id': bayan_config_settings.bayan_client_id,
                           'Content-Type': 'application/json'}
                api_end = bayan_config_settings.bayan_live_url + '/api/v1/carrier/trip/waybill/close'
                actualDeliveryDate = datetime.now() + relativedelta(days=4)
                actualDeliveryDate = actualDeliveryDate.strftime('%Y-%m-%d')
                request_data_dynamic = {
                    "waybillId": int(self.waybill_id),
                    "actualDeliveryDate": actualDeliveryDate
                }
                response = requests.put(url=api_end, headers=headers, data=json.dumps(request_data_dynamic))
                if response.status_code == 200:
                    self.bayan_way_bill_line_id.write({'state': 'closed'})
                else:
                    _logger.warning("Close WayBill Response : " + str(response.text or response))

    
    def action_update_waybill(self):
        print("adaqd")
        bayan_config_settings = self.env.ref('bayan_api.bayan_config_settings_data')
        HEADERS = {
            'app_id': bayan_config_settings.bayan_app_id, 'app_key': bayan_config_settings.bayan_app_key,
            'client_id': bayan_config_settings.bayan_client_id,
            'Content-Type': 'application/json',
        }
        api_end = bayan_config_settings.bayan_live_url + "/api/v1/carrier/trip/waybill"
        if self.waybill_id:
            main_way_bill_dict = {}
            main_way_bill_dict["waybillId"] = int(self.waybill_id)
            sender_country_code = self.bsg_cargo_sale_id.sender_nationality.code or 'SA'
            sender_city_id = self.loc_from.region_city_id.bayan_city_id
            sender_address = self.loc_from.route_waypoint_name
            receiver_name = self.bsg_cargo_sale_id.receiver_name
            receiver_phone = "+" + self.bsg_cargo_sale_id.receiver_mob_country_code + self.bsg_cargo_sale_id.receiver_mob_no
            receiver_country_code = self.bsg_cargo_sale_id.receiver_nationality.code or 'SA'
            receiver_city_id = self.loc_to.region_city_id.bayan_city_id
            receiver_address = self.loc_to.route_waypoint_name
            receiving_loc_country_code = self.bsg_cargo_sale_id.receiver_nationality.code or 'SA'
            receiving_loc_city_id = self.loc_from.region_city_id.bayan_city_id
            receiving_loc_address = self.loc_from.route_waypoint_name
            delivery_loc_country_code = self.bsg_cargo_sale_id.sender_nationality.code or 'SA'
            delivery_loc_city_id = self.loc_to.region_city_id.bayan_city_id
            delivery_loc_address = self.loc_to.route_waypoint_name
            if self.bsg_cargo_sale_id.sender_mob_no and self.bsg_cargo_sale_id.sender_mob_country_code:
                sender_phone = "+" + self.bsg_cargo_sale_id.sender_mob_country_code + self.bsg_cargo_sale_id.sender_mob_no
            else:
                sender_phone = "+" + self.bsg_cargo_sale_id.receiver_mob_country_code + self.bsg_cargo_sale_id.receiver_mob_no
            main_way_bill_dict["sender"] = {"name": self.bsg_cargo_sale_id.sender_name, "phone": sender_phone,
                                            "countryCode": sender_country_code,
                                            "cityId": sender_city_id,
                                            "address": sender_address}
            main_way_bill_dict["recipient"] = {"name": receiver_name, "phone": receiver_phone,
                                               "countryCode": receiver_country_code,
                                               "cityId": receiver_city_id, "address": receiver_address}
            main_way_bill_dict["items"] = [{
                "unitId": 1,
                "valid": True,
                "quantity": 1,
                "price": self.charges,
                "goodTypeId": 9,
                "weight": self.car_size.weight,
                "dimensions": str(self.car_size.car_size_len) + "*" + str(
                    self.car_size.car_size_width) + "*" + str(
                    self.car_size.car_size_height)}]
            main_way_bill_dict["deliverToClient"] = True
            main_way_bill_dict["fare"] = self.charges
            main_way_bill_dict["tradable"] = True
            main_way_bill_dict["paidBySender"] = True
            main_way_bill_dict["receivingLocation"] = {
                "countryCode": receiving_loc_country_code,
                "cityId": receiving_loc_city_id,
                "address": receiving_loc_address
            }
            main_way_bill_dict["deliveryLocation"] = {
                "countryCode": delivery_loc_country_code,
                "cityId": delivery_loc_city_id,
                "address": delivery_loc_address
            }
            try:
                response = requests.post(
                    url=api_end, headers=HEADERS, data=json.dumps(main_way_bill_dict))
                print(response)
                if response.status_code == 200:
                    print("asdfasdsad")

                else:
                    print("asdasdad")

            except Exception as e:
                _logger.warning(
                    "BAYAN Update WayBill API-----%r---------" % (e))
                raise UserError(e)