# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning

_logger = logging.getLogger(__name__)


class ResUser(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        res = super(ResUser, self).create(vals)
        if res.has_group('base.group_portal') and res.partner_id.partner_types:
            res.partner_id.sudo().write({
                'property_account_receivable_id': res.partner_id.sudo().partner_types.accont_rec.id or False,
                'property_account_payable_id': res.partner_id.sudo().partner_types.accont_payable.id or False
            })
        return res


class BsgVehicleCargoSale(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale'

    transaction_ids = fields.Many2many('payment.transaction', 'cargo_sale_transaction_rel', 'cargo_sale_id',
                                       'transaction_id',
                                       string='Transactions', copy=False, readonly=True)
    authorized_transaction_ids = fields.Many2many('payment.transaction', compute='_compute_authorized_transaction_ids',
                                                  string='Authorized Transactions', copy=False, readonly=True)

    @api.depends('transaction_ids')
    def _compute_authorized_transaction_ids(self):
        for trans in self:
            trans.authorized_transaction_ids = trans.transaction_ids.filtered(lambda t: t.state == 'authorized')

    
    def get_portal_last_transaction(self):
        self.ensure_one()
        return self.transaction_ids.get_last_transaction()

    
    def _create_payment_transaction(self, vals):
        '''Similar to self.env['payment.transaction'].create(vals) but the values are filled with the
        current Cargo Sale fields (e.g. the partner or the currency).
        :param vals: The values to create a new payment.transaction.
        :return: The newly created payment.transaction record.
        '''
        # Ensure the currencies are the same.
        currency = self[0].currency_id
        amount = self.geting_portal_order_due_amount()
        if self[0].currency_id.id != self[0].company_id.currency_id.id:
            currency = self[0].company_id.currency_id
        elif any([cargo.currency_id != currency for cargo in self]):
            raise ValidationError(_('A transaction can\'t be linked to orders having different currencies.'))

        # Ensure the partner are the same.
        partner = self[0].customer
        if any([cargo.customer != partner for cargo in self]):
            raise ValidationError(_('A transaction can\'t be linked to orders having different partners.'))

        # Try to retrieve the acquirer. However, fallback to the token's acquirer.
        acquirer_id = vals.get('acquirer_id')
        acquirer = None
        payment_token_id = vals.get('payment_token_id')

        if payment_token_id:
            payment_token = self.env['payment.token'].sudo().browse(payment_token_id)

            # Check payment_token/acquirer matching or take the acquirer from token
            if acquirer_id:
                acquirer = self.env['payment.acquirer'].browse(acquirer_id)
                if payment_token and payment_token.acquirer_id != acquirer:
                    raise ValidationError(_('Invalid token found! Token acquirer %s != %s') % (
                        payment_token.acquirer_id.name, acquirer.name))
                if payment_token and payment_token.partner_id != partner:
                    raise ValidationError(_('Invalid token found! Token partner %s != %s') % (
                        payment_token.partner.name, partner.name))
            else:
                acquirer = payment_token.acquirer_id

        # Check an acquirer is there.
        if not acquirer_id and not acquirer:
            raise ValidationError(_('A payment acquirer is required to create a transaction.'))

        if not acquirer:
            acquirer = self.env['payment.acquirer'].browse(acquirer_id)

        # Check a journal is set on acquirer.
        if not acquirer.journal_id:
            raise ValidationError(_('A journal must be specified of the acquirer %s.' % acquirer.name))

        if not acquirer_id and acquirer:
            vals['acquirer_id'] = acquirer.id
        if acquirer.provider == 'tamara':
            vals.update({
                'is_tamara': True,
                'tamara_reference_id': vals.get('acquirer_reference', False),
                'amount': amount,
                'currency_id': currency.id,
                'partner_id': partner.id,
                'tamara_transaction_ids': [(6, 0, self.ids)],
            })
        else:
            vals.update({
                'amount': amount,
                'currency_id': currency.id,
                'partner_id': partner.id,
                'cargo_sale_ids': [(6, 0, self.ids)],
            })

        transaction = self.env['payment.transaction'].create(vals)
        if transaction.is_tamara and not transaction.tamara_reference_id:
            transaction.write({ 'tamara_reference_id': transaction.acquirer_reference })
            transaction.write({ 'acquirer_reference': False})
        # Process directly if payment_token
        if transaction.payment_token_id:
            transaction.s2s_do_transaction()

        return transaction

    
    def payment_action_capture(self):
        self.authorized_transaction_ids.s2s_capture_transaction()

    
    def payment_action_void(self):
        self.authorized_transaction_ids.s2s_void_transaction()

    def _compute_access_url(self):
        super(BsgVehicleCargoSale, self)._compute_access_url()
        for cargo in self:
            cargo.access_url = '/my/shipments/%s' % (cargo.id)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    cargo_sale_ids = fields.Many2many('bsg_vehicle_cargo_sale', 'cargo_sale_transaction_rel', 'transaction_id',
                                      'cargo_sale_id', string='Cargo Sale', copy=False, readonly=True)
    cargo_ids_nbr = fields.Integer(compute='_compute_cargo_ids_nbr', string='# of Cargo')
    transaction_reference = fields.Char('Transaction Reference', readonly=True)
    app_fortid = fields.Char('Payfort Transaction ID', readonly=True)
    is_refunded = fields.Boolean()

    @api.depends('cargo_sale_ids')
    def _compute_cargo_ids_nbr(self):
        for trans in self:
            trans.cargo_ids_nbr = len(trans.cargo_sale_ids)

    def render_cargo_button(self, cargo, submit_txt=None, render_values=None):
        currency = cargo.currency_id
        amount = cargo.geting_portal_order_due_amount()
        if cargo.currency_id.id != cargo.company_id.currency_id.id:
            currency = cargo.company_id.currency_id

        values = {
            'partner_id': cargo.customer.id,
        }
        if render_values:
            values.update(render_values)
        return self.acquirer_id.with_context(transaction_data=self, cargo=cargo, submit_class='btn btn-primary',
                                             submit_txt=submit_txt or _('Pay Now')).sudo().render(
            self.reference,
            amount,
            currency.id,
            values=values,
        )

    
    def action_view_cargo(self):
        action = {
            'name': _('Cargo Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'bsg_vehicle_cargo_sale',
            'target': 'current',
        }
        cargo_ids = self.cargo_sale_ids.ids
        if len(cargo_ids) == 1:
            cargo = cargo_ids[0]
            action['res_id'] = cargo
            action['view_mode'] = 'form'
            form_view = [(self.env.ref('bsg_cargo_sale.view_vehicle_cargo_sale_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', cargo_ids)]
        return action

    @api.model
    def _compute_reference_prefix(self, values):
        if values and values.get('invoice_ids'):
            many_list = self.resolve_2many_commands('invoice_ids', values['invoice_ids'], fields=['number'])
            return ','.join(dic['number'] for dic in many_list)
        if values and values.get('cargo_sale_ids'):
            many_list = self.resolve_2many_commands('cargo_sale_ids', values['cargo_sale_ids'], fields=['name'])
            return ','.join(str(dic['name'].replace('*', '')) for dic in many_list)
        return None

    
    def _payfort_form_validate(self, data):
        res = {}
        res = super(PaymentTransaction, self)._payfort_form_validate(data)
        if data.get('status') == '14':
            self.sudo().write({'transaction_reference': data.get('merchant_reference')})
            self.sudo().write({'app_fortid': data.get('fort_id')})
            if self.cargo_sale_ids:
                _logger.info(
                    'Validated payfort Cargo confirm %s: '
                    'set as done' % (self.reference))
                self.cargo_sale_ids.sudo().write({
                    'app_payment_method': 'credit',
                    'app_paid_amount': data.get('amount'),
                    'app_fortid': data.get('fort_id'),
                    'transaction_reference': data.get('merchant_reference'),
                })
                try:
                    for so in self.cargo_sale_ids:
                        so.sudo()._amount_all()
                        so.sudo()._amount_so_all()
                    invoice_ids = self.env['account.move'].sudo().search(
                        [('cargo_sale_id', '=', self.cargo_sale_ids[0].id)])
                    if not invoice_ids:
                        self.cargo_sale_ids.sudo().confirm_btn()
                    self.cargo_sale_ids.sudo()._get_invoiced()
                    # Add All Open Invoice To Payment Transaction
                    self.sudo().write({'invoice_ids': [(6, 0, self.cargo_sale_ids[0].order_line_ids.mapped(
                        'invoice_line_ids').filtered(lambda s: not s.is_refund and s.invoice_id.state == 'open').mapped(
                        'invoice_id').ids)]})
                    _logger.info(
                        'Validated payfort Invoice Added confirm %s: '
                        'set as done2' % (self.cargo_sale_ids[0].invoice_ids.ids))
                except UserError as e:
                    self.cargo_sale_ids.sudo().write({'online_pay_error': e.name or e.value})
                except ValidationError as e:
                    self.cargo_sale_ids.sudo().write({'online_pay_error': e.name or e.value})
        return res

    
    def _post_process_after_done(self):
        res = super(PaymentTransaction, self)._post_process_after_done()
        if self.cargo_sale_ids:
            if (self.cargo_sale_ids[0].is_from_portal or self.cargo_sale_ids[0].is_from_app) and self.cargo_sale_ids[
                0].payment_method.payment_type == 'cash':
                self.cargo_sale_ids.sudo().write({'state': 'registered'})
            cargo_line_pay = self.env['account.cargo.line.payment']
            for pay in self.payment_id:
                pay.sudo().write({'transaction_reference': self.transaction_reference})
                pay.sudo().write({'app_fortid': self.app_fortid})
                for so_line in self.cargo_sale_ids.mapped('order_line_ids'):
                    if (self.cargo_sale_ids[0].is_from_portal or self.cargo_sale_ids[0].is_from_app) and \
                            self.cargo_sale_ids[0].payment_method.payment_type == 'cash':
                        so_line.sudo().write({'state': 'registered'})
                    if not so_line.is_paid and pay.residual_amount > 0:
                        for inv_line in self.invoice_ids.mapped('invoice_line_ids').filtered(
                                lambda s: s.cargo_sale_line_id.id == so_line.id):
                            # amount = pay.currency_id._convert(
                            #      pay.residual_amount, inv_line.invoice_id.currency_id, self.env.user.company_id, pay.payment_date or fields.Date.today())
                            cargo_line_pay.with_context({'without_check_amount': True}).sudo().create({
                                'cargo_sale_line_id': inv_line.cargo_sale_line_id.id,
                                'account_invoice_line_id': inv_line.id,
                                'amount': inv_line.price_total,
                                'residual': inv_line.price_total - inv_line.paid_amount,
                                'account_payment_id': pay.id,
                            })
        return res
