# -*- coding: utf-8 -*-

from odoo import models, fields, api

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang

class SaleCoupon(models.Model):
    _inherit = 'loyalty.reward'

    cargo_sale_order_id = fields.Many2one('bsg_vehicle_cargo_sale', 'Cargo Order Reference', readonly=True,
        help="The sales order from which coupon is generated")
    cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale', 'Applied on Cargo order', readonly=True,
        help="The cargo order on which the coupon is applied")

    def _cargo_check_coupon_code(self, order):
        message = {}
        applicable_programs = order._cargo_get_applicable_programs()
        if self.state in ('used', 'expired') or \
           (self.expiration_date and self.expiration_date < order.order_date.date()):
            message = {'error': _('This coupon %s has been used or is expired.') % (self.code)}
        elif self.state == 'reserved':
            message = {'error': _('This coupon %s exists but the origin sales order is not validated yet.') % (self.code)}
        # Minimum requirement should not be checked if the coupon got generated by a promotion program (the requirement should have only be checked to generate the coupon)
        elif self.program_id.program_type == 'coupon_program' and not self.program_id._cargo_filter_on_mimimum_amount(order):
            message = {'error': _('A minimum of %s %s should be purchased to get the reward') % (self.program_id.rule_minimum_amount, self.program_id.currency_id.name)}
        elif not self.program_id.active:
            message = {'error': _('The coupon program for %s is in draft or closed state') % (self.code)}
        elif self.partner_id and self.partner_id != order.customer:
            message = {'error': _('Invalid partner.')}
        elif self.program_id in order.applied_coupon_ids.mapped('program_id'):
            message = {'error': _('A Coupon is already applied for the same reward')}
        elif self.program_id._is_global_discount_program() and order._cargo_is_global_discount_already_applied():
            message = {'error': _('Global discounts are not cumulable.')}
        elif self.program_id.reward_type == 'product' and not order._cargo_is_reward_in_order_lines(self.program_id):
            message = {'error': _('The reward products should be in the sales order lines to apply the discount.')}
        elif not self.program_id._is_valid_partner(order.customer):
            message = {'error': _("The customer doesn't have access to this reward.")}
        # Product requirement should not be checked if the coupon got generated by a promotion program (the requirement should have only be checked to generate the coupon)
        elif self.program_id.program_type == 'coupon_program' and not self.program_id._cargo_filter_programs_on_products(order):
            message = {'error': _("You don't have the required product quantities on your sales order. All the products should be recorded on the sales order. (Example: You need to have 3 T-shirts on your sales order if the promotion is 'Buy 2, Get 1 Free').")}
        #Add Cargo Checks
        elif not self.program_id._cargo_filter_payment_method_reward_programs(order):
            message = {'error': _("This Coupon Can't Apply For Order Payment Method!")}
        elif not self.program_id._cargo_filter_partner_types_reward_programs(order):
            message = {'error': _("This Coupon Can't Apply For Order Partner Type!")}
        elif not self.program_id._cargo_filter_agreement_type_reward_programs(order):
            message = {'error': _("This Coupon Can't Apply For Order Agreement Type!")}    
        elif not self.program_id._cargo_filter_from_location_domain_reward_programs(order):
            message = {'error': _("This Coupon Can't Apply In Order,Coupon Not Include Order From Location!")}
        elif not self.program_id._cargo_filter_to_location_domain_reward_programs(order):
            message = {'error': _("This Coupon Can't Apply In Order,Coupon Not Include Order To Location!")}
        elif not self.program_id._cargo_filter_lines_shipment_type_domain_reward_programs(order):
            message = {'error': _("This Coupon Can't Apply In Order,Coupon Not Include Car Shipment Type!")}     
        elif not self.program_id._cargo_filter_lines_specific_product_reward_programs(cargo_order):
            message = {'error': _("This Coupon Can't Apply In Order,Coupon Not Include Service Type!")}
        else:
            if self.program_id not in applicable_programs and self.program_id.promo_applicability == 'on_current_order':
                message = {'error': _('At least one of the required conditions is not met to get the coupon!')}
        return message 