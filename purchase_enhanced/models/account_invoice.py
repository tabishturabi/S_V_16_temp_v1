# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import  UserError


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    purchase_count = fields.Integer(compute="_compute_purchase", string='Po Count', copy=False, default=0, store=True)
    purchase_ids = fields.Many2many('purchase.order','invoice_id','purchase_id',compute="_compute_purchase", string='PO/Orders', copy=False, store=True)
    state = fields.Selection(
        selection_add=[('emp_audit', 'Employee Audit'),('manager_audit', 'Manager Audit'),('manager_approve', 'Manager Approved')],
        ondelete={'emp_audit': 'set default',
                  'manager_audit': 'set default',
                  'manager_approve': 'set default'})
    

    # @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: not inv.partner_id):
            raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
        if to_open_invoices.filtered(lambda inv: inv.state != 'draft' and inv.purchase_count == 0):
            raise UserError(_("Invoice must be in draft state in order to validate it."))
        if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
            raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
        # Migration Note
        # if to_open_invoices.filtered(lambda inv: not inv.account_id):
        #     raise UserError(_('No account was found to create the invoice, be sure you have installed a chart of account.'))
        to_open_invoices._compute_invoice_date_due()
        # to_open_invoices.action_move_create()
        # return to_open_invoices.invoice_validate()
        return True

    # @api.multi
    def action_send_to_emp_audit(self):
        if self.filtered(lambda inv: inv.state not in ('draft')):
            raise UserError(_('Invoice Must Be In Draft'))
        return self.write({'state': 'emp_audit'})

    # @api.multi
    def action_send_to_manager_audit(self):
        if self.filtered(lambda inv: inv.state not in ('emp_audit')):
            raise UserError(_('Invoice Must Be In Employee Audit .'))
        return self.write({'state': 'manager_audit'})

    # @api.multi
    def action_audit_manger_approve(self):
        if self.filtered(lambda inv: inv.state not in ('manager_audit')):
            raise UserError(_('Invoice Must Be In Manager Audit.'))
        return self.write({'state': 'manager_approve'})

    # @api.multi
    def action_audit_manger_approve_cancel(self):
        if self.filtered(lambda inv: inv.state not in ('manager_approve')):
            raise UserError(_('Invoice Must Be In Manager Approved State.'))
        return self.write({'state': 'draft'})


    # @api.multi
    def action_send_to_manager_return(self):
        if self.filtered(lambda inv: inv.state not in ('emp_audit')):
            raise UserError(_('Invoice Must Be In Employee Audit .'))
        return self.write({'state': 'draft'})

    # @api.multi
    def action_audit_manger_return(self):
        if self.filtered(lambda inv: inv.state not in ('manager_audit')):
            raise UserError(_('Invoice Must Be In Manager Audit.'))
        return self.write({'state': 'emp_audit'})  

    def _prepare_invoice_line_from_po_line(self, line):
        data = super(AccountInvoice,self)._prepare_invoice_line_from_po_line(line)
        if line.product_id.type  == 'service' or (line.product_id.type == 'consu' and not line.product_id.product_tmpl_id.asset_category_id):
            if line.fleet_id_ref:
                if str(line.fleet_id_ref).__contains__('fleet_trailer'):
                    data['trailer_id'] = line.fleet_id_ref.id
                if str(line.fleet_id_ref).__contains__('fleet.vehicle'):
                    data['fleet_id'] = line.fleet_id_ref.id
            data['branch_id'] = line.branches.id
            data['department_id'] = line.department_id.id
            data['account_analytic_id'] = line.account_analytic_id.id
            data['quantity'] = line.product_qty
        else:
            data['branch_id'] = False
            data['department_id'] = False
            data['fleet_id'] = False
            data['trailer_id'] = False
            data['analytic_distribution'] = False
        data['discount'] = line.discount_percent      
        return data


    @api.depends('invoice_line_ids.purchase_line_id.order_id')
    def _compute_purchase(self):
        for inv in self:
            po_orders = self.env['purchase.order']
            for line in inv.invoice_line_ids:
                po_orders |= line.purchase_line_id.order_id
            inv.purchase_ids = po_orders
            inv.purchase_count = len(po_orders)
            
    #This For Make P.R Done  
    @api.model
    def create(self, vals):
        invoice = super(AccountInvoice, self.with_context(mail_create_nolog=True)).create(vals)
        if invoice.purchase_ids:
            if invoice.purchase_ids.filtered(lambda s:s.partner_ref):
                invoice.name = str(invoice.purchase_ids.filtered(lambda s:s.partner_ref).mapped('partner_ref')).replace(']','').replace('[','')
            for order in invoice.purchase_ids:
                order.purchase_transfer.set_to_done()
        return invoice


    def action_view_po(self):
        orders = self.purchase_ids.ids
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders)]
        elif len(orders) == 1:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = orders[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action 

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'



    purchase_count = fields.Integer(compute="_compute_purchase", string='Po Count', copy=False, default=0, store=True)
    is_fleet_operation = fields.Boolean(seting="Is Fleet Operation")
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order' )


    @api.depends('purchase_line_id.order_id')
    def _compute_purchase(self):
        for inv in self:
            po_orders = self.env['purchase.order']
            # for line in inv.invoice_line_ids:
            po_orders |= inv.purchase_line_id.order_id
            # inv.purchase_ids = po_orders
            inv.purchase_count = len(po_orders)

    @api.model
    def create(self,vals):
        if vals.get('move_id'):
            if vals.get('tax_ids') or vals.get('analytic_account_id'):
               invoice_line_id = self.env['account.move.line'].search([('move_id','=',vals.get('move_id')),('account_id','=',vals.get('account_id'))],limit=1)
               vals['trailer_id'] = invoice_line_id.trailer_id.id if invoice_line_id.trailer_id else False              
        res = super(AccountMoveLine,self).create(vals)
        return res
