# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class AccountInvoiceExt(models.Model):
    _inherit = 'account.move'

    truck_accident_id = fields.Many2one('bsg.truck.accident', string='Truck Accident')
    compensation_id = fields.Many2one('bsg.truck.accident', string='Compensation Bill')
    # Migration Note
    # reverse_entry_id = fields.Many2one('account.move', String="Reverse entry", store=True, readonly=True,
    #                                    related='move_id.reverse_entry_id')
    claims_branch_id = fields.Many2one('bsg_branches.bsg_branches', string="Claims Paid By Branch",
                                       track_visibility=True)
    branches_ids = fields.Many2many('bsg_branches.bsg_branches', string='Branches', track_visibility=True)

    # @api.multi
    def write(self, vals):
        res = super(AccountInvoiceExt, self).write(vals)
        if vals.get('state', '') == 'paid':
            accident_obj = self.env['bsg.truck.accident']
            truck_accident_id = self.truck_accident_id.id if self.truck_accident_id else self.compensation_id.id
            accident_obj.browse(truck_accident_id).write({'state': '8'})
        return res
