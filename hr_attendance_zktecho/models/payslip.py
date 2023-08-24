# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models ,api

class Payslip(models.Model):
    _inherit = 'hr.payslip'
    
    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        return super(Payslip, self).get_worked_day_lines(contracts.with_context(calc_from_att = True), date_from, date_to)
    
    
class Employee(models.Model):
    _inherit = 'hr.employee'
    
    def get_work_days_data(self, from_datetime, to_datetime, compute_leaves=True, calendar=None, domain=None):
        if 'calc_from_att' in self._context:
            data = self.get_attendance_data(from_datetime, to_datetime)
            return {
                'days': data['number_of_days'],
                'hours': data['number_of_hours'],
            }
        # Migration Note
        # return super(Employee, self).get_work_days_data(from_datetime, to_datetime, compute_leaves=compute_leaves, calendar=calendar, domain=domain)
    
    def get_attendance_data(self, from_datetime, to_datetime):
        total_wh = 0
        if to_datetime and from_datetime:
            from_date = from_datetime
            to_date = to_datetime
            attendences = {}
            employee = self
            attendences = self.env['hr.attendance'].search([('employee_id','=',employee.id),
                                                            ('check_in','>=',str(from_date)),
                                                            ('check_out','<=',str(to_date))])
            wh = 0.0
            number_days = 0
            for att in attendences:
                wh += att.inside_calendar_duration
                number_days+=1
        return {'number_of_hours':wh , 'number_of_days':number_days}
    