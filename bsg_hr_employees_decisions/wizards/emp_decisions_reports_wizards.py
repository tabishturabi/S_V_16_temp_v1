# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError



class EmployeeAppointmentReport(models.TransientModel):
    _name = 'wizard.employee.decisions.report'

    decision_type = fields.Selection([('appoint_employee', 'Decision to appoint an employee'),
                                      ('transfer_employee', 'Decision to transfer an employee'),
                                      ('assign_employee', 'Decision to assign an employee')],
                                     string='Decision Type')
    print_date = fields.Date(string='Print Date',readonly=True,default=fields.date.today())
    employee_decisions = fields.Many2one('employees.appointment',string='Employee Decision')


    def action_print_decision_report(self):
        pass
        # data = {
        #     'ids': self.ids,
        #     'model': self._name,
        # }
        # return self.env.ref('bsg_hr_employees_decisions.employee_appointment_report_pdf_id').report_action(self, data=data)



























