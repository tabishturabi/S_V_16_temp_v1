# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class HRTicketRequestReject(models.TransientModel):
    _name = "hr.ticket.request.reject"
    _description = "HR Ticket Request Reject"

    reason = fields.Text(string='Reason', required=True)

    
    def ticket_reject_reason(self):
        active_ids = self.env.context.get('active_ids', [])
        ticket_request = self.env['hr.ticket.request'].browse(active_ids)
        ticket_request.write({'state': 'draft'})
        ticket_request.message_post(subject=_('Reject Reason'),
                                    body="Reject Reason : " + self.reason)

        return {'type': 'ir.actions.act_window_close'}
