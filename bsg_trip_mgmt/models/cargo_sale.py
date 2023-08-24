# -*- coding: utf-8 -*-
from lxml import etree
# from odoo.osv.orm import setup_modifiers
import json
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import datetime
from collections.abc import Iterable
from datetime import datetime
from datetime import date, timedelta


def get_days_hours(hours_count, days, hours):
    if hours_count <= 0:
        return days, hours
    elif hours_count >= 25:
        days += 1
        hours_count = hours_count - 24
        return get_days_hours(hours_count, days, hours)
    elif hours_count < 24 and hours_count > 0:
        hours += hours_count
        hours_count = 0
        return get_days_hours(hours_count, days, hours)


# Cargo Sale Order
class InheritBsgCargoSale(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale'


# Cargo Sale Order Line
class bsg_vehicle_cargo_sale_line(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale_line'

    # Get default local trip revenue
    @api.model
    def _default_local_trip_revenue(self):
        return self.env['ir.config_parameter'].sudo().get_param('bsg_trip_mgmt.local_trip_revenue')

    # 
    def _get_arrival_info(self):
        trip_id = self.env['fleet.trip.arrival.line'].search([('delivery_id', '=', self.id)], limit=1,
                                                             order='write_date desc')
        self.actual_start_time = trip_id.actual_start_time
        self.drawer_no = trip_id.drawer_no
        self.parking_no = trip_id.parking_no

    # @api.multi
    def print_delivery_report(self):
        if self.invoice_ids:
            for data in self.invoice_ids:
                if data.payment_state not in ['paid', 'reversed']:
                    raise UserError(_('Please Paid first Demurrage Invoices ....!'))
        if self.bsg_cargo_sale_id.is_old_order:
            if self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
                for data in self.bsg_cargo_sale_id.invoice_ids:
                    if data.payment_state != 'paid' and not data.payment_state == 'reversed':
                        raise UserError(_('Please First Pay Your Cargo Invoice'))
                other_service_invoice = self.env['account.move'].search(
                    [('ref', '=', self.bsg_cargo_sale_id.name), ('is_other_service_invoice', '=', True)], limit=1)
                if other_service_invoice:
                    if other_service_invoice.payment_state != 'paid':
                        raise UserError(_('Please First Pay Your Cargo Other Service Invoice'))
        elif self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
            if not all(self.invoice_line_ids.filtered(lambda s: not s.is_refund).mapped('is_paid')):
                raise UserError(_('Please First Pay Your Cargo Invoice Lines'))
        other_service_not_invoiced = self.env['other_service_items'].search(
            [('cargo_sale_id', '=', self.bsg_cargo_sale_id.id),('cost','>',0), ('cargo_sale_line_id', '=', self.id),
             ('is_invoice_create', '=', False)])
        if other_service_not_invoiced:
            raise UserError(
                _('Sorry This Line Has Other Service Not Invoiced, You Must Create Invoice For It Or Delete It '))
        self.state = 'done'
        self.create_delivery_history()
        return self.env.ref('bsg_cargo_sale.report_cs_delivery_report').report_action(self)

    fleet_trip_id = fields.Many2one(string="Trip ID", comodel_name="fleet.vehicle.trip", track_visibility=True, )
    last_fleet_trip_id = fields.Many2one(string="Last Trip ID", comodel_name="fleet.vehicle.trip",
                                         compute="_get_last_bsg_fleet_trip_id", readonly=True)
    scheduled_arrival_date = fields.Datetime(related="fleet_trip_id.expected_end_date", store=True)
    actual_start_time = fields.Datetime(string="Trip Start Time", compute="_get_arrival_info")
    parking_no = fields.Char(string="Park No", compute="_get_arrival_info")
    drawer_no = fields.Char(string="Drawer No", compute="_get_arrival_info")
    added_to_trip = fields.Boolean(string='Added To Trip', track_visibility=True, )
    added_to_local_to_shipment_branch = fields.Boolean(string='Added To Local Trip to shipment branch',
                                                       track_visibility=True,
                                                       help="True when record is added to local trip from customer location to the shipment branch")
    added_to_local_from_arriavl_branch = fields.Boolean(string='Added To Local Trip from arriavl branch',
                                                        track_visibility=True,
                                                        help="True when record is added to local trip from arrival branch to the customer location")

    trip_history_ids = fields.One2many(
        'bsg.sale.line.trip.history',
        'cargo_sale_line_id',
        string='Trip History IDS',
    )
    arrival_status = fields.Boolean(string='Arrived')
    refund_discount = fields.Float(string="Credit Note Amount", track_visibility="onchange", compute='_compute_discount_amount')
    net_revenue = fields.Float(string="Net Revenue", track_visibility="onchange", compute='_compute_net_revenue_amount')
    no_of_days_hours = fields.Char(string='Arrival Delay Period', compute='_compute_no_of_days')
    check_release_car = fields.Boolean(string="Release Car", compute="_get_release_car_check")

    @api.depends('pickup_loc')
    def _get_release_car_check(self):
        if self.state == 'on_transit' and self.pickup_loc.loc_branch_id.id == self.env.user.user_branch_id.id:
            self.check_release_car = True
        else:
            self.check_release_car = False

    def _compute_no_of_days(self):
        for rec in self:
            if rec.expected_delivery:
                exp_delivery = datetime.combine(rec.expected_delivery, datetime.min.time())
                exp_delivery = exp_delivery + timedelta(minutes=59)
                current = datetime.now()

                if rec.fleet_trip_id:
                    branch_current_ids = rec.fleet_trip_id.bsg_trip_arrival_ids.filtered(
                        lambda s: s.waypoint_to.id == rec.loc_to.id)
                    if branch_current_ids:
                        for branch_current_id in branch_current_ids:
                            if branch_current_id.actual_end_time:
                                current = branch_current_id.actual_end_time

                delta = current - exp_delivery
                delta_temp = int(delta.total_seconds())
                if delta_temp < 0:
                    delta_temp = abs(int(delta.total_seconds()))
                    day_and_hours = get_days_hours(int(delta_temp / 3600), 0, 0)
                    if isinstance(day_and_hours,Iterable):
                      day, hours = day_and_hours
                    else:
                      day = int(delta_temp / (60*60*24))
                      hours = int(int(delta_temp % (60*60*24)) / 3600)
                    day = -day
                    hours = -hours
                    rec.no_of_days_hours = "{0} Days {1} Hours ".format(day, hours)
                else:
                    day_and_hours = get_days_hours(int(delta_temp / 3600), 0, 0)
                    if isinstance(day_and_hours,Iterable):
                      day, hours = day_and_hours
                    else:
                      day = int(delta_temp / (60*60*24))
                      hours = int(int(delta_temp % (60*60*24)) / 3600)
                    rec.no_of_days_hours = "{0} Days {1} Hours ".format(day, hours)
            else:
                rec.no_of_days_hours = "No Expected Delivery Date "




    # @api.multi
    @api.depends('invoice_line_ids')
    def _compute_discount_amount(self):
        for rec in self:
            rec.refund_discount = sum(rec.invoice_line_ids.filtered(lambda s: s.is_refund).mapped('price_unit'))

    # @api.multi
    @api.depends('revenue_amount', 'refund_discount')
    def _compute_net_revenue_amount(self):
        for rec in self:
            rec.net_revenue = rec.revenue_amount - rec.refund_discount

    # @api.multi
    def _get_last_bsg_fleet_trip_id(self):
        for rec in self:
            query = """SELECT bsg_fleet_trip_id, create_date FROM fleet_vehicle_trip_pickings where picking_name = %s order by create_date desc limit 1;"""
            self.env.cr.execute(query, (str(rec.id),))
            query_results = self.env.cr.dictfetchall()
            if query_results:
                rec.last_fleet_trip_id = query_results[0]['bsg_fleet_trip_id']
            else:
                rec.last_fleet_trip_id = False

    # @api.multi
    def action_reset_line(self):
        if self.added_to_trip:
            self.added_to_trip = False

    # @api.multi
    def link_trip_to_sale_line(self):
        pass

    # trip_ids = self.env['fleet.vehicle.trip'].search([('state','not in', ['draft', 'cancelled'])])
    # trip_history = self.env['bsg.sale.line.trip.history']
    # for trip_id in trip_ids:
    # 	for line in trip_id.stock_picking_id:
    # 		branchRecord = self.env['branch.distance'].search([('branch_from','=',line.picking_name.pickup_loc.id),('branch_to','=',line.picking_name.drop_loc.id)], limit=1)
    # 		trip_distance = branchRecord.distance
    # 		if not trip_distance:
    # 			trip_distance = 1
    # 		if line.picking_name.fleet_trip_id.trip_type != 'local':
    # 			revenue = (trip_distance * line.picking_name.total_without_tax)/(sum(line.trip_distance for line in line.picking_name.trip_history_ids) or 1)
    # 		else:
    # 			default_revenue = float(self._default_local_trip_revenue())
    # 			revenue = default_revenue if default_revenue > 0 else 35
    # 		if (not line.picking_name.fleet_trip_id or (line.picking_name.fleet_trip_id and line.picking_name.fleet_trip_id.id != trip_id.id))\
    # 			 and (not line.picking_name.trip_history_ids or(line.picking_name.trip_history_ids and trip_id.id not in [trip.id for trip in line.picking_name.trip_history_ids.mapped('fleet_trip_id')])):
    # 				trip_history.create({
    # 					'cargo_sale_line_id':line.picking_name.id,
    # 					'fleet_trip_id':trip_id.id,
    # 					'trip_distance': trip_distance,
    # 					'earned_revenue':float(revenue),
    # 				})
    # 		else:
    # 			for rec in line.picking_name.trip_history_ids:
    # 				if rec.fleet_trip_id.id == trip_id.id:
    # 					rec.update({
    # 						'trip_distance': trip_distance,
    # 						'earned_revenue':float(revenue),
    # 						})

    # Calculation of earned revenue on basis of state change
    # @api.onchange('state')
    # def _onchange_state(self):
    # 	self.calculate_earned_revenue()

    # @api.multi
    def action_Delivered(self):
        res = super(bsg_vehicle_cargo_sale_line, self).action_Delivered()
        for rec in self:
            rec.calculate_earned_revenue()
        return res

    # @api.multi
    def calculate_earned_revenue(self):
        if self.state in ['Delivered', 'done']:
            default_revenue = float(self._default_local_trip_revenue())
            local_revenue = default_revenue > 0 and default_revenue or 35
            total_distance = sum(self.trip_history_ids.mapped('trip_distance')) or 1
            for th in self.trip_history_ids:
                if th.trip_type != 'local':
                    th.earned_revenue = (th.trip_distance * self.total_without_tax) / total_distance
                else:
                    th.earned_revenue = float(local_revenue)
    # @api.multi
    def add_to_auto_trip(self):
        #Search For auto Trip
        fleet_trip_id = self.env['fleet.vehicle.trip'].search([('trip_type','=','auto'),('state','=','draft'),('trip_waypoint_ids.waypoint','in',[self.loc_from.id]),('trip_waypoint_ids.waypoint','in',[self.loc_to.id])])
        for trip in fleet_trip_id.filtered(lambda s: s.display_capacity > 0 and (self.loc_from.id == s.route_id.waypoint_from.id or  \
            (s.route_id.waypoint_to_ids.filtered(lambda w:w.waypoint.id == self.loc_from.id)[0].sequence < s.route_id.waypoint_to_ids.filtered(lambda w:w.waypoint.id == self.loc_to.id)[0].sequence))):
            self.sudo().write(
                {'pickup_loc': self.loc_from.id, 'drop_loc': self.loc_to.id, 'arrival_status': False, })
            self.env['bsg_vehicle_cargo_sale'].sudo().create_trip_picking(
                self,
                self.loc_from,
                self.loc_to,
                fleet_trip_id
            )
            if not self.added_to_trip:
                self.added_to_trip = True
            if not self.fleet_trip_id:    
                self.fleet_trip_id = trip.id

# Trip History Cargo Sale Order Line
class BsgSaleLineTripHistory(models.Model):
    _name = 'bsg.sale.line.trip.history'
    _description = "Trip History Cargo Sale Line"

    # 
    @api.depends('fleet_trip_id')
    def _get_trip_type(self):
        if self.fleet_trip_id:
            self.trip_type = self.fleet_trip_id.sudo().trip_type

    fleet_trip_id = fields.Many2one(string="Trip ID", comodel_name="fleet.vehicle.trip")
    cargo_sale_line_id = fields.Many2one(string="Cargo Sale Line ID", comodel_name="bsg_vehicle_cargo_sale_line")
    trip_distance = fields.Float(string='Distance')
    earned_revenue = fields.Float(string='Earned Revenue')
    expected_start_date = fields.Datetime(related="fleet_trip_id.expected_start_date", string="Shipped Date",
                                          track_visibility=True, )
    # trip_type = fields.Selection(related="fleet_trip_id.trip_type", track_visibility=True, string="Plan Type", compute="_get_trip_type")
    trip_type = fields.Selection([
        ('auto', 'تخطيط تلقائي'),
        ('manual', 'تخطيط يدوي'),
        ('local', 'خدمي')], string="Plan Type", compute='_get_trip_type', store=True)

    delivery_date = fields.Datetime(related="cargo_sale_line_id.delivery_date", string=',Actual Arrival Date',
                                    track_visibility=True)
    expected_end_date = fields.Datetime(related="fleet_trip_id.expected_end_date", string="Expected Arrival Date",
                                        track_visibility=True, )


class CargoSaleLineAddLineData(models.TransientModel):
    _name = 'cargo_sale_line_data_trip'
    _description = "Cargo Sale Line Trip Info"

    cargo_sale_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line', string="Cargo Sale Line")
    cs_line_id = fields.Many2one(related="cargo_sale_line_id", store=True, string="Cargo Sale Line")
    loc_from = fields.Many2one('bsg_route_waypoints', string="From")
    pickup_loc = fields.Many2one('bsg_route_waypoints', string="Pickup Location")
    loc_to = fields.Many2one('bsg_route_waypoints', string="To")
    drop_loc = fields.Many2one('bsg_route_waypoints', string="Drop")
    cargo_sale_line_trip_id = fields.Many2one('cargo_sale_line_add_trip', string="Cargo Sale Trip ID")
    bsg_route_waypoints_line_ids = fields.Many2many('bsg_route_waypoints', string="Waypoint IDS")
    basg_route_waypoint_city_ids = fields.Many2many('bsg_route_waypoints', 'city_ids', 'waypoint_id',
                                                    string="Waypoint City IDS")
    pickup_readonly = fields.Boolean("Pickup readonly")
    drop_readonly = fields.Boolean("Drop readonly")

    @api.model
    def create(self, vals):
        wiz = self.env["cargo_sale_line_add_trip"].browse(vals.get("cargo_sale_line_trip_id"))
        if not vals.get('pickup_loc') or not vals.get('drop_loc'):
            if wiz.fleet_trip_id.trip_type != 'local':
                raise UserError(_("Please Select Pickup And Drop Location....!"))
            else:
                vals.update({
                    "pickup_loc": wiz.pickup_loc.id,
                    "drop_loc": wiz.drop_loc.id,
                })
        res = super(CargoSaleLineAddLineData, self).create(vals)
        return res


class CargoSaleLineAddTrip(models.TransientModel):
    _name = 'cargo_sale_line_add_trip'
    _description = "Cargo Sale Line Add Trip"

    fleet_trip_id = fields.Many2one(string="Trip ID", comodel_name="fleet.vehicle.trip",
                                    domain=[('state', 'not in', ['finished', 'cancelled', 'done'])])
    fleet_type = fields.Selection([
        ('all', 'All'), ('from_to', 'From-To')], default='all', string="Operation Type")
    route_id = fields.Many2one(string="Route", comodel_name="bsg_route", related="fleet_trip_id.route_id", store=True)
    vehicle_id = fields.Many2one(string="Vehicle", comodel_name="fleet.vehicle", related="fleet_trip_id.vehicle_id",
                                 store=True)
    driver_id = fields.Many2one(string="Driver", comodel_name="hr.employee", related="fleet_trip_id.driver_id",
                                store=True)
    cargo_sale_line_data_trip_ids = fields.One2many("cargo_sale_line_data_trip", "cargo_sale_line_trip_id")
    is_cargo_sale_line = fields.Boolean(string="IS Cargo Sale Line")
    pickup_loc = fields.Many2one('bsg_route_waypoints', string="Pickup Location")
    drop_loc = fields.Many2one('bsg_route_waypoints', string="Drop")

    @api.onchange('drop_loc', 'pickup_loc')
    def onchange_drop_loc(self):
        if self.pickup_loc:
            if self.pickup_loc == self.drop_loc:
                raise UserError('Drop location must be different from pickup location')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(CargoSaleLineAddTrip, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(result['arch'])
            active_ids = self.env.context.get('active_ids', [])
            lines = self.env["bsg_vehicle_cargo_sale_line"].search([("id", "in", active_ids)])
            if lines:
                route_from_loc = lines[0].loc_from
                route_to_loc = lines[0].loc_to
                user_branch = self.env.user.user_branch_id
                from_branch = route_from_loc.loc_branch_id
                to_branch = route_to_loc.loc_branch_id
                internal_loc = self.env["bsg_route_waypoints"].search([("route_waypoint_seq", "=", "GEN0337")])
                if user_branch == from_branch:
                    for node in doc.xpath("//field[@name='pickup_loc']"):
                        node.set('readonly', "1")
                        modifiers = json.loads(node.get("modifiers"))
                        modifiers['readonly'] = True
                        node.set("modifiers", json.dumps(modifiers))
                if user_branch == to_branch:
                    for node in doc.xpath("//field[@name='drop_loc']"):
                        node.set('readonly', "1")
                        modifiers = json.loads(node.get("modifiers"))
                        modifiers['readonly'] = True
                        node.set("modifiers", json.dumps(modifiers))
            result['arch'] = etree.tostring(doc, encoding='unicode')
        return result

    # put restriction
    @api.model
    def default_get(self, fields):
        res = super(CargoSaleLineAddTrip, self).default_get(fields)
        list_data = []
        for data in self._context.get('active_ids'):
            cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line'].sudo().browse(data)
            route_from_loc = cargo_sale_line.loc_from
            route_to_loc = cargo_sale_line.loc_to
            from_branch = route_from_loc.loc_branch_id
            to_branch = route_to_loc.loc_branch_id
            user_branch = self.env.user.user_branch_id
            internal_loc = self.env["bsg_route_waypoints"].search([("route_waypoint_seq", "=", "GEN0337")])
            if from_branch == user_branch:
                res.update({'pickup_loc': internal_loc.id})
            if to_branch == user_branch:
                res.update({'drop_loc': internal_loc.id})
            # if cargo_sale_line.cargo_sale_state not in ['done','pod']:
            # 	raise UserError(_("Please Confirm First Register Arrival....!")
            if self._context.get('so_type'):
                if self._context.get('so_type') == 'local_services_so':
                    # as told by muhammad.yousef
                    if not cargo_sale_line.state == 'Delivered':
                        if self.env.user.user_branch_id.id == cargo_sale_line.loc_to.loc_branch_id.id \
                                or self.env.user.user_branch_id.id == cargo_sale_line.drop_loc.loc_branch_id.id \
                                or self.env.user.user_branch_id.id == cargo_sale_line.loc_from.loc_branch_id.id \
                                or self.env.user.user_branch_id.id == cargo_sale_line.pickup_loc.loc_branch_id.id:
                            continue
                        else:
                            raise UserError(_("You can not Add to Trip ....!"))
                    if cargo_sale_line.state in ('draft','confirm'):
                        if self.env.user.user_branch_id.id == cargo_sale_line.loc_from.loc_branch_id.id \
                                or self.env.user.user_branch_id.id == cargo_sale_line.pickup_loc.loc_branch_id.id:
                            continue
                        else:
                            raise UserError(_("You can not Add to Trip ....!"))
            else:
                if cargo_sale_line.state in ['Delivered', 'done']:
                    raise UserError(_("You can not add So lines on state Devlivered or Done"))
                if self.env.user.user_branch_id.id == cargo_sale_line.loc_from.loc_branch_id.id \
                        or self.env.user.user_branch_id.id == cargo_sale_line.pickup_loc.loc_branch_id.id:
                    continue
                else:
                    raise UserError(_("You can not Add to Trip ....!"))
        return res

    @api.onchange('fleet_trip_id')
    def _onchange_fleet_trip_id(self):
        if not self.fleet_trip_id:
            self.is_cargo_sale_line = False
        if self.fleet_trip_id:
            self.is_cargo_sale_line = True
            list_data = []
            city_data = []
            waypoint_data = []
            for data in self.route_id.waypoint_to_ids:
                waypoint_data.append(data.waypoint.id)
                city_data.append(data.waypoint.id)
            waypoint_data.append(self.route_id.waypoint_from.id)
            for data in self._context.get('active_ids'):
                cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line'].sudo().browse(data)
                default_pickup = self.pickup_loc or (cargo_sale_line.loc_from if cargo_sale_line.loc_from.id in waypoint_data else False)
                default_drop_loc = self.drop_loc or (cargo_sale_line.loc_to if cargo_sale_line.loc_to.id in city_data else False)
                if self.fleet_trip_id.trip_type == "local" and cargo_sale_line.loc_to.not_local:
                    raise ValidationError(_("The drop location does not allow local trips"))

                list_data.append((0, 0, {'cargo_sale_line_id': cargo_sale_line.id,
                                         'loc_from': cargo_sale_line.loc_from.id or cargo_sale_line.return_loc_from.id,
                                         # 'pickup_loc': cargo_sale_line.loc_from.id if cargo_sale_line.loc_from.id in waypoint_data else False,
                                         'pickup_loc': default_pickup.id if default_pickup else False,
                                         'loc_to': cargo_sale_line.loc_to.id or cargo_sale_line.return_loc_to.id,
                                         'bsg_route_waypoints_line_ids': [(6, 0, waypoint_data)],
                                         'basg_route_waypoint_city_ids': [(6, 0, city_data)],
                                         'drop_loc': default_drop_loc.id if default_drop_loc else False,
                                         # 'drop_loc': cargo_sale_line.loc_to.id if cargo_sale_line.loc_to.id in city_data else False,
                                         }))
            if not self.cargo_sale_line_data_trip_ids:
                self.cargo_sale_line_data_trip_ids = list_data

            return {'domain': {
                'pickup_loc': [('id', 'in', waypoint_data)],
                'drop_loc': [('id', 'in', [data.waypoint.id for data in self.route_id.waypoint_to_ids])]
            }}

    @api.onchange('fleet_type')
    def _onchange_parent_id(self):
        id_list = []
        if self.fleet_type == 'from_to':
            search = self.env[self._context['active_model']].search([('id', 'in', self._context['active_ids'])],
                                                                    limit=1)
            for data in self.env['fleet.trip.arrival'].search(
                    [('waypoint_from', '=', search.loc_from.id), ('waypoint_to', '=', search.loc_to.id)]):
                id_list.append(data.trip_id.id)
            if self.env.user.has_group('bsg_trip_mgmt.group_create_trip_with_all_route_view'):
                return {
                    'domain': {
                        'fleet_trip_id': [('id', 'in', id_list), ('state', 'in', ['draft', 'on_transit', 'confirmed'])]}
                }
            else:
                return {
                    'domain': {'fleet_trip_id': ['|', (
                        'route_id.waypoint_to_ids.waypoint.loc_branch_id', '=', self.env.user.user_branch_id.id), (
                                                     'route_id.waypoint_from.loc_branch_id', '=',
                                                     self.env.user.user_branch_id.id),
                                                 ('state', 'in', ['draft', 'on_transit', 'confirmed']),
                                                 ('id', 'in', id_list)]}
                    # ('id', 'in', id_list),('route_id.waypoint_from.loc_branch_id','=',self.env.user.user_branch_id.id),('create_uid','=',self.env.user.id),
                }
        if self.fleet_type == 'all':
            search = self.env['fleet.vehicle.trip'].search([('state', 'in', ['draft', 'on_transit', 'confirmed'])])
            if self.env.user.has_group('bsg_trip_mgmt.group_create_trip_with_all_route_view'):
                return {
                    'domain': {'fleet_trip_id': [('id', 'in', search.ids)]}
                }
            else:
                return {
                    'domain': {'fleet_trip_id': ['|', (
                        'route_id.waypoint_to_ids.waypoint.loc_branch_id', '=', self.env.user.user_branch_id.id), (
                                                     'route_id.waypoint_from.loc_branch_id', '=',
                                                     self.env.user.user_branch_id.id), ('id', 'in', search.ids)]}
                    # ,('route_id.waypoint_from.loc_branch_id','=',self.env.user.user_branch_id.id),('create_uid','=',self.env.user.id)
                }

    @api.onchange('pickup_loc')
    def _onchange_pickup_loc(self):
        if self.pickup_loc and self.cargo_sale_line_data_trip_ids and self.fleet_trip_id:
            for line in self.cargo_sale_line_data_trip_ids:
                line.pickup_loc = self.pickup_loc.id

    @api.onchange('drop_loc')
    def _onchange_drop_loc(self):
        if self.drop_loc and self.cargo_sale_line_data_trip_ids and self.fleet_trip_id:
            for line in self.cargo_sale_line_data_trip_ids:
                line.drop_loc = self.drop_loc.id

    def add_trip(self):
        if self.fleet_trip_id.trip_type == 'local':
            for data in self.cargo_sale_line_data_trip_ids:
                cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line'].sudo().browse(data.cargo_sale_line_id.id)
                if cargo_sale_line.loc_to.is_internal:
                    raise UserError(_("You cant add SO line  location TO equal %s !!" % (
                        cargo_sale_line.loc_to.route_waypoint_name)))

        if self.fleet_trip_id.trip_type != 'auto':
            for data in self.env[self._context['active_model']].sudo().search(
                    [('id', 'in', self._context['active_ids'])]):
                if data.sudo().added_to_trip or data.sudo().fleet_trip_id:
                    raise UserError(_("In your selection a record already added to trip!"))

            for data in self.cargo_sale_line_data_trip_ids:
                cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line'].sudo().browse(data.cargo_sale_line_id.id)
                cargo_sale_line.sudo().write(
                    {'pickup_loc': data.pickup_loc.id, 'drop_loc': data.drop_loc.id, 'arrival_status': False, })
                self.env['bsg_vehicle_cargo_sale'].sudo().create_trip_picking(
                    data.cargo_sale_line_id,
                    data.pickup_loc,
                    data.drop_loc,
                    self.fleet_trip_id
                )
            for data in self.env[self._context['active_model']].sudo().search([('id', 'in', self._context['active_ids'])]):
                if not data.added_to_trip and not data.fleet_trip_id:
                    data.added_to_trip = True

            for data in self.env[self._context['active_model']].sudo().search([('id', 'in', self._context['active_ids'])]):
                if data.sudo().fleet_trip_id.state == 'on_transit':
                    data.sudo().fleet_trip_id.write({'total_on_transit_cars': data.sudo().fleet_trip_id.total_on_transit_cars + 1, })
        else:
            raise UserError(_("You have selected automatic trip please select manual trip to proceed."))

    def add_to_local_trip(self):
        if self.fleet_trip_id.trip_type == 'local':
            trip_so_lines = self.fleet_trip_id.mapped('stock_picking_id.picking_name.id')
            for data in self.cargo_sale_line_data_trip_ids:
                cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line'].sudo().browse(data.cargo_sale_line_id.id)
                # if cargo_sale_line.loc_to in self.fleet_trip_id.trip_waypoint_ids.mapped('waypoint'):
                #     raise UserError(_("Can't Add So Line %s To This Trip Has Location To in Trip Route!!" % (
                #         cargo_sale_line.sale_line_rec_name)))
                if cargo_sale_line.id in trip_so_lines:
                    raise UserError(
                        _("Recored %s is already added to this trip!!" % (cargo_sale_line.sale_line_rec_name)))
                if cargo_sale_line.loc_to.is_internal:
                    raise UserError(_("You cant add SO line  location TO equal %s !!" % (
                        cargo_sale_line.loc_to.route_waypoint_name)))

            for data in self.cargo_sale_line_data_trip_ids:
                cargo_sale_line = self.env['bsg_vehicle_cargo_sale_line'].sudo().browse(data.cargo_sale_line_id.id)
                if cargo_sale_line.loc_to.is_internal:
                    raise UserError(_("You cant add SO line  location TO equal %s !!" % (
                        cargo_sale_line.loc_to.route_waypoint_name)))

            for rec in self.env[self._context['active_model']].sudo().search(
                    [('id', 'in', self._context['active_ids'])]):
                # if data.sudo().added_to_local_trip:
                if rec.sudo().added_to_local_to_shipment_branch and rec.sudo().added_to_local_from_arriavl_branch:
                    raise UserError(
                        _("Record %s already added to local trip from customer to shipment branch and from arrival branch to customer location!" % (
                            rec.sale_line_rec_name)))
            for data in self.cargo_sale_line_data_trip_ids:
                cargo_sale_line = data.cs_line_id
                if data.drop_loc.id == cargo_sale_line.loc_from.id and cargo_sale_line.sudo().added_to_local_to_shipment_branch == True:
                    raise UserError(
                        _("Record %s already added to local trip from customer location to the shipment branach!" % (
                            cargo_sale_line.sale_line_rec_name)))
                if data.pickup_loc.id == cargo_sale_line.loc_to.id and cargo_sale_line.sudo().added_to_local_from_arriavl_branch == True:
                    raise UserError(
                        _("Record %s already added to local trip from arriavl branch to the customer location!" % (
                            cargo_sale_line.sale_line_rec_name)))
                cargo_sale_line.sudo().write({'arrival_status': False, })
                self.env['bsg_vehicle_cargo_sale'].sudo().create_trip_picking(
                    cargo_sale_line,
                    data.pickup_loc,
                    data.drop_loc,
                    self.fleet_trip_id
                )
                if data.drop_loc.id == cargo_sale_line.loc_from.id:
                    cargo_sale_line.sudo().added_to_local_to_shipment_branch = True
                if data.pickup_loc.id == cargo_sale_line.loc_to.id:
                    cargo_sale_line.sudo().added_to_local_from_arriavl_branch = True
            # cargo_sale_line.sudo().added_to_local_from_arriavl_branch = True
        # for data in self.env[self._context['active_model']].sudo().search([('id', 'in', self._context['active_ids'])]):
        # 	if drop_loc.id == data.branch_from:
        # 		added_to_local_to_shipment_branch = True
        # 	elif pickup_loc.id == data.branch_ro:
        # 		data.added_to_local_from_arriavl_branch = True
        else:
            raise UserError(_("You have selected other trips please select Local Service trip to proceed."))
