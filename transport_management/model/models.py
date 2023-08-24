# -*- coding: utf-8 -*-
import math
import re
import datetime
import time
from datetime import datetime, date, time, timedelta
import datetime as dt
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, date_utils
from odoo import time
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError
import pytz


class FleetVehicleState(models.Model):
    _inherit = 'fleet.vehicle.state'

    in_service = fields.Boolean()


class TransportManagement(models.Model):
    _name = 'transport.management'
    _description = 'Transport Management'
    _inherit = ['mail.thread']
    _rec_name = 'transportation_no'

    @api.model
    def _default_get_site(self):
        if self.env.user and self.env.user.user_branch_id:
            site_import = self.env['bsg_route_waypoints'].search(
                [('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                limit=1)
            if site_import:
                return site_import.id
            else:
                return False

    def get_fleet_type(self):
        return [('domain_name', 'in', self.env.user.company_id.vehicle_type_domain_ids.ids)]

    # @api.multi
    def name_get(self):
        result = []
        for bx_trip in self:
            transportation_no = bx_trip.transportation_no + " - " + (bx_trip.route_id.route_name or " ")
            result.append((bx_trip.id, transportation_no))
        return result

    #     @api.model
    #     def _default_cus1(self):
    #         ab = self.user_has_groups('base_customer.group_credit_customer')
    #         cd = self.user_has_groups('base_customer.group_customer')
    #         if ab and cd:
    #             return True
    #         elif ab or cd :
    #             return True
    #         else:
    #             return False

    partner_types = fields.Many2one("partner.type",
                                    track_visibility='onchange',
                                    string="Partner Type",
                                    domain="['|','|',('is_construction','=',True),('is_custoemer','=',True),('is_dealer','=',True)]")
    transportation_no = fields.Char(string="Transportation No", readonly=True, store=True, default='New', copy=False)

    customer = fields.Many2one('res.partner', string='Customer', store=True, help='It shows the list of all customers',
                               track_visibility=True)
    #     cus1 = fields.Boolean('Cus1',default=_default_cus1)
    clearance_mode = fields.Selection(string="Service Type", selection=[('import', 'Import'), ('export', 'Export'), ],
                                      default='import', store=True, track_visibility=True)
    custom_import = fields.Many2one('import.custom', string="Import No.", store=True, track_visibility=True)
    custom_export = fields.Many2one('export.custom', string="Export No.", store=True, track_visibility=True)
    site_import = fields.Many2one(string="Site", comodel_name="bsg_route_waypoints", default=_default_get_site,
                                  track_visibility=True)
    site_export = fields.Many2one(string="Site", comodel_name="bsg_route_waypoints", default=_default_get_site)
    sale_status = fields.Many2one('import.status', string='Sale Status', store=True, track_visibility=True)
    vessel_name = fields.Char(String='Vessel Name', store=True, track_visibility=True)
    order_date = fields.Date(string='Order Date', default=fields.Date.context_today, required=True,
                             track_visibility=True)
    expiration_date = fields.Date(string='Expiration Date', track_visibility=True)
    payment_terms = fields.Many2one('account.payment.term', string='Payment Terms', required=False,
                                    track_visibility=True)
    bill_no_import = fields.Char(related='custom_import.bill_no', string="B/L Number", readonly=False,
                                 track_visibility=True)
    bill_no_export = fields.Char(related='custom_export.bill_no', string="B/L Number", readonly=False,
                                 track_visibility=True)
    priority_type = fields.Selection(string="Priority Type", selection=[('high', 'High'), ('low', 'Low'), ],
                                     default='low', store=True, track_visibility=True)
    delivery_date = fields.Date(string='Delivery Date', store=True, track_visibility=True)
    customer_ref = fields.Char(string='Customer Reference', track_visibility=True)
    transport_management_line = fields.One2many('transport.management.line', 'transport_management')
    demurrage_date = fields.Date(string='Demurrage', store=True, track_visibility=True)
    detention_date = fields.Date(string='Detention', store=True, track_visibility=True)
    payment_method = fields.Many2one('cargo_payment_method', string='Payment Method', track_visibility=True)
    delivery_way = fields.Selection([('dr2dr', 'Dr2Dr'), ('albassami_branch', 'Albassami Branches')],
                                    string='Delivery Way', track_visibility=True)
    insurance_req = fields.Boolean(string='Insurance Required', track_visibility=True)
    payment = fields.Many2one('account.payment', string='Payment', readonly=True, track_visibility=True, copy=False)
    service_type = fields.Selection(
        [('express', 'Express'), ('line_haul', 'Line Haul'), ('intra_city', 'Intra City'), ('cargo', 'Cargo'),
         ('car_carrier','Car Carrier'),('others', 'Others')], string='Service Type', track_visibility=True)
    agreement_type = fields.Selection([('one_way', 'One way'), ('round_trip', 'Round trip')], string='Agreement Type',
                                      track_visibility=True)

    from_route_branch_id = fields.Many2one('bsg_branches.bsg_branches')
    route_id = fields.Many2one('bsg_route', string='Route', domain=lambda self: self._get_route_domain(),
                               track_visibility=True)
    fuel_exp_method_id = fields.Many2one('bsg.fuel.expense.method', string='Fuel Expense Method', store=True,
                                         track_visibility=True)
    truck_load = fields.Selection([
        ('full', 'Full Load'),
        ('empty', 'Empty Load')
    ], string="Truck Load", compute="_compute_truck_load"
        , track_visibility=True)
    is_rented = fields.Boolean()
    rented_vehicle_vendor = fields.Many2one('res.partner', "Rented Vehicle Vendor")
    trip_cost = fields.Float("Trip Cost")
    #     fuel_trip_amt = fields.Float(string='Fuel Expense Amount',compute="compute_fuel_trip_amt",store=True)

    fuel_expense_type = fields.Selection([
        ('km', 'Per KM'),
        ('local', 'Local'),
        ('route', 'Route'),
        ('port', 'Port'),
        ('hybrid', 'Hybrid')], string="Fuel ExpenseMethod",
        store=True, track_visibility=True)
    total_fuel_amount = fields.Float(string="Total Fuel Expense", compute='compute_fuel_trip_amt', store=True,
                                     track_visibility=True)
    trip_distance = fields.Float(string="Trip Distance", store=True, track_visibility=True)
    extra_distance = fields.Integer(string="Extra Distance", track_visibility=True)
    reason = fields.Text(string="Reason", track_visibility=True)
    total_distance = fields.Float(string='Total Distance', compute='_get_total_distance', readonly=True, store=True,
                                  track_visibility=True)
    extra_distance_amount = fields.Float(string="Extra Distance Amount", compute="_get_extra_distance_amount",
                                         track_visibility=True)
    total_reward_amount = fields.Float(string="Total Reward amount Backend", compute='_get_total_distance', store=True,
                                       track_visibility=True)
    display_expense_mthod_id = fields.Many2one(related='fuel_exp_method_id', string='Fuel Expense Method', store=True,
                                               track_visibility=True)
    display_expense_type = fields.Selection(related="fuel_expense_type", string="Fuel Expense Type", store=True,
                                            track_visibility=True)

    transportation_vehicle = fields.Many2one('fleet.vehicle', string='Transportation Vehicle', store=True,
                                             track_visibility=True)
    transportation_mode = fields.Selection(string="Transportation Mode",
                                           selection=[('internal', 'Internal'), ('external', 'External'), ],
                                           default='internal', store=True, track_visibility=True)
    service_name = fields.Selection(string='Service Name', selection=[('import', 'Import'), ('export', 'Export'), ],
                                    default='import', store=True, track_visibility=True)
    transportation_driver = fields.Many2one('hr.employee', string='Transportation Driver', store=True,
                                            track_visibility=True)
    transportation_driver_rented = fields.Many2one('res.partner', string='Transportation Driver', store=True,
                                                   track_visibility=True)
    driver = fields.Many2one('hr.employee', store=True, track_visibility=True)
    driver_number = fields.Char(string='Driver Number', store=True, track_visibility=True)
    internal_number = fields.Integer(string='Internal Number', store=True, track_visibility=True)
    supplier_name = fields.Many2one('res.partner', string='Supplier Name', store=True, track_visibility=True)
    supplier_freight = fields.Float(string='Supplier freight', store=True, track_visibility=True)

    form_transport = fields.Many2one('bsg_route_waypoints', string="From", store=True, default=_default_get_site,
                                     track_visibility=True)
    to_transport = fields.Many2one('bsg_route_waypoints', string="To",track_visibility=True)
    fleet_type_transport = fields.Many2one('bsg.vehicle.type.table', string="Fleet Type", domain=get_fleet_type,
                                           track_visibility=True)
    is_created_return_invoice = fields.Boolean(string="Is Created Return Invoice", copy=False, default=False)
    is_created_return_bill = fields.Boolean(string="Is Created Return Bill", copy=False, default=False)
    customer_contract = fields.Many2one(string="Contract No.", comodel_name="bsg_customer_contract")
    pull_from_other_bx = fields.Boolean(string="Load with Other Agreement")
    other_bx_id = fields.Many2one('transport.management', string="Bx Agreement No")
    pull_reason_note = fields.Text('Note')
    trailer_id = fields.Many2one('bsg_fleet_trailer_config', readonly=True, string="Trailer")
    vehicle_type_domain_id = fields.Many2one('vehicle.type.domain', related="fleet_type_transport.domain_name",
                                             store=True, string="Domain Name")

    @api.onchange('other_bx_id')
    def _onchane_other_bx_id(self):
        if self.other_bx_id:
            self.service_name = self.other_bx_id.service_name
            self.internal_number = self.other_bx_id.internal_number
            self.supplier_name = self.other_bx_id.supplier_name.id
            self.driver = self.other_bx_id.driver.id
            self.supplier_freight = self.other_bx_id.supplier_freight
            self.fleet_type_transport = self.other_bx_id.fleet_type_transport.id
            self.route_id = self.other_bx_id.route_id.id
            self.fuel_expense_type = self.other_bx_id.route_id.route_type
            self.display_expense_type = self.other_bx_id.route_id.route_type

            self.transportation_vehicle = self.other_bx_id.transportation_vehicle.id
            self.transportation_driver = self.other_bx_id.transportation_driver.id
            self.driver_number = self.other_bx_id.driver_number
            self.display_expense_mthod_id = self.other_bx_id.display_expense_mthod_id.id
            self.truck_load = self.other_bx_id.truck_load

            self.fuel_exp_method_id = self.other_bx_id.fuel_exp_method_id.id
            self.extra_distance = 0.0
            self.trip_distance = 0.0
            self.total_distance = 0.0
            self.total_reward_amount = 0.0
            self.total_fuel_amount = 0.0
            self.reason = self.other_bx_id.reason
            self.loading_date = self.other_bx_id.loading_date
            # self.arrival_date = self.other_bx_id.arrival_date
            self.arrival_time = self.route_id.estimated_time
            self.return_date = self.other_bx_id.return_date
            self.stuffing_date = self.other_bx_id.stuffing_date
            self.waybill_date = self.other_bx_id.waybill_date
            self.pod_date = self.other_bx_id.pod_date
            self.lead_days = self.other_bx_id.lead_days

    @api.model
    def _get_loading_date(self):
        user = self.env['res.users'].browse(self.env.uid)
        # converting time to users timezone
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            today_utc = pytz.UTC.localize(datetime.now())
            today_tz = today_utc.astimezone(tz)
            today = datetime(year=today_tz.year, month=today_tz.month, day=today_tz.day, hour=today_tz.hour,
                             minute=today_tz.minute, second=today_tz.second)
            if today:
                return today

    loading_date = fields.Datetime(string='Loading Date', store=True, default=_get_loading_date, track_visibility=True)
    arrival_date = fields.Datetime(string='Arrival Date', compute='_compute_time', store=True, track_visibility=True)
    return_date = fields.Date(string='Return Date', store=True, track_visibility=True)
    stuffing_date = fields.Date(string='Stuffing Date', store=True, track_visibility=True)
    arrival_time = fields.Float(string='Est Duration', track_visibility=True)

    waybill_date = fields.Date(string='WayBill Date', store=True, track_visibility=True)
    pod_date = fields.Date(string='POD Date', store=True, track_visibility=True)
    lead_days = fields.Integer(string='Lead Days', store=True, track_visibility=True)

    receiver_information = fields.Char(string='Recfeiver Information', store=True, track_visibility=True)
    receiver_mobile = fields.Char(string='Receiver Mobile', store=True, track_visibility=True)

    receive_pod = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_receive_pod_rel", column1="m2m_id",
                                   column2="attachment_id", string="Attachments", track_visibility=True)

    acc_link = fields.Char(string="Invoice", readonly=True, store=True)
    acc_link_vendor = fields.Many2one('account.move', string="Invoice", readonly=True, store=True)
    refund_vendor_id = fields.Many2one('account.move', string='Vendor Refund Invoice', readonly=True)
    acc_link_refund_id = fields.Many2one('account.move', string='Customer Refund Invoice', readonly=True)
    invoice_id = fields.Many2one('account.move', string='Invoice')

    total_before_taxes = fields.Float(string='Total Amt Before Taxes', compute='_amount_all', store=True,
                                      track_visibility=True)
    tax_amount = fields.Float(string='Tax Amount', compute='_amount_all', store=True, track_visibility=True)
    total_amount = fields.Float(string='Total Amount', compute='_amount_all', store=True, track_visibility=True)
    paymen = fields.Integer(string='Payment', compute='_get_payment_voucher')

    is_created_return_invoice = fields.Boolean(string="Is Created Return Invoice", copy=False, default=False)
    is_created_return_bill = fields.Boolean(string="Is Created Return Bill", copy=False, default=False)

    '''@api.onchange('fleet_type_transport')
    def change_vehicle(self):
        if self.fleet_type_transport:
            fleet = self.env['fleet.vehicle'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('vehicle_type','=',self.fleet_type_transport.id)])
            if fleet:
                return {'domain':{'transportation_vehicle':[('id', 'in', fleet.ids),('state_id.name','in',['Linked','linked','link'])]}}
            else:
                return {'domain':{'transportation_vehicle':[('id', 'in', False)]}}'''

    '''@api.onchange('form_transport','to_transport','customer_contract')
    def _onchange_get_contract_price(self):
        if self.customer_contract and self.form_transport and self.to_transport:
            for line in self.transport_management_line:
                if line.product_id and line.car_size_id: 
                    ContractLine = self.env['bsg_customer_contract_line'].search([
                                ('cust_contract_id', '=', self.customer_contract.id),
                                ('service_type', '=', line.product_id.product_tmpl_id.id),
                                ('loc_from', '=', self.form_transport.id),
                                ('loc_to', '=', self.to_transport.id),
                                ('car_size', '=', line.car_size_id.id),
                                ], limit=1)                           
                    cut_price =  ContractLine.price if ContractLine else 0.0
                    line.with_context({'without_track':True}).write({'price': cut_price})'''

    @api.onchange('customer')
    def _onchange_customer(self):
        if self.customer:
            if self.customer_contract:
                self.customer_contract = False
                self._onchange_get_contract_price()
            if self.customer.partner_types.id != self.partner_types.id:
                self.partner_types = self.customer.partner_types.id

    @api.onchange('route_id')
    def _onchange_route_id(self):
        if self.route_id and not self.pull_from_other_bx:
            self.from_route_branch_id = self.route_id.waypoint_from.loc_branch_id.id
            self.trip_distance = self.route_id.total_distance
            self.arrival_time = self.route_id.estimated_time
            # Getting Fuel methods
            self.display_expense_type = self.route_id.route_type
            # self.transportation_vehicle = False

    @api.onchange('transportation_vehicle','route_id')
    def onchange_transportation_vehicle(self):
            if self.transportation_vehicle and self.route_id:
                if self.transportation_vehicle.trailer_id:
                    if self.display_expense_type:
                        vehicle_type = self.transportation_vehicle.vehicle_type.id
                        domain = [('vehicle_type','=',vehicle_type),('fuel_expense_type','=',self.display_expense_type)]
                        if self.display_expense_type == 'route':
                            domain.append(('route_id', '=', self.route_id.id))
                        fuel_exp_rule = self.env['bsg.fuel.expense.method'].search(domain,limit=1)
                        if fuel_exp_rule:
                            self.display_expense_mthod_id = fuel_exp_rule.id
                        else:
                            raise UserError(_("Fuel expense rule not found for this vehicle please define one."))
            if self.transportation_vehicle:
                if self.transportation_vehicle.rented_vehicle:
                    self.is_rented = True
                    contract_id = self.env['fleet.vehicle.log.contract'].sudo().search(
                        [('vehicle_id', '=', self.transportation_vehicle.id)], limit=1)
                    if not contract_id:
                        raise UserError(_("This Vehicle Is Rented But No Contract For it!"))
                    else:
                        if not contract_id.purchaser_id:
                            raise UserError(_("This Vehicle is without driver you need to set driver first!"))
                        else:
                            self.rented_vehicle_vendor = contract_id.insurer_id.id
                            self.trip_cost = contract_id.amount
                            self.rented_driver_id = contract_id.purchaser_id.id
                            self.transportation_driver_rented = contract_id.purchaser_id.id

                else:
                    self.is_rented = False
                    if not self.transportation_vehicle.bsg_driver:
                        raise UserError(_("This Vehicle is without driver you need to set driver first!"))
                    else:
                        self.driver = self.transportation_vehicle.bsg_driver.id
                        self.transportation_driver = self.transportation_vehicle.bsg_driver.id
                        self.driver_number = self.transportation_vehicle.bsg_driver.driver_code
                if self.transportation_vehicle.trailer_id:
                    if not self.trailer_id:
                        self.trailer_id = self.transportation_vehicle.trailer_id

    def get_current_user_branch(self):
        return self.env.user.user_branch_id.id

    # @api.multi
    @api.depends('total_amount')
    def _compute_truck_load(self):
        for rec in self:
            if rec.total_amount > 0.00:
                rec.truck_load = 'full'
            else:
                rec.truck_load = 'empty'

    # 
    @api.depends('extra_distance', 'trip_distance', 'truck_load')
    def _get_total_distance(self):
        if not self.pull_from_other_bx:
            if self.trip_distance and self.extra_distance:
                self.total_distance = self.trip_distance + self.extra_distance
            else:
                self.total_distance = self.trip_distance
            if self.truck_load == 'full':
                self.total_reward_amount = self.trip_distance * self.display_expense_mthod_id.fl_reward
            else:
                self.total_reward_amount = self.trip_distance * self.display_expense_mthod_id.el_reward

    @api.onchange('display_expense_mthod_id', 'display_expense_type')
    def _onchange_fuel_fields(self):
        self.compute_rc_fuel_trip_amt()

    # @api.multi
    @api.depends('display_expense_mthod_id', 'display_expense_type', 'trip_distance', 'extra_distance_amount')
    def compute_rc_fuel_trip_amt(self):
        if not self.pull_from_other_bx:
            if self.route_id and self.display_expense_mthod_id and self.transportation_vehicle and self.transportation_vehicle.vehicle_type:
                if self.display_expense_type in ['km', 'hybrid']:
                    if self.driver.driver_rewards and self.driver.driver_rewards in ['by_delivery', 'by_delivery_b',
                                                                                     'by_revenue']:
                        self.total_fuel_amount = round(
                            self.route_id.total_distance * self.display_expense_mthod_id.full_load_amt)
                    else:
                        self.total_fuel_amount = round(
                            self.route_id.total_distance * self.display_expense_mthod_id.amt_full_without_reward)
                    if self.driver.driver_rewards and self.driver.driver_rewards in ['by_delivery', 'by_delivery_b',
                                                                                     'by_revenue']:
                        self.total_fuel_amount = round(
                            self.route_id.total_distance * self.display_expense_mthod_id.empty_load_amt)
                    else:
                        self.total_fuel_amount = round(
                            self.route_id.total_distance * self.display_expense_mthod_id.amt_empty_without_reward)
                elif self.display_expense_type in ['route']:
                    # self.total_fuel_amount = round(self.display_expense_mthod_id.fuel_amount)
                    self.total_fuel_amount = round(self.display_expense_mthod_id.expense_amount)

                elif self.display_expense_type in ['port', 'local']:
                    port_rule = self.env['bsg.port.fuel.amount'].search([
                        ('rule_option', '=', self.display_expense_mthod_id.port_rule_option),
                        ('distance_from', '<=', self.trip_distance),
                        ('distance_to', '>=', self.trip_distance),
                        ('vehicle_type', '=', self.transportation_vehicle.vehicle_type.id),
                        ('route_type', '=', self.route_id.route_type),
                    ], limit=1)
                    if not self.transportation_vehicle.daily_trip_count > 0:
                        self.transportation_vehicle.write({'daily_trip_count': 1})
                    if port_rule:
                        if self.display_expense_mthod_id.port_rule_option == 'trip' and self.transportation_vehicle:
                            trip_fuel = self.env['bsg.port.fuel.trip'].search([
                                ('fuel_trip_config_id', '=', port_rule.id),
                                ('loc_from', '<=',
                                 self.transportation_vehicle.daily_trip_count if self.transportation_vehicle.daily_trip_count > 0 else 1),
                                ('loc_to', '>=',
                                 self.transportation_vehicle.daily_trip_count if self.transportation_vehicle.daily_trip_count > 0 else 1),
                            ], limit=1)
                            if trip_fuel:
                                self.total_fuel_amount = round(trip_fuel.amount)
                self.trip_distance = self.route_id.total_distance
                self.arrival_time = self.route_id.estimated_time

    # @api.multi
    @api.depends('display_expense_mthod_id', 'display_expense_type', 'trip_distance', 'extra_distance_amount')
    def compute_fuel_trip_amt(self):
        if not self.pull_from_other_bx:
            if self.route_id and self.display_expense_mthod_id and self.transportation_vehicle and self.transportation_vehicle.trailer_id and self.transportation_vehicle.trailer_id.trailer_categories_id:
                if self.display_expense_type in ['km', 'hybrid']:
                    if self.driver.driver_rewards and self.driver.driver_rewards in ['by_delivery', 'by_delivery_b',
                                                                                     'by_revenue']:
                        self.total_fuel_amount = round(
                            self.route_id.total_distance * self.display_expense_mthod_id.full_load_amt)
                    else:
                        self.total_fuel_amount = round(
                            self.route_id.total_distance * self.display_expense_mthod_id.amt_full_without_reward)
                    if self.driver.driver_rewards and self.driver.driver_rewards in ['by_delivery', 'by_delivery_b',
                                                                                     'by_revenue']:
                        self.total_fuel_amount = round(
                            self.route_id.total_distance * self.display_expense_mthod_id.empty_load_amt)
                    else:
                        self.total_fuel_amount = round(
                            self.route_id.total_distance * self.display_expense_mthod_id.amt_empty_without_reward)
                elif self.display_expense_type in ['route']:
                    # self.total_fuel_amount = round(self.display_expense_mthod_id.fuel_amount)
                    self.total_fuel_amount = round(self.display_expense_mthod_id.expense_amount)

                elif self.display_expense_type in ['port', 'local']:
                    port_rule = self.env['bsg.port.fuel.amount'].search([
                        ('rule_option', '=', self.display_expense_mthod_id.port_rule_option),
                        ('distance_from', '<=', self.trip_distance),
                        ('distance_to', '>=', self.trip_distance),
                        ('vehicle_type', '=', self.transportation_vehicle.vehicle_type.id),
                        ('route_type', '=', self.route_id.route_type),
                    ], limit=1)
                    if not self.transportation_vehicle.daily_trip_count > 0:
                        self.transportation_vehicle.write({'daily_trip_count': 1})
                    if port_rule:
                        if self.display_expense_mthod_id.port_rule_option == 'trip' and self.transportation_vehicle:
                            trip_fuel = self.env['bsg.port.fuel.trip'].search([
                                ('fuel_trip_config_id', '=', port_rule.id),
                                ('loc_from', '<=',
                                 self.transportation_vehicle.daily_trip_count if self.transportation_vehicle.daily_trip_count > 0 else 1),
                                ('loc_to', '>=',
                                 self.transportation_vehicle.daily_trip_count if self.transportation_vehicle.daily_trip_count > 0 else 1),
                            ], limit=1)
                            if trip_fuel:
                                self.total_fuel_amount = round(trip_fuel.amount)
                self.trip_distance = self.route_id.total_distance
                self.arrival_time = self.route_id.estimated_time
            if self.extra_distance_amount != 0:
                self.total_fuel_amount = self.total_fuel_amount + self.extra_distance_amount
            else:
                self.total_fuel_amount = self.total_fuel_amount

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

    # @api.multi
    @api.depends('route_id', 'display_expense_mthod_id', 'extra_distance')
    def _get_extra_distance_amount(self):
        for res in self:
            res.extra_distance_amount = 0
            if res.extra_distance and res.display_expense_mthod_id and res.route_id:
                if res.display_expense_type in ['km', 'hybrid']:
                    if res.driver.driver_rewards and res.driver.driver_rewards in ['by_delivery', 'by_delivery_b',
                                                                                   'by_revenue']:
                        res.extra_distance_amount = round(
                            res.extra_distance * res.display_expense_mthod_id.full_load_amt)
                    else:
                        res.extra_distance_amount = round(
                            res.extra_distance * res.display_expense_mthod_id.amt_full_without_reward)
                    if res.driver.driver_rewards and res.driver.driver_rewards in ['by_delivery', 'by_delivery_b',
                                                                                   'by_revenue']:
                        res.extra_distance_amount = round(
                            res.extra_distance * res.display_expense_mthod_id.empty_load_amt)
                    else:
                        res.extra_distance_amount = round(
                            res.extra_distance * res.display_expense_mthod_id.amt_empty_without_reward)

    #  Prepare Invoice
    # @api.multi
    def _prepare_invoice(self, transportation_driver):
        self.ensure_one()
        journal_id = self.env['account.journal'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                     company_id=self.env.user.company_id.id).search(
            [('type', '=', 'purchase')], limit=1)
        default_journal_id = self.env['ir.config_parameter'].sudo().with_context(
            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_bx_vendor_journal_id')
        default_partner = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_supplier_id')
        driver = self.env['res.partner'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                             company_id=self.env.user.company_id.id).search(
            [('id', '=', default_partner)])
        default_cash_rounding = self.env['ir.config_parameter'].sudo().with_context(
            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_cash_rounding_id')
        cash_rounding = self.env['account.cash.rounding'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).search(
            [('id', '=', default_cash_rounding)])
        account_id = self.transportation_driver.partner_id.property_account_payable_id
        if not journal_id:
            raise UserError(_("Be Sure You Have Cash Journal With Waypoints"))
        invoice_vals = {
            'name': '',
            'invoice_origin': self.transportation_no,
            'invoice_cash_rounding_id': default_cash_rounding,
            'move_type': 'in_invoice',
            # 'account_id': driver.property_account_payable_id.id if driver.property_account_payable_id else account_id.id,
            # self.transportation_driver.partner_id.property_account_payable_id.id,
            'partner_id': int(default_partner) if int(default_partner) else self.transportation_driver.partner_id.id,
            'journal_id': int(default_journal_id) if int(default_journal_id) else journal_id.id,
            # 'comment': self.transportation_no,
            'currency_id': self.env.user.company_id.currency_id.id,
            'user_id': self.env.user.id,
        }
        return invoice_vals

    #  Prepare Invoice Line
    # @api.multi
    def _prepare_invoice_line(self, inv_id, account_id, product, analytic_tag_id, analytic_id, default_product,
                              fuel_amount, supplier_taxes_id):
        fule_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                           company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_product_id')
        default_account = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_analytic_account_id')
        default_fuel_analytic_tag_id = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_analytic_tag_ids')
        product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                  company_id=self.env.user.company_id.id).search(
            [('id', '=', fule_product)])
        fuel_analytic_tag_list = []
        if int(default_fuel_analytic_tag_id):
            fuel_analytic_tag_list.append(int(default_fuel_analytic_tag_id))
        data = {
            'product_id': int(fule_product),
            'name': product.name,
            'account_id': account_id,
            'price_unit': self.total_fuel_amount,
            'quantity': 1.00,
            'analytic_distribution': {self.fleet_type_transport.analytic_account_id.id if self.fleet_type_transport and self.fleet_type_transport.analytic_account_id else int(default_account) if int(default_account) else False: 100},
            # 'account_tag_ids': self.fleet_type_transport.analytic_tag_ids and [
            #     (6, 0, self.fleet_type_transport.analytic_tag_ids.ids)] or fuel_analytic_tag_list and [
            #                         (6, 0, fuel_analytic_tag_list)] or False,
            'move_id': inv_id,
            'fleet_id': self.transportation_vehicle.id,
            'branch_id': self.env.user.user_branch_id.id,
            'tax_ids': product.supplier_taxes_id and [(6, 0, product.supplier_taxes_id.ids)] or False,
        }
        return data

    # @api.multi
    def _prepare_reward_invoice_line(self, inv_id, account_id, product, driver_account_analytic_id, driver_analytic_id,
                                     reward_product, reward_amount, supplier_taxes_id):
        reward_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                             company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_reward_for_load_id')
        product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                  company_id=self.env.user.company_id.id).search(
            [('id', '=', reward_product)])
        reward_analytic_tag_list = []
        if int(driver_analytic_id):
            reward_analytic_tag_list.append(int(driver_analytic_id))
        data = {
            'product_id': int(reward_product),
            'name': product.name,
            'account_id': account_id,
            'price_unit': self.total_reward_amount,
            'quantity': 1.0,
            'account_analytic_id': self.fleet_type_transport.reward_for_analytic_account_id.id if self.fleet_type_transport and self.fleet_type_transport.reward_for_analytic_account_id else int(driver_account_analytic_id) if int(driver_account_analytic_id) else False,
            'analytic_tag_ids': self.fleet_type_transport.reward_for_analytic_tag_id and [(6, 0, self.fleet_type_transport.reward_for_analytic_tag_id.ids)] or reward_analytic_tag_list and [(6, 0, reward_analytic_tag_list)] or False,
            'invoice_id': inv_id,
            'fleet_id': self.transportation_vehicle.id,
            'branch_id': self.env.user.user_branch_id.id,
            'invoice_line_tax_ids': product.supplier_taxes_id and [(6, 0, product.supplier_taxes_id.ids)] or False
        }
        return data

    # @api.multi
    def pay_trip_money(self):
        reward_amount = self.total_reward_amount
        fuel_amount = self.total_fuel_amount
        if self.state != 'vendor_trip':
            return True    
        if self.transportation_vehicle:
            vehicle_odometer_id = self.env['fleet.vehicle.odometer'].create({
                'vehicle_id': self.transportation_vehicle.id,
                'fleet_bx_trip_id': self.id,
                'src_location': self.form_transport.id if self.form_transport.id else False,
                'dest_location': self.route_id.waypoint_to_ids[-1].waypoint.id,
                'bsg_driver': self.transportation_driver.id if self.transportation_driver.id else False,
                'extra_distance': self.extra_distance if self.extra_distance else False,
                'trip_distance': self.trip_distance if self.trip_distance else False,
                'value': self.total_distance + self.transportation_vehicle.odometer,
                'date': self.arrival_date if self.arrival_date else False,
            })
            if vehicle_odometer_id:
                vehicle_odometer_id.vehicle_id.fleet_bx_trip_id = self.id
                vehicle_odometer_id.vehicle_id.expected_end_date = self.arrival_date
                vehicle_odometer_id.vehicle_id.route_id = self.route_id
        if (not reward_amount > 0) and (not fuel_amount > 0):
            return self.write({'state':'fuel_voucher'})    
        default_product = self.env['ir.config_parameter'].sudo().get_param('transport_management.default_fuel_product_id')
        default_account = self.fleet_type_transport.analytic_account_id.id if self.fleet_type_transport.analytic_account_id else False
        default_analytic_tag = self.fleet_type_transport.analytic_tag_ids.ids if self.fleet_type_transport.analytic_tag_ids else False
        product = self.env['product.product'].sudo().search([('id','=',default_product)])
        default_partner = False
        default_partner = self.env['ir.config_parameter'].sudo().get_param('transport_management.default_fuel_supplier_id')
        if not default_partner:
            default_partner = self.transportation_driver.partner_id.id
        journal_id = self.env['account.journal'].sudo().search(['|',('sub_type','in',['All']),('sub_type','in',['Payment']),('branches','in',self.env.user.user_branch_id.id),('type','in',['cash'])],limit=1)
        default_journal_id = self.env['ir.config_parameter'].sudo().get_param('transport_management.default_bx_vendor_journal_id')
        default_reward_product = self.env['ir.config_parameter'].sudo().get_param('transport_management.default_reward_for_load_id')
        default_reward_account = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                    'transport_management.default_reward_for_analytic_account_id')
        default_reward_analytic_tag = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                    'transport_management.default_reward_for_analytic_tag_ids')
        reward_product = self.env['product.product'].sudo().search([('id','=',default_reward_product)])
        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']
        inv_data = self._prepare_invoice(default_partner)
        print('..............inv_data..........', inv_data)
        invoice = inv_obj.create(inv_data)
        print('..............invoice..........',invoice)
        account_id = product.property_account_expense_id.id
        analytic_id = default_account
        analytic_tag_id = default_analytic_tag
        driver_analytic_id = default_reward_analytic_tag
        driver_account_analytic_id = default_reward_account
        fleet_id = self.transportation_vehicle.id
        user = self.env.user
        payment_method = self.env.ref('account.account_payment_method_manual_in')
        supplier_taxes_id = []
        if fuel_amount > 0:
            vals = self._prepare_invoice_line(invoice.id,account_id,analytic_id,analytic_tag_id,default_product,fuel_amount,product.supplier_taxes_id,fleet_id)
            inv_line_obj.create(vals)
        if reward_amount > 0:
            val = self._prepare_reward_invoice_line(invoice.id,account_id,default_reward_product,driver_account_analytic_id,driver_analytic_id,reward_product,reward_amount,reward_product.supplier_taxes_id)
            inv_line_obj.create(val)
        invoice._compute_amount()
        invoice._onchange_cash_rounding()
        if invoice.invoice_cash_rounding_id.strategy == 'add_invoice_line':
                invoice_line = self.env['account.move.line'].sudo().search([('name','=',invoice.invoice_cash_rounding_id.name),('invoice_id','=',invoice.id)],limit=1)
                invoice_line.write({'branch_id':user.user_branch_id.id,
                                    'account_analytic_id':default_account,
                                    'fleet_id':self.transportation_vehicle.id,
                                    'analytic_tag_ids':default_analytic_tag and [(6, 0, default_analytic_tag)] or False,
                                    })
        invoice.action_post()
        invoice_list = []
#         names = self.acc_link_vendor.number
        partner = invoice.partner_id.id
        invoice_list.append(invoice.id)
        create_voucher = self.env['account.payment'].with_context(search_default_inbound_filter=True).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'is_voucher_or_expense': True,
            'communication': str(self.transportation_no) + ' ' + 'عبارة عن قيمة مصــروف الطريق لرحلـة رقــم',
            'payment_reference': self.transportation_no,
            'partner_id': int(default_partner) if int(default_partner) else self.transportation_driver.partner_id.id,
            'amount': invoice.amount_total,
            'journal_id': int(default_journal_id) if int(default_journal_id) else journal_id.id,
            'transport': True,
            'date': str(fields.Date.today()),
            'collectionre': invoice.name,
            'branch_ids': self.env.user.user_branch_id.id,
            'invoice_ids': invoice_list and [(6, 0, invoice_list)] or False,
            'payment_method_id': payment_method.id,
            'bx_transport_id': self.id
        })
        #         payment_line = self.env['account.voucher.line.custom'].create({'payment_id' : create_voucher.id,
        #                                                                         'account_id' : account_id,
        #                                                                          'analytic_id' : analytic_id})
        create_voucher.post_state()
        # create_voucher.action_post()
        self.payment = create_voucher
        self.write({'state': 'fuel_voucher'})

    # @api.multi
    def _prepare_trans_invoice_line(self, inv_id, account_id, product, analytic_tag_id, analytic_id, default_product,
                                    fuel_amount, supplier_taxes_id):
        fule_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                           company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_product_id')
        default_account = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_analytic_account_id')
        product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                  company_id=self.env.user.company_id.id).search(
            [('id', '=', fule_product)])
        payment_id = self.env['account.payment'].search(
            ['|', ('bx_transport_id', '=', self.id), ('id', '=', self.payment.id)])
        amount = self.total_fuel_amount
        if payment_id:
            invoice_id = self.env['account.move'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                         company_id=self.env.user.company_id.id).search(
                [('number', '=', payment_id.collectionre)], limit=1)
            amt = invoice_id.invoice_line_ids[0]
            fuel_amount = amt.price_unit
            amount = self.total_fuel_amount - fuel_amount
            if self.total_fuel_amount == fuel_amount:
                amount = 0.0
        data = {
            'product_id': int(fule_product),
            'name': product.name,
            'account_id': account_id,
            'price_unit': amount if amount else 0.0,
            'quantity': 1.00,
            'account_analytic_id': int(default_account) if int(default_account) else False,
            'analytic_tag_ids': analytic_tag_id and [(6, 0, analytic_tag_id)] or False,
            'invoice_id': inv_id,
            'fleet_id': self.transportation_vehicle.id,
            'branch_id': self.env.user.user_branch_id.id,
            'invoice_line_tax_ids': product.supplier_taxes_id and [(6, 0, product.supplier_taxes_id.ids)] or False,
        }
        return data

    # @api.multi
    def _prepare_trans_reward_invoice_line(self, inv_id, account_id, product, driver_account_analytic_id,
                                           driver_analytic_id, reward_product, reward_amount, supplier_taxes_id):
        reward_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                             company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_reward_for_load_id')
        product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                  company_id=self.env.user.company_id.id).search(
            [('id', '=', reward_product)])
        payment_id = self.env['account.payment'].search(
            ['|', ('bx_transport_id', '=', self.id), ('id', '=', self.payment.id)])
        amount = self.total_reward_amount
        if payment_id:
            invoice_id = self.env['account.move'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                         company_id=self.env.user.company_id.id).search(
                [('number', '=', payment_id.collectionre)], limit=1)
            amt = invoice_id.invoice_line_ids[1]
            reward_amount = amt.price_unit
            amount = self.total_reward_amount - reward_amount
            if self.total_reward_amount == reward_amount:
                amount = 0.0
        data = {
            'product_id': int(reward_product),
            'name': product.name,
            'account_id': account_id,
            'price_unit': amount if amount else 0.0,
            'quantity': 1.0,
            'account_analytic_id': int(driver_account_analytic_id) or False,
            'analytic_tag_ids': driver_analytic_id and [(6, 0, driver_analytic_id)] or False,
            'invoice_id': inv_id,
            'fleet_id': self.transportation_vehicle.id,
            'branch_id': self.env.user.user_branch_id.id,
            'invoice_line_tax_ids': product.supplier_taxes_id and [(6, 0, product.supplier_taxes_id.ids)] or False
        }
        return data

    # @api.multi
    def pay_trip_money_trans(self):
        default_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_product_id')
        default_account = self.fleet_type_transport.analytic_account_id.id if self.fleet_type_transport.analytic_account_id else False
        default_analytic_tag = self.fleet_type_transport.analytic_tag_ids.ids if self.fleet_type_transport.analytic_tag_ids else []
        product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                  company_id=self.env.user.company_id.id).search(
            [('id', '=', default_product)])
        default_partner = False
        default_partner = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_supplier_id')
        if not default_partner:
            default_partner = self.transportation_driver.partner_id.id
        journal_id = self.env['account.journal'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                     company_id=self.env.user.company_id.id).search(
            ['|', ('sub_type', 'in', ['All']), ('sub_type', 'in', ['Payment']),
             ('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash'])], limit=1)
        default_journal_id = self.env['ir.config_parameter'].sudo().with_context(
            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_bx_vendor_journal_id')
        default_reward_product = self.env['ir.config_parameter'].sudo().with_context(
            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_reward_for_load_id')
        default_reward_account = self.fleet_type_transport.reward_for_analytic_account_id.id if self.fleet_type_transport.reward_for_analytic_account_id else False
        default_reward_analytic_tag = self.fleet_type_transport.reward_for_analytic_tag_id.id if self.fleet_type_transport.reward_for_analytic_tag_id else False
        reward_amount = self.total_reward_amount
        reward_product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                         company_id=self.env.user.company_id.id).search(
            [('id', '=', default_reward_product)])

        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']
        payment_method = self.env.ref('account.account_payment_method_manual_in')
        res = []
        for rec in self:
            payment_id = self.env['account.payment'].search(
                ['|', ('bx_transport_id', '=', rec.id), ('id', '=', rec.payment.id)])
            if payment_id:
                invoice_id = self.env['account.move'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                             company_id=self.env.user.company_id.id).search(
                    [('number', '=', payment_id.collectionre)], limit=1)
                f_amt = invoice_id.invoice_line_ids[0]
                fuel_amount = f_amt.price_unit
                f_amount = self.total_fuel_amount - fuel_amount
                amt = invoice_id.invoice_line_ids[1]
                reward_amount = amt.price_unit
                amount = self.total_reward_amount - reward_amount
                if self.total_fuel_amount > fuel_amount or self.total_reward_amount > reward_amount:
                    fuel_amount -= payment_id.amount
                    search_partner = self.env['res.partner'].search(
                        [('name', '=', str(rec.transportation_driver.partner_id.name))], limit=1)
                    inv_data = self._prepare_invoice(search_partner)
                    invoice = inv_obj.create(inv_data)
                    fleet_id = rec.transportation_vehicle.id
                    account_id = product.property_account_expense_id.id
                    analytic_id = default_account
                    analytic_tag_id = default_analytic_tag
                    driver_analytic_id = default_reward_analytic_tag
                    driver_account_analytic_id = default_reward_account
                    fuel_amount = self.total_fuel_amount
                    fleet_id = self.transportation_vehicle.id
                    user = self.env.user
                    supplier_taxes_id = []
                    vals = self._prepare_trans_invoice_line(invoice.id,account_id,analytic_id,analytic_tag_id,default_product,fuel_amount,product.supplier_taxes_id,fleet_id)
                    val = self._prepare_trans_reward_invoice_line(invoice.id,account_id,default_reward_product,driver_account_analytic_id,driver_analytic_id,reward_product,reward_amount,reward_product.supplier_taxes_id)
                    inv_line_obj.create(vals)
                    inv_line_obj.create(val)
                    invoice._compute_amount()
                    invoice._onchange_cash_rounding()
                    if invoice.invoice_cash_rounding_id.strategy == 'add_invoice_line':
                        invoice_line = self.env['account.move.line'].sudo().with_context(
                            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                            [('name', '=', invoice.invoice_cash_rounding_id.name), ('invoice_id', '=', invoice.id)], limit=1)
                        invoice_line.write({'branch_id': user.user_branch_id.id,
                                            'account_analytic_id': default_account,
                                            'fleet_id': self.transportation_vehicle.id,
                                            'analytic_tag_ids': default_analytic_tag and [(6, 0, default_analytic_tag)] or False,
                                            })
                    invoice.action_post()
                    invoice_list = []
                    #         names = self.acc_link_vendor.number
                    partner = invoice.partner_id.id
                    invoice_list.append(invoice.id)
                    create_voucher = self.env['account.payment'].with_context(
                        search_default_inbound_filter=True).create({
                        'payment_type': 'outbound',
                        'partner_type': 'supplier',
                        'is_voucher_or_expense': True,
                        'communication': str(
                            self.transportation_no) + ' ' + 'عبارة عن قيمة مصــروف الطريق لرحلـة رقــم',
                        'payment_reference': self.transportation_no,
                        'partner_id': int(default_partner) if int(
                            default_partner) else self.transportation_driver.partner_id.id,
                        'amount': invoice.amount_total,
                        'journal_id': int(default_journal_id) if int(default_journal_id) else journal_id.id,
                        'transport': True,
                        'date': str(fields.Date.today()),
                        'collectionre': invoice.number,
                        'branch_ids': self.env.user.user_branch_id.id,
                        'invoice_ids': invoice_list and [(6, 0, invoice_list)] or False,
                        'payment_method_id': payment_method.id,
                        'bx_transport_id': self.id
                    })
                    create_voucher.post_state()
                    create_voucher.action_post()
                    self.payment = create_voucher
                else:
                    raise UserError(_("Fuel amount or Total Reward amount must be greater than voucher amount!"))
            else:
                raise UserError(_("Use Pay Transport Trip button"))

    # @api.multi
    def action_view_payment(self):
        search_ids = self.env['account.payment'].search(
            ['|', ('bx_transport_id', '=', self.id), ('id', '=', self.payment.id)])
        search_ids = search_ids.filtered(lambda pay: pay.state == 'posted')
        return {
            'name': _('Fuel voucher'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'domain': [('id', 'in', search_ids.ids)],
            'type': 'ir.actions.act_window',
            'context': {'create': False}
        }

    # 
    def _get_payment_voucher(self):
        search_ids = self.env['account.payment'].search(
            ['|', ('bx_transport_id', '=', self.id), ('id', '=', self.payment.id)])
        self.paymen = len(search_ids.filtered(lambda pay: pay.state == 'posted'))

    # 
    @api.depends('loading_date', 'arrival_time')
    def _compute_time(self):
        if self.loading_date and self.arrival_time:
            start_time = self.loading_date
            end_time = self.arrival_time
            time = timedelta(hours=end_time)
            total = start_time + time
            self.arrival_date = total

    # Shipper and Receiver Details

    # Sender Validation Checks
    # 
    @api.constrains('sender_id_card_no')
    def _check_sender_id(self):
        if self.sender_id_card_no and self.sender_type == '2':
            match = re.match(r'2[0-9]{9}', self.sender_id_card_no)
            if match is None or len(str(self.sender_id_card_no)) != 10:
                raise UserError(
                    _('Sender ID no must be start from 2 and must have 10 digits.'),
                )
        if self.sender_id_card_no and self.sender_type == '1':
            match = re.match(r'1[0-9]{9}', self.sender_id_card_no)
            if match is None or len(str(self.sender_id_card_no)) != 10:
                raise UserError(
                    _('Sender ID no must be start from 1 and must have 10 digits.'),
                )

    # 
    @api.constrains('sender_visa_no')
    def _check_sender_visa_no(self):
        if self.sender_visa_no:
            match = re.match(r'[a-zA-Z0-9]', self.sender_visa_no)
            if match is None or len(self.sender_visa_no) > 15:
                raise UserError(
                    _('Sender Visa/Passport no must contain Alphanumeric and 15 digits!'),
                )

    # Reciever Validation Checks
    # 
    @api.constrains('receiver_id_card_no')
    def _check_receiver_id_card_no(self):
        if self.receiver_id_card_no and self.receiver_type == '2':
            match = re.match(r'2[0-9]{9}', self.receiver_id_card_no)
            if match is None or len(str(self.receiver_id_card_no)) != 10:
                raise UserError(
                    _('Receiver ID no must be start from 2 and must have 10 digits.'),
                )
        if self.receiver_id_card_no and self.receiver_type == '1':
            match = re.match(r'1[0-9]{9}', self.receiver_id_card_no)
            if match is None or len(str(self.receiver_id_card_no)) != 10:
                raise UserError(
                    _('Receiver ID no must be start from 1 and must have 10 digits.'),
                )

    # 
    @api.constrains('receiver_visa_no')
    def _check_receiver_visa_no(self):
        if self.receiver_visa_no:
            match = re.match(r'[a-zA-Z0-9]', self.receiver_visa_no)
            if match is None or len(self.receiver_visa_no) > 15:
                raise UserError(
                    _('Receiver Visa/Passport no must contain Alphanumeric and 15 digits!'),
                )

    # Get Bill
    # 
    def _get_refund_invoices(self):
        invoice_ids = self.env['account.move'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                      company_id=self.env.user.company_id.id).search(
            [('return_vendor_tranport_id', '=', self.id)])
        self.update({
            'refund_invoice_count': len(set(invoice_ids.ids)),
            'reversal_move_ids': invoice_ids.ids,
        })

    # Get Invoice
    # 
    def _get_invoice_refund_invoices(self):
        invoice_ids = self.env['account.move'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                      company_id=self.env.user.company_id.id).search(
            [('return_customer_tranport_id', '=', self.id)])
        self.update({
            'refund_customer_invoice_count': len(set(invoice_ids.ids)),
            'refund_customer_invoice_ids': invoice_ids.ids,
        })

    # getting return bill state
    # 
    def _get_return_validate(self):
        for rec in self:
            rec.is_return_validate = False
            for data in rec.reversal_move_ids:
                if data.state == 'paid':
                    rec.is_return_validate = True
                else:
                    rec.is_return_validate = False

    # getting return invoice state
    # 
    def _get_customer_return_validate(self):
        for rec in self:
            rec.is_customer_return_validate = False
            for data in rec.refund_customer_invoice_ids:
                if data.state == 'paid':
                    rec.is_customer_return_validate = True
                else:
                    rec.is_customer_return_validate = False

    # getting created invoice status
    # 
    def _get_invoice_state(self):
        if self.invoice_id:
            if self.invoice_id.payment_state != 'paid':
                self.invoice_status = True
            else:
                self.invoice_status = False
        else:
            self.invoice_status = False

    sender_name = fields.Char(string='Sender Name', track_visibility=True)
    company = fields.Char(string='Company Name', store=True, track_visibility=True)
    customer_number = fields.Char(string='Customer Number', store=True, track_visibility=True)
    phone = fields.Char(string='Phone', store=True, track_visibility=True)
    mobile = fields.Char(string='Mobile', store=True, track_visibility=True)
    street = fields.Char(string='Address', store=True, track_visibility=True)
    street2 = fields.Char(string='Street2', store=True, track_visibility=True)
    city = fields.Char(string='City', store=True, track_visibility=True)
    state_id = fields.Many2one('res.country.state', string='State', store=True, track_visibility=True)
    zip = fields.Char(string='Zip', store=True, track_visibility=True)
    country_id = fields.Many2one('res.country', string="Country", store=True, track_visibility=True)
    sender_type = fields.Selection(string="Sender Type", track_visibility=True, selection=[
        ('1', 'Saudi'),
        ('2', 'Non-Saudi'),
        ('3', 'Corporate'),
    ])
    sender_nationality = fields.Many2one(string="Sender Nationality", comodel_name="res.country", track_visibility=True)
    sender_id_type = fields.Selection(string="Sender ID Type", track_visibility=True, selection=[
        ('saudi_id_card', 'Saudi ID Card'),
        ('iqama', 'Iqama'),
        ('gcc_national', 'GCC National'),
        ('passport', 'Passport'),
        ('other', 'Other'),
    ])
    sender_id_card_no = fields.Char(string="Sender ID Card No", track_visibility=True)
    sender_visa_no = fields.Char(string="Sender Visa No", track_visibility=True)

    same_as_customer = fields.Boolean(string='Same As Customer', track_visibility=True)
    same_as_sender = fields.Boolean(string='Same As Sender', track_visibility=True)

    receiver_name = fields.Char(string='Receiver Name', track_visibility=True)
    rec_company = fields.Char(string='Company Name', store=True, track_visibility=True)
    rec_customer_number = fields.Char(string='Customer Number', store=True, track_visibility=True)
    rec_phone = fields.Char(string='Phone', store=True, track_visibility=True)
    rec_mobile = fields.Char(string='Mobile', store=True, track_visibility=True)
    rec_street = fields.Char(string='Address', store=True, track_visibility=True)
    rec_street2 = fields.Char(string='Street2', store=True, track_visibility=True)
    rec_city = fields.Char(string='City', store=True, track_visibility=True)
    rec_state_id = fields.Many2one('res.country.state', string='State', store=True, track_visibility=True)
    rec_zip = fields.Char(string='Zip', store=True, track_visibility=True)
    rec_country_id = fields.Many2one('res.country', string="Country", store=True, track_visibility=True)
    receiver_type = fields.Selection(string="Receiver Type", track_visibility=True, selection=[
        ('1', 'Saudi'),
        ('2', 'Non-Saudi'),
        ('3', 'Corporate'),
    ])
    receiver_nationality = fields.Many2one(string="Receiver Nationality", comodel_name="res.country",
                                           track_visibility=True)
    receiver_id_type = fields.Selection(string="Receiver ID Type", track_visibility=True, selection=[
        ('saudi_id_card', 'Saudi ID Card'),
        ('iqama', 'Iqama'),
        ('gcc_national', 'GCC National'),
        ('passport', 'Passport'),
        ('other', 'Other'),
    ])
    receiver_id_card_no = fields.Char(string="Receiver ID Card No", track_visibility=True)
    receiver_visa_no = fields.Char(string="Receiver Visa No", track_visibility=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed Order'),
        ('issue_bill', 'Issue Bill'),
        ('vendor_trip', 'Vendor Trip Money'),
        ('fuel_voucher', 'Fuel Voucher'),
        ('receive_pod', 'Received POD'),
        ('done', 'Invoiced'),
        ('cancel', 'Cancel'),
    ], default='draft', track_visibility=True)

    reversal_move_ids = fields.Many2many("account.move", string='Refund Invoices', compute="_get_refund_invoices",
                                          readonly=True,
                                          copy=False)
    is_return_validate = fields.Boolean(string="Is Payment", compute="_get_return_validate")
    refund_invoice_count = fields.Integer(string='Refund Invoice Count', compute='_get_refund_invoices', readonly=True)

    refund_customer_invoice_ids = fields.Many2many("account.move", string='Refund Invoices',
                                                   compute="_get_invoice_refund_invoices", readonly=True,
                                                   copy=False)
    is_customer_return_validate = fields.Boolean(string="Is Payment", compute="_get_customer_return_validate")
    refund_customer_invoice_count = fields.Integer(string='Refund Invoice Count',
                                                   compute='_get_invoice_refund_invoices', readonly=True)
    invoice_status = fields.Boolean("Invoice Status", compute="_get_invoice_state")

    # open wizrad for invoice register payment
    def register_payment_for_invoice(self):
        view_id = self.env.ref('account.view_account_payment_register_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Name',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.payment',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_payment_type': 'inbound',
                'default_partner_id': self.invoice_id.partner_id.id,
                'default_partner_type': 'customer',
                'default_amount': self.invoice_id.amount_residual,
                'default_communication': self.transportation_no,
                'default_invoice_ids': [(4, self.invoice_id.id, None)]
            }
        }

    # View Refund Invoices
    # @api.multi
    def action_view_refund_invoice(self, context):
        # invoices = self.mapped(context.get('field'))
        invoices = self.env['account.move'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                   company_id=self.env.user.company_id.id).search(
            [('return_customer_tranport_id', '=', self.id)])
        action = self.env.ref('account.action_move_out_refund_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # View Refund Bill
    # @api.multi
    def action_view_refund_bill(self, context):
        # invoices = self.mapped(context.get('field'))
        invoices = self.env['account.move'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                   company_id=self.env.user.company_id.id).search(
            [('return_vendor_tranport_id', '=', self.id)])
        action = self.env.ref('account.action_invoice_in_refund').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # 
    @api.constrains('expiration_date')
    def _validateon_expiry(self):
        if self.expiration_date and self.order_date and self.expiration_date <= self.order_date:
            raise ValidationError(_("Expiration Date Should be greater Than Order Date"))

    @api.onchange('same_as_customer')
    def change_same_as_customer_value(self):
        if self.same_as_customer:
            self.sender_name = self.customer.name
            self.company = self.customer.parent_id.name
            self.customer_number = self.customer.commmercial_number
            self.phone = self.customer.phone
            self.mobile = self.customer.mobile
            self.street = self.customer.street
            self.street2 = self.customer.street2
            self.city = self.customer.city
            self.state_id = self.customer.state_id.id
            self.zip = self.customer.zip
            self.country_id = self.customer.country_id.id
            self.sender_type = self.customer.customer_type
            self.sender_nationality = self.customer.customer_nationality
            self.sender_id_type = self.customer.customer_id_type
            self.sender_id_card_no = self.customer.customer_id_card_no or self.customer.iqama_no
            self.sender_visa_no = self.customer.customer_visa_no

    @api.onchange('same_as_sender')
    def change_same_as_sender_value(self):
        if self.same_as_sender:
            self.receiver_name = self.sender_name
            self.rec_company = self.company
            self.rec_customer_number = self.customer_number
            self.rec_phone = self.phone
            self.rec_mobile = self.mobile
            self.rec_street = self.street
            self.rec_street2 = self.street2
            self.rec_city = self.city
            self.rec_state_id = self.state_id.id
            self.rec_zip = self.zip
            self.rec_country_id = self.country_id.id
            self.receiver_type = self.sender_type
            self.receiver_nationality = self.sender_nationality
            self.receiver_id_type = self.sender_id_type
            self.receiver_id_card_no = self.sender_id_card_no
            self.receiver_visa_no = self.sender_visa_no

    @api.depends('transport_management_line.total_amount')
    def _amount_all(self):
        for trans in self:
            total_before_taxes = tax_amount = 0.0
            for trans_line in trans.transport_management_line:
                total_before_taxes += trans_line.total_before_taxes
                tax_amount += trans_line.tax_amount

            trans.update({
                'total_before_taxes': total_before_taxes,
                'tax_amount': tax_amount,
                'total_amount': total_before_taxes + tax_amount,
            })

    @api.onchange('transport_management_line')
    def _Fleet_from(self):
        for res in self:
            for res_line in res.transport_management_line:
                res.fleet_type_transport = res_line.fleet_type

    @api.model
    def create(self, vals):
        res = super(TransportManagement, self).create(vals)
        if not res.is_government:
            if res.site_export.id:
                res.transportation_no = 'BX' + res.site_export.branch_no + self.env['ir.sequence'].next_by_code(
                    'transport.management')
            elif res.site_import.id:
                res.transportation_no = 'BX' + res.site_import.branch_no + self.env['ir.sequence'].next_by_code(
                    'transport.management')
            else:
                res.transportation_no = 'BX' + self.env['ir.sequence'].next_by_code('transport.management')
        return res

    @api.model
    def _cron_bx_invoice_draft_delete(self):
        for res in self.search([('payment_method.payment_type', 'in', ['credit'])]):
            if res.invoice_id and res.invoice_id.state == 'draft':
                res.invoice_id.unlink()

    # @api.multi
    def _prepare_refund_invoice(self, transportation_driver):
        self.ensure_one()
        journal_id = self.env['account.journal'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                     company_id=self.env.user.company_id.id).search(
            [('type', '=', 'purchase')], limit=1)
        default_journal_id = self.env['ir.config_parameter'].sudo().with_context(
            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_bx_vendor_journal_id')
        default_partner = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_supplier_id')
        driver = self.env['res.partner'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                             company_id=self.env.user.company_id.id).search(
            [('id', '=', default_partner)])
        default_cash_rounding = self.env['ir.config_parameter'].sudo().with_context(
            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_cash_rounding_id')
        cash_rounding = self.env['account.cash.rounding'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).search(
            [('id', '=', default_cash_rounding)])
        account_id = self.transportation_driver.partner_id.property_account_payable_id
        if not journal_id:
            raise UserError(_("Be Sure You Have Cash Journal With Waypoints"))
        invoice_vals = {
            'name': '',
            'invoice_origin': self.transportation_no,
            'invoice_cash_rounding_id': default_cash_rounding,
            'move_type': 'in_refund',
            'account_id': driver.property_account_payable_id.id if driver.property_account_payable_id else account_id.id,
            # self.transportation_driver.partner_id.property_account_payable_id.id,
            'partner_id': int(default_partner) if int(default_partner) else self.transportation_driver.partner_id.id,
            'journal_id': int(default_journal_id) if int(default_journal_id) else journal_id.id,
            'comment': self.transportation_no,
            'currency_id': self.env.user.company_id.currency_id.id,
            'user_id': self.env.user.id,
        }
        return invoice_vals

    #  Prepare Invoice Line
    # @api.multi
    def _prepare_refund_invoice_line(self, inv_id, account_id, product, analytic_tag_id, analytic_id, default_product,
                                     fuel_amount, supplier_taxes_id):
        fule_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                           company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_product_id')
        default_account = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_analytic_account_id')
        product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                  company_id=self.env.user.company_id.id).search(
            [('id', '=', fule_product)])
        data = {
            'product_id': int(fule_product),
            'name': product.name,
            'account_id': account_id,
            'price_unit': self.total_fuel_amount,
            'quantity': 1.00,

            'account_analytic_id': int(default_account) if int(default_account) else False,
            'analytic_tag_ids': analytic_tag_id and [(6, 0, analytic_tag_id)] or False,
            'invoice_id': inv_id,
            'fleet_id': self.transportation_vehicle.id,
            'branch_id': self.env.user.user_branch_id.id,
            'invoice_line_tax_ids': product.supplier_taxes_id and [(6, 0, product.supplier_taxes_id.ids)] or False,
        }
        return data

    # @api.multi
    def _prepare_refund_reward_invoice_line(self, inv_id, account_id, product, driver_account_analytic_id,
                                            driver_analytic_id, reward_product, reward_amount, supplier_taxes_id):
        reward_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                             company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_reward_for_load_id')
        product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                  company_id=self.env.user.company_id.id).search(
            [('id', '=', reward_product)])
        data = {
            'product_id': int(reward_product),
            'name': product.name,
            'account_id': account_id,
            'price_unit': self.total_reward_amount,
            'quantity': 1.0,
            'account_analytic_id': int(driver_account_analytic_id) or False,
            'analytic_tag_ids': driver_analytic_id and [(6, 0, driver_analytic_id)] or False,
            'invoice_id': inv_id,
            'fleet_id': self.transportation_vehicle.id,
            'branch_id': self.env.user.user_branch_id.id,
            'invoice_line_tax_ids': product.supplier_taxes_id and [(6, 0, product.supplier_taxes_id.ids)] or False
        }
        return data

    # @api.multi
    def action_draft(self):
        if self.payment:
            default_product = self.env['ir.config_parameter'].sudo().with_context(
                force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                'transport_management.default_fuel_product_id')
            default_account = self.env['ir.config_parameter'].sudo().with_context(
                force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                'transport_management.default_fuel_analytic_account_id')
            default_analytic_tag = self.env['ir.config_parameter'].sudo().with_context(
                force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                'transport_management.default_fuel_analytic_tag_ids')
            product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                      company_id=self.env.user.company_id.id).search(
                [('id', '=', default_product)])
            default_partner = False
            default_partner = self.env['ir.config_parameter'].sudo().with_context(
                force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                'transport_management.default_fuel_supplier_id')
            if not default_partner:
                default_partner = self.transportation_driver.partner_id.id
            journal_id = self.env['account.journal'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                         company_id=self.env.user.company_id.id).search(
                ['|', ('sub_type', 'in', ['All']), ('sub_type', 'in', ['Payment']),
                 ('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash'])], limit=1)
            default_journal_id = self.env['ir.config_parameter'].sudo().with_context(
                force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                'transport_management.default_bx_vendor_journal_id')
            default_reward_product = self.env['ir.config_parameter'].sudo().with_context(
                force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                'transport_management.default_reward_for_load_id')
            default_reward_account = self.env['ir.config_parameter'].sudo().with_context(
                force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                'transport_management.default_reward_for_analytic_account_id')
            default_reward_analytic_tag = self.env['ir.config_parameter'].sudo().with_context(
                force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                'transport_management.default_reward_for_analytic_tag_ids')
            reward_amount = self.total_reward_amount
            reward_product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                             company_id=self.env.user.company_id.id).search(
                [('id', '=', default_reward_product)])

            inv_obj = self.env['account.move']
            inv_line_obj = self.env['account.move.line']
            inv_data = self._prepare_refund_invoice(default_partner)
            invoice = inv_obj.create(inv_data)
            fuel_amount = self.total_fuel_amount
            account_id = product.property_account_expense_id.id
            analytic_id = default_account
            analytic_tag_id = [int(default_analytic_tag)]
            driver_analytic_id = [int(default_reward_analytic_tag)]
            driver_account_analytic_id = default_reward_account
            fleet_id = self.transportation_vehicle.id
            user = self.env.user
            payment_method = self.env.ref('account.account_payment_method_manual_in')
            supplier_taxes_id = []
            vals = self._prepare_refund_invoice_line(invoice.id, account_id, analytic_id, analytic_tag_id,
                                                     default_product, fuel_amount, product.supplier_taxes_id, fleet_id)
            val = self._prepare_refund_reward_invoice_line(invoice.id, account_id, default_reward_product,
                                                           driver_account_analytic_id, driver_analytic_id,
                                                           reward_product, reward_amount,
                                                           reward_product.supplier_taxes_id)
            inv_line_obj.create(vals)
            inv_line_obj.create(val)
            invoice._compute_amount()
            invoice._onchange_cash_rounding()
            if invoice.invoice_cash_rounding_id.strategy == 'add_invoice_line':
                invoice_line = self.env['account.move.line'].sudo().with_context(
                    force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                    [('name', '=', invoice.invoice_cash_rounding_id.name), ('invoice_id', '=', invoice.id)], limit=1)
                invoice_line.write({'branch_id': user.user_branch_id.id,
                                    'account_analytic_id': default_account,
                                    'fleet_id': self.transportation_vehicle.id,
                                    'analytic_tag_ids': default_analytic_tag and [(6, 0, default_analytic_tag)] or False,
                                    })
            invoice.action_post()

            self.payment.write({'state': 'cancelled'})

            self.write({'state': 'draft'})
        # Customer Invoice
        invoice = self.env['account.move']
        invoice_lines = self.env['account.move.line']

        default_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_product_id')
        default_account = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_analytic_account_id')
        default_analytic_tag = self.env['ir.config_parameter'].sudo().with_context(
            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_analytic_tag_ids')
        product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                  company_id=self.env.user.company_id.id).search(
            [('id', '=', default_product)])
        department = self.env['hr.department'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                   company_id=self.env.user.company_id.id).search(
            [('name', '=', self.driver.department_id.parent_id.name)])
        default_cash_rounding = self.env['ir.config_parameter'].sudo().with_context(
            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_cash_rounding_id')
        user = self.env.user

        if self.acc_link_vendor:
            if self.acc_link_vendor.state == 'draft':
                self.acc_link_vendor.unlink()

                self.write({'state': 'draft'})
            elif self.acc_link_vendor.state != 'draft':
                create_invoice = invoice.create({
                    'partner_id': self.transportation_driver.partner_id.id or self.supplier_name.id,
                    'invoice_date': date.today(),
                    'number': self.transportation_no,
                    'name': self.transportation_no,
                    'invoice_cash_rounding_id': default_cash_rounding,
                    'type': 'in_refund',
                })
                create_invoice_lines = invoice_lines.create({
                    'product_id': default_product,
                    'account_analytic_id': default_account,
                    'branch_id': user.user_branch_id.id,
                    'fleet_id': self.transportation_vehicle.id,
                    'analytic_tag_ids': default_analytic_tag and [(6, 0, default_analytic_tag)] or False,
                    'quantity': 1,
                    'invoice_line_tax_ids': product.supplier_taxes_id and [(6, 0, product.supplier_taxes_id.ids)] or False,
                    'price_unit': self.total_fuel_amount,
                    'account_id': product.property_account_expense_id.id,
                    'name': '- مصروف الطريق من' + (self.form_transport.route_waypoint_name) + '- الي' + (
                        self.to_transport.route_waypoint_name) + '- بمسافة' + str(self.total_distance),
                    'invoice_id': create_invoice.id,
                })

                default_reward_product = self.env['ir.config_parameter'].sudo().with_context(
                    force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                    'transport_management.default_reward_for_load_id')
                default_reward_account = self.env['ir.config_parameter'].sudo().with_context(
                    force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                    'transport_management.default_reward_for_analytic_account_id')
                default_reward_analytic_tag = self.env['ir.config_parameter'].sudo().with_context(
                    force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                    'transport_management.default_reward_for_analytic_tag_ids')

                reward_product = self.env['product.product'].sudo().with_context(
                    force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                    [('id', '=', default_reward_product)])

                create_driver_invoice_lines = invoice_lines.create({
                    'product_id': default_reward_product,
                    'account_analytic_id': default_reward_account,
                    'branch_id': user.user_branch_id.id,
                    'fleet_id': self.transportation_vehicle.id,
                    'analytic_tag_ids': default_reward_analytic_tag and [(6, 0, default_reward_analytic_tag)] or False,
                    'quantity': 1,
                    'invoice_line_tax_ids': reward_product.supplier_taxes_id and [(6, 0, reward_product.supplier_taxes_id.ids)] or False,
                    'price_unit': self.total_reward_amount,
                    'account_id': reward_product.property_account_expense_id.id,
                    'name': reward_product.name or False,
                    'invoice_id': create_invoice.id,
                })

                create_invoice._compute_amount()
                create_invoice._onchange_cash_rounding()
                if create_invoice.invoice_cash_rounding_id.strategy == 'add_invoice_line':
                    invoice_line = self.env['account.move.line'].sudo().with_context(
                        force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                        [('name', '=', create_invoice.invoice_cash_rounding_id.name),
                         ('id', 'in', create_invoice.invoice_line_ids.ids)], limit=1)
                    invoice_line.write({
                        'account_analytic_id': default_account,
                        'branch_id': user.user_branch_id.id,
                        'fleet_id': self.transportation_vehicle.id,
                        'analytic_tag_ids': default_analytic_tag and [(6, 0, default_analytic_tag)] or False})
                create_invoice.action_post()
                create_invoice._onchange_invoice_line_ids()
                self.acc_link_vendor = create_invoice.id
                self.refund_vendor_id = create_invoice.id
                self.write({'state': 'draft'})

        if self.invoice_id:
            if self.invoice_id.state == 'draft':
                self.invoice_id.unlink()
                self.write({'state': 'draft'})

            elif self.invoice_id.state != 'draft':
                invoice_create = invoice.create({
                    'partner_id': self.customer.id,
                    'invoice_date': date.today(),
                    'move_type': 'out_invoice',
                    'invoice_payment_term_id': self.payment_terms.id,
                    'name': self.transportation_no,
                })
                for x in self.transport_management_line:
                    invoice_create_lines = invoice_lines.create({
                        'product_id': x.product_id.id,
                        'name': x.description,
                        'department_id': department.id,
                        'branch_id': user.user_branch_id.id,
                        'account_analytic_id': default_account,
                        'fleet_id': self.transportation_vehicle.id,
                        'analytic_tag_ids': default_analytic_tag and [(6, 0, default_analytic_tag)] or False,
                        'quantity': x.product_uom_qty,
                        'price_unit': x.price,
                        'invoice_line_tax_ids': x.tax_ids and [(6, 0, x.tax_ids.ids)] or False,
                        'price_subtotal': x.total_amount,
                        'account_id': x.product_id.property_account_income_id.id or False,
                        'invoice_id': invoice_create.id,
                    })
                    invoice_create._onchange_invoice_line_ids()
                    invoice_create._compute_amount()
                self.invoice_id = invoice_create.id
                self.acc_link = invoice_create.id
                self.write({'state': 'draft'})

        return self.write({'state': 'draft'})

    # @api.multi
    def action_confirm(self):
        return self.write({'state': 'confirm'})

    # @api.multi
    def action_issue_bill(self):
        return self.write({'state': 'issue_bill'})

    # @api.multi
    def action_vendor_trip(self):
        if not self.is_government:
            if not self.fleet_type_transport:
                raise UserError('Please! Enter Fleet Type.')
        if self.total_fuel_amount <= 0:
            raise UserError('Please! Total Fuel Expense	must be greater than zero.')
        if not self.route_id:
            raise UserError('Please! Enter Route.')
        if not self.transportation_vehicle:
            raise UserError('Please! Enter Transportation Vehicle.')
        if self.transportation_vehicle.rented_vehicle:
            return self.write({'state':'receive_pod'})
        if self.pull_from_other_bx:
            if self.other_bx_id:
                return self.write({'state': 'receive_pod'})
            else:
                raise UserError('Please! Enter Other Bx.')
        return self.write({'state': 'vendor_trip'})

    # @api.multi
    def action_receive_pod(self):
        return self.write({'state': 'receive_pod'})

    # @api.multi
    def action_normal_cancel(self):
        return self.write({'state': 'cancel'})

    # @api.multi
    def action_done(self):
        if self.transport_management_line:
            if self.payment_method.payment_type in ['cash', 'pod']:
                for rec in self:
                    invoice = self.env['account.move']
                    invoice_lines = self.env['account.move.line']
                    journal_id = self.env['account.journal'].sudo().with_context(
                        force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                        [('type', '=', 'sale'), ('company_id', '=', self.env.user.company_id.id)], limit=1)
                    default_journal_id = self.env['ir.config_parameter'].sudo().with_context(
                        force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                        'transport_management.default_bx_customer_journal_id')
                    default_account = self.env['ir.config_parameter'].sudo().with_context(
                        force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                        'transport_management.default_invoice_analytic_account_id')
                    default_analytic_tag = self.env['ir.config_parameter'].sudo().with_context(
                        force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                        'transport_management.default_invoice_analytic_tags')
                    department = self.env['hr.department'].sudo().with_context(
                        force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                        [('name', '=', self.driver.department_id.parent_id.parent_id.name)])
                    user = self.env.user

                    if rec.clearance_mode == 'import' and not rec.invoice_id:
                        invoice_create = invoice.create({
                            'partner_id': rec.customer.id,
                            'invoice_date': date.today(),
                            'move_type': 'out_invoice',
                            'invoice_payment_term_id': rec.payment_terms.id,
                            'name': rec.transportation_no,
                            'journal_id': int(default_journal_id) if int(default_journal_id) else journal_id.id,
                            'transport_cus_inv_id': rec.id
                        })
                        for x in rec.transport_management_line:
                            invoice_create_lines = invoice_lines.create({
                                'product_id': x.product_id.id,
                                'name': x.description,
                                'department_id': department.id,
                                'branch_id': user.user_branch_id.id,
                                 'account_analytic_id': self.vehicle_type_domain_id.sales_analytic_account.id if self.vehicle_type_domain_id and self.vehicle_type_domain_id.sales_analytic_account else default_account,
                                'fleet_id': rec.transportation_vehicle.id,
                                'analytic_tag_ids': self.vehicle_type_domain_id.sales_analytic_tag and [(6, 0,
                                                                                                         self.vehicle_type_domain_id.sales_analytic_tag.ids)] or default_analytic_tag and [
                                                        (6, 0, default_analytic_tag)] or False,
                                'quantity': x.product_uom_qty,
                                'price_unit': x.price,
                                'invoice_line_tax_ids': x.tax_ids and [(6, 0, x.tax_ids.ids)] or False,
                                'price_subtotal': x.total_amount,
                                'account_id': x.product_id.property_account_income_id.id or False,
                                'invoice_id': invoice_create.id,
                            })
                            invoice_create.write({'payment_method': rec.payment_method.id})
                            invoice_create._onchange_invoice_line_ids()
                            invoice_create._compute_amount()
                            invoice_create.action_post()
                        rec.invoice_id = invoice_create.id
                        rec.acc_link = invoice_create.id

                    if rec.clearance_mode == 'export' and not rec.invoice_id:
                        invoice_create = invoice.create({
                            'partner_id': rec.customer.id,
                            'invoice_date': date.today(),
                            'move_type': 'out_invoice',
                            'invoice_payment_term_id': rec.payment_terms.id,
                            'name': rec.transportation_no,
                            'journal_id': int(default_journal_id) if int(default_journal_id) else journal_id.id,
                            'transport_cus_inv_id': rec.id
                        })

                        for x in rec.transport_management_line:
                            invoice_create_lines = invoice_lines.create({
                                'product_id': x.product_id.id,
                                'name': x.description,
                                'department_id': department.id,
                                'branch_id': user.user_branch_id.id,
                                'account_analytic_id': self.vehicle_type_domain_id.sales_analytic_account.id if self.vehicle_type_domain_id and self.vehicle_type_domain_id.sales_analytic_account else default_account,
                                'fleet_id': rec.transportation_vehicle.id,
                                'analytic_tag_ids': self.vehicle_type_domain_id.sales_analytic_tag and [(6, 0,
                                                                                                         self.vehicle_type_domain_id.sales_analytic_tag.ids)] or default_analytic_tag and [
                                                        (6, 0, default_analytic_tag)] or False,
                                'quantity': x.product_uom_qty,
                                'price_unit': x.price,
                                'invoice_line_tax_ids': x.tax_ids and [(6, 0, x.tax_ids.ids)] or False,
                                'price_subtotal': x.total_amount,
                                'account_id': x.product_id.property_account_income_id.id or False,
                                'invoice_id': invoice_create.id,
                            })
                            invoice_create.write({'payment_method': rec.payment_method.id})
                            invoice_create._onchange_invoice_line_ids()
                            invoice_create._compute_amount()
                            invoice_create.action_post()
                        rec.invoice_id = invoice_create.id
                        rec.acc_link = invoice_create.id
                return rec.write({'state': 'done'})
            else:
                return self.write({'state': 'done'})
        else:
            raise UserError('Please! Create must be one line.')

    # @api.multi
    def action_view_invoice(self):
        xml_id = 'account.view_move_form'
        form_view_id = self.env.ref(xml_id).id
        return {
            'name': _('Employee log'),
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(form_view_id, 'form')],
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'domain': [('id', 'in', self.invoice_id.ids)],
            'type': 'ir.actions.act_window',
        }

    # @api.multi
    def _prepare_to_cancel_invoice(self, transportation_driver):
        self.ensure_one()
        journal_id = self.env['account.journal'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                     company_id=self.env.user.company_id.id).search(
            [('type', '=', 'purchase')], limit=1)
        default_partner = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_supplier_id')
        driver = self.env['res.partner'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                             company_id=self.env.user.company_id.id).search(
            [('id', '=', default_partner)])
        default_cash_rounding = self.env['ir.config_parameter'].sudo().with_context(
            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_cash_rounding_id')
        cash_rounding = self.env['account.cash.rounding'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).search(
            [('id', '=', default_cash_rounding)])
        account_id = self.transportation_driver.partner_id.property_account_payable_id
        if not journal_id:
            raise UserError(_("Be Sure You Have Cash Journal With Waypoints"))
        invoice_vals = {
            'name': '',
            'invoice_origin': self.transportation_no,
            'invoice_cash_rounding_id': default_cash_rounding,
            'move_type': 'in_refund',
            'account_id': driver.property_account_payable_id.id if driver.property_account_payable_id else account_id.id,
            # self.transportation_driver.partner_id.property_account_payable_id.id,
            'partner_id': int(default_partner) if int(default_partner) else self.transportation_driver.partner_id.id,
            'journal_id': journal_id.id,
            'comment': self.transportation_no,
            'currency_id': self.env.user.company_id.currency_id.id,
            'user_id': self.env.user.id,
        }
        return invoice_vals

    #  Prepare Invoice Line
    # @api.multi
    def _prepare_to_cancel_invoice_line(self, inv_id, account_id, product, analytic_tag_id, analytic_id,
                                        default_product, fuel_amount, supplier_taxes_id):
        fule_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                           company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_product_id')
        default_account = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_fuel_analytic_account_id')
        product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                  company_id=self.env.user.company_id.id).search(
            [('id', '=', fule_product)])
        data = {
            'product_id': int(fule_product),
            'name': product.name,
            'account_id': account_id,
            'price_unit': self.total_fuel_amount,
            'quantity': 1.00,

            'account_analytic_id': int(default_account) if int(default_account) else False,
            'analytic_tag_ids': analytic_tag_id and [(6, 0, analytic_tag_id)] or False,
            'invoice_id': inv_id,
            'fleet_id': self.transportation_vehicle.id,
            'branch_id': self.env.user.user_branch_id.id,
            'invoice_line_tax_ids': product.supplier_taxes_id and [(6, 0, product.supplier_taxes_id.ids)] or False,
        }
        return data

    # @api.multi
    def _prepare_to_cancel_reward_invoice_line(self, inv_id, account_id, product, driver_account_analytic_id,
                                               driver_analytic_id, reward_product, reward_amount, supplier_taxes_id):
        reward_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                             company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_reward_for_load_id')
        product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                  company_id=self.env.user.company_id.id).search(
            [('id', '=', reward_product)])
        data = {
            'product_id': int(reward_product),
            'name': product.name,
            'account_id': account_id,
            'price_unit': self.total_reward_amount,
            'quantity': 1.0,
            'account_analytic_id': int(driver_account_analytic_id) or False,
            'analytic_tag_ids': driver_analytic_id and [(6, 0, driver_analytic_id)] or False,
            'invoice_id': inv_id,
            'fleet_id': self.transportation_vehicle.id,
            'branch_id': self.env.user.user_branch_id.id,
            'invoice_line_tax_ids': product.supplier_taxes_id and [(6, 0, product.supplier_taxes_id.ids)] or False
        }
        return data

    # try to open a new wizard on that for invoice
    # @api.multi
    def cancel_tranport_invoice(self):
        view_id = self.env.ref('account.view_account_move_reversal').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Name',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.move.reversal',
            'view_id': view_id,
            'context': {
                'default_wizard_transport_id': self.id,
                'context_for_invoice': True,
                'default_refund_method': 'cancel' if self.invoice_id and self.invoice_id.state == 'open' else 'refund',
            },
            'target': 'new',
        }

    # try to open a new wizard on that for bill
    # @api.multi
    def action_cancel(self):
        view_id = self.env.ref('account.view_account_move_reversal').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Name',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.move.reversal',
            'view_id': view_id,
            'context': {
                'default_wizard_transport_id': self.id,
                'default_refund_method': 'refund'
            },
            'target': 'new',
        }

    # Register Payment for credit Bill
    # @api.multi
    def register_payment_for_return(self):
        view_id = self.env.ref('account.view_account_payment_register_form').id
        if self.reversal_move_id:
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
                    'default_partner_id': self.reversal_move_id.partner_id.id,
                    'default_partner_type': 'supplier',
                    'default_amount': self.reversal_move_id.amount_residual,
                    'default_return_invoice_id': self.reversal_move_id[0].id,
                    'default_communication': self.transportation_no,
                    # 'pass_sale_order_id': self.id,
                    'default_invoice_ids': [(4, self.reversal_move_id[0].id, None)]
                }
            }

    # Register Payment for credit Bill
    # @api.multi
    def register_payment_for_return_invoice(self):
        view_id = self.env.ref('account.view_account_payment_register_form').id
        if self.refund_customer_invoice_ids:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Name',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'account.payment',
                'view_id': view_id,
                'target': 'new',
                'context': {
                    'default_payment_type': 'inbound',
                    'default_partner_id': self.refund_customer_invoice_ids.partner_id.id,
                    'default_partner_type': 'customer',
                    'default_amount': self.refund_customer_invoice_ids.amount_residual,
                    'default_return_invoice_id': self.refund_customer_invoice_ids[0].id,
                    'default_communication': self.transportation_no,
                    # 'pass_sale_order_id': self.id,
                    'default_invoice_ids': [(4, self.refund_customer_invoice_ids[0].id, None)]
                }
            }
    # wrong method
    # @api.multi
    # def action_cancel(self):
    #     if self.payment:
    #         default_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('transport_management.default_fuel_product_id')
    #         default_account = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('transport_management.default_fuel_analytic_account_id')
    #         default_analytic_tag = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('transport_management.default_fuel_analytic_tag_ids')
    #         product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('id','=',default_product)])
    #         default_partner = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('transport_management.default_fuel_supplier_id')
    #         journal_id = self.env['account.journal'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(['|',('sub_type','in',['All']),('sub_type','in',['Payment']),('branches','in',self.env.user.user_branch_id.id),('type','in',['cash'])],limit=1)

    #         default_reward_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('transport_management.default_reward_for_load_id')
    #         default_reward_account = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('transport_management.default_reward_for_analytic_account_id')
    #         default_reward_analytic_tag = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('transport_management.default_reward_for_analytic_tag_ids')
    #         reward_amount = self.total_reward_amount
    #         reward_product = self.env['product.product'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('id','=',default_reward_product)])

    #         inv_obj = self.env['account.move']
    #         inv_line_obj = self.env['account.move.line']
    #         inv_data = self._prepare_to_cancel_invoice(int(default_partner))
    #         invoice = inv_obj.create(inv_data)
    #         fuel_amount = self.total_fuel_amount
    #         account_id = product.property_account_expense_id.id
    #         analytic_id = default_account
    #         analytic_tag_id = [int(default_analytic_tag)]
    #         driver_analytic_id = [int(default_reward_analytic_tag)]
    #         driver_account_analytic_id = default_reward_account
    #         fleet_id = self.transportation_vehicle.id
    #         user = self.env.user
    #         payment_method = self.env.ref('account.account_payment_method_manual_in')
    #         supplier_taxes_id = []
    #         vals = self._prepare_to_cancel_invoice_line(invoice.id,account_id,analytic_id,analytic_tag_id,default_product,fuel_amount,product.supplier_taxes_id,fleet_id)
    #         val = self._prepare_to_cancel_reward_invoice_line(invoice.id,account_id,default_reward_product,driver_account_analytic_id,driver_analytic_id,reward_product,reward_amount,reward_product.supplier_taxes_id)
    #         inv_line_obj.create(vals)
    #         inv_line_obj.create(val)
    #         invoice._compute_amount()
    #         invoice._onchange_cash_rounding()
    #         if invoice.cash_rounding_id.strategy == 'add_invoice_line':
    #                 invoice_line = self.env['account.move.line'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('name','=',invoice.cash_rounding_id.name),('invoice_id','=',invoice.id)],limit=1)
    #                 invoice_line.write({'branch_id':user.user_branch_id.id,
    #                                     'account_analytic_id':default_account,
    #                                     'fleet_id':self.transportation_vehicle.id,
    #                                     'analytic_tag_ids':[(6, 0, default_analytic_tag)] or False,
    #                                     })
    #         invoice.action_post()

    #         self.payment.write({'state':'cancelled'})
    #     return self.write({'state': 'cancel'})


class TransportManagementLine(models.Model):
    _name = 'transport.management.line'
    _inherit = ['mail.thread']
    _description = 'Transport Management Line'

    # 
    @api.depends('price', 'tax_ids', 'product_uom_qty')
    def _get_price(self):
        if self.product_id:
            if self.product_uom_qty:
                self.total_before_taxes = self.product_uom_qty * self.price
            if self.tax_ids:
                currency = self.currency_id or None
                quantity = 1
                product = self.product_id
                taxes = self.tax_ids.compute_all((self.total_before_taxes), currency, quantity,
                                                 product=product)
                self.tax_amount = taxes['total_included'] - taxes['total_excluded']

    # 
    @api.depends('tax_amount', 'product_uom_qty')
    def _get_total_before_taxes(self):
        if self.total_before_taxes:
            self.total_amount = self.total_before_taxes + self.tax_amount

    def get_config_products(self):
        return [('sale_ok', '=', True), ('categ_id', 'in', self.env.user.company_id.product_category_ids.ids)]

    def get_car_size(self):
        return [('id', 'in', self.env.user.company_id.bsg_car_size_ids.ids)]

    transport_management = fields.Many2one('transport.management', string='Transport Management', store=True)
    product_id = fields.Many2one('product.product', string='Product', domain=get_config_products, track_visibility=True)
    description = fields.Text(string='Description', store=True, track_visibility=True)
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    weight = fields.Float(string='Weight', store=True, track_visibility=True)
    length = fields.Float(string='Length', store=True, track_visibility=True)
    width = fields.Float(string='Width', store=True, track_visibility=True)
    height = fields.Float(string='Height', store=True, track_visibility=True)
    total_pieces = fields.Float(string='Total Pieces', store=True, track_visibility=True)
    form = fields.Many2one('bsg_route_waypoints', string="From", store=True, track_visibility=True)
    to = fields.Many2one('bsg_route_waypoints', string="To", store=True, track_visibility=True)
    fleet_type = fields.Many2one('bsg.vehicle.type.table', related='transport_management.fleet_type_transport',
                                 string="Fleet Type", store=True, track_visibility=True)
    product_uom_qty = fields.Float(string='Quantity', required=False, default=1.0, track_visibility=True)
    price = fields.Float(string='Price', default=0.0, track_visibility=True)
    seal_number = fields.Char(string='Seal Number', store=True, track_visibility=True)
    container_number = fields.Char(string='Container No.', store=True, track_visibility=True)
    tax_ids = fields.Many2many('account.tax', string='Taxes', track_visibility=True)
    total_before_taxes = fields.Float(compute='_get_price', string='Total Before Taxes', store=True,
                                      track_visibility=True)
    tax_amount = fields.Float(compute='_get_price', string='Tax Amount', store=True, track_visibility=True)
    total_amount = fields.Float(compute='_get_total_before_taxes', string='Total Amount', store=True,
                                track_visibility=True)
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', related='transport_management.transportation_vehicle',
                                       string="Transportation Vehicle", store=True, track_visibility=True)
    car_size_id = fields.Many2one('bsg_car_size', string='Fleet Size', domain=get_car_size, required=True,
                                  track_visibility=True)
    customer_contract = fields.Many2one(string="Contract No.", comodel_name="bsg_customer_contract",
                                        related='transport_management.customer_contract', store=True,
                                        track_visibility=True)
    partner_types = fields.Many2one("partner.type", related='transport_management.partner_types', store=True,
                                    track_visibility='onchange')

    # @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.tax_ids = rec.product_id.taxes_id and [(6, 0, rec.product_id.taxes_id.ids)] or False
            else:
                rec.tax_ids = False

    @api.onchange('product_id', 'car_size_id', 'form', 'to')
    def onchange_line_get_contract_price(self):
        for rec in self:
            rec.price = 0
            if rec.product_id and rec.form and rec.to and rec.car_size_id:
                if rec.transport_management.customer_contract:
                    ContractLine = self.env['bsg_customer_contract_line'].sudo().with_context(
                        force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([
                        ('cust_contract_id', '=', rec.transport_management.customer_contract.id),
                        ('service_type', '=', rec.product_id.product_tmpl_id.id),
                        ('loc_from', '=', rec.form.id),
                        ('loc_to', '=', rec.to.id),
                        ('car_size', '=', rec.car_size_id.id),
                    ], limit=1)
                    rec.price = ContractLine.price if ContractLine else 0.0
                else:
                    price_id = self.env['bsg_price_line'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                              company_id=self.env.user.company_id.id).search(
                        [
                            ('price_config_id.waypoint_from', '=', rec.form.id),
                            ('price_config_id.waypoint_to', '=', rec.to.id),
                            ('customer_type', '=', rec.transport_management.customer.partner_types.pricing_type),
                            ('service_type', '=', rec.product_id.product_tmpl_id.id),
                            # ('car_classfication', '=', self.car_classfication.id),
                            ('car_size', '=', rec.car_size_id.id),
                        ], limit=1)
                    if price_id:
                        if self.transport_management.agreement_type == 'round_trip':
                            rec.price = price_id.addtional_price
                        else:
                            rec.price = price_id.price

    # @api.model
    # def create(self, vals):
    #     res = super(TransportManagementLine, self).create(vals)
    #     if vals.get('transport_management'):
    #         transport_obj = self.env['transport.management'].browse(int(vals.get('transport_management')))
    #         if transport_obj and transport_obj.form_transport and transport_obj.to_transport:
    #             res.form = transport_obj.form_transport.id
    #             res.to = transport_obj.to_transport.id
    #     return res

    # #for tracking value on change on lie
    # @api.multi
    # def write(self, vals):
    #     old_values = {
    #     'product_id':self.product_id,
    #     'description':self.description,
    #     'weight':self.weight,
    #     'length':self.length,
    #     'width': self.width,
    #     'height': self.height,
    #     'total_pieces': self.total_pieces,
    #     'form' : self.form,
    #     'to' : self.to,
    #     'fleet_type':self.fleet_type,
    #     'product_uom_qty':self.product_uom_qty,
    #     'price' : self.price,
    #     'seal_number':self.seal_number,
    #     'container_number':self.container_number,
    #     'tax_ids':self.tax_ids,
    #     'total_before_taxes': self.total_before_taxes,
    #     'tax_amount':self.tax_amount,
    #     'total_amount':self.total_amount
    #     }
    #     res = super(TransportManagementLine,self).write(vals)
    #     tracked_fields = self.env['transport.management.line'].fields_get(vals)
    #     changes, tracking_value_ids = self._message_track(tracked_fields, old_values)
    #     if changes:
    #         self.transport_management.message_post(tracking_value_ids=tracking_value_ids)
    #     return res


class TransporterInformation(models.Model):
    _name = 'transporter.information'
    _description = 'Transporter Information'

    transport_driver = fields.Char(string='Driver Name', store=True, required=True)
    transport_vehicle = fields.Char(string='Vehicle Number', store=True)
    serial = fields.Char(string='Serial #', store=True)


class SaleStatus(models.Model):
    _name = 'sale.status'
    _description = 'Sale Status Information'

    s_no = fields.Char(string="Serial No.")
    name = fields.Char(string="Sale Status")
