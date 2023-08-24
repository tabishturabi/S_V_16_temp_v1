# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrExitReturnRefuse(models.TransientModel):
    _name = "hr.exit.return.refuse"
    _description = "Exit Return Refuse Reason"

    reason = fields.Text(string='Reason', required=True)
    hr_exit_return_id = fields.Many2one('hr.exit.return')

    @api.model
    def default_get(self, fields):
        res = super(HrExitReturnRefuse, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'hr_exit_return_id': active_ids,
        })
        return res

    
    def exit_entry_refuse_reason(self):
        if self.hr_exit_return_id:
            for rec in self.hr_exit_return_id:
                rec.write({'reject_reason': self.reason, 'state': 'draft'})
        return {'type': 'ir.actions.act_window_close'}
