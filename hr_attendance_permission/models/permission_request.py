# -*- coding: utf-8 -*-
import json
from datetime import datetime, time
from pytz import timezone, UTC
from lxml import etree

# from odoo.osv.orm import setup_modifiers
from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.addons.base.models.res_partner import _tz_get


class PermissionRequest(models.Model):
    _name = 'hr.permission.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    HOUR_SEL = [
        ('0', '12:00 AM'), ('-1', '0:30 AM'),
        ('1', '1:00 AM'), ('-2', '1:30 AM'),
        ('2', '2:00 AM'), ('-3', '2:30 AM'),
        ('3', '3:00 AM'), ('-4', '3:30 AM'),
        ('4', '4:00 AM'), ('-5', '4:30 AM'),
        ('5', '5:00 AM'), ('-6', '5:30 AM'),
        ('6', '6:00 AM'), ('-7', '6:30 AM'),
        ('7', '7:00 AM'), ('-8', '7:30 AM'),
        ('8', '8:00 AM'), ('-9', '8:30 AM'),
        ('9', '9:00 AM'), ('-10', '9:30 AM'),
        ('10', '10:00 AM'), ('-11', '10:30 AM'),
        ('11', '11:00 AM'), ('-12', '11:30 AM'),
        ('12', '12:00 PM'), ('-13', '0:30 PM'),
        ('13', '1:00 PM'), ('-14', '1:30 PM'),
        ('14', '2:00 PM'), ('-15', '2:30 PM'),
        ('15', '3:00 PM'), ('-16', '3:30 PM'),
        ('16', '4:00 PM'), ('-17', '4:30 PM'),
        ('17', '5:00 PM'), ('-18', '5:30 PM'),
        ('18', '6:00 PM'), ('-19', '6:30 PM'),
        ('19', '7:00 PM'), ('-20', '7:30 PM'),
        ('20', '8:00 PM'), ('-21', '8:30 PM'),
        ('21', '9:00 PM'), ('-22', '9:30 PM'),
        ('22', '10:00 PM'), ('-23', '10:30 PM'),
        ('23', '11:00 PM'), ('-24', '11:30 PM')]

    # main info
    permission_type_id = fields.Many2one("hr.permission.type", string="Type", requierd=True )
    description = fields.Char(string="Description")
    name = fields.Char('Description')

    # duration
    duration = fields.Integer("Duration", reaonly=True)
    duration_display = fields.Integer("Duration/Display", compute="compute_duration_display")
    hour_from = fields.Selection(HOUR_SEL, "Hour From", required=True)
    hour_to = fields.Selection(HOUR_SEL, "Hour To", required=True)
    date_from = fields.Datetime("From Date")
    date_to = fields.Datetime("Date To")
    request_date = fields.Date("Request Date", required=True)
    tz = fields.Selection(_tz_get, compute='_compute_tz')
    permission_period = fields.Selection([("signin", "Sign In"), ("singout", "Sign Out")], default="signin", required=True)

    # mode
    permission_type = fields.Selection([
        ('employee', 'By Employee'),
        ('company', 'By Company'),
        ('department', 'By Department'),
        ('category', 'By Employee Tag')],
        string='Allocation Mode', required=True, default='employee',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})

    employee_id = fields.Many2one("hr.employee", string="Employee", requierd=True, default=_default_employee,
                                  track_visibility='onchange')
    category_id = fields.Many2one(
        'hr.employee.category', string='Employee Tag', readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, help='Category of Employee')
    mode_company_id = fields.Many2one(
        'res.company', string='Company', readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    department_id = fields.Many2one(
        'hr.department', string='Department', readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})

    # linked requests
    parent_id = fields.Many2one('hr.permission.request', string='Parent', copy=False)
    linked_request_ids = fields.One2many('hr.permission.request', 'parent_id', string='Linked Requests')

    # notes
    notes = fields.Text('Reasons', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    manager_comment = fields.Text(string='Comment By Manager', track_visibility='always')

    # technical
    can_reset = fields.Boolean('Can reset', compute='_compute_can_reset')
    can_approve = fields.Boolean('Can Approve', compute='_compute_can_approve')
    first_approver_id = fields.Many2one(
        'hr.employee', string='First Approval', readonly=True, copy=False,
        help='This area is automatically filled by the user who validate the request')
    second_approver_id = fields.Many2one(
        'hr.employee', string='Second Approval', readonly=True, copy=False,
        help='This area is automaticly filled by the user who validate the request with second request '
             '(If permission type need second validation)', track_visibility='onchange')
    user_id = fields.Many2one("res.users", string="User", default=lambda self: self.env.user)
    can_change_mode = fields.Boolean('Can reset', compute='_compute_can_change_mode')
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('direct_approve', 'Direct Manager'),
        # ('hr_approve', 'HR Department'),
        ('validate', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help="The status is set to 'To Submit', when a permission request is created." +
             "\nThe status is 'To Approve', when permission request is confirmed by user." +
             "\nThe status is 'Refused', when permission request is refused by manager." +
             "\nThe status is 'Approved', when permission request is approved by manager.")

    @api.depends('duration')
    def compute_duration_display(self):
        for rec in self:
            rec.duration_display = False
            if rec.duration:
                rec.duration_display = rec.duration

    @api.constrains('state', 'duration', 'permission_type_id')
    def _check_request_duration(self):
        for request in self:
            if request.permission_type != 'employee' or not request.employee_id or \
                    request.permission_type_id.allocation_type == 'no' or not request.request_date:
                continue
            request_days = request.permission_type_id.get_days(request.employee_id.id, request.request_date)[request.permission_type_id.id]
            if float_compare(request_days['remaining_requests'], 0, precision_digits=2) == -1 or \
                    float_compare(request_days['virtual_remaining_requests'], 0, precision_digits=2) == -1:
                raise ValidationError(_('The number of remaining permission is not sufficient for this permission type.\n'
                                        'Please also check the permission waiting for validation.'))

    @api.depends('employee_id', 'permission_type', 'department_id.company_id.resource_calendar_id.tz', 'mode_company_id.resource_calendar_id.tz')
    def _compute_tz(self):
        for request in self:
            tz = None
            if request.permission_type == 'employee':
                tz = request.employee_id.tz
            elif request.permission_type == 'department':
                tz = request.department_id.company_id.resource_calendar_id.tz
            elif request.permission_type == 'company':
                tz = request.mode_company_id.resource_calendar_id.tz
            tz = tz or self.env.user.company_id.resource_calendar_id.tz or self.env.user.tz or 'UTC'
            request.tz = tz

    @api.onchange('hour_from', 'hour_to', 'request_date')
    def _onchange_request_parameters(self):
        if not self.hour_from:
            self.date_from = False
            return

        if not self.hour_to:
            self.date_to = False
            return
        if not self.request_date:
            self.date_to = False
            return

        # This hack is related to the definition of the field, basically we convert
        # the negative integer into .5 floats
        hour_from = float_to_time(
            abs(self.hour_from) - 0.5 if self.hour_from < 0 else self.hour_from)
        hour_to = float_to_time(
            abs(self.hour_to) - 0.5 if self.hour_to < 0 else self.hour_to)

        self.date_from = timezone(self.tz).localize(datetime.combine(self.request_date, hour_from)).astimezone(
            UTC).replace(tzinfo=None)
        self.date_to = timezone(self.tz).localize(datetime.combine(self.request_date, hour_to)).astimezone(
            UTC).replace(tzinfo=None)
        self._onchange_request_dates()

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_request_dates(self):
        if self.date_from and self.date_to:
            self.duration = int((self.date_to - self.date_from).total_seconds() / 60 )
        else:
            self.duration = 0

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        # is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        for rec in self:
            pass
            # val_type = rec.permission_type_id.validation_type
            # if state == 'confirm':
            #     continue
            #
            # if state == 'draft':
            #     if rec.employee_id != current_employee and not is_manager:
            #         raise UserError(_('Only a Permissions Manager can reset other people Permissions.'))
            #     continue
            #
            # if not is_officer:
            #     raise UserError(_('Only a Permission Officer or Manager can approve or refuse Permissions requests.'))
            #
            # if is_officer:
            #     # use ir.rule based first access check: department, members, ... (see security.xml)
            #     rec.check_access_rule('write')
            #
            # if rec.employee_id == current_employee and not is_manager:
            #     raise UserError(_('Only a Permissions Manager can approve its own requests.'))
            #
            # if (state == 'validate1' and val_type == 'both') or (state == 'validate' and val_type == 'manager'):
            #     manager = rec.employee_id.parent_id or rec.employee_id.department_id.manager_id
            #     if (manager and manager != current_employee) and not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            #         raise UserError(_('You must be either %s\'s manager or Permissions manager to approve this Permissions') % (rec.employee_id.name))
            #
            # if state == 'validate' and val_type == 'both':
            #     if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            #         raise UserError(_('Only an Permissions Manager can apply the second approval on Permissions requests.'))

    # @api.multi
    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_reset(self):
        for rec in self:
            try:
                rec._check_approval_update('draft')
            except (AccessError, UserError):
                rec.can_reset = False
            else:
                rec.can_reset = True

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(PermissionRequest, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and not self.env.user.has_group('hr_attendance_permission.group_attendance_permission_manager'):
            doc = etree.XML(result['arch'])
            for node in doc.xpath("//field[@name='employee_id']"):
                node.set('readonly', "1")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//field[@name='permission_type']"):
                node.set('readonly', "1")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))
            result['arch'] = etree.tostring(doc, encoding='unicode')
        return result

            # method_nodes = doc.xpath("//field")
        #     for node in method_nodes:
        #         if node.get('name', False) != 'branch_type':
        #             node.set('readonly', "0")
        #             setup_modifiers(node, result['fields'][node.get('name', False)])
        #     result['arch'] = etree.tostring(doc)
        # return result

    # @api.depends("user_id")
    def _compute_can_change_mode(self):
        for rec in self:
            if self.env.user and self.env.user.has_group("hr_attendance_permission.group_attendance_permission_manager"):
                rec.can_change_mode = True
            else:
                rec.can_change_mode = False

    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_approve(self):
        for rec in self:
            try:
                if rec.state == 'confirm' and rec.permission_type_id.validation_type == 'both':
                    rec._check_approval_update('validate1')
                else:
                    rec._check_approval_update('validate')
            except (AccessError, UserError):
                rec.can_approve = False
            else:
                rec.can_approve = True

    # # workflow #
    ##################
    def action_confirm(self):
        for rec in self:
            if rec.state == "draft":
                rec.state = "confirm"

    def action_direct_approve(self):
        for rec in self:
            if rec.state == "confirm":
                rec.state = "direct_approve"

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    # @api.multi
    def action_draft(self):
        if any(request.state not in ['confirm', 'refuse'] for request in self):
            raise UserError(_('Permission request state must be "Refused" or "Confirmed" in order to be reset to draft.'))
        self.write({
            'state': 'draft',
            'first_approver_id': False,
            'second_approver_id': False,
        })
        linked_requests = self.mapped('linked_request_ids')
        if linked_requests:
            linked_requests.action_draft()
            linked_requests.unlink()
        return True

    # @api.multi
    def action_approve(self):
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        if any(request.state != 'direct_approve' for request in self):
            raise UserError(_('request must be confirmed ("To Approve") in order to approve it.'))
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        self.filtered(lambda request: request.permission_type_id.validation_type == 'both').write(
            {'state': 'validate1', 'first_approver_id': current_employee.id})

        self.filtered(lambda request: not request.permission_type_id.validation_type == 'both').action_validate()

        return True

    # @api.multi
    def _prepare_request_values(self, employee):
        self.ensure_one()
        values = {
            'name': self.name,
            'permission_type': 'employee',
            'permission_type_id': self.permission_type_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'hour_from': self.date_from,
            'hour_to': self.date_to,
            'notes': self.notes,
            'parent_id': self.id,
            'employee_id': employee.id
        }
        return values

    def action_validate(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if any(request.state not in ['direct_approve', 'validate1',] for request in self):
            raise UserError(_('request must be confirmed in order to approve it.'))

        self.write({'state': 'validate'})
        self.filtered(lambda request: request.permission_type_id.validation_type == 'both').write({'second_approver_id': current_employee.id})
        self.filtered(lambda request: request.permission_type_id.validation_type != 'both').write({'first_approver_id': current_employee.id})

        for request in self.filtered(lambda request: request.permission_type != 'employee'):
            if request.permission_type == 'category':
                employees = request.category_id.employee_ids
            elif request.permission_type == 'company':
                employees = self.env['hr.employee'].search([('company_id', '=', request.mode_company_id.id)])
            else:
                employees = request.department_id.member_ids
            values = [request._prepare_request_values(employee) for employee in employees]
            requests = self.env['hr.permission.request'].with_context(
                tracking_disable=True,
                mail_activity_automation_skip=True,
            ).create(values)
            requests.action_approve()
            # FIXME RLi: This does not make sense, only the parent should be in validation_type both
            if requests and requests[0].permission_type_id.validation_type == 'both':
                requests.action_validate()

    # @api.multi
    def action_refuse(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if any(request.state not in ['confirm', 'validate', 'validate1'] for request in self):
            raise UserError(_('request must be confirmed or validated in order to refuse it.'))
        print("self", self)

        validated_requests = self.filtered(lambda request: request.state == 'validate1')
        print("============", validated_requests)
        validated_requests.write({'state': 'refuse', 'first_approver_id': current_employee.id})
        (self - validated_requests).write({'state': 'refuse', 'second_approver_id': current_employee.id})
        # If a category that created several requests, cancel all related
        linked_requests = self.mapped('linked_request_ids')
        if linked_requests:
            linked_requests.action_refuse()
        return True

    @api.model
    def create(self, values):
        res = super(PermissionRequest, self).create(values)
        reference = res.name if res.name else ''
        data_dict = {}
        if 'state' in values:
            data_dict['state'] = {'name': 'State', 'new': res.state}
        if data_dict:
            log_body = "<p>Reference/Description : " + reference + "</p>"
            for val in data_dict.keys():
                log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(
                    data_dict[val]['new']) + '</li>'
            self.env['mail.message'].create(
                {'body': log_body, 'model': 'hr.permission.request', 'res_id': res.id, 'subtype_id': '2'})
        return res

    def write(self, values):
        """Override to log changes"""
        old_dict = {
            'state': self.state if self.state else '',
        }
        data_dict = {}
        res = super(PermissionRequest, self).write(values)
        reference = self.name if self.name else ''
        if 'state' in values:
            data_dict['state'] = {'name': 'State', 'old': old_dict['state'], 'new': self.state}
        if data_dict and self:
            log_body = "<p>Reference/Description : " + reference + "</p>"
            for val in data_dict.keys():
                log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                    data_dict[val]['new']) + '</li>'
            self.env['mail.message'].create(
                {'body': log_body, 'model': 'hr.permission.request', 'res_id': self.id, 'subtype_id': '2'})
        return res
