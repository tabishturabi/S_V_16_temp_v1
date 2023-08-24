from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime
from itertools import groupby
from num2words import num2words


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    credit_collection_id = fields.Many2one('credit.customer.collection')
    credit_collection_ids = fields.Many2many('credit.customer.collection')

    @api.model
    def _get_refund_copy_fields(self):
        result = super(AccountInvoice, self)._get_refund_copy_fields()
        credit_coll_copy_fields = ['credit_collection_id']
        return result + credit_coll_copy_fields

    def unlink(self):
        for inv in self:
            if inv.credit_collection_ids:
                for credit in inv.credit_collection_ids:
                    credit.write({'state': 'confirm'})
        return super(AccountInvoice, self).unlink()


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.move.reversal'

    credit_collection_id = fields.Many2one('credit.customer.collection')

    @api.model
    def default_get(self, fields):
        res = super(AccountInvoiceRefund, self).default_get(fields)
        if self.env.context.get('active_model') == 'bsg_vehicle_cargo_sale':
            move_ids = self.env['bsg_vehicle_cargo_sale'].browse(self.env.context.get('active_ids')).invoice_ids
        else:
            move_ids = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.env['account.move']

        if any(move.state != "posted" for move in move_ids):
            raise UserError(_('You can only reverse posted moves.'))
        if 'company_id' in fields:
            res['company_id'] = move_ids.company_id.id or self.env.company.id
        if 'move_ids' in fields:
            res['move_ids'] = [(6, 0, move_ids.ids)]
        if 'refund_method' in fields:
            if self.env.context.get('active_model') == 'bsg_vehicle_cargo_sale':
                res['refund_method'] = 'cancel'
            else:
                res['refund_method'] = (len(move_ids) > 1 or move_ids.move_type == 'entry') and 'cancel' or 'refund'
        return res
    def reverse_moves(self):
        res = super(AccountInvoiceRefund, self).reverse_moves()
        if self.credit_collection_id:
            self.credit_collection_id.unlink_analytic_line()
            self.credit_collection_id.state = 'cancel'
        return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_credit_customer = fields.Boolean(string="Is Credit Customer", related="partner_types.is_credit_customer",
                                        store=True, track_visibility='onchange')


class CreditCustomerCollection(models.Model):
    _name = "credit.customer.collection"
    _description = "Credit Customer Collection"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    @api.depends('cargo_sale_line_ids.charges', 'cargo_sale_line_ids.other_service_ids.cost',
                 'cargo_sale_line_ids.other_service_ids.tax_amount')
    def _get_total(self):
        self.ensure_one()
        self.amount_total = sum(self.cargo_sale_line_ids.mapped('charges')) + sum(
            self.cargo_sale_line_ids.mapped('other_service_ids.cost')) + sum(
            self.cargo_sale_line_ids.mapped('other_service_ids.tax_amount'))

    def _get_invoice_count(self):
        self.invoice_count = self.env['account.move'].search_count(
            ['|', ('credit_collection_id', '=', self.id), ('credit_collection_ids', 'in', self.ids)])

    name = fields.Char(string="Credit Customer Seq")
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    contract_id = fields.Many2one('bsg_customer_contract',
                                  domain=[('is_invoice_create', '=', False), ('state', '=', 'confirm')], \
                                  track_visibility='always', string='Contract')
    customer_id = fields.Many2one('res.partner', string="Customer",
                                  track_visibility='always')  # , domain=[('is_credit_customer', '=', True)]
    partner_types = fields.Many2one('partner.type', related='customer_id.partner_types', store=True)
    invoice_to = fields.Many2one('res.partner', string="Customer")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.sudo().with_context(
                                      force_company=self.env.user.company_id.id,
                                      company_id=self.env.user.company_id.id).company_id.currency_id)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('invoiced', 'Invoiced'), ('cancel', 'Cancel')], default='draft', string="Status")
    date = fields.Date("Date", default=fields.Date.context_today)
    amount_total = fields.Float(string="Total", compute="_get_total", track_visibility='onchange', store=True)
    is_domain = fields.Boolean(string="Is Domain", track_visibility='always')
    loc_from = fields.Many2one(string="From", comodel_name="bsg_route_waypoints", track_visibility='onchange')
    loc_to = fields.Many2one(string="To", comodel_name="bsg_route_waypoints", track_visibility='onchange')
    from_date = fields.Date(string="From Date")
    to_data = fields.Date(string="To Date")
    trip_number = fields.Many2many('fleet.vehicle.trip')
    cargo_sale_line_ids = fields.Many2many('bsg_vehicle_cargo_sale_line', string="Cargo Sale Line")
    invoice_count = fields.Integer("total invoie", compute="_get_invoice_count")
    internal_note = fields.Text(string="Internal Notes")
    report_branch_wise = fields.Boolean(string="Sort Ship Branch Wise", track_visibility='always')
    report_branch_wise_delivery = fields.Boolean(string="Sort Delivery Branch Wise", track_visibility='always')
    received_date = fields.Date(string="Received Date", track_visibility='always')
    active = fields.Boolean(string='Active', default=True)
    has_line_without_pickup_other_services = fields.Boolean(
        compute='_has_line_without_pickup_and_delivery_other_services_', store=True, compute_sudo=True)
    has_line_without_delivery_other_services = fields.Boolean(
        compute='_has_line_without_pickup_and_delivery_other_services_', store=True, compute_sudo=True)

    @api.depends('cargo_sale_line_ids.has_pickup_other_services', 'cargo_sale_line_ids.has_delivery_other_services')
    def _has_line_without_pickup_and_delivery_other_services_(self):
        for rec in self:
            if rec.cargo_sale_line_ids:
                if not all(rec.cargo_sale_line_ids.mapped('has_pickup_other_services')):
                    rec.has_line_without_pickup_other_services = True
                else:
                    rec.has_line_without_pickup_other_services = False
                if not all(rec.cargo_sale_line_ids.mapped('has_delivery_other_services')):
                    rec.has_line_without_delivery_other_services = True
                else:
                    rec.has_line_without_delivery_other_services = False
            else:
                rec.has_line_without_pickup_other_services = False
                rec.has_line_without_delivery_other_services = False

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
            'default_model': 'credit.customer.collection',
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

    # View So Line

    def view_so_without_pickup_other_services(self, context):
        so_lines = self.cargo_sale_line_ids.filtered(lambda s: not s.has_pickup_other_services)
        action = self.env.ref('bsg_cargo_sale.action_bsg_vehicle_cargo_sale_line').read()[0]
        if len(so_lines) > 1:
            action['domain'] = [('id', 'in', so_lines.ids)]
        elif len(so_lines) == 1:
            action['views'] = [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_form').id, 'form')]
            action['res_id'] = so_lines.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def view_so_without_delivery_other_services(self, context):
        so_lines = self.cargo_sale_line_ids.filtered(lambda s: not s.has_delivery_other_services)
        action = self.env.ref('bsg_cargo_sale.action_bsg_vehicle_cargo_sale_line').read()[0]
        if len(so_lines) > 1:
            action['domain'] = [('id', 'in', so_lines.ids)]
        elif len(so_lines) == 1:
            action['views'] = [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_form').id, 'form')]
            action['res_id'] = so_lines.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

        # for uncheck add_to_cc

    def set_to_uncheck(self):
        if self.cargo_sale_line_ids:
            update_query = "update bsg_vehicle_cargo_sale_line set add_to_cc = False where id in %s;"
            self.env.cr.execute(update_query, (tuple(self.cargo_sale_line_ids.ids),))
        # self.cargo_sale_line_ids.write({'add_to_cc' : False})

    def set_to_draft(self):
        self.set_to_uncheck()
        self.state = 'draft'

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('You Can Delete Record Only In Draft State'))
        return super(CreditCustomerCollection, self).unlink()

    # for unlink Account Analytical line
    def unlink_analytic_line(self):
        lines = self.env['account.analytic.line'].search([('name', '=', self.name)])
        lines.sudo().with_context(force_company=self.env.user.company_id.id,
                                  company_id=self.env.user.company_id.id).unlink()

    # for canceling collection

    def cancel_collection(self):
        if self.state == 'confirm':
            self.set_to_uncheck()
            self.unlink_analytic_line()
            self.state = 'cancel'
        if self.state == 'invoiced':
            inv_id = self.env['account.move'].search([('credit_collection_id', '=', self.id), ('state', '=', 'open')],
                                                     limit=1)
            if inv_id:
                action = self.env.ref('account.action_view_account_move_reversal').read()[0]
                view_id = self.env.ref('account.view_account_move_reversal').id
                context = dict(self._context or {})
                context.update({
                    'default_credit_collection_id': self.id,
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

                # data.action_invoice_cancel()
            # self.set_to_uncheck()
            # self.unlink_analytic_line()
            # self.state = 'cancel'    

    # Constrains METHOD

    @api.constrains('cargo_sale_line_ids')
    def _check_cargo_sale_line_ids(self):
        for data in self.cargo_sale_line_ids:
            search_id = self.search_count([('cargo_sale_line_ids', '=', data.id), ('id', '!=', self.id)])
            if search_id > 0:
                raise UserError(
                    _('Be Sure that you have not same cargo sale line %s with another Record...!' % (
                        data.sale_line_rec_name)),
                )

    # for creating multiple invoice from action
    def create_collection_invoice(self):
        if not self.env.user.has_group('bsg_corporate_invoice_contract.group_cc_create_invoice'):
            raise UserError(_("You have not Access to Create Invoice"))
        if any(state != 'confirm' for state in self.mapped('state')):
            raise UserError(_("Only a Confirm Collection can be invoiced."))
        for data in self:
            data.create_invoice()

    @api.onchange('customer_id')
    def onchange_customer_id(self):
        if self.customer_id:
            return {'domain': {
                'cargo_sale_line_ids': [('customer_id', '=', self.customer_id.id),
                                        ('state', 'not in', ['draft', 'cancel']), ('add_to_cc', '=', False)],
                'invoice_to': [('id', 'in', self.customer_id.child_ids.ids)],
            }}
        # ('fleet_trip_id','!=',False), for not need now as per khaleed told
        # domain="[('customer_id','=',customer_id),('fleet_trip_id','!=',False)]"

    # View Invoices

    def action_view_invoice(self, context):
        invoices = self.env['account.move'].search(
            ['|', ('credit_collection_id', '=', self.id), ('credit_collection_ids', 'in', self.ids)])
        action = self.env.ref('account.action_move_out_refund_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    #  Prepare Invoice

    def _prepare_invoice(self):
        self.ensure_one()
        # journal_id = self.env['account.move'].default_get(['journal_id'])['journal_id']
        journal_id = self.env['account.journal'].search([('is_cc_journal', '=', True)], limit=1)
        if not journal_id:
            raise UserError(_('Please define an Journal related Credit Customer...!'))
        invoice_vals = {
            'name': self.name,
            'ref': self.name,
            'credit_collection_id': self.id,
            'move_type': 'out_invoice',
            'invoice_date': self.date,
            'invoice_date_due': self.received_date,
            # 'account_id': self.customer_id.property_account_receivable_id.id,
            'partner_id': self.invoice_to.id if self.invoice_to else self.customer_id.id,
            'parent_customer_id': self.customer_id.id,
            'partner_shipping_id': self.customer_id.id,
            'journal_id': journal_id.id,
            'currency_id': self.currency_id.id,
            'user_id': self.env.user.id,
        }
        return invoice_vals

    # Before changing in any method pls check where it is being used

    def _prepare_invoice_line(self, inv_id, account_id, name, amount, discount, tax_ids, analytic, product_id):
        print('................._prepare_invoice_line account_id.....................',account_id)
        data = {
            'product_id': product_id,
            'name': str(self.name) + '-' + name,
            'account_id': account_id,
            'price_unit': amount,
            'quantity': 1,
            'discount': discount,
            'move_id': inv_id,
            # 'account_analytic_id': analytic.id if analytic else False,
            'analytic_distribution': {analytic.id: 100},
            # 'invoice_line_tax_ids': [(6, 0, tax_ids.ids)] if tax_ids else [(6, 0, [])]
            'tax_ids': [(6, 0, tax_ids.ids)] if tax_ids else [(6, 0, [])]
        }
        return data

    @api.model
    def _default_inv_line_account_id(self):
        return self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                   company_id=self.env.user.company_id.id).get_param(
            'bsg_cargo_sale.inv_line_account_id')

    def create_invoice(self):
        if not self.env.user.has_group('bsg_corporate_invoice_contract.group_cc_create_invoice'):
            raise UserError(_("You have not Access to Create Invoice"))
        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']
        self.env['account.move'].default_get(['journal_id'])
        if not self.cargo_sale_line_ids:
            raise UserError(
                _('You have no Any Cargo Sale Line Please check ...!'),
            )
        if not self.received_date:
            raise UserError(
                _('Please set Received Date to create invoice ...!'),
            )
        first_line = self.cargo_sale_line_ids[0]
        product_id = first_line.service_type.product_variant_id
        account_id = product_id.property_account_income_id.id if product_id.property_account_income_id else self._default_inv_line_account_id()
        # tax_id =
        # discount = 
        analytic_account_id = first_line.account_id
        unit_charge = 0
        record_list = []
        inv_data = self._prepare_invoice()
        print('................inv_data.............',inv_data)
        invoice = inv_obj.create(inv_data)
        payment_method_id = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')], limit=1)
        invoice.write({'payment_method': payment_method_id.id})
        discount = 0
        untaxed_cargo_sale_line_ids = self.cargo_sale_line_ids.filtered(lambda l: not l.tax_ids)
        taxed_cargo_sale_line_ids = self.cargo_sale_line_ids - untaxed_cargo_sale_line_ids
        if untaxed_cargo_sale_line_ids:
            other_service_untaxed = untaxed_cargo_sale_line_ids.mapped('other_service_ids') and sum(
                untaxed_cargo_sale_line_ids.mapped('other_service_ids.cost')) or 0
            untaxed_charge = sum(untaxed_cargo_sale_line_ids.mapped('total_without_tax')) + other_service_untaxed
            if not account_id:
                raise ValidationError(_("Property income account or defalut invoice line account is not set "))
            invoive_line_data = self._prepare_invoice_line(invoice.id, account_id, product_id.name,
                                                           untaxed_charge, discount, False, analytic_account_id,
                                                           product_id.id)
            data = inv_line_obj.create(invoive_line_data)
        if taxed_cargo_sale_line_ids:
            tax_ids = list(set(taxed_cargo_sale_line_ids.mapped('tax_ids')))
            for tax in tax_ids:
                sale_line_ids = taxed_cargo_sale_line_ids.filtered(lambda ln: tax in ln.tax_ids)
                other_service_untaxed = sale_line_ids.mapped('other_service_ids') and sum(
                    sale_line_ids.mapped('other_service_ids.cost')) or 0
                taxed_charge = sum(sale_line_ids.mapped('total_without_tax')) + other_service_untaxed
                discount = 0
                invoive_line_data = self._prepare_invoice_line(invoice.id, account_id, product_id.name,
                                                               taxed_charge, discount, tax, analytic_account_id,
                                                               product_id.id)
                data = inv_line_obj.create(invoive_line_data)
        invoice._compute_amount()
        invoice.action_post()
        vals = []
        sorted_lines = sorted(self.cargo_sale_line_ids, key=lambda line: line.loc_from.loc_branch_id.id)
        grouped_lines = groupby(sorted_lines, lambda l: (l.loc_from.loc_branch_id.id))
        vlas = []
        name = self.name
        date = self.date
        user_id = self.env.user.id
        partner_id = self.customer_id.id,
        company_id = self.env.user.company_id.id
        for branch, lines in grouped_lines:
            total_without_tax = sum(ln.total_without_tax for ln in lines)
            vals.append({
                'name': name,
                'date': date,
                'account_id': analytic_account_id.id,
                'unit_amount': 1,
                'product_id': product_id.id or False,
                'amount': total_without_tax,
                'general_account_id': account_id,
                'user_id': user_id,
                'partner_id': partner_id,
                'company_id': company_id,
                'branch_id': branch,
            })
        self.env['account.analytic.line'].create(vals)
        # if len(self.cargo_sale_line_ids) > 0:
        #     for rec in self.cargo_sale_line_ids:
        #         rec.cc_create_delivery_history()
        return self.write({'state': 'invoiced'})

        #  Prepare Invoice

    def _prepare_multi_invoice(self):
        # journal_id = self.env['account.move'].default_get(['journal_id'])['journal_id']
        journal_id = self.env['account.journal'].search([('is_cc_journal', '=', True)], limit=1)
        if not journal_id:
            raise UserError(_('Please define an Journal related Credit Customer...!'))
        invoice_vals = {
            'name': ",".join(self.mapped('name')),
            'ref': ",".join(self.mapped('name')),
            'credit_collection_ids': [(6, 0, self.ids)],
            'move_type': 'out_invoice',
            'invoice_date': self[0].date,
            'invoice_date_due': self[0].received_date,
            'account_id': self[0].customer_id.property_account_receivable_id.id,
            'partner_id': self[0].invoice_to.id if self[0].invoice_to else self[0].customer_id.id,
            'parent_customer_id': self[0].customer_id.id,
            'partner_shipping_id': self[0].customer_id.id,
            'journal_id': journal_id.id,
            'currency_id': self[0].currency_id.id,
            'user_id': self.env.user.id,
        }
        return invoice_vals

    def create_multi_invoice(self):
        if not self.env.user.has_group('bsg_corporate_invoice_contract.group_cc_create_invoice'):
            raise UserError(_("You have not Access to Create Invoice"))
        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']
        journal_id = self.env['account.move']._search_default_journal()
        if not all(self.mapped('cargo_sale_line_ids')):
            raise UserError(
                _('You have no Any Cargo Sale Line Please check ...!'),
            )

        if not all(credit.state == 'confirm' for credit in self):
            raise UserError(
                _('All Credit Must be In Confirm State ...!'),
            )
        if not all(credit.customer_id.id == self[0].customer_id.id for credit in self):
            raise UserError(
                _('All Credit Must be With Same Customer ...!'),
            )
        if not all(credit.invoice_to.id == self[0].invoice_to.id for credit in self):
            raise UserError(
                _('All Credit Must be With Same Invoice To Customer ...!'),
            )
        if not all(credit.currency_id.id == self[0].currency_id.id for credit in self):
            raise UserError(
                _('All Credit Must be With Same Currency ...!'),
            )
        if not all(self.mapped('received_date')):
            raise UserError(
                _('Please set Received Date to create invoice ...!'),
            )
        inv_data = self._prepare_multi_invoice()
        invoice = inv_obj.create(inv_data)
        payment_method_id = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')], limit=1)
        invoice.write({'payment_method': payment_method_id.id})
        for rec in self:
            first_line = rec.cargo_sale_line_ids[0]
            product_id = first_line.service_type.product_variant_id
            account_id = product_id.property_account_income_id.id if product_id.property_account_income_id else rec._default_inv_line_account_id()
            # tax_id =
            # discount = 
            analytic_account_id = first_line.account_id
            unit_charge = 0
            record_list = []
            discount = 0
            untaxed_cargo_sale_line_ids = rec.cargo_sale_line_ids.filtered(lambda l: not l.tax_ids)
            taxed_cargo_sale_line_ids = rec.cargo_sale_line_ids - untaxed_cargo_sale_line_ids
            if untaxed_cargo_sale_line_ids:
                untaxed_charge = sum(untaxed_cargo_sale_line_ids.mapped('total_without_tax'))
                invoive_line_data = rec._prepare_invoice_line(invoice.id, account_id, product_id.name,
                                                              untaxed_charge, discount, False, analytic_account_id,
                                                              product_id.id)
                data = inv_line_obj.create(invoive_line_data)
            if taxed_cargo_sale_line_ids:
                tax_ids = list(set(taxed_cargo_sale_line_ids.mapped('tax_ids')))
                for tax in tax_ids:
                    sale_line_ids = taxed_cargo_sale_line_ids.filtered(lambda ln: tax in ln.tax_ids)
                    taxed_charge = sum(sale_line_ids.mapped('total_without_tax'))
                    discount = 0
                    invoive_line_data = rec._prepare_invoice_line(invoice.id, account_id, product_id.name,
                                                                  taxed_charge, discount, tax, analytic_account_id,
                                                                  product_id.id)
                    data = inv_line_obj.create(invoive_line_data)
            vals = []
            sorted_lines = sorted(rec.cargo_sale_line_ids, key=lambda line: line.loc_from.loc_branch_id.id)
            grouped_lines = groupby(sorted_lines, lambda l: (l.loc_from.loc_branch_id.id))
            vlas = []
            name = rec.name
            date = rec.date
            user_id = self.env.user.id
            partner_id = rec.customer_id.id,
            company_id = rec.env.user.company_id.id
            for branch, lines in grouped_lines:
                total_without_tax = sum(ln.total_without_tax for ln in lines)
                vals.append({
                    'name': name,
                    'date': date,
                    'account_id': analytic_account_id.id,
                    'unit_amount': 1,
                    'product_id': product_id.id or False,
                    'amount': total_without_tax,
                    'general_account_id': account_id,
                    'user_id': user_id,
                    'partner_id': partner_id,
                    'company_id': company_id,
                    'branch_id': branch,
                })
            rec.env['account.analytic.line'].create(vals)
            rec.write({'state': 'invoiced'})
        invoice._compute_amount()
        # invoice.action_post()

    def confirm_button(self):
        if not self.cargo_sale_line_ids:
            raise UserError(_("Please At Least Add One Line To Cofirm Order."))
        if not self.name:
            self.name = self.env['ir.sequence'].next_by_code('credit.customer.collection')
        if self.cargo_sale_line_ids:
            update_query = "update bsg_vehicle_cargo_sale_line set add_to_cc = TRUE where id in %s;"
            self.env.cr.execute(update_query, (tuple(self.cargo_sale_line_ids.ids),))
            # self.cargo_sale_line_ids.write({'add_to_cc' : True})
        self.state = 'confirm'

    # @api.model
    # def create(self, vals):
    #     vals['name'] = self.env['ir.sequence'].next_by_code('credit.customer.collection')
    #     return super(CreditCustomerCollection, self).create(vals)

    def write(self, vals):
        CreditCustomer = super(CreditCustomerCollection, self).write(vals)
        if self.cargo_sale_line_ids.ids:
            update_query = "update bsg_vehicle_cargo_sale_line set report_seq = 0 where id not in %s and customer_id = %s and state not in ('draft','cancel') and add_to_cc = FALSE and report_seq != 0;"
            self.env.cr.execute(update_query, [tuple(self.cargo_sale_line_ids.ids), self.customer_id.id])
        # remove_ids = self.env['bsg_vehicle_cargo_sale_line'].search([('id', 'not in', self.cargo_sale_line_ids.ids),('customer_id','=',self.customer_id.id),('state','not in',['draft','cancel']),('add_to_cc','=',False),('report_seq','!=',0)])
        # if remove_ids:
        #     remove_ids.write({'report_seq': 0})
        return CreditCustomer

    @api.onchange('cargo_sale_line_ids')
    def onchange_cargo_sale_line_ids(self):
        if self.cargo_sale_line_ids:
            seq_count = max(self.cargo_sale_line_ids.mapped('report_seq'))
            lines = self.cargo_sale_line_ids.filtered(lambda l: l.report_seq == 0)
            vals_list = []
            if lines:
                ids = lines.ids
                for lid in ids:
                    seq_count = seq_count + 1
                    vals_list.append("(%d, %d)" % (lid, seq_count))
            if vals_list:
                vals = ",".join(vals_list)
                update_query = """update bsg_vehicle_cargo_sale_line 
                set report_seq = so.report_seq
                from
                ( values
                    %s
                ) as so (id, report_seq)
                where bsg_vehicle_cargo_sale_line.id = so.id;
                """ % vals
                self.env.cr.execute(update_query)

            # for line in lines:
            #     seq_count = seq_count + 1
            #     line.write({'report_seq' : seq_count})
            # for check in self.cargo_sale_line_ids:
            #     if check.report_seq == 0:
            #         seq_count = seq_count + 1
            #         check.write({'report_seq' : seq_count})

        remove_ids = self.env['bsg_vehicle_cargo_sale_line'].search(
            [('id', 'not in', self.cargo_sale_line_ids.ids), ('customer_id', '=', self.customer_id.id),
             ('state', 'not in', ['draft', 'cancel']), ('add_to_cc', '=', False), ('report_seq', '!=', 0)])
        if remove_ids:
            update_query = "update bsg_vehicle_cargo_sale_line set report_seq = 0 where id in %s;"
            self.env.cr.execute(update_query, (tuple(remove_ids.ids),))

    def get_arabic_total_word(self, amount):
        word = num2words(float("%.2f" % amount), lang='ar')
        word = word.title()
        warr = str(("%.2f" % amount)).split('.')
        if self.currency_id.name == 'SAR':
            ar = ' ريال' if str(warr[1]) == '00' else ' هلله'
            rword = str(word).replace(',', ' ريال و ') + ar
            # rword = str(rword).replace('ريال و ', 'فاصلة')
        elif self.currency_id.name == 'AED':
            ar = ' درهم' if str(warr[1]) == '00' else ' فلس'
            rword = str(word).replace(',', ' درهم و ') + ar
            # rword = str(rword).replace('ريال و ', 'فاصلة')
        elif self.currency_id.name == 'JOD':
            ar = ' دينار' if str(warr[1]) == '00' else ' فلس'
            rword = str(word).replace(',', ' دينار و ') + ar
            # rword = str(rword).replace('ريال و ', 'فاصلة')
        elif self.currency_id.name == 'OMR':
            ar = ' ريال' if str(warr[1]) == '00' else ' بيسة'
            rword = str(word).replace(',', ' ريال و ') + ar
            # rword = str(rword).replace('ريال و ', 'فاصلة')
        else:
            ar = ' ريال' if str(warr[1]) == '00' else ' هلله'
            rword = str(word).replace(',', ' ريال و ') + ar
            # rword = str(rword).replace('ريال و ', 'فاصلة')
        return rword
