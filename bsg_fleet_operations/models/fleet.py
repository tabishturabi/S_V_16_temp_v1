# -*- coding: utf-8 -*-
from datetime import datetime
import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ummalqura.hijri_date import HijriDate
from datetime import date, datetime

_logger = logging.getLogger(__name__)


class bsg_inherit_fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    # oveerride to give track visibility

    odometer = fields.Float(compute='_get_odometer', inverse='_set_odometer', string='Last Odometer',
                            help='Odometer measure of the vehicle at the moment of this log', track_visibility=True)
    odometer_unit = fields.Selection([
        ('kilometers', 'Kilometers'),
        ('miles', 'Miles')
    ], 'Odometer Unit', default='kilometers', help='Unit of the odometer ', required=True, track_visibility=True)
    # location = fields.Many2one('bsg.fleet.asset.location',string="Vehicle Location (Garage)", track_visibility=True)
    vin_sn = fields.Char('Chassis Number', help='Unique number written on the vehicle motor (VIN/SN number)',
                         copy=False, track_visibility=True)
    model_year = fields.Char('Model Year', help='Year of the model', track_visibility=True)
    acquisition_date = fields.Date('Immatriculation Date', required=False,
                                   default=fields.Date.today, help='Date when the vehicle has been immatriculated',
                                   track_visibility=True)
    first_contract_date = fields.Date(string="First Contract Date", default=fields.Date.today, track_visibility=True)
    car_value = fields.Float(string="Catalog Value (VAT Incl.)", help='Value of the bought vehicle',
                             track_visibility=True)
    residual_value = fields.Float(track_visibility=True)

    seats = fields.Integer('Seats Number', help='Number of seats of the vehicle', track_visibility=True)
    doors = fields.Integer('Doors Number', help='Number of doors of the vehicle', default=5, track_visibility=True)
    color = fields.Char(help='Color of the vehicle', track_visibility=True)
    transmission = fields.Selection([('manual', 'Manual'), ('automatic', 'Automatic')], 'Transmission',
                                    help='Transmission Used by the vehicle', track_visibility=True)
    fuel_type = fields.Selection([
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('lpg', 'LPG'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
    ], 'Fuel Type', help='Fuel Used by the vehicle', track_visibility=True)
    co2 = fields.Float('CO2 Emissions', help='CO2 emissions of the vehicle', track_visibility=True)
    horsepower = fields.Integer(track_visibility=True)
    horsepower_tax = fields.Float('Horsepower Taxation', track_visibility=True)
    power = fields.Integer('Power', help='Power in kW of the vehicle', track_visibility=True)

    current_loc_id = fields.Many2one('bsg_route_waypoints', string="Current Location", track_visibility=True)
    fleet_dedicated_area_ids = fields.Many2many('trucks.dedicating.area', string="Fleet Dedicated Area", track_visibility=True)

    bsg_route = fields.Many2one(string="Route", comodel_name="bsg_route", track_visibility=True)
    bsg_driver = fields.Many2one(string="Vehicle Driver", comodel_name="hr.employee", track_visibility=True)
    taq_number = fields.Char(string="Taq Number/Sticker/Asset ID", track_visibility=True)
    assert_status = fields.Selection(string="Asset Status", selection=[
        ('On Road', 'On Road'), ('Parking', 'Parking'), ('Maintains WorkShop', 'Maintains WorkShop')],
                                     track_visibility=True)
    assert_division = fields.Selection(string="Asset Division", selection=[
        ('Car Carrier', 'Car Carrier'), ('Bx', 'Bx'), ('Cargo', 'Cargo'), ('Service', 'Service')],
                                       track_visibility=True)
    last_association = fields.Char(string="Last Associated Equipment Id", track_visibility=True)
    last_association_name = fields.Char(string="Last Associated Equipment Name", track_visibility=True)
    region_id = fields.Many2one('region.config', string="Region Id", track_visibility=True)
    vehicle_group = fields.Char(string="Vehicle Group", track_visibility=True)
    vehicle_group_name = fields.Many2one('bsg.vehicle.group', string="Vehicle Group Name", track_visibility=True)
    trailer_ids = fields.One2many('trailer.associated', 'fleet_id', string="Trailer IDS", track_visibility=True)
    document_ids = fields.One2many('document.info.fleet', 'document_id', track_visibility=True)
    tires_history_id = fields.One2many('tires.history', 'tries_id', track_visibility=True)
    battery_history_ids = fields.One2many('battery.history', 'battery_id', track_visibility=True)
    comment_date = fields.Datetime(string="Comments Date", default=lambda self: fields.datetime.now(),
                                   track_visibility=True)
    short_comment_des = fields.Char(string="Short Comments Des.", track_visibility=True)
    attachment_ids = fields.Many2many('ir.attachment', track_visibility=True)
    comments = fields.Text(string="Comments", track_visibility=True)
    trailer_added = fields.Boolean(string='Trailer Added Check', track_visibility=True)
    trailer_id = fields.Many2one('bsg_fleet_trailer_config', string='Trailer ', track_visibility=True)
    is_driver_linked = fields.Boolean(string='Driver Linkage', help='It checks if driver is linked or not.',
                                      track_visibility=True)
    # For Data Import Necessary Fields added
    vehicle_ar_name = fields.Char(string="Vehicle AR Name", track_visibility=True)
    vehicle_en_name = fields.Char(string="Vehicle En Name", track_visibility=True)
    purchase_veh_date = fields.Date(string='Purchase Date', track_visibility=True)
    veh_regis_type = fields.Selection([
        ('saudi', 'Saudi'),
        ('nonsaudi', 'Non Saudi')
    ], string="Registration Type", track_visibility=True)
    vendor_name = fields.Many2one('res.partner', string='Vendor Name', track_visibility=True)
    driver_code = fields.Char(string="Driver Code", track_visibility=True, related="bsg_driver.driver_code")
    mobile_phone = fields.Char(related="bsg_driver.mobile_phone", string='mobile_phone', track_visibility=True,                               readonly=False)
    vehicle_status = fields.Many2one('bsg.vehicle.status', string='Vehicle Status', track_visibility=True)
    vehicle_type = fields.Many2one('bsg.vehicle.type.table', string='Vehicle Type Name', track_visibility=True)
    region_restrict = fields.Selection([
        ('yes', 'نعم/Yes'),
        ('no', 'لا/No')
    ], string="Region Restrict", track_visibility=True)
    insurance_company_name = fields.Char(string="Insurance company", track_visibility=True)
    current_branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Current Branch', track_visibility=True)
    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip Id')
    route_id = fields.Many2one('bsg_route', string='Route Name')
    expected_end_date = fields.Datetime(string='Scheduled Arrival Date')
    no_of_cars = fields.Char(string='No of Cars')
    time_diff = fields.Char(string='Late Hours')
    daily_trip_count = fields.Integer(string='Daily Trip Count', track_visibility=True)
    trip_count_last_rest = fields.Date('Trip count last reset date')
    estmaira_serial_no = fields.Integer(string='Estmaira Serial No.')
    location_id = fields.Many2one('bsg.fleet.asset.location', string='Location')

    # *-------------Driver Custody ------------------*

    driver_assign_id = fields.Many2one('driver.assign', string='Driver Assignment', store=True, track_visibility=True)
    driver_unassign_id = fields.Many2one('driver.unassign', string='Driver Unassignment', store=True,
                                         track_visibility=True)
    kilometrage = fields.Integer(string='Kilometrage', store=True, track_visibility=True)
    truck_license = fields.Selection([('none', 'None'), ('original', 'Original'), ('copy', 'Copy')],
                                     string='Truck License', store=True, track_visibility=True)
    insurance_card = fields.Selection([('none', 'None'), ('original', 'Original'), ('copy', 'Copy')],
                                      string='Insurance Card', store=True, track_visibility=True)
    weight_card = fields.Selection([('none', 'None'), ('original', 'Original'), ('copy', 'Copy')], string='Weight Card',
                                   store=True, track_visibility=True)
    plate = fields.Integer(string='Plate', default=2, store=True, track_visibility=True)
    oil_card = fields.Boolean(string='Oil Card', store=True, track_visibility=True)
    truck_head = fields.Boolean(string='Truck head Tire Card', store=True, track_visibility=True)
    trailer_tire = fields.Boolean(string='Trailer Tire Card', store=True, track_visibility=True)
    spare_tire_truck = fields.Integer(string='Spare Tire For Truck Head', default=1, store=True, track_visibility=True)
    spare_tire_trailer = fields.Integer(string='Spare Tire For Trailer', default=2, store=True, track_visibility=True)
    jack = fields.Integer(string='Jack', default=1, store=True, track_visibility=True)
    fire_extinguisher = fields.Integer(string='Fire Extinguisher', default=2, store=True, track_visibility=True)
    triangel = fields.Integer(string='Triangle', default=1, store=True, track_visibility=True)
    tire_wrench_tractor = fields.Integer(string='Tire Wrench Tractor', default=1, store=True, track_visibility=True)
    tire_wrench_trailer = fields.Integer(string='Tire Wrench Trailer', default=1, store=True, track_visibility=True)
    tire_unfix_lieber = fields.Integer(string='Tire Unfix Lieber', default=1, store=True, track_visibility=True)
    hands_lifted_trailer = fields.Integer(string='Hands Lifted Trailer Footer', default=1, store=True,
                                          track_visibility=True)
    lift_tool_truck_head = fields.Integer(string='Lift Tool of Truck Head', default=1, store=True,
                                          track_visibility=True)
    unfix_tool_spare_tire = fields.Integer(string='Unfix Tool of Spare Tire', default=1, store=True,
                                           track_visibility=True)
    fixing_tools = fields.Integer(string='Fixing Tools', default=16, store=True, track_visibility=True)
    belt = fields.Integer(string='Belt', default=10, store=True, track_visibility=True)
    lock = fields.Integer(string='Lock', store=True, track_visibility=True)
    chain = fields.Integer(string='Chain', store=True, track_visibility=True)
    ladders = fields.Integer(string='Ladders', default=2, store=True, track_visibility=True)
    air_condition = fields.Selection([('none', 'None'), ('working', 'Working'), ('not_working', 'Not Working')],
                                     string='Air Condition', store=True, track_visibility=True)
    cabin_cleaner = fields.Selection([('clean', 'Clean'), ('good', 'Good'), ('bad', 'Bad')], string='Cabin Cleaner',
                                     store=True, track_visibility=True)
    recoder = fields.Boolean(string='Recorder', store=True, track_visibility=True)
    air_pipe = fields.Integer(string='Air Pipe', store=True, track_visibility=True)
    truck_inspection_card = fields.Selection([('none', 'None'), ('original', 'Original'), ('copy', 'Copy')],
                                             string='Truck Inspection Card', store=True, track_visibility=True)
    fuel_qty = fields.Integer(string='Fuel Quantity', store=True, track_visibility=True)
    shocks_scratches = fields.Char(string='Shocks & scratches', store=True, track_visibility=True)
    battery = fields.Integer(string='Battery', store=True, track_visibility=True)
    other_tools = fields.Text(string='Other Tools', store=True, track_visibility=True)
    driver_comment = fields.Text(string='Driver Comments', store=True, track_visibility=True)

    cooler = fields.Boolean(string='Cooler', store=True, track_visibility=True)
    cover_battery = fields.Boolean(string='Cover of Battery', store=True, track_visibility=True)
    cover_of_diesel_tank = fields.Boolean(string='Cover of Diesel Tank', store=True, track_visibility=True)
    emergency_rotaing_light = fields.Boolean(string='Emergency Rotaing Light', store=True, track_visibility=True)
    curtains = fields.Boolean(string='Curtains', store=True, track_visibility=True)
    bed = fields.Boolean(string='Bed', store=True, track_visibility=True)
    trailer_plate = fields.Boolean(string='Trailer Plate (Sticker)', store=True, track_visibility=True)
    cover = fields.Integer(string='Cover', default=1, store=True, track_visibility=True)
    pliers = fields.Integer(string='Pliers', default=1, store=True, track_visibility=True)
    spanner_musharshar = fields.Integer(string='Spanner(Musharshar)', default=1, store=True, track_visibility=True)
    spanner_baladi = fields.Integer(string='Spanner(Baladi)', default=3, store=True, track_visibility=True)
    hammer = fields.Integer(string='Hammer', default=1, store=True, track_visibility=True)
    spanner = fields.Integer(string='Spanner', default=1, store=True, track_visibility=True)
    screw_drivers = fields.Integer(string='Screw Drivers', default=1, store=True, track_visibility=True)
    sixfold_key = fields.Integer(string='Sixfold Key', store=True, track_visibility=True)
    front_glass = fields.Char(string='Front Glass', store=True, track_visibility=True)
    side_glass = fields.Char(string='Side Glass', store=True, track_visibility=True)
    lights = fields.Char(string='Lights', store=True, track_visibility=True)
    front_light = fields.Char(string='Front Flashing Lights', store=True, track_visibility=True)
    back_light = fields.Char(string='Back Flashing Lights', store=True, track_visibility=True)
    side_flashing_tractor = fields.Char(string='Side Flashing Lights Tractor', store=True, track_visibility=True)
    side_flashing_trailer = fields.Char(string='Side Flashing Lights Trailer', store=True, track_visibility=True)
    big_side_mirror = fields.Char(string='Big Side Mirrors', default=2, store=True, track_visibility=True)
    small_side_mirror = fields.Char(string='Small Side Mirrors', default=2, store=True, track_visibility=True)
    comment = fields.Text(string='Comments', store=True, track_visibility=True)
    rented_vehicle = fields.Boolean("Rented Vehicle")
    driver_receipt_original_istimara = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                        string='Driver Receipt Original ISTIMARA ', readonly=True)
    driver_receipt_original_istimara = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                        string='Driver Receipt Original ISTIMARA ', readonly=True)
    rightLetter = fields.Selection([('ا', 'ا'),('أ', 'أ'), ('ب', 'ب'), ('ح', 'ح'), ('د', 'د'),
                                    ('ر', 'ر'), ('س', 'س'), ('ص', 'ص'), ('ط', 'ط'),
                                    ('ع', 'ع'), ('ق', 'ق'), ('ك', 'ك'), ('ل', 'ل'),
                                    ('م', 'م'), ('ن', 'ن'), ('ه', 'هـ'), ('و', 'و'), ('ى', 'ى')], track_visibility=True,
                                   required=True)
    middleLetter = fields.Selection([('ا', 'ا'),('أ', 'أ'), ('ب', 'ب'), ('ح', 'ح'), ('د', 'د'),
                                     ('ر', 'ر'), ('س', 'س'), ('ص', 'ص'), ('ط', 'ط'),
                                     ('ع', 'ع'), ('ق', 'ق'), ('ك', 'ك'), ('ل', 'ل'),
                                     ('م', 'م'), ('ن', 'ن'), ('ه', 'هـ'), ('و', 'و'), ('ى', 'ى')],
                                    track_visibility=True, required=True)
    leftLetter = fields.Selection([('ا', 'ا'),('أ', 'أ'), ('ب', 'ب'), ('ح', 'ح'), ('د', 'د'),
                                   ('ر', 'ر'), ('س', 'س'), ('ص', 'ص'), ('ط', 'ط'),
                                   ('ع', 'ع'), ('ق', 'ق'), ('ك', 'ك'), ('ل', 'ل'),
                                   ('م', 'م'), ('ن', 'ن'), ('ه', 'هـ'), ('و', 'و'), ('ى', 'ى')], track_visibility=True,
                                  required=True)
    plate_no = fields.Char(string="Plate No", size=4, track_visibility=True,required=True)
    bayan_plate_type_id = fields.Many2one('bayan.plate.type.config', track_visibility=True, string="Bayan Plate Type")
    safety_certificate_received = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                   string='Safety Certificate Received')
    safety_certificate_received_reason = fields.Char(string="Reason", readonly=True)

    # @api.multi
    # @api.onchange('bsg_driver')
    # def set_driver_phone(self):
    # 	for rec  in self:
    # 		if rec.bsg_driver:
    # 			rec.mobile_phone = rec.bsg_driver.mobile_phone

    # commented because no used in any cron job #sachin
    # Cron job for linking driver with vehicle on basis of  vehicle_sticker_no, driver_code and taq_number
    # This is one time running job so no record added in data file
    # @api.model
    # def _cron_link_vehicle_driver(self):
    # 	DriversObj = self.env['hr.employee'].search([('is_driver','=',True)])
    # 	for driver in DriversObj:
    # 		if driver.vehicle_sticker_no and driver.driver_code:
    # 			vehicle = self.env['fleet.vehicle'].search([('taq_number','=',driver.vehicle_sticker_no),('driver_code','=',driver.driver_code)])
    # 			if vehicle:
    # 				vehicle.bsg_driver = driver.id
    # 				vehicle.link_driver()

    # @api.multi
    # def write(self, vals):
    # 	if vals.get('bsg_driver'):
    # 		driver_id = self.env['hr.employee'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(vals.get('bsg_driver'))
    # 		vals['bsg_driver'] = False
    # 	# 	self.update({'bsg_driver' : driver_id})
    # 	res = super(bsg_inherit_fleet_vehicle, self).write(vals)
    # 	return res

    # override to restict user to create record as task id 263

    # TDOD uncomment this on 31/1/2020 @gaga
    # @api.multi
    # def write(self, values):
    # 	if values.get('daily_trip_count', False):
    # 		if self.trip_count_last_rest != fields.date.today():
    # 			self.daily_trip_count = 0
    # 			self.trip_count_last_rest = fields.date.today()
    # 	res = super(bsg_inherit_fleet_vehicle, self).write(values)
    # 	return res

    # 	@api.model
    # 	def _reset_daily_trip_count(self):
    # 		if self.daily_trip_count > 0:
    # 			self.daily_trip_count = 0

    @api.model
    def reset_daily_count(self):
        query = """update fleet_vehicle set daily_trip_count = 0, trip_count_last_rest = '%s'""" % (fields.date.today())
        self.env.cr.execute(query)
        VehicleObj = self.env['fleet.vehicle'].search([])
        for veh in VehicleObj:
            veh.daily_trip_count = 0
            veh.trip_count_last_rest = fields.date.today()

    def reset_daily_trip_count(self):
        query = """update fleet_vehicle set daily_trip_count = 0, trip_count_last_rest = '%s'""" % (fields.date.today())
        self.env.cr.execute(query)
        VehicleObj = self.env['fleet.vehicle'].search([])
        for veh in VehicleObj:
            veh.daily_trip_count = 0
            veh.trip_count_last_rest = fields.date.today()

    # @api.multi
    def create_associated_trailer(self):
        data = {'default_vehicle_id': self.id}
        return {
            'name': 'Add Trailer',
            'type': 'ir.actions.act_window',
            'res_model': 'add.trailer.wizard',
            'view_id': self.env.ref('bsg_fleet_operations.add_trailer_wizard_form').id,
            'view_mode': 'form',
            'view_type': 'form',
            'context': data,
            'target': 'new',
        }
        # if self.trailer_id:
        #     for tr_line in self.trailer_ids:
        #         if not tr_line.expiration_date:
        #             raise UserError(
        #                 _('There is already an active trailer first deactivate that to add new!'), )
        #     # Trailer Associated History On Vehicle Form
        #     self.trailer_ids.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create({
        #         'trailer_name': self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).trailer_id.id,
        #         'effective_date': datetime.now(),
        #         'fleet_id': self.id,
        #     })
        #     # Trailer Associated History On Trailer Form
        #     self.trailer_id.associated_ids.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create({
        #         'vehicle_name': self.id,
        #         'vehicle_division': self.name,
        #         'driver_name': self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_driver.name,
        #         'associated_date': datetime.now(),
        #         'config_id': self.trailer_id.id,
        #     })
        #     self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).trailer_id.state = 'linked'
        #     self.trailer_added = True
        #     vehicle_linked_state = self.state_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('name', 'in', ['Linked', 'linked', 'link']), ('company_id', '=', self.env.user.company_id.id)],
        #                                                        limit=1).id
        #     if vehicle_linked_state:
        #         self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).state_id = vehicle_linked_state
        #     else:
        #         raise UserError(
        #             _('States Not found or you dont have similar states as trailer please create same to proceed!'), )

    # @api.multi
    def link_driver(self):
        _logger.info("link Driver...!")
        if not self.bsg_driver:
            raise UserError(_("please select driver!"))

        linked_vehicles_count = self.search_count(
            [('bsg_driver', '=', self.bsg_driver.id), ('is_driver_linked', '=', True)])
        if linked_vehicles_count > 0:
            vehicle_no = self.bsg_driver.vehicle_sticker_no
            msg = vehicle_no and 'This Driver is Linked with Vehicle no. %s' % (
                vehicle_no) or "driver is already linked to vehicle!"
            raise UserError(_(msg))
        _logger.info("self.bsg_driver...!", self.bsg_driver)
        self.env['fleet.vehicle.assignation.log'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create({
            'bsg_driver_id': self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_driver.id,
            'date_start': fields.datetime.today(),
            'vehicle_id': self.id
        })
        _logger.info("link Driver successfully...!")
        self.is_driver_linked = True
        self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_driver.vehicle_sticker_no = self.taq_number

    # @api.multi
    def unlink_driver(self):
        if self.bsg_driver:
            driver_history = self.env['fleet.vehicle.assignation.log'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([
                ('vehicle_id', '=', self.id),
                ('bsg_driver_id', '=', self.bsg_driver.id),
                ('date_end', '=', False)
            ], limit=1)
            if driver_history:
                driver_history.date_end = fields.date.today()
            self.is_driver_linked = False
            self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_driver.vehicle_sticker_no = False
            self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).bsg_driver = False


class TrailerAssociated(models.Model):
    _name = "trailer.associated"
    _description = "Trailer Associated"

    fleet_id = fields.Many2one('fleet.vehicle', string="Fleet ID")
    trailer_name = fields.Many2one('bsg_fleet_trailer_config', string="Trailer Name")
    effective_date = fields.Datetime(string="Effective Date", default=lambda self: fields.datetime.now())
    expiration_date = fields.Datetime(string="Expireation Date")
    comments = fields.Text(string="Comments")
    safety_certificate_delivered = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                    string='Safety Certificate Delivered', required=True)
    safety_certificate_delivered_reason = fields.Char(string="Reason")

    # @api.multi
    def release_trailer(self):
        data = {'default_trailer_associated_id': self.id}
        return {
            'name': 'Release Trailer',
            'type': 'ir.actions.act_window',
            'res_model': 'release.trailer.wizard',
            'view_id': self.env.ref('bsg_fleet_operations.release_trailer_wizard_form').id,
            'view_mode': 'form',
            'view_type': 'form',
            'context': data,
            'target': 'new',
        }
        # if self.effective_date:
        #     self.expiration_date = datetime.now()
        #     if self.trailer_name:
        #         self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).trailer_name.state = 'unlinked'
        #         self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).fleet_id.trailer_added = False
        #         self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).fleet_id.trailer_id = False
        #         vehicle_linked_state = self.fleet_id.state_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
        #             [('name', 'in', ['UnLinked', 'Un-Linked', 'unlinked', 'unlink']), ('company_id', '=', self.env.user.company_id.id)], limit=1).id
        #         if vehicle_linked_state:
        #             self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).fleet_id.state_id = vehicle_linked_state
        #         else:
        #             raise UserError(_(
        #                 'States Not found or you dont have similar states as trailer please create same to proceed!'), )



class TrailerReleaseWizard(models.TransientModel):
    _name = "release.trailer.wizard"
    _description = "Release Trailer Wizard"

    trailer_associated_id = fields.Many2one('trailer.associated', string="Trailer Associated")
    safety_certificate_delivered = fields.Selection([('yes', 'Yes'),('no', 'No')], string='Safety Certificate Delivered',required=True)
    safety_certificate_delivered_reason = fields.Char(string="Reason")

    # @api.multi
    def release_trailer(self):
        if self.trailer_associated_id.effective_date:
            self.trailer_associated_id.expiration_date = datetime.now()
            self.trailer_associated_id.safety_certificate_delivered = self.safety_certificate_delivered
            self.trailer_associated_id.safety_certificate_delivered_reason = self.safety_certificate_delivered_reason
            if self.trailer_associated_id.trailer_name:
                print('.......trailer name state ...........',self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).trailer_associated_id.trailer_name.state)
                self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).trailer_associated_id.trailer_name.state = 'unlinked'
                print('.......trailer name state ...........',self.sudo().with_context(force_company=self.env.user.company_id.id,company_id=self.env.user.company_id.id).trailer_associated_id.trailer_name.state)
                self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).trailer_associated_id.fleet_id.trailer_added = False
                self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).trailer_associated_id.fleet_id.trailer_id = False
                vehicle_linked_state = self.trailer_associated_id.fleet_id.state_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                    [('name', 'in', ['UnLinked', 'Un-Linked', 'unlinked', 'unlink']), ('company_id', '=', self.env.user.company_id.id)], limit=1).id
                if vehicle_linked_state:
                    self.sudo().with_context(force_company=self.env.user.company_id.id,company_id=self.env.user.company_id.id).trailer_associated_id.fleet_id.state_id = vehicle_linked_state
                else:
                    raise UserError(_(
                        'States Not found or you dont have similar states as trailer please create same to proceed!'), )

class TrailerAddWizard(models.TransientModel):
    _name = "add.trailer.wizard"
    _description = "Add Trailer Wizard"

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    safety_certificate_received = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                   string='Safety Certificate Received', required=True)
    safety_certificate_received_reason = fields.Char(string="Reason")

    # @api.multi
    def add_trailer(self):
        self.vehicle_id.safety_certificate_received = self.safety_certificate_received
        self.vehicle_id.safety_certificate_received_reason = self.safety_certificate_received_reason
        if self.vehicle_id.trailer_id:
            for tr_line in self.vehicle_id.trailer_ids:
                if not tr_line.expiration_date:
                    raise UserError(
                        _('There is already an active trailer first deactivate that to add new!'), )
            # Trailer Associated History On Vehicle Form
            self.vehicle_id.trailer_ids.sudo().with_context(force_company=self.env.user.company_id.id,
                                                 company_id=self.env.user.company_id.id).create({
                'trailer_name': self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                         company_id=self.env.user.company_id.id).vehicle_id.trailer_id.id,
                'effective_date': datetime.now(),
                'fleet_id': self.vehicle_id.id,
            })
            # Trailer Associated History On Trailer Form
            self.vehicle_id.trailer_id.associated_ids.sudo().with_context(force_company=self.env.user.company_id.id,
                                                               company_id=self.env.user.company_id.id).create({
                'vehicle_name': self.vehicle_id.id,
                'vehicle_division': self.vehicle_id.name,
                'driver_name': self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                        company_id=self.env.user.company_id.id).vehicle_id.bsg_driver.name,
                'associated_date': datetime.now(),
                'config_id': self.vehicle_id.trailer_id.id,
            })
            self.sudo().with_context(force_company=self.env.user.company_id.id,
                                     company_id=self.env.user.company_id.id).vehicle_id.trailer_id.state = 'linked'
            self.vehicle_id.trailer_added = True
            vehicle_linked_state = self.vehicle_id.state_id.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                     company_id=self.env.user.company_id.id).search(
                [('name', 'in', ['Linked', 'linked', 'link']), ('company_id', '=', self.env.user.company_id.id)],
                limit=1).id
            if vehicle_linked_state:
                self.sudo().with_context(force_company=self.env.user.company_id.id,
                                         company_id=self.env.user.company_id.id).vehicle_id.state_id = vehicle_linked_state
            else:
                raise UserError(
                    _('States Not found or you dont have similar states as trailer please create same to proceed!'), )


class DocumentInfo(models.Model):
    _name = "document.info.fleet"
    _inherit = ['mail.thread']
    _description = "Document Info Fleet"
    _rec_name = 'document_id'

    document_id = fields.Many2one('fleet.vehicle', string="Sticker No")
    document_type_id = fields.Many2one('documents.type', string="Document Type ID")
    document_name = fields.Char(related='document_type_id.name', string="Document Name")
    issue_date = fields.Date(string='Issue Date', default=date.today())
    document_no = fields.Char(string="Document No")
    expiry_date = fields.Date(string='Expiry Date')
    hijri_date = fields.Char(stinrg="Expire Hijri Date")
    attachment_ids = fields.Many2many('ir.attachment', string='Attachment')

    @api.onchange('expiry_date')
    def get_arabic_dates(self):
        if self.expiry_date:
            self.hijri_date = HijriDate.get_hijri_date(self.expiry_date)


class TiresHistory(models.Model):
    _name = "tires.history"
    _description = "Tires History"

    tries_id = fields.Many2one('fleet.vehicle', string="Fleet ID")
    product_id = fields.Many2one('product.product', string="Product Name")
    tires_serial_no = fields.Char(string="Tire Serial No")
    work_job_no = fields.Char(string="WorkJob No")
    work_job_date = fields.Datetime(string="WorkJob Date", default=lambda self: fields.datetime.now())


class BatteryHistory(models.Model):
    _name = "battery.history"
    _description = "Battery History"

    battery_id = fields.Many2one('fleet.vehicle', string="Fleet ID")
    product_id = fields.Many2one('product.product', string="Product Name")
    bateery_serial_no = fields.Char(string="Battery Serial No")
    battery_expiration_date = fields.Datetime(string="Battery Expire Date")
    work_job_no = fields.Char(string="WorkJob No")
    work_job_date = fields.Datetime(string="WorkJob Date", default=lambda self: fields.datetime.now())
