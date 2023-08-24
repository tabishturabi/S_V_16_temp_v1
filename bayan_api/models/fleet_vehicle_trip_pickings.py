from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)
import requests
import json


class FleetVehicleTripPickings(models.Model):
    _inherit = 'fleet.vehicle.trip.pickings'


    bayan_config_active = fields.Boolean(string="Is Bayan Config Active", compute="_compute_baya_config_id")
    way_bill_line_state = fields.Selection([('closed', 'Closed'), ('cancelled', 'Cancelled')],
                                    string="Bayan Status", track_visibility=True, related='picking_name.way_bill_line_state')

    bayan_way_bill_line_id = fields.Many2one('way.bill.line', track_visibility=True, string="Way Bill ID",related='picking_name.bayan_way_bill_line_id')


    def _compute_baya_config_id(self):
        bayan_config = self.env.ref('bayan_api.bayan_config_settings_data')
        for rec in self:
            rec.bayan_config_active = False
            if bayan_config and bayan_config.is_active:
                rec.bayan_config_active = True

    def btn_cancel_waybill(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cancel Waybill',
            'view_mode': 'form',
            'res_model': 'cancel.way.bill',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'active_ids': self.ids,
                'bsg_fleet_trip_id': self.bsg_fleet_trip_id.id,
                'cargo_sale_line': self.picking_name.id,
            }}
