# -*- coding: utf-8 -*-

from datetime import datetime, time
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.addons.resource.models.resource import HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_round
from collections import defaultdict

LOG_ACCESS_COLUMNS = ['create_uid', 'create_date', 'write_uid', 'write_date']
MAGIC_COLUMNS = ['id'] + LOG_ACCESS_COLUMNS


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    accrual = fields.Boolean("Accrual", readonly=True,
                             states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    is_used = fields.Boolean()
    is_annual_allocation = fields.Boolean("Is Annual Allocation", default=False)
    nextcall = fields.Date("Date of the next accrual allocation", default=False, readonly=False)


    def activity_update(self):
        pass

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        for holiday in self:
            val_type = holiday.holiday_status_id.sudo().leave_validation_type
            if state == 'confirm':
                continue

            if state == 'draft':
                if holiday.employee_id != current_employee and not is_manager:
                    raise UserError(_('Only a Leave Manager can reset other people leaves.'))
                continue

            # if not is_officer:
            #     raise UserError(_('Only a Leave Officer or Manager can approve or refuse leave requests.'))

            if is_officer:
                # use ir.rule based first access check: department, members, ... (see security.xml)
                holiday.check_access_rule('write')

            # if holiday.employee_id == current_employee and not is_manager:
            #     raise UserError(_('Only a Leave Manager can approve its own requests.'))

            if (state == 'validate1' and val_type == 'both') or (state == 'validate' and val_type == 'manager'):
                manager = holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
                if (manager and manager != current_employee) and not self.env.user.has_group(
                        'hr_holidays.group_hr_holidays_manager'):
                    raise UserError(_('You must be either %s\'s manager or Leave manager to approve this leave') % (
                        holiday.employee_id.name))

            if state == 'validate' and val_type == 'both':
                if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                    raise UserError(_('Only an Leave Manager can apply the second approval on leave requests.'))

    
    @api.returns(None, lambda value: value[0])
    def copy_data(self, default=None):
        """
        Copy given record's data with all its fields values

        :param default: field values to override in the original values of the copied record
        :return: list with a dictionary containing all the field values
        """
        # In the old API, this method took a single id and return a dict. When
        # invoked with the new API, it returned a list of dicts.
        self.ensure_one()
        if not self._context.get('force_copy', False):
            raise UserError(_('A leave cannot be duplicated.'))

        # avoid recursion through already copied records in case of circular relationship
        if '__copy_data_seen' not in self._context:
            self = self.with_context(__copy_data_seen=defaultdict(set))
        seen_map = self._context['__copy_data_seen']
        if self.id in seen_map[self._name]:
            return
        seen_map[self._name].add(self.id)

        default = dict(default or [])
        if 'state' not in default and 'state' in self._fields:
            field = self._fields['state']
            if field.default:
                value = field.default(self)
                value = field.convert_to_cache(value, self)
                value = field.convert_to_record(value, self)
                value = field.convert_to_write(value, self)
                default['state'] = value

        # build a black list of fields that should not be copied
        blacklist = set(MAGIC_COLUMNS + ['parent_path'])
        whitelist = set(name for name, field in self._fields.items() if not field.inherited)

        def blacklist_given_fields(model):
            # blacklist the fields that are given by inheritance
            for parent_model, parent_field in model._inherits.items():
                blacklist.add(parent_field)
                if parent_field in default:
                    # all the fields of 'parent_model' are given by the record:
                    # default[parent_field], except the ones redefined in self
                    blacklist.update(set(self.env[parent_model]._fields) - whitelist)
                else:
                    blacklist_given_fields(self.env[parent_model])
            # blacklist deprecated fields
            for name, field in model._fields.items():
                if field.deprecated:
                    blacklist.add(name)

        blacklist_given_fields(self)

        fields_to_copy = {name: field
                          for name, field in self._fields.items()
                          if field.copy and name not in default and name not in blacklist}

        for name, field in fields_to_copy.items():
            if field.type == 'one2many':
                # duplicate following the order of the ids because we'll rely on
                # it later for copying translations in copy_translation()!
                lines = [rec.copy_data()[0] for rec in self[name].sorted(key='id')]
                # the lines are duplicated using the wrong (old) parent, but then
                # are reassigned to the correct one thanks to the (0, 0, ...)
                default[name] = [(0, 0, line) for line in lines if line]
            elif field.type == 'many2many':
                default[name] = [(6, 0, self[name].ids)]
            else:
                default[name] = field.convert_to_write(self[name], self)

        return [default]

    @api.model
    def _update_accrual(self):
        today = fields.Date.from_string(fields.Date.today())
        holidays = self.search(
            [('is_annual_allocation', '=', True), ('employee_id.employee_state', 'in', ['on_job']),
             ('employee_id.state', 'in', ['on_job', 'trail_period']),
             ('employee_id.active', '=', True), ('state', '=', 'validate'), ('holiday_type', '=', 'employee'),
             '|', ('nextcall', '=', False), ('nextcall', '<', today)])
        delta = relativedelta(days=0)
        # if not holidays.nextcall and holidays.employee_id.last_return_date:
        #     diff = today - holidays.employee_id.last_return_date
        # else:
        #     diff = today - holidays.nextcall
        # if diff.days == 30:
        for holiday in holidays:
            values = {}
            values['nextcall'] = (holiday.nextcall if holiday.nextcall else today) + delta
            contract_id = holiday.employee_id.contract_id
            if contract_id and contract_id.state == 'open':
                contract_annual_legal_leave = contract_id.annual_legal_leave
                if holiday.employee_id.country_id.code == 'SA':
                    if contract_annual_legal_leave > 30:
                        days_to_give = contract_annual_legal_leave / 12
                        balance_per_day = days_to_give / 30
                    else:
                        days_to_give = 30 / 12
                        balance_per_day = days_to_give / 30
                else:
                    if contract_annual_legal_leave > 21:
                        days_to_give = contract_annual_legal_leave / 12
                        balance_per_day = days_to_give / 30
                    else:
                        day_from = fields.Datetime.from_string(contract_id.date_start)
                        day_to = fields.Datetime.from_string(today)
                        date_diff = relativedelta(day_to, day_from)
                        if date_diff.years >= 5:
                            days_to_give = 30 / 12
                            balance_per_day = days_to_give / 30
                        else:
                            days_to_give = 21 / 12
                            balance_per_day = days_to_give / 30
                values['number_of_days'] = holiday.number_of_days + float_round(balance_per_day, precision_digits=3)
            if values.get('number_of_days', 0) > 0:
                values['state'] = 'validate'
                values['nextcall'] = today
                holiday.write(values)
        # else:
        #     return 0

    @api.model
    def create(self, values):
        if values.get('holiday_status_id', False) and values.get('employee_id', False):
            leave_type = self.env['hr.leave.type'].browse(values.get('holiday_status_id'))
            if leave_type and leave_type.leave_type == 'paid':
                leave_allocation = self.env['hr.leave.allocation'].search(
                    [('is_annual_allocation', '=', True), ('employee_id', '=', values.get('employee_id'))]).filtered(
                    lambda l: l.holiday_status_id.leave_type == 'paid')
                if len(leave_allocation) > 0:
                    raise ValidationError(_('Allocation request for this employee already exists'))
                values['is_annual_allocation'] = True
        return super(HolidaysAllocation, self).create(values)

    
    def action_confirm(self):
        if self.holiday_status_id and self.holiday_status_id.leave_type == 'paid':
            if not self.is_annual_allocation:
                self.is_annual_allocation = True

        return super(HolidaysAllocation, self).action_confirm()

    
    def action_approve(self):
        for rec in self:
            if rec.holiday_status_id and rec.holiday_status_id.leave_type == 'paid':
                if not rec.is_annual_allocation:
                    rec.is_annual_allocation = True
        return super(HolidaysAllocation, self).action_approve()


    def _action_validate_create_childs(self):
        childs = self.env['hr.leave.allocation']
        if self.state == 'validate' and self.holiday_type in ['category', 'department', 'company']:
            if self.holiday_type == 'category':
                employees = self.category_id.employee_ids
            elif self.holiday_type == 'department':
                employees = self.department_id.member_ids
            else:
                employees = self.env['hr.employee'].search([('company_id', '=', self.mode_company_id.id)])
            employees = employees.filtered(lambda emp: emp.state in ['trail_period','on_job','on_leave'] and emp.employee_state in ['on_job','on_leave'])
            for employee in employees:
                childs += self.with_context(
                    mail_notify_force_send=False,
                    mail_activity_automation_skip=True
                ).create(self._prepare_holiday_values(employee))
            # TODO is it necessary to interleave the calls?
            childs.action_approve()
            if childs and self.holiday_status_id.validation_type == 'both':
                childs.action_validate()
        return childs

    
    def action_refuse(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if not self.env.user.has_group('base.group_system') and not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            raise UserError(_('No access right for this action!.'))
        if any(holiday.state not in ['confirm', 'validate', 'validate1'] for holiday in self):
            raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))
        validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
        validated_holidays.write({'state': 'refuse', 'first_approver_id': current_employee.id})
        # Migration NOte
        # (self - validated_holidays).write({'state': 'refuse', 'second_approver_id': current_employee.id})
        (self - validated_holidays).write({'state': 'refuse', 'approver_id': current_employee.id})
        # If a category that created several holidays, cancel all related
        linked_requests = self.mapped('linked_request_ids')
        if linked_requests:
            linked_requests.action_refuse()
        self.activity_update()
        return True
