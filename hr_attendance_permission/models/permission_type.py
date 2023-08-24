# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, time
from dateutil.relativedelta import relativedelta

from odoo import models, fields, _, api
from odoo.tools.float_utils import float_round


class PermissionType(models.Model):
    _name = 'hr.permission.type'


    # Migration Note
    # DAY_SEL = [(i, str(i)) for i in range(1, 31)]
    DAY_SEL = [(str(i), str(i)) for i in range(1, 31)]

    # @api.multi
    def name_get(self):
        if not self._context.get('employee_id'):
            # requests counts is based on employee_id, would be inaccurate if not based on correct employee
            return super(PermissionType, self).name_get()
        res = []
        for record in self:
            name = record.name
            if record.allocation_type != 'no':
                name = "%(name)s (%(count)s)" % {
                    'name': name,
                    'count': _('%g remaining out of %g') % (
                        float_round(record.virtual_remaining_requests, precision_digits=2) or 0.0,
                        float_round(record.max_requests, precision_digits=2) or 0.0,
                    ) + _(" Minutes")
                }
            res.append((record.id, name))
        return res

    name = fields.Char("Name", required=True)
    balance = fields.Float(string="Balance")

    validation_type = fields.Selection([
        ('hr', 'Human Resource officer'),
        ('manager', 'Employee Manager'),
        ('both', 'Double Validation')], default='hr', string='Validation By')

    double_validation = fields.Boolean(string='Apply Double Validation',
                                       compute='_compute_validation_type', inverse='_inverse_validation_type',
                                       help="When selected, the permission Requests for this type require a "
                                            "second validation to be approved.")
    unpaid = fields.Boolean("Unpaid?")
    day_from = fields.Selection(DAY_SEL, string="Day From", required=True)
    day_to = fields.Selection(DAY_SEL, string="Day To", required=True)
    date_from = fields.Date("Date From")
    date_to = fields.Date("Date To")
    on_signin = fields.Boolean("Activate on Sign In")
    on_signout = fields.Boolean("Activate on Sign Out")
    validity_start = fields.Date("Valid From", required=True)
    validity_stop = fields.Date("Valid To", required=True)
    allocation_type = fields.Selection([
        ('fixed', 'Fixed by HR'),
        ('fixed_allocation', 'Fixed by HR + allocation request'),
        ('no', 'No allocation')],
        default='fixed', string='Mode')
    virtual_remaining_requests = fields.Float(
        compute='_compute_requests', string='Virtual Remaining Balance',
        help='Maximum Requests Allowed - Requests Already Taken - Requests Waiting Approval')
    max_requests = fields.Float(compute='_compute_requests', string='Maximum Allowed')

    active = fields.Boolean(string="Active", track_visibility=True, default=True)

    accrual = fields.Boolean("Accrual", default=True, )
    interval_number = fields.Integer("Number of Days for Accrual", default=30)
    accrual_created = fields.Boolean("Accrual", readonly=True)
    origin_type_id = fields.Many2one("hr.permission.type", readonly=True)
    # nextcall = fields.Date("Date of the next accrual allocation", default=False, readonly=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('The Name must be unique !')),
    ]

    # @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = _("%s (copy)") % (self.name or '')
        return super(PermissionType, self).copy(default)

    def _inverse_validation_type(self):
        for request_type in self:
            if request_type.double_validation == True:
                request_type.validation_type = 'both'
            else:
                # IF to preserve the information (hr or manager)
                if request_type.validation_type == 'both':
                    request_type.validation_type = 'hr'

    @api.depends('validation_type')
    def _compute_validation_type(self):
        for request_type in self:
            if request_type.validation_type == 'both':
                request_type.double_validation = True
            else:
                request_type.double_validation = False

    def _get_contextual_employee_id(self):
        if 'employee_id' in self._context:
            employee_id = self._context['employee_id']
        elif 'default_employee_id' in self._context:
            employee_id = self._context['default_employee_id']
        else:
            employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1).id
        return employee_id

    def _get_contextual_date(self):
        if 'date' in self._context:
            date = self._context['date']
        elif 'default_date' in self._context:
            date = self._context['default_date']
        print("===================", date)
        return date

    # @api.multi
    def get_days(self, employee_id, date=None):
        # need to use `dict` constructor to create a dict per id
        result = dict((id, dict(max_requests=0, requests_taken=0, remaining_requests=0, virtual_remaining_requests=0)) for id in self.ids)

        requests = self.env['hr.permission.request'].search([
            ('employee_id', '=', employee_id),
            # ('state', 'in', ['draft', 'confirm', 'validate1', 'validate']),
            ('permission_type_id', 'in', self.ids)
        ])
        today = date or fields.Date.today()
        allocations = self.env['hr.permission.type'].search([('id', 'in', self.ids), ("validity_start", "<=", today),
                                                             ("validity_stop", ">=", today)])
        for request in requests:
            status_dict = result[request.permission_type_id.id]
            status_dict['virtual_remaining_requests'] -= (request.duration)
            # if request.state == 'validate':
            status_dict['requests_taken'] += (request.duration)
            status_dict['remaining_requests'] -= (request.duration)
        for allocation in allocations.sudo():
            status_dict = result[allocation.id]
            status_dict['virtual_remaining_requests'] += (allocation.balance)
            status_dict['max_requests'] += (allocation.balance)
            status_dict['remaining_requests'] += (allocation.balance)
        return result

    # @api.multi
    def _compute_requests(self):
        data_days = {}
        employee_id = self._get_contextual_employee_id()
        date = self._get_contextual_date()

        if employee_id and date:
            data_days = self.get_days(employee_id, date)

        for permission_type in self:
            result = data_days.get(permission_type.id, {})
            permission_type.max_requests = result.get('max_requests', 0)
            permission_type.requests_taken = result.get('requests_taken', 0)
            permission_type.remaining_requests = result.get('requests_requests', 0)
            permission_type.virtual_remaining_requests = result.get('virtual_remaining_requests', 0)

    @api.model
    def _update_permission_accrual(self):
        """
            Method called by the cron task in order to create new permision types allocation
        """
        today = fields.Date.from_string(fields.Date.today())

        permission_types = self.search([('accrual', '=', True),
                                        ("validity_start", "<=", today),
                                        ("validity_stop", ">=", today), ("accrual_created", "=", False)])

        for permission_type in permission_types:
            delta = relativedelta(days=permission_type.interval_number)

            validity_start = datetime.combine(permission_type.validity_stop, time(0, 0, 0)) + relativedelta(days=1)
            validity_stop = datetime.combine(validity_start, time(0, 0, 0)) + delta
            new_allocation = permission_type.copy()
            values = {
                "validity_start": validity_start,
                "validity_stop": validity_stop,
                "accrual_created": False,
                "origin_type_id": permission_type.id,
                "name": "%s - %s" % (permission_type.name, str(validity_start.month)),
            }
            new_allocation.write(values)
            permission_type.accrual_created = True



