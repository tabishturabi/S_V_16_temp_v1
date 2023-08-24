# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _

class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    
    def action_batch_wise_register_payment(self):
        context = dict(self._context or {})
        action = self.env.ref('bsg_hr_payroll.hr_payslip_sheet_register_payment_wizard_action').read()[0]
        action['views'] = [(self.env.ref('bsg_hr_payroll.hr_payslip_sheet_register_payment_view_form').id, 'form')]
        context['active_ids'] = self.slip_ids.ids
        action['context'] = context
        return action

    

