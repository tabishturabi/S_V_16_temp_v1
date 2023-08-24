# -*- coding: utf-8 -*-
import time
from datetime import datetime, date, time, timedelta
import datetime as dt
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from pytz import timezone, UTC
import logging

_logger = logging.getLogger(__name__)

from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, date_utils


class FleetVehicle(models.Model):
    _inherit = 'bsg_route'

    # 
    def _get_branches_of_route(self):
        list_data = []
        if self.waypoint_to_ids:
            for data in self.waypoint_to_ids:
                list_data.append(data.waypoint.loc_branch_id.id)
        self.branch_ids = [(6, 0, list_data)]

    branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="Branches", compute="_get_branches_of_route")


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    # @api.multi
    def name_get(self):
        res = []
        for vehicle in self:
            name = vehicle.taq_number
            res.append((vehicle.id, name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if self._context.get('route_id') or (self._context.get('is_trip_search') \
                                             and self._context.get('model') == 'fleet.vehicle.trip'):
            # '|',('license_plate',operator, name),\
            args = [('taq_number', operator, name), ('current_branch_id', '=', self._context.get('current_branch_id')),
                    ('state_id.in_service', '=', True)]
            search_id = self.env['fleet.vehicle'].search(
                ['|', ('bsg_route', '=', self._context.get('route_id')), ('bsg_route', '=', False)])
            domain = args or []
            domain += [
                ('id', 'in', search_id.ids)]
            rec = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
            # return self.browse(rec).name_get()
            return rec
        elif len(args) == 0:
            search_id = self.env['fleet.vehicle'].search([('taq_number', operator, name)])
            domain = args or []
            domain += [
                ('id', 'in', search_id.ids)]
            rec = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
            # return self.browse(rec).name_get()
            return rec
        elif name:
            args += [('taq_number', operator, name)]
            search_id = self.env['fleet.vehicle'].search([])
            domain = args or []
            domain += [('id', 'in', search_id.ids)]
            rec = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
            # return self.browse(rec).name_get()
            return rec
        return super(FleetVehicle, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                                                      name_get_uid=name_get_uid)

    # @api.depends('model_id.brand_id.name', 'model_id.name', 'license_plate','taq_number')
    def _compute_vehicle_name(self):
        res = super(FleetVehicle, self)._compute_vehicle_name()
        for record in self:
            record.name = record.model_id.brand_id.name + '/' + record.model_id.name + '/' + \
                          (record.license_plate or _('No Plate')) + '/' + (record.taq_number or _('No Sticker'))
        return res


class BsgFleetVehicleTrip(models.Model):
    _name = 'fleet.vehicle.trip'
    _description = "Trip"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    state = fields.Selection(string="State", selection=[
        ('draft', 'Draft'),
        ('on_transit', 'On Transit'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Operation'),
        ('done', 'Done'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled')

    ], default="draft", track_visibility=True, )

    # 
    def _get_payment(self):
        search_ids = self.env['account.payment'].search(
            [('is_pay_trip_money', '=', True), ('fleet_trip_id', '=', self.id), ('state', '!=', 'reversal_entry')])
        self.payment = len(search_ids)

    # @api.multi
    def name_get(self):
        result = []
        for trip in self:
            name = trip.name + " - " + (trip.route_id.route_name or " ")
            result.append((trip.id, name))
        return result

    # @api.multi
    # def get_ruh_current_datetime(self):
    #     '''Get the current datetime with the Mexican timezone.
    #     '''
    #     return fields.Datetime.context_timestamp(
    #         self.with_context(tz='Asia/Riyadh'), fields.Datetime.now())

    @api.model
    def _update_cargo_line_state(self):
        finished_trips = self.env['fleet.vehicle.trip'].search([('state', '=', 'finished')])
        for trip in finished_trips:
            for line in trip.stock_picking_id:
                if line.picking_name.state == 'shipped' or line.picking_name.state == 'draft':
                    line.picking_name.state = 'Delivered'

    # @api.multi
    def action_view_driver_reward(self):
        """
        This function returns an action that display existing payments of given
        account invoices.
        When only one found, show the payment immediately.
        """
        search_ids = self.env['account.payment'].search(
            [('is_pay_driver_rewards', '=', True), ('fleet_trip_id', '=', self.id)])
        return {
            'name': 'Name',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', search_ids.ids)],
            'context': {'create': False}
        }

    # @api.multi
    def action_view_payment(self):
        """
        This function returns an action that display existing payments of given
        account invoices.
        When only one found, show the payment immediately.
        """
        search_ids = self.env['account.payment'].search(
            [('is_pay_trip_money', '=', True), ('fleet_trip_id', '=', self.id), ('state', '!=', 'reversal_entry')])
        return {
            'name': 'Fuel Voucher',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', search_ids.ids)],
            'context': {'create': False}
        }

    # for checking for boolean is invoice paid or not
    # 
    def _get_voucher_info(self):
        for rec in self:
            rec.is_register_payment = False
            for data in rec.env['account.payment'].search(
                    [('is_pay_trip_money', '=', True), ('fleet_trip_id', '=', rec.id)]):
                for invoice_data in data.invoice_ids:
                    if invoice_data.state != 'posted':
                        rec.is_register_payment = False
                    else:
                        rec.is_register_payment = True

    # Register Payment
    # @api.multi
    def register_payment(self):
        view_id = self.env.ref('account.view_account_payment_register_form').id
        search_ids = self.env['account.payment'].search(
            [('is_pay_trip_money', '=', True), ('fleet_trip_id', '=', self.id)])
        journal_id = self.env['account.journal'].search([('type', '=', 'cash')], limit=1)
        amount = 0
        for data in search_ids.invoice_ids:
            amount += data.amount_residual
        if not journal_id:
            raise UserError(_("There is no cash journal defined please define in accounting."))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Name',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.payment',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_payment_type': 'outbound',
                'default_partner_id': search_ids.invoice_ids[0].partner_id.id,
                'default_partner_type': 'supplier',
                'default_amount': amount,
                'default_communication': self.name + ' ' + 'عبارة عن فروقات قيمة مصــروف الطريق لرحلـة رقــم',
                'default_is_pay_trip_money': True,
                'default_fleet_trip_id': self.id,
                'default_invoice_ids': [(4, search_ids.invoice_ids.id, None)]
            }
        }

    def _get_trip_type(self):
        list_of_trip_type = [('auto', 'تخطيط تلقائي'), ('manual', 'تخطيط يدوي'), ('local', 'خدمي')]
        if self.env.user.has_group('base.group_erp_manager'):
            return list_of_trip_type
        if self.env.user.has_group('bsg_trip_mgmt.group_plan_trip_manual') and self.env.user.has_group(
                'bsg_trip_mgmt.group_plan_trip_automatic'):
            list_of_trip_type = [('auto', 'تخطيط تلقائي'), ('manual', 'تخطيط يدوي'), ('local', 'خدمي')]
            return list_of_trip_type
        elif self.env.user.has_group('bsg_trip_mgmt.group_plan_trip_manual'):
            list_of_trip_type = [('manual', 'تخطيط يدوي')]
            return list_of_trip_type
        elif self.env.user.has_group('bsg_trip_mgmt.group_plan_trip_automatic'):
            list_of_trip_type = [('auto', 'تخطيط تلقائي'), ('local', 'خدمي')]
            return list_of_trip_type
        else:
            list_of_trip_type = [('auto', 'تخطيط تلقائي'),
                                 ('manual', 'تخطيط يدوي')]  # ,('local','خدمي') no need as per mr khaleed
            return list_of_trip_type

    @api.model
    def _get_route_domain(self):
        domain = []
        if self.env.user.has_group('bsg_trip_mgmt.group_create_trip_with_all_route_view'):
            id_list = self.env['bsg_route'].search([])
            domain = [('id', 'in', id_list.ids)]
        else:
            id_list = self.env['bsg_route'].search(
                [('waypoint_from.loc_branch_id', '=', self.env.user.user_branch_id.id)])
            domain = [('id', 'in', id_list.ids)]
            return domain

    # 
    def _get_trip_user_access(self):
        if self.route_id:
            if self.env.user.user_branch_id.id == self.route_id.waypoint_from.loc_branch_id.id:
                self.is_user_pay_trip_money = True
            else:
                self.is_user_pay_trip_money = False

    # 
    def _get_driver_payment(self):
        search_ids = self.env['account.payment'].search(
            [('is_pay_driver_rewards', '=', True), ('fleet_trip_id', '=', self.id)])
        self.driver_payment = len(search_ids)

    driver_payment = fields.Integer("Payment", compute="_get_driver_payment")
    payment = fields.Integer("Payment", compute="_get_payment")
    name = fields.Char(string="Reference", default="/", readonly=True)
    trip_name = fields.Char(string="Trip Name", default="/", compute="_compute_trip_name")
    active = fields.Boolean(string="Active", track_visibility=True, default=True)
    route_id = fields.Many2one(string="Route", comodel_name="bsg_route", domain=lambda self: self._get_route_domain(),
                               track_visibility=True, )
    driver_id = fields.Many2one(string="Driver", comodel_name="hr.employee", store=True, track_visibility=True, )
    driver_mobile_phone = fields.Char(related="driver_id.mobile_phone", string="Driver Phone")
    from_route_branch_id = fields.Many2one('bsg_branches.bsg_branches')
    driver_code = fields.Char(related="driver_id.driver_code", store=True)
    driver_rewards = fields.Selection(related="driver_id.driver_rewards", store=True,
                                      string='Driver Reward')
    vehicle_sticker_no = fields.Char(related="driver_id.vehicle_sticker_no", store=True)
    vehicle_id = fields.Many2one(string="Vehicle", comodel_name="fleet.vehicle")
    expected_start_date = fields.Datetime(string="Scheduled Start Date", required=True, default=fields.Datetime.now,
                                          track_visibility=True, )
    expected_end_date = fields.Datetime(string="Scheduled End Date", required=True, track_visibility=True, )
    d_date = fields.Datetime(string="Date", default=fields.Datetime.now)

    est_trip_time = fields.Float(string="Est. Duration", compute="_compute_time")
    trip_distance = fields.Float(string="Trip Distance", related="route_id.total_distance", store=True,
                                 track_visibility=True)
    operator_id = fields.Many2one(string="Operator", comodel_name="res.users", track_visibility=True, )
    description = fields.Text(string="Description", track_visibility=True, )
    stock_picking_id = fields.One2many(string="Stock Picking", comodel_name="fleet.vehicle.trip.pickings",
                                       inverse_name="bsg_fleet_trip_id")
    trip_waypoint_ids = fields.One2many(string="Trip Waypoints", comodel_name="fleet.vehicle.trip.waypoints",
                                        inverse_name="bsg_fleet_trip_id")
    total_capacity = fields.Integer(string="Actual capacity", track_visibility=True, )
    # This field is just for display purpose actual field is total_capacity
    display_capacity = fields.Integer(string="Available Space", compute="_get_trailer_capacity")
    bsg_trip_arrival_ids = fields.One2many(string="Arrival Ids", comodel_name="fleet.trip.arrival",
                                           inverse_name="trip_id")
    odometer_count = fields.Integer(string="Odometer Count", compute="_compute_odometer")
    is_done_fuel = fields.Boolean(string="Done Fuel")
    fuel_exp_method_id = fields.Many2one('bsg.fuel.expense.method', string='Fuel Expense Rule', track_visibility=True, )
    fuel_trip_amt = fields.Float(string='Fuel Expense Amount')
    additional_fuel_exp = fields.Float(string='Additional Reward Amount Backend')
    fuel_expense_type = fields.Selection([
        ('km', 'Per KM'),
        ('local', 'Local'),
        ('route', 'Route'),
        ('port', 'Port'),
        ('hybrid', 'Hybrid Route')], string="Fuel ExpenseMethod", track_visibility=True,
    )

    display_expense_mthod_id = fields.Many2one(related='fuel_exp_method_id', string='Fuel Expense Method',
                                               track_visibility=True)
    display_expense_type = fields.Selection(related="fuel_expense_type", string="Fuel Expense Type",
                                            track_visibility=True)

    truck_load = fields.Selection([
        ('full', 'Full Load'),
        ('empty', 'Empty Load')
    ], string="Practical Truck Load"
    )
    display_truck_load = fields.Selection(related="truck_load", string="Truck Load", track_visibility=True)
    # Speed logic for customer satisfaction need to be changed after hide button after click
    check_trip_money = fields.Boolean(string='Check Trip Money', )
    is_user_pay_trip_money = fields.Boolean(string="Is user Pay to trip money", compute="_get_trip_user_access")
    check_dispatch_report = fields.Boolean(string='Check Dispatch Report', default=True)
    check_start_trip = fields.Boolean(string='Check Start Trip', default=True, track_visibility=True, )
    trailer_category_id = fields.Many2one("bsg.trailer.categories",
                                          related="vehicle_id.trailer_id.trailer_categories_id",
                                          string='Trailer Category', store=True)
    is_given_drive_reward = fields.Boolean(string="Given Reward to Driver")
    trip_type = fields.Selection(_get_trip_type, track_visibility=True, string="Trip Type")
    next_branch_id = fields.Many2one(
        'bsg_branches.bsg_branches',
        string='Next Branch', track_visibility=True,
    )
    next_loc_id = fields.Many2one('bsg_route_waypoints', string='Next Location', track_visibility=True)
    current_loc_id = fields.Many2one('bsg_route_waypoints', string='Current Location', track_visibility=True)
    registered_branch_ids = fields.Many2many(
        'bsg_branches.bsg_branches',
        string='Registered Branch IDS', track_visibility=True,
    )
    check_user = fields.Boolean(
        string='Check User', compute="_compute_logged_user", track_visibility=True,
    )
    recurring = fields.Integer(string='Recurring', default=1, track_visibility=True)
    satha = fields.Boolean(related="vehicle_id.vehicle_type.satha", string='Satha Vehcile')
    extra_distance = fields.Integer(string="Extra Distance", track_visibility=True)
    extra_distance_amount = fields.Float(string="Extra Distance Amount", compute="_get_extra_distance_amount")
    total_fuel_amount = fields.Float(string="Total Fuel Expense", store=True, compute="_get_total_fuel_amount",
                                     track_visibility=True)

    tot_amount = fields.Integer(string="Total Amount", compute='_get_sum', store=True)
    total_on_transit_cars = fields.Integer(string="Total On Transit Cars")

    @api.depends('extra_distance', 'trip_distance')
    def _get_sum(self):
        for rec in self:
            rec.update({
                'tot_amount': rec.extra_distance + rec.trip_distance,
            })

    reason = fields.Text(string="Reason")
    cargo_sale_line_ids = fields.Many2many('bsg_vehicle_cargo_sale_line', string='So Lines')
    is_done_add_fuel = fields.Boolean(string='is_done_add_fuel')
    check_add_money = fields.Boolean(string='check_add_money')
    total_reward_amount = fields.Float(string="Total Reward amount Backend")
    capacity_threshold_limit = fields.Float(string="Threshold Limit", compute="_compute_capacity_threshold",
                                            track_visibility=True)
    capacity_threshold_percent = fields.Float(string="Actual Threshold", compute="_compute_capacity_threshold")
    tot_reward_amt_frontend = fields.Float(related='total_reward_amount', string="Total Reward amount")
    add_reward_amt_frontend = fields.Float(related='additional_fuel_exp', string="Additional Reward Amount",
                                           track_visibility=True)
    is_trip_started = fields.Boolean(string='Trip Started ?', default=False, help='This field is for checking trip is started or \
        not when it moves from draft state to confrim for the first time the value of this field will be True', )
    total_cars = fields.Integer(string='Total Cars')
    trailer_id = fields.Many2one('bsg_fleet_trailer_config', string='Trailer ID')
    # so_line_status_count = fields.Integer(string='So Line Count', compute="compute_so_line_status_count", store=True)
    register_arrival_btn_vistible = fields.Boolean(compute="compute_register_arrival_btn_vistible", store=True)
    is_register_payment = fields.Boolean(string="IS Visible Register Payment", compute="_get_voucher_info")
    standard_revenue = fields.Float(readonly=True)
    actual_revenue = fields.Float(readonly=True)
    is_rented = fields.Boolean()
    rented_vehicle_vendor = fields.Many2one('res.partner', "Rented Vehicle Vendor")
    trip_cost = fields.Float("Trip Cost")

    rented_driver_id = fields.Many2one('res.partner', string="Driver", track_visibility=True)
    rented_driver_mobile_phone = fields.Char(related="rented_driver_id.phone", store=True, string="Driver Phone")

    show_trip_money = fields.Boolean(compute='_compute_show_trip_money')
    from_route_dedicated_area_id = fields.Many2one('trucks.dedicating.area', string="Trucks Dedicated Area",
                                                   track_visibility=True)

    def _compute_show_trip_money(self):
        for rec in self:
            if rec.trip_waypoint_ids:
                if rec.env.user.has_group(
                        'bsg_trip_mgmt.group_trip_vehicle_show_trip_money') or rec.env.user.user_branch_id.id == \
                        rec.trip_waypoint_ids[0].waypoint.loc_branch_id.id:
                    rec.show_trip_money = True

    actual_start_datetime = fields.Datetime('Actual Start Date', readonly=True)
    start_branch = fields.Many2one('bsg_route_waypoints', 'Start Branch', readonly=True)
    actual_end_datetime = fields.Datetime('Actual End Date', readonly=True)
    end_branch = fields.Many2one('bsg_route_waypoints', 'End Branch', readonly=True)
    expected_trip_datetime = fields.Datetime('Expeced Trip Date', readonly=True)

    def get_current_tz_time(self, expected_date):
        tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        return UTC.localize(expected_date).astimezone(tz).replace(tzinfo=None)

    def get_schedule_start_date(self, o):
        if self.expected_start_date:
            schedule_start_date = self.expected_start_date
            if self.trip_waypoint_ids:
                waypoint_ids = self.trip_waypoint_ids.filtered(lambda l: l.waypoint.id == o.drop_loc.id)
                for waypoint_id in waypoint_ids:
                    if waypoint_id:
                        if waypoint_id.delivered_items_count > 0:
                            trip_waypoint_id = waypoint_id.waypoint
                            if trip_waypoint_id:
                                if self.route_id.waypoint_to_ids:
                                    estimated_time = 0.0
                                    actual_route_waypoint_id = False
                                    for route_waypoint_id in self.route_id.waypoint_to_ids:
                                        if route_waypoint_id:
                                            if route_waypoint_id.waypoint.id != trip_waypoint_id.id:
                                                estimated_time += route_waypoint_id.estimated_time
                                            else:
                                                actual_route_waypoint_id = route_waypoint_id
                                                break;
                                    if actual_route_waypoint_id:
                                        estimated_time += actual_route_waypoint_id.estimated_time
                                        estimated_time = round(estimated_time, 2)
                                        h = str(estimated_time).split('.')[0]
                                        h = int(h)
                                        m = str(estimated_time).split('.')[1]
                                        m = int(m)
                                        schedule_start_date = schedule_start_date + timedelta(hours=h, minutes=m)
                                        schedule_start_date = self.get_current_tz_time(schedule_start_date)
            return schedule_start_date

    # @api.multi
    @api.depends('bsg_trip_arrival_ids', 'bsg_trip_arrival_ids.actual_end_time')
    def compute_register_arrival_btn_vistible(self):
        for rec in self:
            if rec.bsg_trip_arrival_ids:
                if not all(rec.bsg_trip_arrival_ids.mapped('actual_end_time')):
                    rec.register_arrival_btn_vistible = True
                else:
                    rec.register_arrival_btn_vistible = False

    # @api.multi
    # @api.depends('bsg_trip_arrival_ids', 'bsg_trip_arrival_ids.is_done_survey')
    # def compute_so_line_status_count(self):
    # 	for rec in self:
    # 		if rec.stock_picking_id:
    # 			rec.so_line_status_count = len(rec.stock_picking_id.filtered(lambda line:line.state == 'shipped'))
    # 		else:
    # 			rec.so_line_status_count = 1

    # 
    def _compute_logged_user(self):
        for rec in self:
            rec.check_user = False
            if rec.next_branch_id:
                if rec.env.user.user_branch_id.id == rec.next_branch_id.id:
                    rec.check_user = True
                else:
                    rec.check_user = False

    def _compute_odometer(self):
        Odometer = self.env['fleet.vehicle.odometer']
        for record in self:
            record.odometer_count = Odometer.search_count(
                [('vehicle_id', '=', record.vehicle_id.id), ('fleet_trip_id', '=', record.id)])

    # Compute Trip Name
    # 
    @api.depends('name', 'route_id')
    def _compute_trip_name(self):
        if self.name or self.route_id:
            self.trip_name = self.name + " - " + (self.route_id.route_name or " ")

    # get default capacity for display field
    # as told by mr hamdan
    # 
    @api.depends('total_capacity')
    def _get_trailer_capacity(self):
        self.display_capacity = False
        if self.total_capacity:
            self.display_capacity = self.total_capacity

    # 
    @api.depends('expected_start_date', 'expected_end_date')
    def _compute_time(self):
        for rec in self:
            rec.est_trip_time = 0
            if rec.expected_start_date and rec.expected_end_date:
                start_time = rec.expected_start_date
                end_time = rec.expected_end_date
                time_delta_in_seconds = (end_time - start_time).total_seconds()
                timedelta_in_hours, second_reminder = divmod(time_delta_in_seconds, 3600)
                rec.est_trip_time = timedelta_in_hours

    @api.onchange('fuel_exp_method_id', 'fuel_expense_type', 'truck_load')
    def _onchange_fuel_fields(self):
        self.compute_fuel_trip_amt()

    def compute_fuel_trip_amt(self):
        if self.route_id and self.fuel_exp_method_id and self.vehicle_id and self.vehicle_id.trailer_id and self.vehicle_id.trailer_id.trailer_categories_id:
            if self.fuel_expense_type in ['km', 'hybrid']:
                if self.truck_load == 'full':
                    if self.driver_id.driver_rewards and self.driver_id.driver_rewards in ['by_delivery',
                                                                                           'by_delivery_b',
                                                                                           'by_revenue']:
                        self.fuel_trip_amt = round(self.route_id.total_distance * self.fuel_exp_method_id.full_load_amt)
                    else:
                        self.fuel_trip_amt = round(
                            self.route_id.total_distance * self.fuel_exp_method_id.amt_full_without_reward)
                elif self.truck_load == 'empty':
                    if self.driver_id.driver_rewards and self.driver_id.driver_rewards in ['by_delivery',
                                                                                           'by_delivery_b',
                                                                                           'by_revenue']:
                        self.fuel_trip_amt = round(
                            self.route_id.total_distance * self.fuel_exp_method_id.empty_load_amt)
                    else:
                        self.fuel_trip_amt = round(
                            self.route_id.total_distance * self.fuel_exp_method_id.amt_empty_without_reward)
            elif self.fuel_expense_type in ['route']:
                # self.fuel_trip_amt = round(self.fuel_exp_method_id.fuel_amount)
                self.fuel_trip_amt = round(self.fuel_exp_method_id.expense_amount)

            elif self.fuel_expense_type in ['port', 'local']:
                port_rule = self.env['bsg.port.fuel.amount'].search([
                    ('rule_option', '=', self.fuel_exp_method_id.port_rule_option),
                    ('distance_from', '<=', self.trip_distance),
                    ('distance_to', '>=', self.trip_distance),
                    ('vehicle_type', '=', self.vehicle_id.vehicle_type.id),
                    ('route_type', '=', self.route_id.route_type),
                ], limit=1)
                if port_rule:
                    if self.fuel_exp_method_id.port_rule_option == 'trip' and self.vehicle_id:
                        if self.vehicle_id.daily_trip_count == 0:
                            self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                     company_id=self.env.user.company_id.id).vehicle_id.write(
                                {'daily_trip_count': 1})
                        trip_fuel = self.env['bsg.port.fuel.trip'].search([
                            ('fuel_trip_config_id', '=', port_rule.id),
                            ('loc_from', '<=', self.vehicle_id.daily_trip_count),
                            ('loc_to', '>=', self.vehicle_id.daily_trip_count),
                        ], limit=1)
                        if trip_fuel:
                            self.fuel_trip_amt = round(trip_fuel.amount)
                    else:
                        car_fuel = 0
                        for line in self.stock_picking_id.filtered(lambda l: not l.picking_name.is_package):
                            car_fuel += self.env['bsg.port.fuel.car'].search([
                                ('fuel_trip_config_id', '=', port_rule.id),
                                ('car_size_id', '=', line.picking_name.car_size.id),
                            ], limit=1).amount
                        if car_fuel:
                            self.fuel_trip_amt = round(car_fuel)

            if self.fuel_expense_type == 'hybrid':
                port_rule = self.env['bsg.port.fuel.amount'].search([
                    ('rule_option', '=', self.fuel_exp_method_id.port_rule_option),
                    ('distance_from', '<=', self.trip_distance),
                    ('distance_to', '>=', self.trip_distance),
                    ('vehicle_type', '=', self.vehicle_id.vehicle_type.id),
                    ('route_type', '=', self.route_id.route_type),
                ], limit=1)
                if port_rule:
                    if self.fuel_exp_method_id.port_rule_option == 'trip' and self.vehicle_id:
                        if self.vehicle_id.daily_trip_count == 0:
                            self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                     company_id=self.env.user.company_id.id).vehicle_id.write(
                                {'daily_trip_count': 1})
                        trip_fuel = self.env['bsg.port.fuel.trip'].search([
                            ('fuel_trip_config_id', '=', port_rule.id),
                            ('loc_from', '<=', self.vehicle_id.daily_trip_count),
                            ('loc_to', '>=', self.vehicle_id.daily_trip_count),
                        ], limit=1)
                        if trip_fuel:
                            self.total_reward_amount = round(trip_fuel.amount)
                    else:
                        car_fuel = 0
                        for line in self.stock_picking_id.filtered(lambda l: not l.picking_name.is_package):
                            car_fuel += self.env['bsg.port.fuel.car'].search([
                                ('fuel_trip_config_id', '=', port_rule.id),
                                ('car_size_id', '=', line.picking_name.car_size.id),
                            ], limit=1).amount
                        if car_fuel:
                            self.total_reward_amount = round(car_fuel)

    # if self.recurring:
    # 	self.fuel_trip_amt = round(self.fuel_trip_amt * self.recurring)

    # 
    @api.depends('route_id', 'fuel_exp_method_id', 'extra_distance')
    def _get_extra_distance_amount(self):
        self.extra_distance_amount = 0
        if self.extra_distance and self.fuel_exp_method_id and self.route_id:
            if self.fuel_expense_type in ['km', 'hybrid']:
                if self.truck_load == 'full':
                    if self.driver_id.driver_rewards and self.driver_id.driver_rewards in ['by_delivery',
                                                                                           'by_delivery_b',
                                                                                           'by_revenue']:
                        self.extra_distance_amount = round(self.extra_distance * self.fuel_exp_method_id.full_load_amt)
                    else:
                        self.extra_distance_amount = round(
                            self.extra_distance * self.fuel_exp_method_id.amt_full_without_reward)
                elif self.truck_load == 'empty':
                    if self.driver_id.driver_rewards and self.driver_id.driver_rewards in ['by_delivery',
                                                                                           'by_delivery_b',
                                                                                           'by_revenue']:
                        self.extra_distance_amount = round(self.extra_distance * self.fuel_exp_method_id.empty_load_amt)
                    else:
                        self.extra_distance_amount = round(
                            self.extra_distance * self.fuel_exp_method_id.amt_empty_without_reward)

    # 
    @api.depends('fuel_trip_amt', 'extra_distance', 'fuel_exp_method_id', 'route_id')
    def _get_total_fuel_amount(self):
        self.total_fuel_amount = 0
        if self.extra_distance_amount != 0:
            self.total_fuel_amount = self.fuel_trip_amt + self.extra_distance_amount
        else:
            self.total_fuel_amount = self.fuel_trip_amt

    @api.onchange('route_id')
    def _onchange_route_id(self):
        if self.route_id:
            self.from_route_branch_id = self.route_id.waypoint_from.loc_branch_id.id
            self.trip_waypoint_ids = False
            # Creation of only Source or From Waypoint
            self.trip_waypoint_ids |= self.trip_waypoint_ids.new({
                'waypoint': self.route_id.waypoint_from.id,
            })
            # Creation of all the To or Destination Waypoints
            waypoint_ids = sorted(self.route_id.waypoint_to_ids, key=lambda x: x['sequence'])
            for line in waypoint_ids:
                self.trip_waypoint_ids |= self.trip_waypoint_ids.new({
                    'waypoint': line.waypoint.id
                })
            # Creation of all connecting routes
            self.bsg_trip_arrival_ids = False
            stating_loc = self.route_id.waypoint_from.id
            for loc in waypoint_ids:
                self.bsg_trip_arrival_ids |= self.bsg_trip_arrival_ids.new({
                    'waypoint_from': stating_loc,
                    'waypoint_to': loc.waypoint.id,
                })
                stating_loc = loc.waypoint.id

            # Getting Fuel methods
            self.fuel_expense_type = self.route_id.route_type

            # getting expected end-date
            self.expected_end_date = fields.Datetime.now() + timedelta(hours=self.route_id.estimated_time)
            # setting vehicle id false
            self.vehicle_id = False
            self.from_route_dedicated_area_id = self.route_id.waypoint_to_ids[-1].waypoint.location_dedicated_area_id.id if len(self.route_id.waypoint_to_ids) > 0 else False

    @api.onchange('expected_start_date', 'expected_end_date')
    def _onchange_sch_dates(self):
        if self.expected_start_date:
            if self.route_id:
                self.expected_end_date = self.expected_start_date + timedelta(hours=self.route_id.estimated_time)

                if self.route_id and self.vehicle_id:
                    prev_trip_recs = self.env['fleet.vehicle.trip'].search(
                        [('state', 'not in', ['finished', 'cancelled']), ('vehicle_id', '=', self.vehicle_id.id)])
                    for rec in prev_trip_recs:
                        if self.expected_end_date >= self.expected_start_date:
                            raise UserError(_("A trip for this Truck is already planned for given dates!"))
        if self.expected_end_date and self.expected_start_date:
            if self.expected_end_date <= self.expected_start_date:
                raise UserError(_("Scheduled End Date cant be less or same as Scheduled Start Date"))

    @api.onchange('vehicle_id', 'route_id')
    def _onchange_dedicated_area_vehicle_id(self):
        for record in self:
            if record.from_route_dedicated_area_id and record.vehicle_id.fleet_dedicated_area_ids.ids:
                if record.from_route_dedicated_area_id.id not in record.vehicle_id.fleet_dedicated_area_ids.ids:
                    list_name = " , ".join(data.name for data in record.vehicle_id.fleet_dedicated_area_ids)
                    record.vehicle_id = False
                    raise ValidationError(
                        ('This Fleet is Dedicated to ({}) Area, Please contact operation department.').format(
                            list_name))

    @api.onchange('vehicle_id', 'route_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id and self.route_id:
            if self.vehicle_id.trailer_id:
                self.trailer_id = self.vehicle_id.trailer_id.id
                self.total_capacity = (self.vehicle_id.trailer_id.trailer_capacity * self.recurring) - len(
                    self.stock_picking_id)
                if self.fuel_expense_type:
                    vehicle_type = self.vehicle_id.vehicle_type.id
                    domain = [('vehicle_type', '=', vehicle_type), ('fuel_expense_type', '=', self.fuel_expense_type)]
                    if self.fuel_expense_type == 'route':
                        domain.append(('route_id', '=', self.route_id.id))
                    fuel_exp_rule = self.env['bsg.fuel.expense.method'].search(domain, limit=1)
                    if fuel_exp_rule:
                        self.fuel_exp_method_id = fuel_exp_rule.id
                    else:
                        raise UserError(_("Fuel expense rule not found for this vehicle please define one."))

            else:
                self.total_capacity = 0
        else:
            self.total_capacity = 8
        if self.vehicle_id and not self.vehicle_id.rented_vehicle:
            self.driver_id = False
            self.rented_driver_id
            self.is_rented = False
            if not self.vehicle_id.bsg_driver:
                raise UserError(_("This Vehicle is without driver you need to set driver first!"))
            else:
                self.driver_id = self.vehicle_id.bsg_driver.id
        elif self.vehicle_id.rented_vehicle:
            self.driver_id = False
            self.rented_driver_id
            self.is_rented = True
            contract_id = self.env['fleet.vehicle.log.contract'].sudo().search(
                [('vehicle_id', '=', self.vehicle_id.id)], limit=1)
            if not contract_id:
                raise UserError(_("This Vehicle Is Rented But No Contract For it!"))
            else:
                self.rented_vehicle_vendor = contract_id.insurer_id.id
                self.trip_cost = contract_id.amount
                self.rented_driver_id = contract_id.purchaser_id.id

    @api.onchange('recurring')
    def _onchange_recurring_value(self):
        if self.recurring:
            if self.vehicle_id.trailer_id:
                self.total_capacity = (self.vehicle_id.trailer_id.trailer_capacity * self.recurring) - len(
                    self.stock_picking_id.filtered(lambda l: not l.picking_name.is_package))
            self.compute_fuel_trip_amt()

    # #Check state if finished then it add 1 to daily trip count
    # @api.onchange('state')
    # def _onchange_state(self):
    # 	if self.state and self.state == 'finished':
    # 		self.vehicle_id.daily_trip_count += 1

    # @api.multi
    def action_confirm(self):
        # Commented due to bassami demand for allowing empty dispatch
        # if len(self.stock_picking_id) == 0 and self.fuel_expense_type != 'port':
        # 		raise UserError(_("No Found Any Picking of These Records"))
        # elif len(self.stock_picking_id) == 0 and self.fuel_expense_type == 'port':
        # 	return self.write({'state': 'confirmed'})
        if self.state in ['finished', 'cancelled']:
            raise UserError(_("Trip already in finished or cancelled state"))
        message = 'There are %s out %s cars space left do you still wish to proceed without filling them?' % (
            len(self.stock_picking_id.filtered(lambda l: not l.picking_name.is_package)), self.total_capacity)
        error_msg = "There are %s out %s cars space left please fill them first..or change the recurring number to total vehicles!" % (
            len(self.stock_picking_id.filtered(lambda l: not l.picking_name.is_package)), self.total_capacity)
        if self.recurring > 1:
            if self.total_capacity != 0:
                raise UserError(_(error_msg))
        self.env.ref('bsg_trip_mgmt.calculate_value_wizard_action')
        data = {'default_id': self.id, 'default_yes_no': message}
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calculate.value.wizard',
            'view_id': self.env.ref('bsg_trip_mgmt.calculate_value_wizard_form').id,
            'view_mode': 'form',
            'view_type': 'form',
            'context': data,
            'target': 'new',
        }

    # @api.multi
    def action_cancel(self):
        for rec in self:
            if rec.stock_picking_id:
                raise ValidationError(_("You can not cancel Trip.....!"))
            else:
                self.write({'state': 'cancelled'})

    # @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})

    # @api.multi
    def action_on_transit(self):
        records_len = len([(number, line) for number, line in enumerate(self.bsg_trip_arrival_ids, 1) \
                           if not line.is_done_survey])
        if records_len <= 0:
            # self.vehicle_id.daily_trip_count += 1

            # for so_line in self.stock_picking_id:
            # 	so_line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.single_trip_history()
            return self.write({'state': 'finished'})
        return self.write({'state': 'on_transit'})

    # For Printing Dispatching Voucher
    # @api.multi
    def action_print_dispatch(self):
        # return self.env.ref('bsg_cargo_sale.report_cs_delivery_report').report_action(self.id)
        self.write({'check_dispatch_report': True})
        self.write({'check_start_trip': False})
        return self.env.ref('bsg_trip_mgmt.report_dispatch_template_report').report_action(self.id)

    # for reloading arrival lines a
    # @api.multi
    def action_get_arrival(self):
        if not self.bsg_trip_arrival_ids:
            if self.route_id:
                stating_loc = self.route_id.waypoint_from.id
                for loc in self.route_id.waypoint_to_ids:
                    self.bsg_trip_arrival_ids |= self.bsg_trip_arrival_ids.new({
                        'waypoint_from': stating_loc,
                        'waypoint_to': loc.waypoint.id,
                    })
                    stating_loc = loc.waypoint.id
            for line in self.stock_picking_id:
                self._update_arriva_lines(line.picking_name.id, line.loc_from.id, line.loc_to.id)

    # @api.multi
    def action_add_to_trip(self):
        if self.trip_type != 'auto':

            for data in self.cargo_sale_line_ids:
                if data.sudo().with_context(force_company=self.env.user.company_id.id,
                                            company_id=self.env.user.company_id.id).added_to_trip or data.sudo().with_context(
                        force_company=self.env.user.company_id.id,
                        company_id=self.env.user.company_id.id).fleet_trip_id:
                    raise UserError(_("In your selection a record already added to trip!"))

            for data in self.cargo_sale_line_ids:
                data.sudo().with_context(force_company=self.env.user.company_id.id,
                                         company_id=self.env.user.company_id.id).write(
                    {'pickup_loc': data.pickup_loc.id, 'drop_loc': data.drop_loc.id})
                self.env['bsg_vehicle_cargo_sale'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                       company_id=self.env.user.company_id.id).create_trip_picking(
                    data,
                    data.pickup_loc,
                    data.drop_loc,
                    self.env['fleet.vehicle.trip'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                       company_id=self.env.user.company_id.id).browse(
                        self.id)
                )
            for data in self.cargo_sale_line_ids:
                if not data.added_to_trip and not data.fleet_trip_id:
                    data.sudo().with_context(force_company=self.env.user.company_id.id,
                                             company_id=self.env.user.company_id.id).added_to_trip = True
        else:
            raise UserError(_("You have selected automatic trip please select manual trip to proceed."))

    def _update_arriva_lines(self, so_line_id, loc_from, loc_to):
        if loc_from and loc_to:
            for line in self.bsg_trip_arrival_ids:
                line.arrival_line_ids.create({
                    'arrival_id': line.id,
                    'delivery_id': so_line_id,
                })

    # for paying driver Reward money
    # @api.multi
    def pay_driver_reward(self):
        total_reward_point = 0
        is_driver_reward_given_val = []
        total_deducation = 0
        payment_method = self.env.ref('account.account_payment_method_manual_in')
        search_id = self.env['account.fuel.trip.configuration'].search([])
        for line_data in self.bsg_trip_arrival_ids:
            is_driver_reward_given_val.append(line_data.is_driver_reward_given)
            if (line_data.trip_id.driver_id.driver_rewards == 'by_delivery') \
                    or (line_data.trip_id.driver_id.driver_rewards == 'by_delivery_b'):
                if line_data.is_driver_reward_given:
                    total_reward_point += line_data.driver_reward_amount
                    total_deducation += line_data.driver_deduction
                else:
                    total_reward_point += line_data.driver_reward_amount
                    total_deducation += line_data.driver_deduction
            else:
                total_car = 0
                for car_data in line_data.arrival_line_ids:
                    total_car += car_data.delivery_id.car_size.trailer_capcity

                self.env['employee_reward_history'].create({'trip_id': line_data.trip_id.id,
                                                            'employee_id': line_data.trip_id.driver_id.id,
                                                            'reward_type': 'by_delivery',
                                                            'currency_id': line_data.env.user.company_id.currency_id.id,
                                                            'reward_amount': line_data.driver_reward_amount,
                                                            'fine_amount': line_data.driver_deduction,
                                                            'state': 'paid',
                                                            'waypoint_from': line_data.waypoint_from.id,
                                                            'waypoint_to': line_data.waypoint_to.id,
                                                            'no_of_cars': int(total_car)})

        if False in is_driver_reward_given_val:
            search_partner = self.env['res.partner'].search([('name', '=', str(self.driver_id.name))], limit=1)
            if not search_partner:
                search_partner_type = self.env['partner.type'].search([('is_vendor', '=', True)], limit=1)
                search_partner = self.env['res.partner'].create({'name': self.driver_id.name,
                                                                 'customer': False,
                                                                 'supplier': True,
                                                                 'partner_types': search_partner_type.id if search_partner_type else False})
                search_partner._onchange_partner_types()
            # for getting branch from jounal
            journal_id = self.env['account.journal'].search(
                [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash']),
                 ('sub_type', 'in', ['Payment'])], limit=1)
            if journal_id.branches:
                branch_id = journal_id.branches[0].id
            else:
                branch_id = False

            create_voucher = self.env['account.payment'].create({'payment_type': 'outbound',
                                                                 'partner_type': 'supplier',
                                                                 'branch_ids': branch_id,
                                                                 'is_voucher_or_expense': True,
                                                                 'is_pay_driver_rewards': True,
                                                                 'payment_reference': line_data.trip_id.name,
                                                                 'fleet_trip_id': line_data.trip_id.id,
                                                                 'partner_id': search_partner.id,
                                                                 'amount': (total_reward_point - total_deducation),
                                                                 'collectionre': line_data.trip_id.name,
                                                                 'journal_id': journal_id.id,
                                                                 'date': str(fields.Date.today()),
                                                                 'payment_method_id': payment_method.id
                                                                 })

            line_data_search = self.env['fleet.trip.arrival'].search(
                [('trip_id', '=', self.id), ('is_driver_reward_given', '=', False)], limit=1)

            payment_line = self.env['account.voucher.line.custom'].create({'payment_id': create_voucher.id,
                                                                           'account_id': search_id.trip_account.id,
                                                                           'analytic_id': search_id.trip_analytical_account_id.id})
            total_car = 0
            for car_data in line_data_search.arrival_line_ids:
                total_car += car_data.delivery_id.car_size.trailer_capcity
            if (total_reward_point - total_deducation) != 0:
                self.env['employee_reward_history'].create({'trip_id': line_data_search.trip_id.id,
                                                            'employee_id': line_data_search.trip_id.driver_id.id,
                                                            'reward_type': 'by_delivery',
                                                            'currency_id': self.env.user.company_id.currency_id.id,
                                                            'reward_amount': (total_reward_point - total_deducation),
                                                            'fine_amount': total_deducation,
                                                            'state': 'paid',
                                                            'waypoint_from': line_data_search.waypoint_from.id,
                                                            'waypoint_to': line_data_search.waypoint_to.id,
                                                            'no_of_cars': int(total_car)})
        self.is_given_drive_reward = True

    #  Prepare Invoice
    # @api.multi
    def _prepare_invoice(self, partner_id):
        self.ensure_one()
        journal_id = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        if not journal_id:
            raise UserError(_("Be Sure You Have Cash Journal With Waypoints"))
        Config = self.env.user.company_id


        # Migration Note
        # 'account_id': partner_id.property_account_payable_id.id,

        invoice_vals = {
            'name': '',
            'ref': self.name,
            'move_type': 'in_invoice',
            'is_fleet_operation': True,
            'invoice_cash_rounding_id': Config.sudo().cash_rounding_id.id,
            'partner_id': partner_id.id,
            'journal_id': journal_id.id,
            'narration': self.name,
            'currency_id': self.env.user.company_id.currency_id.id,
            'user_id': self.env.user.id,
            'invoice_date_due': fields.Date.today(),
            'invoice_date': fields.Date.today(),
            'date': fields.Date.today(),
        }
        return invoice_vals

    #  Prepare Invoice Line
    # @api.multi
    def _prepare_invoice_line(self, inv_id, account_id, analytic_id, analytic_tags, product_id, amount, tax_ids,
                              fleet_id):
        is_pay_fuel_diff = self._context.get('is_pay_fuel_diff', False)
        name = not is_pay_fuel_diff and product_id.name or product_id.name + " difference"
        data = {
            'product_id': product_id.id,
            'name': name,
            'account_id': account_id,
            'price_unit': amount,
            'quantity': 1,
            'move_id': inv_id,
            'fleet_id': fleet_id,
            'date_maturity': fields.Date.today(),
            'bsg_branches_id': self.env.user.user_branch_id.id,
            'tax_ids': [(6, 0, tax_ids.ids)] if tax_ids else [(6, 0, [])],
        }
        return data

    # @api.multi
    def pay_trip_money_diff(self):
        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']
        search_id = self.env['account.fuel.trip.configuration'].search([])
        if not search_id.fuel_expense_account_id or not search_id.fuel_expense_analytical_account_id:
            raise UserError(_("Go To Accouting --> Configuration --> Add Rewards and Fuel Configuration"))
        journal_id = self.env['account.journal'].search(
            ['|', ('sub_type', 'in', ['All']), ('sub_type', 'in', ['Payment']),
             ('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash'])], limit=1)
        fule_product = self.env['product.product'].search([('is_fuel_expense', '=', True)], limit=1)
        if not journal_id:
            raise UserError(_("Be Sure You Have Cash Journal With Waypoints"))
        if not self.driver_id:
            raise UserError(_("Be Sure You Have Select Drive"))
        if journal_id.branches:
            branch_id = journal_id.branches[0].id
        else:
            branch_id = False
        payment_method = self.env.ref('account.account_payment_method_manual_in')
        res = []
        for rec in self:
            if rec.is_done_fuel:
                payment_id = self.env['account.payment'].search(
                    [('is_pay_trip_money', '=', True), ('fleet_trip_id', '=', rec.id)])
                if payment_id:
                    # tax_amount = sum(fule_product.taxes_id.mapped('amount'))/100
                    fuel_amount = rec.display_expense_type not in ['km', 'hybrid'] and rec.total_fuel_amount or (
                        rec.total_fuel_amount) + rec.tot_reward_amt_frontend
                    if fuel_amount > payment_id.amount:
                        fuel_amount -= payment_id.amount
                        search_partner = self.env['res.partner'].browse(self.driver_id.partner_id.id)
                        inv_data = rec._prepare_invoice(search_partner)
                        invoice = inv_obj.create(inv_data)
                        fleet_id = rec.vehicle_id.id
                        account_id = search_id.fuel_expense_account_id.id
                        analytic_id = self.vehicle_id.vehicle_type.analytic_account_id.id if self.vehicle_id.vehicle_type.analytic_account_id else False
                        analytic_tags = self.vehicle_id.vehicle_type.analytic_tag_ids.ids if self.vehicle_id.vehicle_type.analytic_tag_ids else []
                        tax_ids = []
                        inv_line_obj.create(
                            rec.with_context({'is_pay_fuel_diff': True})._prepare_invoice_line(invoice.id, account_id,
                                                                                               analytic_id,
                                                                                               analytic_tags,
                                                                                               fule_product,
                                                                                               fuel_amount,
                                                                                               fule_product.supplier_taxes_id,
                                                                                               fleet_id))
                        invoice._compute_amount()
                        invoice._onchange_cash_rounding()
                        invoice.action_post()
                        invoice_list = []
                        invoice_list.append(invoice.id)
                        create_voucher = self.env['account.payment'].with_context(
                            search_default_inbound_filter=True).create({'payment_type': 'outbound',
                                                                        'partner_type': 'supplier',
                                                                        'is_voucher_or_expense': True,
                                                                        'ref': str(
                                                                            rec.name) + ' ' + 'عبارة عن فروقات قيمة مصــروف الطريق لرحلـة رقــم',
                                                                        'payment_reference': rec.name,
                                                                        'partner_id': search_partner.id,
                                                                        'amount': invoice.amount_total,
                                                                        'journal_id': journal_id.id,
                                                                        'fleet_trip_id': rec.id,
                                                                        'is_pay_trip_money': True,
                                                                        'date': str(fields.Date.today()),
                                                                        'collectionre': rec.name,
                                                                        'branch_ids': branch_id,
                                                                        'invoice_ids': [(6, 0, invoice_list)],
                                                                        'payment_method_id': payment_method.id
                                                                        })
                        create_voucher.post_state()
                        create_voucher.action_post()
                    else:
                        raise UserError(_("Fuel amount on trip must be greater than voucher amount!"))
                else:
                    raise UserError(_("Use pay trip money button"))

    # For Paying Trip Money and made payment voucher
    # @api.multi
    def pay_trip_money(self):
        fleet_id = False
        account_id = False
        analytic_id = False

        if self.state == 'cancelled':
            raise UserError(_("Payment is not allowed when trip status is cancelled"))

        if self.vehicle_id and self.route_id:
            if not self.env['fleet.vehicle.odometer'].search([
                ('fleet_trip_id', '=', self.id),
                ('vehicle_id', '=', self.vehicle_id.id),
                ('src_location', '=', self.route_id.waypoint_from.id),
                ('dest_location', '=', self.route_id.waypoint_to_ids[-1].waypoint.id)
            ], limit=1):
                vehicle_odometer_id = self.env['fleet.vehicle.odometer'].create({
                    'vehicle_id': self.vehicle_id.id,
                    'fleet_trip_id': self.id,
                    'src_location': self.route_id.waypoint_from.id,
                    'dest_location': self.route_id.waypoint_to_ids[-1].waypoint.id,
                    'bsg_driver': self.driver_id.id if self.driver_id else False,
                    'extra_distance': self.extra_distance if self.extra_distance else False,
                    'trip_distance': self.trip_distance if self.trip_distance else False,
                    'value': self.tot_amount + self.vehicle_id.odometer,
                    'date': self.expected_end_date if self.expected_end_date else False,
                })
                if vehicle_odometer_id:
                    if vehicle_odometer_id.vehicle_id:
                        vehicle_odometer_id.vehicle_id.trip_id = self.id
                        vehicle_odometer_id.vehicle_id.expected_end_date = self.expected_end_date
                        vehicle_odometer_id.vehicle_id.route_id = self.route_id.id
        if not self.is_done_fuel:
            fuel_amount = 0
            if self.extra_distance_amount != 0:
                fuel_amount = self.fuel_trip_amt + self.extra_distance_amount
            else:
                fuel_amount = self.fuel_trip_amt
            if not self.total_reward_amount and not fuel_amount:
                return self.write({'check_trip_money': True, 'is_done_fuel': True})

        search_id = self.env['account.fuel.trip.configuration'].search([])
        if not search_id.fuel_expense_account_id or not search_id.fuel_expense_analytical_account_id:
            raise UserError(_("Go To Accouting --> Configuration --> Add Rewards and Fuel Configuration"))
        else:
            # if self.trip_waypoint_ids:
            # journal_id = self.env['account.journal'].search([('branches','in',self.trip_waypoint_ids[0].waypoint.loc_branch_id.id),('type','in',['cash']),('sub_type','in',['Payment'])],limit=1)
            journal_id = self.env['account.journal'].search(
                ['|', ('sub_type', 'in', ['All']), ('sub_type', 'in', ['Payment']),
                 ('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash'])], limit=1)
            # journal_id = self.env['account.journal'].search([('type','=','cash')],limit=1)
            if not journal_id:
                raise UserError(_("Be Sure You Have Cash Journal With Waypoints"))
            if not self.driver_id:
                raise UserError(_("Be Sure You Have Select Drive"))

            search_partner = self.env['res.partner'].browse(self.driver_id.partner_id.id)
            if not search_partner:
                search_partner_type = self.env['partner.type'].search([('is_vendor', '=', True)], limit=1)
                search_partner = self.env['res.partner'].create({'name': self.driver_id.name,
                                                                 'customer': False,
                                                                 'supplier': True,
                                                                 'partner_types': search_partner_type.id if search_partner_type else False})
                search_partner._onchange_partner_types()
            # for getting branch from jounal
            if journal_id.branches:
                branch_id = journal_id.branches[0].id
            else:
                branch_id = False
            if not self.is_done_fuel:
                payment_method = self.env.ref('account.account_payment_method_manual_in')
                fuel_amount = 0
                if self.extra_distance_amount != 0:
                    fuel_amount = self.fuel_trip_amt + self.extra_distance_amount
                else:
                    fuel_amount = self.fuel_trip_amt

                inv_obj = self.env['account.move']
                inv_line_obj = self.env['account.move.line']
                inv_data = self._prepare_invoice(search_partner)
                invoice = inv_obj.create(inv_data)
                if fuel_amount:
                    fule_product = self.env['product.product'].search([('is_fuel_expense', '=', True)], limit=1)
                    if not fule_product:
                        raise UserError(_("Please Cofigure Fule product...!"))
                    # if not fule_product.property_account_expense_id:
                    # 	raise UserError(_("Please Cofigure Expense Account on Fule product...!"))
                    fleet_id = self.vehicle_id.id
                    account_id = search_id.fuel_expense_account_id.id
                    analytic_id = self.vehicle_id.vehicle_type.analytic_account_id.id if self.vehicle_id.vehicle_type.analytic_account_id else False
                    analytic_tags = self.vehicle_id.vehicle_type.analytic_tag_ids.ids if self.vehicle_id.vehicle_type.analytic_tag_ids else []
                    # as need of nabeel
                    if self.display_expense_type in ['km', 'hybrid']:
                        inv_line_obj.with_context({'is_trip':True}).create(
                            self._prepare_invoice_line(invoice.id, account_id, analytic_id, analytic_tags, fule_product,
                                                       fuel_amount,
                                                       fule_product.supplier_taxes_id, fleet_id))
                    else:
                        tax_ids = []
                        inv_line_obj.with_context({'is_trip':True}).create(
                            self._prepare_invoice_line(invoice.id, account_id, analytic_id, analytic_tags, fule_product,
                                                       fuel_amount,
                                                       tax_ids, fleet_id))

                if self.total_reward_amount:
                    reward_product = self.env['product.product'].search([('is_driver_reward', '=', True)], limit=1)
                    if not reward_product:
                        raise UserError(_("Please Cofigure Driver Reward product...!"))
                    # if not reward_product.property_account_expense_id:
                    # 	raise UserError(_("Please Cofigure Expense Account on Fule product...!"))
                    fleet_id = self.vehicle_id.id
                    account_id = search_id.trip_account.id
                    analytic_id = self.vehicle_id.vehicle_type.analytic_account_id.id if self.vehicle_id.vehicle_type.analytic_account_id else False
                    analytic_tags = self.vehicle_id.vehicle_type.analytic_tag_ids.ids if self.vehicle_id.vehicle_type.analytic_tag_ids else []

                    tax_ids = []
                    inv_line_obj.with_context({'is_trip':True}).create(
                        self._prepare_invoice_line(invoice.id, account_id, analytic_id, analytic_tags, reward_product,
                                                   self.total_reward_amount, tax_ids, fleet_id))

                # Config = self.env.ref('bsg_trip_mgmt.res_config_cash_rounding_data', False)
                # invoice.write({'cash_rounding_id' : Config.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).cash_rounding_id.id})
                invoice._compute_amount()
                invoice.with_context({'fleet_id': fleet_id, 'analytic_id': analytic_id})._onchange_cash_rounding()
                invoice.action_post()

                invoice_list = []
                invoice_list.append(invoice.id)
                create_voucher = self.env['account.payment'].with_context(search_default_inbound_filter=True).create(
                    {'payment_type': 'outbound',
                     'partner_type': 'supplier',
                     'is_voucher_or_expense': True,
                     'ref': str(self.name) + ' ' + 'عبارة عن قيمة مصــروف الطريق لرحلـة رقــم',
                     'payment_reference': self.name,
                     'partner_id': search_partner.id,
                     'amount': invoice.amount_total,
                     'journal_id': journal_id.id,
                     'fleet_trip_id': self.id,
                     'is_pay_trip_money': True,
                     'date': str(fields.Date.today()),
                     'collectionre': self.name,
                     'branch_ids': branch_id,
                     'invoice_ids': [(6, 0, invoice_list)],
                     'payment_method_id': payment_method.id
                     })

                create_voucher.post_state()
                create_voucher.action_post()
                self.write({'is_done_fuel': True})
            else:
                raise UserError(_("Fuel Voucher Already Created"))
            # Migration Note
            # self.env['fleet.vehicle.log.fuel'].sudo().with_context(force_company=self.env.user.company_id.id,
            #                                                        company_id=self.env.user.company_id.id).create({
            #     'vehicle_id': self.vehicle_id.id,
            #     'fleet_trip_id': self.id,
            #
            # })
            self.write({'check_trip_money': True})

    # @api.multi
    def pay_additional_fuel(self):
        search_id = self.env['account.fuel.trip.configuration'].search([])
        if not search_id.fuel_expense_account_id or not search_id.fuel_expense_analytical_account_id:
            raise UserError(_("Go To Accouting --> Configuration --> Add Rewards and Fuel Configuration"))
        else:
            journal_id = self.env['account.journal'].search(
                ['|', ('sub_type', 'in', ['All']), ('sub_type', 'in', ['Payment']),
                 ('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash'])], limit=1)
            if not journal_id:
                raise UserError(_("Be Sure You Have Cash Journal With Waypoints"))
            if not self.driver_id:
                raise UserError(_("Be Sure You Have Select Drive"))
            search_partner = self.env['res.partner'].search([('name', '=', str(self.driver_id.name))], limit=1)
            if not search_partner:
                search_partner_type = self.env['partner.type'].search([('is_vendor', '=', True)], limit=1)
                search_partner = self.env['res.partner'].create({'name': self.driver_id.name,
                                                                 'customer': False,
                                                                 'supplier': True,
                                                                 'partner_types': search_partner_type.id if search_partner_type else False})
                search_partner._onchange_partner_types()
            # for getting branch from jounal
            if journal_id.branches:
                branch_id = journal_id.branches[0].id
            else:
                branch_id = False

            invoice_list = []
            pay_trip_amount = 0
            if self.additional_fuel_exp:
                inv_obj = self.env['account.move']
                inv_line_obj = self.env['account.move.line']
                inv_data = self._prepare_invoice(search_partner)
                invoice = inv_obj.create(inv_data)
                fule_product = self.env['product.product'].search([('is_driver_reward', '=', True)], limit=1)
                if not fule_product:
                    raise UserError(_("Please Cofigure Fule product...!"))
                # if not fule_product.property_account_expense_id:
                # 	raise UserError(_("Please Cofigure Expense Account on Fule product...!"))
                fleet_id = self.vehicle_id.id
                account_id = search_id.fuel_expense_account_id.id
                analytic_id = self.vehicle_id.vehicle_type.analytic_account_id.id if self.vehicle_id.vehicle_type.analytic_account_id else False
                analytic_tags = self.vehicle_id.vehicle_type.analytic_tag_ids.ids if self.vehicle_id.vehicle_type.analytic_tag_ids else []
                tax_ids = []
                inv_line_obj.create(
                    self._prepare_invoice_line(invoice.id, account_id, analytic_id, analytic_tags, fule_product,
                                               self.add_reward_amt_frontend, tax_ids, fleet_id))

                # invoice._compute_amount()
                invoice.action_post()
                # Config = self.env.ref('bsg_trip_mgmt.res_config_cash_rounding_data', False)
                # invoice.write({'cash_rounding_id' : Config.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).cash_rounding_id.id})
                # invoice._onchange_cash_rounding()

                # Config = self.env.ref('bsg_trip_mgmt.res_config_cash_rounding_data', False)
                # invoice.update({'cash_rounding_id' : Config.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).cash_rounding_id.id})
                # invoice._compute_amount()
                invoice._onchange_cash_rounding()
                invoice.action_post()
                if invoice:
                    invoice_list.append(invoice.id)
                    pay_trip_amount = invoice.amount_total
                else:
                    pay_trip_amount = self.additional_fuel_exp

            if not self.is_done_add_fuel and self.additional_fuel_exp != 0:
                payment_method = self.env.ref('account.account_payment_method_manual_in')
                create_voucher = self.env['account.payment'].with_context(search_default_inbound_filter=True).create(
                    {'payment_type': 'outbound',
                     'partner_type': 'supplier',
                     'is_voucher_or_expense': True,
                     'ref': str(self.name) + ' ' + 'عبارة عن قيمة مصــروف الطريق لرحلـة رقــم',
                     'payment_reference': self.name,
                     'partner_id': search_partner.id,
                     'amount': pay_trip_amount,
                     'journal_id': journal_id.id,
                     'fleet_trip_id': self.id,
                     'is_pay_trip_money': True,
                     'currency_id': self.env.user.company_id.currency_id.id,
                     'invoice_ids': [(6, 0, invoice_list)] if invoice_list else [(6, 0, [])],
                     'date': str(fields.Date.today()),
                     'collectionre': self.name,
                     'branch_ids': branch_id,
                     'payment_method_id': payment_method.id
                     })

                create_voucher.post_state()
                create_voucher.action_post()
                self.write({'is_done_add_fuel': True})
            else:
                raise UserError(_("Fuel Voucher Already Created"))
            # Migration Note
            # self.env['fleet.vehicle.log.fuel'].create({
            #     'vehicle_id': self.vehicle_id.id,
            #     'fleet_trip_id': self.id,
            #
            # })
            self.write({'check_add_money': True})

    # @api.multi
    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window']._for_xml_id('fleet.fleet_vehicle_odometer_action')
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.vehicle_id.id, default_fleet_trip_id=self.id,
                             group_by=False),
                domain=[('vehicle_id', '=', self.vehicle_id.id), ('fleet_trip_id', '=', self.id)]
            )
            return res
        return False

    def confim_data(self):
        # For Hiding the button
        if self.vehicle_id:
            if dt.datetime.now() < self.expected_start_date:
                self.vehicle_id.daily_trip_count = 0
        self.write({
            'check_dispatch_report': False,
        })
        self._get_fuel_expense()
        self.compute_fuel_trip_amt()
        return self.write({'state': 'confirmed'})

    # method to find fuel exp on bases of capacity threshold
    def _get_fuel_expense(self):
        total_capacity_percent = sum(line.picking_name.car_size.capacity_per_load for line in self.stock_picking_id \
                                     if line.picking_name.arrival_status != True and not line.picking_name.is_package)
        if self.vehicle_id.vehicle_type.satha:
            capacity_threshold = float(
                self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                    company_id=self.env.user.company_id.id).get_param(
                    'bsg_master_config.satha_capacity_threshold'))
        else:
            capacity_threshold = float(
                self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                    company_id=self.env.user.company_id.id).get_param(
                    'bsg_master_config.capacity_threshold'))

        if self.state == 'draft':
            if total_capacity_percent >= capacity_threshold:
                self.truck_load = 'full'
            else:
                self.truck_load = 'empty'
            # as driver will get reward on emtpy picking so commenting this if condition
            # if self.stock_picking_id:
            self._calculate_total_reward_amt()

        if self.state == 'on_transit':
            if total_capacity_percent >= capacity_threshold:
                if self.truck_load == 'empty':
                    self.truck_load = 'full'
                    # trip_arrival = self.env['fleet.trip.arrival'].search([('trip_id','=',self.id),('is_done_survey','=',False)],limit=1)
                    trip_arrival_ids = self.bsg_trip_arrival_ids.filtered(lambda a: a.register_done == True)
                    trip_arrival = trip_arrival_ids and trip_arrival_ids[-1:] or self.bsg_trip_arrival_ids[-1:]
                    current_loc_id = trip_arrival.waypoint_to
                    self.current_loc_id = current_loc_id and current_loc_id.id
                    distance = self._get_branch_distance(current_loc_id, self.trip_waypoint_ids[-1].waypoint)
                    self.additional_fuel_exp = (self._get_full_load_amt() - self._get_empty_load_amt()) * distance
            else:
                self.truck_load = 'empty'

    # for calculation of reward amount
    def _calculate_total_reward_amt(self):
        if self.route_id and self.fuel_exp_method_id and self.vehicle_id and self.vehicle_id.trailer_id and self.vehicle_id.trailer_id.trailer_categories_id:
            if self.fuel_expense_type == 'km':
                if self.truck_load == 'full':
                    if self.driver_id.driver_rewards and self.driver_id.driver_rewards in ['by_delivery',
                                                                                           'by_delivery_b',
                                                                                           'by_revenue']:
                        self.total_reward_amount = round(
                            (self.route_id.total_distance) * self.fuel_exp_method_id.fl_reward)
                    else:
                        self.total_reward_amount = round(
                            (self.route_id.total_distance) * self.fuel_exp_method_id.nfl_reward)
                elif self.truck_load == 'empty':
                    if self.driver_id.driver_rewards and self.driver_id.driver_rewards in ['by_delivery',
                                                                                           'by_delivery_b',
                                                                                           'by_revenue']:
                        self.total_reward_amount = round(
                            (self.route_id.total_distance) * self.fuel_exp_method_id.el_reward)
                    else:
                        self.total_reward_amount = round(
                            (self.route_id.total_distance) * self.fuel_exp_method_id.nel_reward)

    # 
    def _compute_capacity_threshold(self):
        self.capacity_threshold_percent = sum(
            line.picking_name.car_size.capacity_per_load for line in self.stock_picking_id \
            if line.picking_name.arrival_status != True and not line.picking_name.is_package)
        if self.vehicle_id.vehicle_type.satha:
            self.capacity_threshold_limit = float(
                self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                    company_id=self.env.user.company_id.id).get_param(
                    'bsg_master_config.satha_capacity_threshold'))
        else:
            self.capacity_threshold_limit = float(
                self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                    company_id=self.env.user.company_id.id).get_param(
                    'bsg_master_config.capacity_threshold'))

    # Method to find distance between branches
    def _get_branch_distance(self, location_from, location_to):
        if location_from and location_to:
            search_id = self.env['branch.distance'].search(
                [('branch_from', '=', location_from.id), ('branch_to', '=', location_to.id)], limit=1)
            if search_id:
                return search_id.distance
            else:
                return 0

    # Get full load amount
    def _get_full_load_amt(self):
        if self.driver_id.driver_rewards and self.driver_id.driver_rewards in ['by_delivery', 'by_delivery_b',
                                                                               'by_revenue']:
            return self.fuel_exp_method_id.full_load_amt + self.fuel_exp_method_id.fl_reward
        else:
            return self.fuel_exp_method_id.amt_full_without_reward + self.fuel_exp_method_id.nfl_reward

    # Get amount when there is empty load
    def _get_empty_load_amt(self):
        if self.driver_id.driver_rewards and self.driver_id.driver_rewards in ['by_delivery', 'by_delivery_b',
                                                                               'by_revenue']:
            return self.fuel_exp_method_id.empty_load_amt + self.fuel_exp_method_id.el_reward
        else:
            return self.fuel_exp_method_id.amt_empty_without_reward + self.fuel_exp_method_id.nel_reward

    # button for start trip
    def action_start_trip(self):
        if self.state in ['finished', 'cancelled']:
            raise UserError(_("Trip already in finished or cancelled state"))
        self.compute_fuel_trip_amt()
        self.sudo().with_context(force_company=self.env.user.company_id.id,
                                 company_id=self.env.user.company_id.id).remove_delivered_ids()
        for arrival in self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                company_id=self.env.user.company_id.id).bsg_trip_arrival_ids:
            if not arrival.sudo().with_context(force_company=self.env.user.company_id.id,
                                               company_id=self.env.user.company_id.id).register_done and not arrival.sudo().with_context(
                    force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).actual_start_time \
                    and not arrival.sudo().with_context(force_company=self.env.user.company_id.id,
                                                        company_id=self.env.user.company_id.id).is_done_survey:
                arrival.sudo().with_context(force_company=self.env.user.company_id.id,
                                            company_id=self.env.user.company_id.id).actual_start_time = dt.datetime.now()
                for line in arrival.sudo().with_context(force_company=self.env.user.company_id.id,
                                                        company_id=self.env.user.company_id.id).arrival_line_ids:
                    if self.trip_type != 'local':
                        if line.delivery_id.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                company_id=self.env.user.company_id.id).state not in [
                            'Delivered', 'done', 'released',
                            'cancel'] and not line.arrived:
                            if line.delivery_id.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                    company_id=self.env.user.company_id.id).fleet_trip_id and line.delivery_id.sudo().with_context(
                                    force_company=self.env.user.company_id.id,
                                    company_id=self.env.user.company_id.id).fleet_trip_id.id == self.id:
                                line.delivery_id.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                     company_id=self.env.user.company_id.id).action_shipped()
                break
        if self.sudo().with_context(force_company=self.env.user.company_id.id,
                                    company_id=self.env.user.company_id.id).vehicle_id and self.sudo().with_context(
                force_company=self.env.user.company_id.id,
                company_id=self.env.user.company_id.id).vehicle_id.current_branch_id:
            self.vehicle_id.current_branch_id = False
        if self.sudo().with_context(force_company=self.env.user.company_id.id,
                                    company_id=self.env.user.company_id.id).vehicle_id and self.sudo().with_context(
                force_company=self.env.user.company_id.id,
                company_id=self.env.user.company_id.id).vehicle_id.current_loc_id:
            self.vehicle_id.current_loc_id = False
        self.vehicle_id.sudo().write({
            'trip_id': self.id,
            'route_id': self.route_id.id,
            'expected_end_date': self.expected_end_date,
            'no_of_cars': str(len(self.stock_picking_id))
        })

        trip_arrival = self.env['fleet.trip.arrival'].search(
            [('trip_id', '=', self.id), ('is_done_survey', '=', False)], limit=1)
        self.next_branch_id = trip_arrival.waypoint_to.loc_branch_id.id
        self.next_loc_id = trip_arrival.waypoint_to.id

        if not self.is_trip_started:
            self.is_trip_started = True
            total_capacity_percent = sum(line.picking_name.car_size.capacity_per_load for line in self.stock_picking_id \
                                         if
                                         line.picking_name.arrival_status != True and not line.picking_name.is_package)

            if self.vehicle_id.vehicle_type.satha:
                capacity_threshold = float(
                    self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                        company_id=self.env.user.company_id.id).get_param(
                        'bsg_master_config.satha_capacity_threshold'))
            else:
                capacity_threshold = float(
                    self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                        company_id=self.env.user.company_id.id).get_param(
                        'bsg_master_config.capacity_threshold'))

            if total_capacity_percent >= capacity_threshold:
                self.truck_load = 'full'
            else:
                self.truck_load = 'empty'
            self._calculate_total_reward_amt()
        self.total_cars = sum(line.delivered_items_count for line in self.trip_waypoint_ids)
        if not self.actual_start_datetime:
            self.actual_start_datetime = fields.Datetime.now()
            self.start_branch = self.route_id.waypoint_from.id
        return self.sudo().with_context(force_company=self.env.user.company_id.id,
                                        company_id=self.env.user.company_id.id).write({'state': 'progress'})

    # it remove the so lines whose state is delivered from the arrival screen
    def remove_delivered_ids(self):
        removeData = []
        for arrival in self.bsg_trip_arrival_ids:
            if arrival.register_done and arrival.actual_start_time \
                    and arrival.actual_end_time and arrival.is_done_survey:
                for line in arrival.arrival_line_ids:
                    if line.arrived:
                        for rec in self.bsg_trip_arrival_ids:
                            if rec.id != arrival.id:
                                for item in rec.arrival_line_ids:
                                    if item.delivery_id.id == line.delivery_id.id:
                                        item.unlink()

    # Performing the register arrival functionality when clicked do the processing and return popup
    def action_register_arrival(self):
        """ For registering the arrival this method check if user is 
        worthy to register arrival or not then pass to trip arrival and on validation 
        calling a register_arrival_method that perform all the action """
        trip_arrival = self.env['fleet.trip.arrival'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                          company_id=self.env.user.company_id.id).search(
            [('waypoint_to.loc_branch_id', '=', self.env.user.user_branch_id.id), ('trip_id', '=', self.id),
             ('actual_end_time', '=', False)], limit=1)
        if not trip_arrival and not trip_arrival.waypoint_to.is_allow_to_release:
            raise UserError(_("You already Register Arrival or you are not authorized....!"))
        if self.env.user.user_branch_id.id not in [line.waypoint.loc_branch_id.id for line in self.trip_waypoint_ids]:
            raise UserError(
                _("You can not Register arrival either you have created this record or you belong to a different branch."))
        route_waypoints = trip_arrival.trip_id.route_id.waypoint_to_ids.mapped('waypoint')
        route_waypoint_ids = [waypoint.id for waypoint in route_waypoints if not waypoint.loc_branch_id]
        route_waypoint_ids += [trip_arrival.waypoint_to.id]
        if not trip_arrival.sudo().with_context(force_company=self.env.user.company_id.id,
                                                company_id=self.env.user.company_id.id).register_done and not trip_arrival.sudo().with_context(
                force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).actual_end_time \
                and not trip_arrival.sudo().with_context(force_company=self.env.user.company_id.id,
                                                         company_id=self.env.user.company_id.id).is_done_survey:
            for line in trip_arrival.sudo().with_context(force_company=self.env.user.company_id.id,
                                                         company_id=self.env.user.company_id.id).arrival_line_ids:
                drop_loc = line.delivery_id.drop_loc.id
                line.route_waypoint_ids = [(6, 0, route_waypoint_ids + [drop_loc])]
                line.drop_loc = drop_loc
                if (line.delivery_id.drop_loc.id == trip_arrival.sudo().with_context(
                        force_company=self.env.user.company_id.id,
                        company_id=self.env.user.company_id.id).waypoint_to.id) or line.delivery_id.loc_to.location_type != 'albassami_loc':
                    if self.trip_type != 'local':
                        line.arrived = True
                    else:
                        line.arrived = False
                else:
                    line.arrived = False

        if trip_arrival:
            view_id = self.env.ref('bsg_trip_mgmt.fleet_trip_arrival_form').id
            trip_arrival.sudo().with_context(force_company=self.env.user.company_id.id,
                                             company_id=self.env.user.company_id.id).update({'is_required': True})
            return {
                'type': 'ir.actions.act_window',
                'name': 'Trip Arrival',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'fleet.trip.arrival',
                'view_id': view_id,
                'res_id': trip_arrival.id,
                'target': 'new',
            }

    # for getting logged user branc
    def get_current_user_branch(self):
        return self.env.user.user_branch_id.id

    # Overiding Create Method
    @api.model
    def create(self, vals):
        prev_trip_recs = self.env['fleet.vehicle.trip'].search(
            [('state', 'not in', ['finished', 'cancelled']), ('vehicle_id', '=', vals['vehicle_id'])])
        driver_trip_recs = False
        FleetVehTrip = super(BsgFleetVehicleTrip, self).create(vals)
        sequence = self.env['ir.sequence'].with_context(force_company=self.env.user.company_id.id).next_by_code(
            'bsg_fleet_vehicle_trip_sq_code')
        _logger.info('Sequence ' + str(sequence))
        if FleetVehTrip.trip_waypoint_ids:
            branch_no = str(FleetVehTrip.trip_waypoint_ids[0].waypoint.branch_no)
            if not branch_no:
                branch_no = 'TN'
            FleetVehTrip.name = branch_no + str(sequence)
        if FleetVehTrip.sale_gov_id:
            FleetVehTrip.name = str(sequence)
        if FleetVehTrip.vehicle_id:
            if not FleetVehTrip.vehicle_id.rented_vehicle:
                FleetVehTrip.is_rented = False
                if not FleetVehTrip.vehicle_id.bsg_driver:
                    raise UserError(_("This Vehicle is without driver you need to set driver first!"))
                else:
                    FleetVehTrip.driver_id = FleetVehTrip.vehicle_id.bsg_driver.id
            elif FleetVehTrip.vehicle_id.rented_vehicle:
                FleetVehTrip.is_rented = True
                contract_id = self.env['fleet.vehicle.log.contract'].sudo().search(
                    [('vehicle_id', '=', FleetVehTrip.vehicle_id.id)], limit=1)
                if not contract_id:
                    raise UserError(_("This Vehicle Is Rented But No Contract For it!"))
                else:
                    FleetVehTrip.rented_vehicle_vendor = contract_id.insurer_id.id
                    FleetVehTrip.trip_cost = contract_id.amount
                    FleetVehTrip.rented_driver_id = contract_id.purchaser_id.id

        for rec in prev_trip_recs:
            if rec.expected_end_date >= FleetVehTrip.expected_start_date:
                raise UserError(_("A trip for this Truck is already planned for given dates!"))
        driver_trip_recs = self.env['fleet.vehicle.trip'].search(
            [('id', '!=', FleetVehTrip.id), ('create_date', '>', '2021-03-01'),
             ('state', 'not in', ['finished', 'cancelled']), ('driver_id', '=', FleetVehTrip.vehicle_id.bsg_driver.id)])
        if driver_trip_recs:
            raise ValidationError(
                _("Cannot create trip! There's one or more open trips for selected driver. driver => %s    trips => %s" % (
                driver_trip_recs[0].driver_id.driver_code, ','.join(driver_trip_recs.mapped('name')))))
        if not FleetVehTrip.bsg_trip_arrival_ids:
            stating_loc = FleetVehTrip.route_id.waypoint_from.id
            for loc in FleetVehTrip.route_id.waypoint_to_ids:
                FleetVehTrip.bsg_trip_arrival_ids |= FleetVehTrip.bsg_trip_arrival_ids.new({
                    'waypoint_from': stating_loc,
                    'waypoint_to': loc.waypoint.id,
                })
                stating_loc = loc.waypoint.id
        FleetVehTrip.compute_fuel_trip_amt()

        return FleetVehTrip

    # Overiding Write Method
    # @api.multi
    def write(self, vals):
        if vals.get('state', False) in ['draft', 'on_transit']:
            print('................state ...............', self.state)
            if self.trip_waypoint_ids:
                if self.next_loc_id:
                    location_ids = self.trip_waypoint_ids.mapped('waypoint').ids
                    print('location_id ...............', location_ids)
                    if location_ids:
                        if self.next_loc_id.id in location_ids:
                            next_loc_index = location_ids.index(self.next_loc_id.id)
                            if next_loc_index not in [0]:
                                current_loc_index = next_loc_index - 1
                                current_loc_id = location_ids[current_loc_index]
                                if current_loc_id:
                                    current_loc = self.env['bsg_route_waypoints'].browse(current_loc_id)
                                    print('vehicle id ...............', self.vehicle_id)
                                    self.vehicle_id.current_loc_id = current_loc.id
                                    self.vehicle_id.current_branch_id = current_loc.loc_branch_id.id
        if vals.get('state', False) == 'finished':
            vals['actual_end_datetime'] = fields.Datetime.now()
            if self.route_id:
                vals['end_branch'] = self.route_id.waypoint_to_ids[-1].waypoint.id
        FleetVehTrip = super(BsgFleetVehicleTrip, self).write(vals)
        # if self.stock_picking_id:
        # 	self.so_line_status_count = len(self.stock_picking_id.filtered(lambda line:line.state == 'shipped'))
        # self._onchange_sch_dates()
        return FleetVehTrip

    # @api.multi
    def copy(self, default=None):
        """
            Create a new record in BsgFleetVehicleTrip model from existing one
            @param default: dict type contains the values to be override during copy of object

            @return: returns a id of newly created record
        """
        sequence = self.env['ir.sequence'].with_context(force_company=self.env.user.company_id.id).next_by_code(
            'bsg_fleet_vehicle_trip_sq_code')
        name = sequence
        if self.trip_waypoint_ids:
            branch_no = str(self.trip_waypoint_ids[0].waypoint.branch_no)
            if not branch_no:
                branch_no = 'TN'
            name = branch_no + str(sequence)
        default = {
            'route_id': False,
            'vehicle_id': False,
            'driver_id': False,
            'name': name,
            'stock_picking_id': False,
            'expected_start_date': fields.Datetime.now(),
            'actual_start_datetime': False,
            'actual_end_datetime': False,
            'start_branch': False,
            'end_branch': False,
        }
        return super(BsgFleetVehicleTrip, self).copy(default)
