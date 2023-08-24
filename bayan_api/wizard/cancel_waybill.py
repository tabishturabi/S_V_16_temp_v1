from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
import requests

_logger = logging.getLogger(__name__)



class CancelWayBill(models.TransientModel):
    _name = "cancel.way.bill"

    @api.model
    def default_get(self, fields_list):
        defaults = super(CancelWayBill, self).default_get(fields_list)
        cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line'].browse(self.env.context.get('cargo_sale_line'))
        if cargo_sale_line:
            defaults['reference'] = cargo_sale_line.display_name
            defaults['way_bill_id'] = cargo_sale_line.waybill_id

        print(cargo_sale_line)
        return defaults

    reference = fields.Char("Reference")
    way_bill_id = fields.Char("Way Bill ID")
    bayan_reason_id = fields.Many2one('cancel.status.reasons', track_visibility=True, string="Bayan Reason")

    
    def action_cancel_waybill(self):
        if self.way_bill_id:
            bayan_config_settings = self.env.ref('bayan_api.bayan_config_settings_data')
            headers = {'app_id': bayan_config_settings.bayan_app_id, 'app_key': bayan_config_settings.bayan_app_key,
                       'client_id': bayan_config_settings.bayan_client_id,
                       'Content-Type': 'application/json'}
            api_end = bayan_config_settings.bayan_live_url + '/api/v1/carrier/trip/waybill/cancel'
            request_data_dynamic = {
                "waybillId": int(self.way_bill_id),
                "reasonId": str(self.bayan_reason_id.reason_id)
            }
            if self.env.context.get('bsg_fleet_trip_id') and self.bayan_reason_id:
                fleet_vehicle_trip = self.env['fleet.vehicle.trip'].browse(self.env.context.get('bsg_fleet_trip_id'))
                fleet_vehicle_trip.message_post(body="Reason : "+ str(self.bayan_reason_id.name))
            response = requests.put(url=api_end, headers=headers, data=json.dumps(request_data_dynamic))
            if response.status_code == 200:
                cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line'].browse(self.env.context.get('cargo_sale_line'))
                cargo_sale_line.bayan_way_bill_line_id.write({'state':'cancelled'})
            else:
                raise UserError(_("Cancel WayBill Response : " + str(response.text or response)))
