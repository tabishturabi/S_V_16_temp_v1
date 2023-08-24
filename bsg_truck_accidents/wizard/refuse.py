# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class RejectWizard(models.TransientModel):
    _name = "reject.wizard"
    _description = "Truck Accident Reject Reason Wizard"

    reason = fields.Text(string='Reason', required=True)

    # @api.multi
    def truck_accident_reject_reason(self):
        active_ids = self.env.context.get('active_ids', [])
        truck_accident = self.env['bsg.truck.accident'].browse(active_ids)
        if truck_accident.claim_type == 'third_party_claim':
            state_id = int(truck_accident.state_third_party)
            state_id -= 1
            truck_accident.write({'state_third_party': str(state_id)})
        elif truck_accident.claim_type == 'shaamil_claim':
            state_id = int(truck_accident.state_shaamil)
            state_id -= 1
            truck_accident.write({'state_shaamil': str(state_id)})
        elif truck_accident.claim_type == 'clear_cars':
            state_id = int(truck_accident.state_clear_cars)
            state_id -= 1
            truck_accident.write({'state_clear_cars': str(state_id)})
        else:
            if truck_accident.is_path_to_audit:
                truck_accident.write({'state': '7', 'is_send_to_audit': False})
                truck_accident.message_post(subject=_('Reject Reason'),
                                            body="Reject Reason : " + self.reason)
            else:
                state_id = int(truck_accident.state)
                if truck_accident.accident_agreement_type == 'agreement_comp':
                    if state_id == 3:
                        state_id -= 2
                    elif state_id == 6:
                        state_id -= 3
                    elif state_id == 12:
                        state_id = 3
                    else:
                        state_id -= 1
                else:
                    state_id -= 1
                truck_accident.write({'state': str(state_id)})
                truck_accident.message_post(subject=_('Reject Reason'),
                                            body="Reject Reason : " + self.reason)

        return {'type': 'ir.actions.act_window_close'}
