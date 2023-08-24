# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round


class WizardLeaveRefect(models.TransientModel):
    _name = 'wizard.leave.reject'

    leave_id = fields.Many2one('hr.leave', string='Leave')
    reject_reason = fields.Text(string='Reason To Reject')

    def click_reject(self):
        if not self.reject_reason:
            raise ValidationError(_('Reason to reject the leave is mandatory.'))
        else:
            if self.leave_id.holiday_status_id.leave_type in (
            'sick', 'death', 'birth', 'marry', 'birthdelivery', 'test'):
                if self.leave_id.state == 'hr_specialist':
                    self.leave_id.write({
                        'state': 'draft',
                        'reject_reason': self.reject_reason
                    })
            elif self.leave_id.holiday_status_id.leave_type in ('unpaid', 'haj'):
                if self.leave_id.state == 'department_manager':
                    self.leave_id.write({
                        'state': 'draft',
                        'reject_reason': self.reject_reason
                    })
                elif self.leave_id.state == 'hr_specialist':
                    self.leave_id.write({
                        'state': 'department_manager',
                        'reject_reason': self.reject_reason
                    })
                elif self.leave_id.state == 'hr_manager':
                    self.leave_id.write({
                        'state': 'hr_specialist',
                        'reject_reason': self.reject_reason
                    })
            elif self.leave_id.holiday_status_id.leave_type in ('paid'):
                if self.leave_id.state == 'department_manager':
                    self.leave_id.write({'state': 'draft',
                                         'reject_reason': self.reject_reason
                                         })
                elif self.leave_id.state == 'hr_specialist':
                    self.leave_id.write({'state': 'department_manager',
                                         'reject_reason': self.reject_reason
                                         })
                elif self.leave_id.state == 'hr_manager':
                    self.leave_id.write({'state': 'hr_specialist',
                                         'reject_reason': self.reject_reason
                                         })
                elif self.leave_id.state == 'internal_audit_manager' and self.leave_id.is_send_confirmation:
                    self.leave_id.write({'state': 'hr_specialist',
                                         'reject_reason': self.reject_reason,
                                         'is_send_confirmation': False
                                         })
                elif self.leave_id.state == 'finance_manager':
                    self.leave_id.write({'state': 'internal_audit_manager',
                                         'reject_reason': self.reject_reason
                                         })
                elif self.leave_id.state == 'accountant':
                    if not self.leave_id.is_send_confirmation:
                        if self.leave_id.is_allocation:
                            allocation_request = self.env['hr.leave.allocation'].search(
                                [('is_annual_allocation', '=', True),
                                 ('employee_id', '=', self.leave_id.employee_id.id),
                                 ('employee_id.active', '=', True), ('state', '=', 'validate'),
                                 ('holiday_type', '=', 'employee')], limit=1)
                            allocation_request.sudo().write(
                                {'number_of_days': allocation_request.number_of_days - float_round(
                                    self.leave_id.vacation_balance % 1, precision_digits=3)})
                            self.leave_id.is_allocation = False
                        self.leave_id.write({'state': 'hr_manager',
                                             'reject_reason': self.reject_reason
                                             })
