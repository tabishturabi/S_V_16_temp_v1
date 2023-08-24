# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp

class FleetDailyTripCount(models.Model):
    _name = 'fleet.daily.trip.count'
    _description = "Support Team Fleet Daily Trip Count"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('fleet.vehicle',string="Vehicle ID", track_visibility="onchange")
    daily_trip_count = fields.Integer(string="Current Daily Trip Count", track_visibility="onchange")
    new_daily_trip_count = fields.Integer(string="New Daily Trip Count",track_visibility="onchange")
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')], string='Status', track_visibility=True, default='draft')

    
    @api.onchange('name')
    def _onchange_parent_id(self):
        for data in self:
            data.daily_trip_count = data.name.daily_trip_count

    
    def change_trip_count(self):
        self.name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).write({'daily_trip_count' : self.new_daily_trip_count})
#         self.name.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).link_driver()
        self.state = 'confirmed'

    @api.model
    def create(self, vals):
        res = super(FleetDailyTripCount, self).create(vals)
        res._onchange_parent_id()
        return res

    
    def write(self, vals):
        if vals.get('name'):
            vehicle_id = self.env['fleet.vehicle'].browse(vals.get('name'))
            vals['daily_trip_count'] = vehicle_id.daily_trip_count
        res = super(FleetDailyTripCount, self).write(vals)
        return res