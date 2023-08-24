# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrEosRefuse(models.TransientModel):
    _name = "hr.eos.refuse"

    reason = fields.Text(string='Reason', required=True)
    hr_termination_id = fields.Many2one('hr.termination')

    @api.model
    def default_get(self, fields):
        res = super(HrEosRefuse, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        res.update({
            'hr_termination_id': active_id,
        })
        return res

    
    def eos_refuse_reason(self):
        active_ids = self.env.context.get('active_ids', [])
        termination_id = self.env['hr.termination'].browse(active_ids)
        state_id = int(termination_id.state)
        if self.hr_termination_id:
            for rec in self.hr_termination_id:
                if rec.eos_by_employee_service and state_id == 5:
                    state_id -= 2
                else:
                    state_id-=1
                rec.write({'reject_reason': self.reason, 'state': str(state_id)})
        return {'type': 'ir.actions.act_window_close'}
