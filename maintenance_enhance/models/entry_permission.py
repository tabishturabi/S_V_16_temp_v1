from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EntryPermission(models.Model):
    _name = 'entry_permission'
    _inherit = ['mail.thread']
    _description = "Entry Permission"
    _rec_name = "vehicle_name"
    _order = "date desc"

    def _default_get_vehicle(self):
        status_ids = self.env['fleet.vehicle.state'].search([('code', 'in', ['D', 'L', 'UL'])]).ids
        if status_ids:
            fleet_ids = self.env['fleet.vehicle'].search([('state_id', 'in', status_ids)]).ids
            domain = [('id', 'in', fleet_ids)]
        else:
            domain = [('id', '=', -1)]
        return domain

    vehicle_name = fields.Many2one('fleet.vehicle.model', string='Model', readonly=False, track_visibility=True)
    vehicle_code = fields.Many2one('fleet.vehicle', string='Truck Code', readonly=False, track_visibility=True,
                                   domain=_default_get_vehicle)
    vehicle_status = fields.Many2one('fleet.vehicle.state', string='Vehicle Status', readonly=False,
                                     related='vehicle_code.state_id', track_visibility=True)
    driver_id = fields.Many2one('hr.employee', string='Driver Name', track_visibility=True)
    driver_code = fields.Char(string='Driver Code', readonly=False, track_visibility=True)
    driver_mobile = fields.Char(related='driver_id.mobile_phone', string='Driver Mobile', track_visibility='onchange')
    plate_no = fields.Char(string='Plate Number', readonly=False, track_visibility=True)
    kilometer = fields.Char(string='Last Odometer', readonly=False, track_visibility=True, copy=False,
                            compute="_compute_kilometer", store=True)
    name = fields.Char(string='Name', readonly=True, track_visibility=True)
    date = fields.Datetime(string='Datetime', track_visibility=True, default=lambda self: fields.datetime.now(),
                           readonly=True, copy=False)
    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')],
                             default='draft', track_visibility=True)
    department_service = fields.Selection(string="Department Service",
                                          selection=[('maintenance', 'Maintenance'),
                                                     ('technical_support', 'Technical Support'),
                                                     ('operation', 'Operation')],
                                          default='maintenance', track_visibility=True)
    description = fields.Text(string="Description", track_visibility=True)
    taq_number = fields.Many2one('bsg_fleet_trailer_config', string="Trailer Taq No", track_visibility=True)
    maintenance_for = fields.Selection(string="Maintenance For",
                                       selection=[('fleet', 'Fleet'), ('trailer', 'Trailer'), ('both', 'Both')],
                                       default='fleet', track_visibility=True)
    upload_inspection = fields.Binary(string="Upload Inspection")
    vehicle_id = fields.Many2one('fleet.vehicle', string='Truck Code', track_visibility=True)
    inspection_config_trailer = fields.Many2many('inspection.config', string='Trailer Inspection',
                                                 domain=[('type', '=', 'trailer')])
    inspection_config_truck = fields.Many2many('inspection.config','entry_permission_id','inspection_config_truck_id', string='Truck Inspection',
                                               domain=[('type', '=', 'truck')])
    wo_id = fields.Many2one('maintenance.request.enhance', string='Work Order', track_visibility=True)
    wo_count = fields.Integer('WO Count', compute='_compute_wo_number')
    truck_load = fields.Selection([('full', 'Full'), ('empty', 'Empty'), ], string='Truck Load', required=True)
    odometer_not_work = fields.Boolean("Odometer disabled")
    current_branch_user_id = fields.Many2one('bsg_branches.bsg_branches', string='Current User Branch',
                                             default=lambda self: self.env.user.user_branch_id.id,
                                             track_visibility=True)

    # @api.multi
    def _compute_wo_number(self):
        for rec in self:
            rec.wo_count = self.env['maintenance.request.enhance'].search_count([('entry_permission_id', '=', rec.id)])

    # @api.multi
    def action_get_wo_view(self):
        self.ensure_one()
        # res = self.env['ir.actions.act_window'].for_xml_id('maintenance_enhance', 'maintenance_req_enh_action')
        res = self.env['ir.actions.act_window']._for_xml_id('maintenance_enhance.maintenance_req_enh_action')
        res['domain'] = [('entry_permission_id', 'in', self.ids)]
        return res

    @api.model
    def create(self, vals):
        res = super(EntryPermission, self).create(vals)
        if res.vehicle_code:
            state_id_val = self.env['fleet.vehicle.state'].search([('code', 'in', ['MC'])], limit=1).id
            if state_id_val:
                res.vehicle_code.write({'state_id': state_id_val})
            else:
                raise ValidationError(_('Please do add a reference on Vehicle Status with label MC(Maintenance Check)'))
        return res

    @api.depends('vehicle_code')
    def _compute_kilometer(self):
        for rec in self:
            rec.kilometer = False
            if rec.vehicle_code:
                rec.kilometer = rec.vehicle_code.odometer

    # @api.multi
    @api.onchange('vehicle_code')
    def get_vehicle_code_data(self):
        if self.vehicle_code:
            self.driver_id = self.vehicle_code.bsg_driver
            self.vehicle_name = self.vehicle_code.model_id
            self.plate_no = self.vehicle_code.license_plate
            self.kilometer = self.vehicle_code.odometer
            self.driver_code = self.vehicle_code.bsg_driver.driver_code
            self.taq_number = self.vehicle_code.trailer_id.id

    @api.constrains('vehicle_id', 'taq_number')
    def _validate_vehicle_id(self):
        wo_lines = self.env['work.order.lines']
        domain = []
        if self.vehicle_id:
            domain += [('vehicle_id', '=', self.vehicle_id.id)]
        if self.taq_number:
            domain += [('taq_number', '=', self.taq_number.id)]
        wo_lines.search(domain)
        for rec in wo_lines:
            if rec.state not in ['closed', 'waiting_availability']:
                raise ValidationError(_("Cannot duplicate WO of an in-progress Truck/Trailer"))

    # @api.multi
    def action_cancel(self):
        state_id_val = self.env['fleet.vehicle.state'].search([('code', 'in', ['L'])], limit=1).id
        wo_lines_obj = self.env['work.order.lines'].search(
            [('entry_permission_id', 'in', self.ids), ('state', 'not in', ['draft', 'assigned'])])
        if len(wo_lines_obj) > 0:
            raise ValidationError(_('Please make sure work order against this record is in draft'))
        else:
            wo_obj = self.env['maintenance.request.enhance'].search([('entry_permission_id', 'in', self.ids)], limit=1)
            wo_obj.action_cancel()
        self.write({'state': 'cancel', 'vehicle_status': state_id_val})

    # @api.multi
    def action_confirm(self):
        # if not self.upload_inspection:
        #     raise ValidationError(_('Please do upload the inspections'))
        sequence = self.env['ir.sequence'].next_by_code('maintenance.enhance.entry.permission.seq') or _('New')
        wo_id = self.env['maintenance.request.enhance'].create(
            {'maintenance_for': self.maintenance_for, 'truck_load': self.truck_load, 'taq_number': self.taq_number.id,
             'origin': sequence, 'entry_permission_id': self.id, 'vehicle_id': self.vehicle_code.id,
             'entry_date': fields.datetime.now()})
        state_id_val = self.env['fleet.vehicle.state'].search([('code', 'in', ['M'])], limit=1).id
        if state_id_val:
            self.vehicle_code.write({'state_id': state_id_val})
        else:
            raise ValidationError(_('Please do add a reference on Vehicle Status with label M(Maintenance)'))
        self.write({'state': 'done', 'wo_id': wo_id.id, 'name': sequence})

    # @api.multi
    def action_reset(self):
        self.write({'state': 'draft'})

    # @api.model
    # def create(self, vals):
    #     vals['name'] =
    #     return super(EntryPermission, self).create(vals)
