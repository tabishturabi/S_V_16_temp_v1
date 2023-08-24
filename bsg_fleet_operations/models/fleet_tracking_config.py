# -*- coding: utf-8 -*-
from odoo import api, fields, models

class FleetTrackingConfigCustomFields(models.Model):
    _name = 'fleet.tracking.config.custom.fields'
    _description = 'Fleet tracking custoom fields configuration'
    _rec_name ='remote_label'

    remote_label = fields.Char('Label', required=True, readonly=True)
    remote_field_id = fields.Integer('Remote field ID', readonly=True)
    remote_field_value = fields.Integer('Remote field Value', readonly=True)
    fleet_tracking_config_id = fields.Many2one('fleet.tracking.config', string='Tracking config', readonly=True)


class FleetTrackingConfig(models.Model):
    _name = 'fleet.tracking.config'
    _description = 'Fleet tracking configuration'
    _rec_name = 'remote_imei'

    fleet_vehicle_id  = fields.Many2one('fleet.vehicle',string='Fleet Vehicle', required=True)
    remote_imei = fields.Char('Remote IMEI', required=True)
    custom_field_ids = fields.One2many('fleet.tracking.config.custom.fields', 'fleet_tracking_config_id', string="Remote Custom Fields")


