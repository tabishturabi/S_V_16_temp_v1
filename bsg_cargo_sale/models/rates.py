# -*- coding: utf-8 -*-

from odoo import models, fields, api

class bsg_customer_rates(models.Model):
    _name = 'bsg_customer_rates'
    _description = "Customer Rates"
    _inherit = ['mail.thread']

    loc_from = fields.Many2one(string="From", comodel_name="bsg_route_waypoints")
    loc_to = fields.Many2one(string="To", comodel_name="bsg_route_waypoints")
    car_size = fields.Many2one(string="Car Size", comodel_name="bsg_car_size")
    price = fields.Float(string="Price")
    partner_id = fields.Many2one(string="Partner ID", comodel_name="res.partner")
    active = fields.Boolean(string="Active", track_visibility=True, default=True)