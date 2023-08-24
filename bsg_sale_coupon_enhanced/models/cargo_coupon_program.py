# -*- coding: utf-8 -*-

from odoo import models, fields, api

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError, ValidationError

class SaleCouponProgram(models.Model):
    _inherit = 'loyalty.program'

    cargo_order_count = fields.Integer(compute='_compute_cargo_order_count')
    cargo_sale_coupon_line_ids = fields.One2many('bsg_vehicle_cargo_sale_coupon','promo_program_id')
    is_with_order_taxes = fields.Boolean(track_visibility='onchange')

    payment_method_ids = fields.Many2many(
        'cargo_payment_method', string="Payment Method", track_visibility='onchange')
    location_domain = fields.Boolean("By Locations",default=False,track_visibility='onchange')
    loc_from_ids = fields.Many2many('bsg_route_waypoints','coupon_program_from_location_rel','coupon_program_id', 'location_from_id',string="From Loctions",track_visibility='onchange')
    loc_to_ids = fields.Many2many('bsg_route_waypoints','coupon_program_to_location_rel','coupon_program_id', 'location_to_id',string="To Loctions",track_visibility='onchange')
    shipment_type = fields.Many2many(string="Shipment Type", comodel_name="bsg.car.shipment.type",track_visibility='onchange')
    partner_types = fields.Many2many("partner.type",track_visibility='onchange',string="Partner Type")
    agreement_type = fields.Selection(string="Agreement Type", selection=[
        ('return', 'Round Trip'),
        ('oneway', 'Oneway')
    ],track_visibility='onchange')
    discount_specific_product_id = fields.Many2many('product.product','program_promo_specific_product','program_id','product_id', string="Product",
        help="Product that will be discounted if the discount is applied on a specific product")


    @api.constrains('discount_specific_product_id','discount_apply_on')
    def _check_specific_product_id(self):
        if self.discount_apply_on == 'specific_product' and len(self.discount_specific_product_id) < 1:
            raise ValidationError(_('Please Specify Products To Apply'))


    @api.depends('cargo_sale_coupon_line_ids','cargo_sale_coupon_line_ids.cargo_sale_order_id')
    def _compute_cargo_order_count(self):
        for program in self:
            program.cargo_order_count = len(program.cargo_sale_coupon_line_ids.mapped('cargo_sale_order_id'))

    def action_view_cargo_sales_orders(self):
        self.ensure_one()
        orders = self.cargo_sale_coupon_line_ids.mapped('cargo_sale_order_id')
        return {
            'name': _('Cargo Sales Orders'),
            'view_mode': 'tree,form',
            'res_model': 'bsg_vehicle_cargo_sale',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', orders.ids)]
        }

    def _cargo_check_promo_code(self, cargo_order, coupon_code):
        message = {}
        applicable_programs = cargo_order._cargo_get_applicable_programs()
        if self.maximum_use_number != 0 and self.cargo_order_count >= self.maximum_use_number:
            message = {'error': _('Promo code %s has been expired.') % (coupon_code)}
        elif not self._cargo_filter_on_mimimum_amount(cargo_order):
            message = {'error': _('A minimum of %s %s should be purchased to get the reward') % (self.rule_minimum_amount, self.currency_id.name)}
        elif self.promo_code and self.promo_code == cargo_order.promo_code:
            message = {'error': _('The promo code is already applied on this order')}
        elif not self.promo_code and self in cargo_order.no_code_promo_program_ids:
            message = {'error': _('The promotional offer is already applied on this order')}
        elif not self.active:
            message = {'error': _('Promo code is invalid')}
        elif self.rule_date_from and self.rule_date_from > cargo_order.order_date or self.rule_date_to and cargo_order.order_date > self.rule_date_to:
            message = {'error': _('Promo code is expired')}
        elif cargo_order.promo_code and self.trigger == 'auto':
            message = {'error': _('Promotionals codes are not cumulative.')}
        elif self._is_global_discount_program() and cargo_order._cargo_is_global_discount_already_applied():
            message = {'error': _('Global discounts are not cumulative.')}
        elif self.promo_applicability == 'on_current_order' and self.reward_type == 'product' and not cargo_order._cargo_is_reward_in_order_lines(self):
            message = {'error': _('The reward products should be in the sales order lines to apply the discount.')}
        elif not self._is_valid_partner(cargo_order.customer):
            message = {'error': _("The customer doesn't have access to this reward.")}
        elif not self._cargo_filter_programs_on_products(cargo_order):
            message = {'error': _("You don't have the required product quantities on your sales order. If the reward is same product quantity, please make sure that all the products are recorded on the sales order (Example: You need to have 3 T-shirts on your sales order if the promotion is 'Buy 2, Get 1 Free'.")}
        #Add Cargo Checks
        elif not self._cargo_filter_payment_method_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply For Order Payment Method!")}
        elif not self._cargo_filter_partner_types_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply For Order Partner Type!")}
        elif not self._cargo_filter_agreement_type_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply For Order Agreement Type!")}    
        elif not self._cargo_filter_from_location_domain_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply In Order,Promotion Not Include Order From Location!")}
        elif not self._cargo_filter_to_location_domain_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply In Order,Promotion Not Include Order To Location!")}            
        elif not self._cargo_filter_lines_shipment_type_domain_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply In Order,Promotion Not Include Car Shipment Type!")}            
        elif not self._cargo_filter_lines_specific_product_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply In Order,Promotion Not Include Service Type!")}  
        else:
            if self not in applicable_programs and self.promo_applicability == 'on_current_order':
                message = {'error': _('At least one of the required conditions is not met to get the reward!')}
        return message

    def _cargo_check_cargo_condition_promo_code(self, cargo_order):
        message = {}
        applicable_programs = cargo_order._cargo_get_applicable_programs()
        #Add Cargo Checks
        if not self._cargo_filter_payment_method_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply For Order Payment Method!")}
        elif not self._cargo_filter_partner_types_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply For Order Partner Type!")}
        elif not self._cargo_filter_agreement_type_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply For Order Agreement Type!")}    
        elif not self._cargo_filter_from_location_domain_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply In Order,Promotion Not Include Order From Location!")}
        elif not self._cargo_filter_to_location_domain_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply In Order,Promotion Not Include Order To Location!")}            
        elif not self._cargo_filter_lines_shipment_type_domain_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply In Order,Promotion Not Include Car Shipment Type!")}  
        elif not self._cargo_filter_lines_specific_product_reward_programs(cargo_order):
            message = {'error': _("This Promotional Can't Apply In Order,Promotion Not Include Service Type!")}              
        else:
            if self not in applicable_programs and self.promo_applicability == 'on_current_order':
                message = {'error': _('At least one of the required conditions is not met to get the reward!')}
        return message

    @api.model
    def _cargo_filter_on_mimimum_amount(self, order):
        untaxed_amount = sum([line.total_without_tax for line in order.order_line_ids])
        tax_amount = sum([line.tax_amount for line in order.order_line_ids])

        # Some lines should not be considered when checking if threshold is met like delivery
        return self.filtered(lambda program:
            program.rule_minimum_amount_tax_inclusion == 'tax_included' and
            program._compute_program_amount('rule_minimum_amount', order.currency_id) <= untaxed_amount + tax_amount or
            program.rule_minimum_amount_tax_inclusion == 'tax_excluded' and
            program._compute_program_amount('rule_minimum_amount', order.currency_id) <= untaxed_amount)

    @api.model
    def _cargo_filter_on_validity_dates(self, order):
        return self.filtered(lambda program:
            program.rule_date_from and program.rule_date_to and
            program.rule_date_from <= order.order_date and program.rule_date_to >= order.order_date or
            not program.rule_date_from or not program.rule_date_to)

    def _is_global_discount_program(self):
        self.ensure_one()
        #Make Global Even For Fixed Discount(Odoo Consider Just For Percentage Discount)
        #To Prevent Apply Other Coupon With Already Applied Coupon
        
        #self.promo_applicability == 'on_current_order' and \
        #        self.reward_type == 'discount' and \
        #        self.discount_type == 'percentage' and \
        #        self.discount_apply_on == 'on_order' or \
        #        self.discount_type == 'fixed_amount'

        return True   

               
    @api.model
    def _cargo_filter_promo_programs_with_code(self, order):
        '''Filter Promo program with code with a different promo_code if a promo_code is already ordered'''
        return self.filtered(lambda program: program.trigger == 'auto' and program.promo_code != order.promo_code)

    def _cargo_filter_unexpired_programs(self, order):
        return self.filtered(lambda program: program.maximum_use_number == 0 or program.cargo_order_count <= program.maximum_use_number)

    def _cargo_filter_programs_on_partners(self, order):
        return self.filtered(lambda program: program._is_valid_partner(order.customer))

    def _cargo_filter_programs_on_products(self, order):
        """
        To get valid programs according to product list.
        i.e Buy 1 imac + get 1 ipad mini free then check 1 imac is on cart or not
        or  Buy 1 coke + get 1 coke free then check 2 cokes are on cart or not
        """
        order_lines = order.order_line_ids.filtered(lambda line: line.service_type.product_variant_id)
        products = order_lines.mapped('service_type.product_variant_id')
        products_qties = dict.fromkeys(products, 0)
        for line in order_lines:
            products_qties[line.service_type.product_variant_id] += 1 #line.product_uom_qty (because No Qty In Order Line)
        valid_programs = self.filtered(lambda program: not program.rule_products_domain)
        for program in self - valid_programs:
            valid_products = program._get_valid_products(products)
            ordered_rule_products_qty = sum(products_qties[product] for product in valid_products)
            # Avoid program if 1 ordered foo on a program '1 foo, 1 free foo'
            if program.promo_applicability == 'on_current_order' and \
               program._is_valid_product(program.reward_product_id) and program.reward_type == 'product':
                ordered_rule_products_qty -= program.reward_product_quantity
            if ordered_rule_products_qty >= program.rule_min_quantity:
                valid_programs |= program
        return valid_programs

    def _cargo_filter_not_ordered_reward_programs(self, order):
        """
        Returns the programs when the reward is actually in the order lines
        """
        programs = self.env['loyalty.program']
        for program in self:
            if program.reward_type == 'product' and \
               not order.order_line_ids.filtered(lambda line: line.service_type.product_variant_id == program.reward_product_id):
                continue
            elif program.reward_type == 'discount' and program.discount_apply_on == 'specific_product' and \
               not order.order_line_ids.filtered(lambda line: line.service_type in program.discount_specific_product_id.mapped('product_tmpl_id')):
                continue
            programs |= program
        return programs

    @api.model
    def _cargo_filter_programs_from_common_rules(self, order, next_order=False):
        """ Return the programs if every conditions is met
            :param bool next_order: is the reward given from a previous order
        """
        programs = self
        # Minimum requirement should not be checked if the coupon got generated by a promotion program (the requirement should have only be checked to generate the coupon)
        if not next_order:
            programs = programs and programs._cargo_filter_on_mimimum_amount(order)
        programs = programs and programs._cargo_filter_on_validity_dates(order)
        programs = programs and programs._cargo_filter_unexpired_programs(order)
        programs = programs and programs._cargo_filter_programs_on_partners(order)
        # Product requirement should not be checked if the coupon got generated by a promotion program (the requirement should have only be checked to generate the coupon)
        if not next_order:
            programs = programs and programs._cargo_filter_programs_on_products(order)

        programs_curr_order = programs.filtered(lambda p: p.promo_applicability == 'on_current_order')
        programs = programs.filtered(lambda p: p.promo_applicability == 'on_next_order')
        if programs_curr_order:
            # Checking if rewards are in the SO should not be performed for rewards on_next_order
            programs += programs_curr_order._cargo_filter_not_ordered_reward_programs(order)
        return programs



    def _cargo_filter_payment_method_reward_programs(self, order):
        return self.filtered(lambda program:
            program.payment_method_ids and order.payment_method.id in program.payment_method_ids.ids
             or not program.payment_method_ids)

    def _cargo_filter_partner_types_reward_programs(self, order):
        return self.filtered(lambda program:
            program.partner_types and order.partner_types.id in program.partner_types.ids
             or not program.partner_types)

    def _cargo_filter_agreement_type_reward_programs(self, order):
        return self.filtered(lambda program:
            program.agreement_type and order.shipment_type == program.agreement_type
             or not program.agreement_type)

    def _cargo_filter_from_location_domain_reward_programs(self, order):   
        return self.filtered(lambda program:
            program.location_domain and program.loc_from_ids and order.loc_from.id in program.loc_from_ids.ids
             or not program.location_domain or  not program.loc_from_ids)

    def _cargo_filter_to_location_domain_reward_programs(self, order):   
        return self.filtered(lambda program:
            program.location_domain and program.loc_to_ids and order.loc_to.id in program.loc_to_ids.ids
             or not program.location_domain or not program.loc_to_ids)          

    def _cargo_filter_lines_shipment_type_domain_reward_programs(self, order):   
        return self.filtered(lambda program:
            program.shipment_type and set(order.order_line_ids.mapped('shipment_type.id')) & set(program.shipment_type.ids)
             or not program.shipment_type) 
    def _cargo_filter_lines_specific_product_reward_programs(self, order): 
        return self.filtered(lambda program:
            program.discount_apply_on != 'specific_product' or  (program.discount_apply_on ==  'specific_product' and set(order.order_line_ids.mapped('service_type.id')) & set(program.discount_specific_product_id.mapped('product_tmpl_id.id'))))
