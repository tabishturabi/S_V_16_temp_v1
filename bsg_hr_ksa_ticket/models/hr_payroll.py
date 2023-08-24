# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from calendar import monthrange


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    
    def set_tickets_to_paid(self):
        for rec in self:
            rec.hr_ticket_ids.write({'state': 'paid'})

    
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        self.set_tickets_to_paid()
        if self.leave_request_id:
            ticket = self.env['hr.ticket.request'].search([('state','=','done'),('leave_request_id','=',self.leave_request_id.id)],limit=1)
            self.contract_id.last_ticket_date = ticket.ticket_date
        return res

    
    def get_hr_tickets(self, payslip):
        if payslip.dict and payslip.dict.type != 'salary':
            sum = 0
            if payslip.dict.leave_request_id or self.env.context.get("leave_id") or payslip.env.get('leave_id'):
                if payslip.dict.type == 'holiday':
                    leave_id = payslip.dict.leave_request_id.id or self.env.context.get("leave_id") or payslip.env.leave_id
                    payslip.env.leave_id = leave_id
                    leave_data = self.env['hr.leave'].browse(leave_id)
                    if not leave_data.issue_ticket_by_company:
                        tickets_vals = self.env['hr.ticket.request'].search(
                            [('employee_id', '=', leave_data.employee_id.id),('leave_request_id', '=', leave_id), ('ticket_date', '>=', leave_data.holiday_salary_start_date),
                             ('ticket_date', '<=', leave_data.holiday_salary_end_date),('state', '=', 'done')])
                        sum = 0
                        if tickets_vals:
                            for rec in tickets_vals:
                                sum = sum + rec.ticket_cost
                        return sum
            elif payslip.dict.hr_termination_id or self.env.context.get("hr_termination_id") or payslip.env.get('hr_termination_id'):
                if payslip.dict.type == 'eos':
                    hr_termination_id = payslip.dict.hr_termination_id or self.env.context.get("hr_termination_id") or payslip.env.get('hr_termination_id')
                    payslip.env.hr_termination_id = hr_termination_id
                    hr_termination = self.env['hr.termination'].browse(hr_termination_id.id)
                    tickets_vals = self.env['hr.ticket.request'].search(
                        [('employee_id', '=', hr_termination.employee_id.id),('termination_id', '=', hr_termination.id), ('ticket_date', '>=', hr_termination.eos_start_date),
                         ('ticket_date', '<=', hr_termination.eos_end_date),('state', '=', 'done')])
                    sum = 0
                    if tickets_vals:
                        for rec in tickets_vals:
                            sum = sum + rec.ticket_cost
                    return sum

            return sum
        else:
            return 0

    hr_ticket_ids = fields.One2many('hr.ticket.request', 'payslip_id',string='Ticket Request')


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    
    def close_payslip_run(self):
        res = super(HrPayslipRun, self).close_payslip_run()
        for run in self:
            run.slip_ids.set_tickets_to_done()
        return res
