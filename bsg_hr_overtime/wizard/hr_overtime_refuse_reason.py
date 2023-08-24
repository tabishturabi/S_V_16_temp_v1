# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrOvertimeRefuseWizard(models.TransientModel):
    

    _name = "hr.overtime.refuse.wizard"
    _description = "Overtime Refuse Reason Wizard"

    reason = fields.Text(string='Reason', required=True)
    hr_overtime_ids = fields.Many2many('hr.overtime')

    @api.model
    def default_get(self, fields):
        res = super(HrOvertimeRefuseWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
                'hr_overtime_ids': active_ids,
            })
        return res

    #@api.multi
    def overtime_refuse_reason(self):
        if self.hr_overtime_ids:
            for rec in self.hr_overtime_ids:
                rec.write({'refusal_reason':self.reason,'state':'cancel'})

        return {'type': 'ir.actions.act_window_close'}
