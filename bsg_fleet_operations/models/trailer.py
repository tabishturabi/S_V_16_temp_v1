# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class bsg_fleet_trailer_config(models.Model):
    _name = 'bsg_fleet_trailer_config'
    _description = "Trailer Configuration"
    _inherit = ['mail.thread']
    _rec_name = "trailer_config_name"

    # Trailer Screen
    trailer_config_name = fields.Char(string="Name", track_visibility=True)
    active = fields.Boolean(string="Active", track_visibility=True, default=True)
    trailer_taq_no = fields.Char(string="Trailer Taq No", track_visibility=True)
    trailer_ar_name = fields.Char(string="Trailer Ar Name", track_visibility=True)
    trailer_er_name = fields.Char(string="Trailer Er Name", track_visibility=True)
    last_drive = fields.Many2one(string="Last Associated Driver", comodel_name="hr.employee", track_visibility=True)
    last_vehicle = fields.Many2one('fleet.vehicle', string="Last Associated vehicle", track_visibility=True)
    state = fields.Selection(string="State", selection=[
        ('draft', 'Draft'), ('linked', 'Linked'), ('unlinked', 'Un-Linked'), ('maintenance', 'Maintenance'), ('sold', 'Sold')],
                             default='draft', track_visibility=True)
    trailer_asset_status = fields.Many2one('bsg.fleet.asset.status', string="Asset Status", track_visibility=True)
    trailer_asset_group = fields.Many2one('bsg.fleet.asset.group', string="Asset Group", track_visibility=True)
    domain_name = fields.Selection(string="Domain Name", selection=[
        ('Carrier', 'Carrier'), ('Bx', 'Bx'), ('Cargo', 'Cargo'), ('Service', 'Service')], track_visibility=True)
    trailer_capacity = fields.Float(string="Capacity", default=8, track_visibility=True)
    trailer_last_date = fields.Datetime(
        string='Last Associated Date', track_visibility=True
    )
    virtual_trail = fields.Boolean(string="Virtual Trail", track_visibility=True, default=False)

    # general infomration
    trailer_categories_id = fields.Many2one('bsg.trailer.categories', string="Trailer Categories",
                                            track_visibility=True, required=True)
    trailer_type_id = fields.Many2one('bsg.trailer.type', string="Trailer Type Name", track_visibility=True)
    vendor_no = fields.Char(string="Vendor No", track_visibility=True)
    vendor_id = fields.Many2one('res.partner', string="Vendor Name", domain=[('supplier_rank','>',0)],
                                track_visibility=True)
    owener_name = fields.Char(string="Owner Name", track_visibility=True)
    chassis_number = fields.Char(string="Chassis Number", track_visibility=True)
    manufacturing_year = fields.Char(string="Manufacturing Year", track_visibility=True)
    maker = fields.Char(string="Maker", track_visibility=True)
    purchase_date = fields.Datetime(string="Purchase Date", default=lambda self: fields.datetime.now(),
                                    track_visibility=True)
    color = fields.Char(sting="Color", track_visibility=True)
    branch_no = fields.Many2one('bsg_branches.bsg_branches', string="Branch No", track_visibility=True)
    location_id = fields.Many2one('bsg_route_waypoints', string='Location')

    # One2Many Fields
    associated_ids = fields.One2many('associate_history', 'config_id')
    maintance_history_ids = fields.One2many('maintance_history', 'config_id')
    tries_ids = fields.One2many('tires.history.config', 'tries_id')
    trailer_comment_ids = fields.One2many('trailer.comments.config', 'triler_config_id')

    trailer_services_count = fields.Integer(string="Odometer Count", compute="_compute_service_logs",
                                            track_visibility=True)

    # @api.multi
    def _compute_trips_number(self):
        for rec in self:
            rec.trips_number = self.env['fleet.vehicle.trip'].search_count([('trailer_id', 'in', self.ids)])

    # @api.multi
    def action_get_trips_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_trip_mgmt.action_fleet_vehicle_trip_all')
        res['domain'] = [('trailer_id', 'in', self.ids)]
        return res

    trips_number = fields.Integer('Number of Trips', compute='_compute_trips_number')

    # @api.multi
    def _compute_assign_number(self):
        for trailer in self:
            trailer.driver_assign_count = self.env['driver.assign'].search_count([('trailer_id', '=', trailer.id)])

    # @api.multi
    def action_get_assigned_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_fleet_operations.bsg_driver_assign_action')
        res['domain'] = [('trailer_id', 'in', self.ids)]
        return res

    driver_assign_count = fields.Integer('Number of Driver Assign', compute='_compute_assign_number')

    # @api.multi
    def _compute_unassigned_number(self):
        for trailer in self:
            trailer.driver_unassigned_count = self.env['driver.unassign'].search_count(
                [('trailer_id', '=', trailer.id)])

    # @api.multi
    def action_get_unassigned_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_fleet_operations.bsg_driver_unassign_action')
        res['domain'] = [('trailer_id', 'in', self.ids)]
        return res

    driver_unassigned_count = fields.Integer('Number of Driver Assign', compute='_compute_unassigned_number')

    # @api.multi
    def _compute_bx_trip(self):
        for rec in self:
            rec.bx_trip_count = self.env['transport.management'].search_count(
                [('trailer_id', '=', rec.id)])

    # @api.multi
    def action_get_bx_trip(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('transport_management.transport_management_action')
        res['domain'] = [('trailer_id', 'in', self.ids)]
        return res

    bx_trip_count = fields.Integer('Number of Bx Trips', compute='_compute_bx_trip')


    # Cron job for updating capacity to 8 this is one time job so no need to add this in data file
    @api.model
    def _cron_update_trailer_capacity(self):
        TrailersObj = self.env['bsg_fleet_trailer_config'].search([])
        for trailer in TrailersObj:
            trailer.trailer_capacity = 8

    # override to restict user to create record as task id 263
    @api.model
    def create(self, values):
        if not self.env.user.has_group('bsg_fleet_operations.group_can_create_vehicles_and_triler'):
            raise UserError(_('You have not access to create new record, Please contact Admin...!'))
        record = super(bsg_fleet_trailer_config, self).create(values)
        return record

    # 
    def _compute_service_logs(self):
        ServicesLog = self.env['trailer.service.log']
        self.trailer_services_count = ServicesLog.search_count([('trailer_id', '=', self.id)])

    # @api.multi
    def draft_btn(self):
        return self.write({'state': 'draft'})

    # @api.multi
    def linked_btn(self):
        return self.write({'state': 'linked'})

    # @api.multi
    def unlinked_btn(self):
        return self.write({'state': 'unlinked'})

    # @api.multi
    def maintenance_btn(self):
        return self.write({'state': 'maintenance'})

    # @api.multi
    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window'].for_xml_id('bsg_fleet_operations', xml_id)
            res.update(
                context=dict(self.env.context, default_trailer_id=self.id, group_by=False),
                domain=[('trailer_id', '=', self.id)]
            )
            return res
        return False

    # @api.multi
    def trailer_config_get_form_view(self):
        trailer_action = self.env.ref('bsg_fleet_operations.bsg_fleet_trailer_config_action')
        action = trailer_action.read()[0]
        action['views'] = [(self.env.ref('bsg_fleet_operations.view_bsg_fleet_trailer_config_form').id, 'form')]
        action['view_mode'] = 'form'
        action['res_id'] = self.id
        return action


class AssociatedHistory(models.Model):
    _name = "associate_history"
    _description = "Associated History"

    config_id = fields.Many2one('bsg_fleet_trailer_config')
    vehicle_name = fields.Many2one('fleet.vehicle', string="Vehicle Name")
    vehicle_division = fields.Char(string="Vehicle Division")
    driver_name = fields.Char(string="Driver Name")
    associated_date = fields.Datetime(string="Associated Date", default=lambda self: fields.datetime.now())


class ManintanceHistory(models.Model):
    _name = "maintance_history"
    _description = "Manintance History"

    config_id = fields.Many2one('bsg_fleet_trailer_config')
    workhob = fields.Char(string="WorkJob")
    work_job_date = fields.Datetime(string="WorkJob Date", default=lambda self: fields.datetime.now())
    work_close_date = fields.Datetime(string="WorkJob Close Date")


class TiresHistory(models.Model):
    _name = "tires.history.config"
    _description = "Tires History Config"

    tries_id = fields.Many2one('bsg_fleet_trailer_config', string="Fleet ID")
    product_id = fields.Many2one('product.product', string="Product Name")
    tires_serial_no = fields.Char(string="Tire Serial No")
    tires_expiry = fields.Datetime(string="Tire Expiry Date")
    work_job_no = fields.Char(string="WorkJob No")
    work_job_date = fields.Datetime(string="WorkJob Date", default=lambda self: fields.datetime.now())
