# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class BranchesZones(models.Model):
    _name = 'branches.zones'
    _inherit = 'mail.thread'
    _description = 'Branches Zones'

    name = fields.Char(string='Name',translate=True,track_visibility='always')
    location_ids = fields.Many2many('bsg_route_waypoints','route_waypoints_branches_zones_rel','route_waypoint_id','zone_id',string="Locations")

    #@api.multi
    def write(self, values):
        res = super(BranchesZones, self).write(values)
        for rec in self:
            if rec:
                if rec.location_ids:
                    rec.location_ids.write({
                        'zone_id': rec.id
                    })
        return res

    @api.model
    def create(self, vals):
        res = super(BranchesZones, self).create(vals)
        for rec in res:
            if rec:
                if rec.location_ids:
                    rec.location_ids.write({
                        'zone_id': rec.id
                    })
        return res


# class RegionConfigInherit(models.Model):
#     _inherit = 'region.config'
#
#     bsg_region_name = fields.Char(track_visibility='always')
#     bsg_region_code = fields.Char(track_visibility='always')
#     region_arabic_name = fields.Char(string='Region Arabic Name',track_visibility='always')
#     region_line = fields.One2many('region.config.line','region_id',string='Region Line')
#
#
# class RegionConfigLine(models.Model):
#     _name = 'region.config.line'
#     _rec_name='city_name'
#
#     region_id = fields.Many2one('region.config',string='Region ID')
#     city_name = fields.Char(string='City Name' ,translate=True)
#     city_code = fields.Char(string='City Code')
#     bayan_city_id = fields.Integer("Bayan City ID", track_visibility='always')
#
#
#
# class BranchesInherit(models.Model):
#     _inherit = 'bsg_branches.bsg_branches'
#
#     region = fields.Many2one(readonly=True)
#     region_city = fields.Many2one('region.config.line', string='Region City', readonly=True)
#     zone_id = fields.Many2one('branches.zones', string='Zone', track_visibility='always', readonly=True)
#     check = fields.Boolean(string='Check')
#     weekly_working_hours = fields.Char(string="Weekly Working Hours", track_visibility='always')
#     friday_working_hours = fields.Char(string="Friday Working Hours", track_visibility='always')
#     description = fields.Char(string='Description',track_visibility='always')

    # @api.onchange('region')
    # def _get_region_city(self):
    #     if self.region:
    #         if not self.check:
    #             self.region_city = False
    #         if self.region.region_line:
    #             self.check = False
    #             return {'domain': {'region_city': [('id', 'in',self.region.region_line.ids)]}}
    #         if not self.region.region_line:
    #             self.check = False
    #             return {'domain': {'region_city': [('id', 'in',self.region.region_line.ids)]}}
    #
    #     else:
    #         city_ids = self.env['region.config.line'].search([])
    #         return {'domain': {'region_city': [('id', 'in',city_ids.ids)]}}
    #
    #
    # @api.onchange('region_city')
    # def _get_region(self):
    #     if self.region_city:
    #         if not self.region:
    #             self.check = True
    #         self.region=self.region_city.region_id

    # #@api.multi
    # def write(self, values):
    #     res = super(BranchesInherit, self).write(values)
    #     for rec in self:
    #         if rec:
    #             route_waypoint_ids = rec.env['bsg_route_waypoints'].search([('loc_branch_id','=',rec.id)])
    #             if route_waypoint_ids:
    #                 route_waypoint_ids.write({
    #                     'region':rec.region.id,
    #                     'region_city_id': rec.region_city.id,
    #                     'zone_id': rec.zone_id.id
    #                 })
    #     return res








