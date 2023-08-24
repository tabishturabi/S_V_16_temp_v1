# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


# Asset Status
class BsgFleetAssetStatus(models.Model):
    _name = 'bsg.fleet.asset.status'
    _description = 'Asset Status'
    _inherit = ['mail.thread']
    _rec_name = "asset_status_name"

    asset_status_name = fields.Char()
    active = fields.Boolean(string="Active", track_visibility=True, default=True)

    _sql_constraints = [
        ('value_asset_status_name_uniq', 'unique (asset_status_name)', 'This Record already exists !')
    ]

    # @api.multi
    def unlink(self):
        trailer_obj = self.env['bsg_fleet_trailer_config'].search([('trailer_asset_status', '=', self.id)])
        if trailer_obj:
            raise UserError(
                _('Sorry you cant delete this record as it is already in used by some other records'),
            )
        result = super(BsgFleetAssetStatus, self).unlink()
        return result


# Asset Location
class BsgFleetAssetLocation(models.Model):
    _name = 'bsg.fleet.asset.location'
    _description = 'Asset Location'
    _inherit = ['mail.thread']
    _rec_name = 'asset_location_name'

    asset_location_name = fields.Char(string='Asset Location')
    active = fields.Boolean(string="Active", track_visibility=True, default=True)


# Asset Group
class BsgFleetAssetGroup(models.Model):
    _name = 'bsg.fleet.asset.group'
    _description = 'Asset Group'
    _inherit = ['mail.thread']
    _rec_name = "asset_group_name"

    asset_group_name = fields.Char()
    active = fields.Boolean(string="Active", track_visibility=True, default=True)

    _sql_constraints = [
        ('value_asset_group_name_uniq', 'unique (asset_group_name)', 'This Record already exists !')
    ]

    # @api.multi
    def unlink(self):
        trailer_obj = self.env['bsg_fleet_trailer_config'].search([('trailer_asset_group', '=', self.id)])
        if trailer_obj:
            raise UserError(
                _('Sorry you cant delete this record as it is already in used by some other records'),
            )
        result = super(BsgFleetAssetStatus, self).unlink()
        return result


# Document Types
class DocumentsType(models.Model):
    _name = 'documents.type'
    _description = 'All Documents Type'
    _inherit = ['mail.thread']
    _rec_name = 'document_type_id'

    document_type_id = fields.Char(string='Document Type Id')
    name = fields.Char(string='Document Type Name')
    active = fields.Boolean(string="Active", track_visibility=True, default=True)
    year_of_renew = fields.Integer('Year of Renew')


# Vehicle Group
class BsgVehicleGroup(models.Model):
    _name = 'bsg.vehicle.group'
    _description = "Vehicle Group"
    _inherit = ['mail.thread']
    _rec_name = "vehicle_group_name"

    vehicle_group_name = fields.Char()
    active = fields.Boolean(string="Active", track_visibility=True, default=True)

    _sql_constraints = [
        ('value_vehicle_group_name_uniq', 'unique (vehicle_group_name)', 'This Record already exists !')
    ]


# Vehicle Table Type
class BsgVehicleTypeTable(models.Model):
    _name = 'bsg.vehicle.type.table'
    _description = "Vehicle Types Talbe"
    _inherit = ['mail.thread']
    _rec_name = "vehicle_type_name"

    vehicle_type_name = fields.Char()
    vehicle_type_code = fields.Char()

    domain_id = fields.Selection(string="Domain Name", selection=[
        ('Carrier', 'Carrier'), ('Bx', 'Bx'), ('Cargo', 'Cargo'), ('Service', 'Service')])
    satha = fields.Boolean(string='Satha')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.account.tag', string="Analytic Tags")
    active = fields.Boolean(string="Active", track_visibility=True, default=True)
    reward_for_analytic_account_id = fields.Many2one('account.analytic.account', string='Reward For Load Analytic Account')
    reward_for_analytic_tag_id = fields.Many2one('account.account.tag', string='Reward For Load Invoice Analytic Tag')

    _sql_constraints = [
        ('value_vehicle_type_code_uniq', 'unique (vehicle_type_code)', 'This Record already exists !')
    ]

    # @api.multi
    def unlink(self):
        for rec in self:
            search_vehicle = self.env['fleet.vehicle'].search([('vehicle_type', '=', rec.id)])
            if search_vehicle:
                raise UserError(_('Cant delete this record as is linked with others.'))

        return super(BsgVehicleTypeTable, self).unlink()


# Vehicle Status
class BsgVehicleStatus(models.Model):
    _name = 'bsg.vehicle.status'
    _description = "Vehicle Status"
    _inherit = ['mail.thread']
    _rec_name = "vehicle_status_name"

    vehicle_status_name = fields.Char()
    active = fields.Boolean(string="Active", track_visibility=True, default=True)

    _sql_constraints = [
        ('value_vehicle_status_name_uniq', 'unique (vehicle_status_name)', 'This Record already exists !')
    ]
