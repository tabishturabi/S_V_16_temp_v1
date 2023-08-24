# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import UserError


class DriverUnassign(models.Model):
    _name = 'driver.unassign'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'All About Driver Unassignment'
    _rec_name = 'unassignment_no'

    serial_no = fields.Char(string='Serial No.', track_visibility='onchange')
    model_id = fields.Many2one('fleet.vehicle.model', string='Vehicle Name', store=True)
    unassignment_no = fields.Char(string='Unassignment No.', track_visibility='onchange')
    branch = fields.Char(default=lambda self: self.env.user.user_branch_id.branch_no, string='Branch')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, string='User')
    assign_driver_id = fields.Many2one('hr.employee', string='Assignment Driver No/Name')
    assign_driver_code = fields.Char(string="Assignment Driver ID", track_visibility=True,
                                     related="assign_driver_id.driver_code")

    unassign_date = fields.Datetime(string='Unassignment Date', default=fields.Datetime.today, readonly=True,
                                    track_visibility='onchange')
    #     truck_type_name = fields.Char(string='Truck Type Name', track_visibility='onchange')
    unassign_driver_id = fields.Many2one('hr.employee', string='Unassignment Driver No/Name')
    unassign_driver_code = fields.Char(string="Unassignment Driver ID", track_visibility=True,
                                       related="unassign_driver_id.driver_code")

    #     trailer_no = fields.Char(string='Trailer No', track_visibility='onchange')
    #     trailer_name = fields.Char(string='Trailer Name', track_visibility='onchange')
    #     manufacturing_year = fields.Char(string='Manufacturing Year', track_visibility='onchange')
    assign_id = fields.Many2one('assign.driver', string='Assign')
    document_ref = fields.Char(string='Reference/Description')
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Truck", track_visibility='onchange', store=True)
    maintenence_work = fields.Selection(
        [('janadriyah_workshop', 'Janadriyah Workshop'), ('bahra_workshop', 'Bahra Workshop'),
         ('insurance_workshop', 'Insurance Workshop')], string='Maintenance Workshop')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancel'),
    ], default='draft')

    register = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string='Register ON TAMM', required=True)
    register_tamm = fields.Char(string='Register Reference')
    register_date = fields.Datetime(string='Register Date', required=True)

    description = fields.Text(string="Reason", track_visibility=True, translate=True, required=True)

    kilometrage = fields.Integer(string='Kilometrage', store=True)
    truck_license = fields.Selection([('none', 'None'), ('original', 'Original'), ('copy', 'Copy')],
                                     string='Truck License', store=True)
    insurance_card = fields.Selection([('none', 'None'), ('original', 'Original'), ('copy', 'Copy')],
                                      string='Insurance Card', store=True)
    weight_card = fields.Selection([('none', 'None'), ('original', 'Original'), ('copy', 'Copy')], string='Weight Card',
                                   store=True)
    plate = fields.Integer(string='Plate', default=2, store=True)
    oil_card = fields.Boolean(string='Oil Card', store=True)
    truck_head = fields.Boolean(string='Truck head Tire Card', store=True)
    trailer_tire = fields.Boolean(string='Trailer Tire Card', store=True)
    spare_tire_truck = fields.Integer(string='Spare Tire For Truck Head', default=1, store=True)
    spare_tire_trailer = fields.Integer(string='Spare Tire For Trailer', default=2, store=True)
    jack = fields.Integer(string='Jack', default=1, store=True)
    fire_extinguisher = fields.Integer(string='Fire Extinguisher', default=2, store=True)
    triangel = fields.Integer(string='Triangle', default=1, store=True)
    tire_wrench_tractor = fields.Integer(string='Tire Wrench Tractor', default=1, store=True)

    tire_wrench_trailer = fields.Integer(string='Tire Wrench Trailer', default=1, store=True)
    tire_unfix_lieber = fields.Integer(string='Tire Unfix Lieber', default=1, store=True)
    hands_lifted_trailer = fields.Integer(string='Hands Lifted Trailer Footer', default=1, store=True)
    lift_tool_truck_head = fields.Integer(string='Lift Tool of Truck Head', default=1, store=True)
    unfix_tool_spare_tire = fields.Integer(string='Unfix Tool of Spare Tire', default=1, store=True)
    fixing_tools = fields.Integer(string='Fixing Tools', default=16, store=True)
    belt = fields.Integer(string='Belt', default=10, store=True)
    lock = fields.Integer(string='Lock', store=True)
    chain = fields.Integer(string='Chain', store=True)
    ladders = fields.Integer(string='Ladders', default=2, store=True)
    air_condition = fields.Selection([('none', 'None'), ('working', 'Working'), ('not_working', 'Not Working')],
                                     string='Air Condition', store=True)
    cabin_cleaner = fields.Selection([('clean', 'Clean'), ('good', 'Good'), ('bad', 'Bad')], string='Cabin Cleaner')
    air_pipe = fields.Integer(string='Air Pipe', store=True)
    recoder = fields.Boolean(string='Recorder', store=True)
    truck_inspection_card = fields.Selection([('none', 'None'), ('original', 'Original'), ('copy', 'Copy')],
                                             string='Truck Inspection Card', store=True)
    fuel_qty = fields.Integer(string='Fuel Quantity', store=True)
    shocks_scratches = fields.Char(string='Shocks & scratches', store=True)
    battery = fields.Integer(string='Battery', store=True)
    other_tools = fields.Text(string='Other Tools', store=True)
    driver_comment = fields.Text(string='Driver Comments', store=True)

    cooler = fields.Boolean(string='Cooler', store=True)
    cover_battery = fields.Boolean(string='Cover of Battery', store=True)
    cover_of_diesel_tank = fields.Boolean(string='Cover of Diesel Tank', store=True)
    emergency_rotaing_light = fields.Boolean(string='Emergency Rotaing Light', store=True)
    curtains = fields.Boolean(string='Curtains', store=True)
    bed = fields.Boolean(string='Bed', store=True)
    trailer_plate = fields.Boolean(string='Trailer Plate (Sticker)', store=True)
    cover = fields.Integer(string='Cover', default=1, store=True)
    pliers = fields.Integer(string='Pliers', default=1, store=True)
    spanner_musharshar = fields.Integer(string='Spanner(Musharshar)', default=1, store=True)
    spanner_baladi = fields.Integer(string='Spanner(Baladi)', default=3, store=True)
    hammer = fields.Integer(string='Hammer', default=1, store=True)
    spanner = fields.Integer(string='Spanner', default=1, store=True)
    screw_drivers = fields.Integer(string='Screw Drivers', default=1, store=True)
    sixfold_key = fields.Integer(string='Sixfold Key', store=True)
    front_glass = fields.Char(string='Front Glass', store=True)
    side_glass = fields.Char(string='Side Glass', store=True)
    lights = fields.Char(string='Lights', store=True)
    front_light = fields.Char(string='Front Flashing Lights', store=True)
    back_light = fields.Char(string='Back Flashing Lights', store=True)
    side_flashing_tractor = fields.Char(string='Side Flashing Lights Tractor', store=True)
    side_flashing_trailer = fields.Char(string='Side Flashing Lights Trailer', store=True)
    big_side_mirror = fields.Char(string='Big Side Mirrors', default=2, store=True)
    small_side_mirror = fields.Char(string='Small Side Mirrors', default=2, store=True)
    comment = fields.Text(string='Vehicle Comments', store=True)

    # *----------------gernral information -------------*

    vehicle_type_id = fields.Many2one('bsg.vehicle.type.table', string='Vehicle Type Name', store=True)
    chassis_no = fields.Char(string='Chassis Number', store=True)
    truck_status_id = fields.Many2one('bsg.vehicle.status', string='Truck Status')
    manufactr_year = fields.Char(string='Manufacturing Year', store=True)
    plat_no = fields.Char(string='Plate No', store=True)
    comme = fields.Text(string='Comment', store=True)
    location_id = fields.Many2one('bsg_route_waypoints', string='Location')

    previous_trailer_no = fields.Many2one('bsg_fleet_trailer_config', string='Previous Trailer No.')
    trailer_id = fields.Many2one('bsg_fleet_trailer_config', string='New Trailer Linking')
    trailer_type_id = fields.Many2one('bsg.trailer.type', string='Trailer Type Name')
    trailer_asset_status = fields.Many2one('bsg.fleet.asset.status', string='Previous Trailer Status')
    new_trailer_asset_status = fields.Many2one('bsg.fleet.asset.status', string='Trailer Status')
    pre_location_id = fields.Many2one('bsg_route_waypoints', string='Previous Trailer Location')
    new_location_id = fields.Many2one('bsg_route_waypoints', string='Trailer Location')
    trailer_names = fields.Char(string='Trailer Name', store=True)
    comm = fields.Text(string='Comment', store=True)
    x_vehicle_type_id = fields.Many2one('bsg.vehicle.type.table', string='New Vehicle Type')
    driver_receipt_original_istimara = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                        string='Driver Receipt Original ISTIMARA ', required=True)
    reason = fields.Char(string="Reason")

    original_form = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string='Original Form', required=True)
    original_form_reason = fields.Char(string='Original Form Reason')

    original_periodic_check = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string='Original Periodic Check', required=True)
    original_periodic_check_reason = fields.Char(string='Original Periodic Check Reason')

    @api.model
    def create(self, values):
        record = super(DriverUnassign, self).create(values)
        if record.branch:
            record.unassignment_no = 'DU' + record.branch + self.env['ir.sequence'].next_by_code('driver.unassign')
        else:
            record.unassignment_no = 'DU' + self.env['ir.sequence'].next_by_code('driver.unassign')
        if values.get('fleet_vehicle_id'):
            fleet_id = self.env['fleet.vehicle'].search([('id', '=', values.get('fleet_vehicle_id'))])
            fleet_id.write({
                #                 'bsg_driver':values.get('assign_driver_id'),
                'kilometrage': values.get('kilometrage'),
                'truck_license': values.get('truck_license'),
                'insurance_card': values.get('insurance_card'),
                'weight_card': values.get('weight_card'),
                'plate': values.get('plate'),
                'oil_card': values.get('oil_card'),
                'truck_head': values.get('truck_head'),
                'trailer_tire': values.get('trailer_tire'),
                'spare_tire_truck': values.get('spare_tire_truck'),
                'spare_tire_trailer': values.get('spare_tire_trailer'),
                'jack': values.get('jack'),
                'fire_extinguisher': values.get('fire_extinguisher'),
                'triangel': values.get('triangel'),
                'tire_wrench_tractor': values.get('tire_wrench_tractor'),
                'tire_wrench_trailer': values.get('tire_wrench_trailer'),
                'tire_unfix_lieber': values.get('tire_unfix_lieber'),
                'hands_lifted_trailer': values.get('hands_lifted_trailer'),
                'lift_tool_truck_head': values.get('lift_tool_truck_head'),
                'unfix_tool_spare_tire': values.get('unfix_tool_spare_tire'),
                'fixing_tools': values.get('fixing_tools'),
                'belt': values.get('belt'),
                'lock': values.get('lock'),
                'chain': values.get('chain'),
                'ladders': values.get('ladders'),
                'air_condition': values.get('air_condition'),
                'cabin_cleaner': values.get('cabin_cleaner'),
                'air_pipe': values.get('air_pipe'),
                'recoder': values.get('recoder'),
                'cooler': values.get('cooler'),
                'cover_battery': values.get('cover_battery'),
                'cover_of_diesel_tank': values.get('cover_of_diesel_tank'),
                'emergency_rotaing_light': values.get('emergency_rotaing_light'),
                'curtains': values.get('curtains'),
                'bed': values.get('bed'),
                'trailer_plate': values.get('trailer_plate'),
                'cover': values.get('cover'),
                'pliers': values.get('pliers'),
                'spanner_musharshar': values.get('spanner_musharshar'),
                'spanner_baladi': values.get('spanner_baladi'),
                'hammer': values.get('hammer'),
                'spanner': values.get('spanner'),
                'screw_drivers': values.get('screw_drivers'),
                'sixfold_key': values.get('sixfold_key'),
                'front_glass': values.get('front_glass'),
                'side_glass': values.get('side_glass'),
                'lights': values.get('lights'),
                'front_light': values.get('front_light'),
                'back_light': values.get('back_light'),
                'side_flashing_tractor': values.get('side_flashing_tractor'),
                'side_flashing_trailer': values.get('side_flashing_trailer'),
                'big_side_mirror': values.get('big_side_mirror'),
                'small_side_mirror': values.get('small_side_mirror'),
                'comment': values.get('comment'),
                'vehicle_status': values.get('truck_status_id'),
                'current_loc_id':  values.get('location_id'),
                'truck_inspection_card': values.get('truck_inspection_card'),
                'fuel_qty': values.get('fuel_qty'),
                'shocks_scratches': values.get('shocks_scratches'),
                'battery': values.get('battery'),
                'other_tools': values.get('other_tools'),
                'driver_comment': values.get('driver_comment'),
            })

        return record

    # @api.multi
    def write(self, vals):
        res = super(DriverUnassign, self).write(vals)
        if self.fleet_vehicle_id:
            self.fleet_vehicle_id.update({
                'kilometrage': self.kilometrage,
                'truck_license': self.truck_license,
                'insurance_card': self.insurance_card,
                'weight_card': self.weight_card,
                'plate': self.plate,
                'oil_card': self.oil_card,
                'truck_head': self.truck_head,
                'trailer_tire': self.trailer_tire,
                'spare_tire_truck': self.spare_tire_truck,
                'spare_tire_trailer': self.spare_tire_trailer,
                'jack': self.jack,
                'fire_extinguisher': self.fire_extinguisher,
                'triangel': self.triangel,
                'tire_wrench_tractor': self.tire_wrench_tractor,
                'tire_wrench_trailer': self.tire_wrench_trailer,
                'tire_unfix_lieber': self.tire_unfix_lieber,
                'hands_lifted_trailer': self.hands_lifted_trailer,
                'lift_tool_truck_head': self.lift_tool_truck_head,
                'unfix_tool_spare_tire': self.unfix_tool_spare_tire,
                'fixing_tools': self.fixing_tools,
                'belt': self.belt,
                'lock': self.lock,
                'chain': self.chain,
                'ladders': self.ladders,
                'air_condition': self.air_condition,
                'air_pipe': self.air_pipe,
                'recoder': self.recoder,
                'cooler': self.cooler,
                'cover_battery': self.cover_battery,
                'cover_of_diesel_tank': self.cover_of_diesel_tank,
                'emergency_rotaing_light': self.emergency_rotaing_light,
                'curtains': self.curtains,
                'bed': self.bed,
                'trailer_plate': self.trailer_plate,
                'cover': self.cover,
                'pliers': self.pliers,
                'spanner_musharshar': self.spanner_musharshar,
                'spanner_baladi': self.spanner_baladi,
                'hammer': self.hammer,
                'spanner': self.spanner,
                'screw_drivers': self.screw_drivers,
                'sixfold_key': self.sixfold_key,
                'front_glass': self.front_glass,
                'back_light': self.back_light,
                'side_flashing_tractor': self.side_flashing_tractor,
                'side_flashing_trailer': self.side_flashing_trailer,
                'big_side_mirror': self.big_side_mirror,
                'small_side_mirror': self.small_side_mirror,
                'comment': self.comment,

                'truck_inspection_card': self.truck_inspection_card,
                'fuel_qty': self.fuel_qty,
                'shocks_scratches': self.shocks_scratches,
                'battery': self.battery,
                'other_tools': self.other_tools,
                'driver_comment': self.driver_comment,
            })
        return res

    # @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    # @api.multi
    def action_confirm(self, values):
        assign_id = self.env['driver.assign']
        assign = assign_id.create({
            'fleet_vehicle_id': self.fleet_vehicle_id.id,
            #             'assign_driver_id': self.assign_driver_id.id,
            'maintenence_work': self.maintenence_work,
            'document_ref': self.unassignment_no,
            'serial_no': self.serial_no,
            'model_id': self.model_id.id,
            'assign_date': self.unassign_date,
            'unassign_driver_id': self.unassign_driver_id.id,
            'kilometrage': self.kilometrage,
            'truck_license': self.truck_license,
            'insurance_card': self.insurance_card,
            'weight_card': self.weight_card,
            'plate': self.plate,
            'oil_card': self.oil_card,
            'truck_head': self.truck_head,
            'trailer_tire': self.trailer_tire,
            'spare_tire_truck': self.spare_tire_truck,
            'spare_tire_trailer': self.spare_tire_trailer,
            'jack': self.jack,
            'fire_extinguisher': self.fire_extinguisher,
            'triangel': self.triangel,
            'tire_wrench_tractor': self.tire_wrench_tractor,
            'tire_wrench_trailer': self.tire_wrench_trailer,
            'tire_unfix_lieber': self.tire_unfix_lieber,
            'hands_lifted_trailer': self.hands_lifted_trailer,
            'lift_tool_truck_head': self.lift_tool_truck_head,
            'unfix_tool_spare_tire': self.unfix_tool_spare_tire,
            'fixing_tools': self.fixing_tools,
            'belt': self.belt,
            'lock': self.lock,
            'chain': self.chain,
            'ladders': self.ladders,
            'air_condition': self.air_condition,
            'cabin_cleaner': self.cabin_cleaner,
            'air_pipe': self.air_pipe,
            'recoder': self.recoder,
            'cooler': self.cooler,
            'cover_battery': self.cover_battery,
            'cover_of_diesel_tank': self.cover_of_diesel_tank,
            'emergency_rotaing_light': self.emergency_rotaing_light,
            'curtains': self.curtains,
            'bed': self.bed,
            'trailer_plate': self.trailer_plate,
            'cover': self.cover,
            'pliers': self.pliers,
            'spanner_musharshar': self.spanner_musharshar,
            'spanner_baladi': self.spanner_baladi,
            'hammer': self.hammer,
            'spanner': self.spanner,
            'screw_drivers': self.screw_drivers,
            'sixfold_key': self.sixfold_key,
            'front_glass': self.front_glass,
            'side_glass': self.side_glass,
            'lights': self.lights,
            'front_light': self.front_light,
            'back_light': self.back_light,
            'side_flashing_tractor': self.side_flashing_tractor,
            'side_flashing_trailer': self.side_flashing_trailer,
            'big_side_mirror': self.big_side_mirror,
            'small_side_mirror': self.small_side_mirror,
            'comment': self.comment,

            'truck_inspection_card': self.truck_inspection_card,
            'fuel_qty': self.fuel_qty,
            'shocks_scratches': self.shocks_scratches,
            'battery': self.battery,
            'other_tools': self.other_tools,
            'driver_comment': self.driver_comment,

            'vehicle_type_id': self.vehicle_type_id.id,
            'plat_no': self.plat_no,
            'truck_status_id': self.truck_status_id.id,
            'chassis_no': self.chassis_no,
            'manufactr_year': self.manufactr_year,
            'location_id': self.location_id.id,
            'comme': self.comme,

            'trailer_id': self.trailer_id.id,
            'trailer_names': self.trailer_names,
            'trailer_asset_status': self.trailer_asset_status.id,
            'trailer_type_id': self.trailer_type_id.id,
            'new_trailer_asset_status': self.new_trailer_asset_status.id,
            'pre_location_id': self.pre_location_id.id,
            'new_location_id': self.new_location_id.id,
            'previous_trailer_no': self.previous_trailer_no.id,
            'comm': self.comm,
            'state': 'confirm'
        })
        if self.assign_driver_id:
            vehicle_linked_state = self.fleet_vehicle_id.state_id.sudo().search(
                [('name', 'in', ['Linked', 'linked', 'link'])], limit=1).id
            self.sudo().fleet_vehicle_id.state_id = vehicle_linked_state
        else:
            vehicle_unlinked_state = self.fleet_vehicle_id.state_id.sudo().search(
                [('name', 'in', ['UnLinked', 'Un-Linked', 'unlinked', 'unlink'])], limit=1).id
            self.sudo().fleet_vehicle_id.state_id = vehicle_unlinked_state
        if self.assign_driver_id:
            link_unlink_id = 2
        else:
            link_unlink_id = 3

        if self.fleet_vehicle_id:
            fleet_id = self.env['fleet.vehicle'].search([('id', '=', self.fleet_vehicle_id.id)])
            fleet_id.sudo().write({
                'bsg_driver': self.assign_driver_id.id,
                'trailer_id': self.trailer_id.id,
                'vehicle_status': self.truck_status_id.id,
                'current_loc_id': self.new_location_id.id,
                'driver_unassign_id': self.id,
                'state_id': link_unlink_id,
                'vehicle_type':self.x_vehicle_type_id.id,
            })

            trailer_status_id = self.env['bsg_fleet_trailer_config'].sudo().search([('id', '=', self.trailer_id.id)])
            if trailer_status_id:
                trailer_status_id.sudo().write({
                    'trailer_asset_status': self.new_trailer_asset_status.id,
                    'location_id': self.new_location_id.id
                })
            employee_id = self.env['hr.employee'].search([('id', '=', self.assign_driver_id.id)])
            employee_id.sudo().write({
                'vehicle_sticker_no': self.fleet_vehicle_id.taq_number
            })
            emp_id = self.env['hr.employee'].search([('id', '=', self.unassign_driver_id.id)])
            emp_id.sudo().write({
                'vehicle_sticker_no': ''
            })
        if self.assign_driver_id and self.unassign_date and self.unassignment_no:
            self.env['fleet.vehicle.assignation.log'].create(
                {'bsg_driver_id': self.assign_driver_id.id, 'end_start': self.unassign_date.date(),
                 'seq_name': self.unassignment_no, 'vehicle_id': self.fleet_vehicle_id.id})
        return self.sudo().write(
            {'state': 'confirm', 'document_ref': assign.assignment_no, 'assign_id': assign.id})

    # @api.multi
    def action_cancel(self):
        return self.write({'state': 'cancel'})

    # @api.multi
    @api.onchange('fleet_vehicle_id')
    def _get_driver_custody_data(self):
        if self.fleet_vehicle_id:
            self.kilometrage = self.fleet_vehicle_id.kilometrage
            self.truck_license = self.fleet_vehicle_id.truck_license
            self.insurance_card = self.fleet_vehicle_id.insurance_card
            self.weight_card = self.fleet_vehicle_id.weight_card
            self.plate = self.fleet_vehicle_id.plate
            self.oil_card = self.fleet_vehicle_id.oil_card
            self.truck_head = self.fleet_vehicle_id.truck_head
            self.trailer_tire = self.fleet_vehicle_id.trailer_tire
            self.spare_tire_truck = self.fleet_vehicle_id.spare_tire_truck
            self.spare_tire_trailer = self.fleet_vehicle_id.spare_tire_trailer
            self.jack = self.fleet_vehicle_id.jack
            self.fire_extinguisher = self.fleet_vehicle_id.fire_extinguisher
            self.triangel = self.fleet_vehicle_id.triangel
            self.tire_wrench_tractor = self.fleet_vehicle_id.tire_wrench_tractor
            self.tire_wrench_trailer = self.fleet_vehicle_id.tire_wrench_trailer
            self.tire_unfix_lieber = self.fleet_vehicle_id.tire_unfix_lieber
            self.hands_lifted_trailer = self.fleet_vehicle_id.hands_lifted_trailer
            self.lift_tool_truck_head = self.fleet_vehicle_id.lift_tool_truck_head
            self.unfix_tool_spare_tire = self.fleet_vehicle_id.unfix_tool_spare_tire
            self.fixing_tools = self.fleet_vehicle_id.fixing_tools
            self.belt = self.fleet_vehicle_id.belt
            self.lock = self.fleet_vehicle_id.lock
            self.chain = self.fleet_vehicle_id.chain
            self.ladders = self.fleet_vehicle_id.ladders
            self.air_condition = self.fleet_vehicle_id.air_condition
            self.cabin_cleaner = self.fleet_vehicle_id.cabin_cleaner
            self.recoder = self.fleet_vehicle_id.recoder
            self.air_pipe = self.fleet_vehicle_id.air_pipe

            self.cooler = self.fleet_vehicle_id.cooler
            self.cover_battery = self.fleet_vehicle_id.cover_battery
            self.cover_of_diesel_tank = self.fleet_vehicle_id.cover_of_diesel_tank
            self.emergency_rotaing_light = self.fleet_vehicle_id.emergency_rotaing_light
            self.curtains = self.fleet_vehicle_id.curtains
            self.bed = self.fleet_vehicle_id.bed
            self.trailer_plate = self.fleet_vehicle_id.trailer_plate
            self.cover = self.fleet_vehicle_id.cover
            self.pliers = self.fleet_vehicle_id.pliers
            self.spanner_musharshar = self.fleet_vehicle_id.spanner_musharshar
            self.spanner_baladi = self.fleet_vehicle_id.spanner_baladi
            self.hammer = self.fleet_vehicle_id.hammer
            self.spanner = self.fleet_vehicle_id.spanner
            self.screw_drivers = self.fleet_vehicle_id.screw_drivers
            self.sixfold_key = self.fleet_vehicle_id.sixfold_key
            self.front_glass = self.fleet_vehicle_id.front_glass
            self.side_glass = self.fleet_vehicle_id.side_glass
            self.lights = self.fleet_vehicle_id.lights
            self.front_light = self.fleet_vehicle_id.front_light
            self.back_light = self.fleet_vehicle_id.back_light
            self.side_flashing_tractor = self.fleet_vehicle_id.side_flashing_tractor
            self.side_flashing_trailer = self.fleet_vehicle_id.side_flashing_trailer
            self.big_side_mirror = self.fleet_vehicle_id.big_side_mirror
            self.small_side_mirror = self.fleet_vehicle_id.small_side_mirror
            self.comment = self.fleet_vehicle_id.comment

            self.truck_inspection_card = self.fleet_vehicle_id.truck_inspection_card
            self.fuel_qty = self.fleet_vehicle_id.fuel_qty
            self.shocks_scratches = self.fleet_vehicle_id.shocks_scratches
            self.battery = self.fleet_vehicle_id.battery
            self.other_tools = self.fleet_vehicle_id.other_tools
            self.driver_comment = self.fleet_vehicle_id.driver_comment

            self.model_id = self.fleet_vehicle_id.model_id
            #             self.assign_driver_id = self.fleet_vehicle_id.bsg_driver
            self.unassign_driver_id = self.fleet_vehicle_id.bsg_driver

            self.vehicle_type_id = self.fleet_vehicle_id.vehicle_type
            self.plat_no = self.fleet_vehicle_id.license_plate
            self.truck_status_id = self.fleet_vehicle_id.vehicle_status
            self.chassis_no = self.fleet_vehicle_id.vin_sn
            self.manufactr_year = self.fleet_vehicle_id.model_year

            self.previous_trailer_no = self.fleet_vehicle_id.trailer_id
            self.trailer_id = self.fleet_vehicle_id.trailer_id
            self.trailer_asset_status = self.fleet_vehicle_id.trailer_id.trailer_asset_status.id
            self.pre_location_id = self.fleet_vehicle_id.trailer_id.location_id.id
            self.trailer_names = self.fleet_vehicle_id.trailer_id.trailer_ar_name
            self.trailer_type_id = self.fleet_vehicle_id.trailer_id.trailer_type_id

    @api.constrains('assign_driver_id')
    def check_driver(self):
        if self.assign_driver_id and self.unassign_driver_id:
            if self.assign_driver_id.id != self.unassign_driver_id.id:
                record_id = self.env['fleet.vehicle'].search(
                    [('id', '!=', self.fleet_vehicle_id.id), ('bsg_driver', '=', self.assign_driver_id.id)])
                if record_id:
                    raise UserError(_("Vehicle driver already linked with %s...!" % (record_id.taq_number)))
