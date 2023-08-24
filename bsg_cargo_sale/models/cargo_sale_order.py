# -*- coding: utf-8 -*-
import csv
import os

import math
import re
from collections import defaultdict
from datetime import datetime, date, timedelta
from datetime import timedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import requests
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import logging

_logger = logging.getLogger(__name__)


class BsgVehicleCargoSale(models.Model):
    _name = 'bsg_vehicle_cargo_sale'
    _description = "Cargo Sale"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = "order_date desc"

    # Get default satah account id
    @api.model
    def _default_satah_account_id(self):
        return self.env.user.company_id.satah_account_id.id

    # Get default invoice line account id for cargo sale
    @api.model
    def _default_inv_line_account_id(self):
        return self.env.user.company_id.inv_line_account_id.id

    # Get default option for cargo_service_id
    @api.model
    def _default_cargo_service(self):
        return self.env.user.company_id.cargo_service_id.id

    # Get default option for estimated delivery days
    @api.model
    def _default_estimated_delivery(self):
        return self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                   company_id=self.env.user.company_id.id).get_param(
            'bsg_master_config.est_delivery_selection')

    @api.model
    def _default_get_loc_from(self):
        if self.env.user and self.env.user.user_branch_id:
            loc_from = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                              limit=1)
            if loc_from:
                return loc_from.id
            else:
                return False

    def _get_total_of_demurrae_cost(self):
        for data in self:  # .search([('state','not in',['draft'])]):
            if data.deliver_date:
                delviery_date = datetime.strptime(
                    str(data.deliver_date), '%Y-%m-%d')
                today_date = datetime.strptime(
                    str(fields.Date.today()), '%Y-%m-%d')
                diff = (today_date - delviery_date).days
                demurrage_rules = self.env['demurrage_charges_config'].search([
                ])
                for rule in demurrage_rules:
                    if rule.starting_day_no < diff <= rule.ending_day_no:
                        data.write({'no_of_days': diff, 'current_date': fields.Date.today(),
                                    'without_discount_price': ((rule.chares * diff) * data.total_line)})

    def execute_coupon(self):
        for rec in self:
            coupon = rec.qitaf_coupon
            if coupon:
                lines = rec.order_line_ids.filtered(lambda l: coupon)
                if lines:
                    total_without_tax = sum(lines.mapped('total_without_tax'))
                    qitaf_base_url, qitaf_token, qitaf_user_key = self.get_qitaf_config()
                    headers = {
                        'Authorization': 'Bearer %s' % qitaf_token,
                        'Content-Type': 'application/json', }
                    data = '{ "apiName": "couponExecution", "userKey": "%s", "language": "en", "param": { "coupon": "%s" , "totalAmount": "%s" } }' % (
                    qitaf_user_key, coupon, str(total_without_tax))
                    response = requests.post(qitaf_base_url, headers=headers, data=data)
                    if response.status_code == 200:
                        res = response.json()['response']
                        if res['status'] != 200:
                            raise ValidationError(_(res['result']))
                        total_after_discount = float(res['result']['totalAfterDiscount'])
                        discounted_amount = total_without_tax - total_after_discount
                        self.env['qitaf.copoun.redeem'].sudo().create({
                            'name': coupon,
                            'discount_type': self.qitaf_discount_type,
                            'sale_order_id': self.id,
                            'sale_total_amount': total_without_tax,
                            'sale_discounted_amount': discounted_amount,
                            'total_after_discount': total_after_discount,
                        }
                        )
        return True

    def action_get_qitaf_discount(self):
        if not bool(self.sudo().env['ir.config_parameter'].get_param("qitaf.enable")):
            return
        for rec in self:
            if not rec.qitaf_coupon:
                if not self._context.get('do_not_raise_exception'):
                    raise ValidationError(_("Please type coupon code!"))
                else:
                    return
            if rec.partner_types.id != 5:
                if not self._context.get('do_not_raise_exception'):
                    raise ValidationError(_("Coupon is applicable to cash and POD clinets only!"))
                else:
                    return
            if rec.customer_price_list.id != 1:  # TODO: use pricelist_code
                if not self._context.get('do_not_raise_exception'):
                    raise ValidationError(_("Coupon is applicable for public pricelist only!"))
                else:
                    return
            rec.process_qitaf_coupon()
        return True

    def get_qitaf_config(self):
        qitaf_base_url = self.sudo(
        ).env['ir.config_parameter'].get_param("qitaf.base.url")
        qitaf_token = self.sudo(
        ).env['ir.config_parameter'].get_param("qitaf.token")
        qitaf_user_key = self.sudo(
        ).env['ir.config_parameter'].get_param("qitaf.user.key")
        return qitaf_base_url, qitaf_token, qitaf_user_key

    def process_qitaf_coupon(self):

        coupon = self.qitaf_coupon
        qitaf_base_url, qitaf_token, qitaf_user_key = self.get_qitaf_config()
        headers = {
            'Authorization': 'Bearer %s' % qitaf_token,
            'Content-Type': 'application/json', }

        data = '{ "apiName": "couponDetails", "userKey": "%s", "language": "en", "param": { "coupon": "%s" } }' % (
        qitaf_user_key, coupon)
        response = requests.post(qitaf_base_url, headers=headers, data=data)
        if response.status_code == 200:
            res = response.json()['response']
            if res['status'] == 200:
                if res['result']['discountType'] == 'percent':
                    for line in self.order_line_ids:
                        if line.shipment_type.is_coupon_applicable:
                            line.discount = float(res['result']['discountValue'])
                    self.qitaf_discount_type = 'percent'
                    self.coupon_readonly = True

                else:
                    for line in self.order_line_ids:
                        if line.shipment_type.is_coupon_applicable:
                            line.fixed_discount = float(res['result']['discountValue'])
                    self.qitaf_discount_type = 'fixed'
                    self.coupon_readonly = True

            else:
                if not self._context.get('do_not_raise_exception'):
                    raise ValidationError(_(res['result']))
                else:
                    return

    # @api.model

    def calculated_no_of_days(self):
        if not self.is_demurrage_inovice:
            for data in self:  # .search([('state','not in',['draft'])]):
                if data.deliver_date:
                    delviery_date = datetime.strptime(
                        str(data.deliver_date), '%Y-%m-%d')
                    today_date = datetime.strptime(
                        str(fields.Date.today()), '%Y-%m-%d')
                    diff = ((today_date - delviery_date).days)
                    demurrage_rules = self.env['demurrage_charges_config'].search([
                    ])
                    for rule in demurrage_rules:
                        if rule.starting_day_no < diff <= rule.ending_day_no:
                            data.write({'no_of_days': diff, 'current_date': fields.Date.today(),
                                        'without_discount_price': ((rule.chares * diff) * data.total_line)})

            if self.final_price != 0 and not self.demurrage_check:
                invoices = self.mapped('invoice_ids')
                if not invoices or len(invoices) <= 1:
                    journal_id = self.env['account.move']._search_default_journal()
                    if not journal_id:
                        raise UserError(
                            _('Please define an accounting sales journal for this company.'))
                    invoice_vals = {
                        'name': '',
                        'ref': self.name,
                        'cargo_sale_id': self.id,
                        'move_type': 'out_invoice',
                        'account_id': self.customer.property_account_receivable_id.id,
                        'partner_id': self.cargo_invoice_to.id or self.customer.id,
                        'parent_customer_id': self.customer.id,
                        'partner_shipping_id': self.customer.id,
                        'journal_id': journal_id,
                        'currency_id': self.currency_id.id,
                        'comment': self.note,
                        'user_id': self.user_id and self.user_id.id,
                    }
                    invocie_id = self.env['account.move'].create(
                        invoice_vals)

                    product_id = self.env['product.product'].search(
                        [('name', '=', 'Demurrage Cost')], limit=1)

                    if not product_id:
                        product_id = self.env['product.product'].create(
                            {'name': 'Demurrage Cost', 'type': 'service'})

                    invoice_line_vals = {
                        'name': product_id.name,
                        'product_id': product_id.id,
                        'account_id': product_id.categ_id.property_account_income_categ_id.id,
                        'price_unit': self.without_discount_price,
                        'quantity': 1,
                        'discount': self.discount_price,
                        'tax_ids': [(6, 0, product_id.taxes_id.ids)],
                        'invoice_id': invocie_id.id,
                    }
                    invoice_line_ids = self.env['account.move.line'].create(
                        invoice_line_vals)
                    invocie_id._compute_amount()
                    self.write({'is_demurrage_inovice': True})
            self.demurrage_check = True
        else:
            raise UserError(
                _('Already Demurrage Cost Calculated and invoice is also created'))

    # 
    @api.depends('order_line_ids')
    def _get_total_line(self):
        self.total_line = len(self.order_line_ids)

    # Total Discount
    # 
    @api.depends('order_line_ids.charges', 'order_line_ids.discount', 'order_line_ids.tax_amount', 'satah_line.price')
    def _amount_all(self):
        amount_discount = amount_total = toal_tax = 0.0
        for line in self.order_line_ids:
            # for need of hamdan to cancel not reflect on cargo sale amount
            if line.state != 'cancel':
                amount_discount += line.discount_price
                amount_total += line.charges
                toal_tax += line.tax_amount
            # if self.is_satah:
            # 	for satah in self.satah_line:
            # 		amount_total += satah.price
            self.update({
                'total_discount': amount_discount,
                # 'total_amount': round(abs(amount_total)),#khaleed need dicsussion with therir managemetn
                'total_amount': amount_total,
                'tax_amount_total': toal_tax,
            })

    # Getting Total so amount
    # 
    @api.depends('total_service_amount', 'total_amount')
    def _amount_so_all(self):
        for rec in self:
            rec.update({
                'total_so_amount': (rec.total_amount + rec.total_service_amount)})

    # for getting total without tax amount
    # 
    @api.depends('tax_amount_total', 'total_amount')
    def _get_total_witout_tax(self):
        for rec in self:
            rec.total_without_tax = rec.total_amount - rec.tax_amount_total

    # for getting Paid amount and net Amount
    # 
    @api.depends('invoice_ids')
    def _get_net_paid_amount(self):
        self.paid_amount = self.net_amount = 0
        if self.payment_method.payment_type in ['cash', 'pod']:
            if self.invoice_ids:
                self.paid_amount = (self.total_amount -
                                    self.invoice_ids[0].amount_residual)
                self.net_amount = self.invoice_ids[0].amount_residual
            else:
                self.net_amount = self.total_amount
        elif self.payment_method.payment_type == 'credit':
            if self.state not in ['draft', 'cancel']:
                customer_collection_ids = self.env['credit.customer.collection'].search(
                    [('cargo_sale_line_ids.bsg_cargo_sale_id', '=', self.id)])
                if customer_collection_ids and sum(customer_collection_ids.mapped('invoice_count')) != 0:
                    invoice_ids = self.env['account.move'].search(
                        [('credit_collection_id', 'in', customer_collection_ids.ids), ('state', '!=', 'cancel')])

                    if not invoice_ids or not all(state == 'paid' for state in invoice_ids.mapped('state')):
                        self.paid_amount = 0
                        self.net_amount = self.total_amount
                    else:
                        self.paid_amount = self.total_amount
                        self.net_amount = 0
            else:
                self.net_amount = self.total_amount

    # Total of all other Service products
    # 
    @api.depends('other_service_line_ids.cost')
    def _amount_service_all(self):
        service_tax = service_total = 0.0
        for line in self.other_service_line_ids:
            service_tax += line.tax_amount
            service_total += line.cost
        self.total_service_tax = service_tax
        self.total_service_amount = (service_total + service_tax)
        self.total_service_without_tax = (service_total)

    # 
    @api.depends('order_line_ids.type')
    def _check_satash_type(self):
        for rec in self:
            rec.is_satah = False
            if rec.order_line_ids:
                for data in rec.order_line_ids:
                    if data.type != 'none':
                        rec.is_satah = True
                    else:
                        rec.is_satah = False

    #
    @api.depends('without_discount_price', 'discount_price')
    def _calcualte_final_price(self):
        for rec in self:
            rec.final_price = 0
            if rec.discount_price and rec.discount_price > 0:
                rec.final_price = rec.without_discount_price - \
                                   (rec.without_discount_price * rec.discount_price / 100)
            else:
                rec.final_price = rec.without_discount_price

    # Get Invoice
    # 
    @api.depends('name')
    def _get_invoiced(self):
        for rec in self:
            invoice_ids = self.env['account.move'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                       company_id=self.env.user.company_id.id).search(
                [('cargo_sale_id', '=', rec.id), ('wizard_cargo_sale_id', '=', False), ('cargo_sale_line_id', '=', False),
                 ('is_other_service_invoice', '=', False)])
            rec.update({
                'invoice_count': len(set(invoice_ids.ids)),
                'invoice_ids': invoice_ids.ids,
                # 'invoice_status': invoice_status
            })

    # Get Invoice
    # 
    def _get_refund_invoices(self):
        # invoice_ids = self.env['account.move'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('wizard_cargo_sale_id', '=', self.id)])
        invoice_ids = False
        if self.invoice_ids:
            invoice_ids = self.env['account.move'].search(
                ['|', ('reversed_entry_id', '=', self.invoice_ids[0].id), ('wizard_cargo_sale_id', '=', self.id)])
        else:
            invoice_ids = self.env['account.move'].search(
                [('wizard_cargo_sale_id', '=', self.id)])

        self.update({
            'refund_invoice_count': len(set(invoice_ids.ids)),
            'reversal_move_id': invoice_ids.ids,
        })

    # Get Other Service Invoice
    # 
    def _get_other_service_count(self):
        other_service_invoice = self.env['account.move'].search(
            ['|','&',('invoice_origin', '=', self.name), ('is_other_service_invoice', '=', True),
            '&',('reversed_entry_id.invoice_origin', '=', self.name), ('reversed_entry_id.is_other_service_invoice', '=', True)
            ])
        self.other_service_invoice_count = len(other_service_invoice)

    # Get Other Service Invoice Status
    # 
    def _other_service_invoice_state(self):
        other_service_invoice = self.env['account.move'].search(
            [('ref', '=', self.name), ('is_other_service_invoice', '=', True)], limit=1)
        if other_service_invoice.payment_state == 'paid':
            self.other_service_status = True
        else:
            self.other_service_status = False

    # getting return invoice state
    # 
    def _get_return_validate(self):
        if not self.reversal_move_id:
            self.is_return_validate = False
        for data in self.reversal_move_id:
            if data.payment_state == 'paid':
                self.is_return_validate = True
            else:
                self.is_return_validate = False

    # 
    def _get_validate_payment(self):
        self.is_validate = False
        for data in self.invoice_ids:
            if data.payment_state == 'paid':
                self.is_validate = True
            else:
                self.is_validate = False

    @api.depends('order_line_ids')
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in sale order lines.
        Then we add 1 to this value for the next sequence.
        This value is given to the context of the o2m field in the view.
        So when we create new sale order lines, the sequence is automatically
        added as :  max_sequence + 1
        """
        for sale in self:
            sale.max_line_sequence = (
                    max(sale.mapped('order_line_ids.sequence') or [0]) + 1)

    # def _get_customer_type(self):
    # 	if self.env.user.has_group('bsg_cargo_sale.group_create_agreement_for_corporate') and self.env.user.has_group('bsg_cargo_sale.group_create_agreement_for_individual'):
    # 		list_of_customer_type = [('individual', 'عمـيل أفــراد'),('corporate', 'عمـيل شــركات')]
    # 		return list_of_customer_type
    # 	elif self.env.user.has_group('bsg_cargo_sale.group_create_agreement_for_corporate'):
    # 		list_of_customer_type = [('corporate', 'عمـيل شــركات')]
    # 		return list_of_customer_type
    # 	elif self.env.user.has_group('bsg_cargo_sale.group_create_agreement_for_individual'):
    # 		list_of_customer_type = [('individual', 'عمـيل أفــراد')]
    # 		return list_of_customer_type
    # 	else:
    # 		list_of_customer_type = [('individual', 'عمـيل أفــراد'),('corporate', 'عمـيل شــركات')]
    # 		return list_of_customer_type

    max_line_sequence = fields.Integer(string='Max sequence in lines',
                                       compute='_compute_max_line_sequence',
                                       store=True)
    partner_types = fields.Many2one("partner.type",
                                    track_visibility='onchange',
                                    string="Partner Type",
                                    domain="['|','|',('is_construction','=',True),('is_custoemer','=',True),('is_dealer','=',True)]")
    name = fields.Char(string="Name")
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('registered', 'Registered'),
            ('confirm', 'Confrim'),
            ('pod', 'Payment on Delivery'),
            ('done', 'Paid'),
            ('awaiting', 'Awaiting Return'),
            ('shipped', 'Shipped'),
            ('on_transit', 'On Transit'),
            ('Delivered', 'Delivered'),
            ('unplanned', 'Unplanned'), ('cancel_request', 'Cancel Request'),
            ('cancel', 'Declined')
        ], string='State', default="draft", track_visibility=True, )
    active = fields.Boolean(
        string="Active", track_visibility=True, default=True)
    cargo_sale_type = fields.Selection(string="Cargo Sale Type", selection=[
        ('local', 'Local'),
        ('international', 'International')], default="local")
    customer_type = fields.Selection(
        related="partner_types.pricing_type", string='Pricing Type', track_visibility=True)
    # customer_type = fields.Selection(_get_customer_type, string='Customer Type', track_visibility=True)
    tax_amount_total = fields.Monetary(string='Tax Amount', store=True, compute='_amount_all',
                                       track_visibility='onchange', digits=dp.get_precision('Cargo Sale'),
                                       track_sequence=6)
    total_without_tax = fields.Float(string="Total without Tax", compute="_get_total_witout_tax",
                                     digits=dp.get_precision('Cargo Sale'), track_visibility=True, )
    net_amount = fields.Float(string="Net Amount", compute="_get_net_paid_amount",
                              digits=dp.get_precision('Cargo Sale'), track_visibility=True, )
    paid_amount = fields.Float(string="Paid Amount", compute="_get_net_paid_amount",
                               digits=dp.get_precision('Cargo Sale'), track_visibility=True, )
    customer = fields.Many2one(
        string="Customer", comodel_name="res.partner", track_visibility='onchange',
        domain="[('id', 'in', customer_domain_ids)]")
    partner_id = fields.Many2one('res.partner', related="customer")
    customer_number = fields.Char(
        related="customer.customer_number", store=True)
    customer_price_list = fields.Many2one(
        'product.pricelist', string="Pricelist")
    is_attachment_required = fields.Boolean("Is attachment Required", compute="compute_is_attachment_required",
                                            store=True)
    cooperate_customer = fields.Many2one(string="Cooperate Customer", comodel_name="res.partner",
                                         track_visibility='onchange', domain="[('id', 'in', customer_domain_ids)]")
    is_validate = fields.Boolean(
        string="Is Payment", compute="_get_validate_payment")
    is_return_validate = fields.Boolean(
        string="Is Payment", compute="_get_return_validate")
    # cooperate_customer_price_list = fields.Many2one(related="cooperate_customer.property_product_pricelist",store=True)
    shipment_type = fields.Selection(string="Shipment Type", selection=[
        ('return', 'Round Trip'),
        ('oneway', 'Oneway')
    ], default="oneway", track_visibility='onchange')
    # payment_method = fields.Many2one('cargo_payment_method', string="Payment Method", required=True, default=lambda self: self.env['cargo_payment_method'].search([('payment_method_name','in',['Cash'])], limit=1).id)
    payment_method = fields.Many2one(
        'cargo_payment_method', string="Payment Method", track_visibility='onchange')
    payment_type = fields.Selection(
        [
            ('cash', 'Cash'),
            ('credit', 'Credit'),
            ('pod', 'Payment On Delivery'),
            ('bank', 'Bank Transfer'),
        ], string='Payment type', related="payment_method.payment_type", track_visibility='onchange')
    payment_method_code = fields.Selection(
        [
            ('cash', 'Cash'),
            ('credit', 'Credit'),
            ('pod', 'Payment On Delivery'),
            ('bank', 'Bank Transfer'),
        ], string='Payment Method Code', related="payment_method.payment_type", track_visibility='onchange')

    allow_contract = fields.Boolean(string="Proceed W/O Contract", related="cooperate_customer.is_dealer", store=True,
                                    track_visibility='onchange')
    is_credit_customer = fields.Boolean(string="Is Credit Customer", related="partner_types.is_credit_customer",
                                        store=True, track_visibility='onchange')
    is_for_credit_attch = fields.Boolean(string="Is Credit For Attach")
    is_credit_customer_parnter = fields.Boolean(string="Is Credit Customer")

    loc_from = fields.Many2one(string="From", comodel_name="bsg_route_waypoints", default=_default_get_loc_from,
                               track_visibility='onchange')
    loc_from_branch_id = fields.Many2one(
        related="loc_from.loc_branch_id", store=True, track_visibility='onchange')
    loc_to = fields.Many2one(
        string="To", comodel_name="bsg_route_waypoints", track_visibility='onchange')
    return_loc_from = fields.Many2one(string="Return From", comodel_name="bsg_route_waypoints",
                                      track_visibility='onchange', store=True)
    return_loc_to = fields.Many2one(string="Return To", comodel_name="bsg_route_waypoints", track_visibility='onchange',
                                    store=True)
    order_date = fields.Datetime(
        string="Order Date", default=lambda self: fields.datetime.now())
    user_id = fields.Many2one(
        string="Current User", comodel_name="res.users", default=lambda self: self.env.user)
    deliver_date = fields.Date(string="Expected Delivery Date")
    expected_delivery_days = fields.Integer(
        string="Expected Delivery Days", compute="_compute_days_frm_dates")
    expected_hours = fields.Float(
        string="Expected No of Hours", compute="_compute_days_frm_dates")
    est_max_no_delivery_days = fields.Integer(string='Est Max No of Days', compute="_compute_days_frm_dates")
    est_max_no_hours = fields.Float(string='Est Max No of Hours', compute="_compute_days_frm_dates")
    actual_deliver_date = fields.Date(string="Actual Delivery Date")
    route = fields.Many2one(string="Route", comodel_name="bsg_route")
    order_line_ids = fields.One2many(string="Order Line", comodel_name="bsg_vehicle_cargo_sale_line",
                                     inverse_name="bsg_cargo_sale_id", ondelete='cascade')
    other_service_line_ids = fields.One2many(string="Order Service Line", comodel_name="other_service_items",
                                             inverse_name="cargo_sale_id", ondelete='cascade')
    return_order_line_ids = fields.One2many(string="Return Line", comodel_name="bsg_vehicle_cargo_sale_line",
                                            inverse_name="bsg_cargo_return_sale_id", ondelete='cascade')

    invoice_ids = fields.Many2many("account.move", string='Invoices', compute="_get_invoiced", readonly=True,
                                   copy=False)
    invoice_count = fields.Integer(
        string='Invoice Count', compute='_get_invoiced', readonly=True)

    reversal_move_id = fields.Many2many("account.move", string='Refund Invoices', compute="_get_refund_invoices",
                                          readonly=True,
                                          copy=False)
    demurrage_invoice_id = fields.Many2one(
        "account.move", string="Demurrage Invoice")
    refund_invoice_count = fields.Integer(
        string='Refund Invoice Count', compute='_get_refund_invoices', readonly=True)

    total_discount = fields.Monetary(string='Total Discount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='onchange', track_sequence=6,
                                     digits=dp.get_precision('Cargo Sale'))
    total_amount = fields.Monetary(string='Total Amount', store=True, readonly=True, compute='_amount_all',
                                   track_visibility='onchange', track_sequence=6, digits=dp.get_precision('Cargo Sale'))
    total_so_amount = fields.Monetary(string='Total So Amount', readonly=True, compute='_amount_so_all',
                                      track_visibility='onchange', track_sequence=6,
                                      digits=dp.get_precision('Cargo Sale'))
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    cargo_invoice_to = fields.Many2one(
        string="Invoice To", comodel_name="res.partner", track_visibility=True)

    note = fields.Text('Description')
    total_line = fields.Integer(string="Total line", compute="_get_total_line")
    customer_contract = fields.Many2one(
        string="Select Contract", comodel_name="bsg_customer_contract")
    same_as_customer = fields.Boolean(string="Same as Customer ?")
    as_customer_id = fields.Boolean(string="Same as Other Customer ?")

    sender_name = fields.Char(string="Sender Name")
    sender_type = fields.Selection(string="Sender Type", selection=[
        ('1', 'Saudi'),
        ('2', 'Non-Saudi'),
        ('3', 'Corporate'),
    ])
    sender_nationality = fields.Many2one(
        string="Sender Nationality", comodel_name="res.country")
    sender_id_type = fields.Selection(string="Sender ID Type", selection=[
        ('saudi_id_card', 'Saudi ID Card'),
        ('iqama', 'Iqama'),
        ('gcc_national', 'GCC National'),
        ('passport', 'Passport'),
        ('other', 'Other'),
    ])
    sender_id_card_no = fields.Char(string="Sender ID Card No")
    sender_visa_no = fields.Char(string="Sender Visa No")
    same_as_sender = fields.Boolean(string="Same as Sender ?")
    sender_mob_country_code = fields.Selection([('966', '+966'), ('971', '+971'), ('962', '+962'), ('968', '+968')],
                                               string='Sender Mobile Code', default='966')
    sender_mob_no = fields.Char(
        string="Sender Mobile No", track_visibility=True, search='_search_sender_mob_no')
    owner_name = fields.Char(string="Owner Name")
    owner_type = fields.Selection(string="Owner Type", selection=[
        ('1', 'Saudi'),
        ('2', 'Non-Saudi'),
        ('3', 'Corporate'),
    ])
    owner_nationality = fields.Many2one(
        string="Owner Nationality", comodel_name="res.country")
    owner_id_type = fields.Selection(string="Owner ID Type", selection=[
        ('saudi_id_card', 'Saudi ID Card'),
        ('iqama', 'Iqama'),
        ('gcc_national', 'GCC National'),
        ('passport', 'Passport'),
        ('other', 'Other'),
    ])
    owner_id_card_no = fields.Char(string="Owner ID Card No")
    owner_visa_no = fields.Char(string="Owner Visa No")
    same_as_owner = fields.Boolean(string="Same as Owner ?")
    receiver_name = fields.Char(string="Receiver Name")
    receiver_type = fields.Selection(string="Receiver Type", selection=[
        ('1', 'Saudi'),
        ('2', 'Non-Saudi'),
        ('3', 'Corporate'),
    ])
    receiver_nationality = fields.Many2one(
        string="Receiver Nationality", comodel_name="res.country")
    receiver_id_type = fields.Selection(string="Receiver ID Type", selection=[
        ('saudi_id_card', 'Saudi ID Card'),
        ('iqama', 'Iqama'),
        ('gcc_national', 'GCC National'),
        ('passport', 'Passport'),
        ('other', 'Other'),
    ])
    receiver_id_card_no = fields.Char(string="Receiver ID Card No")
    receiver_visa_no = fields.Char(string="Receiver Visa No")
    receiver_mob_country_code = fields.Selection([('966', '+966'), ('971', '+971'), ('962', '+962'), ('968', '+968')],
                                                 string='Receiver Mobile Code', default='966')
    receiver_mob_no = fields.Char(
        string="Receiver Mobile No", track_visibility=True, search='_search_receiver_mob_no')
    is_satah = fields.Boolean('Add Satah', compute="_check_satash_type")
    satah_line = fields.One2many(
        "satah.vehicale.list", "cargo_sale_id", string="Satah Vehicale")
    branch_sr_no = fields.Char(string="Branch Sr", default="02")

    # demurrage_charge
    is_demurrage_inovice = fields.Boolean(string="Deamurrate Invoice")
    no_of_days = fields.Integer(string="No of Days", readonly="1")
    current_date = fields.Date(string="Today Date", readonly="1")
    without_discount_price = fields.Float(
        string='Total without Discount', digits=dp.get_precision('Cargo Sale'))
    discount_price = fields.Float(
        string="Discount", digits=dp.get_precision('Cargo Sale'))
    final_price = fields.Float(
        string="Total", compute='_calcualte_final_price', digits=dp.get_precision('Cargo Sale'))
    barcode = fields.Char(string="Barcode")
    demurrage_check = fields.Boolean(
        string='Demurrage Calculated',
    )
    account_id = fields.Many2one(string="Analytic Account",
                                 comodel_name="account.analytic.account",
                                 related="loc_from.loc_branch_id.account_analytic_id",
                                 store=True)
    allow_change_loc = fields.Boolean(
        string='Change Location',
    )
    no_of_copy = fields.Integer(string='No of Copy')

    total_service_tax = fields.Monetary(string='Total Service Tax', compute='_amount_service_all',
                                        track_visibility='onchange')
    total_service_without_tax = fields.Monetary(string='Total Service Without Tax', compute='_amount_service_all',
                                                track_visibility='onchange')
    total_service_amount = fields.Monetary(string='Total Service Amount', compute='_amount_service_all',
                                           track_visibility='onchange')
    attachment_id = fields.Many2many('ir.attachment', string="Attachment")
    is_other_service_invoice = fields.Boolean(
        string="Is Other Service Invoice")
    other_service_invoice_count = fields.Integer(
        string="Other Serice count", compute="_get_other_service_count")
    other_service_status = fields.Boolean(
        compute="_other_service_invoice_state")
    is_construction = fields.Boolean(
        string="IS Construction", related="partner_types.is_construction", store=True)
    return_intiated = fields.Boolean(string="Return Initiated", default=False)

    # restict for user creating invoice multiple time
    is_invoice_created = fields.Boolean(
        string="IS Invoice Created", copy=False)
    is_to_other_customer = fields.Boolean(
        string="Creating Invoice to Other Customer")
    other_customer_id = fields.Many2one(
        'res.partner', string="Other Customer ID")
    is_from_app = fields.Boolean('Is From App', readonly=True)
    is_from_contract_api = fields.Boolean('Is From Contract API', readonly=True)
    is_return_so = fields.Boolean()
    return_so_id = fields.Many2one(
        'bsg_vehicle_cargo_sale', string='Return Sale Order', readonly=True)
    is_old_order = fields.Boolean(default=True)
    no_line_to_return = fields.Boolean(
        'Has No Line To Return', compute='_compute_no_line_to_return', store=True)
    company_currency_id = fields.Many2one(string="Company Currency", comodel_name="res.currency",
                                          default=lambda self: self.env.user.company_id.currency_id.id)
    is_currency_diff = fields.Boolean(
        compute='compute_currency_diff', store=True)
    qitaf_coupon = fields.Char('Coupon Code')
    qitaf_discount_type = fields.Selection([('fixed', 'Fixed'), ('percent', 'Percent')], 'Copoun Discount Type')
    coupon_readonly = fields.Boolean()
    recieved_from_customer_date = fields.Datetime('Date Recieved From Customer')
    warning_expired = fields.Boolean(string='Warning Expired')
    warning_to_be_expired = fields.Boolean(string='Warning to be Expired')
    shipment_date = fields.Datetime(default=fields.Datetime.now, copy=False)
    is_from_portal = fields.Boolean()
    is_invoice = fields.Boolean(string='IS Invoice', compute="get_is_invoice")
    baptizing_number = fields.Integer(string="Baptizing Number")
    is_support_team = fields.Boolean(string="Is Support Team", compute="_get_user_access")
    so_receiver_info_update_check = fields.Boolean(string="Receiver Info Update", compute="_get_receiver_check")

    def _get_receiver_check(self):
        if not self.so_receiver_info_update_check:
            if self.order_line_ids:
                for line in self.order_line_ids:
                    if line.state not in ['draft', 'registered', 'confirm']:
                        self.so_receiver_info_update_check = True
                        break

    def _get_user_access(self):
        if self.env.user.has_group('bsg_support_team.group_update_so_line'):
            self.is_support_team = True
        else:
            self.is_support_team = False

    @api.model
    def _search_sender_mob_no(self, operator, operand):
        # Users search uning mobile with/out 0 prefix
        if operator == '=' and operand:
            return [('sender_mob_no', 'in', [operand, operand[-9:]])]
        return [('sender_mob_no', operator, operand)]

    @api.depends('invoice_ids')
    def get_is_invoice(self):
        if self.invoice_ids:
            self.is_invoice = True
        else:
            self.is_invoice = False

    def print_tax_invoice(self):
        if self.sudo().invoice_ids:
            return self.sudo().env.ref('qr_code_invoice_app.account_invoices_zakat_tax_authority').report_action(
                self.sudo().invoice_ids[0])
        else:
            raise UserError('This order has no Invoice')

    @api.model
    def _search_receiver_mob_no(self, operator, operand):
        # Users search uning mobile with/out 0 prefix
        if operator == '=' and operand:
            return [('receiver_mob_no', 'in', [operand, operand[-9:]])]
        return [('receiver_mob_no', operator, operand)]

    @api.depends('company_currency_id', 'currency_id')
    def compute_currency_diff(self):
        for rec in self:
            rec.is_currency_diff = False
            if rec.company_currency_id and rec.currency_id:
                if rec.company_currency_id.id != rec.currency_id.id:
                    rec.is_currency_diff = True
                else:
                    rec.is_currency_diff = False
            else:
                rec.is_currency_diff = False

    @api.depends('order_line_ids.is_return_canceled', 'order_line_ids.return_intiated')
    def _compute_no_line_to_return(self):
        for rec in self:
            rec.no_line_to_return = False
            if rec.shipment_type == 'return':
                if all([line.is_return_canceled or line.return_intiated for line in rec.order_line_ids]):
                    rec.no_line_to_return = True

    @api.depends('customer_price_list', 'order_line_ids', 'order_line_ids.customer_price_list')
    def compute_is_attachment_required(self):
        for rec in self:
            rec.is_attachment_required = False
            if rec.customer_price_list and rec.customer_price_list.is_attachment_required:
                rec.is_attachment_required = True
            else:
                val = any(rec.order_line_ids.mapped(
                    'customer_price_list.is_attachment_required'))
                rec.is_attachment_required = val

    @api.onchange('loc_from', 'loc_to', 'partner_types', 'order_date', 'shipment_type')
    def _onchange_sale_price_list_domain(self):
        self.order_line_ids._onchange_order_price_list_domain()

    @api.onchange('order_line_ids', 'is_credit_customer', 'cooperate_customer', 'customer_type', 'shipment_type')
    def _onchange_order_payment_method_domain(self):
        if self.shipment_type == 'return':
            self.payment_method = self.env['cargo_payment_method'].search(
                [('payment_type', '=', 'cash')], limit=1).id
            return {'domain': {'payment_method': [('payment_type', 'in', ['cash'])]}}
        if self.is_credit_customer:
            return {'domain': {'payment_method': [('payment_type', 'in', ['credit', 'cash', 'pod'])]}}
        if self.order_line_ids:
            config_year = self.env['ir.config_parameter'].sudo(
            ).get_param('bsg_master_config.car_year_id')
            for rec in self.order_line_ids:
                if (rec.customer_price_list.is_cash) or (
                        config_year and rec.year.car_year_name < self.env['bsg.car.year'].sudo().with_context(
                    force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(
                    int(config_year)).car_year_name):
                    self.payment_method = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')],
                                                                                  limit=1).id
                    return {'domain': {'payment_method': [('payment_type', '=', 'cash')]}}
        if self.cooperate_customer.is_dealer:
            return {'domain': {'payment_method': [('payment_type', 'in', ['cash', 'pod'])]}}
        if self.customer_type == 'corporate':
            return {'domain': {'payment_method': [('payment_type', 'in', ['cash', 'credit', 'pod'])]}}
        if self.customer_type == 'individual':
            return {'domain': {'payment_method': [('payment_type', 'in', ['cash', 'pod'])]}}
        else:
            return {'domain': {'payment_method': [('payment_type', 'in', ['cash', 'pod'])]}}

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain == [['cargo_sale_type', '=', 'local'], ['payment_method.payment_type', '=', 'pod'],
                      ['create_uid', '=', self.env.user.id]]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                domain = ['|', '|', '|',
                          ('loc_from.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('order_line_ids.pickup_loc.loc_branch_id',
                           '=', self.env.user.user_branch_id.id),
                          ('order_line_ids.loc_from.loc_branch_id',
                           '=', self.env.user.user_branch_id.id),
                          ('loc_to.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('cargo_sale_type', '=',
                           'local'), ('payment_method.payment_type', '=', 'pod'),
                          ('create_uid', '=', self.env.user.id)]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                domain = [('cargo_sale_type', '=', 'local'),
                          ('payment_method.payment_type', '=', 'pod')]
        elif domain == [['cargo_sale_type', '=', 'local'], ['payment_method.payment_type', '=', 'pod']]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                domain = ['|', '|', '|',
                          ('loc_from.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('order_line_ids.pickup_loc.loc_branch_id',
                           '=', self.env.user.user_branch_id.id),
                          ('order_line_ids.loc_from.loc_branch_id',
                           '=', self.env.user.user_branch_id.id),
                          ('loc_to.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('cargo_sale_type', '=', 'local'), ('payment_method.payment_type', '=', 'pod')]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                domain = [('cargo_sale_type', '=', 'local'),
                          ('payment_method.payment_type', '=', 'pod')]
        elif domain == [['cargo_sale_type', '=', 'local'], ['create_uid', '=', self.env.user.id]]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                domain = ['|', '|', '|',
                          ('loc_from.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('order_line_ids.pickup_loc.loc_branch_id',
                           '=', self.env.user.user_branch_id.id),
                          ('order_line_ids.loc_from.loc_branch_id',
                           '=', self.env.user.user_branch_id.id),
                          ('loc_to.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('cargo_sale_type', '=', 'local'), ('create_uid', '=', self.env.user.id)]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                domain = [('cargo_sale_type', '=', 'local')]
        elif domain == [['cargo_sale_type', '=', 'local']]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                domain = ['|', '|', '|',
                          ('loc_from.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('order_line_ids.pickup_loc.loc_branch_id',
                           '=', self.env.user.user_branch_id.id),
                          ('order_line_ids.loc_from.loc_branch_id',
                           '=', self.env.user.user_branch_id.id),
                          ('loc_to.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('cargo_sale_type', '=', 'local')]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                domain = [('cargo_sale_type', '=', 'local')]
        elif domain == [['cargo_sale_type', '=', 'international'], ['create_uid', '=', self.env.user.id]]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                domain = ['|', '|', '|',
                          ('loc_from.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('order_line_ids.pickup_loc.loc_branch_id',
                           '=', self.env.user.user_branch_id.id),
                          ('order_line_ids.loc_from.loc_branch_id',
                           '=', self.env.user.user_branch_id.id),
                          ('loc_to.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('cargo_sale_type', '=', 'international'), ('create_uid', '=', self.env.user.id)]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                domain = [('cargo_sale_type', '=', 'international')]
        elif domain == [['cargo_sale_type', '=', 'international']]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                domain = ['|', '|', '|',
                          ('loc_from.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('order_line_ids.pickup_loc.loc_branch_id',
                           '=', self.env.user.user_branch_id.id),
                          ('order_line_ids.loc_from.loc_branch_id',
                           '=', self.env.user.user_branch_id.id),
                          ('loc_to.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('cargo_sale_type', '=', 'international')]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                domain = [('cargo_sale_type', '=', 'international')]
        res = super(BsgVehicleCargoSale, self).search_read(
            domain, fields, offset, limit, order)
        return res

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        if args == [['cargo_sale_type', '=', 'local'], ['payment_method.payment_type', '=', 'pod'],
                    ['create_uid', '=', self.env.user.id]]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                args = ['|', '|', '|',
                        ('loc_from.loc_branch_id', '=',
                         self.env.user.user_branch_id.id),
                        ('order_line_ids.pickup_loc.loc_branch_id',
                         '=', self.env.user.user_branch_id.id),
                        ('order_line_ids.loc_from.loc_branch_id',
                         '=', self.env.user.user_branch_id.id),
                        ('loc_to.loc_branch_id', '=',
                         self.env.user.user_branch_id.id),
                        ('cargo_sale_type', '=',
                         'local'), ('payment_method.payment_type', '=', 'pod'),
                        ('create_uid', '=', self.env.user.id)]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                args = [('cargo_sale_type', '=', 'local'),
                        ('payment_method.payment_type', '=', 'pod')]
        elif args == [['cargo_sale_type', '=', 'local'], ['payment_method.payment_type', '=', 'pod']]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                args = ['|', '|', '|',
                        ('loc_from.loc_branch_id', '=',
                         self.env.user.user_branch_id.id),
                        ('order_line_ids.pickup_loc.loc_branch_id',
                         '=', self.env.user.user_branch_id.id),
                        ('order_line_ids.loc_from.loc_branch_id',
                         '=', self.env.user.user_branch_id.id),
                        ('loc_to.loc_branch_id', '=',
                         self.env.user.user_branch_id.id),
                        ('cargo_sale_type', '=', 'local'), ('payment_method.payment_type', '=', 'pod')]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                args = [('cargo_sale_type', '=', 'local'),
                        ('payment_method.payment_type', '=', 'pod')]
        elif args == [['cargo_sale_type', '=', 'local'], ['create_uid', '=', self.env.user.id]]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                args = ['|', '|', '|',
                        ('loc_from.loc_branch_id', '=',
                         self.env.user.user_branch_id.id),
                        ('order_line_ids.pickup_loc.loc_branch_id',
                         '=', self.env.user.user_branch_id.id),
                        ('order_line_ids.loc_from.loc_branch_id',
                         '=', self.env.user.user_branch_id.id),
                        ('loc_to.loc_branch_id', '=',
                         self.env.user.user_branch_id.id),
                        ('cargo_sale_type', '=', 'local'), ('create_uid', '=', self.env.user.id)]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                args = [('cargo_sale_type', '=', 'local')]
        elif args == [['cargo_sale_type', '=', 'local']]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                args = ['|', '|', '|',
                        ('loc_from.loc_branch_id', '=',
                         self.env.user.user_branch_id.id),
                        ('order_line_ids.pickup_loc.loc_branch_id',
                         '=', self.env.user.user_branch_id.id),
                        ('order_line_ids.loc_from.loc_branch_id',
                         '=', self.env.user.user_branch_id.id),
                        ('loc_to.loc_branch_id', '=',
                         self.env.user.user_branch_id.id),
                        ('cargo_sale_type', '=', 'local')]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                args = [('cargo_sale_type', '=', 'local')]
        elif args == [['cargo_sale_type', '=', 'international'], ['create_uid', '=', self.env.user.id]]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                args = ['|', '|', '|',
                        ('loc_from.loc_branch_id', '=',
                         self.env.user.user_branch_id.id),
                        ('order_line_ids.pickup_loc.loc_branch_id',
                         '=', self.env.user.user_branch_id.id),
                        ('order_line_ids.loc_from.loc_branch_id',
                         '=', self.env.user.user_branch_id.id),
                        ('loc_to.loc_branch_id', '=',
                         self.env.user.user_branch_id.id),
                        ('cargo_sale_type', '=', 'international'), ('create_uid', '=', self.env.user.id)]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                args = [('cargo_sale_type', '=', 'international')]
        elif args == [['cargo_sale_type', '=', 'international']]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                args = ['|', '|', '|',
                        ('loc_from.loc_branch_id', '=',
                         self.env.user.user_branch_id.id),
                        ('order_line_ids.pickup_loc.loc_branch_id',
                         '=', self.env.user.user_branch_id.id),
                        ('order_line_ids.loc_from.loc_branch_id',
                         '=', self.env.user.user_branch_id.id),
                        ('loc_to.loc_branch_id', '=',
                         self.env.user.user_branch_id.id),
                        ('cargo_sale_type', '=', 'international')]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                args = [('cargo_sale_type', '=', 'international')]
        else:
            # if found the duplicate record
            args_list = []
            for data in args:
                if data not in args_list or data == '|':
                    args_list.append(data)
            return super(BsgVehicleCargoSale, self)._search(args_list, offset, limit, order, count=count,
                                                            access_rights_uid=access_rights_uid)
        return super(BsgVehicleCargoSale, self)._search(args, offset, limit, order, count=count,
                                                        access_rights_uid=access_rights_uid)

    '''@api.model
    def _cron_update_so_cancel(self):
        for data in self.search([('state', '=', 'confirm')], limit=50):
            for cargo_line_data in data.order_line_ids.filtered(lambda l: l.state == 'draft'):
                data.write({'state': 'cancel'})
        for data in self.search([('state', '=', 'draft')], limit=50):
            cargo_config = self.env.ref(
                'bsg_cargo_sale.cargo_sale_order_config_data').name
            if fields.datetime.now() >= data.order_date:
                data.write({'state': 'cancel'})
            if date.today() == data.order_date.date() and int(cargo_config) <= data.order_date.hour:
                data.write({'state': 'cancel'})'''

    @api.model
    def _cron_update_so_cancel(self):
        # for data in self.search([('state','=','confirm')],limit=50):
        # 	for cargo_line_data in data.order_line_ids.filtered(lambda l: l.state == 'draft'):
        # 		data.write({'state' : 'cancel'})
        cargo_config = self.env['cargo_sale_order_config'].sudo().with_context(
            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
            [], limit=1).name
        for data in self.search([('state', '=', 'draft')], limit=50):
            # if fields.datetime.now() >= data.order_date:
            #	data.write({'state' : 'cancel'})
            diff = date.today() - data.order_date.date()
            hour = diff.total_seconds() / 3600.0

            if int(cargo_config) <= hour:
                data.write({'state': 'cancel'})

    @api.model
    def _cron_update_so_price(self, so_id):
        if so_id:
            sale_order = self.env['bsg_vehicle_cargo_sale'].browse(so_id)
            for so_line in sale_order.order_line_ids:
                so_line._onchange_shipment_type()

    # COMPUTE METHODS
    # 
    @api.depends('deliver_date')
    def _compute_days_frm_dates(self):
        """
        Calculation of days between two dates
        """
        for rec in self:
            rec.est_max_no_hours = rec.expected_delivery_days = rec.est_max_no_delivery_days = rec.expected_hours = 0
            if self.loc_from and self.loc_to:
                record = self.env['bsg.estimated.delivery.days'].search(
                    [('loc_from_id', '=', rec.loc_from.id), ('loc_to_id', '=', rec.loc_to.id)], limit=1)
                if record:
                    rec.expected_delivery_days = record.est_no_delivery_days
                    rec.expected_hours = record.est_no_hours
                    rec.est_max_no_delivery_days = record.est_max_no_delivery_days
                    rec.est_max_no_hours = record.est_max_no_hours

    # 
    # @api.depends('loc_to', 'loc_from')
    # def _get_second_leg_loc(self):
    # 	if self.cargo_sale_type == 'international' and self.loc_from.loc_branch_id.branch_operation == 'international':
    # 		self.currency_id = self.loc_from.loc_branch_id.currency_id.id
    # 	if self.shipment_type == 'return':
    # 		self.return_loc_to = self.loc_from
    # 		self.return_loc_from = self.loc_to
    # 	for line in self.order_line_ids:
    # 		line._onchange_service_price()

    # CONSTRAIS METHOD
    # Attachment Validation Checks
    # 
    @api.constrains('attachment_id', 'is_to_other_customer', 'is_attachment_required')
    def _check_attachment_id(self):
        validate_attachment_required = self.env['ir.config_parameter'].sudo(
        ).get_param('validate_attachment_required')
        _30_days_ago = (
                    datetime.strptime(str(fields.Date.today()), DEFAULT_SERVER_DATE_FORMAT) - timedelta(days=30)).date()
        if not self.is_from_portal and self.create_date.date() > _30_days_ago:
            if validate_attachment_required == '0':
                return True
            else:
                for rec in self:
                    if rec.is_to_other_customer and rec.is_credit_customer:
                        if not rec.attachment_id:
                            raise UserError(
                                _('Please Attach some Attachment ...!'),
                            )
                    if rec.allow_contract or rec.is_construction:
                        if not rec.attachment_id:
                            raise UserError(
                                _('Please Attach some Attachment ...!'),
                            )
                    if rec.is_attachment_required and not rec.attachment_id:
                        raise UserError(_('Please Attach some Attachment ...!'), )

    # CONSTRAIS METHOD
    # Sender Validation Checks
    # 
    @api.constrains('sender_id_card_no', 'sender_id_type')
    def _check_sender_id(self):
        if not self.is_from_app and self.sender_id_card_no and self.sender_type == '2' and self.sender_id_type == 'iqama':
            match = re.match(r'2[0-9]{9}', self.sender_id_card_no)
            if match is None or len(str(self.sender_id_card_no)) != 10:
                raise UserError(
                    _('Sender ID no must be start from 2 and must have 10 digits.'),
                )
        if not self.is_from_app and self.sender_id_card_no and self.sender_type == '1' and self.sender_id_type == 'saudi_id_card':
            match = re.match(r'1[0-9]{9}', self.sender_id_card_no)
            if match is None or len(str(self.sender_id_card_no)) != 10:
                raise UserError(
                    _('Sender ID no must be start from 1 and must have 10 digits.'),
                )

    # 
    @api.constrains('sender_visa_no')
    def _check_sender_visa_no(self):
        if self.sender_visa_no:
            match = re.match(r'[a-zA-Z0-9]', self.sender_visa_no)
            if match is None or len(self.sender_visa_no) > 15:
                raise UserError(
                    _('Sender Visa/Passport no must contain Alphanumeric and 15 digits!'),
                )

    # Owner Validation Checks
    # 
    @api.constrains('owner_id_card_no', 'owner_id_type')
    def _check_owner_id_card_no(self):
        if not self.is_from_app and self.owner_id_card_no and self.owner_type == '2' and self.owner_id_type == 'iqama':
            match = re.match(r'2[0-9]{9}', self.owner_id_card_no)
            if match is None or len(str(self.owner_id_card_no)) != 10:
                raise UserError(
                    _('Owner ID no must be start from 2 and must have 10 digits.'),
                )
        if not self.is_from_app and self.owner_id_card_no and self.owner_type == '1' and self.owner_id_type == 'saudi_id_card':
            match = re.match(r'1[0-9]{9}', self.owner_id_card_no)
            if match is None or len(str(self.owner_id_card_no)) != 10:
                raise UserError(
                    _('Owner ID no must be start from 1 and must have 10 digits.'),
                )

    # 
    @api.constrains('owner_visa_no')
    def _check_owner_visa_no(self):
        if not self.is_from_app:
            if self.owner_visa_no:
                match = re.match(r'[a-zA-Z0-9]', self.owner_visa_no)
                if match is None or len(self.owner_visa_no) > 15:
                    raise UserError(
                        _('Owner Visa/Passport no must contain Alphanumeric and 15 digits!'),
                    )

    # Reciever Validation Checks
    # 
    @api.constrains('receiver_id_card_no', 'receiver_id_type')
    def _check_receiver_id_card_no(self):
        if not self.is_from_app and self.receiver_id_card_no and self.receiver_type == '2' and self.receiver_id_type == 'iqama':
            match = re.match(r'2[0-9]{9}', self.receiver_id_card_no)
            if match is None or len(str(self.receiver_id_card_no)) != 10:
                raise UserError(
                    _('Receiver ID no must be start from 2 and must have 10 digits.'),
                )
        if not self.is_from_app and self.receiver_id_card_no and self.receiver_type == '1' and self.receiver_id_type == 'saudi_id_card':
            match = re.match(r'1[0-9]{9}', self.receiver_id_card_no)
            if match is None or len(str(self.receiver_id_card_no)) != 10:
                raise UserError(
                    _('Receiver ID no must be start from 1 and must have 10 digits.'),
                )

    # 
    @api.constrains('receiver_visa_no')
    def _check_receiver_visa_no(self):
        if not self.is_from_app:
            if self.receiver_visa_no:
                match = re.match(r'[a-zA-Z0-9]', self.receiver_visa_no)
                if match is None or len(self.receiver_visa_no) > 15:
                    raise UserError(
                        _('Receiver Visa/Passport no must contain Alphanumeric and 15 digits!'),
                    )

    # 
    @api.constrains('receiver_mob_no')
    def _check_receiver_mob_no(self):
        if not self.is_from_app:
            if self.receiver_mob_no:
                if not self.receiver_mob_no.isdigit() or len(self.receiver_mob_no) < 8:
                    raise UserError(
                        _('Reciever Mobile No is not correct ..!'),
                    )

    # 
    # @api.constrains('customer_contract')
    # def _check_contract_remaing_amt(self):
    # 	if self.customer_contract:
    # 		if self.customer_contract.remainder_amt < self.total_amount:
    # 			raise UserError(_('Contract Remaining Balance is less then actual amt'),)

    @api.onchange('is_to_other_customer')
    def _onchange_for_attach(self):
        if self.is_to_other_customer and self.is_credit_customer:
            self.is_for_credit_attch = True
        else:
            self.is_for_credit_attch = False

    # Onchange Methods
    # on true get following filed from res.partner
    customer_domain_ids = fields.Many2many(
        'res.partner',
        compute='_compute_customer_domain_ids',
    )
    @api.depends('partner_types', 'customer_type')
    def _compute_customer_domain_ids(self):
        for m in self:
            if m.customer_type == 'individual':
                domain = [('is_company','=',False),('customer_type','=',m.customer_type),('block_list','!=',True)]
                m.customer_domain_ids = self.env['res.partner'].search(domain)
            else:
                domain = [('is_company','=',True),('customer_type','=',m.customer_type),('block_list','!=',True)]
                m.customer_domain_ids = self.env['res.partner'].search(domain)

    @api.onchange('partner_types')
    def _oncahnge_loc_from_to(self):
        if self.partner_types and self.partner_types.is_credit_customer:
            self.is_credit_customer_parnter = True
        # mr Khaleed want to complete tehse things
        if self.partner_types:
            self.payment_method = False
        # if self.customer_type == 'individual':
        #     return {'domain': {'customer': [('partner_types', '=', self.partner_types.id), ('block_list', '=', True)]}}
        # else:
        #     return {'domain': {'cooperate_customer': [('partner_types', '=', self.partner_types.id), ('block_list', '=', True)]}}

    @api.onchange('same_as_customer')
    def _onchange_same_as_customer(self):
        if self.same_as_customer:
            self.sender_name = self.customer.name
            self.sender_type = self.customer.customer_type
            self.sender_nationality = self.customer.customer_nationality
            self.sender_id_type = self.customer.customer_id_type
            self.sender_id_card_no = self.customer.customer_id_card_no or self.customer.iqama_no
            self.sender_visa_no = self.customer.customer_visa_no

    @api.onchange('as_customer_id')
    def _onchange_as_customer_id(self):
        if self.as_customer_id:
            self.sender_name = self.other_customer_id.name
            self.sender_type = self.other_customer_id.customer_type
            self.sender_nationality = self.other_customer_id.customer_nationality
            self.sender_id_type = self.other_customer_id.customer_id_type
            self.sender_id_card_no = self.other_customer_id.customer_id_card_no or self.other_customer_id.iqama_no
            self.sender_visa_no = self.other_customer_id.customer_visa_no

    # on true get following filed from customer_checked_fields
    @api.onchange('same_as_sender')
    def _onchange_same_as_sender(self):
        if self.same_as_sender:
            self.owner_name = self.sender_name
            self.owner_type = self.sender_type
            self.owner_nationality = self.sender_nationality
            self.owner_id_type = self.sender_id_type
            self.owner_id_card_no = self.sender_id_card_no
            self.owner_visa_no = self.sender_visa_no

    # on true get following filed from same_as_sender
    @api.onchange('same_as_owner')
    def _onchange_same_as_owner(self):
        if self.same_as_owner:
            self.receiver_name = self.owner_name
            self.receiver_type = self.owner_type
            self.receiver_nationality = self.owner_nationality
            self.receiver_id_type = self.owner_id_type
            self.receiver_id_card_no = self.owner_id_card_no
            self.receiver_visa_no = self.owner_visa_no

    @api.onchange('sender_type', 'owner_type', 'receiver_type')
    def _onchange_customer_type(self):
        if self.sender_type and self.sender_type == '1':
            self.sender_nationality = self.env['res.country'].search([('code', '=', 'SA'), ('phone_code', '=', '966')])[
                0].id
            self.sender_id_type = 'saudi_id_card'
        elif self.sender_type and self.sender_type == '2':
            self.sender_id_type = 'iqama'
            self.sender_id_card_no = self.customer.iqama_no if self.customer else self.cooperate_customer.iqama_no

        if self.owner_type and self.owner_type == '1':
            self.owner_nationality = self.env['res.country'].search([('code', '=', 'SA'), ('phone_code', '=', '966')])[
                0].id
            self.owner_id_type = 'saudi_id_card'
        elif self.owner_type and self.owner_type == '2':
            self.owner_id_type = 'iqama'
            self.owner_id_card_no = self.customer.iqama_no if self.customer else self.cooperate_customer.iqama_no

        if self.receiver_type and self.receiver_type == '1':
            self.receiver_nationality = \
                self.env['res.country'].search(
                    [('code', '=', 'SA'), ('phone_code', '=', '966')])[0].id
            self.receiver_id_type = 'saudi_id_card'
        elif self.receiver_type and self.receiver_type == '2':
            self.receiver_id_type = 'iqama'
            self.receiver_id_card_no = self.customer.iqama_no if self.customer else self.cooperate_customer.iqama_no

    @api.onchange('cooperate_customer')
    def _onchange_cooperate_customer(self):
        if self.customer and self.customer.block_list:
            if self.customer and self.customer.block_list:
                raise UserError(_("You can't create this SO plz contact HQ."))
        else:
            if self.cooperate_customer:
                self.customer = self.cooperate_customer.id
                self.customer_price_list = self.cooperate_customer.property_product_pricelist.id
            for data in self.cooperate_customer:
                if not data.child_ids:
                    self.cargo_invoice_to = self.cooperate_customer.id
                if data.child_ids:
                    self.cargo_invoice_to = False

    @api.onchange('customer_price_list')
    def _onchange_customer_price_list(self):
        if self.customer_price_list:
            if self.order_line_ids:
                for CargoSaleLine in self.order_line_ids:
                    CargoSaleLine.customer_price_list = self.customer_price_list.id

    @api.onchange('customer')
    def _onchange_customer(self):
        if self.customer and self.customer.block_list:
            if self.customer and self.customer.block_list:
                raise UserError(_("You can't create this SO plz contact HQ."))
        else:
            if self.customer:
                if self.partner_types.is_credit_customer:
                    self.payment_method = self.env['cargo_payment_method'].search([("payment_type", "=", "credit")],
                                                                                  limit=1).id
                self.customer_contract = False
                self.customer_price_list = self.customer.property_product_pricelist.id
                self._onchange_same_as_customer()
                self._onchange_same_as_sender()
                self._onchange_same_as_owner()
                '''if self.customer.commercial_reg_expiry_date:
                    current_date = date.today()
                    commercial_reg_expire_timedelta = self.customer.commercial_reg_expiry_date - self.order_date.date()
                    commercial_reg_expire_days = commercial_reg_expire_timedelta.days
                    customer_contract = self.env['bsg_customer_contract'].search(
                        [('cont_customer', '=', self.customer.id), ('cont_end_date', '>=', self.order_date),
                         ('state', '=', 'confirm')])
                    if commercial_reg_expire_days >= 0 and commercial_reg_expire_days <= 60:
                        self.warning_expired = False
                        self.warning_to_be_expired = True
                        if customer_contract:
                            for contract_id in customer_contract:
                                contract_id.write({
                                    'reg_expiry_check': True
                                })
                    elif commercial_reg_expire_days < 0:
                        self.warning_expired = True
                        self.warning_to_be_expired = False
                        if customer_contract:
                            for contract_id in customer_contract:
                                contract_id.write({
                                    'reg_expiry_check': False
                                })
                    else:
                        self.warning_expired = False
                        self.warning_to_be_expired = False
                        for contract_id in customer_contract:
                            contract_id.write({
                                'reg_expiry_check': True
                                'contract_id': True
                            })'''

    @api.onchange('customer_type', 'shipment_type')
    def onchange_customer_type(self):
        if self.customer_type == 'corporate':
            return {'domain': {'customer': [('is_company', '=', True), ('customer_rank', '>', 0)]}}
        elif self.customer_type == 'individual':
            return {'domain': {
                'customer': [('is_company', '=', False), ('parent_id', '=', False), ('customer_rank', '>', 0)]
            }}

    @api.onchange('customer_contract', 'payment_method')
    def onchange_customer_contract(self):
        if self.customer_contract:
            # as per khaleed told
            # payment_method = self.env['cargo_payment_method'].search(
            #    [('payment_type', '=', 'credit')], limit=1)
            # self.payment_method = payment_method.id
            # Due to someone change _onchange_cooperate_customer this method so
            # self.cargo_invoice_to = self.customer_contract.cont_invoice_to.id
            self.cargo_invoice_to = self.cooperate_customer.id
            if self.partner_types.is_credit_customer:
                for type in self.customer_contract.payment_method_ids:
                    if type == self.payment_method:
                        return {}
                raise UserError(_("Payment Method must be in the customer Contract "))

    # @api.onchange('payment_method')
    # def _onchange_payment_method(self):
    # 	if self.payment_method:
    # 		if self.payment_method.payment_type in ['cash', 'pod']:
    # 			if self.customer_type == 'corporate':
    # 				self.cooperate_customer.partner_types = self.payment_method.partner_type_id.id
    # 				self.cooperate_customer.property_account_receivable_id = self.payment_method.partner_type_id.accont_rec.id
    # 				self.cooperate_customer.property_account_payable_id = self.payment_method.partner_type_id.accont_payable.id
    # 			elif self.customer_type == 'individual':
    # 				self.customer.partner_types = self.payment_method.partner_type_id.id
    # 				self.customer.property_account_receivable_id = self.payment_method.partner_type_id.accont_rec.id
    # 				self.customer.property_account_payable_id = self.payment_method.partner_type_id.accont_payable.id

    @api.onchange('order_line_ids', 'is_satah')
    def _onchange_order_lines(self):
        for record in self:
            if record.is_credit_customer or record.customer_type == 'corporate' and not record.allow_contract:
                if not record.customer_contract:
                    raise UserError(
                        _('You must first select a Contract...!'),
                    )
            if record.is_satah:
                if record.order_line_ids:
                    new_lines = record.env['satah.vehicale.list']
                    record.satah_line = False
                    for line in record.order_line_ids:
                        if line.type == 'both':
                            data = {
                                'cargo_sale_line_id': line.id,
                                'cargo_sale_id': record.id,
                                'plate_no': line.general_plate_no,
                                'loc_dest': record.loc_from.id,
                                'type': 'pickup',
                                # [0]
                                'product_id': self.env['product.template'].search([('is_satah', '=', True)]).id,
                            }
                            new_line = new_lines.new(data)
                            data.update(
                                {'type': 'delivery', 'loc_src': record.loc_to.id, 'loc_dest': False, })
                            new_line = new_lines.new(data)
                        else:
                            data = {
                                'cargo_sale_line_id': line.id,
                                'cargo_sale_id': record.id,
                                'plate_no': line.general_plate_no,
                                'type': line.type,
                                # [0]
                                'product_id': record.env['product.template'].search([('is_satah', '=', True)]).id,
                                'loc_dest': record.loc_from.id if line.type == 'pickup' else False,
                                'loc_src': record.loc_to.id if line.type == 'delivery' else False,
                            }
                            new_line = new_lines.new(data)
                else:
                    record.satah_line = False
            if record.order_line_ids:
                if (record.total_amount or record.total_discount) <= 0:
                    raise UserError(
                        _('You can not Save a Sale Order Line with amount 0 or less then 0 !'), )

    @api.onchange('loc_from', 'loc_to', 'shipment_type')
    def _onchange_loc_from_to(self):
        # don't touch untill ask to me
        # 		Commented BY EHTISHAM AS HAMDAN SAID
        # 		if self.order_line_ids:
        # 			for data in self.order_line_ids:
        # 				data._onchange_service_price()
        if self.loc_from and self.loc_to:
            record = self.env['bsg.estimated.delivery.days'].search(
                [('loc_from_id', '=', self.loc_from.id), ('loc_to_id', '=', self.loc_to.id)], limit=1)
            if record:
                self.deliver_date = str(
                    datetime.now() + timedelta(days=record.est_no_delivery_days, hours=record.est_no_hours))

            if self.loc_from.is_international or self.loc_to.is_international:
                self.cargo_sale_type = 'international'
            else:
                self.cargo_sale_type = 'local'

        if self.cargo_sale_type == 'international' and self.loc_from.is_international:
            self.currency_id = self.loc_from.loc_branch_id.currency_id.id
        elif self.cargo_sale_type == 'local' and not self.loc_from.is_international:
            self.currency_id = self.env.user.company_id.currency_id.id
        if not self.currency_id:
            self.currency_id = self.env.user.company_id.currency_id.id
        if self.shipment_type == 'return':
            self.return_loc_to = self.loc_from
            self.return_loc_from = self.loc_to

    # CRUD METHODS

    # Overiding create method
    @api.model
    def create(self, vals):
        if vals.get('receiver_mob_no', False):
            receiver_mob_no = vals['receiver_mob_no']
            if receiver_mob_no.startswith('0'):
                vals.update({
                    'receiver_mob_no': receiver_mob_no[1:]
                })
        CargoSale = super(BsgVehicleCargoSale, self).create(vals)
        CargoSale.name = "*" + str(CargoSale.id)
        CargoSale.is_old_order = False
        ean = generate_ean(CargoSale.name)
        CargoSale.barcode = ean
        if CargoSale.customer_contract:
            self._check_max_contract_limit(CargoSale)
            self._check_max_credit_limit(CargoSale)
        CargoSale._onchange_loc_from_to()
        # CargoSale._onchange_payment_method()
        if vals.get('state', False):
            CargoSale.update_order_lines_state()
        return CargoSale

    def update_order_lines_state(self):
        for rec in self:
            if rec.order_line_ids:
                for line in rec.order_line_ids:
                    line.sale_order_state = rec.state

    def remove_initail_return_shipment(self):
        for rec in self:
            for line in rec.return_so_id.order_line_ids:
                line.write({'state': 'cancel'})
            rec.return_so_id = False
            for line in rec.order_line_ids:
                line.write({'return_intiated': False, 'is_return_canceled': False})
            rec._compute_no_line_to_return()
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def write(self, line_values):
        if not self.is_from_portal and line_values.get('shipment_type', self.shipment_type) == 'return' and (
                line_values.get('loc_from',
                                self.loc_from) or line_values.get(
            'loc_to', self.loc_to)):
            line_values.update({
                'return_loc_from': line_values.get('loc_to', self.loc_to.id or False),
                'return_loc_to': line_values.get('loc_from', self.loc_from.id or False)

            })
        if line_values.get('receiver_mob_no', False):
            receiver_mob_no = line_values['receiver_mob_no']
            if receiver_mob_no.startswith('0'):
                line_values.update({
                    'receiver_mob_no': receiver_mob_no
                })

        res = super(BsgVehicleCargoSale, self).write(line_values)
        for data in self:
            if data.state == 'draft':
                data._reset_sequence()
        # data._onchange_loc_from_to()
        if line_values.get('state', False):
            for data in self:
                data.update_order_lines_state()
        if (line_values.get('loc_to', False) or line_values.get('shipment_type', False)) and not self.is_from_portal:
            self.order_line_ids.unlink()
        # self._onchange_payment_method()
        return res

    def copy(self, default=None):
        if not self._context.get('is_return_process', False) and self.shipment_type == 'return':
            raise ValidationError(
                _("Can't duplicate Sale Order with shipment type 'round trip'"))
        vals = default or {}
        user_loc = self._default_get_loc_from()
        vals.update({
            'order_date': datetime.now(),
            'expected_delivery_days': False,
            'deliver_date': False,
            'user_id': self.env.user.id,
            'customer_type': False,
            'allow_change_loc': False,
            'return_intiated': False,
            'is_return_so': False,
            'loc_from': user_loc,
            'return_so_id': False,
            'loc_to': False
        })
        return super(BsgVehicleCargoSale, self.with_context(keep_line_sequence=True)).copy(vals)

    # Overiding Unlink method

    def unlink(self):
        for order in self:
            if order.state != 'draft':
                raise UserError(
                    _('You can not delete a confirmed Sale Order.'),
                )
        return super(BsgVehicleCargoSale, self).unlink()

    def receive_from_customer(self):
        for rec in self:
            if rec.state == 'registered':
                inv = self.env['account.move'].sudo().search([('cargo_sale_id', '=', rec.id)], limit=1)
                if not inv:
                    rec.invoice_create_validate()
                    inv = self.env['account.move'].sudo().search([('cargo_sale_id', '=', rec.id)], limit=1)
                if rec.payment_method.payment_type == 'pod':
                    rec.write({'state': 'pod'})
                elif rec.payment_method.payment_type == 'credit' or (inv and inv.state == 'paid'):
                    rec.write({'state': 'done'})
                elif rec.shipment_type == 'return':
                    rec.write({'state': 'confirm'})
                else:
                    rec.write({'state': 'confirm'})
                rec.recieved_from_customer_date = fields.Datetime.now()
                for line in rec.order_line_ids:
                    line.state = 'confirm'
                    line.recieved_from_customer_date = fields.Datetime.now()
                    if line.shipment_type.is_normal:
                        line._set_exp_delivery_date(line.loc_from, line.loc_to, line.car_size)
                    else:
                        line._set_exp_delivery_date(line.loc_from, line.loc_to, line.shipment_type.car_size)

    # Action methods

    def confirm_btn(self):
        # data = {'default_order_id': self.id, 'do_not_create_invoice': self._context.get('do_not_create_invoice', False)}
        # return {
        #     'name': 'Confirm',
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'sale.order.confirm.message',
        #     'view_mode': 'form',
        #     'view_type': 'form',
        #     'context': data,
        #     'target': 'new',
        # }
        if not self.order_line_ids:
            raise UserError(_('There is no order line please create one.'), )
        if self.is_return_so != True and (self.total_amount <= 0 or self.total_discount < 0):
            raise UserError(
                _('You can not confirm a SO with amount 0 or less then 0..!'), )
        contract_id = self.customer_contract
        if contract_id and not self.is_return_so:
            if contract_id.remainder_amt < self.total_amount:
                raise UserError(
                    _('You Can not Confirm SO with (Customer Contract)Remaining Balance is less then 0 ..!'), )
        # if self.payment_method.payment_type != 'cash':
        self.create_trip_picking(
            self.order_line_ids, self.loc_from, self.loc_to, False)
        name = str(self.loc_from.loc_branch_id.branch_no) + \
               self.env['ir.sequence'].with_context(force_company=self.env.user.company_id.id).next_by_code(
                   'bsg_vehicle_cargo_sale')
        if self.is_return_so:
            self.name = 'R' + name
            self.state = 'done'
            self._reset_sequence()
            return True
        else:
            self.name = name
        for data in self:
            data._reset_sequence()
        if not self._context.get('do_not_create_invoice', False):
            self.invoice_create_validate()
        self.action_inspection()
        if not self.is_from_portal:
            self.recieved_from_customer_date = self.order_date
        for line in self.order_line_ids:
            if line.shipment_type.is_normal:
                line._set_exp_delivery_date(
                    line.loc_from, line.loc_to, line.car_size)
            else:
                line._set_exp_delivery_date(
                    line.loc_from, line.loc_to, line.shipment_type.car_size)
            if not self.is_from_portal:
                line.recieved_from_customer_date = self.order_date
            if self.payment_method.payment_type == 'credit':
                if line.state == 'draft':
                    line.state = 'confirm'
            if self.payment_method.payment_type == 'pod':
                if line.state == 'draft':
                    line.state = 'confirm'
                # if not line.added_to_trip or not line.fleet_trip_id:
                #     line.add_to_auto_trip()
            # else:
            # if self.payment_method.payment_type == 'pod':
            #   if line.state == 'draft':
            #       line.state = 'pod'
            #   if not line.added_to_trip or not line.fleet_trip_id:
            #       line.add_to_auto_trip()
            line.confirm_sms_setup()
        self.execute_coupon()

    def set_draft_btn(self):
        return self.write({'state': 'draft'})

    def initiate_return_btn(self):
        """Initiate return button"""
        user_loc = self._default_get_loc_from()
        if not user_loc or (self.loc_to.id != user_loc and user_loc not in self.loc_to.allowed_return_waypoint_ids.ids):
            raise ValidationError(
                _("Can't initiate return for sale order with loc to not equals to user branch."))
        if all(st == 'draft' for st in self.order_line_ids.mapped('state')):
            raise ValidationError(
                _("The outbound sale line must be processed first!"))
        if all(self.order_line_ids.mapped('return_intiated')):
            raise ValidationError(
                _("All return trips for this order already intiated"))
        if self.return_loc_from and self.return_loc_to:
            if (self.return_loc_to.branch_type not in ['pickup', 'both']):
                message = "You have to update %s as this is %s branch and you cant intiate like this" % (
                    self.return_loc_to.route_waypoint_name, self.return_loc_to.branch_type)
                self.env.ref('bsg_cargo_sale.change_so_locations_action')
                data = {'sale_id': self.id,
                        'default_return_loc_to': True,
                        'default_loc_to_id': self.return_loc_to.id,
                        'default_msg': message,
                        'default_sale_line_ids': self.order_line_ids.filtered(lambda
                                                                                  s: s.state == 'done' and s.return_intiated == False and s.is_return_canceled == False).ids,
                        }

                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'change_so_locations',
                    'view_id': self.env.ref('bsg_cargo_sale.change_so_locations_form').id,
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': data,
                    'target': 'new'
                }
            # elif self.return_loc_from.branch_type not in ['shipping', 'both']:
            #     message = "You have to update %s as this is %s branch and you cant intiate like this" % (
            #         self.return_loc_from.route_waypoint_name, self.return_loc_from.branch_type)
            #     self.env.ref('bsg_cargo_sale.change_so_locations_action')
            #     data = {'sale_id': self.id,
            #             'default_new_ret_loc_from': user_loc,
            #             'default_return_loc_from': True,
            #             'default_msg': message,
            #             'default_sale_line_ids': self.order_line_ids.filtered(lambda s:s.state in ['Delivered','done','released'] and s.return_intiated == False and s.is_return_canceled == False).ids,
            #             }
            #     return {
            #         'type': 'ir.actions.act_window',
            #         'res_model': 'change_so_locations',
            #         'view_id': self.env.ref('bsg_cargo_sale.change_so_locations_form').id,
            #         'view_mode': 'form',
            #         'view_type': 'form',
            #         'context': data,
            #         'target': 'new',
            #     }
            elif len(self.order_line_ids) > 1:
                message = "Please select sale lines for return trip."
                data = {'sale_id': self.id,
                        'default_msg': message,
                        'default_sale_line_ids': self.order_line_ids.filtered(lambda
                                                                                  s: s.state == 'done' and s.return_intiated == False and s.is_return_canceled == False).ids,
                        }
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'change_so_locations',
                    'view_id': self.env.ref('bsg_cargo_sale.change_so_locations_form').id,
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': data,
                    'target': 'new',
                }
            else:
                return self.start_return_process()
        else:
            raise UserError(_("Location are not set...!"))

    def start_return_process(self):
        if self.order_line_ids:
            user_loc = self._default_get_loc_from()
            if not user_loc or (
                    self.loc_to.id != user_loc and user_loc not in self.loc_to.allowed_return_waypoint_ids.ids):
                raise ValidationError(
                    _("Can't initiate return for sale order with loc to not equals to user branch."))
            order_lines = False
            if self._context.get('sale_line_ids', False):
                order_lines = self.env['bsg_vehicle_cargo_sale_line'].browse(
                    self._context.get('sale_line_ids'))
            else:
                order_lines = self.order_line_ids
            if any(st != 'done' for st in order_lines.mapped('state')):
                raise ValidationError(
                    _("The outbound sale line must be processed first!"))
            if all(order_lines.mapped('return_intiated')):
                raise ValidationError(
                    _("All return trips for this order already intiated"))
            _logger.info("start_return_process: starting copy")
            so_vals = {'order_line_ids': False, 'order_date': datetime.now(),
                       'shipment_type': 'oneway',
                       'loc_from': self.loc_to.id, 'loc_to': self.loc_from.id,
                       'return_loc_from': self.loc_to.id, 'payment_method': self.payment_method.id,
                       'recieved_from_customer_date': datetime.now(), 'shipment_date': datetime.now()}
            new_so = self.with_context(
                {'is_return_process': True}).copy(default=so_vals)
            _logger.info("start_return_process: end copy")
            loc_to = False
            if self._context.get('new_ret_loc_to', False):
                loc_to = self._context.get('new_ret_loc_to')
            else:
                loc_to = self.loc_from.id
            new_so.write({
                'loc_to': loc_to,
                'loc_from': user_loc
            })
            # new_so.loc_to = self._context.get('new_ret_loc_to', self.loc_from.id)
            self.return_so_id = new_so.id
            new_so.is_return_so = True
            new_so._onchange_loc_from_to()
            # new_so.name = 'R' + new_so.name
            _logger.info("start_return_process: new order %s" % new_so.id)
            for line in order_lines:
                _logger.info("start_return_process: in order_line_ids loop")
                if line.state == 'done':
                    _logger.info("start_return_process:line is draft")
                    return_line = line.duplicate_record(new_so.id)
                    _logger.info(
                        "start_return_process: duplicated line %s" % return_line.id)
                    # for updating data when return the procee
                    return_line.bsg_cargo_sale_id = new_so.id
                    # return_line.bsg_cargo_return_sale_id = new_so.id
                    bsg_cargo_return_sale_id = new_so
                    vals = {'order_date': bsg_cargo_return_sale_id.order_date,
                            'account_id': bsg_cargo_return_sale_id.account_id.id,
                            'receiver_name': bsg_cargo_return_sale_id.receiver_name,
                            'receiver_mob_no': bsg_cargo_return_sale_id.receiver_mob_no,
                            #  'payment_method' : line.payment_method.id,
                            'deliver_date': False,
                            'delivery_date': False,
                            'customer_id': bsg_cargo_return_sale_id.customer.id,
                            'receiver_type': bsg_cargo_return_sale_id.receiver_type,
                            'receiver_nationality': bsg_cargo_return_sale_id.receiver_nationality.id,
                            'receiver_id_type': bsg_cargo_return_sale_id.receiver_id_type,
                            'receiver_id_card_no': bsg_cargo_return_sale_id.receiver_id_card_no,
                            'receiver_visa_no': bsg_cargo_return_sale_id.receiver_visa_no,
                            'receiver_mob_no': bsg_cargo_return_sale_id.receiver_mob_no,
                            'no_of_copy': bsg_cargo_return_sale_id.no_of_copy,
                            'cargo_sale_state': 'draft',
                            'unit_charge': 0,
                            'discount': 0,
                            'tax_ids': False,
                            'price_line_id': False,
                            'return_loc_from': return_line.loc_from.id,
                            'return_loc_to': return_line.loc_to.id,
                            'so_line_revenue_technical': line.so_line_revenue_technical,
                            'shipping_source_id': self.id,
                            'recieved_from_customer_date': datetime.now(),
                            }
                    return_line.write(vals)
                    return_line._set_exp_delivery_date(
                        new_so.loc_from, new_so.loc_to, line.shipment_type.car_size)
                    line.return_intiated = True
                    line.return_source_id = new_so.id
                else:
                    raise UserError(
                        _("The outbound sale line must be processed first!"))
            new_so.write({
                'total_amount': 0,
                'state': 'draft',
            })
            # self.create_trip_picking(new_so.order_line_ids, new_so.loc_from, new_so.loc_to, False)
            all_return_intiated = all(
                self.order_line_ids.mapped('return_intiated'))
            to_write_vals = {
                'return_intiated': all_return_intiated
            }
            if all_return_intiated:
                to_write_vals.update({
                    'state': 'done'
                })

            self.write(to_write_vals)
            action = self.env.ref(
                'bsg_cargo_sale.action_bsg_vehicle_cargo_sale').read()[0]
            action['views'] = [
                (self.env.ref('bsg_cargo_sale.view_vehicle_cargo_sale_form').id, 'form')]
            action['res_id'] = new_so.id
            return action

        else:
            return True

    def decline(self):
        return self.write({'state': 'cancel'})

    def action_inspection(self):
        Inspection = self.env['bassami.inspection']
        for rec in self:
            for line in rec.order_line_ids:
                val = {'cargo_sale_id': rec.id,
                       'cargo_sale_line_id': line.id,
                       'customer': rec.customer.id,
                       'branch_from': rec.loc_from.id,
                       'branch_to': rec.loc_to.id,

                       'branch_ids': [(6, 0, [rec.loc_from.loc_branch_id.id, rec.create_uid.user_branch_id.id])]
                       }
                Ins_id = Inspection.create(val)
                line.write({'inspection_id': Ins_id.id})

    # Register Payment for credit invoice

    def register_payment_for_return(self):
        self.refund_invoice_validate()
        view_id = self.env.ref('account.view_account_payment_register_form').id
        journal_id = self.env['account.journal'].search(
            [('type', '=', 'cash')], limit=1)
        if not journal_id:
            raise UserError(
                _("There is no cash journal defined please define in accounting."))
        if self.reversal_move_id.filtered(
                lambda s: s.state == 'posted'):
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
                    'default_partner_id':
                        self.reversal_move_id.filtered(
                            lambda s: s.state == 'posted').mapped('partner_id')[0].id,
                    'default_partner_type': 'customer',
                    'default_amount': self.reversal_move_id.filtered(lambda s: s.state == 'posted')[0].residual - self.refund_invoice_ids.filtered(lambda s: s.state == 'posted')[0].single_trip_reason.stc_value,
                    'default_amount_return_cargo_invoice': self.refund_invoice_ids.filtered(lambda s: s.state == 'posted')[0].residual - self.refund_invoice_ids.filtered(lambda s: s.state == 'posted')[0].single_trip_reason.stc_value,
                    'default_return_invoice_id': self.reversal_move_id.filtered(lambda s: s.state == 'posted')[0].id,
                    'default_communication': self.name,
                    'pass_sale_order_id': self.id,
                    'default_invoice_ids': [
                        (4, self.refund_invoice_ids.filtered(lambda s: s.state == 'posted')[0].id, None)]
                }
            }

    # elif self.payment_method.payment_type == 'cash':
    # 	# Creation of trip and on cash method
    # 	# self.create_trip_picking(self.order_line_ids, self.loc_from, self.loc_to, False)
    # 	return {
    # 		'type': 'ir.actions.act_window',
    # 		'name': 'Name',
    # 		'view_mode': 'form',
    # 		'view_type': 'form',
    # 		'res_model': 'account.payment',
    # 		'view_id': view_id,
    # 		'target': 'new',
    # 		'context': {
    # 			'default_partner_id': self.customer.id,
    # 			'default_payment_type': 'inbound',
    # 			'default_partner_type': 'customer',
    # 			'context_sequnce_cash': True,
    # 			# 'default_journal_id': journal_id.id,
    # 			'default_amount': self.total_amount - self.refund_invoice_ids[0].single_trip_reason.stc_value,
    # 			'default_communication': self.name,
    # 			'default_is_show_partial' : True,
    # 			'default_cargo_sale_order_id': self.id,
    # 			'default_invoice_ids': [(4, self.refund_invoice_ids[0].id, None)]
    # 		}
    # 	}

    # else:
    # 	return {
    # 		'type': 'ir.actions.act_window',
    # 		'name': 'Name',
    # 		'view_mode': 'form',
    # 		'view_type': 'form',
    # 		'res_model': 'account.payment',
    # 		'view_id': view_id,
    # 		'target': 'new',
    # 		'context': {
    # 			'default_partner_id': self.customer.id,
    # 			'default_payment_type': 'inbound',
    # 			'default_partner_type': 'customer',
    # 			# 'default_journal_id': journal_id.id,
    # 			'default_amount': self.total_amount - self.refund_invoice_ids[0].single_trip_reason.stc_value,
    # 			'default_communication': self.name,
    # 			'default_cargo_sale_order_id': self.id,
    # 			'default_invoice_ids': [(4, self.refund_invoice_ids[0].id, None)]
    # 		}
    # 	}

    # Register Payment

    def register_payment(self):
        self.invoice_ids.action_register_payment()
        if self.is_validate:
            raise UserError(_("Please Posted a invoice Voucher First"))
        if not self.invoice_ids.filtered(lambda s: s.state == 'posted'):
            raise ValidationError(_("Please make sure the order has an [posted] invoice!"))
        view_id = self.env.ref('account.view_account_payment_register_form').id
        journal_id = self.env['account.journal'].search(
            [('type', '=', 'cash')], limit=1)
        # As Per Told By Mr Hamdan
        # if self.loc_from.loc_branch_id.id != self.env.user.user_branch_id.id:
        # 	if self.payment_method.payment_type == 'cash':
        # 		raise UserError(_("You can not Register Payment ....!"))
        if not journal_id:
            raise UserError(
                _("There is no cash journal defined please define in accounting."))
        if self.payment_method.payment_type == 'pod':
            return {
                'type': 'ir.actions.act_window',
                'name': 'Name',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'account.payment.register',
                'view_id': view_id,
                'target': 'new',
                'context': {
                    'active_model':'account.move',
                    'active_ids':self.invoice_ids.ids,
                    'default_payment_type': 'inbound',
                    'default_partner_id': self.invoice_ids.filtered(lambda s: s.state == 'posted').mapped('partner_id')[
                        0].id,
                    'default_partner_type': 'customer',
                    'default_journal_id': journal_id.id,
                    'default_amount': sum(
                        self.order_line_ids.filtered(lambda s: not s.is_paid and s.state != 'cancel').mapped(
                            'charges')),
                    'default_communication': self.name,
                    'default_show_invoice_amount': True,
                    'pass_sale_order_id': self.id,
                    'default_is_form_cargo_line': True,

                    'default_is_patrtially_payment': True,
                    'default_cargo_sale_order_id': self.id,
                    'default_cargo_sale_line_order_ids': self.order_line_ids.filtered(
                        lambda s: not s.is_paid and s.state != 'cancel').ids,
                    'default_invoice_ids': [(4, self.invoice_ids.filtered(lambda s: s.state == 'posted')[0].id, None)],
                    'driver_collection_id': self._context.get('driver_collection_id', False),
                }
            }
        elif self.payment_method.payment_type == 'cash':
            # Creation of trip and on cash method
            # self.create_trip_picking(self.order_line_ids, self.loc_from, self.loc_to, False)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Name',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'account.payment.register',
                'view_id': view_id,
                'target': 'new',
                'context': {
                    'active_model': 'account.move',
                    'active_ids': self.invoice_ids.ids,
                    'default_payment_type': 'inbound',
                    'default_partner_id': self.invoice_ids.filtered(lambda s: s.state == 'posted').mapped('partner_id')[
                        0].id,
                    'default_partner_type': 'customer',
                    # 'default_journal_id': journal_id.id,
                    'default_amount': sum(self.order_line_ids.filtered(lambda s: not s.payment_ids).mapped('charges')),
                    'default_communication': self.name,
                    # 'default_show_invoice_amount': True,
                    'pass_sale_order_id': self.id,
                    'context_sequnce_cash': True,
                    'default_is_show_partial': True,
                    'default_is_form_cargo_line': True,
                    'default_cargo_sale_order_id': self.id,
                    'default_cargo_sale_line_order_ids': self.order_line_ids.filtered(
                        lambda s: not s.is_paid and s.state != 'cancel').ids,
                    'default_invoice_ids': [(4, self.invoice_ids.filtered(lambda s: s.state == 'posted')[0].id, None)],
                    'driver_collection_id': self._context.get('driver_collection_id', False),
                }
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Name',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'account.payment.register',
                'view_id': view_id,
                'target': 'new',
                'context': {
                    'default_payment_type': 'inbound',
                    'default_partner_id': self.invoice_ids.filtered(lambda s: s.state == 'posted').mapped('partner_id')[
                        0].id,
                    'default_partner_type': 'customer',
                    # 'default_journal_id': journal_id.id,
                    'default_amount': sum(self.order_line_ids.filtered(lambda s: not s.payment_ids).mapped('charges')),
                    'default_communication': self.name,
                    'pass_sale_order_id': self.id,
                    'default_is_form_cargo_line': True,

                    'default_cargo_sale_order_id': self.id,
                    'default_cargo_sale_line_order_ids': self.order_line_ids.filtered(
                        lambda s: not s.is_paid and s.state != 'cancel').ids,
                    'default_invoice_ids': [(4, self.invoice_ids[0].id, None)],
                    'driver_collection_id': self._context.get('driver_collection_id', False),
                }
            }

    def register_payment_tamara_instore(self):
        if self.is_validate:
            raise UserError(_("Please Posted a invoice Voucher First"))
        if not self.invoice_ids.filtered(lambda s: s.state == 'posted'):
            raise ValidationError(_("Please make sure the order has an [open] invoice!"))
        view_id = self.env.ref('account.view_account_payment_register_form').id
        journal_id = self.env['account.journal'].search(
            [('type', '=', 'cash')], limit=1)
        # As Per Told By Mr Hamdan
        # if self.loc_from.loc_branch_id.id != self.env.user.user_branch_id.id:
        # 	if self.payment_method.payment_type == 'cash':
        # 		raise UserError(_("You can not Register Payment ....!"))
        if not journal_id:
            raise UserError(
                _("There is no cash journal defined please define in accounting."))
        if self.payment_method.payment_type == 'pod':
            return {
                'payment_type': 'inbound',
                'partner_id': self.invoice_ids.filtered(lambda s: s.state == 'posted').mapped('partner_id')[
                    0].id,
                'partner_type': 'customer',
                # 'default_journal_id': journal_id.id,
                'amount': sum(
                    self.order_line_ids.filtered(lambda s: not s.is_paid and s.state != 'cancel').mapped('charges')),
                'communication': self.name,
                'show_invoice_amount': True,
                'pass_sale_order_id': self.id,
                'is_patrtially_payment': True,
                'cargo_sale_order_id': self.id,
                'cargo_sale_line_order_ids': self.order_line_ids.filtered(
                    lambda s: not s.is_paid and s.state != 'cancel').ids,
                'invoice_ids': [(4, self.invoice_ids.filtered(lambda s: s.state == 'posted')[0].id, None)],
                'driver_collection_id': self._context.get('driver_collection_id', False),
            }
        elif self.payment_method.payment_type == 'cash':
            # Creation of trip and on cash method
            # self.create_trip_picking(self.order_line_ids, self.loc_from, self.loc_to, False)
            return {
                'payment_type': 'inbound',
                'partner_id': self.invoice_ids.filtered(lambda s: s.state == 'posted').mapped('partner_id')[
                    0].id,
                'partner_type': 'customer',
                # 'default_journal_id': journal_id.id,
                'amount': sum(self.order_line_ids.filtered(lambda s: not s.payment_ids).mapped('charges')),
                'communication': self.name,
                # 'default_show_invoice_amount': True,
                'pass_sale_order_id': self.id,
                'context_sequnce_cash': True,
                'is_show_partial': True,
                'cargo_sale_order_id': self.id,
                'cargo_sale_line_order_ids': self.order_line_ids.filtered(
                    lambda s: not s.is_paid and s.state != 'cancel').ids,
                'invoice_ids': [(4, self.invoice_ids.filtered(lambda s: s.state == 'posted')[0].id, None)],
                'driver_collection_id': self._context.get('driver_collection_id', False),
            }
        else:
            return {
                'payment_type': 'inbound',
                'partner_id': self.invoice_ids.filtered(lambda s: s.state == 'posted').mapped('partner_id')[
                    0].id,
                'partner_type': 'customer',
                # 'default_journal_id': journal_id.id,
                'amount': sum(self.order_line_ids.filtered(lambda s: not s.payment_ids).mapped('charges')),
                'communication': self.name,
                'pass_sale_order_id': self.id,
                'cargo_sale_order_id': self.id,
                'cargo_sale_line_order_ids': self.order_line_ids.filtered(
                    lambda s: not s.is_paid and s.state != 'cancel').ids,
                'invoice_ids': [(4, self.invoice_ids[0].id, None)],
                'driver_collection_id': self._context.get('driver_collection_id', False),
            }

    # for cenceling invoice and payment record
    def cancel_related_records(self):
        if self.invoice_ids:
            for data in self.invoice_ids:
                for payment_data in data.payment_ids:
                    payment_data.cancel_payment()
                data.action_invoice_cancel()
        if self.reversal_move_id:
            for return_data in self.reversal_move_id:
                for payment_data in return_data.payment_ids:
                    payment_data.cancel_payment()
                return_data.action_invoice_cancel()
        self.state = 'cancel'
        for data in self.order_line_ids:
            data.write({'state': 'cancel'})

    # for cenceling invoice and payment record wth particular line data as well
    def cancel_related_caego_records(self, cargo_sale_line):
        if self.invoice_ids:
            for data in self.invoice_ids:
                for payment_data in data.payment_ids:
                    payment_data.cancel_payment()
                data.action_invoice_cancel()
        if self.reversal_move_id:
            for return_data in self.refund_invoice_ids:
                for payment_data in return_data.payment_ids:
                    payment_data.cancel_payment()
                return_data.action_invoice_cancel()
        self.state = 'cancel'
        cargo_sale_line.write({'state': 'cancel'})

    # cancel So Line
    def cancel_so_agreement(self):
        # validation as told by Muhammad
        if not self.env.user.has_group('account.group_account_manager') and (
                self.env.user.user_branch_id.id != self.loc_from_branch_id.id):
            raise UserError(
                _("You can not cancel, Your branch not match with shipment branch...!"))
        if len(self.order_line_ids.filtered(
                lambda s: not s.fleet_trip_id and s.last_fleet_trip_id and s.last_fleet_trip_id.trip_type == 'local').ids) > 0:
            raise UserError(_("You can not cancel"))

        data = {'default_cargo_sale_id': self.id,
                'default_cargo_sale_line_ids': [(6, 0,
                                                 self.order_line_ids.filtered(
                                                     lambda s: not s.fleet_trip_id and s.state in ['draft',
                                                                                                   'confirm'] and not s.add_to_cc).ids)],
                }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cancel.multi.so.line.record',
            'view_id': self.env.ref('bsg_cargo_sale.cancel_multi_so_line_record_form').id,
            'view_mode': 'form',
            'view_type': 'form',
            'context': data,
            'target': 'new',
        }

    # set to draft
    def set_to_draft(self):
        self.state = 'draft'

    # for canceling allow to execuate and no need to do code more than 1 times
    def cancel_order_line_record(self):
        for data in self.order_line_ids:
            if data.state != 'draft' or data.add_to_cc:
                raise UserError(
                    _("You can not cancel, Please contact Finance"))
            else:
                self.cancel_related_caego_records(data)

    # Cancel Agreement

    def cancel_agreement(self):
        list_of_check = []

        if not self.env.user.has_group('account.group_account_manager') and not self.env.user.has_group(
                'account.group_account_user') and self.env.user.user_branch_id.id != self.loc_from_branch_id.id:
            raise UserError(
                _("You can not cancel, Your branch not match with shipment branch...!"))
        if len(self.order_line_ids.filtered(
                lambda s: not s.fleet_trip_id and s.last_fleet_trip_id and s.last_fleet_trip_id.trip_type == 'local').ids) > 0:
            raise UserError(_("You can not cancel"))

        # validation as told by Muhammad
        # if len(self.order_line_ids) > 1:
        # 	raise UserError(_("You can not cancel, more than 1 cargo sale line not cancelled ...!"))

        # Stop Here And Add It In Refund Wiard in Cargo line domain###########
        if self.is_old_order:
            for data in self.order_line_ids:
                if data.fleet_trip_id or data.state not in ['draft', 'registered']:
                    raise UserError(_("You can not cancel Agreement.....!"))

            if self.reversal_move_id:
                self.refund_invoice_validate()
                raise UserError(
                    _("Refund is already created for this invoice."))
        #################This Stopped To Add To Domain######################

        # if self.payment_method.payment_type == 'credit':
        '''if self.is_credit_customer:
            if self.env.user.has_group('bsg_cargo_sale.group_cancel_branch_so') or self.env.user.has_group('bsg_cargo_sale.group_cancel_any_branch_so'):
                if self.env.user.has_group('bsg_cargo_sale.group_cancel_any_branch_so'):
                    self.cancel_order_line_record()
                elif self.env.user.has_group('bsg_cargo_sale.group_cancel_branch_so'):
                    if self.env.user.user_branch_id.id == self.loc_from_branch_id.id:
                        self.cancel_order_line_record()
                    else:
                        raise UserError(_("You can not cancel, Your branch not match with shipment branch...!"))
            else:
                if self.create_uid.id == self.env.user.id:
                    self.cancel_order_line_record()
                else:
                    raise UserError(_("You can not cancel, Please contact Finance"))'''

        if self.payment_method.payment_type in ['cash', 'pod'] and self.invoice_ids:
            # for data in self.order_line_ids:
            #    if data.fleet_trip_id:
            #        raise UserError(_("You can not cancel, Cargo sale line linked with Trip"))

            view_id = self.env.ref('account.view_account_move_reversal').id
            ctx = {
                'default_wizard_cargo_sale_id': self.id,
                'default_refund_method': 'cancel' if self.invoice_ids and self.invoice_ids[
                    0].state == 'posted' else 'refund',
                'default_cargo_sale_line_ids': [(6, 0, self.order_line_ids.filtered(
                    lambda s: not s.fleet_trip_id and s.state in ['draft', 'registered','confirm']).ids)]
            }
            fiscalyear_lock_date = self.invoice_ids[0].company_id.fiscalyear_lock_date
            period_lock_date = self.invoice_ids[0].company_id.period_lock_date
            invoice_date = self.invoice_ids[0].invoice_date
            if (fiscalyear_lock_date and invoice_date <= fiscalyear_lock_date) or (
                    period_lock_date and invoice_date <= period_lock_date):
                invoice_date = fiscalyear_lock_date and fiscalyear_lock_date + timedelta(
                    days=1) or period_lock_date and period_lock_date + timedelta(days=1)
                ctx.update({
                    'invoice_date': invoice_date
                })
            else:
                ctx.update({
                    'invoice_date': self.invoice_ids[0].invoice_date
                })

            return {
                'type': 'ir.actions.act_window',
                'name': 'Name',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'account.move.reversal',
                'view_id': view_id,
                'context': ctx,
                'target': 'new',
            }

    # for cancel return trip

    def action_cancel_retrun_trip(self):
        if self.env.user.user_branch_id.id != self.loc_from.loc_branch_id.id and self.env.user.user_branch_id.id != self.loc_to.loc_branch_id.id:
            raise UserError(
                _("You Are Not autherize To Cancel Return Trip ...!"))
        view_id = self.env.ref('account.view_account_move_reversal').id
        ctx = {
            'default_wizard_cargo_sale_id': self.id,
            'default_refund_method': 'refund',
            'default_cancel_return_trip': True,
            'default_cargo_sale_line_ids': self.order_line_ids.filtered(
                lambda s: s.state != 'cancel' and s.return_intiated == False and s.is_return_canceled == False).ids
        }
        fiscalyear_lock_date = self.invoice_ids[0].company_id.fiscalyear_lock_date
        period_lock_date = self.invoice_ids[0].company_id.period_lock_date
        invoice_date = self.invoice_ids[0].date_invoice
        if (fiscalyear_lock_date and invoice_date <= fiscalyear_lock_date) or (
                period_lock_date and invoice_date <= period_lock_date):
            invoice_date = fiscalyear_lock_date and fiscalyear_lock_date + timedelta(
                days=1) or period_lock_date and period_lock_date + timedelta(days=1)
            ctx.update({
                'invoice_date': invoice_date
            })
        else:
            ctx.update({
                'invoice_date': self.invoice_ids[0].invoice_date
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Name',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.move.reversal',
            'view_id': view_id,
            'context': ctx,
            'target': 'new',
        }

    # this method to create and validate invoice
    def invoice_create_validate(self):
        if not self.is_invoice_created:
            self.invoice_create()
            if self.invoice_ids:
                for inv in self.invoice_ids:
                    if inv.state == 'draft':
                        inv.action_post()
                self.is_invoice_created = True

    # this method to validate refund invoice
    def refund_invoice_validate(self):
        for inv in self.reversal_move_id:
            inv.action_post()

    # View Invoices

    def action_view_refund_invoice(self):
        # invoices = self.mapped(context.get('field'))
        invoces = False
        if self.invoice_ids:
            invoices = self.env['account.move'].search(
                ['|', ('reversed_entry_id', '=', self.invoice_ids[0].id), ('wizard_cargo_sale_id', '=', self.id)])
        else:
            invoices = self.env['account.move'].search(
                [('wizard_cargo_sale_id', '=', self.id)])
        action = self.env.ref('account.action_move_out_refund_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [
                (self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # View Invoices

    def action_view_invoice(self):
        # invoices = self.mapped(context.get('field'))

        invoices = self.env['account.move'].search(
            [('cargo_sale_id', '=', self.id), ('wizard_cargo_sale_id', '=', False), ('cargo_sale_line_id', '=', False),
             ('is_other_service_invoice', '=', False)])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [
                (self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # View Other Services Invoices

    def action_view_other_invoice(self, context):
        invoices = self.env['account.move'].search(
            ['|','&',('invoice_origin', '=', self.name), ('is_other_service_invoice', '=', True),
            '&',('reversed_entry_id.invoice_origin', '=', self.name), ('reversed_entry_id.is_other_service_invoice', '=', True)])
        action = self.env.ref('account.view_out_invoice_tree').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [
                (self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # Register Payment For other Services

    def other_serive_register_payment(self):
        if not self.is_other_service_invoice:
            raise UserError(_("Please Create Invoice First....!"))
        view_id = self.env.ref('account.view_account_payment_register_form').id
        journal_id = self.env['account.journal'].search(
            [('type', '=', 'cash')], limit=1)
        if not journal_id:
            raise UserError(
                _("There is no cash journal defined please define in accounting."))
        other_service_invoice = self.env['account.move'].search(
            [('ref', '=', self.name), ('is_other_service_invoice', '=', True)], limit=1)
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
                'default_partner_id': self.other_service_invoice.partner_id.id,
                'default_partner_type': 'customer',
                'default_amount': self.total_service_amount,
                'default_communication': self.name,
                'default_show_invoice_amount': False,
                'default_invoice_ids': [(4, other_service_invoice.id, None)]
            }
        }

    def create_other_serive_invoice(self):
        invoice = False
        if self.state == 'draft':
            raise UserError(
                _('You Can not Create Invoice in Draft State.....!'))
        if self.other_service_line_ids.filtered(lambda s: not s.is_invoice_create):
            other_services_lines = self.other_service_line_ids.filtered(lambda s: not s.is_invoice_create)
            other_services_currencies = set(other_services_lines.mapped('currency_id'))
            inv_obj = self.env['account.move']
            inv_line_obj = self.env['account.move.line']
            for currency in other_services_currencies:
                inv_data = self._prepare_invoice_for_other_service(currency)
                invoice = inv_obj.create(inv_data)
                for other_services in other_services_lines.filtered(lambda s: s.currency_id.id == currency.id):
                    if not other_services.is_invoice_create:
                        if other_services.cost <= 0:
                            raise UserError(
                                _('Service Amount Must Not Be More Than Or Equal 0'),
                            )
                        if not other_services.product_id.property_account_income_id:
                            raise UserError(
                                _('Service Product account is missing!! Please add in configuration'),
                            )
                        line_name = str(other_services.cargo_sale_line_id.sale_line_rec_name) + '-' + str(
                            other_services.description if other_services.description else "Other Service")
                        other_inv_line_vals = self._prepare_invoice_line(invoice.id,
                                                                         other_services.product_id.property_account_income_id.id,
                                                                         line_name,
                                                                         other_services.cost, False,
                                                                         other_services.tax_ids if other_services.tax_ids else False,
                                                                         False, other_services.product_id.id)

                        other_inv_line_vals.update({
                            'cargo_sale_line_id': other_services.cargo_sale_line_id.id,
                            'is_other_service_line': True,
                        })
                        inv_line_obj.create(other_inv_line_vals)
                    other_services.write({'is_invoice_create': True})
                invoice._compute_amount()
                invoice.action_post()
        else:
            raise UserError(_('Not Found Any Other Service Line....!'))
        self.write({'is_other_service_invoice': True})
        return invoice

    #  Prepare Invoice

    def _prepare_invoice_for_other_service(self, currency=False):
        self.ensure_one()
        if not currency:
            currency = self.currency_id
        journal_id = self.env['account.move']._search_default_journal()
        if not journal_id:
            raise UserError(
                _('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': self.name,
            'ref': self.name,
            'move_type': 'out_invoice',
            'cargo_sale_id': self.id,
            'other_service_line_id': self._context.get('other_service_line_id') if self._context.get(
                'other_service_line_id') else False,
            'is_other_service_invoice': True,
            'account_id': self.customer.property_account_receivable_id.id,
            'partner_id': self.customer.id,
            'parent_customer_id': self.customer.id,
            'partner_shipping_id': self.customer.id,
            'journal_id': journal_id,
            'currency_id': currency.id,
            'comment': self.note,
            'user_id': self.user_id and self.user_id.id,
            'cargo_sale_id': self.id,
        }
        return invoice_vals

    #  Prepare Invoice

    def _prepare_invoice(self):
        self.ensure_one()
        # journal_id = self.env['account.move']._default_journal()
        journal_id = self.env['account.journal'].sudo().search([('type', '=', 'sale'), ('company_id', '=', 1)],limit=1)
        if not journal_id:
            raise UserError(
                _('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': self.name,
            'ref': self.name,
            'invoice_date_due' : fields.Date().today(),
            'cargo_sale_id': self.id,
            'move_type': 'out_invoice',
            'is_international_so_invoice': True if self.cargo_sale_type == 'international' else False,
            # 'account_id': self.other_customer_id.property_account_receivable_id.id if self.other_customer_id.property_account_receivable_id else self.customer.property_account_receivable_id.id,
            'partner_id': self.cargo_invoice_to.id or self.customer.id if not self.is_to_other_customer else self.other_customer_id.id,
            'parent_customer_id': self.customer.id if not self.is_to_other_customer else self.other_customer_id.id,
            'partner_shipping_id': self.customer.id if not self.is_to_other_customer else self.other_customer_id.id,
            'journal_id': journal_id.id,
            'currency_id': self.currency_id.id,
            # 'comment': self.note,
            'user_id': self.user_id and self.user_id.id,
            'is_so_invoice': True,
        }
        return invoice_vals

    # Prepare Invoice Line
    #  Before changing in any method pls check where it is being used

    def _prepare_invoice_line(self, inv_id, account_id, name, amount, discount, tax_ids, analytic, product_id,
                              **plate_no):
        data = {
            'product_id': product_id,
            'name': str(name) + '-' + str(self.loc_from.loc_branch_id.branch_no) + '-' + str(
                self.loc_to.loc_branch_id.branch_no) + '-  ' + str(plate_no.get('plate_no')) if plate_no.get(
                'plate_no') else str(name) + '  -' + str(
                self.loc_from.loc_branch_id.branch_no) + '-' + str(
                self.loc_to.loc_branch_id.branch_no),
            'account_id': account_id,
            'price_unit': amount,
            'branch_id': self.loc_from.loc_branch_id and self.loc_from.loc_branch_id.id or False,
            'quantity': 1,
            'discount': discount,
            'move_id': inv_id,
            'analytic_distribution': {
                52: 100.0,
            },
            'tax_ids': [(6, 0, tax_ids.ids)] if tax_ids else [(6, 0, [])]
        }

        return data

    # invoice creation method

    def invoice_create(self):
        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']
        journal_id = self.env['account.move']._compute_journal_id()
        if not self.customer_contract or self.payment_method.payment_type in ['cash', 'pod']:
            for order in self:
                inv_data = order._prepare_invoice()
                invoice = inv_obj.create(inv_data)
                for line in order.order_line_ids:
                    account_id = line.service_type.property_account_income_id.id if line.service_type.property_account_income_id else self._default_inv_line_account_id()
                    product_id = self.env['product.product'].search([('product_tmpl_id', '=', line.service_type.id)],
                                                                    limit=1).id
                    if not account_id:
                        raise UserError(
                            _('Account Invoice Line account is missing!! Please add in configuration'),
                        )
                    car_details = str(line.sale_line_rec_name) + '-' + str(
                        line.car_make.car_maker.car_make_name) + " " + str(
                        line.car_model.car_model_name) + " " + str(line.car_size.car_size_name)
                    plate_no = False
                    if line.plate_registration == 'saudi':
                        plate_no = line.plate_no + line.palte_third + line.palte_second + line.palte_one
                    else:
                        plate_no = line.non_saudi_plate_no
                    charges = (line.unit_charge + line.additional_ship_amount)
                    inv_line_vals = self._prepare_invoice_line(invoice.id, account_id, car_details,
                                                               charges, line.discount, line.tax_ids, line.account_id,
                                                               product_id, plate_no=plate_no)
                    inv_line_vals.update({
                        'cargo_sale_line_id': line.id
                    })
                    inv_line_obj.create(inv_line_vals)

                if order.is_satah and order.satah_line:
                    for satah in order.satah_line:
                        product_id = self.env['product.product'].search(
                            [('product_tmpl_id', '=', line.service_type.id)],
                            limit=1).id
                        account_income_id = self.env['product.product'].search(
                            [('is_satah', '=', True)], limit=1)
                        account_id = account_income_id.property_account_income_id.id if account_income_id.property_account_income_id else self._default_satah_account_id()
                        if not account_id:
                            raise UserError(
                                _('Satah Service account is missing!! Please add in configuration'),
                            )
                        line_name = str(self.name) + '-' + str("Satah Service")
                        inv_line_vals = self._prepare_invoice_line(invoice.id, account_id, line_name, satah.price,
                                                                   False,
                                                                   line.tax_ids, line.account_id, product_id)
                        inv_line_vals.update({
                            'cargo_sale_line_id': line.id
                        })
                        inv_line_obj.create(inv_line_vals)

                # for passing other service on creating invoice
                if order.other_service_line_ids:
                    for data in order.other_service_line_ids:
                        line_name = str(data.cargo_sale_line_id.sale_line_rec_name) + '-' + str(
                            data.description if data.description else "Other Service")
                        other_inv_line_vals = self._prepare_invoice_line(invoice.id,
                                                                         data.product_id.property_account_income_id.id,
                                                                         line_name,
                                                                         data.cost, False,
                                                                         data.tax_ids if data.tax_ids else False,
                                                                         False, data.product_id.id)
                        other_inv_line_vals.update({
                            'cargo_sale_line_id': data.cargo_sale_line_id.id,
                            'is_other_service_line': True,
                        })
                        inv_line_obj.create(other_inv_line_vals)
                        data.write({'is_invoice_create': True})
            if self.state not in ['draft', 'registered']:
                self._get_total_of_demurrae_cost()
                if self.final_price != 0:
                    product_id = self.env['product.product'].search(
                        [('name', '=', 'Demurrage Cost')], limit=1)
                    if not product_id:
                        product_id = self.env['product.product'].create(
                            {'name': 'Demurrage Cost', 'type': 'service'})
                        invoice_line_vals = {
                            'name': product_id.name,
                            'product_id': product_id.id,
                            'account_id': product_id.categ_id.property_account_income_categ_id.id,
                            'price_unit': self.final_price,
                            'quantity': 1,
                            'discount': self.discount_price,
                            'invoice_id': invoice.id,
                        }
                        invoice_line_ids = self.env['account.move.line'].create(
                            invoice_line_vals)
                        self.write({'is_demurrage_inovice': True})
            invoice._compute_tax_totals()
            # as not updated on production
            invoice.action_post()
        # if self.is_to_other_customer and self.other_customer_id:
        # 	return self.write({'state': 'confirm'})
        # else:
        if self.payment_method.payment_type == 'pod':
            return self.write({'state': 'pod'})
        elif self.payment_method.payment_type == 'credit':
            return self.write({'state': 'done'})
        elif self.shipment_type == 'return':
            return self.write({'state': 'confirm'})
        else:
            return self.write({'state': 'confirm'})

    # check max contract limit
    def _check_max_contract_limit(self, sale_order):
        if sale_order.customer_contract and sale_order.customer_contract.max_sales_limit:
            domain = [
                ('customer', '=', sale_order.customer_contract.cont_customer.id),
                ('customer_contract', '=', sale_order.customer_contract.id)]
            prev_sale_recs = self.env['bsg_vehicle_cargo_sale'].search(domain)
            prev_sales_amount = sum(rec.total_amount for rec in prev_sale_recs)
        # As need M.Khalid
        # if (prev_sales_amount + sale_order.total_amount) > sale_order.customer_contract.max_sales_limit:
        # 	raise UserError(
        # 		_('Total contract amount exceeded for this contract.'),
        # 	)

    # if sale_order.customer_contract:
    # 	if sale_order.customer_contract.remainder_amt < sale_order.total_amount:
    # 		raise UserError(_('Contract Remaining Balance is less then actual amt'),)

    # check max credit limit
    def _check_max_credit_limit(self, sale_order):
        if sale_order.customer and sale_order.customer.max_credit_limit:
            domain = [
                ('customer', '=', sale_order.customer.id)]
            prev_sale_recs = self.env['bsg_vehicle_cargo_sale'].search(domain)
            prev_sales_amount = sum(rec.total_amount for rec in prev_sale_recs)
            if (prev_sales_amount + sale_order.total_amount) > sale_order.customer.max_credit_limit:
                raise UserError(
                    _('Max Credit limit exceeded for this customer.'),
                )

    # Create Picking In Vehicle Trips Via sale order Confirmation.
    # PLEASE DONT CHANGE THIS METHOD ALWAYS CONCERN LEAD FOR THIS
    def create_trip_picking(self, order_line, loc_from, loc_to, Trips):
        if not Trips:
            trips = self.get_suitable_trip(loc_from, loc_to)
            # Trips = self.env['fleet.vehicle.trip'].search(
            # 	[
            # 		('id', 'in', self.get_suitable_trip(loc_from, loc_to)),
            # 		('trip_type', '=', 'auto'),
            # 	])
        order_line_capacity = sum(
            line.car_size.trailer_capcity for line in order_line)
        if Trips:
            for tr in Trips:
                if tr.trip_type != 'local':
                    if order_line_capacity >= 0:
                        if tr.total_capacity > 0:
                            for sl in order_line:
                                if not sl.fleet_trip_id:
                                    if tr.total_capacity >= 2 and sl.sudo().with_context(
                                            force_company=self.env.user.company_id.id,
                                            company_id=self.env.user.company_id.id).car_size.trailer_capcity > 1:
                                        order_line_capacity -= 2

                                        # Creation of picking
                                        tr.total_capacity = tr.total_capacity - 2
                                        # tr.trailer_capcity = tr.total_capacity - 2
                                        create_id = tr.stock_picking_id.with_context(
                                            force_company=self.env.user.company_id.id,
                                            company_id=self.env.user.company_id.id).create({
                                            'picking_name': sl.id,
                                            'picking_date': sl.sudo().with_context(
                                                force_company=self.env.user.company_id.id,
                                                company_id=self.env.user.company_id.id).bsg_cargo_sale_id.order_date,
                                            'scheduled_date': sl.sudo().with_context(
                                                force_company=self.env.user.company_id.id,
                                                company_id=self.env.user.company_id.id).bsg_cargo_sale_id.deliver_date,
                                            'bsg_fleet_trip_id': tr.id,
                                        })
                                        # Writing fleet trip id of sale order line
                                        sl.sudo().with_context(force_company=self.env.user.company_id.id,
                                                               company_id=self.env.user.company_id.id).write(
                                            {'fleet_trip_id': tr.id})
                                        if tr.trip_type == 'manual' and not sl.partner_add_to_trip_id:
                                            sl.partner_add_to_trip_id = create_id.create_uid.partner_id.id
                                        end_date = datetime.strptime(
                                            str(tr.expected_end_date), "%Y-%m-%d %H:%M:%S")
                                        est_delivery_option = self._default_estimated_delivery()
                                        if est_delivery_option == 'edd':
                                            self._set_exp_delivery_date(
                                                loc_from, loc_to)
                                        else:
                                            self.write(
                                                {'deliver_date': end_date.date()})
                                        # Creation or updation of waypoints
                                        for line in tr.trip_waypoint_ids:
                                            if line.waypoint.id == loc_from.id:
                                                line.picked_items = [
                                                    (4, sl.id)]
                                            elif line.waypoint.id == loc_to.id:
                                                line.delivered_items = [
                                                    (4, sl.id)]
                                        # Creation or updation of Arrivals
                                        self._update_arriva_lines(
                                            tr, sl.id, loc_from, loc_to)
                                        # tr.truck_load = 'full'
                                    elif tr.total_capacity >= 1:
                                        if sl.car_size.trailer_capcity == 1:
                                            order_line_capacity -= 1
                                            # Creation of picking
                                            tr.total_capacity = tr.total_capacity - 1
                                            # tr.trailer_capcity = tr.total_capacity - 2
                                            create_id = tr.stock_picking_id.with_context(
                                                force_company=self.env.user.company_id.id,
                                                company_id=self.env.user.company_id.id).create({
                                                'picking_name': sl.id,
                                                'picking_date': sl.sudo().with_context(
                                                    force_company=self.env.user.company_id.id,
                                                    company_id=self.env.user.company_id.id).bsg_cargo_sale_id.order_date,
                                                'scheduled_date': sl.sudo().with_context(
                                                    force_company=self.env.user.company_id.id,
                                                    company_id=self.env.user.company_id.id).bsg_cargo_sale_id.deliver_date,
                                                'bsg_fleet_trip_id': tr.id,
                                            })
                                            # Writing tirp id

                                            sl.write({'fleet_trip_id': tr.id, })
                                            if tr.trip_type == 'manual' and not sl.partner_add_to_trip_id:
                                                sl.partner_add_to_trip_id = create_id.create_uid.partner_id.id
                                            end_date = datetime.strptime(
                                                str(tr.expected_end_date), "%Y-%m-%d %H:%M:%S")
                                            est_delivery_option = self._default_estimated_delivery()
                                            if est_delivery_option == 'edd':
                                                self._set_exp_delivery_date(
                                                    loc_from, loc_to)
                                            else:
                                                self.write(
                                                    {'deliver_date': end_date.date()})
                                            # Creation or updation of waypoints
                                            for line in tr.trip_waypoint_ids:
                                                if line.waypoint.id == loc_from.id:
                                                    line.picked_items = [
                                                        (4, sl.id)]
                                                elif line.waypoint.id == loc_to.id:
                                                    line.delivered_items = [
                                                        (4, sl.id)]
                                            # Creation or updation of Arrivals
                                            self._update_arriva_lines(
                                                tr, sl.id, loc_from, loc_to)
                                            # tr.truck_load = 'full'
                                        elif not sl.car_size:
                                            # Creation of picking
                                            create_id = tr.stock_picking_id.create({
                                                'picking_name': sl.id,
                                                # 'loc_from': loc_from.id,
                                                # 'loc_to': loc_to.id,
                                                'picking_date': sl.sudo().with_context(
                                                    force_company=self.env.user.company_id.id,
                                                    company_id=self.env.user.company_id.id).bsg_cargo_sale_id.order_date,
                                                'scheduled_date': sl.sudo().with_context(
                                                    force_company=self.env.user.company_id.id,
                                                    company_id=self.env.user.company_id.id).bsg_cargo_sale_id.deliver_date,
                                                'bsg_fleet_trip_id': tr.id,
                                            })
                                            # Writing tirp id
                                            sl.write({'fleet_trip_id': tr.id})
                                            if tr.trip_type == 'manual' and not sl.partner_add_to_trip_id:
                                                sl.partner_add_to_trip_id = create_id.create_uid.partner_id.id
                                            end_date = datetime.strptime(
                                                str(tr.expected_end_date), "%Y-%m-%d %H:%M:%S")
                                            est_delivery_option = self._default_estimated_delivery()
                                            if est_delivery_option == 'edd':
                                                self._set_exp_delivery_date(
                                                    loc_from, loc_to)
                                            else:
                                                self.write(
                                                    {'deliver_date': end_date.date()})
                                            # Creation or updation of waypoints
                                            for line in tr.trip_waypoint_ids:
                                                if line.waypoint.id == loc_from.id:
                                                    line.picked_items = [
                                                        (4, sl.id)]
                                                elif line.waypoint.id == loc_to.id:
                                                    line.delivered_items = [
                                                        (4, sl.id)]
                                            # Creation or updation of Arrivals
                                            self._update_arriva_lines(
                                                tr, sl.id, loc_from, loc_to)
                                            # tr.truck_load = 'full'
                        else:
                            raise UserError(
                                _('Capacity Issue ...!'), )
                else:
                    if order_line_capacity >= 0:
                        if tr.total_capacity > 0:
                            for sl in order_line:
                                if tr.total_capacity >= 2 and sl.sudo().with_context(
                                        force_company=self.env.user.company_id.id,
                                        company_id=self.env.user.company_id.id).car_size.trailer_capcity > 1:
                                    order_line_capacity -= 2
                                    # Creation of picking
                                    tr.total_capacity = tr.total_capacity - 2
                                    create_id = tr.stock_picking_id.sudo().with_context(
                                        force_company=self.env.user.company_id.id,
                                        company_id=self.env.user.company_id.id).create({
                                        'picking_name': sl.id,
                                        'picking_date': sl.sudo().with_context(
                                            force_company=self.env.user.company_id.id,
                                            company_id=self.env.user.company_id.id).bsg_cargo_sale_id.order_date,
                                        'scheduled_date': sl.sudo().with_context(
                                            force_company=self.env.user.company_id.id,
                                            company_id=self.env.user.company_id.id).bsg_cargo_sale_id.deliver_date,
                                        'bsg_fleet_trip_id': tr.id,
                                    })
                                    # Writing fleet trip id of sale order line
                                    # sl.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).write({'fleet_trip_id': tr.id})
                                    end_date = datetime.strptime(
                                        str(tr.expected_end_date), "%Y-%m-%d %H:%M:%S")
                                    est_delivery_option = self._default_estimated_delivery()
                                    if est_delivery_option == 'edd':
                                        self._set_exp_delivery_date(
                                            loc_from, loc_to)
                                    else:
                                        self.write(
                                            {'deliver_date': end_date.date()})
                                    # Creation or updation of waypoints
                                    for line in tr.trip_waypoint_ids:
                                        if line.waypoint.id == loc_from.id:
                                            line.picked_items = [(4, sl.id)]
                                        elif line.waypoint.id == loc_to.id:
                                            line.delivered_items = [(4, sl.id)]
                                    # Creation or updation of Arrivals
                                    self._update_arriva_lines(
                                        tr, sl.id, loc_from, loc_to)
                                    # tr.truck_load = 'full'
                                elif tr.total_capacity >= 1:
                                    if sl.car_size.trailer_capcity == 1:
                                        order_line_capacity -= 1
                                        # Creation of picking
                                        tr.total_capacity = tr.total_capacity - 1
                                        tr.stock_picking_id.sudo().with_context(
                                            force_company=self.env.user.company_id.id,
                                            company_id=self.env.user.company_id.id).create({
                                            'picking_name': sl.id,
                                            'picking_date': sl.sudo().with_context(
                                                force_company=self.env.user.company_id.id,
                                                company_id=self.env.user.company_id.id).bsg_cargo_sale_id.order_date,
                                            'scheduled_date': sl.sudo().with_context(
                                                force_company=self.env.user.company_id.id,
                                                company_id=self.env.user.company_id.id).bsg_cargo_sale_id.deliver_date,
                                            'bsg_fleet_trip_id': tr.id,
                                        })
                                        # Writing tirp id
                                        # sl.write({'fleet_trip_id': tr.id})
                                        end_date = datetime.strptime(
                                            str(tr.expected_end_date), "%Y-%m-%d %H:%M:%S")
                                        est_delivery_option = self._default_estimated_delivery()
                                        if est_delivery_option == 'edd':
                                            self._set_exp_delivery_date(
                                                loc_from, loc_to)
                                        else:
                                            self.write(
                                                {'deliver_date': end_date.date()})
                                        # Creation or updation of waypoints
                                        for line in tr.trip_waypoint_ids:
                                            if line.waypoint.id == loc_from.id:
                                                line.picked_items = [
                                                    (4, sl.id)]
                                            elif line.waypoint.id == loc_to.id:
                                                line.delivered_items = [
                                                    (4, sl.id)]
                                        # Creation or updation of Arrivals
                                        self._update_arriva_lines(
                                            tr, sl.id, loc_from, loc_to)
                                        # tr.truck_load = 'full'
                                    elif not sl.car_size:
                                        # Creation of picking
                                        tr.stock_picking_id.sudo().with_context(
                                            force_company=self.env.user.company_id.id,
                                            company_id=self.env.user.company_id.id).create({
                                            'picking_name': sl.id,
                                            # 'loc_from': loc_from.id,
                                            # 'loc_to': loc_to.id,
                                            'picking_date': sl.sudo().with_context(
                                                force_company=self.env.user.company_id.id,
                                                company_id=self.env.user.company_id.id).bsg_cargo_sale_id.order_date,
                                            'scheduled_date': sl.sudo().with_context(
                                                force_company=self.env.user.company_id.id,
                                                company_id=self.env.user.company_id.id).bsg_cargo_sale_id.deliver_date,
                                            'bsg_fleet_trip_id': tr.id,
                                        })
                                        # Writing tirp id
                                        # sl.write({'fleet_trip_id': tr.id})
                                        end_date = datetime.strptime(
                                            str(tr.expected_end_date), "%Y-%m-%d %H:%M:%S")
                                        est_delivery_option = self._default_estimated_delivery()
                                        if est_delivery_option == 'edd':
                                            self._set_exp_delivery_date(
                                                loc_from, loc_to)
                                        else:
                                            self.write(
                                                {'deliver_date': end_date.date()})
                                        # Creation or updation of waypoints
                                        for line in tr.trip_waypoint_ids:
                                            if line.waypoint.id == loc_from.id:
                                                line.picked_items = [
                                                    (4, sl.id)]
                                            elif line.waypoint.id == loc_to.id:
                                                line.delivered_items = [
                                                    (4, sl.id)]
                                        # Creation or updation of Arrivals
                                        self._update_arriva_lines(
                                            tr, sl.id, loc_from, loc_to)
                                        # tr.truck_load = 'full'
                                    # else:
                                    # 	# raise UserError(
                                    # 	# 	_('Either Capacity Issue or Car size issue please check and re-confirm.'), )
                        else:
                            raise UserError(
                                _('Capacity Issue ...!'), )
                # else:
                # 	raise UserError(_('Trailer Aquiring Capacity on car size configuration is missing..!'), )
            if self.payment_method_code == 'credit':
                return self.write({'state': 'done'})
            return self.write({'state': 'confirm'})
        else:
            self._set_exp_delivery_date(loc_from, loc_to)

            return self.write({'state': 'confirm'})

        # raise UserError(_('Trips are not available.'), )

    # search suitable trip on the basis of location
    def get_suitable_trip(self, loc_from, loc_to):
        if loc_from and loc_to:
            TripsObj = self.env['fleet.vehicle.trip']
            trip_records = TripsObj.search([
                ('state', 'in', ['draft', 'on_transit']),
                ('total_capacity', '>=', 1),
                ('trip_type', '=', 'auto')
                # ('expected_start_date','>=',datetime.now())
            ])
            Tripdata = TripsObj.browse()
            for trip in trip_records:
                for waypoint in trip.bsg_trip_arrival_ids:
                    if not waypoint.register_done:
                        if waypoint.waypoint_from.id == loc_from.id and waypoint.waypoint_to.id == loc_to.id:
                            Tripdata += trip
                        elif waypoint.waypoint_from.id == loc_from.id:
                            current_trip = TripsObj.browse(trip.id)
                            dest_location = [dest.waypoint_to.id for dest in current_trip.bsg_trip_arrival_ids if
                                             dest.waypoint_to.id == loc_to.id]
                            if dest_location:
                                Tripdata += trip
            return Tripdata

    # # Update arrival screen on sale order Confirmation
    def _update_arriva_lines(self, trip, line_id, loc_from, loc_to):
        if trip:
            if loc_from and loc_to:
                for line in trip.bsg_trip_arrival_ids:
                    # if line.waypoint_from.id == loc_from.id or line.waypoint_to.id == loc_to.id:
                    line.arrival_line_ids.create({
                        'arrival_id': line.id,
                        'delivery_id': line_id,
                    })

    # set delivery date
    def _set_exp_delivery_date(self, loc_from, loc_to):
        record = self.env['bsg.estimated.delivery.days'].search(
            [('loc_from_id', '=', loc_from.id), ('loc_to_id', '=', loc_to.id)], limit=1)
        if record:
            return self.write({'deliver_date': datetime.now() + timedelta(days=record.est_no_delivery_days,
                                                                          hours=record.est_no_hours)})

    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.order_line_ids:
                line.sequence = current_sequence
                current_sequence += 1

    # Cron Job to update order status on basis of order line

    @api.model
    def update_order_status(self):
        ''' This method is called from a cron job. '''
        for order in self.search([]):
            order_line_len = len(order.order_line_ids)
            arrival_count = 0
            for data in order.order_line_ids:
                if data.state == 'Delivered':
                    arrival_count += 1
            if order_line_len == arrival_count:
                order.state = 'Delivered'

    @api.constrains('cooperate_customer')
    def _check_cooperate_customer(self):
        for rec in self:
            if rec.cooperate_customer and rec.cooperate_customer.block_list:
                raise UserError(_("You can't create this SO plz contact HQ."))

    @api.constrains('customer')
    def _check_cargo_sale_customer(self):
        for rec in self:
            if rec.customer and rec.customer.block_list:
                raise UserError(_("You can't create this SO plz contact HQ."))

    @api.constrains('owner_id_card_no')
    def _check_owner_id_card_no(self):
        block_list1 = self.env['res.partner'].search(
            [('block_list', '=', True), ('customer_id_card_no', '!=', False)]).mapped('customer_id_card_no')
        block_list2 = self.env['res.partner'].search([('block_list', '=', True), ('iqama_no', '!=', False)]).mapped(
            'iqama_no') + block_list1
        if block_list2:
            for rec in self:
                if rec.owner_id_card_no:
                    if rec.owner_id_card_no in block_list2:
                        raise UserError(_("You can't create this SO plz contact HQ."))

    @api.constrains('sender_id_card_no')
    def _check_sender_id_card_no(self):
        block_list1 = self.env['res.partner'].search(
            [('block_list', '=', True), ('customer_id_card_no', '!=', False)]).mapped('customer_id_card_no')
        block_list2 = self.env['res.partner'].search([('block_list', '=', True), ('iqama_no', '!=', False)]).mapped(
            'iqama_no') + block_list1
        if block_list2:
            for rec in self:
                if rec.sender_id_card_no:
                    if rec.sender_id_card_no in block_list2:
                        raise UserError(_("You can't create this SO plz contact HQ"))

    @api.constrains('receiver_id_card_no')
    def _check_receiver_id_card_no(self):
        block_list1 = self.env['res.partner'].search(
            [('block_list', '=', True), ('customer_id_card_no', '!=', False)]).mapped('customer_id_card_no')
        block_list2 = self.env['res.partner'].search([('block_list', '=', True), ('iqama_no', '!=', False)]).mapped(
            'iqama_no') + block_list1
        if block_list2:
            for rec in self:
                if rec.receiver_id_card_no:
                    if rec.receiver_id_card_no in block_list2:
                        raise UserError(_("You can't create this SO plz contact HQ."))


# Genration of barcode
def ean_checksum(eancode):
    """returns the checksum of an ean string of length 13, returns -1 if
    the string has the wrong length"""
    if len(eancode) != 13:
        return -1
    oddsum = 0
    evensum = 0
    eanvalue = eancode
    reversevalue = eanvalue[::-1]
    finalean = reversevalue[1:]

    for i in range(len(finalean)):
        if i % 2 == 0:
            oddsum += int(finalean[i])
        else:
            evensum += int(finalean[i])
    total = (oddsum * 3) + evensum

    check = int(10 - math.ceil(total % 10.0)) % 10
    return check


def check_ean(eancode):
    """returns True if eancode is a valid ean13 string, or null"""
    if not eancode:
        return True
    if len(eancode) != 13:
        return False
    try:
        int(eancode)
    except:
        return False
    return ean_checksum(eancode) == int(eancode[-1])


def generate_ean(ean):
    """Creates and returns a valid ean13 from an invalid one"""
    if not ean:
        return "0000000000000"
    ean = re.sub("[A-Za-z]", "0", ean)
    ean = re.sub("[^0-9]", "", ean)
    ean = ean[:13]
    if len(ean) < 13:
        ean = ean + '0' * (13 - len(ean))
    return ean[:-1] + str(ean_checksum(ean))


class InheritCustomerContract(models.Model):
    _inherit = 'bsg_customer_contract'

    commercial_reg_expiry_date = fields.Date("Commercial Registration Expiry Date",
                                             related='cont_customer.commercial_reg_expiry_date')

    reg_exp_alert = fields.Boolean(string='Reg Expiry Alert', compute='_check_cust_reg_and_end_date_expiry')
    reg_near_exp_alert = fields.Boolean(string='Reg Expiry Alert', compute='_check_cust_reg_and_end_date_expiry')

    cont_end_alert = fields.Boolean(string='Contract End Date Alert', compute='_check_cust_reg_and_end_date_expiry')
    cont_near_end_alert = fields.Boolean(string='Contract End Date Alert',
                                         compute='_check_cust_reg_and_end_date_expiry')

    payment_method_ids = fields.Many2many('cargo_payment_method', string='Payment Method', track_visibility=True)

    @api.depends('commercial_reg_expiry_date', 'cont_end_date')
    def _check_cust_reg_and_end_date_expiry(self):
        for rec in self:
            # rec.reg_near_exp_alert = rec.cont_near_end_alert = rec.cont_end_alert = rec.reg_exp_alert = False
            current_date = date.today()
            rec.reg_exp_alert = False
            rec.reg_near_exp_alert = False
            rec.cont_end_alert = False
            rec.cont_near_end_alert = False
            if rec.commercial_reg_expiry_date:
                commercial_reg_expire_timedelta = rec.commercial_reg_expiry_date - current_date
                commercial_reg_expire_days = commercial_reg_expire_timedelta.days
                commercial_reg_expire_validation_timedelta = rec.commercial_reg_expiry_date - current_date
                commercial_reg_expire_validation_days = commercial_reg_expire_validation_timedelta.days
                if commercial_reg_expire_validation_days >= 0 and commercial_reg_expire_validation_days <= 30:
                    rec.reg_near_exp_alert = True
                    rec.reg_exp_alert = False
                elif commercial_reg_expire_validation_days < 0:
                    rec.reg_exp_alert = True
                    rec.reg_near_exp_alert = False
                else:
                    rec.reg_near_exp_alert = False
                    rec.reg_exp_alert = False
            if rec.cont_end_date:
                timedelta_to_contract_end = rec.cont_end_date - current_date
                days_to_contract_end = timedelta_to_contract_end.days
                if days_to_contract_end >= 0 and days_to_contract_end <= 30:
                    rec.cont_near_end_alert = True
                    rec.cont_end_alert = False
                elif days_to_contract_end < 0:
                    rec.cont_near_end_alert = False
                    rec.cont_end_alert = True
                else:
                    rec.cont_near_end_alert = False
                    rec.cont_end_alert = False


class SaleOrderConfirmationMessage(models.TransientModel):
    _name = "sale.order.confirm.message"
    _description = "Sale Order Confirmation Message wizard"

    order_id = fields.Many2one('bsg_vehicle_cargo_sale', string="Order")
    message = fields.Char(string="Message", compute='_get_message')

    @api.depends('order_id')
    def _get_message(self):
        self.message = ''
        if self.order_id.cargo_invoice_to:
            message = "Please confirm with customer that he want the invoice to be printed wtih customer name %s otherwise, set customer name under 'invoiced customer' before you conform the agreement." % (
                self.order_id.cargo_invoice_to.display_name)
            self.message = message
        else:
            message = "Please confirm with customer that he want the invoice to be printed wtih customer name %s otherwise, set customer name under 'invoiced customer' before you conform the agreement." % (
                self.order_id.cooperate_customer.display_name)
            self.message = message

    def confirm_ok(self):
        if not self.order_id.order_line_ids:
            raise UserError(_('There is no order line please create one.'), )
        if self.order_id.is_return_so != True and (self.order_id.total_amount <= 0 or self.order_id.total_discount < 0):
            raise UserError(
                _('You can not confirm a SO with amount 0 or less then 0..!'), )
        contract_id = self.order_id.customer_contract
        if contract_id and not self.order_id.is_return_so:
            if contract_id.remainder_amt < self.order_id.total_amount:
                raise UserError(
                    _('You Can not Confirm SO with (Customer Contract)Remaining Balance is less then 0 ..!'), )
        # if self.payment_method.payment_type != 'cash':
        self.order_id.create_trip_picking(
            self.order_id.order_line_ids, self.order_id.loc_from, self.order_id.loc_to, False)
        name = str(self.order_id.loc_from.loc_branch_id.branch_no) + \
               self.env['ir.sequence'].with_context(force_company=self.env.user.company_id.id).next_by_code(
                   'bsg_vehicle_cargo_sale')
        if self.order_id.is_return_so:
            self.order_id.name = 'R' + name
            self.order_id.state = 'done'
            self.order_id._reset_sequence()
            return True
        else:
            self.order_id.name = name
        for data in self.order_id:
            data._reset_sequence()
        if not self._context.get('do_not_create_invoice', False):
            self.order_id.invoice_create_validate()
        self.order_id.action_inspection()
        if not self.order_id.is_from_portal:
            self.order_id.recieved_from_customer_date = self.order_id.order_date
        for line in self.order_id.order_line_ids:
            if not self.order_id.is_from_portal:
                line.recieved_from_customer_date = self.order_id.order_date
            if self.order_id.payment_method.payment_type == 'credit':
                if line.state == 'draft':
                    line.state = 'confirm'
                if not line.added_to_trip or not line.fleet_trip_id:
                    line.add_to_auto_trip()
            else:
                if self.order_id.payment_method.payment_type == 'pod':
                    if line.state == 'draft':
                        line.state = 'pod'
                    if not line.added_to_trip or not line.fleet_trip_id:
                        line.add_to_auto_trip()
            line.confirm_sms_setup()
        self.order_id.execute_coupon()
