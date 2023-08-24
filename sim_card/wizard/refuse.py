# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class refuseWizard(models.TransientModel):
    _name = "refuse.wizard"
    _description = "Sim Card Refuse Reason Wizard"

    reason = fields.Text(string='Reason', required=True)
    sim_card_ids = fields.Many2many('sim.card.request')

    @api.model
    def default_get(self, fields):
        res = super(refuseWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'sim_card_ids': active_ids,
        })
        return res

    
    def sim_card_refuse_reason(self):
        if self.sim_card_ids:
            for rec in self.sim_card_ids:
                rec.write({'refusal_reason': self.reason, 'state': 'reject'})

        return {'type': 'ir.actions.act_window_close'}


class LostWizard(models.TransientModel):
    _name = "lost.wizard"
    _description = "Refuse Reason Wizard"

    reason = fields.Text(string='Reason', required=True)
    lost_ids = fields.Many2many('lost.request')

    @api.model
    def default_get(self, fields):
        res = super(LostWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'lost_ids': active_ids,
        })
        return res

    
    def lost_refuse_reason(self):
        if self.lost_ids:
            for rec in self.lost_ids:
                rec.write({'refusal_reason': self.reason, 'state': 'cancel'})

        return {'type': 'ir.actions.act_window_close'}