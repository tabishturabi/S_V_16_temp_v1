# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    trailer_id = fields.Many2one('bsg_fleet_trailer_config','Trailer')

    @api.model
    def create(self,vals):
        if vals.get('move_id'):
            if vals.get('tax_ids') or vals.get('analytic_account_id'):
               invoice_line_id = self.env['account.move.line'].search([('move_id','=',vals.get('move_id')),('account_id','=',vals.get('account_id'))],limit=1)
               vals['bsg_branches_id'] = invoice_line_id.branch_id.id if invoice_line_id.branch_id else False
               vals['fleet_vehicle_id'] = invoice_line_id.fleet_id.id if invoice_line_id.fleet_id else False
               vals['department_id'] = invoice_line_id.department_id.id if invoice_line_id.department_id else False
               vals['trailer_id'] = invoice_line_id.trailer_id.id if invoice_line_id.trailer_id else False               
            invoice_line_id = self.env['account.move.line'].search([('move_id','=',vals.get('move_id')),('account_id','=',vals.get('account_id')),('product_id','=',vals.get('product_id'))])
            if len(invoice_line_id) != 1 and len(invoice_line_id) != 0:
                if invoice_line_id[0].contract_line_id:
                    if invoice_line_id[0].contract_line_id.branch_id:
                        vals['bsg_branches_id'] = invoice_line_id[0].contract_line_id.branch_id.id
                    if invoice_line_id[0].contract_line_id.department_id:
                        vals['department_id'] = invoice_line_id[0].contract_line_id.department_id.id
            else:
                if invoice_line_id.contract_line_id:
                    if invoice_line_id.contract_line_id.branch_id:
                        vals['bsg_branches_id'] = invoice_line_id.contract_line_id.branch_id.id
                    if invoice_line_id.contract_line_id.department_id:
                        vals['department_id'] = invoice_line_id.contract_line_id.department_id.id                
        res = super(AccountMoveLine,self).create(vals)
        return res
