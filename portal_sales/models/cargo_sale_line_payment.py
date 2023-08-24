# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class BsgVehicleCargoSaleLine(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale_line'
    
    transaction_ids = fields.Many2many('payment.transaction', 'cargo_sales_line_transaction_rel', 'cargo_sale_line_id', 'transaction_id',
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
        amount = self.getting_portal_due_amount()
        if self[0].currency_id.id != self[0].company_id.currency_id.id:
            currency = self[0].company_id.currency_id
        elif any([line.currency_id != currency for line in self]):
            raise ValidationError(_('A transaction can\'t be linked to orders having different currencies.'))

        # Ensure the partner are the same.
        partner = self[0].customer_id
        if any([line.customer_id != partner for line in self]):
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

        vals.update({
            'amount': amount,
            'currency_id': currency.id,
            'partner_id': partner.id,
            'cargo_sale_line_ids': [(6, 0, self.ids)],
        })

        transaction = self.env['payment.transaction'].create(vals)
        # Process directly if payment_token
        if transaction.payment_token_id:
            transaction.s2s_do_transaction()

        return transaction

    
    def payment_action_capture(self):
        self.authorized_transaction_ids.s2s_capture_transaction()

    
    def payment_action_void(self):
        self.authorized_transaction_ids.s2s_void_transaction()

    def _compute_access_url(self):
        super(BsgVehicleCargoSaleLine, self)._compute_access_url()
        for line in self:
            line.access_url = '/my/shipment/line/%s' % (line.id)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    cargo_sale_line_ids = fields.Many2many('bsg_vehicle_cargo_sale_line', 'cargo_sales_line_transaction_rel', 'transaction_id', 'cargo_sale_line_id',
                                   string='Cargo Sale Lines', copy=False, readonly=True)
    cargo_line_ids_nbr = fields.Integer(compute='_compute_cargo_line_ids_nbr', string='# of Cargo Line')
    signature = fields.Char(readonly=True)                               

    @api.depends('cargo_sale_line_ids')
    def _compute_cargo_line_ids_nbr(self):
        for trans in self:
            trans.cargo_line_ids_nbr = len(trans.cargo_sale_line_ids)


    def render_cargo_line_button(self, cargo_line, submit_txt=None, render_values=None):
        currency = cargo_line.currency_id
        amount = cargo_line.getting_portal_due_amount()
        if cargo_line.currency_id.id != cargo_line.company_id.currency_id.id:
            currency = cargo_line.company_id.currency_id

        values = {
            'partner_id': cargo_line.customer_id.id,
            'cargo_sale_id': cargo_line.bsg_cargo_sale_id.id,
        }
        if render_values:
            values.update(render_values)
        return self.acquirer_id.with_context(submit_class='btn btn-primary', submit_txt=submit_txt or _('Pay Now')).sudo().render(
            self.reference,
            amount,
            currency.id,
            values=values,
        )                                   
    
    def action_view_cargo_sale_line(self):
        action = {
            'name': _('Cargo Line Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'target': 'current',
        }
        cargo_line_ids = self.cargo_sale_line_ids.ids
        if len(cargo_line_ids) == 1:
            cargo_line = cargo_line_ids[0]
            action['res_id'] = cargo_line
            action['view_mode'] = 'form'
            form_view = [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', cargo_line_ids)]
        return action


    @api.model
    def _compute_reference_prefix(self, values):
        if values and values.get('invoice_ids'):
            many_list = self.resolve_2many_commands('invoice_ids', values['invoice_ids'], fields=['number'])
            return ','.join(dic['number'] for dic in many_list)
        if values and values.get('cargo_sale_ids'):
            many_list = self.resolve_2many_commands('cargo_sale_ids', values['cargo_sale_ids'], fields=['name'])
            return ','.join(str(dic['name'].replace('*', '')) for dic in many_list)
        if values and values.get('tamara_transaction_ids'):
            many_list = self.resolve_2many_commands('tamara_transaction_ids', values['tamara_transaction_ids'], fields=['name'])
            return ','.join(str(dic['name'].replace('*', '')) for dic in many_list)
        if values and values.get('cargo_sale_line_ids'):
            many_list = self.resolve_2many_commands('cargo_sale_line_ids', values['cargo_sale_line_ids'], fields=['sale_line_rec_name'])
            return ','.join(str(dic['sale_line_rec_name'].replace('*', '')) for dic in many_list)               
        return None

    
    def _payfort_form_validate(self, data):
        res = {}
        res = super(PaymentTransaction, self)._payfort_form_validate(data)
        if data.get('status') == '14':
            if self.cargo_sale_line_ids:     
                _logger.info(
                'Validated payfort Cargo Line confirm %s: '
                'set as done' % (self.reference))
                self.sudo().write({'transaction_reference' : data.get('merchant_reference')})
                self.sudo().write({'app_fortid' : data.get('fort_id')})
                self.cargo_sale_line_ids[0].bsg_cargo_sale_id.sudo().write({
                    'app_payment_method':'credit',
                    'app_paid_amount':data.get('amount'),
                    'app_fortid':data.get('fort_id'),
                    'transaction_reference':data.get('merchant_reference'),
                    })
                invoice_ids = self.env['account.move'].sudo().search([('cargo_sale_id', '=', self.cargo_sale_line_ids[0].bsg_cargo_sale_id.id)])
                if not invoice_ids:
                    self.cargo_sale_line_ids[0].bsg_cargo_sale_id.sudo().confirm_btn()
                self.cargo_sale_line_ids[0].bsg_cargo_sale_id.sudo()._get_invoiced()
                #Add All Open Invoice To Payment Transaction
                self.sudo().write({'invoice_ids': 
                [(6, 0, self.cargo_sale_line_ids.mapped('invoice_line_ids').filtered(lambda s: not s.is_refund and s.move_id.payment_state == 'not_paid').mapped('move_id').ids
                )]})
        return res

    
    def _post_process_after_done(self):
        res = super(PaymentTransaction, self)._post_process_after_done()
        if self.cargo_sale_line_ids:
                if (self.cargo_sale_line_ids[0].bsg_cargo_sale_id.is_from_portal or self.cargo_sale_line_ids[0].bsg_cargo_sale_id.is_from_app) and self.cargo_sale_line_ids[0].bsg_cargo_sale_id.payment_method.payment_type == 'cash':
                    self.cargo_sale_line_ids[0].bsg_cargo_sale_id.sudo().write({'state': 'registered'})
                cargo_line_pay = self.env['account.cargo.line.payment']
                for pay in self.payment_id:
                    pay.sudo().write({'transaction_reference' : self.transaction_reference})
                    pay.sudo().write({'app_fortid' : self.app_fortid})
                    for so_line in self.cargo_sale_line_ids:
                        if (so_line.bsg_cargo_sale_id.is_from_portal or so_line.bsg_cargo_sale_id.is_from_app) and so_line.bsg_cargo_sale_id.payment_method.payment_type == 'cash':
                            so_line.sudo().write({'state': 'registered'})
                        if pay.residual_amount > 0:
                            for inv_line in self.invoice_ids.mapped('invoice_line_ids').filtered(lambda  s: s.cargo_sale_line_id.id == so_line.id):
                                #amount = pay.currency_id._convert(
				                #      pay.residual_amount, inv_line.invoice_id.currency_id, self.env.user.company_id, pay.payment_date or fields.Date.today())
                                cargo_line_pay.with_context({'without_check_amount':True}).sudo().create({
                                'cargo_sale_line_id': inv_line.cargo_sale_line_id.id,
                                'account_invoice_line_id': inv_line.id,
                                'amount': inv_line.price_total,
                                'residual': inv_line.price_total - inv_line.paid_amount,
                                'account_payment_id' : pay.id,
                            })
        return res    
