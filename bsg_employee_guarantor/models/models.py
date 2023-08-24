# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError
class EmployeeGuarantor(models.Model):
    _inherit = 'hr.employee'
    _description = 'Add Guarantor Field in Employee'




    guarantor_id = fields.Many2one('bsg.hr.guarantor',string='Guarantor',compute="_get_guarantor" ,inverse="inverse_get_guarantor")
    inverse_id = fields.Many2one('bsg.hr.guarantor',string='Guarantor')
    bool_id = fields.Boolean(string='Check')



    @api.onchange('bsg_empiqama')
    def onchange_iqama(self):
        for rec in self:
            if rec:
                rec.bool_id = True

    # @api.multi
    def _get_guarantor(self):
        for rec in self:
            rec.guarantor_id = False
            if rec.bsg_empiqama and not rec.inverse_id:
                rec.guarantor_id = rec.bsg_empiqama.guarantor_id.id
            if rec.inverse_id and not rec.bool_id:
                rec.guarantor_id = rec.inverse_id.id
            if rec.bool_id:
                rec.guarantor_id = rec.bsg_empiqama.guarantor_id.id


    # @api.multi
    def inverse_get_guarantor(self):
        for rec in self:
            if rec:
                rec.inverse_id=rec.guarantor_id.id
                rec.bool_id=False





