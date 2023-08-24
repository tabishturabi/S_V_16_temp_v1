# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError

class PettyExpenceCreateWizard(models.TransientModel):
    _name = 'petty.expence.create.wizard'

    user_id = fields.Many2one('res.users',string="Requested User")
    petty_cash_user_rule_id = fields.Many2one('petty_cash_user_rules',string="Petty Cash User Rule")
    template_id = fields.Many2one('expense.accounting.template',string='Petty Cash Template')
    line_ref = fields.Char(string='Line Ref')
    partner_id = fields.Many2one('res.partner',string='Partner')
    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    branch_id = fields.Many2one('bsg_branches.bsg_branches',string='Branch')
    department_id = fields.Many2one('hr.department',string='Department')
    truck_id = fields.Many2one('fleet.vehicle',string='Truck')
    label = fields.Char()
    attach_files_ids = fields.Many2many('ir.attachment',string="Attachment Files")


    def create_expence(self):
        if not self.attach_files_ids:
            raise UserError(_("The Record Has No Attachment."))
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        record_id = self.env[active_model].browse(int(active_id))
        res = self.env['expense.accounting.petty'].with_context({'without_attachment':True}).create({
            'user_id' : self.user_id.id,
            'petty_cash_user_rule_id' :self.petty_cash_user_rule_id.id, 
            'template_id' : self.template_id.id,
        })
        res._onchange_petty_cash_user_rule_id()
        res._onchange_account_id()
        res.with_context({'without_attachment':True}).onchange_template_id()
        res.with_context({'without_attachment':True})._set_attachment(self.attach_files_ids.ids)
        res.expense_treeview.write({'petty_cash_user_rules_id':self.petty_cash_user_rule_id.id,'is_attach_added':'yes'})
        if self.analytic_account_id and not self.template_id.analytic_account_id:
            res.expense_treeview.write({'analytical_id':self.analytic_account_id.id})

        if self.branch_id and not self.template_id.branch_id:
            res.expense_treeview.write({'branches_id':self.branch_id.id})
        if self.department_id and not self.template_id.department_id:
            res.expense_treeview.write({'department_id':self.department_id.id})
        if self.truck_id:
            res.expense_treeview.write({'fleet_vehicle_id':self.truck_id.id})
        if self.label:
            res.expense_treeview.write({'description':self.label})
        if self.line_ref:
            res.expense_treeview.write({'invoice_ref_no':self.line_ref})
        if self.partner_id:                       
            res.expense_treeview.write({'is_petty_vendor_id':self.partner_id.id}) 
        record_id.set_expense_id(res.id)























