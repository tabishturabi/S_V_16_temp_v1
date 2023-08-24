# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrLeaveExt(models.Model):
    _inherit = 'hr.leave'

    # @api.onchange('date_from', 'date_to', 'employee_id')
    # def _onchange_leave_dates(self):
    #     if self.date_from and self.date_to and self.employee_id and self.holiday_status_id:
    #         number_of_days = self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)
    #         if self.holiday_status_id.allocation_type != 'no':
    #             res = self.holiday_status_id.get_days(self.employee_id.id)
    #             balance = 0
    #             if res:
    #                 balance = res.get(self.holiday_status_id.id, False) and res[self.holiday_status_id.id]['remaining_leaves'] or 0
    #             if balance > 0:
    #                 remaining_after_leave = balance - number_of_days
    #                 if remaining_after_leave > 0 and remaining_after_leave < 1:
    #                     number_of_days += remaining_after_leave
    #         self.number_of_days = number_of_days
    #     else:
    #         self.number_of_days = 0



    # @api.model
    # def create(self, vals):
    #     if 'holiday_status_id' in vals:
    #         holiday_id = self.env['hr.leave.type'].browse(vals['holiday_status_id'])
    #         if holiday_id:
    #             if holiday_id.allocation_type != 'no':
    #                 if holiday_id.remaining_leaves - vals['number_of_days'] < 1:
    #                     vals.update({'number_of_days': vals['number_of_days'] + holiday_id.remaining_leaves - vals[
    #                         'number_of_days']})
    #     return super(HrLeaveExt, self).create(vals)

    # @api.multi
    # def write(self, vals):
    #     holiday_id = self.env['hr.leave.type'].browse(self.holiday_status_id.id)
    #     num_of_days = self.number_of_days
    #     state = self.state
    #     if 'holiday_status_id' in vals:
    #         holiday_id = self.env['hr.leave.type'].browse(vals['holiday_status_id'])
    #     if 'number_of_days' in vals:
    #         num_of_days = vals['number_of_days']

    #     if holiday_id and state != 'validate':
    #         if holiday_id.allocation_type != 'no':
    #             if holiday_id.remaining_leaves - num_of_days < 1:
    #                 vals.update({'number_of_days': num_of_days + holiday_id.remaining_leaves - num_of_days})
    #     return super(HrLeaveExt, self).write(vals)
