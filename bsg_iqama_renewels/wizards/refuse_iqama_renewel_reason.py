# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError



class WizardIqamaRenewels(models.TransientModel):
    _name = 'wizard.iqama.renewel'

    iqama_renewel_id = fields.Many2one('iqama.renewels')
    refusal_reason = fields.Text(string='Reason To Refuse')


    def click_refuse(self):
        if not self.refusal_reason:
            raise ValidationError(_('Reason to refuse the Iqama Renewel is mandatory.'))
        else:
            self.iqama_renewel_id.write({
                'state': 'refused',
                'refusal_reason':self.refusal_reason
            })























