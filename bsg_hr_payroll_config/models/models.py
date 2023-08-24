# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class PayslipBatchesConfig(models.Model):
    _name='hr.payslip.run'
    _inherit = ['hr.payslip.run', 'mail.thread']
    _description = 'Payslip Batches'

    
    def action_import_inputs(self):
        view_id = self.env.ref('bsg_hr_payroll_config.wizard_import_inputs').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Name',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'import.inputs',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_batch_id': self.id,
            }
        }


