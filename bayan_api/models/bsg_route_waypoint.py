from odoo import models, fields, api, _


class BsgRouteWaypoints(models.Model):
    _inherit = 'bsg_route_waypoints'

    bayan_city_id = fields.Integer(string="Bayan City ID", track_visibility=True)
    bayan_region_id = fields.Integer(string="Bayan Region ID", track_visibility=True)
