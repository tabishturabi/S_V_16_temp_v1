# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError



class WizardEmployeeDecisions(models.TransientModel):
    _name = 'wizard.employee.decisions'

    employee_decisions = fields.Many2one('employees.appointment')
    refusal_reason = fields.Text(string='Reason To Refuse')


    def click_refuse(self):
        if not self.refusal_reason:
            raise ValidationError(_('Reason to refuse the decision is mandatory.'))
        else:
            self.employee_decisions.write({
                'state': 'refused',
                'refusal_reason':self.refusal_reason
            })























