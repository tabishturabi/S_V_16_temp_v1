# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError

class SwabRequestWiz(models.TransientModel):
    _name = 'swap.request.wiz'
    _description = 'Rota Swap Request Wizard'

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(SwabRequestWiz, self).default_get(fields_list)
    #     employee_id = self.env['hr.employee'].browse(self._context.get('active_id',False))
    #     res['employee_id'] = employee_id.id
    #     return res

    employee_id = fields.Many2one("hr.employee", string="Employee Name", required=False,readonly=True)
    employee_swap_id = fields.Many2one("hr.employee", string="Employee Name", required=True)
    shift_id = fields.Many2one('rota.shift', string="Shift", required=False, readonly=True)
    shift_swap_id = fields.Many2one("rota.shift", string="Shift", required=False, compute='get_rota_rota_cla_line')
    rota_calendar_id = fields.Many2one('rota.calendar', string='Calendar',readonly=True)
    calendar_swap_id = fields.Many2one('rota.calendar', string='Calendar', compute='get_rota_rota_cla_line')
    rota_calender_line = fields.Many2one('rota.calendar.line', string="Rota Calendar Line", readonly=True)
    rota_calender_line_swap = fields.Many2one('rota.calendar.line', string="Rota Calendar Line", compute='get_rota_rota_cla_line')
    rota_id = fields.Many2one('hr.attendance.rota', string="Rota", readonly=True)
    rota_swap_id = fields.Many2one('hr.attendance.rota', string="Rota", readonly=True, compute='get_rota_rota_cla_line')
    date = fields.Date(string="Date", required=False ,readonly=True)
    swap_date = fields.Date(string="Date", required=False, compute='get_rota_rota_cla_line')
    user_id = fields.Many2one('res.users', string="Requested By",readonly=True, required=False, )

    #@api.multi
    @api.depends('employee_swap_id')
    def get_rota_rota_cla_line(self):
        calendar_line_obj = self.env['rota.calendar.line'].search([('employee_id', '=', self.employee_swap_id.id)])
        for line in calendar_line_obj:
            if line.employee_id == self.employee_swap_id:
                self.rota_swap_id = line.rota_id.id
                self.rota_calender_line_swap = line.id
                self.calendar_swap_id = line.rota_calendar_id.id
                self.shift_swap_id = line.shift_id.id
                self.swap_date = line.date
            else:
                self.rota_swap_id = False
                self.rota_calender_line_swap = False
                self.calendar_swap_id = False
                self.shift_swap_id = False
                self.swap_date = False

    @api.onchange('employee_swap_id','rota_id')
    def get_employees(self):
        if self.rota_id:
            domain = {'employee_swap_id': [('contract_id.type_attendance', '=', 'byrota'),
                                      ('department_id', 'child_of', self.rota_id.department.id)]}
            return {'domain': domain}

    #@api.multi
    def action_create_swap_request(self):
        rota_swap_obj = self.env['rota.swap.request']
        if self.rota_id == self.rota_swap_id:
            check_swap_req = rota_swap_obj.search([('employee_id', '=', self.employee_id.id), ('state', '!=', 'confirm')])
            if not check_swap_req:
                for rec in self:
                    rota_swap_req = ({
                        'state': 'submit',
                        'employee_id': rec.employee_id.id,
                        'shift_id': rec.shift_id.id,
                        'rota_id': rec.rota_id.id,
                        'date': rec.date,
                        'user_id': rec.user_id.id,
                        'employee_swap_id': rec.employee_swap_id.id,
                        'shift_swap_id': rec.shift_swap_id.id,
                        'swap_date': rec.swap_date,
                        'rota_swap_id': rec.rota_swap_id.id,
                        'calendar_swap_id': rec.calendar_swap_id.id,
                        'rota_calender_line_swap': rec.rota_calender_line_swap.id
                        # 'swap_request_date': datetime.now(),
                    })
                    rota_swap_obj.create(rota_swap_req)
                return rota_swap_obj
            else:
                raise ValidationError("This Employee Have Swap Request not Confirmed Yet!.")
        else:
            raise ValidationError("This Employees its'nt in The Same Rota !.")






