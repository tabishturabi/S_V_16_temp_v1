from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
import requests
import base64

_logger = logging.getLogger(__name__)


class BayanData(models.Model):
    _name = 'bayan.data'
    _inherit = ['mail.thread']
    _description = "Bayan Data"

    name = fields.Char(string='Name')
    identity_number = fields.Char(string='Identity Number')
    issue_number = fields.Integer(string='Issue Number')
    mobile = fields.Char(string='Mobile')
    rightLetter = fields.Selection([('ا', 'ا'),('أ', 'أ'), ('ب', 'ب'), ('ح', 'ح'), ('د', 'د'),
                                    ('ر', 'ر'), ('س', 'س'), ('ص', 'ص'), ('ط', 'ط'),
                                    ('ع', 'ع'), ('ق', 'ق'), ('ك', 'ك'), ('ل', 'ل'),
                                    ('م', 'م'), ('ن', 'ن'), ('ه', 'هـ'), ('و', 'و'), ('ى', 'ى')], track_visibility=True)
    middleLetter = fields.Selection([('ا', 'ا'),('أ', 'أ'), ('ب', 'ب'), ('ح', 'ح'), ('د', 'د'),
                                     ('ر', 'ر'), ('س', 'س'), ('ص', 'ص'), ('ط', 'ط'),
                                     ('ع', 'ع'), ('ق', 'ق'), ('ك', 'ك'), ('ل', 'ل'),
                                     ('م', 'م'), ('ن', 'ن'), ('ه', 'هـ'), ('و', 'و'), ('ى', 'ى')],
                                    track_visibility=True)
    leftLetter = fields.Selection([('ا', 'ا'),('أ', 'أ'), ('ب', 'ب'), ('ح', 'ح'), ('د', 'د'),
                                   ('ر', 'ر'), ('س', 'س'), ('ص', 'ص'), ('ط', 'ط'),
                                   ('ع', 'ع'), ('ق', 'ق'), ('ك', 'ك'), ('ل', 'ل'),
                                   ('م', 'م'), ('ن', 'ن'), ('ه', 'هـ'), ('و', 'و'), ('ى', 'ى')], track_visibility=True)
    plate_no = fields.Char(string="Bayan Plate No", size=4, track_visibility=True)
    expected_delivery_date = fields.Date(string='Exp delivery date', track_visibility=True)
    received_date = fields.Date(string='Received Date', track_visibility=True)
    way_bill_ids = fields.One2many('way.bill.line', 'parent_id', track_visibility='always',)
    plate_type_id = fields.Integer(string="Plate Type", track_visibility=True)
    tripId = fields.Char(string="Trip ID", track_visibility=True)
    state = fields.Selection([('draft', 'Draft'), ('success', 'Success'), ('failed', 'Failed')], track_visibility=True)
    bayan_ref = fields.Selection([('cargo_sale', 'Cargo Sale'), ('transport', 'Transport Management')], track_visibility=True)
    reason = fields.Char(string="Response", track_visibility=True)
    report_pdf_file_bin_url = fields.Binary("Binary for pdf live")
    sticker_no = fields.Many2one('fleet.vehicle', track_visibility=True)
    fleet_vehicle_trip = fields.Many2one('fleet.vehicle.trip', track_visibility=True)
    transport_management_id = fields.Many2one('transport.management', track_visibility=True)

    
    def action_get_bayan_pdf_v2(self):
        bayan_config_settings = self.env.ref('bayan_api.bayan_config_settings_data')
        headers = {'app_id': bayan_config_settings.bayan_app_id, 'app_key': bayan_config_settings.bayan_app_key,
                   'client_id': bayan_config_settings.bayan_client_id,
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        api_end = bayan_config_settings.bayan_live_url + '/api/v1/carrier/trip/' + self.tripId + '/print'
        response = requests.get(url=api_end, headers=headers)
        if response.status_code == 200:
            fin = base64.b64encode(response.content)
            self.report_pdf_file_bin_url = fin
            action = {
                'name': 'Bayan Trip PDF',
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=bayan.data&id=" + str(
                    self.id) + "&filename_field=name&field=report_pdf_file_bin_url&download=true&filename=" + self.name,
                'target': 'self',
            }
            return action
        else:
            raise UserError(_(str(response.text) + " Error code : " + str(response.status_code)))

    
    def get_waybill_ids(self, way_bill_lines):
        if len(way_bill_lines) > 0:
            way_bill_list = []
            main_way_bill_dict = {}
            for rec in way_bill_lines:
                main_way_bill_dict["sender"] = {"name": rec.sender_name, "phone": rec.sender_phone,
                                                "countryCode": rec.sender_country_code, "cityId": rec.sender_city_id,
                                                "address": rec.sender_address}
                main_way_bill_dict["recipient"] = {"name": rec.receiver_name, "phone": rec.receiver_phone,
                                                   "countryCode": rec.receiver_country_code,
                                                   "cityId": rec.receiver_city_id, "address": rec.receiver_address}
                main_way_bill_dict["items"] = [{
                    "unitId": rec.line_ids[0].unit_id,
                    "valid": rec.line_ids[0].valid,
                    "quantity": rec.line_ids[0].quantity,
                    "price": rec.line_ids[0].price,
                    "goodTypeId": rec.line_ids[0].good_type_id,
                    "weight": rec.line_ids[0].weight,
                    "dimensions": rec.line_ids[0].dimensions}]
                main_way_bill_dict["deliverToClient"] = rec.line_ids[0].deliver_to_client
                main_way_bill_dict["fare"] = rec.line_ids[0].price
                main_way_bill_dict["tradable"] = True
                main_way_bill_dict["paidBySender"] = True
                main_way_bill_dict["receivingLocation"] = {
                    "countryCode": rec.receiving_loc_country_code,
                    "cityId": rec.receiving_loc_city_id,
                    "address": rec.receiving_loc_address
                }
                main_way_bill_dict["deliveryLocation"] = {
                    "countryCode": rec.delivery_loc_country_code,
                    "cityId": rec.delivery_loc_city_id,
                    "address": rec.delivery_loc_address
                }

                way_bill_list.append(main_way_bill_dict)
            return way_bill_list

    
    def action_create_api(self):
        if self.mobile and len(self.mobile) != 13:
            raise UserError(_("The field mobile is incorrect its length should be 13"))
        if self.plate_type_id != 2:
            raise UserError(_("The field Plate Type is incorrect it should be be 2"))

        bayan_config_settings = self.env.ref('bayan_api.bayan_config_settings_data')
        request_data_dynamic = {
            "vehicle": {
                "plateTypeId": self.plate_type_id,
                "vehiclePlate": {
                    "rightLetter": self.rightLetter,
                    "middleLetter": self.middleLetter,
                    "leftLetter": self.leftLetter,
                    "number": self.plate_no
                }
            },
            "driver": {
                "identityNumber": self.identity_number,
                "issueNumber": self.issue_number,
                "mobile": self.mobile
            },
            "receivedDate": str(self.received_date),
            "expectedDeliveryDate": str(self.expected_delivery_date),
            "waybills": self.get_waybill_ids(self.way_bill_ids)
        }
        HEADERS = {
            'app_id': bayan_config_settings.bayan_app_id, 'app_key': bayan_config_settings.bayan_app_key,
            'client_id': bayan_config_settings.bayan_client_id,
            'Content-Type': 'application/json',
        }
        api_end = bayan_config_settings.bayan_live_url + "/api/v1/carrier/trip"

        try:
            response = requests.post(
                url=api_end, headers=HEADERS, data=json.dumps(request_data_dynamic))
            print(response)
            if response.status_code == 200:
                response_dict = response.json()
                if response_dict.get('tripId'):
                    self.tripId = response_dict.get('tripId')
                    self.name = response_dict.get('tripId')
                if response_dict.get('waybills'):
                    size = len(response_dict.get('waybills'))
                    for i in range(size):
                        self.way_bill_ids[i].write({'waybill_id': response_dict.get('waybills')[i]['waybillId']})

                self.state = 'success'
                self.reason = response.text

            else:
                self.reason = response.text or response
                self.state = 'failed'
                raise UserError(self.reason)

        except Exception as e:
            _logger.warning(
                "BAYAN Create API-----%r---------" % (e))
            raise UserError(e)

    
    def action_get_trip_details(self):
        print("asdadasd")
        bayan_config_settings = self.env.ref('bayan_api.bayan_config_settings_data')
        headers = {'app_id': bayan_config_settings.bayan_app_id, 'app_key': bayan_config_settings.bayan_app_key,
                   'client_id': bayan_config_settings.bayan_client_id,
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        api_end = bayan_config_settings.bayan_live_url + '/api/v1/carrier/trip/' + self.tripId
        response = requests.get(url=api_end, headers=headers)
        print(response.json())
        data = {'default_id': self.id, 'html_data': response.json()}
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'bayan.trip.details.wizard',
            'view_id': self.env.ref('bayan_api.wizard_bayan_trip_details_wizard_view').id,
            'view_mode': 'form',
            'context': data,
            'target': 'new',
        }


class BayanDataLine(models.Model):
    _name = 'bayan.data.line'

    bayan_id = fields.Many2one('way.bill.line', track_visibility=True)
    unit_id = fields.Integer(string='Unit Id', track_visibility=True)
    valid = fields.Boolean(string="Valid", track_visibility=True)
    quantity = fields.Integer(string="Qty", track_visibility=True)
    good_type_id = fields.Integer(string="Good Type ID", track_visibility=True)
    deliver_to_client = fields.Boolean(string="Deliver To Client", track_visibility=True)
    price = fields.Integer(string="Price", track_visibility=True)
    weight = fields.Integer(string="Weight", track_visibility=True)
    dimensions = fields.Char(string="Dimensions", track_visibility=True)
    dangerous_code = fields.Char(string="Dangerous Code", track_visibility=True)
    item_number = fields.Char(string="Item Number", track_visibility=True)


class WayBillLine(models.Model):
    _name = 'way.bill.line'

    line_ids = fields.One2many('bayan.data.line', 'bayan_id', track_visibility='always')
    parent_id = fields.Many2one('bayan.data', track_visibility=True)
    bsg_cargo_sale_line = fields.Many2one('bsg_vehicle_cargo_sale_line', string="Cargo Sale Line",
                                          track_visibility=True)
    transport_management_line = fields.Many2one('transport.management.line', string="Transport Management Line",track_visibility=True)
    sender_name = fields.Char(string='Sender Name')
    sender_phone = fields.Char(string='Sender Phone')
    sender_country_code = fields.Char(string='Sender Country Code')
    sender_city_id = fields.Integer(string='Sender City ID')
    sender_address = fields.Char(string='Sender Address')

    receiver_name = fields.Char(string='Receiver Name')
    receiver_phone = fields.Char(string='Receiver Phone')
    receiver_country_code = fields.Char(string='Receiver Code')
    receiver_city_id = fields.Integer(string='Receiver City ID')
    receiver_address = fields.Char(string='Receiver Address')

    fare = fields.Integer(string='Fare')
    tradable = fields.Boolean(string="Tradable", track_visibility=True)
    paid_by_sender = fields.Boolean(string="Paid By Sender", track_visibility=True)

    receiving_loc_country_code = fields.Char(string='Receiver Country Code')
    receiving_loc_city_id = fields.Char(string='Receiver City ID')
    receiving_loc_address = fields.Char(string='Receiver Address')

    delivery_loc_country_code = fields.Char(string='Delivery Country Code')
    delivery_loc_city_id = fields.Char(string='Delivery City ID')
    delivery_loc_address = fields.Char(string='Delivery Address')
    waybill_id = fields.Char(string='Bayan Waybill ID')
    state = fields.Selection([('closed', 'Closed'), ('cancelled', 'Cancelled')], track_visibility=True)
    deliver_to_client = fields.Boolean(string="Deliver To Client", track_visibility=True)

    
    def action_close_waybill(self):
        print("sad")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Close Waybill',
            'view_mode': 'form',
            'res_model': 'close.way.bill',
            'target': 'new',
            'context': {
                'active_id': self.id,
                's': self.waybill_id,
                'active_ids': self.ids,
            }}
