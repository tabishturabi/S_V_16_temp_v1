# -*- coding: utf-8 -*-


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BsgPackageShipment(models.Model):
    _name = 'bsg_package_shipment'
    _description = 'Bsg Package Shipment'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = "name desc"

    @api.model
    def _default_get_loc_from(self):
        if self.env.user and self.env.user.user_branch_id:
            loc_from = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                              limit=1)
            if loc_from:
                return loc_from.id
            else:
                return False

    name = fields.Char(string="Name")
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('pod', 'Delivery'),
            ('done', 'Done'),
            ('awaiting', 'Awaiting Return'),
            ('shipped', 'Shipped'),
            ('on_transit', 'On Transit'),
            ('Delivered', 'Delivered'),
            ('unplanned', 'Unplanned'),
            ('cancel', 'Declined')
        ], string='State', default="draft", track_visibility=True, )
    send_name = fields.Char('Send Name')
    receiver_name = fields.Char('Recipient Description')
    receiver_employee_id = fields.Many2one("hr.employee", string="Recipient Name", track_visibility='onchange')
    loc_from = fields.Many2one(string="From", comodel_name="bsg_route_waypoints", default=_default_get_loc_from,
                               track_visibility='onchange')
    loc_from_branch_id = fields.Many2one(related="loc_from.loc_branch_id", store=True, track_visibility='onchange')
    loc_to = fields.Many2one(string="To", comodel_name="bsg_route_waypoints", track_visibility='onchange')
    order_date = fields.Datetime(string="Order Date", default=lambda self: fields.datetime.now())
    active = fields.Boolean(string="Active", track_visibility=True, default=True)
    allow_change_loc = fields.Boolean(string='Change Location')
    note = fields.Text('Description')
    cargo_sale_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line', string="Cargo Sale Line")
    sale_line_rec_name = fields.Char('Sale Line')

    trip_id = fields.Many2one(related="cargo_sale_line_id.fleet_trip_id", string='Trip ID', store=True)
    vehicle_id = fields.Many2one(related="cargo_sale_line_id.fleet_trip_id.vehicle_id", string='Truck Sticker#',
                                 store=True)
    driver_id = fields.Many2one(related="cargo_sale_line_id.fleet_trip_id.vehicle_id.bsg_driver", string='Driver Name',
                                store=True)
    trip_start_date = fields.Datetime(related="cargo_sale_line_id.fleet_trip_id.expected_start_date",
                                      string='Trip Start Date', store=True)
    trip_arrival_date = fields.Datetime(related="cargo_sale_line_id.fleet_trip_id.expected_end_date",
                                        string='Trip Arrival Date', store=True)
    trip_status = fields.Selection(related="cargo_sale_line_id.fleet_trip_id.state", string='Trip Status', store=True)

    is_check = fields.Boolean(string="Same As Above")
    receive_date = fields.Date(string='Receive Date')
    actual_receiver_name = fields.Char('Actual Receiver Name')

    # @api.multi
    @api.onchange('is_check')
    def _onchange_is_check(self):
        for data in self:
            if data.receiver_employee_id:
                data.actual_receiver_name = data.receiver_employee_id.name

    # @api.multi
    def set_draft_btn(self):
        return self.write({'state': 'draft'})

    # @api.multi
    def confirm_btn(self):
        # 		self.name = str(self.loc_from.loc_branch_id.branch_no) + self.env['ir.sequence'].next_by_code('bsg_package_shipment')
        cargo_sale = self.env['bsg_vehicle_cargo_sale']
        cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line']

        cargo_sale_vals = {
            'loc_from': self.loc_from.id,
            'loc_to': self.loc_to.id,
            'state': 'done'}
        cs_id = cargo_sale.create(cargo_sale_vals)

        vals = {'bsg_cargo_sale_id': cs_id.id, 'sale_order_state': 'done'}
        csl_id = cargo_sale_line.create(vals)
        csl_id.write({'sale_line_rec_name': self.name})
        self.cargo_sale_line_id = csl_id.id
        return self.write({'state': 'confirm'})

    # @api.multi
    def set_receive_btn(self):
        return self.write({'state': 'done', 'receive_date': fields.Date.today()})

    # CRUD METHODS
    @api.model
    def create(self, vals):
        PackageShipment = super(BsgPackageShipment, self).create(vals)
        PackageShipment.name = self.env['ir.sequence'].next_by_code('bsg_package_shipment')
        return PackageShipment
        vals = {'bsg_cargo_sale_id': cs_id.id, 'sale_order_state': 'done', 'is_package': True}
        csl_id = cargo_sale_line.create(vals)
        csl_id.write({'sale_line_rec_name': self.name})
        self.cargo_sale_line_id = csl_id.id
        return self.write({'state': 'confirm'})

    # CRUD METHODS
    @api.model
    def create(self, vals):
        PackageShipment = super(BsgPackageShipment, self).create(vals)
        PackageShipment.name = self.env['ir.sequence'].next_by_code('bsg_package_shipment')
        return PackageShipment

