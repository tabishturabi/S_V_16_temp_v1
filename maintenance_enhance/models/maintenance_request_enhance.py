from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class MaintenanceRequestEnh(models.Model):
    _name = 'maintenance.request.enhance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Maintenance Request Enhance"
    _order = "entry_date desc"

    @api.model
    def entry_permission_notification(self):
        ''' This method is called from a cron job. '''
        print("sdasdasd")
        datetime_today = datetime.now()
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        me_notification_config_settings = self.env.ref('maintenance_enhance.me_notification_users_data')

        for rec in self.with_context(
                force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('is_notify_sent','=',False),('state','=','1')], limit=25):
            difference = datetime_today - rec.entry_date
            minutes = difference.total_seconds() / 60
            if minutes >= 30:
                print("asdasdasd")
                for user in me_notification_config_settings.user_ids:
                    log_body = '<li> Vehicle Code : ' + str(
                        rec.vehicle_id.taq_number) + "</li>" + '<li> Driver Mobile : ' + str(
                        rec.driver_mobile) + "</li>" + '<li> Name : ' + str(rec.driver_id.name) + "</li>"
                    self.env['mail.activity'].sudo().create(
                        {
                            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                            'note': log_body,
                            'res_id': rec.id,
                            'res_model_id': self.env.ref('maintenance_enhance.model_maintenance_request_enhance').id,
                            'user_id': user.id
                        })
                    base_url = self.env['ir.config_parameter'].sudo().with_context(
                        force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                        'web.base.url')
                    record_url = '%s/web?debug#id=%d&action=1616&model=maintenance.request.enhance&view_type=form&menu_id=1065' % (
                    base_url, rec.id)
                    body = ('Work Order : <br/> <a href="%s">Click here</a><br> <b/> Thanks.') % (record_url)
                    self.env['mail.mail'].sudo().create({
                        'author_id': odoobot_id,
                        'recipient_ids': me_notification_config_settings.user_ids.mapped('partner_id'),
                        'body_html': log_body + body,
                        'subject': 'Work Order',
                        'auto_delete': True,
                        'email_to': user.email,

                        # 'references': msg_dict.get('message_id'),
                    }).send()
                rec.write({'is_notify_sent':True})

    def _default_get_vehicle(self):
        status_ids = self.env['fleet.vehicle.state'].search([('code', 'in', ['D', 'L', 'UL'])]).ids
        if status_ids:
            fleet_ids = self.env['fleet.vehicle'].search([('state_id', 'in', status_ids)]).ids
            domain = [('id', 'in', fleet_ids)]
        else:
            domain = [('id', '=', -1)]
        return domain

    # mre_ids = fields.Many2many('maintenance.request.enhance', string='WO',domain=lambda self: [('is_check_create_pr', '=', False)])

    name = fields.Char(string='Reference')
    taq_number = fields.Many2one('bsg_fleet_trailer_config', string="Trailer Taq No", track_visibility=True)
    origin = fields.Char(string='Origin', track_visibility=True)
    vehicle_type_name = fields.Many2one('bsg.vehicle.type.table', related='vehicle_id.vehicle_type',
                                        string='Vehicle Type Name', track_visibility=True)
    vehicle_status = fields.Many2one('fleet.vehicle.state', string='Vehicle Status', readonly=False,
                                     related='vehicle_id.state_id', track_visibility=True)
    vehicle_name = fields.Many2one('fleet.vehicle.model', string='Model', related='vehicle_id.model_id',
                                   track_visibility=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Truck Code', track_visibility=True,
                                 domain=_default_get_vehicle)
    entry_permission_id = fields.Many2one('entry_permission', string='Entry Permission', track_visibility=True)
    driver_id = fields.Many2one('hr.employee', string='Vehicle Name', related='vehicle_id.bsg_driver',
                                track_visibility=True)
    driver_code = fields.Char(string='Driver Code', related='vehicle_id.bsg_driver.driver_code', track_visibility=True)
    driver_mobile = fields.Char(related='driver_id.mobile_phone', string='Driver Mobile', track_visibility='onchange')

    plate_no = fields.Char(string='Plate Number', track_visibility=True, related='vehicle_id.license_plate')
    total_cars = fields.Char(string='Total Cars', track_visibility=True)
    current_branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Current Vehicle Branch',
                                        related='vehicle_id.current_branch_id', track_visibility=True)
    current_branch_user_id = fields.Many2one('bsg_branches.bsg_branches', string='Current User Branch',
                                             default=lambda self: self.env.user.user_branch_id.id,
                                             track_visibility=True)
    odometer = fields.Float(string='Last Odometer', track_visibility=True, related='vehicle_id.odometer')
    odometer_unit = fields.Selection([('kilometers', 'Kilometers'), ('miles', 'Miles')], 'Odometer Unit',
                                     track_visibility=True, related='vehicle_id.odometer_unit')
    entry_date = fields.Datetime(string='Entry Date', track_visibility=True, default=lambda self: fields.datetime.now())
    exit_date = fields.Datetime(string='Exit Date', track_visibility=True)
    last_reopen_date = fields.Datetime(string='Last Re-open Date', track_visibility=True)
    last_closed_date = fields.Datetime(string='Last Closed Date', track_visibility=True)
    maintenance_for = fields.Selection(string="Maintenance For",
                                       selection=[('fleet', 'Fleet'), ('trailer', 'Trailer'), ('both', 'Both')],
                                       default='fleet', track_visibility=True)
    wo_child_ids = fields.One2many(string='Work Order Lines', comodel_name='work.order.lines',
                                   inverse_name='wo_line_parent', track_visibility=True)
    em_child_ids = fields.One2many(string='External Maintenance Lines', comodel_name='external.maintenance.lines',
                                   inverse_name='em_line_parent', track_visibility=True)
    pr_count = fields.Integer('PR', compute='_compute_pr_number')
    state = fields.Selection(string="State",
                             selection=[('1', 'Draft'), ('2', 'Maintenance Manager Approval'),
                                        ('3', 'Inspection Technician Approval'), ('4', 'Done'),
                                        ('5', 'Cancelled')],
                             default='1', track_visibility=True)
    date = fields.Datetime(string='Datetime', track_visibility=True, default=lambda self: fields.datetime.now(),
                           readonly=True)
    is_ambulance = fields.Boolean('Is Ambulance')
    is_notify_sent = fields.Boolean('Is Notify Sent')
    is_check_create_pr = fields.Boolean('Is ALL PR Created', compute="_compute_is_check_create_pr",
                                        search='_search_status')
    # is_button_create_pr = fields.Boolean('Button PR Created', compute="_compute_is_check_create_pr")
    # is_check_em_create_pr = fields.Boolean('Is ALL PR Created External Maintenance',
    #                                        compute="_compute_is_check_em_create_pr")
    ep_count = fields.Integer('Entry Permission Count', compute='_compute_ep_number')

    maintenance_for = fields.Selection(string="Maintenance For",
                                       selection=[('fleet', 'Fleet'), ('trailer', 'Trailer'), ('both', 'Both')],
                                       track_visibility=True)
    is_check_wo_lines = fields.Boolean('check status of wo lines', compute='_compute_state_lines')
    bool_group_check = fields.Boolean('Check Has Group', compute='_compute_group_check', copy=False, default=True)
    truck_load = fields.Selection([('full', 'Full'), ('empty', 'Empty'), ], string='Truck Load')

    # @api.multi
    def _search_status(self, operator, value):
        res = []
        recs = self.search([]).filtered(lambda x: x.is_check_create_pr)
        if recs:
            return [('id', 'in', [x.id for x in recs])]
        return res

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
    def _compute_group_check(self):
        for rec in self:
            rec.bool_group_check = False
            if rec.state == '2':
                if self.env.user.has_group('maintenance_enhance.group_wo_mm_approve') or self.env.user._is_admin():
                    rec.bool_group_check = True
            elif rec.state == '3':
                if self.env.user.has_group('maintenance_enhance.group_wo_it_approve') or self.env.user._is_admin():
                    rec.bool_group_check = True
            elif rec.state == '1':
                if self.env.user.has_group('maintenance_enhance.group_confirm_wo') or self.env.user._is_admin():
                    rec.bool_group_check = True

    # @api.multi
    def _compute_state_lines(self):
        for rec in self:
            if len(rec.wo_child_ids) > 0:
                rec.is_check_wo_lines = False
                if any(wo.state in ['waiting_availability'] for wo in rec.wo_child_ids):
                    rec.is_check_wo_lines = True
            else:
                rec.is_check_wo_lines = False

    # @api.multi
    def _compute_ep_number(self):
        for rec in self:
            rec.ep_count = self.env['entry_permission'].search_count([('wo_id', '=', rec.id)])

    # @api.multi
    def action_get_ep_view(self):
        self.ensure_one()
        # res = self.env['ir.actions.act_window'].for_xml_id('maintenance_enhance', 'entry_permission_action')
        res = self.env['ir.actions.act_window']._for_xml_id('maintenance_enhance.entry_permission_action')
        res['domain'] = [('wo_id', 'in', self.ids)]
        return res

    # @api.multi
    def _compute_is_check_create_pr(self):
        for rec in self:
            if len(rec.wo_child_ids.filtered(
                    lambda s: not s.is_pr_create and s.requested_from == 'pr' and s.product_id and s.employee_id)) > 0:
                rec.is_check_create_pr = True
            else:
                rec.is_check_create_pr = False

    @api.depends('em_child_ids')
    def _compute_is_check_em_create_pr(self):
        for rec in self:
            if rec.em_child_ids:
                rec.is_check_em_create_pr = True and all(rec.em_child_ids.mapped('is_pr_create')) or False
            else:
                rec.is_check_em_create_pr = False

    # @api.multi
    def _compute_pr_number(self):
        for rec in self:
            rec.pr_count = self.env['purchase.req'].search_count([('maintenance_request_id', '=', rec.id)])

    # @api.multi
    def action_cancel(self):
        purchase_req = self.env['purchase.req'].search([('maintenance_request_id', '=', self.id)])
        if purchase_req:
            purchase_req.action_cancel()
            for line in self.wo_child_ids:
                line.update({'is_pr_create': False})
        self.write({'state': '5'})

    # @api.multi
    def btn_reject(self):
        if self.state == '2':
            self.write({'state': '1'})
        elif self.state == '3':
            self.write({'state': '2'})

    # @api.multi
    def btn_confirm(self):
        if self.state == '1':
            if not self.entry_permission_id:
                state_id_val = self.env['fleet.vehicle.state'].search([('code', 'in', ['M'])], limit=1).id
                self.write({'vehicle_status': state_id_val})
            self.write({'state': '2', 'name': self.env['ir.sequence'].next_by_code('maintenance.enhance.work.order')})
        elif self.state == '2':
            # if any(wo.state not in ['waiting_availability', 'closed'] for wo in self.wo_child_ids):
            #     raise ValidationError(_("You cannot close wo if any order line is not in state (waiting_avail,closed)"))
            if len(self.mapped('wo_child_ids')) <= 0 and len(self.mapped('em_child_ids')) <= 0:
                raise ValidationError(_("Please add atleast one order line"))
            for w in self.wo_child_ids:
                if not w.is_pr_create and not w.product_id and w.state not in ['waiting_availability', 'closed']:
                    raise ValidationError(_("you can't Confirm WO has line not closed"))
            self.write({'state': '3'})

    # @api.multi
    def action_close_wo(self):
        if any(wo.state not in ['waiting_availability', 'closed'] for wo in self.wo_child_ids):
            raise ValidationError(_("You cannot close wo if any order line is not in state (waiting_avail,closed)"))
        state_id_val = self.env['fleet.vehicle.state'].search([('code', 'in', ['L'])], limit=1).id
        if state_id_val and self.vehicle_id:
            self.vehicle_id.write({'state_id': state_id_val})
        self.write({'state': '4', 'exit_date': fields.datetime.now(), 'last_reopen_date': fields.datetime.now()})

    # @api.multi
    def action_create_pr(self):
        wo_lines = []
        if self.wo_child_ids:
            for rec in self.wo_child_ids:
                fleet_ref = False
                if rec.maintenance_for == 'fleet' and rec.vehicle_id:
                    fleet_ref = str("fleet.vehicle") + "," + str(rec.vehicle_id.id)
                elif rec.maintenance_for == 'trailer' and rec.taq_number:
                    fleet_ref = str("bsg_fleet_trailer_config") + "," + str(rec.taq_number.id)
                else:
                    fleet_ref = str("fleet.vehicle") + "," + str(rec.vehicle_id.id)

                if not rec.is_pr_create and rec.requested_from == 'pr':
                    wo_lines.append({'product_id': rec.product_id.id, 'product_categ': rec.product_id.categ_id.id,
                                     'qty': int(rec.pieces), 'name': rec.notes, 'work_order_id': self.name,
                                     'fleet_id_ref': fleet_ref})
        if wo_lines:
            pr_id = self.env['purchase.req'].create(
                {'entry_date': fields.Date.today(), 'request_type': 'workshop',
                 'maintenance_request_id': self.id, 'preq_line': [(0, 0, x) for x in wo_lines]})
            for pr_line in pr_id.preq_line:
                pr_line._onchange_fleet_id()
            for line in self.wo_child_ids:
                if not line.is_pr_create and line.product_id and line.requested_from == 'pr':
                    line.update({'is_pr_create': True})
            pr_id.submission()
            if pr_id.state != 'approve':
                pr_id.approved()
        else:
            raise ValidationError(_("You can not create PR"))

    # @api.multi
    # def action_mm_approval(self):
    #     if len(self.mapped('wo_child_ids')) <= 0:
    #         raise ValidationError(_("Please add atleast one order line"))
    #     self.write(
    #         {'state': 'mm_approval', 'name': self.env['ir.sequence'].next_by_code('maintenance.enhance.work.order')})
    #     wo_lines = []
    #     if self.wo_child_ids:
    #         for rec in self.wo_child_ids:
    #             if not rec.is_pr_create:
    #                 wo_lines.append({'product_id': rec.product_id.id, 'product_categ': rec.product_id.categ_id.id,
    #                                  'qty': int(rec.pieces), 'name': rec.notes, 'work_order_id': self.name})
    #     if wo_lines:
    #         pr_id = self.env['purchase.req'].create(
    #             {'vehicle_id': self.vehicle_id.id, 'entry_date': fields.Date.today(), 'request_type': 'workshop',
    #              'maintenance_request_id': self.id, 'preq_line': [(0, 0, x) for x in wo_lines]})
    #
    #     for line in self.wo_child_ids:
    #         line.update({'is_pr_create': True})
    #     pr_id.submission()
    #     pr_id.approved()
    #
    # @api.multi
    # def action_em_approval(self):
    #     if len(self.mapped('em_child_ids')) <= 0:
    #         raise ValidationError(_("Please add atleast one order line"))
    #     wo_lines = []
    #     if self.em_child_ids:
    #         for rec in self.em_child_ids:
    #             if not rec.is_pr_create:
    #                 wo_lines.append(
    #                     {'product_id': rec.external_service.id, 'product_categ': rec.external_service.categ_id.id,
    #                      'qty': int(rec.qty), 'name': rec.description, 'work_order_id': self.name})
    #     if wo_lines:
    #         pr_id = self.env['purchase.req'].create(
    #             {'vehicle_id': self.vehicle_id.id, 'entry_date': fields.Date.today(), 'request_type': 'workshop',
    #              'maintenance_request_id': self.id, 'preq_line': [(0, 0, x) for x in wo_lines]})
    #
    #     for line in self.em_child_ids:
    #         line.update({'is_pr_create': True})
    #     pr_id.submission()
    #     pr_id.approved()

    # @api.multi
    # def action_it_approval(self):
    #     self.write({'state': 'it_approval'})

    # @api.multi
    def action_reset(self):
        self.write({'state': '1'})

    # @api.multi
    def action_re_open_wo(self):
        self.write({'state': '2', 'last_reopen_date': fields.datetime.now()})

    @api.model
    def create(self, vals):
        if not vals.get('entry_permission_id'):
            vals['is_ambulance'] = False
        return super(MaintenanceRequestEnh, self).create(vals)

    # @api.multi
    def action_get_pr_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('purchase_enhanced.action_purchase_req')
        res['domain'] = [('maintenance_request_id', 'in', self.ids)]
        return res


class WorkOrderLines(models.Model):
    _name = 'work.order.lines'
    _inherit = ['mail.thread']

    @api.model
    def _get_fleet(self):
        context = self._context or {}
        if context.get('default_fleet', False) and context.get('default_fleet') in ['fleet', 'trailer']:
            return context.get('default_fleet')

    name = fields.Char(string='Name', track_visibility=True, related='wo_line_parent.name')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Truck Code', track_visibility=True,
                                 related='wo_line_parent.vehicle_id')
    taq_number = fields.Many2one('bsg_fleet_trailer_config', string="Trailer Taq No", track_visibility=True,
                                 related='wo_line_parent.taq_number')
    driver_code = fields.Char(related='employee_id.driver_code', string='Technician Code', track_visibility=True,
                              readonly=True)
    entry_permission_id = fields.Many2one('entry_permission', string='Entry Permission', track_visibility=True,
                                          readonly=True, related='wo_line_parent.entry_permission_id')

    wo_line_parent = fields.Many2one('maintenance.request.enhance', string='WO Parent', track_visibility=True)
    workshop_name = fields.Many2one('workshop.name', string='Workshop Name', track_visibility=True)
    workshop_service = fields.Many2one('service.name', string='Workshop Service', track_visibility=True)
    product_id = fields.Many2one('product.product', string="Product")
    pieces = fields.Char(string='Pieces', track_visibility=True)
    employee_id = fields.Many2one('hr.employee', string='Technician Name', track_visibility=True)
    notes = fields.Text(string="Notes", track_visibility=True)
    actual_start_time = fields.Datetime(string="Start Time", track_visibility=True)
    actual_close_time = fields.Datetime(string="Close Time", track_visibility=True)
    is_pr_create = fields.Boolean(string="Is PR Created")
    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('assigned', 'Assigned'),
                                                        ('waiting_availability', 'Waiting Availability'),
                                                        ('in_progress', 'In Progress'), ('closed', 'Closed')],
                             track_visibility=True)
    user_id = fields.Many2one('res.users', related='employee_id.user_id', string='User', track_visibility=True)
    external_workshop = fields.Many2one('res.partner', string='External Workshop', track_visibility=True,
                                        domain=[('is_workshop', '=', True)])
    external_service = fields.Many2one('product.product', string='External Service', track_visibility=True,
                                       domain=[('type', '=', 'service')])
    description = fields.Char(string='Description', track_visibility=True)
    maintenance_for = fields.Selection(string="Maintenance For",
                                       selection=[('fleet', 'Fleet'), ('trailer', 'Trailer')],
                                       default=_get_fleet, track_visibility=True)
    requested_from = fields.Selection(string="Requested From", selection=[('scrap', 'Scrap'), ('pr', 'PR')],
                                      track_visibility=True)

    @api.onchange('workshop_name')
    def _onchange_workshop_name(self):
        if self.workshop_name:
            return {'domain': {'workshop_service': [('workshop', '=', self.workshop_name.id)]}}
        else:
            return {'domain': {'workshop_service': [(1, '=', 1)]}}

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.requested_from = 'pr'
        else:
            self.requested_from = False

    @api.onchange('employee_id')
    def _onchange_technician(self):
        if self.employee_id:
            self.state = 'assigned'
        else:
            self.state = 'draft'

    # @api.multi
    def action_start(self):
        self.write({'state': 'in_progress', 'actual_start_time': fields.datetime.now()})

    # @api.multi
    def action_close(self):
        self.write({'state': 'closed', 'actual_close_time': fields.datetime.now()})

    # @api.multi
    def action_waiting_availability(self):
        if not self.is_pr_create:
            raise ValidationError(_('you cannot move to waiting_availability, please create pr first'))
        self.write({'state': 'waiting_availability'})

    # @api.multi
    def action_reopen(self):
        self.write({'state': 'in_progress', 'actual_close_time': False})

    @api.constrains('pieces')
    def _validate_qty_pieces(self):
        for rec in self:
            if rec.product_id and int(rec.pieces) <= 0:
                raise ValidationError(_("Pieces should more than zero"))

    # @api.multi
    def dup_line(self):
        """
        This is to copy work order line
        """
        if self.wo_line_parent and self.wo_line_parent.state not in ['1', '2']:
            raise ValidationError(_("You can only duplicate if state in draft and MM approval"))

        self.copy(default={
            'workshop_name': self.workshop_name.id,
            'workshop_service': self.workshop_service.id,
        })

    # @api.multi
    def unlink(self):
        for rec in self:
            if rec.is_pr_create:
                raise ValidationError(_('You can not delete a record! with PR created'))
            elif not rec.is_pr_create and rec.state != 'draft':
                raise ValidationError(_('You can not delete a record! with state not draft and not PR created'))
        return super(WorkOrderLines, self).unlink()


class ExternalMaintenanceLines(models.Model):
    _name = 'external.maintenance.lines'

    name = fields.Char(string='Name', track_visibility=True, related='em_line_parent.name')
    em_line_parent = fields.Many2one('maintenance.request.enhance', string='EM Parent', track_visibility=True)
    product_id = fields.Many2one('product.product', string="Product")
    qty = fields.Char(string='Qty', track_visibility=True)
    notes = fields.Text(string="Notes", track_visibility=True)
    actual_start_time = fields.Datetime(string="Start Time", track_visibility=True)
    actual_close_time = fields.Datetime(string="Close Time", track_visibility=True)
    is_pr_create = fields.Boolean(string="Is PR Created")
    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('assigned', 'Assigned'),
                                                        ('in_progress', 'In Progress'), ('closed', 'Closed')],
                             track_visibility=True)
    external_workshop = fields.Many2one('res.partner', string='External Workshop', track_visibility=True,
                                        domain=[('is_workshop', '=', True)])
    external_service = fields.Many2one('product.product', string='External Service', track_visibility=True,
                                       domain=[('type', '=', 'service')])
    description = fields.Char(string='Description', track_visibility=True)

    @api.constrains('qty', 'pieces')
    def _validate_qty_pieces(self):
        for rec in self:
            if int(rec.qty) <= 0:
                raise ValidationError(_("Qty and Pieces should more than zero"))
