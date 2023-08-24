# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TruckViolation(models.Model):
    _name = 'fleet.truck.violation'
    _description = 'Fleet Truck Violation'
    _rec_name = 'name'

    name = fields.Char(string='Name', readonly=True)
    location_link = fields.Char(string='Location Link', readonly=True)
    zone = fields.Char(string='Zone', track_visibility='always', readonly=True)
    google_link = fields.Char(string='Google Link',  track_visibility='always', readonly=True)
    Violation_desc = fields.Char(string='Violation Description', track_visibility='always')
    violation_name = fields.Char(string='Violation Name', required=True, track_visibility='always', readonly=True)

    settle_on = fields.Selection([('on_driver', 'On Driver'),
                                  ('on_company', 'On Company')], track_visibility='always')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('settled', 'Settled'), ('cancelled', 'Cancelled')], default='draft',
                             track_visibility='always')
    violation_date = fields.Datetime('Violation Date', track_visibility=True, readonly=True)
    record_date = fields.Datetime(string="Record Date", default=lambda self: fields.Datetime.now(), readonly=True)
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Truck", track_visibility='always', readonly=True)
    driver_id = fields.Many2one('hr.employee', string="Driver", track_visibility='always', readonly=True)
    driver_phone = fields.Char('Driver Phone', readonly=True)
    location_id = fields.Many2one('bsg_route_waypoints', string='Location', track_visibility='always', readonly=True)
    trip_id = fields.Many2one('fleet.vehicle.trip', string='Vehicle Trip', track_visibility='always', readonly=True)
    violation_type_id = fields.Many2one('violation.type', string='Violation Type')
    action_taken_id = fields.Many2one('violation.action', string='Violation Action')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('truck.violation') or _('New')
        return super(TruckViolation, self).create(vals)

    
    def action_set_to_draft(self):
        return self.write({'state': 'draft'})

    
    def action_confirm(self):
        return self.write({'state': 'confirm'})

    
    def action_settle(self):
        return self.write({'state': 'settled'})

    
    def action_cancel(self):
        return self.write({'state': 'cancelled'})

    
    def cron_check_violation(self):
        pass


class ViolationType(models.Model):
    _name = 'violation.type'

    name = fields.Char(string='Violation Type', required=True, track_visibility='always')


class ViolationType(models.Model):
    _name = 'violation.action'

    name = fields.Char(string='Violation Action', required=True, track_visibility='always')
