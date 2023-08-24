# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta, date
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError, Warning, AccessError
from odoo.addons import decimal_precision as dp
import logging
import random
# from tiny_url import UrlShortenTinyurl
import requests
import sys
import traceback
import urllib


class UrlShortenTinyurl:
    URL = "http://tinyurl.com/api-create.php"
    status_code = False
    short_url = False

    def shorten(self, url_long):
        try:
            url = self.URL + "?" \
                  + urllib.parse.urlencode({"url": url_long})
            res = requests.get(url)
            self.status_code = res.status_code
            self.short_url = res.text
        except Exception as e:
            self.short_url = False


_logger = logging.getLogger(__name__)


class account_cargo_line_payment(models.Model):
    _name = "account.cargo.line.payment"
    _rec_name = 'cargo_sale_line_id'

    # def write(self, vals):
    #     print("")
    # def create(self, vals):
    #     return 1/0
    #     print("")

    multi = fields.Boolean()
    cargo_sale_line_id = fields.Many2one(
        'bsg_vehicle_cargo_sale_line', string="Cargo Sale Line", required=True)
    account_invoice_line_id = fields.Many2one(
        'account.move.line', 'Invoice Line')
    account_payment_id = fields.Many2one(
        'account.payment', 'Payment', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('posted', 'Posted'), ('reconciled', 'Reconciled'), ('cancelled', 'Cancelled'),
         ('reversal_entry', 'Reversal Entry')], related='account_payment_id.state')
    total = fields.Monetary(
        related='account_invoice_line_id.price_total', store=True)
    currency_id = fields.Many2one(
        'res.currency', related='account_invoice_line_id.move_id.currency_id', store=True)
    amount = fields.Float('Paid Amount')
    residual = fields.Float()
    is_other_service = fields.Boolean(related='account_invoice_line_id.is_other_service_line',
                                      string='Is Other Service', store=True)
    is_demurrage_line = fields.Boolean(related='account_invoice_line_id.is_demurrage_line', string='Is Demurrage',
                                       store=True)
    payment_currency_id = fields.Many2one(
        'res.currency', related='account_payment_id.currency_id', store=True)
    currency_amount = fields.Float(compute='compute_currency_amount', store=True)
    is_deduct = fields.Boolean(related='account_invoice_line_id.is_deduct', store=True)

    @api.depends('currency_id', 'payment_currency_id', 'amount')
    def compute_currency_amount(self):
        for rec in self:
            rec.currency_amount = rec.account_invoice_line_id.move_id.currency_id._convert(
                rec.amount, rec.payment_currency_id, self.env.user.company_id,
                rec.account_payment_id.date or fields.Date.today())

    '''@api.onchange('cargo_sale_line_id')
	def _onchange_cargo_sale_line_id(self):
		self.amount = self.cargo_sale_line_id.charges - \
			self.cargo_sale_line_id.paid_amount
		self.residual = self.cargo_sale_line_id.charges - \
			self.cargo_sale_line_id.paid_amount
		self.account_invoice_line_id = self.cargo_sale_line_id.bsg_cargo_sale_id.invoice_ids.filtered(
			lambda  s: s.state == 'open').invoice_line_ids.filtered(lambda  s: s.cargo_sale_line_id.id == self.cargo_sale_line_id.id).id
		return {'domain':{'cargo_sale_line_id':[('id','not in',self.account_payment_id.bsg_vehicle_cargo_sale_line_ids.mapped('cargo_sale_line_id').ids),
		('bsg_cargo_sale_id','=',self.env.context.get('pass_sale_order_id',False)),('is_paid','=',False)]}}'''

    @api.constrains('amount')
    def _constrains_amount(self):
        if not self.env.context.get('without_check_amount', False):
            for rec in self:
                if not rec.is_deduct and rec.amount <= 0:
                    raise Warning(
                        _('Sorry! Paid Amount Must Be Greater Than 0!'))
                if rec.amount > rec.residual:
                    raise Warning(
                        _("Sorry! Paid Amount Can't Be Greater Than Residual Amount !"))

    _sql_constraints = [('payment_cargo_invoice_line_uniq', 'unique(account_invoice_line_id,account_payment_id)',
                         'Duplicate Invoice Line in Payment not allowed !')]


# Account Tax
class InheritTax(models.Model):
    _inherit = 'account.tax'
    _rec_name = 'amount'


# Cargo Sale Order Line
class bsg_vehicle_cargo_sale_line(models.Model):
    _name = 'bsg_vehicle_cargo_sale_line'
    _description = "Cargo Sale Line"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = "sale_line_rec_name"
    _order = 'order_date desc'

    # cron job for missing delivery_note_no
    @api.model
    def update_cc_create_delivery_history(self):
        data_obj = self.env['bsg_vehicle_cargo_sale_line'].search(
            [('add_to_cc', '=', True), ('state', '=', 'Delivered')], limit=300)
        count = 0
        _logger.info("Total Count : " + str(len(data_obj)))
        for rec in data_obj:
            _logger.info("Cargo Sale Line : " + str(rec.id))
            rec.cc_create_delivery_history()
            count = count + 1
            _logger.info("Iteration : " + str(count))

    @api.model
    def _cron_update_delivery_note_no(self):
        for data in self.search([('delivery_note_no', '=', False)], limit=1000):
            next_seq_code = self.env['ir.sequence'].with_context(
                force_company=self.env.user.company_id.id).next_by_code(
                'bsg_vehicle_cargo_sale_line_delivery')
            if data.loc_to:
                data.write({'delivery_note_no': str(
                    data.loc_to.branch_no) + str(next_seq_code),
                            'release_date': fields.datetime.now()})
            if data.return_loc_to:
                data.write({'delivery_note_no': str(
                    data.return_loc_to.branch_no) + str(next_seq_code),
                            'release_date': fields.datetime.now()})

    # for getting price of demmuurage invoice price
    #
    def _get_demmurage_charge(self):
        for rec in self:
            rec.without_discount_price = 0
            if rec.state not in ['done', 'released', 'cancel'] and rec.delivery_date:
                rec.without_discount_price = rec.calculating_demurrage_cost()

    # Get default option for cargo_service_id
    @api.model
    def _default_cargo_service(self):
        return self.env.user.company_id.cargo_service_id.id

    #
    @api.depends('car_make', 'unit_charge', 'discount', 'tax_ids', 'amount_with_satah', 'additional_ship_amount')
    def _get_price_reduce(self):
        for rec in self:
            rec.charges = 0.0
            rec.discount_price = 0.0
            rec.tax_amount = 0.0
            rec.original_charges = 0.0
            if rec.car_make and rec.car_model:
                rec.charges = rec.unit_charge * (1.0 - rec.discount / 100.0)
                rec.charges = rec.charges + rec.additional_ship_amount
                rec.discount_price = rec.unit_charge * (rec.discount / 100.0)
                if rec.tax_ids:
                    currency = rec.bsg_cargo_sale_id.currency_id or None
                    quantity = 1
                    product = rec.service_type.product_variant_id
                    taxes = rec.tax_ids.compute_all((rec.charges + rec.amount_with_satah), currency, quantity,
                                                    product=product, partner=rec.customer_id)
                    rec.charges = taxes['total_included']
                    if rec.bsg_cargo_sale_id.cargo_sale_type == 'international':
                        rec.tax_amount = 0
                    else:
                        rec.tax_amount = taxes['total_included'] - \
                                         taxes['total_excluded']
                if rec.bsg_cargo_sale_id.company_currency_id.id != rec.bsg_cargo_sale_id.currency_id.id:
                    rec.original_charges = rec.bsg_cargo_sale_id.currency_id._convert(
                        rec.charges, rec.bsg_cargo_sale_id.company_currency_id, rec.env.user.company_id,
                        rec.bsg_cargo_sale_id.order_date)
                else:
                    rec.original_charges = rec.charges


    def _get_invoice_amount(self):
        if self.bsg_cargo_sale_id.invoice_ids:
            search_id = self.env['account.payment'].search([('payment_type', '=', 'inbound'), (
                'communication', '=', self.bsg_cargo_sale_id.invoice_ids[0].reference)])
            return search_id.amount


    def _get_payment_no(self):
        if self.bsg_cargo_sale_id.invoice_ids:
            search_id = self.env['account.payment'].search([('payment_type', '=', 'inbound'), (
                'communication', '=', self.bsg_cargo_sale_id.invoice_ids[0].reference)])
            return search_id.name

        #


    @api.depends('discount', 'tax_amount', 'charges')
    def _get_total_witout_tax(self):
        for rec in self:
            total_without_tax = rec.charges - rec.tax_amount
            rec.total_without_tax = total_without_tax

        # if self.price_line_id:
        # 	if self.total_without_tax < self.price_line_id.min_price:
        # 		self.total_without_tax = self.price_line_id.min_price


    #
    def _get_invoice_state(self):
        for rec in self:
            rec.invoie_state = False
            rec.other_invoice_state = False
            if rec.bsg_cargo_sale_id and rec.bsg_cargo_sale_id.invoice_ids:
                inv_states = rec.bsg_cargo_sale_id.invoice_ids.mapped('payment_state')
                inv_states = [
                    state for state in inv_states if state in ['paid', 'not_paid']]
                if inv_states:
                    if 'not_paid' in inv_states:
                        rec.invoie_state = 'not_paid'
                    else:
                        rec.invoie_state = 'paid'

            if rec.bsg_cargo_sale_id:
                other_service_invoice = rec.env['account.move'].search(
                    [('invoice_origin', '=', rec.bsg_cargo_sale_id.name), ('is_other_service_invoice', '=', True)], limit=1)
                if other_service_invoice:
                    if other_service_invoice.payment_state == 'paid':
                        rec.other_invoice_state = other_service_invoice[0].state


    # returning only so amount
    def _getting_so_amount(self):
        so_amount = 0
        if self.bsg_cargo_sale_id.is_old_order:
            if self.bsg_cargo_sale_id and self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
                for data in self.bsg_cargo_sale_id.invoice_ids:
                    so_amount += data.amount_residual
        elif self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
            so_amount = sum(self.invoice_line_ids.filtered(
                lambda s: not s.is_other_service_line and not s.is_refund and not s.is_demurrage_line).mapped(
                'price_total')) - sum(self.invoice_line_ids.filtered(
                lambda s: not s.is_other_service_line and not s.is_refund and not s.is_demurrage_line).mapped(
                'paid_amount'))
        if self.bsg_cargo_return_sale_id and self.bsg_cargo_return_sale_id.payment_method.payment_type in ['cash', 'pod']:
            for data in self.bsg_cargo_return_sale_id.invoice_ids:
                so_amount += data.amount_residual
        return so_amount


    # returning only demurrage amount
    def _getting_demurrage_amount(self):
        demurrage_amount = 0
        if self.demurrage_invoice_id:
            demurrage_amount += self.demurrage_invoice_id.amount_residual
        else:
            demurrage_amount += self.final_price
        return demurrage_amount


    # returning only other service amount
    def _getting_other_service_amount(self):
        other_service_amount = 0
        if self.bsg_cargo_sale_id.is_old_order:
            if self.bsg_cargo_sale_id and self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
                for other_service_invoice_data in self.env['account.move'].search(
                        [('ref', '=', self.bsg_cargo_sale_id.name), ('is_other_service_invoice', '=', True)]):
                    if other_service_invoice_data:
                        if other_service_invoice_data.payment_state != 'paid':
                            other_service_amount += other_service_invoice_data.amount_residual
        elif self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
            other_service_amount += sum(
                self.invoice_line_ids.filtered(lambda s: s.is_other_service_line and not s.is_refund).mapped(
                    'price_total')) - sum(
                self.invoice_line_ids.filtered(lambda s: s.is_other_service_line).mapped('paid_amount'))
        if self.bsg_cargo_return_sale_id and self.bsg_cargo_return_sale_id.payment_method.payment_type in ['cash', 'pod']:
            for other_service_invoice_data in self.env['account.move'].search(
                    [('ref', '=', self.bsg_cargo_return_sale_id.name), ('is_other_service_invoice', '=', True)]):
                if other_service_invoice_data:
                    if other_service_invoice_data.payment_state != 'paid':
                        other_service_amount += other_service_invoice_data.amount_residual
        return other_service_amount


    # for getting dynamic warning message as need by mr.khalid
    #
    def _get_warning_message(self):
        for rec in self:
            due_amount = rec.getting_due_amount()
            rec.warning_so_amount = 0
            rec.warning_demurrage_amount = 0
            rec.warning_other_service_amount = 0
            if due_amount == 0:
                rec.is_warning_message = True
                # self.warning_message = False
            else:
                so_amount = rec._getting_so_amount()
                demurrage_amount = rec._getting_demurrage_amount()
                other_service_amount = rec._getting_other_service_amount()
                rec.is_warning_message = False
                rec.warning_so_amount = so_amount
                rec.warning_demurrage_amount = demurrage_amount
                rec.warning_other_service_amount = other_service_amount
            # self.warning_message = 'Warning you have SO amount' + '<span >' + str(so_amount) +'</span> '  + 'and you have Demerage Fees' + ' ' + str(demurrage_amount) + ' ' + ',Other Service' + ' ' + str(other_service_amount)


    #
    def _get_satah_amount(self):
        for rec in self:
            search_id = self.env['satah.vehicale.list'].search(
                [('cargo_sale_id', '=', rec.bsg_cargo_sale_id.id), ('plate_no', '=', rec.general_plate_no),
                 ('type', '=', rec.type)], limit=1)
            rec.amount_with_satah = search_id.final_amount
            rec._get_price_reduce()


    def _get_current_user(self):
        user_ids = self.env['res.users'].search([('id', '=', self._uid)])
        if user_ids:
            return user_ids.name


    def _get_receiver_mob_change(self):
        if self.env.user.has_group('bsg_cargo_sale.group_change_receiver_mob_number'):
            self.is_change_receiver_mob = True
        else:
            self.is_change_receiver_mob = False


    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency",
                                  related='bsg_cargo_sale_id.currency_id', store=True)

    sale_line_rec_name = fields.Char(
        string="Rec Name", compute="_compute_name", store=True)
    cargo_sale_line_name = fields.Char(string="Cargo Sale Line Name")
    bsg_cargo_sale_id = fields.Many2one(string="Cargo Sale ID", comodel_name="bsg_vehicle_cargo_sale",
                                        ondelete="cascade", track_visibility=True, )
    receiver_name = fields.Char(
        string="Receiver Name", related="bsg_cargo_sale_id.receiver_name", store=True, track_visibility=True, )
    act_receiver_name = fields.Char(
        string="Actual Receiver Name", track_visibility=True, )
    receiver_mob_country_code = fields.Selection(related="bsg_cargo_sale_id.receiver_mob_country_code", store=True)
    receiver_mob_no = fields.Char(
        string="Receiver Mobile No", related="bsg_cargo_sale_id.receiver_mob_no", store=True,
        search='_search_receiver_mob_no')
    payment_method = fields.Many2one('cargo_payment_method', string="Payment Method",
                                     related="bsg_cargo_sale_id.payment_method", store=True)
    customer_contract = fields.Many2one('bsg_customer_contract', string="Select Contract",
                                        related="bsg_cargo_sale_id.customer_contract", store=True)

    invoie_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
    ], string='Invoice Status', readonly=True, compute=_get_invoice_state, track_visibility=True)
    invoice_state_stored = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
    ], string='Invoice Status', readonly=True, help='Technical field used to store value of invoie_state')

    other_invoice_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
    ], string='Other Invoice Status', readonly=True, compute=_get_invoice_state, track_visibility=True)

    loc_from = fields.Many2one(string="From", comodel_name="bsg_route_waypoints", related="bsg_cargo_sale_id.loc_from",
                               store=True, track_visibility=True, )
    loc_from_branch_id = fields.Many2one(
        related="loc_from.loc_branch_id", store=True, track_visibility=True, )
    loc_to = fields.Many2one(string="To", comodel_name="bsg_route_waypoints", related="bsg_cargo_sale_id.loc_to",
                             store=True, track_visibility=True, )

    return_loc_from = fields.Many2one(string="Return From", comodel_name="bsg_route_waypoints",
                                      related="bsg_cargo_return_sale_id.return_loc_from",
                                      store=True, track_visibility=True, )
    return_loc_to = fields.Many2one(string="Return To", comodel_name="bsg_route_waypoints",
                                    related="bsg_cargo_return_sale_id.return_loc_to",
                                    store=True, track_visibility=True, )

    order_date = fields.Datetime(
        string="Order Date", related="bsg_cargo_sale_id.order_date", store=True, track_visibility=True, )
    deliver_date = fields.Date(string="Expected Delivery Date",
                               related="bsg_cargo_sale_id.deliver_date", store=True, track_visibility=True, )
    pickup_loc = fields.Many2one(
        string="Pickup Location", comodel_name="bsg_route_waypoints", track_visibility=True, )
    delivery_note_no = fields.Char(string="Delivery Note #")
    drop_loc = fields.Many2one(
        string="Drop", comodel_name="bsg_route_waypoints", track_visibility=True, )

    bsg_cargo_sale_payment = fields.Many2one(
        related="bsg_cargo_sale_id.payment_method", store=True, track_visibility=True)
    bsg_cargo_return_sale_id = fields.Many2one(string="Cargo Return Sale ID", comodel_name="bsg_vehicle_cargo_sale",
                                               ondelete="cascade", track_visibility=True, )
    car_make = fields.Many2one(
        string="Car Maker", comodel_name="bsg_car_config", track_visibility=True)
    car_model = fields.Many2one(
        string="Model", comodel_name="bsg_car_model", track_visibility=True, )
    car_size = fields.Many2one(
        string="Car Size", store=True, comodel_name="bsg_car_size")
    car_classfication = fields.Many2one(string="Car Classfication", comodel_name="bsg_car_classfication")
    shipment_type = fields.Many2one(
        string="Shipment Type", comodel_name="bsg.car.shipment.type")
    customer_id = fields.Many2one(
        'res.partner', related="bsg_cargo_sale_id.customer", store=True)
    year = fields.Many2one(
        string="Year", comodel_name="bsg.car.year", track_visibility='onchange')
    car_color = fields.Many2one(
        string="Color", comodel_name="bsg_vehicle_color", track_visibility=True)
    chassis_no = fields.Char(string="Chassis No", track_visibility=True, )
    # this is saudi plate no
    plate_no = fields.Char(string="Plate No", size=4, track_visibility=True, )
    # this deponds upon saudi and non saudi plate number it will fetch data form saudi and non saudi
    general_plate_no = fields.Char(
        string="Plate No#", compute="_compute_plate_no", store=True, track_visibility=True, )
    ar_plate_no = fields.Char(
        string="Plate No#", compute="_compute_plate_no", store=True, track_visibility=True, )
    # this is non saudi plate no
    non_saudi_plate_no = fields.Char(
        string="Plate No.", track_visibility=True, )
    palte_one = fields.Selection([('أ', 'أ'), ('ب', 'ب'), ('ح', 'ح'), ('د', 'د'),
                                  ('ر', 'ر'), ('س', 'س'), ('ص', 'ص'), ('ط', 'ط'),
                                  ('ع', 'ع'), ('ق', 'ق'), ('ك', 'ك'), ('ل', 'ل'),
                                  ('م', 'م'), ('ن', 'ن'), ('ه', 'هـ'), ('و', 'و'), ('ى', 'ى')], track_visibility=True,
                                 )
    palte_second = fields.Selection([('أ', 'أ'), ('ب', 'ب'), ('ح', 'ح'), ('د', 'د'),
                                     ('ر', 'ر'), ('س', 'س'), ('ص', 'ص'), ('ط', 'ط'),
                                     ('ع', 'ع'), ('ق', 'ق'), ('ك', 'ك'), ('ل', 'ل'),
                                     ('م', 'م'), ('ن', 'ن'), ('ه', 'هـ'), ('و', 'و'), ('ى', 'ى')], track_visibility=True,
                                    )
    palte_third = fields.Selection([('أ', 'أ'), ('ب', 'ب'), ('ح', 'ح'), ('د', 'د'),
                                    ('ر', 'ر'), ('س', 'س'), ('ص', 'ص'), ('ط', 'ط'),
                                    ('ع', 'ع'), ('ق', 'ق'), ('ك', 'ك'), ('ل', 'ل'),
                                    ('م', 'م'), ('ن', 'ن'), ('ه', 'هـ'), ('و', 'و'), ('ى', 'ى')], track_visibility=True,
                                   )

    plate_type = fields.Many2one(
        string="Plate Type", comodel_name="bsg_plate_config")
    plate_registration = fields.Selection(
        [('saudi', 'لوحة سعودية'), ('non-saudi', 'لوحة أخرى '),
         ('new_vehicle', 'بدون لوحة')],
        default='saudi', track_visibility=True, )
    # service_type = fields.Many2one(string="Service", comodel_name="product.template",
    #                                default=lambda self: self.env['product.template'].search(
    #                                    [('name', 'in', ['Cargo Service', 'Cargo'])], limit=1).id)
    service_type = fields.Many2one(
        string="Cargo Service", comodel_name="product.template", track_visibility=True, )
    service_type_name = fields.Char(
        string="Service", related="service_type.name")
    inspection_id = fields.Many2one(
        "bassami.inspection", "Inspection", track_visibility=True, )
    unit_charge = fields.Float(string="Unit Charges", digits=dp.get_precision(
        'Cargo Sale'), track_visibility=True, )  # _get_price
    charges = fields.Float(string="Charges", compute='_get_price_reduce',
                           digits=dp.get_precision('Cargo Sale'), track_visibility=True)
    charges_stored = fields.Float(
        'charges', help="techincal field to store value of field cahrges")
    other_service_amount = fields.Float('Other Services Amount', compute="compute_other_service_amount")
    discount = fields.Float(string="Discount (%)", digits=dp.get_precision(
        'Cargo Sale'), track_visibility=True, )
    discount_price = fields.Float(string="Discount Price", digits=dp.get_precision(
        'Cargo Sale'), track_visibility=True, compute='_get_price_reduce')
    type = fields.Selection([('none', 'None'), ('pickup', 'pickup'), ('delivery', 'delivery'), ('both', 'Both')],
                            'Satah Type',
                            help="Vehicle pickup or delivery charge type", default="none", track_visibility=True, )

    account_id = fields.Many2one(string="Analytic Account", comodel_name="account.analytic.account",
                                 related="bsg_cargo_sale_id.account_id", store=True, track_visibility=True, )
    is_satah = fields.Boolean('Add Satah', track_visibility=True, )
    tax_ids = fields.Many2many('account.tax', 'account_line_tab',
                               'tab_id', 'tax_id', string="Tax", track_visibility=True, )
    tax_amount = fields.Float(compute='_get_price_reduce', digits=dp.get_precision(
        'Cargo Sale'), track_visibility=True, )
    total_without_tax = fields.Float(string="Total without Tax", compute="_get_total_witout_tax",
                                     digits=dp.get_precision('Cargo Sale'), track_visibility=True, )
    amount_with_satah = fields.Float(string="Satah Amount", compute="_get_satah_amount",
                                     digits=dp.get_precision('Cargo Sale'),
                                     track_visibility=True, )  # ,compute="_get_price_reduce"
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('registered', 'Registered'),
            ('confirm', 'Ready To Ship'),
            ('awaiting', 'Awaiting Return'),
            ('shipped', 'Shipped'),
            ('on_transit', 'On Transit'),
            ('Delivered', 'Delivered On Branch'),
            ('done', 'Done'),
            ('released', 'Released'), ('cancel_request', 'Cancel Request'),
            ('cancel', 'Declined')
        ], default='draft', track_visibility=True, )
    # re-defines the field to change the default
    sequence = fields.Integer(help="Gives the sequence of this line when "
                                   "displaying the sale order.",
                              default=9999, string="Sequence1")

    # displays sequence on the order line
    sequence2 = fields.Integer(help="Shows the sequence of this line in "
                                    "the sale order.",
                               related='sequence', readonly=True,
                               store=True, string="Sequence2")
    sale_shipment_type = fields.Selection(
        string="Agreement Type", related="bsg_cargo_sale_id.shipment_type", store=True, readonly=True)
    # Demurrage
    delivery_date = fields.Datetime(
        string='Delivery Date'
    )
    confirmation_date = fields.Datetime(
        string='Confirmation Date'
    )
    release_date = fields.Datetime(
        string='Release Date'
    )
    no_of_days = fields.Integer(string="No of Days", readonly="1")
    current_date = fields.Date(string="Today Date", readonly="1")
    is_demurrage_inovice = fields.Boolean(
        string="Deamurrate Invoice", copy=False)
    demurrage_check = fields.Boolean(
        string='Demurrage Calculated',
    )
    without_discount_price = fields.Float(
        string='Total without Discount', compute="_get_demmurage_charge")
    dummurrage_discount = fields.Float(string="Demmurrage Discount")

    final_without_tax_price = fields.Float(
        string="Total Without Tax", compute='_calcualte_final_price', digits=dp.get_precision('Cargo Sale'))
    final_price = fields.Float(
        string="Total With Tax", compute='_calcualte_final_price', digits=dp.get_precision('Cargo Sale'))
    demmurage_tax_price = fields.Float(
        string="Tax Amount", compute='_calcualte_final_price', digits=dp.get_precision('Cargo Sale'))

    final_price_stored = fields.Float(
        'Final price', help='technical field used to store value of field final_price')
    # receiver name and actually reciver name
    receiver_name = fields.Char(
        string="Receiver Name", related="bsg_cargo_sale_id.receiver_name", store=True)
    receiver_type = fields.Selection(
        string="Receiver Type", related="bsg_cargo_sale_id.receiver_type", store=True)
    receiver_nationality = fields.Many2one(string="Receiver Nationality", comodel_name="res.country",
                                           related="bsg_cargo_sale_id.receiver_nationality", store=True)
    receiver_id_type = fields.Selection(string="Receiver ID Type",
                                        related="bsg_cargo_sale_id.receiver_id_type", store=True)
    receiver_id_card_no = fields.Char(string="Receiver ID Card No",
                                      related="bsg_cargo_sale_id.receiver_id_card_no", store=True)
    receiver_visa_no = fields.Char(string="Receiver Visa No",
                                   related="bsg_cargo_sale_id.receiver_visa_no", store=True)
    receiver_mob_no = fields.Char(string="Receiver Mobile No",
                                  related="bsg_cargo_sale_id.receiver_mob_no", store=True)
    no_of_copy = fields.Integer(string='No of Copy',
                                related="bsg_cargo_sale_id.no_of_copy", store=True)
    # Actually Receiver name
    act_receiver_name = fields.Char(string="Actual Receiver Name")
    act_receiver_type = fields.Selection(string="Receiver Type", selection=[
        ('1', 'Saudi'),
        ('2', 'Non-Saudi'),
        ('3', 'Corporate'),
    ])
    act_receiver_nationality = fields.Many2one(
        string="Receiver Nationality", comodel_name="res.country")
    act_receiver_id_type = fields.Selection(string="Receiver ID Type", selection=[
        ('saudi_id_card', 'Saudi ID Card'),
        ('iqama', 'Iqama'),
        ('gcc_national', 'GCC National'),
        ('passport', 'Passport'),
        ('other', 'Other'),
    ])
    act_receiver_id_card_no = fields.Char(string="Receiver ID Card No")
    act_receiver_visa_no = fields.Char(string="Receiver Visa No")
    act_receiver_mob_no = fields.Char(
        string="Receiver Mobile No", track_visibility=True)
    act_no_of_copy = fields.Integer(string='No of Copy')
    same_as_so_customer = fields.Boolean(string="Same As Above")
    # Invoice
    demurrage_invoice_id = fields.Many2one(
        "account.move", string="Demurrage Invoice")

    invoice_ids = fields.Many2many("account.move", string='Invoices', compute="_get_invoiced", readonly=True,
                                   copy=False)
    invoice_count = fields.Integer(
        string='Invoice Count', compute='_get_invoiced', readonly=True)

    delivery_report_history_ids = fields.One2many(
        'report.history.delivery',
        'cargo_so_line_id',
        string='Delivery Report Ids',
    )

    shipment_report_history_ids = fields.One2many(
        'report.history.shipment',
        'cargo_so_line_id',
        string='Shipment Report Ids',
    )

    is_pricelist_discount = fields.Boolean(string="Is Pricelist Discount")
    is_public_pricelist = fields.Boolean(
        string="Is Pricelist Discount", related="customer_price_list.is_public", store=True)
    # don't use cargo_sale_state in any domain or view use 'sale_order_state' instead ..  by muhammad yousef
    cargo_sale_state = fields.Selection(
        related="bsg_cargo_sale_id.state", string='Carog sale State')
    sale_order_state = fields.Selection(
        [('draft', 'Draft'),
         ('registered', 'registered'),
         ('confirm', 'Confirm'),
         ('pod', 'Delivery'),
         ('done', 'Done'),
         ('awaiting', 'Awaiting Return'),
         ('shipped', 'Shipped'),
         ('on_transit', 'On Transit'),
         ('Delivered', 'Delivered'),
         ('unplanned', 'Unplanned'), ('cancel_request', 'Cancel Request'),
         ('cancel', 'Declined')
         ], string='Sale Order State', default="draft")
    fixed_discount = fields.Float(string="Fixed Discount", digits=dp.get_precision(
        'Cargo Sale'), track_visibility=True, )
    price_line_id = fields.Many2one('bsg_price_line', string='PriceLine', )
    expected_delivery = fields.Date(
        string="Expected Delivery Date", track_visibility=True)
    est_no_delivery_days = fields.Integer(string='Est No of Days', store=True)
    est_no_hours = fields.Float(string='Est No of Hours', store=True)
    est_max_no_delivery_days = fields.Integer(string='Est Max No of Days', store=True)
    est_max_no_hours = fields.Float(string='Est Max No of Hours', store=True)
    sms_sent = fields.Boolean(string='SMS Sent ?', )
    sms_confirm_sent = fields.Boolean(string='SMS Confirm Sent ?')
    track_tiny_url = fields.Char(string='SMS Confirm Sent ?')

    is_change_receiver_mob = fields.Boolean(
        string="Is Change Receiver Mobile", compute="_get_receiver_mob_change")
    change_receiver_mob = fields.Char(string="Change Mobile No")

    # for cancel reason
    single_trip_reason = fields.Many2one(
        'single.trip.cancel', 'One Way Reason')
    round_trip_reason = fields.Many2one(
        'round.trip.cancel', 'Round Trip Vehicale')

    update_stored_fields = fields.Boolean(default=False)
    additional_ship_amount = fields.Float(
        string="Additional Ship Amount", default=0)

    is_warning_message = fields.Boolean(
        string="Is Warning", compute="_get_warning_message")
    warning_so_amount = fields.Float(
        string="So Amount", compute="_get_warning_message")
    warning_demurrage_amount = fields.Float(
        string="Demurrage Amount", compute="_get_warning_message")
    warning_other_service_amount = fields.Float(
        string="Other Service Amount", compute="_get_warning_message")
    revenue_type = fields.Selection([('individual', 'Individual Revenue'), (
        'corporate', 'Corporates Revenue')], string='Revenue Type', readonly=True)
    customer_price_list = fields.Many2one(
        'product.pricelist', string="Pricelist")
    is_from_app = fields.Boolean('Is From App', readonly=True)
    is_from_contract_api = fields.Boolean('Is From Contract API', readonly=True)
    is_package = fields.Boolean('Is Package', compute='_compute_is_package', store=True, readonly=True)
    is_package_2 = fields.Boolean('Is Package', compute='_compute_is_package', store=True, readonly=True)
    qr_code = fields.Char('QR Code')
    is_qr_code_required = fields.Boolean(
        string="Is Qr Required", related="customer_price_list.is_qr_required", store=True)
    payment_ids = fields.One2many(
        'account.cargo.line.payment', 'cargo_sale_line_id', string='Payments')
    paid_amount = fields.Float(compute="_compute_paid_data", store=True)
    is_paid = fields.Boolean(compute="_compute_paid_data", store=True)
    invoice_line_ids = fields.One2many(
        'account.move.line', 'cargo_sale_line_id')
    is_old_order = fields.Boolean(
        related='bsg_cargo_sale_id.is_old_order', store=True)
    no_cargo_inv_line_to_pay = fields.Boolean(
        string="No So Invoice Line To Pay", compute="_get_validate_payment")
    no_other_inv_line_to_pay = fields.Boolean(
        string="No Other Service Invoice Line To Pay", compute="_get_validate_payment")
    no_demurrage_inv_line_to_pay = fields.Boolean(
        string="No Demurrage Invoice Line To Pay", compute="_get_validate_payment")
    payment_method_code = fields.Selection(
        [
            ('cash', 'Cash'),
            ('credit', 'Credit'),
            ('pod', 'Payment On Delivery'),
            ('bank', 'Bank Transfer'),
        ], string='Payment Method Code', related="payment_method.payment_type", track_visibility='onchange')

    revenue_amount = fields.Float('revenue amount', compute="set_so_revenue_amount", readonly=True)
    so_line_revenue_technical = fields.Float(
        'so revenue amount technical', readonly=True)
    owner_id = fields.Many2one('owner_deal_conf', string="Owner Deal")
    is_return_canceled = fields.Boolean('Is Return Trip Canceled')
    original_charges = fields.Float(string="Origin Charges", compute='_get_price_reduce',
                                    digits=dp.get_precision('Cargo Sale'), track_visibility=True)
    company_currency_id = fields.Many2one(string="Company Currency", comodel_name="res.currency",
                                          default=lambda self: self.env.user.company_id.currency_id.id)
    is_currency_diff = fields.Boolean(
        related='bsg_cargo_sale_id.is_currency_diff', store=True)
    return_intiated = fields.Boolean()
    shipping_source_id = fields.Many2one(
        string="Shipping Source", comodel_name="bsg_vehicle_cargo_sale", track_visibility=True)
    return_source_id = fields.Many2one(
        string="Return Source", comodel_name="bsg_vehicle_cargo_sale", track_visibility=True)
    qitaf_coupon = fields.Char('Coupon Code')
    coupon_readonly = fields.Boolean()
    recieved_from_customer_date = fields.Datetime('Date Recieved From Customer')
    other_service_ids = fields.One2many('other_service_items', 'cargo_sale_line_id')
    partner_add_to_trip_id = fields.Many2one('res.partner', string="User add to trip")
    sms_otp = fields.Char("SMS Verfication Code")
    check_sales_team_update = fields.Boolean(string="Check Sales Team Update", compute="get_sales_team_update_check")


    @api.depends('state')
    def get_sales_team_update_check(self):
        for rec in self:
            rec.check_sales_team_update = False
            if rec.env.user.has_group("bsg_cargo_sale.group_sales_team_update") or rec.state in ['draft', 'registered',
                                                                                                 'confirm']:
                rec.check_sales_team_update = True
            else:
                rec.check_sales_team_update = False


    # SQL Constraints
    _sql_constraints = [(
        'cargo_sale_order_line_plate_chasis_uniq',
        'unique(bsg_cargo_sale_id,chassis_no,plate_no)',
        'Duplicate record in order line is not allowed !'
    ),
        (
            'csol_saudi_plate_uniq',
            'unique(bsg_cargo_sale_id,palte_one,palte_second,palte_third,plate_no)',
            'Plate No is duplicated and its not allowed !'
        ),
        (
            'csol_non_saudi_plate_uniq',
            'unique(bsg_cargo_sale_id,non_saudi_plate_no)',
            'Plate No is duplicated and its not allowed !'
        ),
    ]


    # Add constrains To Not Duplicate Same Car Shipping
    #
    # @api.constrains('shipment_type','plate_registration','chassis_no', 'plate_no','palte_one','palte_second','palte_third','non_saudi_plate_no')
    # def _check_for_car_duplicate(self):
    #     sale_line_ids = False
    #     if self.plate_registration == 'saudi':
    #         sale_line_ids = self.env['bsg_vehicle_cargo_sale_line'].sudo().search(
    #             [('plate_no','=',self.plate_no),('palte_one','=',self.palte_one),('palte_second','=',self.palte_second),('palte_third','=',self.palte_third),('id','!=',self.id),
    #             ('state','in',['draft','confirm','registered']),('shipment_type','=',self.shipment_type.id),('plate_registration','=',self.plate_registration)]
    #         )
    #     elif self.plate_registration == 'non-saudi':
    #         sale_line_ids = self.env['bsg_vehicle_cargo_sale_line'].sudo().search(
    #             [('non_saudi_plate_no','=',self.non_saudi_plate_no),('id','!=',self.id),('state','in',['draft','confirm','registered'])
    #             ,('shipment_type','=',self.shipment_type.id),('plate_registration','=',self.plate_registration)]
    #         )
    #     #elif self.plate_registration == 'new_vehicle':
    #     #    sale_line_ids = self.env['bsg_vehicle_cargo_sale_line'].sudo().search([('chassis_no','=',self.chassis_no),('id','!=',self.id),('state','in',['draft','confirm','registered'])
    #     #    ,('shipment_type','=',self.shipment_type.id),('plate_registration','=',self.plate_registration)])
    #     if sale_line_ids:
    #         raise UserError(
    #         		_('Sorry, There is already order for this car : %s')%(str(sale_line_ids.mapped('sale_line_rec_name')).replace(']','').replace('[','').replace("'",'')),
    #          	)

    @api.depends('bsg_cargo_sale_id.other_service_line_ids.cost')
    def compute_other_service_amount(self):
        for rec in self:
            rec.other_service_amount = 0
            amount = 0
            lines = rec.bsg_cargo_sale_id.other_service_line_ids
            if lines:
                others = lines.filtered(lambda l: l.cargo_sale_line_id == rec)
                if others:
                    amount = sum(others.mapped('without_tax_amount'))
            rec.other_service_amount = amount


    @api.model
    def _search_receiver_mob_no(self, operator, operand):
        # Users might search using mobile with/out 0 prefix..
        if operator == '=' and operand:
            return [('receiver_mob_no', 'in', [operand, operand[-9:]])]
        return [('receiver_mob_no', operator, operand)]


    @api.depends('invoice_line_ids.paid_amount', 'invoice_line_ids.is_paid')
    def _compute_paid_data(self):
        for rec in self:
            rec.is_paid = False
            rec.paid_amount = 0
            if rec.payment_ids:
                paid_amount = sum(rec.invoice_line_ids.mapped('paid_amount'))
                refund_amount = 0
                for line in rec.invoice_line_ids:
                    if line.is_refund:
                        refund_amount += line.paid_amount
                rec.paid_amount = paid_amount - refund_amount
                rec.is_paid = all(rec.invoice_line_ids.mapped('is_paid'))
            else:
                rec.is_paid = False
                rec.paid_amount = 0


    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain == [['sale_order_state', 'in', ['done', 'pod']], ['state', 'in', ['draft', 'on_transit']],
                      ['added_to_trip', '=', False], ['fleet_trip_id', '=', False]]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                domain = ['|', '|', '|',
                          ('drop_loc.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('pickup_loc.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('loc_from.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('loc_to.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('sale_order_state', 'in', ['done', 'pod']), [
                              'state', 'in', ['draft', 'on_transit']], ['added_to_trip', '=', False],
                          ('fleet_trip_id', '=', False)]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                domain = [['sale_order_state', 'in', ['done', 'pod']], ['state', 'in', [
                    'draft', 'on_transit']], ['added_to_trip', '=', False], ['fleet_trip_id', '=', False]]
        elif domain == [['state', '=', 'Delivered']]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                domain = ['|', '|', '|',
                          ('drop_loc.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('pickup_loc.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('loc_from.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('loc_to.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('state', '=', 'Delivered')]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                domain = [('state', '=', 'Delivered')]
        elif domain == [['added_to_trip', '=', True], ['fleet_trip_id', '!=', False]]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                domain = ['|', '|', '|',
                          ('drop_loc.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('pickup_loc.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('loc_from.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('loc_to.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('added_to_trip', '=', True), ('fleet_trip_id', '!=', False)]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                domain = [('added_to_trip', '=', True),
                          ('fleet_trip_id', '!=', False)]
        elif domain == ['|', ['sale_order_state', 'in', ['done', 'pod', 'Delivered']],
                        ['bsg_cargo_return_sale_id', '!=', False],
                        ['state', 'in', ['draft', 'on_transit', 'Delivered', 'shipped', 'done', 'released']],
                        ['bsg_cargo_sale_payment', '=', 'cash']]:
            domain = [('bsg_cargo_sale_payment.payment_type', '=', 'cash')]
        elif domain == ['|', ['sale_order_state', 'in', ['done', 'pod', 'Delivered']],
                        ['bsg_cargo_return_sale_id', '!=', False],
                        ['state', 'in', ['draft', 'on_transit', 'Delivered', 'shipped', 'done', 'released']],
                        ['bsg_cargo_sale_payment', '=', 'credit']]:
            domain = [('bsg_cargo_sale_payment.payment_type', '=', 'credit')]
        elif domain == ['|', ['sale_order_state', 'in', ['done', 'pod', 'Delivered']],
                        ['bsg_cargo_return_sale_id', '!=', False],
                        ['state', 'in', ['draft', 'on_transit', 'Delivered', 'shipped', 'done', 'released']],
                        ['bsg_cargo_sale_payment', '=', 'pod']]:
            domain = [('bsg_cargo_sale_payment.payment_type', '=', 'pod')]
        elif not domain:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                domain = ['|', '|', '|',
                          ('drop_loc.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('pickup_loc.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('loc_from.loc_branch_id', '=',
                           self.env.user.user_branch_id.id),
                          ('loc_to.loc_branch_id', '=', self.env.user.user_branch_id.id)]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                domain = []
        res = super(bsg_vehicle_cargo_sale_line, self).search_read(
            domain, fields, offset, limit, order)
        return res


    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        if args == [['sale_order_state', 'in', ['done', 'pod']], ['state', 'in', ['draft', 'on_transit']],
                    ['added_to_trip', '=', False], ['fleet_trip_id', '=', False]]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                args += ['|', '|', '|',
                         ('drop_loc.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('pickup_loc.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('loc_from.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('loc_to.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('sale_order_state', 'in', ['done', 'pod']), [
                             'state', 'in', ['draft', 'on_transit']], ['added_to_trip', '=', False],
                         ('fleet_trip_id', '=', False)]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                args += [['sale_order_state', 'in', ['done', 'pod']], ['state', 'in', ['draft',
                                                                                       'on_transit']],
                         ['added_to_trip', '=', False], ['fleet_trip_id', '=', False]]
        elif args == [['state', '=', 'Delivered']]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                args += ['|', '|', '|',
                         ('drop_loc.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('pickup_loc.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('loc_from.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('loc_to.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('state', '=', 'Delivered')]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                args += [('state', '=', 'Delivered')]
        elif args == [['added_to_trip', '=', True], ['fleet_trip_id', '!=', False]]:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                args += ['|', '|', '|',
                         ('drop_loc.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('pickup_loc.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('loc_from.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('loc_to.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('added_to_trip', '=', True), ('fleet_trip_id', '!=', False)]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                args += [('added_to_trip', '=', True),
                         ('fleet_trip_id', '!=', False)]
        elif args == ['|', ['sale_order_state', 'in', ['done', 'pod', 'Delivered']],
                      ['bsg_cargo_return_sale_id', '!=', False],
                      ['state', 'in', ['draft', 'on_transit', 'Delivered', 'shipped', 'done', 'released']],
                      ['bsg_cargo_sale_payment', '=', 'cash']]:
            args = [('bsg_cargo_sale_payment.payment_type', '=', 'cash')]
        elif args == ['|', ['sale_order_state', 'in', ['done', 'pod', 'Delivered']],
                      ['bsg_cargo_return_sale_id', '!=', False],
                      ['state', 'in', ['draft', 'on_transit', 'Delivered', 'shipped', 'done', 'released']],
                      ['bsg_cargo_sale_payment', '=', 'credit']]:
            args = [('bsg_cargo_sale_payment.payment_type', '=', 'credit')]
        elif args == ['|', ['sale_order_state', 'in', ['done', 'pod', 'Delivered']],
                      ['bsg_cargo_return_sale_id', '!=', False],
                      ['state', 'in', ['draft', 'on_transit', 'Delivered', 'shipped', 'done', 'released']],
                      ['bsg_cargo_sale_payment', '=', 'pod']]:
            args = [('bsg_cargo_sale_payment.payment_type', '=', 'pod')]
        elif not args:
            if self.env.user.has_group('bsg_trip_mgmt.group_register_arrival'):
                args += ['|', '|', '|',
                         ('drop_loc.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('pickup_loc.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('loc_from.loc_branch_id', '=',
                          self.env.user.user_branch_id.id),
                         ('loc_to.loc_branch_id', '=', self.env.user.user_branch_id.id)]
            elif self.env.user.has_group('bsg_cargo_sale.group_view_all_agreements'):
                args = []
        return super(bsg_vehicle_cargo_sale_line, self)._search(args, offset, limit, order, count=count,
                                                                access_rights_uid=access_rights_uid)


    @api.constrains('discount')
    @api.onchange('discount')
    def _constrains_discount(self):
        if self.customer_price_list.is_public:
            if self.env.user.has_group('bsg_cargo_sale.group_cargo_sale_line_discount'):
                if self.env.user.discount_cargo_id:
                    for rec in self:
                        if self.env.user.has_group('bsg_cargo_sale.group_cargo_sale_line_discount'):
                            if rec.discount > 0 and rec.discount > self.env.user.discount_cargo_id.discount:
                                raise Warning(
                                    _('Sorry! You are not allow to add discount more than allowed plz contact sale department !'))
                else:
                    for rec in self:
                        if rec.discount != 0:
                            raise Warning(_('you are not allow to set discount plz contact to technical support'))


    @api.onchange('customer_id')
    def _onchange_customer(self):
        if self.customer_id:
            self.customer_price_list = self.customer_id.property_product_pricelist.id


    @api.onchange('customer_price_list')
    def _onchange_customer_price_list(self):
        if self.customer_price_list and self.service_type:
            if self.customer_price_list.item_ids:
                if self.customer_price_list.item_ids.filtered(lambda l: l.product_tmpl_id.id == self.service_type.id):
                    if self.customer_price_list.item_ids.filtered(
                            lambda l: l.product_tmpl_id.id == self.service_type.id and l.compute_price == 'percentage'):
                        self.discount = max(self.customer_price_list.item_ids.filtered(lambda
                                                                                           l: l.product_tmpl_id.id == self.service_type.id and l.compute_price == 'percentage').mapped(
                            'percent_price'))
                    if self.customer_price_list.item_ids.filtered(
                            lambda l: l.product_tmpl_id.id == self.service_type.id and l.compute_price == 'fixed'):
                        self.fixed_discount = round(max(self.customer_price_list.item_ids.filtered(
                            lambda l: l.product_tmpl_id.id == self.service_type.id and l.compute_price == 'fixed').mapped(
                            'fixed_price')), 2)
                else:
                    self.discount = 0.0


    @api.onchange('shipment_type')
    def _onchange_order_price_list_domain(self):
        for rec in self:
            domain = ['|', ('location_domain', '!=', True), '|', ('loc_from_ids', '=', False),
                      ('loc_from_ids', 'in', rec.bsg_cargo_sale_id.loc_from.id),
                      '|', ('loc_to_ids', '=', False), ('loc_to_ids',
                                                        'in', rec.bsg_cargo_sale_id.loc_to.id),
                      '|', ('partner_types', '=', False), ('partner_types',
                                                           'in', rec.bsg_cargo_sale_id.partner_types.id),
                      '|', ('shipment_type', '=', False), ('shipment_type',
                                                           'in', rec.shipment_type.id),
                      '|', ('date_from', '=', False), ('date_from',
                                                       '<=', rec.bsg_cargo_sale_id.order_date),
                      '|', ('date_to', '=', False), ('date_to',
                                                     '>=', rec.bsg_cargo_sale_id.order_date),
                      '|', ('agreement_type', '=', False), ('agreement_type', '=', rec.bsg_cargo_sale_id.shipment_type)]
            if rec.customer_price_list:
                customer_price = self.env['product.pricelist'].search(domain)
                if not customer_price or rec.customer_price_list.id not in customer_price.ids:
                    rec.customer_price_list = rec.customer_id.property_product_pricelist.id
                    rec._onchange_customer_price_list()
                    rec._onchange_discount()
            if rec.loc_from and rec.loc_to:
                est_delivery_days_id = self.env['bsg.estimated.delivery.days'].search(
                    [('shipemnt_type', '=', rec.shipment_type.id), ('loc_from_id', '=', rec.loc_from.id),
                     ('loc_to_id', '=', rec.loc_to.id)], limit=1)
                rec.est_no_delivery_days = est_delivery_days_id.est_no_delivery_days
                rec.est_no_hours = est_delivery_days_id.est_no_hours
                rec.est_max_no_delivery_days = est_delivery_days_id.est_max_no_delivery_days
                rec.est_max_no_hours = est_delivery_days_id.est_max_no_hours


    @api.onchange('year')
    def _onchange_check_year(self):
        if self.year and self.bsg_cargo_sale_id.payment_method.payment_type != 'cash':
            year = self.env['ir.config_parameter'].sudo(
            ).get_param('bsg_master_config.car_year_id')
            if year and self.bsg_cargo_sale_id.shipment_type != 'return' and not self.bsg_cargo_sale_id.is_credit_customer and not self.customer_price_list.is_cash:
                car_year = self.env['bsg.car.year'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                        company_id=self.env.user.company_id.id).browse(
                    int(year))
                if int(car_year.car_year_name) > int(self.year.car_year_name):
                    return {'warning': {
                        'title': ("Warning For Year"),
                        'message': (
                                _("You Choose Car Year Less Than %s ,it's Car year in the setting ,The Payment Method will be Cash for this SO") % (
                            car_year.car_year_name))
                    }}


    #
    @api.constrains('unit_charge', 'discount', 'charges')
    def _check_amount(self):
        for order in self:
            # if order.discount != 100:
            # if order.charges == 0:
            # 	raise UserError(
            # 		_('You cant have unit price -ve value or amount not greater then 0!'),
            # 	)
            # if order.bsg_cargo_sale_id.payment_method_code != 'cash':
            # 	raise UserError(
            # 		_('not able to create credit So with discount amount "It Must be Cash Payment"'),
            # 	)
            # if order.discount != 100:
            # 	if order.charges == 0:
            # 		raise UserError(
            # 			_('You cant have unit price -ve value or amount not greater then 0!'),
            # 		)
            if not order.bsg_cargo_sale_id.is_return_so and order.charges <= 0 and self.is_package_2:
                raise UserError(
                    _('You cant have price -ve value or amount less then or equal to 0!'),
                )
            if order.unit_charge < 0:
                raise UserError(
                    _('You cant have unit price -ve value or amount not greater then 0!'),
                )
            if order.discount < 0 or order.discount > 100:
                raise UserError(
                    _('You cant have discount -ve value or discount greater then 100!'),
                )
        # if self.price_line_id:
        # if self.total_without_tax < self.price_line_id.min_price:
        # msg = 'You cant have price less then minimum price i.e %s'%(self.price_line_id.min_price)
        # raise UserError(_(msg))


    #
    # @api.constrains('year')
    # def _check_year(self):
    # 	if self.year and self.bsg_cargo_sale_id.payment_method_code != 'cash':
    # 		year = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('bsg_master_config.car_year_id')
    # 		car_year = self.env['bsg.car.year'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).browse(int(year))
    # 		if int(car_year.car_year_name) > int(self.year.car_year_name):
    # 			raise UserError(
    # 			_("You can't make Credit SO for the car year less then  Credit SO For > Car year manufacture in the setting"),
    # 			)

    #
    @api.constrains('service_type')
    def _check_service(self):
        if not self.service_type:
            raise UserError(
                _('Your Cannot Proceed without Service ..!'),
            )


    #
    @api.constrains('plate_no')
    def _check_plate_no(self):
        if self.plate_no:
            if not self.plate_no.isdigit():
                raise UserError(
                    _('Your Plate[%s] No is not correct ..!' % (str(self.plate_no))),
                )


    @api.onchange('dummurrage_discount')
    def _onchange_dummurrage_discount(self):
        if self.dummurrage_discount:
            if self.dummurrage_discount > 100:
                raise UserError(_('Demmurrage value should be less than 100'))


    # Demmurrage Calcualtion
    #
    @api.depends('without_discount_price', 'dummurrage_discount')
    def _calcualte_final_price(self):
        amount = 0
        for rec in self:
            rec.final_price = rec.final_without_tax_price = rec.demmurage_tax_price = 0
            if rec.dummurrage_discount and rec.dummurrage_discount > 0 and rec.without_discount_price > 0:
                amount = rec.without_discount_price - (
                        rec.without_discount_price * rec.dummurrage_discount / 100)
            else:
                amount = rec.without_discount_price

            product_id = rec.env['product.product'].search(
                [('is_demurrage', '=', True), ('type', '=', 'service')], limit=1)
            if not product_id:
                product_id = rec.env['product.product'].create(
                    {'name': 'Demurrage Cost', 'is_demurrage': True, 'type': 'service'})

            currency = rec.currency_id or None
            quantity = 1
            product = product_id
            taxes = product_id.taxes_id.compute_all(
                amount, currency, quantity, product, partner=rec.customer_id)
            rec.demmurage_tax_price = (
                    taxes['total_included'] - taxes['total_excluded'])
            rec.final_without_tax_price = taxes['total_excluded']

            rec.final_price = taxes['total_included']


    # Computing Plate no on basis of saudi plate no and non saudi plate no
    #
    @api.depends('plate_no', 'non_saudi_plate_no', 'palte_one', 'palte_second', 'palte_third')
    def _compute_plate_no(self):
        for rec in self:
            rec.general_plate_no = ""
            if rec.plate_no and rec.palte_one and rec.palte_second and rec.palte_third:
                if rec.env.user.lang != 'en_US':
                    rec.ar_plate_no = rec.palte_third + " " + rec.palte_second + \
                                       " " + rec.palte_one + " " + rec.plate_no
                rec.general_plate_no = rec.palte_third + " " + rec.palte_second + " " + rec.palte_one + " " + rec.plate_no
                # self.general_plate_no = self.plate_no + " " + self.palte_one + \
                #     " " + self.palte_second + " " + self.palte_third
            elif rec.non_saudi_plate_no:
                rec.general_plate_no = rec.non_saudi_plate_no
            elif rec.plate_no and rec.palte_one and rec.palte_second and rec.palte_third and rec.non_saudi_plate_no:
                raise UserError(
                    _("You can not have both saudi and non-saudi plate no at same time!"))


    # Get Invoice
    #
    @api.depends('bsg_cargo_sale_id')
    def _get_invoiced(self):
        for rec in self:
            invoice_ids = self.env['account.move'].search(
                ['|', ('cargo_sale_line_id', '=', rec.id), ('reversed_entry_id.cargo_sale_line_id', '=', rec.id)])
            rec.update({
                'invoice_count': len(set(invoice_ids.ids)),
                'invoice_ids': invoice_ids.ids,
            })


    #
    @api.depends("sequence2")
    def _compute_name(self):
        for rec in self:
            rec.sale_line_rec_name = ""
            if rec.bsg_cargo_sale_id:
                rec.sale_line_rec_name = str(
                    rec.bsg_cargo_sale_id.name) + str(rec.sequence2)
        # if self.bsg_cargo_return_sale_id:
        # 	self.sale_line_rec_name = "R"+str(self.bsg_cargo_return_sale_id.name) + str(self.sequence2)


    #
    @api.depends('sale_line_rec_name')
    def _compute_is_package(self):
        for rec in self:
            rec.is_package = False
            rec.is_package_2 = False
            if rec.sale_line_rec_name:
                if rec.sale_line_rec_name.find('P') == 0 or rec.sale_line_rec_name.find('p') == 0:
                    rec.is_package = True
                elif 'P' in rec.sale_line_rec_name or 'p' in rec.sale_line_rec_name:
                    rec.is_package = True
                else:
                    rec.is_package_2 = True


    #
    @api.onchange("car_model")
    def _get_car_size(self):
        for rec in self:
            rec.car_classfication = False
            rec.car_size = False
            if rec.car_model and rec.car_make:
                for car_line in rec.car_make.car_line_ids:
                    if car_line.car_model.id == rec.car_model.id:
                        rec.car_size = car_line.car_size.id
                        rec.car_classfication = car_line.car_classfication.id
            # self.service_type = self._default_cargo_service()


    @api.onchange('discount')
    def _onchange_discount(self):
        if self.discount:
            if self.discount >= 100:
                raise UserError(_('Discount value should be less than 100'))
            self.fixed_discount = self.unit_charge * (self.discount / 100.0)
        elif self.discount == 0.0:
            self.fixed_discount = 0.0


    # As made restict to don't allow user to enter negative value
    @api.onchange('additional_ship_amount')
    def _onchange_additional_ship_amount(self):
        if self.additional_ship_amount:
            if self.additional_ship_amount < 0:
                raise UserError(_('You should Enter More than 0 value...!'))


    # @api.onchange('service_type', 'plate_type', 'car_model', 'car_make')
    def _onchange_service_price(self):
        if self.service_type:
            if self.customer_price_list.item_ids:
                if self.customer_price_list.item_ids.filtered(lambda l: l.product_tmpl_id.id == self.service_type.id):
                    if self.customer_price_list.item_ids.filtered(
                            lambda l: l.product_tmpl_id.id == self.service_type.id and l.compute_price == 'percentage'):
                        self.discount = max(self.customer_price_list.item_ids.filtered(lambda
                                                                                           l: l.product_tmpl_id.id == self.service_type.id and l.compute_price == 'percentage').mapped(
                            'percent_price'))
                    if self.customer_price_list.item_ids.filtered(
                            lambda l: l.product_tmpl_id.id == self.service_type.id and l.compute_price == 'fixed'):
                        self.fixed_discount = round(max(self.customer_price_list.item_ids.filtered(
                            lambda l: l.product_tmpl_id.id == self.service_type.id and l.compute_price == 'fixed').mapped(
                            'fixed_price')), 2)
            if self.bsg_cargo_sale_id.customer_contract:
                if self.shipment_type:
                    if self.shipment_type.is_normal:

                        ContractLine = self.env['bsg_customer_contract_line'].search([
                            ('cust_contract_id', '=',
                             self.bsg_cargo_sale_id.customer_contract.id),
                            ('loc_from', '=', self.bsg_cargo_sale_id.loc_from.id),
                            ('loc_to', '=', self.bsg_cargo_sale_id.loc_to.id),
                            ('company_id', '=', self.env.user.company_id.id),
                            ('car_size', '=', self.car_size.id)
                        ], limit=1)
                        self.unit_charge = ContractLine.price if ContractLine else 0.0
                    else:
                        ContractLine = self.env['bsg_customer_contract_line'].search([
                            ('cust_contract_id', '=',
                             self.bsg_cargo_sale_id.customer_contract.id),
                            ('loc_from', '=', self.bsg_cargo_sale_id.loc_from.id),
                            ('loc_to', '=', self.bsg_cargo_sale_id.loc_to.id),
                            ('company_id', '=', self.env.user.company_id.id),
                            ('car_size', '=', self.shipment_type.car_size.id),
                        ], limit=1)
                        self.unit_charge = ContractLine.price if ContractLine else 0.0
                # if not self.shipment_type:
                # ContractLine = self.env['bsg_customer_contract_line'].search([
                # 	('cust_contract_id', '=', self.bsg_cargo_sale_id.customer_contract.id),
                # 	('loc_from', '=', self.bsg_cargo_sale_id.loc_from.id),
                # 	('loc_to', '=', self.bsg_cargo_sale_id.loc_to.id),
                # 	('car_size', '=', self.car_size.id)
                # ], limit=1)
                # self.unit_charge = ContractLine.price if ContractLine else 0.0

            else:
                if self.bsg_cargo_sale_id.state == 'draft' and self.state == 'draft':
                    search_id = self.env['bsg_price_line'].search([
                        ('price_config_id.waypoint_from', '=',
                         self.bsg_cargo_sale_id.loc_from.id),
                        ('price_config_id.waypoint_to', '=',
                         self.bsg_cargo_sale_id.loc_to.id),
                        ('price_config_id.customer_type', '=',
                         self.bsg_cargo_sale_id.customer_type),
                        ('service_type', '=', self.service_type.id),
                        ('car_classfication', '=', self.car_classfication.id),
                        ('car_size', '=', self.car_size.id),
                        ('company_id', '=', self.env.user.company_id.id),
                    ], limit=1)
                    self.price_line_id = search_id.id
                    if self.bsg_cargo_sale_id.shipment_type == 'return':
                        self.unit_charge = search_id.price * 2
                        self.discount = 10
                        self._onchange_discount()
                    else:
                        self.unit_charge = search_id.price
        if self.service_type:
            PinConfig = self.env.user.company_id
            # Commented as the taxes should be comming from the customer taxes
            # self.tax_ids = PinConfig.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).tax_ids.ids
            if self.bsg_cargo_sale_id.loc_from.is_international or self.bsg_cargo_sale_id.loc_to.is_international:
                self.tax_ids = [(6, 0, [])]
            else:
                self.tax_ids = PinConfig.sudo().with_context(force_company=self.env.user.company_id.id,
                                                             company_id=self.env.user.company_id.id).tax_ids.ids or self.service_type.taxes_id.ids

        for res in self.bsg_cargo_sale_id:
            if res.loc_from and res.loc_to:
                if res.customer_type == 'corporate' and res.allow_contract:
                    PriceConfig = self.env['bsg_price_config'].search([
                        ('waypoint_from', '=', res.loc_from.id),
                        ('waypoint_to', '=', res.loc_to.id),
                        ('company_id', '=', self.env.user.company_id.id),
                        ('customer_type', '=', res.customer_type),
                    ], limit=1)
                    if PriceConfig:
                        PriceLine = self.env['bsg_price_line'].search([
                            ('price_config_id', '=', PriceConfig.id),
                            ('company_id', '=', self.env.user.company_id.id),
                            # ('service_type', '=', self.service_type.id),
                            ('car_size', '=', self.car_size.id),
                            ('car_classfication', '=',
                             self.car_classfication.id),
                        ], limit=1)
                        self.price_line_id = PriceLine.id
                        self.service_type = PriceLine.service_type.id if PriceLine else self._default_cargo_service()
                        if self.bsg_cargo_sale_id.shipment_type == 'return':
                            self.unit_charge = PriceLine.price * 2 if PriceLine else 0.0
                            self.discount = 10
                            self._onchange_discount()
                        else:
                            self.unit_charge = PriceLine.price if PriceLine else 0.0
                elif res.customer_contract:
                    ContractLine = self.env['bsg_customer_contract_line'].search([
                        ('cust_contract_id', '=', res.customer_contract.id),
                        # ('service_type', '=', self.service_type.id),
                        ('loc_from', '=', res.loc_from.id),
                        ('loc_to', '=', res.loc_to.id),
                        ('company_id', '=', self.env.user.company_id.id),
                        ('car_size', '=', self.car_size.id),
                    ], limit=1)
                    self.service_type = ContractLine.service_type.id if ContractLine else self._default_cargo_service()
                    self.unit_charge = ContractLine.price if ContractLine else 0.0
                    self.service_type = ContractLine.service_type.id if ContractLine else self._default_cargo_service()
                else:
                    if self.car_size and self.car_model:
                        PriceConfig = self.env['bsg_price_config'].search([
                            ('waypoint_from', '=', res.loc_from.id),
                            ('waypoint_to', '=', res.loc_to.id),
                            ('company_id', '=', self.env.user.company_id.id),
                            ('customer_type', '=', res.customer_type),
                        ], limit=1)
                        if PriceConfig:
                            PriceLine = self.env['bsg_price_line'].search([
                                ('price_config_id', '=', PriceConfig.id),
                                ('company_id', '=', self.env.user.company_id.id),
                                # ('service_type','=',self.service_type.id),
                                ('car_classfication', '=',
                                 self.car_classfication.id),
                                ('car_size', '=', self.car_size.id),
                            ], limit=1)
                            self.price_line_id = PriceLine.id
                            self.service_type = PriceLine.service_type.id if PriceLine else self._default_cargo_service()
                            if self.bsg_cargo_sale_id.shipment_type == 'return':
                                self.unit_charge = PriceLine.price * 2 if PriceLine else 0.0
                                self.discount = 10
                                self._onchange_discount()
                            else:
                                self.unit_charge = PriceLine.price if PriceLine else 0.0
                            # self.service_type = PriceLine.service_type.id if PriceLine else self.env[
                            #     'product.template'].search([('name', 'in', ['Cargo Service', 'Cargo'])], limit=1).id
                            self.service_type = PriceLine.service_type.id if PriceLine else self._default_cargo_service()


    @api.onchange('shipment_type', 'car_model', 'car_size')
    def _onchange_shipment_type(self):
        PinConfig = self.env.ref(
            'bsg_cargo_sale.res_config_tax_data', False)
        if self.bsg_cargo_sale_id.partner_types.is_construction:
            self.discount = self.bsg_cargo_sale_id.partner_types.discount
        if self.shipment_type and self.car_size and self.car_model:
            if self.shipment_type.is_normal:
                self._onchange_service_price()
                self._set_exp_delivery_date(
                    self.bsg_cargo_sale_id.loc_from, self.bsg_cargo_sale_id.loc_to, self.car_size)
                extra_charges = 0.0
                if self.payment_method.extra_charges and self.payment_method.extra_charges > 0 and self.bsg_cargo_sale_id.partner_types.is_pod_charges:
                    extra_charges = self.payment_method.extra_charges
                if self.shipment_type.is_express_shipment and self.shipment_type.calculation_type == 'percentage' and self.shipment_type.is_normal and not self.bsg_cargo_sale_id.customer_contract:
                    self._onchange_service_price()
                    self._set_exp_delivery_date(self.bsg_cargo_sale_id.loc_from, self.bsg_cargo_sale_id.loc_to,
                                                self.car_size)
                    unit_charge = self.unit_charge
                    shipment_extra_charges = self.shipment_type.shipment_extra_charges
                    val_express_shipment = self.shipment_type.percentage_express_shipment / 100 * self.unit_charge
                    self.unit_charge = val_express_shipment + extra_charges + unit_charge + shipment_extra_charges
                elif self.shipment_type.is_express_shipment and self.shipment_type.calculation_type == 'fixed_amount' and self.shipment_type.is_normal and not self.bsg_cargo_sale_id.customer_contract:
                    self._onchange_service_price()
                    self._set_exp_delivery_date(self.bsg_cargo_sale_id.loc_from, self.bsg_cargo_sale_id.loc_to,
                                                self.car_size)
                    fixed_amount = self.shipment_type.percentage_express_shipment + self.unit_charge
                    shipment_extra_charges = self.shipment_type.shipment_extra_charges
                    self.unit_charge = fixed_amount + extra_charges + shipment_extra_charges
                elif self.shipment_type.is_normal:
                    self._onchange_service_price()
                    self._set_exp_delivery_date(self.bsg_cargo_sale_id.loc_from, self.bsg_cargo_sale_id.loc_to,
                                                self.car_size)
                    fixed_amount = extra_charges + self.unit_charge
                    self.unit_charge = fixed_amount
            else:
                self._set_exp_delivery_date(self.bsg_cargo_sale_id.loc_from,
                                            self.bsg_cargo_sale_id.loc_to, self.shipment_type.car_size)
                # if self.car_model.id not in self.shipment_type.car_model.ids:
                # 	raise UserError(_('You cant ship this Model with is type of shipment'))
                if self.bsg_cargo_sale_id.customer_contract:
                    ContractLine = self.env['bsg_customer_contract_line'].search([
                        ('cust_contract_id', '=',
                         self.bsg_cargo_sale_id.customer_contract.id),
                        # ('service_type', '=', self.service_type.id),
                        ('loc_from', '=', self.bsg_cargo_sale_id.loc_from.id),
                        ('loc_to', '=', self.bsg_cargo_sale_id.loc_to.id),
                        ('car_size', '=', self.shipment_type.car_size.id),
                    ], limit=1)
                    if ContractLine:
                        self.service_type = ContractLine.service_type.id if ContractLine else self._default_cargo_service()

                        self.unit_charge = ContractLine.price if ContractLine else 0.0
                    else:
                        raise UserError(
                            _('No pricing found for this shipment type.'))
                else:
                    PriceConfig = self.env['bsg_price_config'].search([
                        ('waypoint_from', '=', self.bsg_cargo_sale_id.loc_from.id),
                        ('waypoint_to', '=', self.bsg_cargo_sale_id.loc_to.id),
                        ('company_id', '=', self.env.user.company_id.id),
                        ('customer_type', '=',
                         self.bsg_cargo_sale_id.customer_type),
                    ], limit=1)
                    if PriceConfig:
                        PriceLine = self.env['bsg_price_line'].search([
                            ('price_config_id', '=', PriceConfig.id),
                            # ('service_type','=',self.service_type.id),
                            ('car_classfication', '=',
                             self.car_classfication.id),
                            ('company_id', '=', self.env.user.company_id.id),
                            ('car_size', '=', self.shipment_type.car_size.id),
                        ], limit=1)
                        if PriceLine:
                            self.price_line_id = PriceLine.id
                            if self.bsg_cargo_sale_id.shipment_type == 'return':
                                self.unit_charge = PriceLine.price * 2 if PriceLine else 0.0
                                self.discount = 10
                                self._onchange_discount()
                            else:
                                self.unit_charge = PriceLine.price if PriceLine else 0.0
                            # self.service_type = PriceLine.service_type.id if PriceLine else self.env[
                            #     'product.template'].search([('name', 'in', ['Cargo Service', 'Cargo'])], limit=1).id
                            self.service_type = PriceLine.service_type.id if PriceLine else self._default_cargo_service()
                        else:
                            raise UserError(
                                _('No pricing found for this shipment type.'))
                if self.service_type:
                    PinConfig = self.env.ref(
                        'bsg_cargo_sale.res_config_tax_data', False)

                if self.bsg_cargo_sale_id.loc_from.is_international or self.bsg_cargo_sale_id.loc_to.is_international:
                    self.tax_ids = [(6, 0, [])]
                else:
                    self.tax_ids = PinConfig.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                 company_id=self.env.user.company_id.id).tax_ids.ids or self.service_type.taxes_id.ids


    @api.onchange('car_make')
    def onchange_car_make(self):
        if self.car_make:
            self.car_model = False
            car_models = []
            for line in self.car_make.car_line_ids:
                car_models.append(line.car_model.id)
            return {'domain': {'car_model': [('id', 'in', car_models)]}}
        else:
            return {'domain': {'car_model': [('car_maker_id', '=', self.car_make)]}}


    @api.onchange('same_as_so_customer')
    def _onchange_same_as_customer(self):
        if self.same_as_so_customer:
            self.act_receiver_name = self.receiver_name
            self.act_receiver_type = self.receiver_type
            self.act_receiver_nationality = self.receiver_nationality
            self.act_receiver_id_type = self.receiver_id_type
            self.act_receiver_id_card_no = self.receiver_id_card_no
            self.act_receiver_visa_no = self.receiver_visa_no
            self.act_receiver_mob_no = self.receiver_mob_no


    # onchange for change mobile number as need by mr khalid
    @api.onchange('change_receiver_mob')
    def _onchange_act_receiver_mob_no(self):
        if self.change_receiver_mob:
            self.bsg_cargo_sale_id.receiver_mob_no = self.change_receiver_mob
            self.act_receiver_mob_no = self.change_receiver_mob


    @api.onchange('fixed_discount')
    def _onchange_fixed_discount(self):
        if self.fixed_discount:
            self.discount = (self.fixed_discount / self.unit_charge) * 100


    #

    def dup_line(self):
        """
            This is to copy sale order line
            """
        self.copy(default={
            'bsg_cargo_sale_id': self.bsg_cargo_sale_id.id,
            'chassis_no': "",
            'plate_no': "",
        })


    # calling from wizard
    def cancel_so_line_state_from_wizard(self):
        self.state = 'cancel'
        self.bsg_cargo_sale_id._amount_all()


    # no need to call again and again
    # for opening a wizard if match condition
    # def calling_cargo_sale_line_wizard(self):
    # 	data = {'default_id' : self.id, 'default_cargo_sale_id' : self.bsg_cargo_sale_id.id}
    # 	return {
    # 		'type': 'ir.actions.act_window',
    # 		'res_model': 'cancel_so_line_record',
    # 		'view_id'   :  self.env.ref('bsg_cargo_sale.cancel_so_line_record_form').id,
    # 		'view_mode': 'form',
    # 		'view_type': 'form',
    # 		'context' : data,
    # 		'target': 'new',
    # 	}

    # for canceling so line

    def cancel_so_line(self):
        if self.bsg_cargo_sale_id.is_credit_customer and self.state == 'draft' and not self.add_to_cc:
            if self.env.user.has_group('bsg_cargo_sale.group_cancel_branch_so') or self.env.user.has_group(
                    'bsg_cargo_sale.group_cancel_any_branch_so'):
                if self.env.user.has_group('bsg_cargo_sale.group_cancel_any_branch_so'):
                    data = {'default_id': self.id,
                            'default_cargo_sale_id': self.bsg_cargo_sale_id.id}
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'cancel_so_line_record',
                        'view_id': self.env.ref('bsg_cargo_sale.cancel_so_line_record_form').id,
                        'view_mode': 'form',
                        'view_type': 'form',
                        'context': data,
                        'target': 'new',
                    }
                elif self.env.user.has_group('bsg_cargo_sale.group_cancel_branch_so'):
                    if self.env.user.user_branch_id.id == self.bsg_cargo_sale_id.loc_from_branch_id.id:
                        data = {'default_id': self.id,
                                'default_cargo_sale_id': self.bsg_cargo_sale_id.id}
                        return {
                            'type': 'ir.actions.act_window',
                            'res_model': 'cancel_so_line_record',
                            'view_id': self.env.ref('bsg_cargo_sale.cancel_so_line_record_form').id,
                            'view_mode': 'form',
                            'view_type': 'form',
                            'context': data,
                            'target': 'new',
                        }
                    else:
                        raise UserError(
                            _("You can not cancel, Your branch not match with shipment branch...!"))
            else:
                if self.create_uid.id == self.env.user.id:
                    data = {'default_id': self.id,
                            'default_cargo_sale_id': self.bsg_cargo_sale_id.id}
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'cancel_so_line_record',
                        'view_id': self.env.ref('bsg_cargo_sale.cancel_so_line_record_form').id,
                        'view_mode': 'form',
                        'view_type': 'form',
                        'context': data,
                        'target': 'new',
                    }
                else:
                    raise UserError(
                        _("You can not cancel, Please contact Finance"))

        else:
            raise UserError(_("You can not cancel, Please contact Finance"))


    def duplicate_record(self, cargo_sale_id=False):
        """
            This is to copy sale order line
            """
        sale_id = cargo_sale_id or self.bsg_cargo_sale_id.id
        new_id = self.copy(default={
            'bsg_cargo_return_sale_id': sale_id,
            'bsg_cargo_sale_id': sale_id,
            'pickup_loc': self.bsg_cargo_sale_id.return_loc_from.id,
            'drop_loc': self.bsg_cargo_sale_id.return_loc_to.id,
            'fleet_trip_id': False,
            'added_to_trip': False,
        })
        return new_id


    def print_delivery_report_done_sate(self):
        if self.bsg_cargo_sale_id.is_old_order:
            if self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
                for data in self.bsg_cargo_sale_id.invoice_ids:
                    if data.payment_sate != 'paid' and not data.state == 'cancel':
                        raise UserError(
                            _('Please First Pay Your Cargo Invoice'))
                other_service_invoice = self.env['account.move'].search(
                    [('ref', '=', self.bsg_cargo_sale_id.name), ('is_other_service_invoice', '=', True)], limit=1)
                if other_service_invoice:
                    if other_service_invoice.state not in ['paid', 'cancel']:
                        raise UserError(
                            _('Please First Pay Your Cargo Other Service Invoice'))
        elif self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
            if not all(self.invoice_line_ids.mapped('is_paid')):
                raise UserError(_('Please First Pay Your Cargo Invoice Lines'))
        other_service_not_invoiced = self.env['other_service_items'].search(
            [('cargo_sale_id', '=', self.bsg_cargo_sale_id.id), ('cargo_sale_line_id', '=', self.id), ('cost', '>', 0),
             ('is_invoice_create', '=', False)])
        if other_service_not_invoiced:
            raise UserError(
                _('Sorry This Line Has Other Service Not Invoiced, You Must Create Invoice For It Or Delete It '))
        self.create_delivery_history()
        return self.env.ref('bsg_cargo_sale.report_cs_delivery_report').report_action(self)


    @api.model
    def _cron_update_delivery_note_no(self):
        for data in self.search([('delivery_note_no', '=', False)], limit=1000):
            next_seq_code = self.env['ir.sequence'].with_context(force_company=self.env.user.company_id.id).next_by_code(
                'bsg_vehicle_cargo_sale_line_delivery')
            if data.loc_to:
                data.write({'delivery_note_no': str(
                    data.loc_to.branch_no) + str(next_seq_code),
                            'release_date': fields.datetime.now()})
            if data.return_loc_to:
                data.write({'delivery_note_no': str(
                    data.return_loc_to.branch_no) + str(next_seq_code),
                            'release_date': fields.datetime.now()})


    # @api.model

    def calculated_no_of_days(self):
        if self.sms_otp and self.sms_otp != "verified" and self.payment_method.payment_type != "credit":
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'verify_sms_otp',
                'view_id': self.env.ref('bsg_cargo_sale.verify_sms_otp_wizard').id,
                'view_mode': 'form',
                'context': {"default_line_id": self.id},
                'target': 'new',
            }
        if not self.act_receiver_name:
            raise UserError(_("Please Fill Data of Receiver ...!"))
        if self.loc_to:
            if self.env.user.user_branch_id.id != self.loc_to.loc_branch_id.id and not self.loc_to.is_allow_to_release and self.state != 'on_transit':
                raise UserError(_("You are not authorized to Release Car!"))
        # if self.return_loc_to:
        # 	if self.env.user.user_branch_id.id != self.return_loc_to.loc_branch_id.id and not self.loc_to.is_allow_to_release:
        # 		raise UserError(_("You are not authorized to Release Car!"))
        # self.delivery_note_no = str(self.loc_to.branch_no) + str(next_seq_code)
        if self.bsg_cargo_sale_id.payment_method_code == 'credit':
            self.validate_invoice_from_wizard()
        else:
            # self.get_validation_message()
            other_service_not_invoiced = self.env['other_service_items'].search(
                [('cargo_sale_id', '=', self.bsg_cargo_sale_id.id), ('cargo_sale_line_id', '=', self.id), ('cost', '>', 0),
                 ('is_invoice_create', '=', False)])
            if other_service_not_invoiced:
                raise UserError(
                    _('Sorry This Line Has Other Service Not Invoiced, You Must Create Invoice For It Or Delete It '))

            actual_amount = self.getting_due_amount()
            if actual_amount == 0:
                # if self.loc_to and not self.delivery_note_no:
                # 	self.delivery_note_no = str(self.loc_to.branch_no) + str(next_seq_code)
                # if self.return_loc_to and not self.delivery_note_no:
                # 	self.delivery_note_no = str(self.return_loc_to.branch_no) + str(next_seq_code)
                # self.get_validation_message()
                if self.demurrage_invoice_id:
                    self.write({'is_demurrage_inovice': True})
                self.write({'state': 'released'})
            else:
                if not self.demurrage_invoice_id and self._getting_demurrage_amount():
                    demmurage_amount = self._getting_demurrage_amount()
                    message = False
                    if self._context.get('lang') == 'en_US':
                        message = 'Please First Pay Your Demmurage Amount of %s , Click Ok To Crate Demmurage Invoice' % (
                            demmurage_amount)
                    if self._context.get('lang') == 'ar_001':
                        message = 'في حالة الضغط علي موافق سيتم توليد فاتورة الارضيات لتقوم بالسداد عليها %s الرجاء دفع قيمة المبالغ المستحقة علي الاتفاقية \n في حالة ان العميل يرغب في خصم علي قيمة الارضيات برجاء التواصل مع إدارة المبيعات لعمل الخصم قبل توليد الفاتورة' % (
                            demmurage_amount)
                    data = {'default_id': self.id, 'default_msg': message}
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'change_cargo_sale_line_warning',
                        'view_id': self.env.ref('bsg_cargo_sale.change_cargo_sale_line_warning_form').id,
                        'view_mode': 'form',
                        'view_type': 'form',
                        'context': data,
                        'target': 'new',
                    }
                else:
                    raise UserError(
                        _('Please First Pay Your Due Amount of %s') % (actual_amount))


    # for calculating value
    def getting_due_amount(self):
        due_amount = 0
        if self.bsg_cargo_sale_id.is_old_order:
            if self.bsg_cargo_sale_id and self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
                for data in self.bsg_cargo_sale_id.invoice_ids:
                    if data.payment_state != 'reversed':
                        due_amount += data.amount_residual
                # if data.state != 'paid':
                # 	raise UserError(_('Please Paid first your Cargo invoice'))
                for other_service_invoice_data in self.env['account.move'].search(
                        [('ref', '=', self.bsg_cargo_sale_id.name), ('is_other_service_invoice', '=', True)]):
                    if other_service_invoice_data:
                        if other_service_invoice_data.payment_state != 'paid':
                            due_amount += other_service_invoice_data.amount_residual
        elif self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
            due_amount += sum(
                self.invoice_line_ids.filtered(lambda s: not s.is_refund and not s.is_demurrage_line).mapped(
                    'price_total')) - sum(
                self.invoice_line_ids.filtered(lambda s: not s.is_refund and not s.is_demurrage_line).mapped(
                    'paid_amount'))
        if self.bsg_cargo_return_sale_id and self.bsg_cargo_return_sale_id.payment_method.payment_type in ['cash',
                                                                                                           'pod']:
            for data in self.bsg_cargo_return_sale_id.invoice_ids:
                if data.payment_state != 'reversed':
                    due_amount += data.amount_residual
        if self.demurrage_invoice_id:
            due_amount += self.demurrage_invoice_id.amount_residual
        else:
            due_amount += self.final_price
        return due_amount


    # for creating related invoice from popup
    def validate_invoice_from_wizard(self):
        self.release_date = datetime.now()
        next_seq_code = self.env['ir.sequence'].with_context(force_company=self.env.user.company_id.id).next_by_code(
            'bsg_vehicle_cargo_sale_line_delivery')
        if not self.delivery_note_no:
            if not self.return_loc_to:
                self.release_date = fields.datetime.now()
                self.delivery_note_no = str(
                    self.loc_to.branch_no) + str(next_seq_code)
            if self.return_loc_to:
                if not self.delivery_note_no:
                    self.release_date = fields.datetime.now()
                    self.delivery_note_no = str(
                        self.return_loc_to.branch_no) + str(next_seq_code)
        self.for_normal_cargo_sale_line()


    # for validation purpose
    def get_validation_message(self):
        if self.bsg_cargo_sale_id.is_old_order:
            if self.bsg_cargo_sale_id and self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
                for data in self.bsg_cargo_sale_id.invoice_ids:
                    if data.payment_state != 'paid':
                        raise UserError(
                            _('Please First Pay  Your Cargo Invoice'))
        elif self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
            if not all(self.invoice_line_ids.mapped('is_paid')):
                raise UserError(_('Please First Pay Your Cargo Line Invoice'))
        if self.bsg_cargo_return_sale_id and self.bsg_cargo_return_sale_id.payment_method.payment_type in ['cash',
                                                                                                           'pod']:
            for data in self.bsg_cargo_return_sale_id.invoice_ids:
                if len(self.bsg_cargo_return_sale_id.invoice_ids) == 1:
                    if data.payment_state != 'paid':
                        raise UserError(
                            _('Please Paid first your Cargo invoice'))


    # for calculating value before create invoice
    def get_actually_due_amount(self):
        due_amount = 0
        if self.bsg_cargo_sale_id and self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
            for data in self.bsg_cargo_sale_id.invoice_ids:
                due_amount += data.amount_residual
            # if data.state != 'paid':
            # 	raise UserError(_('Please Paid first your Cargo invoice'))
            other_service_invoice = self.env['account.move'].search(
                [('ref', '=', self.bsg_cargo_sale_id.name), ('is_other_service_invoice', '=', True)], limit=1)
            if other_service_invoice:
                if other_service_invoice.payment_state != 'paid':
                    due_amount += self.demurrage_invoice_id.amount_residual
        if self.bsg_cargo_return_sale_id and self.bsg_cargo_return_sale_id.payment_method.payment_type in ['cash',
                                                                                                           'pod']:
            for data in self.bsg_cargo_return_sale_id.invoice_ids:
                due_amount += data.amount_residual
        demurrage_due = self.calculating_demurrage_cost()
        if demurrage_due:
            due_amount += demurrage_due
        return due_amount


    # for getting due amoutn
    # def get_due_amount(self):
    # 	due_amount = 0
    # 	if self.bsg_cargo_sale_id and self.bsg_cargo_sale_id.payment_method.payment_type in ['cash','pod']:
    # 		for data in self.bsg_cargo_sale_id.invoice_ids:
    # 			due_amount += data.residual
    # 			# if data.state != 'paid':
    # 			# 	raise UserError(_('Please Paid first your Cargo invoice'))
    # 		other_service_invoice = self.env['account.move'].search([('invoice_origin','=',self.bsg_cargo_sale_id.name),('is_other_service_invoice','=',True)],limit=1)
    # 		if other_service_invoice:
    # 			if other_service_invoice.state != 'paid':
    # 				due_amount += self.other_service_invoice.residual
    # 	if self.demurrage_invoice_id:
    # 		if self.demurrage_invoice_id.state != 'paid':
    # 			due_amount += self.demurrage_invoice_id.residual
    # 	if due_amount != 0:
    # 		raise UserError(_('Please First Pay Your Due Amount of (%s)') % (due_amount))

    # for normal cargo sale line

    def for_normal_cargo_sale_line(self):
        due_amount = self.getting_due_amount()
        if self.demurrage_invoice_id and self.demurrage_invoice_id.payment_state != 'paid':
            due_amount = self.getting_due_amount()
            if due_amount != 0:
                raise UserError(_('Please Paid first Pending invoice'))

        if not self.demurrage_invoice_id.payment_state == 'paid':
            # ((rule.chares * diff))
            self.calculating_demurrage_cost()
            if self.final_price != 0:
                if not self.bsg_cargo_sale_id.customer_contract or (
                        self.bsg_cargo_sale_id.customer_contract and self.bsg_cargo_sale_id.payment_method.payment_type in [
                    'cash', 'pod']):
                    journal_id = self.env['account.move'].new({'move_type': 'out_invoice'})._search_default_journal()
                    if not journal_id:
                        raise UserError(
                            _('Please define an accounting sales journal for this company.'))
                    currency_id = False
                    if self.bsg_cargo_sale_id.loc_to.is_international:
                        currency_id = self.bsg_cargo_sale_id.loc_to.loc_branch_id.currency_id.id
                    else:
                        currency_id = self.env.user.company_id.currency_id.id
                    invoice_vals = {
                        'name': self.sale_line_rec_name,
                        'invoice_origin': self.sale_line_rec_name,
                        'cargo_sale_id': self.bsg_cargo_sale_id.id,
                        'cargo_sale_line_id': self.id,
                        'is_demurrage_invoice': True,
                        'move_type': 'out_invoice',
                        # 'account_id': self.bsg_cargo_sale_id.customer.property_account_receivable_id.id,
                        'partner_id': self.bsg_cargo_sale_id.cargo_invoice_to.id or self.bsg_cargo_sale_id.customer.id,
                        'parent_customer_id': self.bsg_cargo_sale_id.customer.id,
                        'partner_shipping_id': self.bsg_cargo_sale_id.customer.id,
                        'journal_id': journal_id.id,
                        'currency_id': currency_id,
                        'ref': self.bsg_cargo_sale_id.note,
                        'user_id': self.bsg_cargo_sale_id.user_id and self.bsg_cargo_sale_id.user_id.id,
                    }
                    invocie_id = self.env['account.move'].create(
                        invoice_vals)

                    product_id = self.env['product.product'].search(
                        [('is_demurrage', '=', True), ('type', '=', 'service')], limit=1)

                    if not product_id:
                        product_id = self.env['product.product'].create(
                            {'name': 'Demurrage Cost', 'is_demurrage': True, 'type': 'service'})

                    invoice_line_vals = {
                        'name': str(self.sale_line_rec_name) + str(product_id.description_sale),
                        'product_id': product_id.id,
                        'account_id': product_id.property_account_income_id.id,
                        'price_unit': self.without_discount_price,
                        'quantity': 1,
                        'discount': self.dummurrage_discount,
                        'tax_ids': [(6, 0, product_id.taxes_id.ids)],
                        'move_id': invocie_id.id,
                        'cargo_sale_line_id': self.id,
                        'is_demurrage_line': True,
                        'branch_id': self.bsg_cargo_sale_id.loc_from.loc_branch_id and self.bsg_cargo_sale_id.loc_from.loc_branch_id.id or False,
                    }
                    invoice_line_ids = self.env['account.move.line'].create(
                        invoice_line_vals)
                    invocie_id._compute_amount()
                    invocie_id.action_post()
                    self.demurrage_invoice_id = invocie_id
                    self.is_demurrage_inovice = True
            else:
                self.is_demurrage_inovice = True
            self.demurrage_check = True
            if self.bsg_cargo_sale_id.payment_method_code == 'credit':
                self.write({'state': 'released'})
        else:
            if self.demurrage_invoice_id.payment_state != 'paid':
                # if self.bsg_cargo_sale_id.customer_type == 'individual':
                # if self.demurrage_invoice_id.state not in ['paid', 'cancel']:
                raise UserError(
                    _('Please Paid First Demurrage Invoice...!'))
                # else:
                #    raise UserError(
                #        _('Already Demurrage Cost Calculated and invoice is also created'))
            else:
                self.write({'is_demurrage_inovice': True, 'state': 'released'})
        # self.create_delivery_history()
        return


    def calculating_demurrage_cost(self):
        actual_charges = 0
        for data in self:  # .search([('state','not in',['draft'])]):
            if data.delivery_date and data.car_size:
                # delviery_date = datetime.strptime(str(data.delivery_date), '%Y-%m-%d')
                dlv_date = data.delivery_date.date()
                ddate = max([date for date in [data.expected_delivery, dlv_date] if date])
                delviery_date = datetime.strptime(
                    str(ddate), '%Y-%m-%d')
                today_date = datetime.strptime(
                    str(fields.Date.today()), '%Y-%m-%d')
                diff = ((today_date - delviery_date).days)
                # demurrage_rules = self.env['demurrage_charges_config'].search([
                # ])
                count_day = diff
                search_charge_id = self.env['demurrage_charges_config'].search(
                    [('chares', '=', 0.0), ('company_id', '=', self.env.user.company_id.id)], limit=1)
                if search_charge_id.ending_day_no > diff and not data.shipment_type.has_demurage_config:
                    data.write({'no_of_days': diff, 'current_date': fields.Date.today(),
                                'without_discount_price': 0})
                else:
                    car_size = data.car_size.id
                    if not data.shipment_type.is_normal and data.shipment_type.has_demurage_config:
                        car_size = data.shipment_type.car_size.id
                    demurrage_rules = self.env['demurrage_charges_config'].sudo().search(
                        [('car_size_ids', 'in', [car_size]), ('company_id', '=', self.env.user.company_id.id)])
                    if not demurrage_rules:
                        raise ValidationError(
                            _("Demurrage cost car size not configured! please contact support. so [%s] - car size [%s]" % (
                                data.sale_line_rec_name,
                                car_size and self.env['bsg_car_size'].sudo().browse(car_size).car_size_name or 'None')))
                    for rule in demurrage_rules:
                        if count_day > rule.total_day:
                            count_day -= rule.total_day
                            actual_charges += rule.chares * rule.total_day
                        else:
                            if count_day != 0:
                                actual_charges += rule.chares * count_day
                                if count_day > rule.total_day:
                                    count_day -= rule.total_day
                                else:
                                    count_day -= count_day
                    data.write({'no_of_days': diff, 'current_date': fields.Date.today(),
                                'without_discount_price': actual_charges})
        return actual_charges


    def _set_exp_delivery_date(self, loc_from, loc_to, shipment_type):
        record = self.env['bsg.estimated.delivery.days'].sudo().search(
            [('loc_from_id', '=', loc_from.id),
             ('loc_to_id', '=', loc_to.id),
             ('shipemnt_type.car_size', '=', not self.shipment_type.is_normal and shipment_type.id or False),
             ], limit=1)
        max_so_per_branch = self.env['max_daily_so_per_branch'].search([('name', '=', loc_from.loc_branch_id.id), (
            'branch_to_ids', 'in', loc_to.loc_branch_id.id), ('shipment_type_ids', 'in', self.shipment_type.id)],
                                                                       limit=1)
        cargo_sale_count = False
        max_per_day_count = False
        base_datetime = self.recieved_from_customer_date or self.order_date or datetime.now()
        if max_so_per_branch:
            max_per_day_count = max_so_per_branch.max_so_per_day
            cargo_sale_count = self.search_count([('loc_from.loc_branch_id', '=', max_so_per_branch.name.id),
                                                  ('loc_to.loc_branch_id', 'in', max_so_per_branch.branch_to_ids.ids), (
                                                      'shipment_type', 'in', max_so_per_branch.shipment_type_ids.ids),
                                                  ('order_date_date', '=', date.today()), ('state', '!=', 'cancel')])
        if record:
            if max_per_day_count and cargo_sale_count and cargo_sale_count >= max_per_day_count:
                if record.est_max_no_delivery_days != 0:
                    days = record.est_max_no_delivery_days + max_so_per_branch.number_of_day
                    self.expected_delivery = str(
                        base_datetime + timedelta(days=days, hours=record.est_max_no_hours))
                    return self.sudo().update({
                        'expected_delivery': str(base_datetime + timedelta(days=days, hours=record.est_max_no_hours)),
                        'est_no_delivery_days': record.est_no_delivery_days + max_so_per_branch.number_of_day,
                        'est_no_hours': record.est_no_hours,
                        'est_max_no_delivery_days': record.est_max_no_delivery_days + max_so_per_branch.number_of_day,
                        'est_max_no_hours': record.est_max_no_hours
                    })
                else:
                    days = record.est_no_delivery_days + max_so_per_branch.number_of_day
                    self.expected_delivery = str(
                        base_datetime + timedelta(days=days, hours=record.est_no_hours))
                    return self.sudo().update({
                        'expected_delivery': str(base_datetime + timedelta(days=days, hours=record.est_no_hours)),
                        'est_no_delivery_days': record.est_no_delivery_days + max_so_per_branch.number_of_day,
                        'est_no_hours': record.est_no_hours,
                        'est_max_no_delivery_days': record.est_max_no_delivery_days + max_so_per_branch.number_of_day,
                        'est_max_no_hours': record.est_max_no_hours
                    })
            else:
                if record.est_max_no_delivery_days != 0:
                    self.expected_delivery = str(datetime.now(
                    ) + timedelta(days=record.est_max_no_delivery_days, hours=record.est_max_no_hours))
                    return self.sudo().update({
                        'expected_delivery': str(base_datetime + timedelta(days=record.est_max_no_delivery_days,
                                                                           hours=record.est_max_no_hours)),
                        'est_no_delivery_days': record.est_no_delivery_days,
                        'est_no_hours': record.est_no_hours,
                        'est_max_no_delivery_days': record.est_max_no_delivery_days,
                        'est_max_no_hours': record.est_max_no_hours
                    })
                else:
                    self.expected_delivery = str(
                        base_datetime + timedelta(days=record.est_no_delivery_days, hours=record.est_no_hours))
                    return self.sudo().update({
                        'expected_delivery': str(base_datetime + timedelta(days=record.est_no_delivery_days,
                                                                           hours=record.est_no_hours)),
                        'est_no_delivery_days': record.est_no_delivery_days,
                        'est_no_hours': record.est_no_hours,
                        'est_max_no_delivery_days': record.est_max_no_delivery_days,
                        'est_max_no_hours': record.est_max_no_hours
                    })

        elif not record:
            record = self.env['bsg.estimated.delivery.days'].sudo().search(
                [('loc_from_id', '=', loc_from.id),
                 ('loc_to_id', '=', loc_to.id),
                 ('shipemnt_type.car_size', '=', False),
                 ], limit=1)
            if max_per_day_count and cargo_sale_count and cargo_sale_count >= max_per_day_count:
                if record.est_max_no_delivery_days != 0:
                    days = record.est_max_no_delivery_days + max_so_per_branch.number_of_day
                    self.expected_delivery = str(
                        base_datetime + timedelta(days=days, hours=record.est_max_no_hours))
                    return self.sudo().update({
                        'expected_delivery': str(datetime.now() + timedelta(days=days, hours=record.est_max_no_hours)),
                        'est_no_delivery_days': record.est_no_delivery_days + max_so_per_branch.number_of_day,
                        'est_no_hours': record.est_no_hours,
                        'est_max_no_delivery_days': record.est_max_no_delivery_days + max_so_per_branch.number_of_day,
                        'est_max_no_hours': record.est_max_no_hours
                    })
                else:
                    days = record.est_no_delivery_days + max_so_per_branch.number_of_day
                    self.expected_delivery = str(
                        base_datetime + timedelta(days=days, hours=record.est_no_hours))
                    return self.sudo().update({
                        'expected_delivery': str(base_datetime + timedelta(days=days, hours=record.est_no_hours)),
                        'est_no_delivery_days': record.est_no_delivery_days + max_so_per_branch.number_of_day,
                        'est_no_hours': record.est_no_hours,
                        'est_max_no_delivery_days': record.est_max_no_delivery_days + max_so_per_branch.number_of_day,
                        'est_max_no_hours': record.est_max_no_hours
                    })

            else:
                if record.est_max_no_delivery_days != 0:
                    self.expected_delivery = str(
                        base_datetime + timedelta(days=record.est_max_no_delivery_days, hours=record.est_max_no_hours))
                    return self.sudo().update({
                        'expected_delivery': str(datetime.now() + timedelta(days=record.est_max_no_delivery_days,
                                                                            hours=record.est_max_no_hours)),
                        'est_no_delivery_days': record.est_no_delivery_days,
                        'est_no_hours': record.est_no_hours,
                        'est_max_no_delivery_days': record.est_max_no_delivery_days,
                        'est_max_no_hours': record.est_max_no_hours
                    })
                else:
                    self.expected_delivery = str(
                        base_datetime + timedelta(days=record.est_no_delivery_days, hours=record.est_no_hours))
                    return self.sudo().update({
                        'expected_delivery': str(base_datetime + timedelta(days=record.est_no_delivery_days,
                                                                           hours=record.est_no_hours)),
                        'est_no_delivery_days': record.est_no_delivery_days,
                        'est_no_hours': record.est_no_hours,
                        'est_max_no_delivery_days': record.est_max_no_delivery_days,
                        'est_max_no_hours': record.est_max_no_hours
                    })
        else:
            self.expected_delivery = False


    @api.model
    def set_exp_delivery_date_json(self, **kwargs):
        print("**************COUT OF SHIPMENT0***********: ", kwargs)
        '''
                @param:
                    -loc_from : (int) id of bsg_route_waypoints model.
                    -loc_to : (int) id of bsg_route_waypoints model.
                    -shipment_type : (int) id of bsg.car.shipment.type model.
                    -car_size : (int) id of bsg_car_size model.
                    -shipment_date : String Of Date Format,
                @return: Json Of =>
                    {
                    'expected_delivery': string Value, 
                    'est_no_delivery_days': int Value,
                    'est_max_no_delivery_days': int Value,
                    } 
            '''
        # Return Dict
        values = {
            'expected_delivery': False,
            'est_no_delivery_days': 0,
            'est_max_no_delivery_days': 0,
            'error': ''
        }
        try:
            # Get Recordset From int Ids:
            if kwargs.get('loc_from'):
                loc_from = kwargs.get('loc_from')
            else:
                values['error'] = _("Please Provide loc_from With Param")
            if kwargs.get('loc_to'):
                loc_to = kwargs.get('loc_to')
            else:
                values['error'] = _("Please Provide loc_to With Param")
            if kwargs.get('shipment_type'):
                shipment_type = kwargs.get('shipment_type')
            else:
                values['error'] = _("Please Provide shipment_type With Param")
            if kwargs.get('car_size'):
                car_size = kwargs.get('car_size')
            else:
                values['error'] = _("Please Provide car_size With Param")
            if kwargs.get('shipment_date'):
                shipment_date = kwargs.get('shipment_date')
            else:
                values['error'] = _("Please Provide shipment_date With Param")
            if len(values['error']):
                values['Description'] = str(self.set_exp_delivery_date_json.__doc__).strip()
                return values

            loc_from = self.env['bsg_route_waypoints'].sudo().search([('id', '=', loc_from)])
            loc_to = self.env['bsg_route_waypoints'].sudo().search([('id', '=', loc_to)])
            shipment_type = self.env['bsg.car.shipment.type'].sudo().search([('id', '=', shipment_type)])
            car_size = self.env['bsg_car_size'].sudo().search([('id', '=', car_size)])
            # Convert Date:
            shipment_date = fields.Date.from_string(shipment_date)

            est_deliv_ids = self.env['bsg.estimated.delivery.days'].sudo().search(
                [('loc_from_id', '=', loc_from.zone_id.id),
                 ('loc_to_id', '=', loc_to.zone_id.id)])
            if est_deliv_ids:
                for record in est_deliv_ids:
                    if record.est_depend_car_size:
                        min_no_delivery_days = 0
                        max_no_delivery_days = 0
                        max_so_per_branch_number_of_day = 0
                        max_so_per_day = False
                        max_so_per_branch = self.env['max_daily_so_per_branch'].search(
                            [('zone_from_id', '=', loc_from.zone_id.id), (
                                'zone_to_id', '=', loc_to.zone_id.id)], limit=1)
                        if record.car_size_line:
                            for est_deliv_line_id in record.car_size_line:
                                if shipment_type.id in est_deliv_line_id.shipemnt_type.ids and car_size.id in est_deliv_line_id.car_size_ids.ids:
                                    min_no_delivery_days = est_deliv_line_id.est_min_days
                                    max_no_delivery_days = est_deliv_line_id.est_max_days + est_deliv_line_id.increment
                                    if max_so_per_branch:
                                        if max_so_per_branch.daily_max_line_ids:
                                            filter_max_daily_line = max_so_per_branch.daily_max_line_ids.filtered(lambda
                                                                                                                      r: r.shipemnt_type.ids == est_deliv_line_id.shipemnt_type.ids and r.car_size_ids.ids == est_deliv_line_id.car_size_ids.ids)
                                            if filter_max_daily_line:
                                                for max_daily_line in filter_max_daily_line:
                                                    if max_daily_line:
                                                        if est_deliv_line_id.so_details >= max_daily_line.min_days and est_deliv_line_id.so_details <= max_daily_line.max_days:
                                                            max_so_per_day = max_daily_line.max_days
                                                            max_so_per_branch_number_of_day = max_daily_line.increment
                            cargo_sale_count = False
                            max_per_day_count = False
                            if max_so_per_branch:
                                max_per_day_count = max_so_per_day
                                # cargo_sale_count = self.sudo().search_count(
                                #     [('loc_from.zone_id', '=', max_so_per_branch.zone_from_id.id),
                                #      ('loc_to.zone_id', '=', max_so_per_branch.zone_to_id.id), (
                                #          'shipment_type', 'in', max_so_per_branch.shipment_type_ids.ids),
                                #      ('shipment_date', '=', date.today()), ('state', '!=', 'cancel')])
                                shipment_type_cond = ''
                                if max_so_per_branch.shipment_type_ids:
                                    shipment_types = len(max_so_per_branch.shipment_type_ids.ids) == 1 and "(%s)" % \
                                                     max_so_per_branch.shipment_type_ids.ids[0] or str(
                                        tuple(max_so_per_branch.shipment_type_ids.ids))
                                    shipment_type_cond = f"AND so_line.shipment_type IN {shipment_types}"
                                self.env.cr.execute("""
                                            SELECT count(*)
                                            FROM bsg_vehicle_cargo_sale_line so_line,
                                            bsg_route_waypoints route_from,bsg_route_waypoints route_to
                                            WHERE so_line.loc_from IS NOT NULL AND so_line.loc_to IS NOT NULL
                                            AND so_line.shipment_type IS NOT NULL 
                                            %s
                                            AND DATE(shipment_date) = '%s'
                                            AND so_line.state != 'cancel'
                                            AND so_line.loc_from = route_from.id
                                            AND so_line.loc_to = route_to.id
                                            AND route_from.zone_id = %s
                                            AND route_to.zone_id = %s;""" \
                                                    % (shipment_type_cond, str(shipment_date),
                                                       max_so_per_branch.zone_from_id.id,
                                                       max_so_per_branch.zone_to_id.id))
                                [cargo_sale_count] = self.env.cr.fetchone()
                                _logger.info(f"**************COUT OF SHIPMENT11***********: {cargo_sale_count}")
                            if max_per_day_count and cargo_sale_count and cargo_sale_count >= max_per_day_count:
                                if max_no_delivery_days != 0:
                                    days = max_no_delivery_days + max_so_per_branch_number_of_day
                                else:
                                    days = min_no_delivery_days + max_so_per_branch_number_of_day

                            else:
                                if max_no_delivery_days != 0:
                                    days = max_no_delivery_days
                                else:
                                    days = min_no_delivery_days
                        values['expected_delivery'] = str(
                            shipment_date + timedelta(days=days, hours=record.est_max_no_hours))
                        values['est_no_delivery_days'] = min_no_delivery_days
                        values['est_max_no_delivery_days'] = max_no_delivery_days

                    else:
                        min_no_delivery_days = record.est_no_delivery_days
                        max_no_delivery_days = record.est_max_no_delivery_days
                        max_so_per_branch = self.env['max_daily_so_per_branch'].search(
                            [('zone_from_id', '=', loc_from.zone_id.id), (
                                'zone_to_id', '=', loc_to.zone_id.id),
                             ('shipment_type_ids', 'in', self.shipment_type.id)],
                            limit=1)
                        cargo_sale_count = False
                        max_per_day_count = False
                        if max_so_per_branch:
                            max_per_day_count = max_so_per_branch.max_so_per_day
                            # cargo_sale_count = self.search_count(
                            #     [('loc_from.zone_id', '=', max_so_per_branch.zone_from_id.id),
                            #      ('loc_to.zone_id', '=', max_so_per_branch.zone_to_id.id), (
                            #          'shipment_type', 'in', max_so_per_branch.shipment_type_ids.ids),
                            #      ('order_date_date', '=', date.today()), ('state', '!=', 'cancel')])
                            shipment_type_cond = ''
                            if max_so_per_branch.shipment_type_ids:
                                shipment_types = len(max_so_per_branch.shipment_type_ids.ids) == 1 and "(%s)" % \
                                                 max_so_per_branch.shipment_type_ids.ids[0] or str(
                                    tuple(max_so_per_branch.shipment_type_ids.ids))
                                shipment_type_cond = f"AND so_line.shipment_type IN {shipment_types}"
                            self.env.cr.execute("""
                                        SELECT count(*)
                                        FROM bsg_vehicle_cargo_sale_line so_line,
                                        bsg_route_waypoints route_from,bsg_route_waypoints route_to
                                        WHERE so_line.loc_from IS NOT NULL AND so_line.loc_to IS NOT NULL
                                        AND so_line.shipment_type IS NOT NULL 
                                        %s
                                        AND DATE(shipment_date) = '%s'
                                        AND so_line.state != 'cancel'
                                        AND so_line.loc_from = route_from.id
                                        AND so_line.loc_to = route_to.id
                                        AND route_from.zone_id = %s
                                        AND route_to.zone_id = %s;""" \
                                                % (shipment_type_cond, str(shipment_date),
                                                   max_so_per_branch.zone_from_id.id, max_so_per_branch.zone_to_id.id))
                            [cargo_sale_count] = self.env.cr.fetchone()
                            _logger.info("**************COUT OF SHIPMENT2***********: ", cargo_sale_count)
                        if shipment_type.id in record.shipemnt_type.ids:

                            if max_per_day_count and cargo_sale_count and cargo_sale_count >= max_per_day_count:
                                if max_no_delivery_days != 0:
                                    days = max_no_delivery_days + max_so_per_branch.number_of_day
                                else:
                                    days = min_no_delivery_days + max_so_per_branch.number_of_day
                            else:
                                if max_no_delivery_days != 0:
                                    days = max_no_delivery_days
                                else:
                                    days = min_no_delivery_days


                        elif shipment_type.id not in record.shipemnt_type.ids:
                            if max_per_day_count and cargo_sale_count and cargo_sale_count >= max_per_day_count:
                                if max_no_delivery_days != 0:
                                    days = max_no_delivery_days + max_so_per_branch.number_of_day
                                else:
                                    days = min_no_delivery_days + max_so_per_branch.number_of_day
                            else:
                                if max_no_delivery_days != 0:
                                    days = max_no_delivery_days
                                else:
                                    days = min_no_delivery_days

                        values['expected_delivery'] = str(
                            shipment_date + timedelta(days=days, hours=record.est_max_no_hours))
                        values['est_no_delivery_days'] = min_no_delivery_days
                        values['est_max_no_delivery_days'] = max_no_delivery_days
        except UserError as e:
            values['error'] = e.name or e.value
        except ValidationError as e:
            values['error'] = e.name or e.value
        except ValueError as e:
            values['error'] = e.args[0]
        except TypeError as e:
            values['error'] = e.args[0]
        except AccessError as e:
            values['error'] = e.name or e.value
        except:
            values['error'] = _("Can't Complete The Process")
        if len(values['error']):
            values['Description'] = str(self.set_exp_delivery_date_json.__doc__).strip()
        return values
        # defined by Gaga to be used on api controllers


    # defined by Gaga to be used on api controllers
    def get_expected_delivery_date(self, loc_from_id, loc_to_id, car_size, date_from, shipemnt_type):
        loc_from = self.env['bsg_route_waypoints'].browse(int(loc_from_id))
        loc_to = self.env['bsg_route_waypoints'].browse(int(loc_to_id))
        car_size = int(car_size)
        shipemnt_type = int(shipemnt_type)
        shipment_date = datetime.strptime(date_from, '%Y-%m-%d %H:%M')
        record = self.env['bsg.estimated.delivery.days'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                             company_id=self.env.user.company_id.id).search(
            [('loc_from_id', '=', loc_from.id),
             ('loc_to_id', '=', loc_to.id),
             ('shipemnt_type.car_size', '=', car_size),
             ], limit=1)
        max_so_per_branch = self.env['max_daily_so_per_branch'].search([('name', '=', loc_from.loc_branch_id.id), (
            'branch_to_ids', 'in', loc_to.loc_branch_id.id), ('shipment_type_ids', 'in', shipemnt_type)], limit=1)
        cargo_sale_count = False
        max_per_day_count = False
        if max_so_per_branch:
            max_per_day_count = max_so_per_branch.max_so_per_day
            cargo_sale_count = self.search_count([('loc_from.loc_branch_id', '=', max_so_per_branch.name.id),
                                                  ('loc_to.loc_branch_id', 'in', max_so_per_branch.branch_to_ids.ids), (
                                                      'shipment_type', 'in', max_so_per_branch.shipment_type_ids.ids),
                                                  ('order_date_date', '=', date.today())])
        if record:
            if max_per_day_count and cargo_sale_count and cargo_sale_count >= max_per_day_count:
                days = record.est_no_delivery_days  # + max_so_per_branch.number_of_day
                shipment_date = str(
                    shipment_date + timedelta(days=max_so_per_branch.number_of_day))
                expected_delivery = str(
                    shipment_date + timedelta(days=record.est_max_no_delivery_days, hours=record.est_max_no_hours))
                return {'shipment_date': str(shipment_date), 'expected_delivery_date': expected_delivery,
                        'min_days': record.est_no_delivery_days or 0, 'min_hrs': record.est_no_hours or 0,
                        'max_days': record.est_max_no_delivery_days or 0, 'max_hrs': record.est_max_no_hours or 0}
            else:
                expected_delivery = str(
                    shipment_date + timedelta(days=record.est_max_no_delivery_days, hours=record.est_max_no_hours))
                return {'shipment_date': str(shipment_date), 'expected_delivery_date': expected_delivery,
                        'min_days': record.est_no_delivery_days or 0, 'min_hrs': record.est_no_hours or 0,
                        'max_days': record.est_max_no_delivery_days or 0, 'max_hrs': record.est_max_no_hours or 0}
        elif not record:
            record = self.env['bsg.estimated.delivery.days'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                                 company_id=self.env.user.company_id.id).search(
                [('loc_from_id', '=', loc_from.id),
                 ('loc_to_id', '=', loc_to.id),
                 ('shipemnt_type.car_size', '=', False),
                 ], limit=1)
            if max_per_day_count and cargo_sale_count and cargo_sale_count >= max_per_day_count:
                days = record.est_max_no_delivery_days  # + max_so_per_branch.number_of_day
                shipment_date = str(
                    shipment_date + timedelta(days=max_so_per_branch.number_of_day))
                expected_delivery = str(
                    shipment_date + timedelta(days=days, hours=record.est_max_no_hours))
                return {'shipment_date': shipment_date, 'expected_delivery_date': expected_delivery,
                        'min_days': record.est_no_delivery_days or 0, 'min_hrs': record.est_no_hours or 0,
                        'max_days': record.est_max_no_delivery_days or 0, 'max_hrs': record.est_max_no_hours or 0}
            else:
                expected_delivery = str(
                    shipment_date + timedelta(days=record.est_max_no_delivery_days, hours=record.est_max_no_hours))
                return {'shipment_date': str(shipment_date), 'expected_delivery_date': expected_delivery,
                        'min_days': record.est_no_delivery_days or 0, 'min_hrs': record.est_no_hours or 0,
                        'max_days': record.est_max_no_delivery_days or 0, 'max_hrs': record.est_max_no_hours or 0}

        else:
            return {'shipment_date': False, 'expected_delivery_date': False, 'min_days': 0, 'min_hrs': 0, 'max_days': 0,
                    'max_hrs': 0}


    def get_seq_no(self):
        seq_no = 0
        for data in self.delivery_report_history_ids:
            seq_no = data.dr_print_no
        return seq_no


    def action_draft(self):
        return self.write({'state': 'draft'})


    def confirm_sms_setup(self):
        for rec in self:
            if rec.receiver_mob_no:
                tiny_url_obj = UrlShortenTinyurl()
                base_url = self.sudo().env['ir.config_parameter'].get_param("web.base.url")
                long_url = "%s/ar_001/track-shipment?so_id=%s&rec_mo=%s" % (
                    base_url, rec.sale_line_rec_name, rec.receiver_mob_no)
                tiny_url_obj.shorten(long_url)
                if tiny_url_obj.short_url:
                    rec.track_tiny_url = tiny_url_obj.short_url
            if not rec.confirmation_date:
                rec.confirmation_date = fields.Datetime.now()
            rec.send_confirmation_sms()
            rec.send_confirmation_sms_credit_customer()


    def action_confirm(self):
        return self.write({'state': 'confirm'})


    def action_awaiting(self):
        return self.write({'state': 'awaiting'})


    def action_shipped(self):
        return self.write({'state': 'shipped'})


    def action_on_transit(self):
        return self.write({'state': 'on_transit'})


    @api.onchange('state')
    def send_cancellation_sms(self):
        try:
            if self.state in ['cancel']:
                if self.bsg_cargo_sale_id.payment_method_code in ['cash', 'pod']:
                    model_id = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                        company_id=self.env.user.company_id.id).env['ir.model'].search(
                        [('model', '=', 'bsg_vehicle_cargo_sale_line')])
                    if model_id:
                        template_id = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                               company_id=self.env.user.company_id.id).env[
                            'send.mobile.sms.template'].search(
                            [('model_id', '=', model_id.id), ('sms_template_code', '=', 'CANCEL')], limit=1)
                        if template_id:
                            system_parameter = self.sudo(
                            ).env['ir.config_parameter'].get_param("web.base.url")
                            if system_parameter in ['https://www.albassamitransport.com',
                                                    'https://albassami.odoo.com'] or self._context.get(
                                'bypass_domain_check', False):
                                print("SMS......SENT..........")
                                response = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                    company_id=self.env.user.company_id.id).env[
                                    'send.mobile.sms.template'].send_sms(
                                    template_id, self.id)
                                # if response in ["1", 1]:
                                self.sms_sent = True
                            else:
                                print("System paramerter not correct.")
        except Exception as e:
            print("System parmerter not correct.")


    def send_delivery_sms(self):
        try:
            if (self.bsg_cargo_sale_id.payment_method_code in ['cash', 'pod'] or (
                    self.bsg_cargo_sale_id.payment_method_code == 'credit' and self.customer_id.cc_sms)) and self.shipment_type.id != 40:
                model_id = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                    company_id=self.env.user.company_id.id).env['ir.model'].search(
                    [('model', '=', 'bsg_vehicle_cargo_sale_line')])
                if model_id:
                    template_id = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                           company_id=self.env.user.company_id.id).env[
                        'send.mobile.sms.template'].search(
                        [('model_id', '=', model_id.id), ('sms_template_code', '=', 'DELIVERY')], limit=1)
                    if template_id:
                        system_parameter = self.sudo(
                        ).env['ir.config_parameter'].get_param("web.base.url")
                        if system_parameter in ['https://www.albassamitransport.com',
                                                'https://albassami.odoo.com'] or self._context.get('bypass_domain_check',
                                                                                                   False):
                            print("SMS......SENT..........")
                            response = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                company_id=self.env.user.company_id.id).env[
                                'send.mobile.sms.template'].send_sms(
                                template_id, self.id)
                            # if response in ["1", 1]:
                            self.sms_sent = True
                        else:
                            print("System parmerter not correct.")
                    if self.customer_id.cc_sms:
                        template_id = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                               company_id=self.env.user.company_id.id).env[
                            'send.mobile.sms.template'].search(
                            [('model_id', '=', model_id.id), ('sms_template_code', '=', 'DELIVERY_OWNER')], limit=1)
                        if template_id:
                            system_parameter = self.sudo(
                            ).env['ir.config_parameter'].get_param("web.base.url")
                            if system_parameter in ['https://www.albassamitransport.com',
                                                    'https://albassami.odoo.com'] or self._context.get(
                                'bypass_domain_check', False):

                                response = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                    company_id=self.env.user.company_id.id).env[
                                    'send.mobile.sms.template'].send_sms(
                                    template_id, self.id)
                                print("SMS......SENT..........", response)
                                # if response in ["1", 1]:
                                self.sms_confirm_sent = True
                            else:
                                print("System parmerter not correct.")
        except Exception as e:
            print("System parmerter not correct.")


    def send_confirmation_sms(self):
        # 8088bc8c6e19ae72982715d38c2ced525add550a
        try:
            _logger.warning("send_confirmation_sms..................above sms condition.......")
            if self.bsg_cargo_sale_id.payment_method_code in ['cash', 'pod'] and self.bsg_cargo_sale_id.state in ['confirm',
                                                                                                                  'pod',
                                                                                                                  'registered']:
                model_id = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                    company_id=self.env.user.company_id.id).env['ir.model'].search(
                    [('model', '=', 'bsg_vehicle_cargo_sale_line')])
                _logger.warning("send_confirmation_sms..................below sms condition.......")
                if model_id:
                    _logger.warning("send_confirmation_sms..................below sms condition..model id.....")
                    template_id = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                           company_id=self.env.user.company_id.id).env[
                        'send.mobile.sms.template'].search(
                        [('model_id', '=', model_id.id), ('sms_template_code', '=', 'CONFIRM')], limit=1)
                    if template_id:
                        _logger.warning("send_confirmation_sms..................below sms condition..template id.....")
                        system_parameter = self.sudo(
                        ).env['ir.config_parameter'].get_param("web.base.url")
                        if system_parameter in ['https://www.albassamitransport.com',
                                                'https://albassami.odoo.com'] or self._context.get('bypass_domain_check',
                                                                                                   False):

                            response = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                company_id=self.env.user.company_id.id).env[
                                'send.mobile.sms.template'].send_sms(
                                template_id, self.id)
                            print("SMS......SENT..........", response)
                            _logger.warning(
                                "send_confirmation_sms..................below sms condition..template id if .....")
                            # if response in ["1", 1]:
                            self.sms_confirm_sent = True
                        else:
                            _logger.warning(
                                "send_confirmation_sms..................below sms condition..template id else .....")
                            print("System parmerter not correct.")
                    if self.bsg_cargo_sale_id.customer.cc_sms:
                        _logger.warning(
                            "send_confirmation_sms..................below sms condition.. cc sms  .....")
                        template_id = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                               company_id=self.env.user.company_id.id).env[
                            'send.mobile.sms.template'].search(
                            [('model_id', '=', model_id.id), ('sms_template_code', '=', 'CONFIRM_OWNER')], limit=1)
                        if template_id:
                            _logger.warning(
                                "send_confirmation_sms..................below sms condition..template id cc sms  .....")
                            system_parameter = self.sudo(
                            ).env['ir.config_parameter'].get_param("web.base.url")
                            if system_parameter in ['https://www.albassamitransport.com',
                                                    'https://albassami.odoo.com'] or self._context.get(
                                'bypass_domain_check', False):

                                response = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                    company_id=self.env.user.company_id.id).env[
                                    'send.mobile.sms.template'].send_sms(
                                    template_id, self.id)
                                print("SMS......SENT..........", response)
                                _logger.warning(
                                    "send_confirmation_sms..................below sms condition..template id cc sms  if.....")
                                # if response in ["1", 1]:
                                self.sms_confirm_sent = True
                            else:
                                _logger.warning(
                                    "send_confirmation_sms..................below sms condition..template id cc sms else .....")
                                print("System parmerter not correct.")

        except:
            return True


    def send_confirmation_sms_credit_customer(self):
        # 8088bc8c6e19ae72982715d38c2ced525add550a
        try:
            _logger.warning("send_confirmation_sms_credit_customer..................above sms condition.......")
            if self.bsg_cargo_sale_id.payment_method_code == 'credit' and self.bsg_cargo_sale_id.customer.cc_sms:
                model_id = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                    company_id=self.env.user.company_id.id).env['ir.model'].search(
                    [('model', '=', 'bsg_vehicle_cargo_sale_line')])
                _logger.warning("send_confirmation_sms_credit_customer..................below sms condition.......")
                if model_id:
                    _logger.warning(
                        "send_confirmation_sms_credit_customer..................below sms condition..model id.....")
                    template_id = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                           company_id=self.env.user.company_id.id).env[
                        'send.mobile.sms.template'].search(
                        [('model_id', '=', model_id.id), ('sms_template_code', '=', 'CONFIRM')], limit=1)
                    if template_id:
                        _logger.warning(
                            "send_confirmation_sms_credit_customer..................below sms condition..template id.....")
                        system_parameter = self.sudo(
                        ).env['ir.config_parameter'].get_param("web.base.url")
                        if system_parameter in ['https://www.albassamitransport.com',
                                                'https://albassami.odoo.com'] or self._context.get(
                            'bypass_domain_check', False):

                            response = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                company_id=self.env.user.company_id.id).env[
                                'send.mobile.sms.template'].send_sms(
                                template_id, self.id)
                            print("SMS......SENT..........", response)
                            _logger.warning(
                                "send_confirmation_sms_credit_customer..................below sms condition..template id if .....")
                            # if response in ["1", 1]:
                            self.sms_confirm_sent = True
                        else:
                            _logger.warning(
                                "send_confirmation_sms_credit_customer..................below sms condition..template id else .....")
                            print("System parmerter not correct.")
                    if self.bsg_cargo_sale_id.customer.cc_sms:
                        _logger.warning(
                            "send_confirmation_sms_credit_customer..................below sms condition.. cc sms  .....")
                        template_id = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                               company_id=self.env.user.company_id.id).env[
                            'send.mobile.sms.template'].search(
                            [('model_id', '=', model_id.id), ('sms_template_code', '=', 'CONFIRM_OWNER')], limit=1)
                        if template_id:
                            _logger.warning(
                                "send_confirmation_sms_credit_customer..................below sms condition..template id cc sms  .....")
                            system_parameter = self.sudo(
                            ).env['ir.config_parameter'].get_param("web.base.url")
                            if system_parameter in ['https://www.albassamitransport.com',
                                                    'https://albassami.odoo.com'] or self._context.get(
                                'bypass_domain_check', False):

                                response = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                    company_id=self.env.user.company_id.id).env[
                                    'send.mobile.sms.template'].send_sms(
                                    template_id, self.id)
                                print("SMS......SENT..........", response)
                                _logger.warning(
                                    "send_confirmation_sms_credit_customer..................below sms condition..template id cc sms  if.....")
                                # if response in ["1", 1]:
                                self.sms_confirm_sent = True
                            else:
                                _logger.warning(
                                    "send_confirmation_sms_credit_customer..................below sms condition..template id cc sms else .....")
                                print("System parmerter not correct.")

        except:
            return True


    def action_Delivered(self):
        if not self.delivery_date:
            self.delivery_date = fields.Datetime.now()

        self.sms_otp = str(random.randint(100000, 999999))
        self.send_delivery_sms()
        return self.write({'state': 'Delivered', })


    def receive_from_customer(self):
        for rec in self:
            if rec.bsg_cargo_sale_id.state == 'registered':
                inv = self.env['account.move'].suod().search([('cargo_sale_id', '=', rec.bsg_cargo_sale_id.id)], limit=1)
                if not inv:
                    rec.bsg_cargo_sale_id.invoice_create_validate()
                else:
                    rec.bsg_cargo_sale_id.state = 'confirm'
                for sol in self.bsg_cargo_sale_id.order_line_ids:
                    sol.state = 'confirm'
                    sol.recieved_from_customer_date = fields.Datetime.now()
                rec.bsg_cargo_sale_id.recieved_from_customer_date = fields.Datetime.now()


    @api.model
    def cron_send_sms(self):
        system_parameter = self.env['ir.config_parameter'].get_param(
            "web.base.url")
        if system_parameter not in ['https://www.albassamitransport.com', 'https://albassami.odoo.com']:
            return True
        delivered_ids = self.env['bsg_vehicle_cargo_sale_line'].search([('bsg_cargo_sale_id.payment_method_code', 'in', [
            'cash', 'pod']), ('sms_sent', '=', False), ('state', '=', 'Delivered')], limit=1000)
        confirmed_ids = self.env['bsg_vehicle_cargo_sale_line'].search([
            ('bsg_cargo_sale_id.payment_method_code', 'in', ['cash', 'pod']), ('sms_confirm_sent', '=', False),
            ('bsg_cargo_sale_id.state', 'in', ['confirm', 'pod'])], limit=1000)
        LineRecs = set(delivered_ids + confirmed_ids)

        model_id = self.env['ir.model'].search(
            [('model', '=', 'bsg_vehicle_cargo_sale_line')])
        if model_id:
            print("...Model")
            delivery_template_id = self.env['send.mobile.sms.template'].search(
                [('model_id', '=', model_id.id), ('sms_template_code', '=', 'DELIVERY')], limit=1)
            confirm_template_id = self.env['send.mobile.sms.template'].search(
                [('model_id', '=', model_id.id), ('sms_template_code', '=', 'CONFIRM')], limit=1)
            if delivery_template_id:
                print("...Template")
            for rec in LineRecs:
                # if rec.bsg_cargo_sale_id.payment_method_code in ['cash','pod']:
                if delivery_template_id and rec.state == 'Delivered' and not rec.sms_sent and rec.shipment_type.id != 40:
                    rec.sms_sent = True
                    if rec.delivery_date:
                        difference = fields.Datetime.now() - rec.delivery_date
                        if (difference.days) <= 4:
                            response = self.env['send.mobile.sms.template'].send_sms(
                                delivery_template_id, rec.id)
                elif confirm_template_id and rec.bsg_cargo_sale_id.state in ['confirm', 'pod'] and not rec.sms_confirm_sent:
                    rec.sms_confirm_sent = True
                    if rec.confirmation_date:
                        difference = fields.Datetime.now() - rec.confirmation_date
                        if (difference.days) <= 2:
                            response = self.env['send.mobile.sms.template'].send_sms(
                                confirm_template_id, rec.id)


    def action_done(self):
        return self.write({'state': 'done'})


    def action_cancel(self):
        return self.write({'state': 'cancel'})


    # Btn for inspection of cars

    def action_inspect_view(self):
        if self.inspection_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Car Inspection',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'bassami.inspection',
                'res_id': self.inspection_id.id,
            }


    def print_shipment_data(self):
        # return self.env.ref('bsg_cargo_sale.report_shipment_data_report').report_action(self.id)

        if self.bsg_cargo_sale_id.payment_method.payment_type in ['cash']:
            for data in self.bsg_cargo_sale_id.invoice_ids:
                if data.payment_state != 'paid':
                    raise UserError(_('Please Paid first your Cargo invoice'))

        if self.bsg_cargo_sale_id.state == 'draft':
            raise UserError(
                _('Please first confirm SO then print...!'),
            )
        if self.bsg_cargo_sale_payment.display_name == 'Cash':
            if not self.bsg_cargo_sale_id.invoice_ids:
                raise UserError(
                    _('Payment Must Be Done'),
                )
            else:
                self.create_shipment_history()
                return self.env.ref('bsg_cargo_sale.report_shipment_data_report').report_action(self.id)
        else:
            self.create_shipment_history()
            return self.env.ref('bsg_cargo_sale.report_shipment_data_report').report_action(self.id)


    def print_empty_data(self):
        return self.env.ref('bsg_cargo_sale.report_shipment_empty_report').report_action(self.id)


    def action_print_inspection(self):
        if self.bsg_cargo_sale_id.state == 'draft':
            raise UserError(
                _('Please first confirm SO then print...!'),
            )

        if self.bsg_cargo_sale_id.payment_method_code == 'cash' and not self.bsg_cargo_sale_id.is_return_so:
            if not self.bsg_cargo_sale_id.invoice_ids:
                raise UserError(
                    _('Payment Must Be Done'),
                )
            if self.bsg_cargo_sale_id.invoice_ids:
                invoice_amt = sum(
                    line.amount_residual for line in self.bsg_cargo_sale_id.invoice_ids)
                if invoice_amt > 0:
                    raise UserError(
                        _('Payment Must Be Done'),
                    )
                else:
                    self.create_shipment_history()
                    return self.env.ref('bsg_cargo_sale.report_inspection_report').report_action(self.id)
        else:
            self.create_shipment_history()
            return self.env.ref('bsg_cargo_sale.report_inspection_report').report_action(self.id)


    def action_print_shipment(self):
        if self.bsg_cargo_sale_id.state == 'draft':
            raise UserError(
                _('Please first confirm SO then print...!'),
            )

        if self.bsg_cargo_sale_id.payment_method_code == 'cash' and not self.bsg_cargo_sale_id.is_return_so:
            if not self.bsg_cargo_sale_id.invoice_ids:
                raise UserError(
                    _('Payment Must Be Done'),
                )
            if self.bsg_cargo_sale_id.invoice_ids:
                invoice_amt = sum(
                    line.amount_residual for line in self.bsg_cargo_sale_id.invoice_ids)
                if invoice_amt > 0:
                    raise UserError(
                        _('Payment Must Be Done'),
                    )
                else:
                    self.create_shipment_history()
                    return self.env.ref('bsg_cargo_sale.report_shipment_report').report_action(self.id)
        else:
            self.create_shipment_history()
            return self.env.ref('bsg_cargo_sale.report_shipment_report').report_action(self.id)


    def action_print_cs_delivery(self):
        if not self.demurrage_check or not self.is_demurrage_inovice:
            raise UserError(
                _('Please release car first or calculate demmurage.'),
            )
        elif self.demurrage_check and self.is_demurrage_inovice:
            self.create_delivery_history()
            return self.env.ref('bsg_cargo_sale.report_cs_delivery_report').report_action(self.id)


    # View Invoices

    def action_view_invoice(self):
        # invoices = self.mapped('invoice_ids')
        invoices = self.env['account.move'].search(
            ['|', ('cargo_sale_line_id', '=', self.id), ('reversed_entry_id.cargo_sale_line_id', '=', self.id)])
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


    def action_email_shipment(self):
        template = self.env.ref(
            'bsg_cargo_sale.email_template_send_shipment_mail', False)
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form', False)
        ctx = dict(self.env.context or {})
        ctx = dict(
            default_model='bsg_vehicle_cargo_sale_line',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment'
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }


    def create_shipment_history(self):
        seq = 0

        if not self.shipment_report_history_ids:
            self.shipment_report_history_ids.create({
                'sr_print_no': seq,
                'sr_user_id': self.env.user.id,
                'sr_print_date': datetime.now(),
                'cargo_so_line_id': self.id,
            })
        else:
            seq = self.shipment_report_history_ids[-1].sr_print_no
            self.shipment_report_history_ids.create({
                'sr_print_no': int(seq) + 1,
                'sr_user_id': self.env.user.id,
                'sr_print_date': datetime.now(),
                'cargo_so_line_id': self.id,
            })


    def create_delivery_history(self):
        seq = 1
        next_seq_code = self.env['ir.sequence'].with_context(force_company=self.env.user.company_id.id).next_by_code(
            'bsg_vehicle_cargo_sale_line_delivery')
        if self.loc_to:
            if not self.delivery_note_no:
                self.release_date = fields.datetime.now()
                self.delivery_note_no = str(
                    self.loc_to.branch_no) + str(next_seq_code)
        if self.return_loc_to:
            if not self.delivery_note_no:
                self.release_date = fields.datetime.now()
                self.delivery_note_no = str(
                    self.return_loc_to.branch_no) + str(next_seq_code)

        if not self.delivery_report_history_ids:
            self.delivery_report_history_ids.create({
                'dr_print_no': seq,
                'dr_user_id': self.env.user.id,
                'dr_print_date': datetime.now(),
                'cargo_so_line_id': self.id,
                'act_receiver_name': self.act_receiver_name,
                'number': self.delivery_note_no,
            })
        else:
            seq = self.delivery_report_history_ids[-1].dr_print_no
            self.delivery_report_history_ids.create({
                'dr_print_no': int(seq) + 1,
                'dr_user_id': self.env.user.id,
                'dr_print_date': datetime.now(),
                'cargo_so_line_id': self.id,
                'act_receiver_name': self.act_receiver_name,
                'number': self.delivery_note_no,
            })


    def write(self, vals):
        if vals.get('change_receiver_mob'):
            self.bsg_cargo_sale_id.receiver_mob_no = vals.get(
                'change_receiver_mob')
            self.act_receiver_mob_no = vals.get('change_receiver_mob')

        # if vals.get('service_type'):
        if 1 != 1:
            if self.shipment_type.is_normal:
                self._onchange_service_price()
            # if self.bsg_cargo_sale_id.customer_contract:
            # 	ContractLine = self.env['bsg_customer_contract_line'].search([
            # 		('cust_contract_id', '=', self.bsg_cargo_sale_id.customer_contract.id),
            # 		('loc_from', '=', self.bsg_cargo_sale_id.loc_from.id),
            # 		('loc_to', '=', self.bsg_cargo_sale_id.loc_to.id),
            # 		('car_size', '=', self.car_size.id),
            # 	], limit=1)
            # 	self.unit_charge = ContractLine.price if ContractLine else 0.0
            # else:
            # 	if self.bsg_cargo_sale_id.state == 'draft' and self.state == 'draft':
            # 		search_id = self.env['bsg_price_line'].search([
            # 			('price_config_id.waypoint_from', '=', self.bsg_cargo_sale_id.loc_from.id),
            # 			('price_config_id.waypoint_to', '=', self.bsg_cargo_sale_id.loc_to.id),
            # 			('price_config_id.customer_type', '=', self.bsg_cargo_sale_id.customer_type),
            # 			('service_type', '=', self.service_type.id),
            # 			('car_classfication', '=', self.car_classfication.id),
            # 			('car_size', '=', self.car_size.id),
            # 		], limit=1)
            # 		self.price_line_id = search_id.id
            # 		if self.bsg_cargo_sale_id.shipment_type == 'return':
            # 			self.unit_charge = search_id.addtional_price
            # 		else:
            # 			self.unit_charge = search_id.price
            else:
                # if self.car_model.id not in self.shipment_type.car_model.ids:
                # 	raise UserError(_('You cant ship this Model with is type of shipment'))
                if self.bsg_cargo_sale_id.customer_contract:
                    ContractLine = self.env['bsg_customer_contract_line'].search([
                        ('cust_contract_id', '=',
                         self.bsg_cargo_sale_id.customer_contract.id),
                        ('service_type', '=', self.service_type.id),
                        ('loc_from', '=', self.bsg_cargo_sale_id.loc_from.id),
                        ('loc_to', '=', self.bsg_cargo_sale_id.loc_to.id),
                        ('car_size', '=', self.shipment_type.car_size.id),
                    ], limit=1)
                    self.unit_charge = ContractLine.price if ContractLine else 0.0
                else:
                    PriceConfig = self.env['bsg_price_config'].search([
                        ('waypoint_from', '=', self.bsg_cargo_sale_id.loc_from.id),
                        ('company_id', '=', self.env.user.company_id.id),
                        ('waypoint_to', '=', self.bsg_cargo_sale_id.loc_to.id),
                        ('customer_type', '=',
                         self.bsg_cargo_sale_id.customer_type),
                    ], limit=1)
                    if PriceConfig:
                        PriceLine = self.env['bsg_price_line'].search([
                            ('price_config_id', '=', PriceConfig.id),
                            ('company_id', '=', self.env.user.company_id.id),
                            # ('service_type','=',self.service_type.id),
                            ('car_classfication', '=',
                             self.car_classfication.id),
                            ('car_size', '=', self.shipment_type.car_size.id),
                        ], limit=1)
                        if PriceLine:
                            self.price_line_id = PriceLine.id
                            if self.bsg_cargo_sale_id.shipment_type == 'return':
                                self.unit_charge = PriceLine.price * 2 if PriceLine else 0.0
                                self.discount = 10
                                self._onchange_discount()
                            else:
                                self.unit_charge = PriceLine.price if PriceLine else 0.0
                            # self.service_type = PriceLine.service_type.id if PriceLine else self.env[
                            #     'product.template'].search([('name', 'in', ['Cargo Service', 'Cargo'])], limit=1).id
                            self.service_type = PriceLine.service_type.id if PriceLine else self._default_cargo_service()
                        else:
                            raise UserError(
                                _('No pricing found for this shipment type.'))
                if self.service_type:
                    PinConfig = self.env.user.company_id
                if self.bsg_cargo_sale_id.loc_from.is_international or self.bsg_cargo_sale_id.loc_to.is_international:
                    self.tax_ids = [(6, 0, [])]
                else:
                    self.tax_ids = PinConfig.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                 company_id=self.env.user.company_id.id).tax_ids.ids or self.service_type.taxes_id.ids
        vals.update({
            'charges_stored': self.charges,
            'final_price_stored': self.final_price,
            'invoice_state_stored': self.invoie_state,
            'update_stored_fields': True
        })
        if self.bsg_cargo_sale_id.customer_contract:
            vals.update({'revenue_type': 'corporate'})
        else:
            vals.update({'revenue_type': 'individual'})
        CargoSaleLine = super(bsg_vehicle_cargo_sale_line, self).write(vals)
        return CargoSaleLine


    def set_so_revenue_amount(self):
        revenue_amount = 0
        for rec in self:
            if rec.bsg_cargo_sale_id.is_return_so:
                if rec.shipping_source_id and rec.shipping_source_id.order_line_ids:
                    line = rec.shipping_source_id.order_line_ids[0]
                    if rec.bsg_cargo_sale_id.company_currency_id == line.bsg_cargo_sale_id.currency_id:
                        revenue_amount = line.total_without_tax * 0.4
                    else:
                        revenue_amount = line.original_charges * 0.4
            else:
                if rec.bsg_cargo_sale_id and rec.bsg_cargo_sale_id.shipment_type == 'oneway':
                    if rec.bsg_cargo_sale_id.company_currency_id == rec.bsg_cargo_sale_id.currency_id:
                        revenue_amount = rec.total_without_tax
                    else:
                        revenue_amount = rec.original_charges
                else:
                    if rec.bsg_cargo_sale_id.company_currency_id == rec.bsg_cargo_sale_id.currency_id:
                        revenue_amount = rec.total_without_tax * 0.6
                    else:
                        revenue_amount = rec.original_charges * 0.6
            rec.revenue_amount = revenue_amount


    def raise_price_warning(self):
        raise UserError(
            _('No pricing found for this shipment type.'))


    @api.model
    def create(self, vals):
        CargoSaleLine = super(bsg_vehicle_cargo_sale_line, self).create(vals)
        if CargoSaleLine.service_type:
            if CargoSaleLine.customer_price_list.item_ids:
                if self.customer_price_list.item_ids.filtered(lambda l: l.product_tmpl_id.id == self.service_type.id):
                    if self.customer_price_list.item_ids.filtered(
                            lambda l: l.product_tmpl_id.id == self.service_type.id and l.compute_price == 'percentage'):
                        self.discount = max(self.customer_price_list.item_ids.filtered(lambda
                                                                                           l: l.product_tmpl_id.id == self.service_type.id and l.compute_price == 'percentage').mapped(
                            'percent_price'))
                    if self.customer_price_list.item_ids.filtered(
                            lambda l: l.product_tmpl_id.id == self.service_type.id and l.compute_price == 'fixed'):
                        self.fixed_discount = round(max(self.customer_price_list.item_ids.filtered(
                            lambda l: l.product_tmpl_id.id == self.service_type.id and l.compute_price == 'fixed').mapped(
                            'fixed_price')), 2)
        if CargoSaleLine.service_type and not self.env.context.get('without_calculate_pric', False):
            if CargoSaleLine.shipment_type.is_normal:
                if CargoSaleLine.bsg_cargo_sale_id.customer_contract:
                    if not CargoSaleLine.car_size and vals.get('car_model'):
                        car_size_from_model = self.env['bsg_car_line'].search(
                            [('car_model', '=', vals.get('car_model'))]).car_size.id
                    else:
                        car_size_from_model = CargoSaleLine.car_size.id
                    ContractLine = self.env['bsg_customer_contract_line'].search([
                        ('cust_contract_id', '=',
                         CargoSaleLine.bsg_cargo_sale_id.customer_contract.id),
                        ('loc_from', '=',
                         CargoSaleLine.bsg_cargo_sale_id.loc_from.id),
                        ('loc_to', '=', CargoSaleLine.bsg_cargo_sale_id.loc_to.id),
                        ('car_size', '=', car_size_from_model),
                    ], limit=1)
                    CargoSaleLine.unit_charge = ContractLine.price if ContractLine else 0.0
                else:
                    if CargoSaleLine.bsg_cargo_sale_id.state == 'draft' and CargoSaleLine.state == 'draft':
                        search_id = self.env['bsg_price_line'].search([
                            ('price_config_id.waypoint_from', '=',
                             CargoSaleLine.bsg_cargo_sale_id.loc_from.id),
                            ('price_config_id.waypoint_to', '=',
                             CargoSaleLine.bsg_cargo_sale_id.loc_to.id),
                            ('price_config_id.customer_type', '=',
                             CargoSaleLine.bsg_cargo_sale_id.customer_type),
                            ('service_type', '=', CargoSaleLine.service_type.id),
                            ('car_classfication', '=',
                             CargoSaleLine.car_classfication.id),
                            ('car_size', '=', CargoSaleLine.car_size.id),
                        ], limit=1)
                        CargoSaleLine.price_line_id = search_id.id
                        if CargoSaleLine.bsg_cargo_sale_id.shipment_type == 'return' and CargoSaleLine.customer_price_list.is_public:
                            CargoSaleLine.unit_charge = search_id.price * 2
                            CargoSaleLine.discount = 10
                            CargoSaleLine._onchange_discount()
                        elif CargoSaleLine.bsg_cargo_sale_id.shipment_type == 'return' and not CargoSaleLine.customer_price_list.is_public:
                            CargoSaleLine.unit_charge = search_id.price * 2
                            if CargoSaleLine.customer_price_list.item_ids:
                                if CargoSaleLine.customer_price_list.item_ids.filtered(
                                        lambda l: l.product_tmpl_id.id == CargoSaleLine.service_type.id):
                                    if CargoSaleLine.customer_price_list.item_ids.filtered(
                                            lambda l: l.product_tmpl_id.id == CargoSaleLine.service_type.id and l.compute_price == 'percentage'):
                                        CargoSaleLine.discount = max(
                                            CargoSaleLine.customer_price_list.item_ids.filtered(lambda
                                                                                                    l: l.product_tmpl_id.id == CargoSaleLine.service_type.id and l.compute_price == 'percentage').mapped(
                                                'percent_price'))
                                    if CargoSaleLine.customer_price_list.item_ids.filtered(
                                            lambda l: l.product_tmpl_id.id == CargoSaleLine.service_type.id and l.compute_price == 'fixed'):
                                        CargoSaleLine.fixed_discount = round(
                                            max(CargoSaleLine.customer_price_list.item_ids.filtered(
                                                lambda
                                                    l: l.product_tmpl_id.id == self.service_type.id and l.compute_price == 'fixed').mapped(
                                                'fixed_price')), 2)
                                else:
                                    CargoSaleLine.discount = 0.0
                            CargoSaleLine._onchange_discount()
                        else:
                            CargoSaleLine.unit_charge = search_id.price
        elif not self.env.context.get('without_calculate_pric', False):
            # if CargoSaleLine.car_model.id not in CargoSaleLine.shipment_type.car_model.ids:
            # 	raise UserError(_('You cant ship this Model with is type of shipment'))

            if CargoSaleLine.bsg_cargo_sale_id.customer_contract:
                ContractLine = self.env['bsg_customer_contract_line'].search([
                    ('cust_contract_id', '=',
                     CargoSaleLine.bsg_cargo_sale_id.customer_contract.id),
                    ('loc_from', '=', CargoSaleLine.bsg_cargo_sale_id.loc_from.id),
                    ('loc_to', '=', CargoSaleLine.bsg_cargo_sale_id.loc_to.id),
                    ('car_size', '=', CargoSaleLine.shipment_type.car_size.id),
                ], limit=1)
                CargoSaleLine.unit_charge = ContractLine.price if ContractLine else 0.0
            else:
                PriceConfig = self.env['bsg_price_config'].search([
                    ('waypoint_from', '=', CargoSaleLine.bsg_cargo_sale_id.loc_from.id),
                    ('waypoint_to', '=', CargoSaleLine.bsg_cargo_sale_id.loc_to.id),
                    ('company_id', '=', self.env.user.company_id.id),
                    ('customer_type', '=',
                     CargoSaleLine.bsg_cargo_sale_id.customer_type),
                ], limit=1)
                if PriceConfig:
                    PriceLine = self.env['bsg_price_line'].search([
                        ('price_config_id', '=', PriceConfig.id),
                        ('company_id', '=', self.env.user.company_id.id),
                        # ('service_type','=',self.service_type.id),
                        ('car_classfication', '=',
                         CargoSaleLine.car_classfication.id),
                        ('car_size', '=', CargoSaleLine.shipment_type.car_size.id),
                    ], limit=1)
                    if PriceLine:
                        CargoSaleLine.price_line_id = PriceLine.id
                        if CargoSaleLine.bsg_cargo_sale_id.shipment_type == 'return':
                            CargoSaleLine.unit_charge = (PriceLine.price * 2) if PriceLine else 0.0
                            CargoSaleLine.discount = 10
                            CargoSaleLine._onchange_discount()
                        else:
                            CargoSaleLine.unit_charge = PriceLine.price if PriceLine else 0.0
                        # self.service_type = PriceLine.service_type.id if PriceLine else self.env[
                        #     'product.template'].search([('name', 'in', ['Cargo Service', 'Cargo'])], limit=1).id
                        CargoSaleLine.service_type = PriceLine.service_type.id if PriceLine else self._default_cargo_service()
                    else:
                        raise UserError(
                            _('No pricing found for this shipment type.'))
            if CargoSaleLine.service_type and not (
                    CargoSaleLine.bsg_cargo_sale_id.loc_from.is_international or CargoSaleLine.bsg_cargo_sale_id.loc_to.is_international):
                PinConfig = self.env.ref(
                    'bsg_cargo_sale.res_config_tax_data', False)
                CargoSaleLine.tax_ids = PinConfig.sudo(
                ).tax_ids.ids or CargoSaleLine.service_type.taxes_id.ids

        if CargoSaleLine.bsg_cargo_sale_id.loc_from.id and CargoSaleLine.bsg_cargo_sale_id.loc_to.id:
            CargoSaleLine.pickup_loc = CargoSaleLine.bsg_cargo_sale_id.loc_from.id
            CargoSaleLine.drop_loc = CargoSaleLine.bsg_cargo_sale_id.loc_to.id

        # CargoSaleLine.cargo_sale_line_name = self.env['ir.sequence'].next_by_code('bsg_vehicle_cargo_sale_line')
        if self.env.context.get('keep_line_sequence'):
            CargoSaleLine.bsg_cargo_sale_id._reset_sequence()
        CargoSaleLine.charges_stored = CargoSaleLine.charges
        CargoSaleLine.final_price_stored = CargoSaleLine.final_price
        CargoSaleLine.invoice_state_stored = CargoSaleLine.invoie_state
        CargoSaleLine.update_stored_fields = True
        if CargoSaleLine.bsg_cargo_sale_id.customer_contract:
            CargoSaleLine.revenue_type = 'corporate'
        else:
            CargoSaleLine.revenue_type = 'individual'
        return_so_ids = self.search([('bsg_cargo_sale_id.customer', '=', CargoSaleLine.bsg_cargo_sale_id.customer.id),
                                     ('bsg_cargo_sale_id.loc_from', '=', CargoSaleLine.bsg_cargo_sale_id.loc_to.id),
                                     ('bsg_cargo_sale_id.loc_to', '=', CargoSaleLine.bsg_cargo_sale_id.loc_from.id),
                                     ('shipment_type', '=', 'return'), ('bsg_cargo_sale_id.return_intiated', '=', False)])
        if return_so_ids:
            plates = return_so_ids.mapped('plate_no')
            chassis = return_so_ids.mapped('chassis_no')
            if CargoSaleLine.plate_no in plates or CargoSaleLine.chassis_no in chassis:
                raise ValidationError(
                    _("Customer return sale order must be initiated first!!"))
        return CargoSaleLine


    @api.model
    def action_update_stored_fields(self):
        line_ids = self.sudo().with_context(force_company=self.env.user.company_id.id,
                                            company_id=self.env.user.company_id.id).search(
            [('update_stored_fields', '=', False)], limit=3000)
        for line in line_ids:
            line.update_stored_fields = True
            _logger.info("Updated stored fields of SO line: ", line.id)


    # restcit user to delete if state not in draft

    def unlink(self):
        """
                    Delete all record(s) from table heaving record id in ids
                    return True on success, False otherwise

                    @return: True on success, False otherwise
            """
        for rec in self:
            if rec.state not in ['draft']:
                raise UserError(
                    _('You can not delete a confirmed record!'),
                )
        return super(bsg_vehicle_cargo_sale_line, self).unlink()


    #
    def _get_validate_payment(self):
        for rec in self:
            rec.no_cargo_inv_line_to_pay = False
            rec.no_demurrage_inv_line_to_pay = False
            if rec.invoice_line_ids:
                other_service_invoice = self.env['account.move'].search(
                    [('ref', '=', rec.bsg_cargo_sale_id.name), ('is_other_service_invoice', '=', True)])
                if all(rec.invoice_line_ids.filtered(
                        lambda s: s.move_id.id in rec.bsg_cargo_sale_id.invoice_ids.ids).mapped('is_paid')):
                    rec.no_cargo_inv_line_to_pay = True
                if all(rec.invoice_line_ids.filtered(lambda s: s.move_id.id in other_service_invoice.ids).mapped(
                        'is_paid')):
                    rec.no_other_inv_line_to_pay = True
                if all(rec.invoice_line_ids.filtered(
                        lambda s: s.cargo_sale_line_id.id == rec.id and s.move_id.is_demurrage_invoice == True).mapped(
                    'is_paid')):
                    rec.no_demurrage_inv_line_to_pay = True
            else:
                rec.no_cargo_inv_line_to_pay = True
                rec.no_other_inv_line_to_pay = True
                rec.no_demurrage_inv_line_to_pay = True


    # Register Payment

    def register_payment(self):
        if self.no_cargo_inv_line_to_pay:
            raise UserError(_("There Is No Line To Pay"))
        view_id = self.env.ref('account.view_account_payment_invoice_form').id
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
                'res_model': 'account.payment',
                'view_id': view_id,
                'target': 'new',
                'context': {
                    'default_payment_type': 'inbound',
                    'default_partner_id':
                        self.bsg_cargo_sale_id.invoice_ids.filtered(lambda s: s.payment_sate != 'paid').mapped('partner_id')[
                            0].id,
                    'default_partner_type': 'customer',
                    'default_is_from_cargo_line': True,
                    # 'default_journal_id': journal_id.id,
                    # 'default_amount': sum(self.invoice_line_ids.filtered(lambda s: not s.is_paid).mapped('charges')),
                    'default_communication': self.invoice_line_ids.mapped('name'),
                    'default_show_invoice_amount': True,
                    'pass_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_is_patrtially_payment': True,
                    'default_cargo_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_cargo_sale_line_order_ids': self.ids,
                    'default_invoice_ids': [(4, self.bsg_cargo_sale_id.invoice_ids[0].id, None)]
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
                'res_model': 'account.payment',
                'view_id': view_id,
                'target': 'new',
                'context': {
                    'default_payment_type': 'inbound',
                    'default_partner_id':
                        self.bsg_cargo_sale_id.invoice_ids.filtered(lambda s: s.payment_state != 'paid').mapped('partner_id')[
                            0].id,
                    'default_partner_type': 'customer',
                    'default_is_from_cargo_line': True,
                    # 'default_journal_id': journal_id.id,
                    # 'default_amount': sum(self.order_line_ids.filtered(lambda s: not s.payment_ids).mapped('charges')),
                    'default_communication': self.invoice_line_ids.mapped('name'),
                    # 'default_show_invoice_amount': True,
                    'pass_sale_order_id': self.bsg_cargo_sale_id.id,
                    'context_sequnce_cash': True,
                    'default_is_show_partial': True,
                    'default_cargo_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_cargo_sale_line_order_ids': self.ids,
                    'default_invoice_ids': [(4, self.bsg_cargo_sale_id.invoice_ids[0].id, None)]
                }
            }
        else:
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
                        self.bsg_cargo_sale_id.invoice_ids.filtered(lambda s: s.state == 'open').mapped('partner_id')[
                            0].id,
                    'default_partner_type': 'customer',
                    'default_is_from_cargo_line': True,
                    # 'default_journal_id': journal_id.id,
                    # 'default_amount': sum(self.order_line_ids.filtered(lambda s: not s.payment_ids).mapped('charges')),
                    'default_communication': self.invoice_line_ids.mapped('name'),
                    'pass_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_cargo_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_cargo_sale_line_order_ids': self.ids,
                    'default_invoice_ids': [(4, self.bsg_cargo_sale_id.invoice_ids[0].id, None)]
                }
            }


    # Register Payment

    def register_other_service_payment(self):
        other_service_invoice = self.env['account.move'].search(
            [('ref', '=', self.bsg_cargo_sale_id.name), ('is_other_service_invoice', '=', True)])
        if self.no_other_inv_line_to_pay:
            raise UserError(_("There Is No Line To Pay"))
        view_id = self.env.ref('account.view_account_payment_invoice_form').id
        journal_id = self.env['account.journal'].search(
            [('type', '=', 'cash')], limit=1)

        if not journal_id:
            raise UserError(
                _("There is no cash journal defined please define in accounting."))
        if self.payment_method.payment_type == 'pod':
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
                        other_service_invoice.filtered(
                            lambda s: s.state == 'open').mapped('partner_id')[0].id,
                    'default_partner_type': 'customer',
                    'default_is_from_cargo_line': True,
                    # 'default_journal_id': journal_id.id,
                    # 'default_amount': sum(self.invoice_line_ids.filtered(lambda s: not s.is_paid).mapped('charges')),
                    'default_communication': self.invoice_line_ids.mapped('name'),
                    'default_show_invoice_amount': True,
                    # 'pass_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_is_patrtially_payment': True,
                    'default_cargo_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_cargo_sale_line_order_ids': self.ids,
                    'default_invoice_ids': [(4, other_service_invoice[0].id, None)]
                }
            }
        elif self.payment_method.payment_type == 'cash':
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
                        other_service_invoice.filtered(
                            lambda s: s.state == 'open').mapped('partner_id')[0].id,
                    'default_partner_type': 'customer',
                    'default_is_from_cargo_line': True,
                    # 'default_journal_id': journal_id.id,
                    # 'default_amount': sum(self.order_line_ids.filtered(lambda s: not s.payment_ids).mapped('charges')),
                    'default_communication': self.invoice_line_ids.mapped('name'),
                    # 'default_show_invoice_amount': True,
                    # 'pass_sale_order_id': self.bsg_cargo_sale_id.id,
                    'context_sequnce_cash': True,
                    'default_is_show_partial': True,
                    'default_cargo_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_cargo_sale_line_order_ids': self.ids,
                    'default_invoice_ids': [(4, other_service_invoice[0].id, None)]
                }
            }
        else:
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
                        other_service_invoice.filtered(
                            lambda s: s.state == 'open').mapped('partner_id')[0].id,
                    'default_partner_type': 'customer',
                    'default_is_from_cargo_line': True,
                    # 'default_journal_id': journal_id.id,
                    # 'default_amount': sum(self.order_line_ids.filtered(lambda s: not s.payment_ids).mapped('charges')),
                    'default_communication': self.invoice_line_ids.mapped('name'),
                    # 'pass_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_cargo_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_cargo_sale_line_order_ids': self.ids,
                    'default_invoice_ids': [(4, other_service_invoice[0].id, None)]
                }
            }


    # Register Payment

    def register_payment_for_all_invoices(self):
        if self.no_cargo_inv_line_to_pay and self.no_other_inv_line_to_pay and self.no_demurrage_inv_line_to_pay:
            raise UserError(_("There Is No Line To Pay"))
        view_id = self.env.ref('account.view_account_payment_register_form').id
        journal_id = self.env['account.journal'].search(
            [('type', '=', 'cash')], limit=1)

        if not journal_id:
            raise UserError(
                _("There is no cash journal defined please define in accounting."))
        invoice_ids = []
        for invoice in self.invoice_line_ids.filtered(lambda s: not s.is_refund and not s.is_paid).mapped(
                'move_id').filtered(lambda s: s.payment_state != 'paid'):
            if (all(line.cargo_sale_line_id.id == self.id for line in invoice.invoice_line_ids)):
                invoice_ids.append(invoice)
        if not invoice_ids:
            raise UserError(
                _("Sorry! You Can't Pay Invoice Has Other Cargo Line , Please Pay it from Cargo Order"))
        currency_id = False
        if len(invoice_ids) == 1:
            currency_id = invoice_ids[0].currency_id.id
        else:
            if self.env.user.has_group(
                    'payments_enhanced.group_allowed_pay_with_fc') and self.env.user.user_branch_id.branch_operation == 'international':
                currency_id = self.env.user.user_branch_id.currency_id.id
            else:
                currency_id = self.env.user.company_id.currency_id.id
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
                    'default_payment_type': 'inbound',
                    'default_partner_id':
                        self.invoice_line_ids.mapped('move_id').filtered(lambda s: s.payment_state == 'not_paid').mapped(
                            'partner_id')[0].id,
                    'default_partner_type': 'customer',
                    'default_is_from_cargo_line': True,
                    'default_multi': True,
                    'default_is_new_order': True,
                    'default_group_invoices': True,
                    'default_is_form_cargo_line': True,
                    # 'default_journal_id': journal_id.id,
                    'default_amount': sum(
                        self.invoice_line_ids.filtered(lambda s: not s.is_refund).mapped('move_id').filtered(
                            lambda s: s.payment_state == 'not_paid').mapped('amount_residual')),
                    'default_communication': self.invoice_line_ids.mapped('name'),
                    # 'default_show_invoice_amount': True,
                    'pass_sale_order_id': self.bsg_cargo_sale_id.id,
                    # 'default_is_patrtially_payment': True,
                    'default_cargo_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_cargo_sale_line_order_ids': self.ids,
                    'cargo_sale_line_order_ids': self.ids,
                    'default_invoice_ids': [(4, invoice.id, None) for invoice in invoice_ids],
                    'default_currency_id': currency_id,

                }
            }
        elif self.payment_method.payment_type == 'cash':
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
                    'default_partner_id':
                        self.invoice_line_ids.mapped('move_id').filtered(lambda s: s.payment_state == 'not_paid').mapped(
                            'partner_id')[0].id,
                    'default_partner_type': 'customer',
                    'default_is_from_cargo_line': True,

                    'default_multi': True,
                    'default_is_new_order': True,
                    'default_group_invoices': True,
                    'default_is_form_cargo_line': True,
                    # 'default_journal_id': journal_id.id,
                    'default_amount': sum(
                        self.invoice_line_ids.filtered(lambda s: not s.is_refund).mapped('move_id').mapped(
                            'amount_residual')),
                    'default_communication': self.invoice_line_ids.mapped('name'),
                    # 'default_show_invoice_amount': True,
                    'pass_sale_order_id': self.bsg_cargo_sale_id.id,
                    'context_sequnce_cash': True,
                    # 'default_is_show_partial' : True,
                    'default_cargo_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_cargo_sale_line_order_ids': self.ids,
                    'cargo_sale_line_order_ids': self.ids,
                    'default_invoice_ids': [(4, invoice.id, None) for invoice in invoice_ids],
                    'default_currency_id': currency_id,
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
                    'default_partner_id':
                        self.invoice_line_ids.mapped('move_id').filtered(lambda s: s.payment_state == 'not_paid').mapped(
                            'partner_id')[0].id,
                    'default_partner_type': 'customer',
                    'default_is_from_cargo_line': True,
                    'default_multi': True,
                    'default_is_new_order': True,
                    'default_group_invoices': True,
                    'default_is_form_cargo_line': True,
                    # 'default_journal_id': journal_id.id,
                    'default_amount': sum(
                        self.invoice_line_ids.filtered(lambda s: not s.is_refund).mapped('move_id').mapped(
                            'amount_residual')),
                    'default_communication': self.invoice_line_ids.mapped('name'),
                    'pass_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_cargo_sale_order_id': self.bsg_cargo_sale_id.id,
                    'default_cargo_sale_line_order_ids': self.ids,
                    'cargo_sale_line_order_ids': self.ids,
                    'default_invoice_ids': [(4, invoice.id, None) for invoice in invoice_ids],
                    'default_currency_id': currency_id,
                }
            }


class account_register_payments(models.TransientModel):
    _inherit = "account.payment.register"

    is_form_cargo_line = fields.Boolean()
