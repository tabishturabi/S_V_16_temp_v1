from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError,Warning
from odoo.tools import float_compare
import datetime
from odoo.osv import expression
from itertools import groupby
from odoo.addons import decimal_precision as dp
from num2words import num2words


MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': -1,
    'in_invoice': -1,
    'out_refund': 1,
}

# class BsgBranches(models.Model):
#     _inherit = 'bsg_branches.bsg_branches'

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
       
    #     if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
    #         search_id = self.env['bsg_branches.bsg_branches'].search([])
    #         domain = args or []
    #         domain += [
    #          ('id', 'in', search_id.ids)]
    #         rec = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
    #         return self.browse(rec).name_get()
    #     else:
    #         brnch_list = []
    #         for data in self.env['bsg_branches.bsg_branches'].search([('member_ids.user_id','=',self.env.user.id)]):
    #             brnch_list.append(data.id)
    #         domain = args or []
    #         domain += [
    #          ('id', 'in', brnch_list)]
    #         rec = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
    #         return self.browse(rec).name_get()
        # else:
        #     return super(BsgBranches, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


# class CustomerCollection(models.Model):
#     _name = "account.collection"
#     _description = "Account Collection"
#
#     # @api.multi
#     def _paymentcount(self):
#         payment = self.env['account.payment'].search([('coll_ids','=',self.id),('collectionre','=',self.name),('track_coll','=',False)])
#         self.update({
#                 'payment_count': len(set(payment))
#                 })
#         pass
#
#     # @api.multi
#     def _get_journal(self):
#         journal = self.env['account.move'].search([('collection','=',self.name)])
#         self.update({
#                 'journal_count': len(set(journal))
#                 })
#         pass
#     @api.depends('account_invoice')
#     def _amount_all(self):
#         """
#         Compute the total amounts of the SO.
#         """
#         total_amounts = 0.0
#         for invoice in self.account_invoice:
#             total_amounts = total_amounts+invoice.amount_total
#
#         self.update({'amount_total':total_amounts,'amount':total_amounts})
# #         for order in self:
# #             amount_untaxed = amount_tax = 0.0
# #             for line in order.order_line:
# #                 amount_untaxed += line.price_subtotal
# #                 amount_tax += line.price_tax
# #             order.update({
# #                 'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
# #                 'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
# #                 'amount_total': amount_untaxed + amount_tax,
# #             })
#
#     partner_id = fields.Many2one('res.partner', string='Customer ')
#     partner_id1 = fields.Many2one('res.partner', string='Customer')
#     branch_id = fields.Many2one('res.partner', string='Branch Customer')
#     show_branch = fields.Boolean(default=False)
#     name = fields.Char("Name",readonly=True)
#     account_invoice = fields.Many2many('account.move', string='Customer Invoices')
#     amount = fields.Monetary(string='Payment Amount', required=True)
#     currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
#     state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),('posted', 'Posted'),
#                                ('cancelled', 'Cancelled')], default='draft',string="Status")
#
#     due_date = fields.Date("Due Date",store=True)
#
#     invoice_state = fields.Boolean(default=False)
#     date = fields.Date(string='Collection Date', default=fields.Date.context_today, required=True, copy=False)
#     communication = fields.Char(string='Memo')
# #     pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', readonly=True, states={'draft': [('readonly', False)]}, help="Pricelist for current sales order.")
# #     currency_id = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency", readonly=True)
#
#
#     amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always', track_sequence=6)
#     payment_count =  fields.Integer(string='Payment Count',compute='_paymentcount')
#     journal_count = fields.Integer(string='Journal Count',compute='_get_journal')
#
#     @api.onchange('branch_id')
#     def onchange_customer_type(self):
#         if self.branch_id:
#             return {'domain': {
#                 'partner_id1': [('id', 'in', self.branch_id.child_ids.ids)],
#                 }}
#
#     @api.onchange('partner_id1')
#     def getPartnerid(self):
#         if(self.partner_id1):
#             self.partner_id = self.partner_id1
#
#     @api.onchange('branch_id')
#     def getBranch(self):
#         if(self.branch_id):
#             self.partner_id = self.branch_id
#
#     @api.onchange('partner_id')
#     @api.constrains('partner_id')
#     def date_difference(self):
#         if(self.date):
#             date_1 = self.date#datetime.datetime.strptime(self.date, "%m/%d/%y")
#             end_date = date_1 + datetime.timedelta(days=self.partner_id.property_payment_term_id.line_ids.days)
#             self.update({'due_date':end_date})
#
#
#     # @api.multi
#     def action_view_payment(self):
#         payment = self.env['account.payment'].search([('coll_ids','=',self.id),('collectionre','=',self.name),('track_coll','=',False)])
#
#         action = self.env.ref('account.action_account_payments').read()[0]
#         if len(payment) > 1:
#             action['domain'] = [('id', 'in', payment.ids)]
#         elif len(payment) == 1:
#             action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
#             action['res_id'] = payment.ids[0]
#         else:
#             action = {'type': 'ir.actions.act_window_close'}
#         return action
#
#
#     # @api.multi
#     def action_view_journal(self):
#         payment = self.env['account.move'].search([('collection','=',self.name)])
#
#         action = self.env.ref('account.action_move_journal_line').read()[0]
#         if len(payment) > 1:
#             action['domain'] = [('id', 'in', payment.ids)]
#         elif len(payment) == 1:
#             action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
#             action['res_id'] = payment.ids[0]
#         else:
#             action = {'type': 'ir.actions.act_window_close'}
#         return action
#
#     def confirm(self):
#         self.write({'state':'confirm'})
#
#     def posted(self):
#         self.write({'state':'posted'})
#
#
#     def action_draft(self):
#         self.write({'state':'cancelled'})
#
#
#     # @api.multi
#     def unlink(self):
#         if(self.state != 'draft'):
#             raise UserError(_('You can only delete an record if the Customer Voucher is not in draft state.'))
#
#         else:
#             for acc in self.account_invoice:
#                 if (acc.state != 'open'):
#                     raise UserError(_('You can only delete an record if the Customer Vouchers invoices is not in open state.'))
#
#         return super(CustomerCollection, self).unlink()
#
#     def action_reset(self):
#         self.action_resetdraftandreconcile()
#         self.write({'state':'draft'})
#
#     def action_resetdraftandreconcile(self):
#
#         collection = self.env['account.payment'].search([('coll_ids.id','=',self.id)])
#         for sap in collection:
#             splt = sap.communication.split(' ')
#             if(len(splt) > 1):
#                 sap.update({'state':'draft'})
#                 sap.unlink()
#             else:
# #                 for s in sap.move_line_ids:
# #                     s.move_id.update({'state':'draft'})
# #                     s.move_id.reverse_moves()
# # #                     s.move_id.unlink()
# # #                     s.unlink()
# #                 sap.update({'state':'draft'})
# #                 sap.invoice_ids.move_id.update({'state':'draft'})
# # #                 sap.invoice_ids.move_id.unlink()
# # #                 sap.invoice_ids.update({'state':'draft'})
#                 sap.cancel()
#                 sap.invoice_ids._get_payment_info_JSON()
#                 sap.invoice_ids.action_invoice_cancel()
#                 sap.invoice_ids.action_invoice_draft()
# #                 sap.invoice_ids.update({'state':'draft'})
#                 sap.invoice_ids.action_post()
# #                 sap.invoice_ids.update({'state':'open'})
# #                 sap.journal_id.unlink()
# #                 sap.unlink()
#
#         return self.write({'state':'draft'})
#
#     @api.onchange('account_invoice')
#     def sel_invoices(self):
#         if(self.account_invoice):
#             self.invoice_state = True
#         else:
#             self.invoice_state = False
#
#     # @api.multi
#     def cust_select(self):
#         if not self.partner_id:
#             return
#         pickings = self.env['account.move']
#
#         if self.partner_id:
#             for acc in self.account_invoice:
#                 pickings += pickings.search([('id','=',acc.id),('state','!=','paid')])
#         if pickings:
#             action = self.env.ref('account.action_move_out_refund_type').read()[0]
#             if len(pickings) > 1:
#                 action['domain'] = [('id', 'in', list(set(pickings.ids)))]
#             elif len(pickings) == 1:
#                 action['views'] = [(self.env.ref("account.view_move_form").id, 'form')]
#                 action['res_id'] = pickings.ids[0]
#             return action
#         else:
#             return False
#         return True
#
#
#     # @api.multi
#     def action_quotation_send(self):
#         '''
#         This function opens a window to compose an email, with the edi sale template message loaded by default
#         '''
#         self.ensure_one()
#         ir_model_data = self.env['ir.model.data']
#         try:
#             template_id = ir_model_data.get_object_reference('account_invoice', 'email_template_edi_sale')[1]
#         except ValueError:
#             template_id = False
#         try:
#             compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
#         except ValueError:
#             compose_form_id = False
#         ctx = {
#             'default_model': 'account.collection',
#             'default_res_id': self.ids[0],
#             'default_use_template': bool(template_id),
#             'default_template_id': template_id,
#             'default_composition_mode': 'comment',
#             'mark_so_as_sent': True,
#             'custom_layout': "mail.mail_notification_paynow",
#             'proforma': self.env.context.get('proforma', False),
#             'force_email': True
#         }
#         return {
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(compose_form_id, 'form')],
#             'view_id': compose_form_id,
#             'target': 'new',
#             'context': ctx,
#         }
#
#     @api.model
#     def create(self, vals):
#         sequence = self.env.ref('payments_enhanced.ir_sequence_customercollection')#self.env['ir.sequence'].next_by_code('account.payment.customer.invoice')#
#         vals['name'] = sequence.next_by_id()#sequence#sequence.next_by_id()
#         return super(CustomerCollection, self).create(vals)
    

# class account_register_payments(models.TransientModel):
#     # Migration Note
#     # _inherit = "account.register.payments"
#     _inherit = "account.payment.register"
#
#     collectionre = fields.Char("Collection Voucher ref")
#     branch_id = fields.Many2one('res.partner', string='Branch Customer')
#     def _compute_journal_id(self):
#         res = super(account_register_payments, self)._compute_journal_id()
#         active_ids = self._context.get('active_ids')
#         active_model = self._context.get('active_model')
#         if active_model == 'account.collection':
#             collectionss = self.env['account.collection'].browse(active_ids)
#             invoices = self.env['account.move'].browse(collectionss.account_invoice.ids)
#             self.amount = abs(self._compute_payment_amount(invoices))
#         return res

# Migration Note
# class account_abstract_payment(models.AbstractModel):
#     _inherit = "account.abstract.payment"
#
#     @api.model
#     def default_get(self, fields):
#         rec = super(account_abstract_payment, self).default_get(fields)
#         active_ids = self._context.get('active_ids')
#         active_model = self._context.get('active_model')
#         total_amount1 = 0.0
#         # Check for selected invoices ids
#         if active_model == 'account.collection':
#
#
#             collectionss = self.env['account.collection'].browse(active_ids)
#             invoices = self.env['account.move'].browse(collectionss.account_invoice.ids)
#             multi = any(inv.commercial_partner_id != invoices[0].commercial_partner_id
#             or MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type]
#             or inv.account_id != invoices[0].account_id
#             or inv.partner_bank_id != invoices[0].partner_bank_id
#             for inv in invoices)
#
#             currency = invoices[0].currency_id
#
#             total_amount = self._compute_payment_amount(invoices=invoices, currency=currency)
#             if(self._context['active_model'] == 'account.collection' and (self.id == False)):
#                 collection = self.env[self._context['active_model']].search([('id','=',self._context['active_id'])]).name
#                 branch = self.env[self._context['active_model']].search([('id','=',self._context['active_id'])])
#                 rec.update({
# #                         'name':self.env['ir.sequence'].next_by_code('account.payment.customer.invoice'),
#                     'amount': abs(total_amount),
#                     'currency_id': currency.id,
#                     'payment_type': total_amount > 0 and 'inbound' or 'outbound',
#                     'partner_id': False if multi else invoices[0].commercial_partner_id.id,
#                     'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
#                     'communication': ' '.join([ref for ref in collectionss.account_invoice.mapped('reference') if ref]),
#                     'invoice_ids': [(6, 0, collectionss.account_invoice.ids)],
#                     'multi': multi,
#                     'collectionre':collection,
#                     'branch_id':branch.id,
#
#                 })
#             else:
#                 rec.update({
#                     'amount': abs(total_amount1),
#                     'currency_id': currency.id,
#                     'payment_type': total_amount1 > 0 and 'inbound' or 'outbound',
#                     'partner_id': False if multi else invoices[0].commercial_partner_id.id,
#                     'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
#                     'communication': ' '.join([ref for ref in collectionss.account_invoice.mapped('reference') if ref]),
#                     'invoice_ids': [(6, 0, collectionss.account_invoice.ids)],
#                     'multi': multi,
#
#                 })
#         return rec
    # Migration Note
#             for invoices in collectionss.account_invoice:
#             # Check all invoices are open
#                 if any(invoice.state != 'open' for invoice in invoices):
#                     continue
#                 # Check all invoices have the same currency
#                 if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
#                     raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))
#         
#                 # Look if we are mixin multiple commercial_partner or customer invoices with vendor bills
#                 multi = any(inv.commercial_partner_id != invoices[0].commercial_partner_id
#                     or MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type]
#                     or inv.account_id != invoices[0].account_id
#                     or inv.partner_bank_id != invoices[0].partner_bank_id
#                     for inv in invoices)
#         
#                 currency = invoices[0].currency_id
#         
#                 total_amount1 = total_amount1+ self._compute_payment_amount(invoices=invoices, currency=currency)
#                 if(self._context['active_model'] == 'account.collection' and (self.id == False)):
#                     collection = self.env[self._context['active_model']].search([('id','=',self._context['active_id'])]).name
#                     rec.update({
# #                         'name':self.env['ir.sequence'].next_by_code('account.payment.customer.invoice'),
#                         'amount': abs(total_amount1),
#                         'currency_id': currency.id,
#                         'payment_type': total_amount1 > 0 and 'inbound' or 'outbound',
#                         'partner_id': False if multi else invoices[0].commercial_partner_id.id,
#                         'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
#                         'communication': ' '.join([ref for ref in collectionss.account_invoice.mapped('reference') if ref]),
#                         'invoice_ids': [(6, 0, collectionss.account_invoice.ids)],
#                         'multi': multi,
#                         'collectionre':collection
#                     })
#                 else:
#                     rec.update({
#                         'amount': abs(total_amount1),
#                         'currency_id': currency.id,
#                         'payment_type': total_amount1 > 0 and 'inbound' or 'outbound',
#                         'partner_id': False if multi else invoices[0].commercial_partner_id.id,
#                         'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
#                         'communication': ' '.join([ref for ref in collectionss.account_invoice.mapped('reference') if ref]),
#                         'invoice_ids': [(6, 0, collectionss.account_invoice.ids)],
#                         'multi': multi,
#                       
#                     })
#         return rec



class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    branch_id = fields.Many2one('bsg_branches.bsg_branches',string="Branch")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle',string="Truck")
    trailer_id = fields.Many2one('bsg_fleet_trailer_config','Trailer')

# class account_move_line(models.Model):
#     _inherit = "account.move.line"

#     #override to pass the branch filed vlaue
#     @api.multi
#     def create_analytic_lines(self):
#         """ Create analytic items upon validation of an account.move.line having an analytic account or an analytic distribution.
#         """
#         for obj_line in self:
#             if obj_line.payment_id.state == 'draft' or not obj_line.payment_id.state:
#                 for tag in obj_line.analytic_tag_ids.filtered('active_analytic_distribution'):
#                     for distribution in tag.analytic_distribution_ids:
#                         vals_line = obj_line._prepare_analytic_distribution_line(distribution)
#                         if obj_line.invoice_id:
#                             vals_line['branch_id'] = obj_line.invoice_id.loc_from.loc_branch_id.id
#                         elif obj_line.payment_id:
#                             if obj_line.payment_id.branch_ids:
#                                 vals_line['branch_id'] = obj_line.payment_id.branch_ids.id
#                         self.env['account.analytic.line'].create(vals_line)
#                 if obj_line.analytic_account_id:
#                     vals_line = obj_line._prepare_analytic_line()[0]
#                     if obj_line.invoice_id:
#                         vals_line['branch_id'] = obj_line.invoice_id.loc_from.loc_branch_id.id
#                     elif obj_line.payment_id:
#                         if obj_line.payment_id.branch_ids:
#                             vals_line['branch_id'] = obj_line.payment_id.branch_ids.id
#                     self.env['account.analytic.line'].create(vals_line)


#     debit = fields.Float(default=0.0, currency_field='company_currency_id', digits=dp.get_precision('Vouchers'))
#     credit = fields.Float(default=0.0, currency_field='company_currency_id', digits=dp.get_precision('Vouchers'))
#     amount_currency = fields.Float(default=0.0, help="The amount expressed in an optional other currency if it is a multi-currency entry.", digits=dp.get_precision('Vouchers'))
    
#     branch_id = fields.Many2one('res.partner', string='Branch Customer')
#     branch_name = fields.Char('Branch Customer ')

#     department_id = fields.Many2one('hr.department',string="Departments")
#     fleet_vehicle_id = fields.Many2one('fleet.vehicle',string="Truck")

#     #override to used voucher line accont and analytic account
#     @api.model
#     def create(self, vals):
#         if not vals.get('account_id'):
#             raise UserError(_("Be sure you have Defined Account in Partner or Journal"))
#         payment = self.env['account.payment'].search([('id','=',vals.get('payment_id'))])
#         if payment.payment_type == 'inbound':
#             if vals.get('credit') != 0.0 and not vals.get('invoice_id'):
#                 if len(payment.voucher_line_ids) != 0:
#                     vals['account_id'] = payment.voucher_line_ids[0].account_id.id
#                     vals['analytic_account_id'] = payment.voucher_line_ids[0].analytic_id.id
#             if vals.get('debit') != 0.0 and not vals.get('invoice_id'):
#                 if len(payment.voucher_line_ids) != 0:
#                     vals['account_id'] = payment.journal_id.default_account_id.id
#         if vals.get('payment_id'):
#             payment = self.env['account.payment'].search([('id','=',vals.get('payment_id'))])
#             if payment.payment_type == 'outbound':
#                 if vals.get('credit') != 0.0 and not vals.get('invoice_id'):
#                     if len(payment.voucher_line_ids) != 0:
#                         vals['account_id'] = payment.journal_id.default_account_id.id
#                 if vals.get('debit') != 0.0 and not vals.get('invoice_id'):
#                     if len(payment.voucher_line_ids) != 0:
#                         vals['account_id'] = payment.voucher_line_ids[0].account_id.id
#                         vals['analytic_account_id'] = payment.voucher_line_ids[0].analytic_id.id
#         res = super(account_move_line, self).create(vals)        
#         return res

class AccountAccount(models.Model):
    _inherit = "account.account"

    # Migration Test
    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #     args = args or []
    #     domain = []
    #     if name:
    #         domain = ['|', ('code', 'like', name), ('name', operator, name)]
    #         if operator in expression.NEGATIVE_TERM_OPERATORS:
    #             domain = ['&', '!'] + domain[1:]
    #     # if not self._context.get('show_parent_account'):
    #     #     domain += [('user_type_id.name','!=','View')]
    #     account_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
    #     return self.browse(account_ids).name_get()

# class account_move(models.Model):
#     _inherit = "account.move"

#     @api.multi
#     @api.depends('line_ids.debit', 'line_ids.credit')
#     def _amount_compute(self):
#         for move in self:
#             total = 0.0
#             for line in move.line_ids:
#                 total += line.debit
#             move.amount = total

#     collection = fields.Char("Collection Ref")
#     amount = fields.Float(compute='_amount_compute', store=True, digits=dp.get_precision('Vouchers'))

#     @api.multi
#     def action_move_create(self):
#         """ Creates invoice related analytics and financial move lines """
#         account_move = self.env['account.move']
 
#         for inv in self:
#             if not inv.journal_id.sequence_id:
#                 raise UserError(_('Please define sequence on the journal related to this invoice.'))
#             if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
#                 raise UserError(_('Please add at least one invoice line.'))
#             if inv.move_id:
#                 continue
 
 
#             if not inv.date_invoice:
#                 inv.write({'invoice_date': fields.Date.context_today(self)})
#             if not inv.date_due:
#                 inv.write({'date_due': inv.date_invoice})
#             company_currency = inv.company_id.currency_id
 
#             # create move lines (one per invoice line + eventual taxes and analytic lines)
#             iml = inv.invoice_line_move_line_get()
#             iml += inv.tax_line_move_line_get()
 
#             diff_currency = inv.currency_id != company_currency
#             # create one move line for the total and possibly adjust the other lines amount
#             total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)
 
#             name = inv.name or ''
#             if inv.payment_term_id:
#                 totlines = inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
#                 res_amount_currency = total_currency
#                 for i, t in enumerate(totlines):
#                     if inv.currency_id != company_currency:
#                         amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id, inv._get_currency_rate_date() or fields.Date.today())
#                     else:
#                         amount_currency = False
 
#                     # last line: add the diff
#                     res_amount_currency -= amount_currency or 0
#                     if i + 1 == len(totlines):
#                         amount_currency += res_amount_currency
 
#                     iml.append({
#                         'type': 'dest',
#                         'name': name,
#                         'price': t[1],
#                         'account_id': inv.account_id.id,
#                         'date_maturity': t[0],
#                         'amount_currency': diff_currency and amount_currency,
#                         'currency_id': diff_currency and inv.currency_id.id,
#                         'invoice_id': inv.id
#                     })
#             else:
#                 iml.append({
#                     'type': 'dest',
#                     'name': name,
#                     'price': total,
#                     'account_id': inv.account_id.id,
#                     'date_maturity': inv.date_due,
#                     'amount_currency': diff_currency and total_currency,
#                     'currency_id': diff_currency and inv.currency_id.id,
#                     'invoice_id': inv.id
#                 })
#             part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
#             line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
#             line = inv.group_lines(iml, line)
 
#             line = inv.finalize_invoice_move_lines(line)
 
#             date = inv.date or inv.date_invoice
#             move_vals = {
#                 'ref': inv.reference,
#                 'line_ids': line,
#                 'journal_id': inv.journal_id.id,
#                 'date': date,
#                 'narration': inv.comment,
                 
#             }
#             move = account_move.create(move_vals)
#             # Pass invoice in method post: used if you want to get the same
#             # account move reference when creating the same invoice after a cancelled one:
#             move.post(invoice = inv)
#             # make the invoice point to that move
#             vals = {
#                 'move_id': move.id,
#                 'date': date,
#                 'move_name': move.name,
#             }
#             inv.write(vals)
#         return True
    
    
#     
