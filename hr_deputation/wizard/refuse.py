# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_


class DeputationRefuseWizard(models.TransientModel):
    _name = "deputation.refuse.wizard"
    _description = "Refuse Reason Wizard"

    reason = fields.Text(string='Reason', required=True)
    deputation_ids = fields.Many2many('hr.deputations')

    @api.model
    def default_get(self, fields):
        res = super(DeputationRefuseWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'deputation_ids': active_ids,
        })
        return res

    def deputation_refuse_reason(self):
        if self.deputation_ids:
            for rec in self.deputation_ids:
                if rec.state == 'finance_manager':
                    rec.state = 'internal_audit'
                elif rec.state == 'internal_audit':
                    rec.state = 'hr_manager'
                elif rec.state == 'hr_manager':
                    rec.state = 'hr_salary_accountant'
                elif rec.state == 'hr_salary_accountant':
                    rec.state = 'direct_manager'
                elif rec.state == 'direct_manager':
                    rec.state = 'draft'
            self.deputation_ids.write({
                'refusal_reason': self.reason
            })
        return {'type': 'ir.actions.act_window_close'}


# class EmpServiceCancelReason(models.TransientModel):
#     _name = "empservice.cancel.wizard"
#     _description = "Cancel Reason Wizard"
#
#     reason = fields.Text(string='Reason', required=True)
#     effective_ids = fields.Many2many('employee.service')
#
#     @api.model
#     def default_get(self, fields):
#         res = super(EmpServiceCancelReason, self).default_get(fields)
#         active_ids = self.env.context.get('active_ids', [])
#         res.update({
#             'effective_ids': active_ids,
#         })
#         return res
#
#     @api.multi
#     def effective_cancel_reason(self):
#         if self.effective_ids:
#             for rec in self.effective_ids:
#                 rec.write({'state': 'cancel','cancel_reason':self.reason})
#
#
#         return {'type': 'ir.actions.act_window_close'}
