# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CheckDuplicate(models.TransientModel):
    _inherit = "calculate.value.wizard"

    
    def create_waybill_ids(self, trip_id,bayan_id):
        way_bill_line = self.env['way.bill.line']
        if trip_id:
            for rec in trip_id.stock_picking_id:
                if rec.picking_name.service_type:
                    cargo_sale = rec.picking_name.bsg_cargo_sale_id
                    sender_name = cargo_sale.sender_name
                    if cargo_sale.same_as_customer:
                        mobile_number_sender = cargo_sale.customer.mobile or cargo_sale.customer.phone
                    else:
                        mobile_number_sender = cargo_sale.sender_mob_no
                    if mobile_number_sender and cargo_sale.sender_mob_country_code:
                        sender_phone = "+" + cargo_sale.sender_mob_country_code + mobile_number_sender
                    else:
                        sender_phone = "+" + cargo_sale.receiver_mob_country_code + cargo_sale.receiver_mob_no
                    sender_country_code = cargo_sale.sender_nationality.code or 'SA'
                    sender_city_id = rec.picking_name.loc_from.region_city_id.bayan_city_id
                    sender_address = rec.picking_name.loc_from.route_waypoint_name
                    receiver_name = cargo_sale.receiver_name
                    receiver_phone = "+" + cargo_sale.receiver_mob_country_code + cargo_sale.receiver_mob_no
                    receiver_country_code = cargo_sale.receiver_nationality.code or 'SA'
                    receiver_city_id = rec.picking_name.loc_to.region_city_id.bayan_city_id
                    receiver_address = rec.picking_name.loc_to.route_waypoint_name
                    fare = rec.picking_name.charges
                    tradable = False
                    paidBySender = True
                    receiving_loc_country_code = cargo_sale.receiver_nationality.code or 'SA'
                    receiving_loc_city_id = rec.picking_name.loc_from.region_city_id.bayan_city_id
                    receiving_loc_address = rec.picking_name.loc_from.route_waypoint_name
                    delivery_loc_country_code = cargo_sale.sender_nationality.code or 'SA'
                    delivery_loc_city_id = rec.picking_name.loc_to.region_city_id.bayan_city_id
                    delivery_loc_address = rec.picking_name.loc_to.route_waypoint_name
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
                        'paid_by_sender': paidBySender,
                        'receiving_loc_country_code': receiving_loc_country_code,
                        'receiving_loc_city_id': receiving_loc_city_id,
                        'receiving_loc_address': receiving_loc_address,
                        'delivery_loc_country_code': delivery_loc_country_code,
                        'delivery_loc_city_id': delivery_loc_city_id,
                        'delivery_loc_address': delivery_loc_address,
                        'bsg_cargo_sale_line': rec.picking_name.id,
                        "deliver_to_client": True,
                        'line_ids': [(0, 0, {
                            "unit_id": 1,
                            "valid": True,
                            "quantity": 1,
                            "price": rec.picking_name.charges,
                            "good_type_id": 9,
                            "weight": rec.picking_name.car_size.weight,
                            "dangerous_code": "dangerous_code",
                            "dimensions": str(rec.picking_name.car_size.car_size_len) + "*" + str(
                                rec.picking_name.car_size.car_size_width) + "*" + str(
                                rec.picking_name.car_size.car_size_height),
                            "item_number": "12"})],
                    })
                    rec.picking_name.write({'bayan_way_bill_line_id':way_bill_id.id})

    
    def check_value(self):
        res = super(CheckDuplicate, self).check_value()
        if self.env.context.get('active_id'):
            bayan = self.env['bayan.data']
            trip_id = self.env['fleet.vehicle.trip'].browse(self.env.context.get('active_id'))
            plate_type_id = trip_id.vehicle_id.bayan_plate_type_id.bayan_id
            leftLetter = trip_id.vehicle_id.leftLetter
            middleLetter = trip_id.vehicle_id.middleLetter
            rightLetter = trip_id.vehicle_id.rightLetter
            plate_no = trip_id.vehicle_id.plate_no
            identityNumber = trip_id.driver_id.bsg_empiqama.bsg_iqama_name
            issueNumber = int(trip_id.driver_id.bsg_empiqama.bayan_issue_number) if trip_id.driver_id.bsg_empiqama.bayan_issue_number else 1
            mobile = trip_id.driver_id.mobile_phone
            if not mobile:
                raise UserError(_("The mobile no against driver is not set"))
            received_date = trip_id.expected_start_date
            expected_delivery_date = trip_id.expected_end_date
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
                'sticker_no': trip_id.vehicle_id.id,
                'fleet_vehicle_trip': trip_id.id,
                'bayan_ref': 'cargo_sale'
            }
            bayan_id = bayan.create(data_dict)
            way_bill_ids = self.create_waybill_ids(trip_id,bayan_id)

            trip_id.write({'bayan_trip_id': bayan_id.id})
        return res
