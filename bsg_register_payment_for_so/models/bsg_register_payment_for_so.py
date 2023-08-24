# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class BsgRegisterPaymentForSo(models.TransientModel):
    _name = 'bsg_register_payment_for_so'

    cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale',string="Cargo Sale ID")

    #for adding group to current login user and opent selected record
    def grant_user_access(self):
        branches_management  = self.env.ref('payments_enhanced.group_branches_management')
        branches_management.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).write({'users': [(4, self.env.user.id)]})
        return {
            'name': _('Local Cargo Sale'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'bsg_vehicle_cargo_sale',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': self.cargo_sale_id.id,
        }