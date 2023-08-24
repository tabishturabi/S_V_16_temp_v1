from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError


class TransportManagement(models.Model):
    _inherit = 'transport.management'

    transport_bayan_trip_id = fields.Many2one('bayan.data', track_visibility=True, string="Transport Bayan Trip ID", copy=False)
    bayan_status = fields.Selection([('draft', 'Draft'), ('success', 'Success'), ('failed', 'Failed')],
                                    string="Transport Bayan Status", track_visibility=True, related='transport_bayan_trip_id.state')

    
    def action_transport_bayan_create_api(self):
        bayan_config = self.env.ref('bayan_api.bayan_config_settings_data')
        if bayan_config and bayan_config.is_transport:
            if self.transport_bayan_trip_id:
                return self.transport_bayan_trip_id.action_create_api()

    def action_get_transport_bayan_pdf(self):
        bayan_config = self.env.ref('bayan_api.bayan_config_settings_data')
        if bayan_config and bayan_config.is_transport:
            if self.transport_bayan_trip_id:
                return self.transport_bayan_trip_id.action_get_bayan_pdf_v2()

    
    def transport_create_waybill_ids(self, transport_id,bayan_id):
        way_bill_line = self.env['way.bill.line']
        if transport_id:
            for rec in transport_id.transport_management_line:
                if rec.product_id:
                    sender_name = self.sender_name
                    sender_phone = "+" + "966" + self.mobile
                    sender_country_code = self.sender_nationality.code or 'SA'
                    sender_city_id = self.form_transport.region_city_id.bayan_city_id
                    sender_address = self.to_transport.route_waypoint_name
                    receiver_name = self.receiver_name
                    receiver_phone = "+" + "966" + self.rec_mobile
                    receiver_country_code = self.receiver_nationality.code or 'SA'
                    receiver_city_id = self.to_transport.region_city_id.bayan_city_id
                    receiver_address = self.to_transport.route_waypoint_name
                    fare = rec.total_amount
                    tradable = False
                    paidBySender = True
                    receiving_loc_country_code = self.receiver_nationality.code or 'SA'
                    receiving_loc_city_id = self.form_transport.region_city_id.bayan_city_id
                    receiving_loc_address = self.to_transport.route_waypoint_name
                    delivery_loc_country_code = self.sender_nationality.code or 'SA'
                    delivery_loc_city_id = self.to_transport.region_city_id.bayan_city_id
                    delivery_loc_address = self.to_transport.route_waypoint_name
                    way_bill_id = way_bill_line.create({
                        'parent_id': bayan_id.id,
                        'sender_name': sender_name,
                        'sender_phone': sender_phone,
                        'sender_country_code': sender_country_code,
                        'sender_city_id': sender_city_id,
                        'sender_address': sender_address,
                        'receiver_name': receiver_name,
                        'receiver_phone': receiver_phone,
                        'receiver_country_code': receiver_country_code,
                        'receiver_city_id': receiver_city_id,
                        'receiver_address': receiver_address,
                        'fare': fare,
                        'tradable': tradable,
                        'paidBySender': paidBySender,
                        'receiving_loc_country_code': receiving_loc_country_code,
                        'receiving_loc_city_id': receiving_loc_city_id,
                        'receiving_loc_address': receiving_loc_address,
                        'delivery_loc_country_code': delivery_loc_country_code,
                        'delivery_loc_city_id': delivery_loc_city_id,
                        'delivery_loc_address': delivery_loc_address,
                        'transport_management_line': rec.id,
                        "deliver_to_client": True,
                        'line_ids': [(0, 0, {
                            "unit_id": 1,
                            "valid": True,
                            "quantity": 1,
                            "price": fare,
                            "good_type_id": rec.transport_bayan_goods_type_id.good_id,
                            "weight": rec.weight,
                            "dangerous_code": "dangerous_code",
                            "dimensions": str(rec.length) + "*" + str(
                                rec.width) + "*" + str(
                                rec.height),
                            "item_number": "12"})],
                    })
                    rec.write({'transport_bayan_way_bill_line_id':way_bill_id.id})

    
    def action_vendor_trip(self):
        res = super(TransportManagement, self).action_vendor_trip()
        bayan_config = self.env.ref('bayan_api.bayan_config_settings_data')
        if bayan_config and bayan_config.is_transport and not self.transport_bayan_trip_id:
            bayan = self.env['bayan.data']
            transport_id = self.env['transport.management'].browse(self.id)
            plate_type_id = transport_id.transportation_vehicle.bayan_plate_type_id.bayan_id
            leftLetter = transport_id.transportation_vehicle.leftLetter
            middleLetter = transport_id.transportation_vehicle.middleLetter
            rightLetter = transport_id.transportation_vehicle.rightLetter
            plate_no = transport_id.transportation_vehicle.plate_no
            identityNumber = transport_id.transportation_driver.bsg_empiqama.bsg_iqama_name
            issueNumber = int(
                transport_id.transportation_driver.bsg_empiqama.bayan_issue_number) if transport_id.transportation_driver.bsg_empiqama.bayan_issue_number else 1
            mobile = transport_id.transportation_driver.mobile_phone
            if not mobile:
                raise UserError(_("The mobile no against driver is not set"))
            received_date = transport_id.loading_date
            expected_delivery_date = transport_id.arrival_date
            data_dict = {
                "name": "New",
                "plate_type_id": plate_type_id,
                "leftLetter": leftLetter,
                "middleLetter": middleLetter,
                "rightLetter": rightLetter,
                "plate_no": plate_no,
                "identity_number": identityNumber,
                "issue_number": issueNumber,
                "mobile": "+966" + str(int(mobile)),
                "received_date": received_date,
                "expected_delivery_date": expected_delivery_date,
                'state': 'draft',
                'sticker_no': transport_id.transportation_vehicle.id,
                'transport_management_id': transport_id.id,
                'bayan_ref': 'transport'
            }
            bayan_id = bayan.create(data_dict)
            self.transport_create_waybill_ids(self, bayan_id)
            transport_id.write({'transport_bayan_trip_id': bayan_id.id})
            return res