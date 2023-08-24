# -*- coding: utf-8 -*-

from odoo import models, fields, api

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from odoo.http import request

        
class BsgVehicleCargoSale(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale'
    
    applied_coupon_ids = fields.One2many('loyalty.reward', 'cargo_sale_id', string="Applied Coupons", copy=False)
    generated_coupon_ids = fields.One2many('loyalty.reward', 'cargo_sale_order_id', string="Offered Coupons", copy=False)
    reward_amount = fields.Float(compute='_compute_cargo_reward_total')
    no_code_promo_program_ids = fields.Many2many('loyalty.program', string="Applied Immediate Promo Programs",
        domain=[('trigger', '=', 'auto')], copy=False)
    code_promo_program_id = fields.Many2one('loyalty.program', string="Applied Promo Program",
        domain=[('trigger', '=', 'auto')], copy=False)
    promo_code = fields.Char(related='code_promo_program_id.name',store=True, help="Applied program code", readonly=False)
    cargo_sale_coupon_ids = fields.One2many('bsg_vehicle_cargo_sale_coupon','cargo_sale_order_id')
    
    @api.depends('cargo_sale_coupon_ids')
    def _compute_cargo_reward_total(self):
        for order in self:
            order.reward_amount = sum([line.price_total for line in order.cargo_sale_coupon_ids])

    def _get_applied_coupon_code(self):
        coupon_str = str('-'.join(self.applied_coupon_ids.mapped('code')))
        coupon_str += self.code_promo_program_id and self.code_promo_program_id.promo_code or ''
        return coupon_str


    def cargo_recompute_coupon_line(self):
        for order in self:
            order._cargo_remove_invalid_reward_lines()
            order._cargo_create_new_no_code_promo_reward_lines()
            order._cargo_update_existing_reward_lines()

    def cargo_recompute_discounts(self):
        """ Method to recompute coupon lines on website """
        pass

    def get_promo_code_error(self, delete=True):
        error = request.session.get('error_promo_code')
        if error and delete:
            request.session.pop('error_promo_code')
        return error

    def confirm_btn(self):
        res = super(BsgVehicleCargoSale, self).confirm_btn()
        self.mapped('generated_coupon_ids').write({'state': 'new'})
        self.mapped('applied_coupon_ids').write({'state': 'used'})
        self._cargo_send_reward_coupon_mail()
        return res

    def remove_cargo_coupon(self):
        for rec in self:
            if rec.state == 'draft':
                for coupon_line in rec.mapped('cargo_sale_coupon_ids'):
                    coupon_line.unlink()
                rec.mapped('generated_coupon_ids').write({'state': 'expired','cargo_sale_order_id':False})
                rec.mapped('applied_coupon_ids').write({'state': 'new','cargo_sale_id':False})
                rec.write({'code_promo_program_id':False,'no_code_promo_program_ids':[(6, 0, [])]})
            else:
                raise UserError(_("Can't Remove Coupon From Confirmed Order"))   

    #TODO:Called From Cancel Wizard
    def action_cancel(self):
        res = super(BsgVehicleCargoSale, self).action_cancel()
        self.mapped('generated_coupon_ids').write({'state': 'expired'})
        self.mapped('applied_coupon_ids').write({'state': 'new'})
        return res

    def action_draft(self):
        res = super(BsgVehicleCargoSale, self).action_draft()
        self.mapped('generated_coupon_ids').write({'state': 'reserved'})
        return res

    def _cargo_is_reward_in_order_lines(self, program):
        self.ensure_one()
        return self.order_line_ids.filtered(lambda line:
            line.service_type.product_variant_id == program.reward_product_id 
            #and line.product_uom_qty >= program.reward_product_quantity #No Qty In Cargo Line
            )

    def _cargo_is_global_discount_already_applied(self):
        applied_programs = self.no_code_promo_program_ids + \
                           self.code_promo_program_id + \
                           self.applied_coupon_ids.mapped('program_id')
        return applied_programs.filtered(lambda program: program._is_global_discount_program())



    def _cargo_get_reward_values_discount_fixed_amount(self, program):
        total_amount = sum(self.order_line_ids.mapped('unit_charge'))
        fixed_amount = program._compute_program_amount('discount_fixed_amount', self.currency_id)
        if total_amount < fixed_amount:
            return total_amount
        else:
            return fixed_amount

    def _cargo_get_cheapest_line(self):
        # Unit prices tax included
        return min(self.order_line_ids.filtered(lambda x:x.unit_charge > 0), key=lambda x: x['unit_charge'])

    def _cargo_get_reward_values_discount_percentage_per_line(self, program, line):
        discount_amount =  line.unit_charge * (program.discount_percentage / 100)
        return discount_amount

    def _cargo_get_reward_values_discount(self, program):
        reward_dict = {}
        lines = self.order_line_ids
        if program.discount_type == 'fixed_amount':
            fixed_amount = self._cargo_get_reward_values_discount_fixed_amount(program)
            if fixed_amount:
                for line in lines:  
                    line_name = str(line.sale_line_rec_name) + '-' + str(line.car_make.car_maker.car_make_name) + " " + str(
                        line.car_model.car_model_name) + " " + str(line.car_size.car_size_name) 
                    reward_dict[line.id] ={
                        'name': _("Discount: ") + program.name + line_name,
                        'vehicle_cargo_sale_line_id' : line.id,
                        'product_id': program.discount_line_product_id.id,
                        'price_unit': (fixed_amount/len(lines)),
                        'tax_ids': [(4, tax.id, False) for tax in program.discount_line_product_id.taxes_id],
                        'promo_program_id':program.id,
                    }
                return reward_dict.values()    
        if program.discount_apply_on == 'cheapest_product':
            line = self._cargo_get_cheapest_line()
            if line:
                line_name = str(line.sale_line_rec_name) + '-' + str(line.car_make.car_maker.car_make_name) + " " + str(
                        line.car_model.car_model_name) + " " + str(line.car_size.car_size_name) 
                discount_line_amount = line.unit_charge * (program.discount_percentage / 100)
                if discount_line_amount:
                    taxes = program.is_with_order_taxes and line.tax_ids or []
                    reward_dict[line.id] = {
                        'name': _("Discount: ") + program.name +line_name,
                        'product_id': program.discount_line_product_id.id,
                        'vehicle_cargo_sale_line_id' : line.id,
                        'price_unit':  discount_line_amount,
                        'tax_ids': [(4, tax.id, False) for tax in taxes],
                        'promo_program_id':program.id,
                    }
        elif program.discount_apply_on in ['specific_product', 'on_order']:
            if program.discount_apply_on == 'specific_product':
                print("ON SPecific>>>>>>>>>>>>>>>>>>")
                # We should not exclude reward line that offer this product since we need to offer only the discount on the real paid product (regular product - free product)
                free_product_lines = self.env['loyalty.program'].search([('reward_type', '=', 'product'), ('reward_product_id', 'in', program.discount_specific_product_id.ids)]).mapped('discount_line_product_id')
                lines = lines.filtered(lambda x: x.service_type in program.discount_specific_product_id.mapped('product_tmpl_id') or x.service_type.product_variant_id in free_product_lines)
                print("ON SPecific>>>>>>>>>>>>>>>>>>",lines)
            for line in lines.filtered(lambda x: program.shipment_type and x.shipment_type.id in program.shipment_type.ids or not program.shipment_type):
                discount_line_amount = self._cargo_get_reward_values_discount_percentage_per_line(program, line)

                if discount_line_amount:
                        taxes = program.is_with_order_taxes and line.tax_ids or []
                        line_name = str(line.sale_line_rec_name) + '-' + str(line.car_make.car_maker.car_make_name) + " " + str(
                        line.car_model.car_model_name) + " " + str(line.car_size.car_size_name)

                        reward_dict[line.id] = {
                            'name': _("Discount: ") + program.name + line_name,
                            'product_id': program.discount_line_product_id.id,
                            'vehicle_cargo_sale_line_id' : line.id,
                            'price_unit': discount_line_amount,
                            'tax_ids': [(4, tax.id, False) for tax in taxes],
                            'promo_program_id':program.id,
                        }
        # If there is a max amount for discount, we might have to limit some discount lines or completely remove some lines
        max_amount = program._compute_program_amount('discount_max_amount', self.currency_id)
        if max_amount > 0:
            amount_already_given = 0
            for val in list(reward_dict):
                amount_to_discount = amount_already_given + reward_dict[val]["price_unit"]
                if abs(amount_to_discount) > max_amount:
                    reward_dict[val]["price_unit"] = - (max_amount - abs(amount_already_given))
                    add_name = formatLang(self.env, max_amount, currency_obj=self.currency_id)
                    reward_dict[val]["name"] += "( " + _("limited to ") + add_name + ")"
                amount_already_given += reward_dict[val]["price_unit"]
                if reward_dict[val]["price_unit"] == 0:
                    del reward_dict[val]
        return reward_dict.values()

    def _cargo_get_reward_line_values(self, program):
        self.ensure_one()
        self = self.with_context(lang=self.customer.lang)
        program = program.with_context(lang=self.customer.lang)
        if program.reward_type == 'discount':
            return self._cargo_get_reward_values_discount(program)
        elif program.reward_type == 'product':
            return [self._cargo_get_reward_values_product(program)]

    def _cargo_create_reward_coupon(self, program):
        # if there is already a coupon that was set as expired, reactivate that one instead of creating a new one
        coupon = self.env['loyalty.reward'].search([
            ('program_id', '=', program.id),
            ('state', '=', 'expired'),
            ('partner_id', '=', self.customer.id),
            ('cargo_sale_order_id', '=', self.id),
            ('discount_line_product_id', '=', program.discount_line_product_id.id),
        ], limit=1)
        if coupon:
            coupon.write({'state': 'reserved'})
        else:
            coupon = self.env['loyalty.reward'].create({
                'program_id': program.id,
                'state': 'reserved',
                'partner_id': self.customer.id,
                'cargo_sale_order_id': self.id,
                'discount_line_product_id': program.discount_line_product_id.id
            })
        self.generated_coupon_ids |= coupon
        return coupon

    def _cargo_send_reward_coupon_mail(self):
        self.ensure_one()
        template = self.env.ref('sale_coupon.mail_template_sale_coupon', raise_if_not_found=False)
        if template:
            for coupon in self.generated_coupon_ids:
                self.message_post_with_template(
                    template.id, composition_mode='comment',
                    model='loyalty.reward', res_id=coupon.id,
                    notif_layout='mail.mail_notification_light',
                )

    def _cargo_get_reward_values_product(self, program):
        price_unit = self.order_line_ids.filtered(lambda line: program.reward_product_id == line.service_type.product_variant_id)[0].unit_charge

        order_line_ids = (self.order_line_ids).filtered(lambda x: program._is_valid_product(x.product_id))
        max_product_qty = len(order_line_ids) or 1
        # Remove needed quantity from reward quantity if same reward and rule product
        if program._is_valid_product(program.reward_product_id):
            # number of times the program should be applied
            program_in_order = max_product_qty // (program.rule_min_quantity + program.reward_product_quantity)
            if program.rule_minimum_amount:
                order_total = sum(order_line_ids.mapped('charges')) - (program.reward_product_quantity * program.reward_product_id.lst_price)
                program_in_order = min(program_in_order, order_total // program.rule_minimum_amount)
            # multipled by the reward qty
            reward_product_qty = program.reward_product_quantity * program_in_order
            reward_product_qty = min(reward_product_qty, self.order_line_ids.filtered(lambda x: x.service_type.product_variant_id == program.reward_product_id).product_uom_qty)
        else:
            reward_product_qty = min(max_product_qty, self.order_line_ids.filtered(lambda x: x.service_type.product_variant_id == program.reward_product_id).product_uom_qty)

        reward_qty = min(int(int(max_product_qty / program.rule_min_quantity) * program.reward_product_quantity), reward_product_qty)
        # Take the default taxes on the reward product, mapped with the fiscal position
        taxes = program.reward_product_id.taxes_id
        return {
            'product_id': program.discount_line_product_id.id,
            'price_unit': price_unit,
            'name': _("Free Product") + " - " + program.reward_product_id.name,
            'tax_id': [(4, tax.id, False) for tax in taxes],
        }

    def _cargo_get_applicable_programs(self):
        """
        This method is used to return the valid applicable programs on given order.
        param: order - The sale order for which method will get applicable programs.
        """
        self.ensure_one()
        programs = self.env['loyalty.program'].search([
        ])._cargo_filter_programs_from_common_rules(self)
        if self.promo_code:
            programs._cargo_filter_promo_programs_with_code(self)
        return programs

    def _cargo_get_applicable_no_code_promo_program(self):
        self.ensure_one()
        programs = self.env['loyalty.program'].search([
            ('trigger', '=', 'auto'),
        ])._cargo_filter_programs_from_common_rules(self)
        return programs

    def _get_applied_coupon_program_coming_from_another_so(self):
        # TODO: Remove me in master as no more used
        pass

    def _cargo_get_valid_applied_coupon_program(self):
        self.ensure_one()
        # applied_coupon_ids's coupons might be coming from:
        #   * a coupon generated from a previous order that benefited from a promotion_program that rewarded the next sale order.
        #     In that case requirements to benefit from the program (Quantity and price) should not be checked anymore
        #   * a coupon_program, in that case the promo_applicability is always for the current order and everything should be checked (filtered)
        programs = self.applied_coupon_ids.mapped('program_id').filtered(lambda p: p.promo_applicability == 'on_next_order')._cargo_filter_programs_from_common_rules(self, True)
        programs += self.applied_coupon_ids.mapped('program_id').filtered(lambda p: p.promo_applicability == 'on_current_order')._cargo_filter_programs_from_common_rules(self)
        return programs

    def _cargo_create_new_no_code_promo_reward_lines(self):
        '''Apply new programs that are applicable'''
        self.ensure_one()
        order = self
        programs = order._cargo_get_applicable_no_code_promo_program()
        programs = programs._keep_only_most_interesting_auto_applied_global_discount_program()
        for program in programs:
            error_status = program._cargo_check_promo_code(order, False)
            if not error_status.get('error'):
                if program.promo_applicability == 'on_next_order':
                    order._cargo_create_reward_coupon(program)
                #elif program.id not in self.no_code_promo_program_ids.ids:
                #apply Program
                #     self._cargo_get_reward_line_values(program)
                order.no_code_promo_program_ids |= program

    def _cargo_update_existing_reward_lines(self):
        '''Update values for already applied rewards'''
        def update_line(order, lines, values):
            '''Update the lines and return them if they should be deleted'''
            lines_to_remove = self.env['bsg_vehicle_cargo_sale_coupon']
            # Check commit 6bb42904a03 for next if/else
            # Remove reward line if price or qty equal to 0
            if values['price_unit']:
                lines.write(values)
            else:
                if program.reward_type != 'free_shipping':
                    # Can't remove the lines directly as we might be in a recordset loop
                    lines_to_remove += lines
                else:
                    values.update(price_unit=0.0)
                    lines.write(values)
            return lines_to_remove

        self.ensure_one()
        order = self
        order.cargo_sale_coupon_ids.unlink()
        res = {}
        applied_programs = order._cargo_get_applied_programs_with_rewards_on_current_order()
        for program in applied_programs:
            error_status = program._cargo_check_cargo_condition_promo_code(order)
            if error_status:
                message_id = self.env['message.wizard'].create({'message': _(error_status.get('error'))})
                return {
                    'name': _("Apply Coupon"),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'message.wizard',
                    # pass the id
                    'res_id': message_id.id,
                    'target': 'new'
                }
            values = order._cargo_get_reward_line_values(program)
            #lines = order.cargo_sale_coupon_ids.filtered(lambda line: line.product_id == program.discount_line_product_id)
            if program.reward_type == 'discount':
                #lines_to_remove = lines
                #lines_to_remove.unlink()
                for value in values:
                    order.write({'cargo_sale_coupon_ids': [(0, False, value)]})
            else:
                #TODO:Update Line For Free Qty
                #update_line(order, lines, values[0]).unlink()
                pass
        #To Update Discount Value        
        order._update_coupon_discount()        

    def _cargo_remove_invalid_reward_lines(self):
        """ Find programs & coupons that are not applicable anymore.
            It will then unlink the related reward order lines.
            It will also unset the order's fields that are storing
            the applied coupons & programs.
            Note: It will also remove a reward line coming from an archive program.
        """
        self.ensure_one()
        order = self

        applicable_programs = order._cargo_get_applicable_no_code_promo_program() + order._cargo_get_applicable_programs() + order._cargo_get_valid_applied_coupon_program()
        applicable_programs = applicable_programs._keep_only_most_interesting_auto_applied_global_discount_program()
        applied_programs = order._cargo_get_applied_programs_with_rewards_on_current_order() + order._cargo_get_applied_programs_with_rewards_on_next_order()
        programs_to_remove = applied_programs - applicable_programs
        products_to_remove = programs_to_remove.mapped('discount_line_product_id')

        # delete reward line coming from an archived coupon (it will never be updated/removed when recomputing the order)
        invalid_lines = order.cargo_sale_coupon_ids.filtered(lambda line: line.product_id.id not in (applied_programs).mapped('discount_line_product_id').ids)

        # Invalid generated coupon for which we are not eligible anymore ('expired' since it is specific to this SO and we may again met the requirements)
        self.generated_coupon_ids.filtered(lambda coupon: coupon.program_id.discount_line_product_id.id in products_to_remove.ids).write({'state': 'expired'})
        # Reset applied coupons for which we are not eligible anymore ('valid' so it can be use on another )
        coupons_to_remove = order.applied_coupon_ids.filtered(lambda coupon: coupon.program_id in programs_to_remove)
        coupons_to_remove.write({'state': 'new'})

        # Unbind promotion and coupon programs which requirements are not met anymore
        if programs_to_remove:
            order.no_code_promo_program_ids -= programs_to_remove
            order.code_promo_program_id -= programs_to_remove
        if coupons_to_remove:
             order.applied_coupon_ids -= coupons_to_remove

        # Remove their reward lines
        invalid_lines |= order.cargo_sale_coupon_ids.filtered(lambda line: line.product_id.id in products_to_remove.ids)
        invalid_lines.unlink()

    def _cargo_get_applied_programs_with_rewards_on_current_order(self):
        # Need to add filter on current order. Indeed, it has always been calculating reward line even if on next order (which is useless and do calculation for nothing)
        # This problem could not be noticed since it would only update or delete existing lines related to that program, it would not find the line to update since not in the order
        # But now if we dont find the reward line in the order, we add it (since we can now have multiple line per  program in case of discount on different vat), thus the bug
        # mentionned ahead will be seen now
        return self.no_code_promo_program_ids.filtered(lambda p: p.promo_applicability == 'on_current_order') + \
               self.applied_coupon_ids.mapped('program_id') + \
               self.code_promo_program_id.filtered(lambda p: p.promo_applicability == 'on_current_order')

    def _cargo_get_applied_programs_with_rewards_on_next_order(self):
        return self.no_code_promo_program_ids.filtered(lambda p: p.promo_applicability == 'on_next_order') + \
            self.code_promo_program_id.filtered(lambda p: p.promo_applicability == 'on_next_order')

    def _cargo_create_reward_line(self, program):
            self.write({'cargo_sale_coupon_ids': [(0, False, value) for value in self._cargo_get_reward_line_values(program)]})
            #To Update Discount Value        
            self._update_coupon_discount()

    def _update_coupon_discount(self):
        for line in self.order_line_ids:
            line.fixed_discount = line.subtotal_coupon_amount  
            if line.subtotal_coupon_amount == 0:
                line._onchange_customer_price_list()
                line._onchange_discount()
            line._onchange_fixed_discount()
            
    def unlink(self):
        self.mapped('generated_coupon_ids').write({'state': 'new'})
        self.mapped('applied_coupon_ids').write({'state': 'used'})
        return super(BsgVehicleCargoSale, self).unlink()

class bsg_vehicle_cargo_sale_coupon(models.Model):
    _name = 'bsg_vehicle_cargo_sale_coupon'    

    cargo_sale_order_id = fields.Many2one('bsg_vehicle_cargo_sale',index=True, required=True, ondelete='cascade') 
    vehicle_cargo_sale_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line',index=True, required=True, ondelete='cascade')
    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict')
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    tax_ids = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    currency_id = fields.Many2one(related='vehicle_cargo_sale_line_id.bsg_cargo_sale_id.currency_id', store=True, string='Currency', readonly=True)
    #company_id = fields.Many2one(related='vehicle_cargo_sale_line_id.bsg_cargo_sale_id.company_id', string='Company', store=True, readonly=True)
    promo_program_id = fields.Many2one('loyalty.program', string="Applied Program",copy=False)

    @api.depends('price_unit', 'tax_ids')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit
            taxes = line.tax_ids.compute_all(price, line.vehicle_cargo_sale_line_id.bsg_cargo_sale_id.currency_id, 1, product=line.product_id, partner=line.vehicle_cargo_sale_line_id.customer_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
    
    def unlink(self):
        cargo_sale_order_id = set(self.mapped('cargo_sale_order_id'))
        res = super(bsg_vehicle_cargo_sale_coupon, self).unlink()
        for cargo_order in cargo_sale_order_id:
            cargo_order._update_coupon_discount()
        return res
        
        

class bsg_vehicle_cargo_sale_line(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale_line'

    cargo_sale_coupon_ids = fields.One2many('bsg_vehicle_cargo_sale_coupon','vehicle_cargo_sale_line_id')  
    subtotal_coupon_amount = fields.Monetary(compute='_compute_coupon_amount', string='Subtotal Coupon Amount', readonly=True, store=True)
    tax_coupon_amount = fields.Monetary(compute='_compute_coupon_amount', string='Tax Coupon Amount', readonly=True, store=True)    
    total_coupon_amount = fields.Monetary(compute='_compute_coupon_amount', string='Total Coupon Amount', readonly=True, store=True)    

    @api.depends('cargo_sale_coupon_ids.price_tax','cargo_sale_coupon_ids.price_total','cargo_sale_coupon_ids.price_subtotal')
    def _compute_coupon_amount(self):
        for rec in self:
            rec.subtotal_coupon_amount = sum(rec.cargo_sale_coupon_ids.mapped('price_subtotal'))
            rec.tax_coupon_amount = sum(rec.cargo_sale_coupon_ids.mapped('price_tax'))
            rec.total_coupon_amount = sum(rec.cargo_sale_coupon_ids.mapped('price_total'))