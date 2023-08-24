# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    #for add validation as need of Tax ID  should be unique

    @api.constrains('vat')
    def _ref_constrains(self):
        for data in self:
            if data.vat:
                # vat =  str(data.vat)
                # search_param = vat.casefold()
                # search_param_upper = vat.upper()
                # search_id = self.search(['|',('vat','=',search_param_upper),('vat','=',search_param)])
                search_id = self.search([('vat','=',data.vat),('id','!=',data.id),('parent_id','!=',data.parent_id.id),('id','!=',data.parent_id.id)])
                if len(search_id) > 1:
                    raise UserError('Tax ID Must Be Unique..!')

    #override to passing domain value
    @api.onchange('partner_types')
    def _onchange_partner_types(self):
        for data in self:
            data.partner_types.with_context({'id_s' : True})
            if data.partner_types:
                data.property_account_receivable_id = data.partner_types.accont_rec.id
                data.property_account_payable_id = data.partner_types.accont_payable.id

    #override to passing domain value
    @api.onchange('is_petty_vendor')
    def _onchange_is_petty_vendor(self):
        if self._context.get('passing_partner_type_ids'):
            list_val = self._context.get('passing_partner_type_ids')[0]
            return {'domain': {'partner_types': [('id', 'in',list_val[2])]}} # list_val[2]

    #for getting balance
    
    def _get_balance(self):
        receive_amount = 0 
        send_amont = 0
        # for data in self.env['account.payment'].search([('partner_id','=',self.id),('payment_type','=','inbound'),('state','not in',['draft','cancelled']),('partner_type','=','customer')]):
        #     send_amont += data.amount
        for data in self.env['account.payment'].search([('partner_id','=',self.id),('payment_type','=','outbound'),('state','not in',['draft','cancelled'])]):
            receive_amount += data.amount
        for receive_data in self.env['expense.accounting.petty'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('requested_partner_id','=',self.id)]):
            send_amont += receive_data.total
        self.balance_payment = (receive_amount - send_amont)

    balance_payment = fields.Float("Balance",compute="_get_balance")
    is_petty_vendor = fields.Boolean("Petty Cash Vendor")

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_expense_product = fields.Boolean(string="Expense Product")
