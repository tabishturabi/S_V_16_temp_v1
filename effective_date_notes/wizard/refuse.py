# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_


class EffectiveDateRefuseWizard(models.TransientModel):
    _name = "effdate.refuse.wizard"
    _description = "Refuse Reason Wizard"

    reason = fields.Text(string='Reason', required=True)
    effective_ids = fields.Many2many('effect.request')

    @api.model
    def default_get(self, fields):
        res = super(EffectiveDateRefuseWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'effective_ids': active_ids,
        })
        return res


    def effective_refuse_reason(self):
        if self.effective_ids:
            for rec in self.effective_ids:
                # if rec.notice_type == 'start_after_vacation' and rec.sick_leave_type.leave_type == 'paid':
                rec.refusal_reason = self.reason
                if rec.state == '2':
                    rec.state = '1'
                elif rec.state == '3':
                    if rec.on_paid_leave:
                        rec.state = '2'
                    else:
                        rec.state = '1'
                elif rec.state == '4':
                    rec.state = '3'
                elif rec.state == '5':
                    rec.state = '4'
                elif rec.state == '6':
                    rec.state = '5'
                elif rec.state == '7':
                    rec.state = '6'
                elif rec.state == '11':
                    rec.state = '7'
        return {'type': 'ir.actions.act_window_close'}


class EffectiveCancelReason(models.TransientModel):
    _name = "effdate.cancel.wizard"
    _description = "Cancel Reason Wizard"

    reason = fields.Text(string='Reason', required=True)
    effective_ids = fields.Many2many('effect.request')

    @api.model
    def default_get(self, fields):
        res = super(EffectiveCancelReason, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'effective_ids': active_ids,
        })
        return res

    
    def effective_cancel_reason(self):
        if self.effective_ids:
            for rec in self.effective_ids:
                rec.write({'state': '9'})
                rec.message_post(subject=_('Cancel Reason'),
                                            body="Reject Reason : " + self.reason)

        return {'type': 'ir.actions.act_window_close'}
