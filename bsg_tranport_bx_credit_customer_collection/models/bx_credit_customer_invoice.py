# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime
from num2words import num2words
from ummalqura.hijri_date import HijriDate


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    bx_credit_collection_id = fields.Many2one('bx.credit.customer.collection')

    @api.model
    def _get_refund_copy_fields(self):
        result = super(AccountInvoice, self)._get_refund_copy_fields()
        bx_coll_copy_fields = ['bx_credit_collection_id']
        return result + bx_coll_copy_fields


class AccountInvoiceRefundBx(models.TransientModel):
    _inherit = 'account.move.reversal'

    def reverse_moves(self):
        bx_obj = self.env['account.move']
        context = dict(self._context or {})
        active_model = self._context.get('active_model', False)
        if active_model == 'account.move' or active_model == 'bx.credit.customer.collection':
            for rec in bx_obj.browse(context.get('active_id')):
                if rec.bx_credit_collection_id:
                    rec.bx_credit_collection_id.state = 'cancel'
        res = super(AccountInvoiceRefundBx, self).reverse_moves()
        return res

    #


#     def invoice_refund(self):
#         res = super(AccountInvoiceRefundBx, self).invoice_refund()
#         bx_obj = self.env['account.move']
#         context = dict(self._context or {})
#         for rec in bx_obj.browse(context.get('active_ids')):
#             print(rec.bx_credit_collection_id)
#             rec.bx_credit_collection_id.state = 'cancel'
#         return res


class BXCreditCustomerCollection(models.Model):
    _name = "bx.credit.customer.collection"
    _description = "Credit Customer Collection"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    # for amout total of all transport line

    @api.depends('transport_management_ids.total_amount')
    def _get_total(self):
        self.ensure_one()
        self.amount_total = sum([data.total_amount for data in self.transport_management_ids])

    # getting number of invoice
    def _get_invoice_count(self):
        self.invoice_count = self.env['account.move'].search_count([('bx_credit_collection_id', '=', self.id)])

    # getting created invoice status
    # def _get_invoice_state(self):
    #    invoice_id = self.env['account.move'].search([('bx_credit_collection_id' ,'=', self.id),('state','=','paid')])
    #    if invoice_id:
    #        self.invoice_status = True
    #    else:
    #        self.invoice_status = False
    is_government = fields.Boolean("Is Government")
    name = fields.Char(string="Credit Customer Seq")
    customer_id = fields.Many2one('res.partner', string="Customer",
                                  track_visibility='always')  # , domain=[('is_credit_customer', '=', True)]
    invoice_to = fields.Many2one('res.partner', string="Customer")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.sudo().with_context(
                                      force_company=self.env.user.company_id.id,
                                      company_id=self.env.user.company_id.id).company_id.currency_id)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('invoiced', 'Invoiced'), ('cancel', 'Cancel')], default='draft', string="Status")
    date = fields.Date("Date", default=fields.Date.context_today)
    amount_total = fields.Float(string="Total", compute="_get_total", track_visibility='onchange', store=True)
    transport_management_ids = fields.Many2many('transport.management.line', string="Transport Management Line")
    invoice_count = fields.Integer("total invoie", compute="_get_invoice_count")
    received_date = fields.Date(string="Received Date")
    internal_note = fields.Text(string="Internal Notes")
    active = fields.Boolean(string='Active', default=True)
    # invoice_status = fields.Boolean("Invoice Status", compute="_get_invoice_state")
    doc_reference_no = fields.Char(string="Doc Reference NO", store=True, compute="_get_doc_reference")
    payment_reference = fields.Char(string="Payment Reference")
    delivery_reference = fields.Char(string="Delivery Reference")

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'bx.credit.customer.collection'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for bx_ccc in self:
            bx_ccc.attachment_number = attachment.get(bx_ccc.id, 0)

    def open_attach_wizard(self):
        view_id = self.env.ref('bsg_tranport_bx_credit_customer_collection.view_attachment_bx_ccc_form').id
        return {
            'name': _('Attachments'),
            'res_model': 'ir.attachment',
            'view_type': 'form',
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id),
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_tranport_bx_credit_customer_collection.action_attachment_bx_ccc_all_access')
        if self.env.user.has_group(
                'bsg_tranport_bx_credit_customer_collection.group_bx_ccc_attachment_delete') or self.env.user._is_admin():
            res['context'] = {'default_res_model': 'bx.credit.customer.collection',
                              'default_res_id': self.env.context.get("active_id"),
                              'create': True,
                              'edit': True, 'delete': True}
        if self.env.user.has_group('bsg_tranport_bx_credit_customer_collection.group_bx_ccc_attachment_view'):
            res['context'] = {'default_res_model': 'bx.credit.customer.collection',
                              'default_res_id': self.env.context.get("active_id"),
                              'create': False,
                              'edit': False, 'delete': False}
        if self.env.user.has_group('bsg_tranport_bx_credit_customer_collection.group_bx_ccc_attachment_add'):
            res['context'] = {'default_res_model': 'bx.credit.customer.collection',
                              'default_res_id': self.env.context.get("active_id"),
                              'create': True,
                              'edit': False, 'delete': False}
        res['domain'] = [('res_model', '=', 'bx.credit.customer.collection'),
                         ('res_id', 'in', [self.env.context.get("active_id")])]
        return res

    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')

    def get_contract(self, obj):
        contract_id = self.env['bsg_customer_contract'].search(
            [('cont_customer', '=', obj.customer_id.id), ('state', '=', 'confirm')], limit=1)
        print('contract_id', contract_id)
        return contract_id

    def get_price(self, obj):
        price = 0
        if obj.transport_management_ids:
            price = sum(obj.transport_management_ids.mapped('price'))
        return price

    def get_tax_amount(self, obj):
        tax_amount = 0
        if obj.transport_management_ids:
            tax_amount = sum(obj.transport_management_ids.mapped('tax_amount'))
        return tax_amount

    def get_arabic_total_word(self, amount):
        word = num2words(float("%.2f" % amount), lang='ar')
        word = word.title()
        warr = str(("%.2f" % amount)).split('.')
        ar = ' ريال' if str(warr[1]) == '00' else ' هلله'
        rword = str(word).replace(',', ' ريال و ') + ar
        rword = str(rword).replace('ريال و ', 'ريال')
        rword = str(rword).replace('فاصلة ', 'ريال ')
        return rword

    def get_contract_date(self, contract_id):
        if contract_id.contract_date:
            contract_date_hijri = HijriDate.get_hijri_date(contract_id.contract_date)
            return contract_date_hijri
        else:
            return False

    @api.depends('invoice_to', 'date')
    def _get_doc_reference(self):
        for rec in self:
            bx_ccc_ids = rec.env['bx.credit.customer.collection'].search(
                [('invoice_to', '=', rec.invoice_to.id), ('customer_id', '=', rec.customer_id.id)])
            bx_ccc_ids = bx_ccc_ids.filtered(lambda r: r.date.year == rec.date.year)
            no_of_partners = len(bx_ccc_ids)
            rec.doc_reference_no = "%s/%04d" % (rec.date.year, no_of_partners)

    # override write method

    def write(self, line_values):
        res = super(BXCreditCustomerCollection, self).write(line_values)
        self._reset_sequence()
        return res

    # for sequnce method

    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.transport_management_ids:
                line.bx_credit_sequnce = current_sequence
                current_sequence += 1

    # for sending mail button

    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = self.env.ref('account.email_template_edi_invoice', False)
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'bx.credit.customer.collection',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            # 'default_template_id': template_id and template_id.id or False,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    # for uncheck add_to_cc
    def set_to_uncheck(self):
        if self.transport_management_ids:
            update_query = "update transport_management_line set add_to_cc = False where id in %s;"
            self.env.cr.execute(update_query, (tuple(self.transport_management_ids.ids),))

    # for setting in draft state

    def set_to_draft(self):
        self.set_to_uncheck()
        self.state = 'draft'

    # for warning message don't allow user to delete it

    def unlink(self):
        if self.state != 'draft':
            warning_obj = self.env['bsg.warning.error'].get_warning('0003')
            raise UserError(warning_obj)
            # raise UserError(_('You Can Delete Record Only In Draft State'))
        return super(BXCreditCustomerCollection, self).unlink()

        # for canceling collection

    # for unlink Account Analytical line
    def unlink_analytic_line(self):
        lines = self.env['account.analytic.line'].search([('name', '=', self.name)])
        lines.sudo().with_context(force_company=self.env.user.company_id.id,
                                  company_id=self.env.user.company_id.id).unlink()

    def cancel_collection(self):
        if self.state == 'confirm':
            self.set_to_uncheck()
            self.unlink_analytic_line()
            self.state = 'cancel'
        if self.state == 'invoiced':
            inv_id = self.env['account.move'].search(
                [('bx_credit_collection_id', '=', self.id), ('state', '=', 'posted')], limit=1)
            for data in inv_id:
                if data.payment_ids:
                    for payment_data in data.payment_ids:
                        payment_data.cancel_payment()
            #                 inv_id.bx_credit_collection_id.state = 'cancel'
            if inv_id:
                action = self.env.ref('account.action_view_account_move_reversal').read()[0]
                view_id = self.env.ref('account.view_account_move_reversal').id
                context = dict(self._context or {})
                context.update({
                    'default_bx_credit_collection_id': self.id,
                    'active_ids': inv_id.id,
                    'active_id': inv_id.id,
                    'default_refund_method': 'cancel',
                })
                action.update({
                    'view_id': view_id,
                    'views': [(view_id, 'form')],
                    'target': 'new',
                    'context': context

                })
                return action

    # Constrains METHOD
    @api.constrains('transport_management_ids')
    def _check_transport_management_ids(self):
        for data in self.transport_management_ids:
            search_id = self.search([('transport_management_ids', '=', data.id), ('id', '!=', self.id)])
            if search_id:
                warning_obj = self.env['bsg.warning.error'].get_warning('0004')
                raise UserError(warning_obj % (data.transport_management))
                # raise UserError(
                #     _('Be Sure that you have not same cargo sale line %s with another Record...!'%(data.sale_line_rec_name)),
                # )

    # for creating multiple invoice from action
    def create_collection_invoice(self):
        for data in self:
            if data.state not in ['confirm']:
                warning_obj = self.env['bsg.warning.error'].get_warning('0005')
                raise UserError(warning_obj)
                # raise UserError(_("Only a Confirm Collection can be invoiced."))
        for data in self:
            if data.state in ['confirm']:
                if self.env.user.has_group('bsg_tranport_bx_credit_customer_collection.group_bx_cc_create_invoice'):
                    data.create_invoice()
                else:
                    warning_obj = self.env['bsg.warning.error'].get_warning('0006')
                    raise UserError(warning_obj)
                    # raise UserError(_("You have not Access to Create Invoice"))

    # for changing the domain
    @api.onchange('customer_id')
    def onchange_customer_id(self):
        if self.customer_id:
            return {'domain': {
                'transport_management_ids': [('customer_id', '=', self.customer_id.id), ('add_to_cc', '=', False),
                                             ('bx_credit_collection_ids', '=', False),
                                             ('transport_management.state', '=', 'done'),
                                             ('payment_method', '=', 'credit')],
                'invoice_to': [('id', 'in', self.customer_id.child_ids.ids)],
            }}

    # View Invoice

    def action_view_invoice(self, context):
        invoice_id = self.env['account.move'].search([('bx_credit_collection_id', '=', self.id)])
        action = self.env.ref('account.action_move_out_refund_type').read()[0]
        if len(invoice_id) > 1:
            action['domain'] = [('id', 'in', invoice_id.ids)]
        elif len(invoice_id) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoice_id.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # register payment

    def register_payment_for_invoice(self):
        invoice_id = self.env['account.move'].search([('bx_credit_collection_id', '=', self.id)])
        view_id = self.env.ref('account.view_account_payment_register_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Name',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.payment',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_payment_type': 'inbound',
                'default_partner_id': self.customer_id.id,
                'default_partner_type': 'customer',
                'default_amount': invoice_id.amount_residual,
                'default_communication': self.name,
                'default_invoice_ids': [(4, invoice_id.id, None)]
            }
        }

    #  Prepare Invoice

    def _prepare_invoice(self):
        self.ensure_one()
        # journal_id = self.env['account.move'].default_get(['journal_id'])['journal_id']
        journal_id = self.env['account.journal'].search([('is_bx_cc_journal', '=', True)], limit=1)
        if not journal_id:
            warning_obj = self.env['bsg.warning.error'].get_warning('0007')
            raise UserError(warning_obj)
            # raise UserError(_('Please define an Journal related Credit Customer...!'))
        invoice_vals = {
            'name': self.name,
            'ref': self.name,
            'bx_credit_collection_id': self.id,
            'move_type': 'out_invoice',
            'invoice_date': self.date,
            'invoice_date_due': self.received_date,
            'account_id': self.customer_id.property_account_receivable_id.id,
            'partner_id': self.invoice_to.id if self.invoice_to else self.customer_id.id,
            'parent_customer_id': self.customer_id.id,
            'partner_shipping_id': self.customer_id.id,
            'journal_id': journal_id.id,
            'currency_id': self.currency_id.id,
            'user_id': self.env.user.id,
        }
        return invoice_vals

    # Before changing in any method pls check where it is being used

    def _prepare_invoice_line(self, inv_id, account_id, name, amount, discount, tax_ids, analytic, product_id, from_id,
                              truk, product_uom_qty, transport_management):
        account_analytic_id = self.env['ir.config_parameter'].sudo().with_context(
            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_invoice_analytic_account_id')
        default_analytic_tag = self.env['ir.config_parameter'].sudo().with_context(
            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
            'transport_management.default_invoice_analytic_tags')
        data = {
            'product_id': product_id,
            'name': str(self.name) + '-' + name,
            'account_id': account_id,
            'price_unit': amount,
            'quantity': product_uom_qty,
            'discount': discount,
            'invoice_id': inv_id,
            'fleet_id': truk.id,
            'branch_id': from_id.loc_branch_id.id if from_id.loc_branch_id else transport_management.form_transport.loc_branch_id.id,
            'account_analytic_id': transport_management.vehicle_type_domain_id.sales_analytic_account.id if transport_management.vehicle_type_domain_id and transport_management.vehicle_type_domain_id.sales_analytic_account else account_analytic_id,
            'analytic_tag_ids': transport_management.vehicle_type_domain_id.sales_analytic_tag and [(6, 0,
                                                                                                     transport_management.vehicle_type_domain_id.sales_analytic_tag.ids)] or default_analytic_tag and [
                                    (6, 0, default_analytic_tag)] or False,
            'invoice_line_tax_ids': [(6, 0, tax_ids.ids)] if tax_ids else [(6, 0, [])]
        }
        return data

    # for creating invoice

    def create_invoice(self):
        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']
        # journal_id = self.env['account.move'].default_get(['journal_id'])['journal_id']
        if not self.transport_management_ids:
            warning_obj = self.env['bsg.warning.error'].get_warning('0008')
            raise UserError(warning_obj)
            # raise UserError(
            # _('You have no Any Tranport Line Please check ...!'),
            # )
        product_id = account_id = invoive_line_data = tax_id = False
        unit_charge = 0
        record_list = []
        inv_data = self._prepare_invoice()
        invoice = inv_obj.create(inv_data)
        payment_method_id = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')], limit=1)
        invoice.write({'payment_method': payment_method_id.id})
        for line in self.transport_management_ids:
            record_list.append(line.id)
            account_id = line.product_id.property_account_income_id.id
            product_id = line.product_id
            product_uom_qty = line.product_uom_qty
            if not account_id:
                warning_obj = self.env['bsg.warning.error'].get_warning('0009')
                raise UserError(warning_obj)
                # raise UserError(
                #     _('Account Invoice Line account is missing!! Please add in configuration'),
                # )
            tax_id = line.tax_ids
            unit_charge = line.price
            name = f'{line.transportation_no} - {product_id.name}'
            invoive_line_data = self._prepare_invoice_line(invoice.id, account_id, product_id.name,
                                                           unit_charge, 0, line.tax_ids, False,
                                                           product_id.id, line.form, line.fleet_vehicle_id,
                                                           product_uom_qty, line.transport_management)
            data = inv_line_obj.create(invoive_line_data)
        invoice._compute_amount()
        invoice.action_post()
        for line in self.env['transport.management.line'].search([('id', 'in', record_list)], order="id asc", ):
            search_id = self.env['account.analytic.line'].search(
                [('name', '=', self.name), ('branch_id', '=', line.form.loc_branch_id.id)])
            if not search_id:
                account_analytic_id = self.env['ir.config_parameter'].sudo().with_context(
                    force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param(
                    'transport_management.default_invoice_analytic_account_id')
                product_id = line.product_id
                data = {
                    'name': self.name,
                    'date': self.date,
                    'account_id': account_analytic_id,
                    'unit_amount': 1,
                    'product_id': product_id.id or False,
                    'amount': line.price,
                    'general_account_id': line.product_id.property_account_income_id.id,
                    'user_id': self.env.user.id,
                    'partner_id': self.customer_id.id,
                    'company_id': self.env.user.company_id.id,
                    'branch_id': line.form.loc_branch_id.id,
                }
                self.env['account.analytic.line'].create(data)
            else:
                search_id.write({'amount': search_id.amount + line.price})
        return self.write({'state': 'invoiced'})

        # when press on confirm button

    def confirm_button(self):
        if not self.transport_management_ids:
            raise UserError(_("Please At Least Add One Line To Cofirm Order."))
        if self.transport_management_ids:
            update_query = "update transport_management_line set add_to_cc = TRUE where id in %s;"
            self.env.cr.execute(update_query, (tuple(self.transport_management_ids.ids),))
        self.state = 'confirm'

    # override create method to passing sequnce on that
    @api.model
    def create(self, vals):
        if not self.env.context.get('is_government', False):
            vals['name'] = self.env['ir.sequence'].next_by_code('bx.credit.customer.collection')
        return super(BXCreditCustomerCollection, self).create(vals)


class IrAttachmentExtCust(models.Model):
    _inherit = "ir.attachment"

    bx_ccc_doc_type = fields.Many2one('documents.type', string="Document Type")
