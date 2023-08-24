# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api,_
from datetime import datetime, time
from pytz import timezone, UTC

class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'
    _description = 'Add Overtime To Payslip Input'

    overtime_ids = fields.Many2many('hr.overtime', string="Overtimes")

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    _description = 'Compute Employee Overtime Requests With Payslip'
    
    #To Write It As Paid When Pay The Salary
    overtime_requests = fields.Integer(string='Overtime', compute='compute_overtime_requests')

    def action_overtime(self):

        #tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        #date_from = datetime.combine(self.date_from, time.min)
        #date_to =   datetime.combine(self.date_to, time.max)
        #date_from =tz.localize(date_from).astimezone(UTC).replace(tzinfo=None)
        #date_to = tz.localize(date_to).astimezone(UTC).replace(tzinfo=None)
        overtime_ids = []
        for rec in self:
            overtime_ids = rec.input_line_ids.mapped('overtime_ids').ids
        return {
            'name': 'Employee Overtime Requests',
            'domain': [('employee_name', '=', self.employee_id.id),('id', 'in', overtime_ids)],
            'res_model': 'hr.overtime',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }
    #@api.multi
    def compute_overtime_requests(self):
        #tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        #date_from = datetime.combine(self.date_from, time.min)
        #date_to =   datetime.combine(self.date_to, time.max)
        #date_from =tz.localize(date_from).astimezone(UTC).replace(tzinfo=None)
        #date_to = tz.localize(date_to).astimezone(UTC).replace(tzinfo=None)
        overtime_ids = []
        for rec in self:
            overtime_ids = rec.input_line_ids.mapped('overtime_ids').ids
        #count = self.env['hr.overtime'].search_count([('employee_name', '=', self.employee_id.id),('state', '=', 'in_payroll'),('report_nextslip','=',True)])
            rec.overtime_requests = len(overtime_ids)
        


    def get_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip"""
        res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
        #tz = timezone(self.env.context.get('tz') or self.env.user.tz)

        #date_from = datetime.combine(self.date_from, time.min)
        #date_to =   datetime.combine(self.date_to, time.max)
        #date_from =tz.localize(date_from).astimezone(UTC).replace(tzinfo=None)
        #date_to = tz.localize(date_to).astimezone(UTC).replace(tzinfo=None)
        if self.type == 'salary':
            overtimes = self.env['hr.overtime'].search([('employee_name', '=', self.employee_id.id),('state', '=', 'in_payroll'),('report_nextslip','=',True),('payslip_ids','=',False)])
            if overtimes:
                for result in res:
                    if result.get('code') == 'ADDVAR':
                        result['amount'] = sum(overtimes.mapped('total_overtime_amount'))
                        result['overtime_ids'] = overtimes
                        result['description'] = _("Overtime For %s" %overtimes.mapped('sequence_number'))
        return res


    #@api.multi
    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.overtime_ids:
                for overtime in line.overtime_ids:
                    overtime.write({'state':'posted'})
        return super(HrPayslip, self).action_payslip_done()

    #@api.multi
    def action_payslip_cancel(self):
        for line in self.input_line_ids:
            if line.overtime_ids:
                line.overtime_ids.write({'payslip_ids':False})
        return super(HrPayslip, self).action_payslip_cancel()            


        


