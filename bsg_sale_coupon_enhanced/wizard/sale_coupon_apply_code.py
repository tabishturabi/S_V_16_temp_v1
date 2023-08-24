# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleCouponApplyCode(models.TransientModel):
    _inherit = 'sale.loyalty.coupon.wizard'

    coupon_code = fields.Char(string="Coupon", required=True)

    def process_coupon(self):
        """
        Apply the entered coupon code if valid, raise an UserError otherwise.
        """
        if self.env.context.get('active_model') == 'bsg_vehicle_cargo_sale':
            sales_order = self.env['bsg_vehicle_cargo_sale'].browse(self.env.context.get('active_id'))
            error_status = self.cargo_apply_coupon(sales_order, self.coupon_code)
            if error_status.get('error', False):
                raise UserError(error_status.get('error', False))
            if error_status.get('not_found', False):
                raise UserError(error_status.get('not_found', False))
        else:
            return super(SaleCouponApplyCode,self).process_coupon()

    def cargo_apply_coupon(self, order, coupon_code):
        error_status = {}
        program = self.env['loyalty.program'].search([('promo_code', '=', coupon_code)])
        if program:
            error_status = program._cargo_check_promo_code(order, coupon_code)
            if not error_status:
                if program.promo_applicability == 'on_next_order':
                    # Avoid creating the coupon if it already exist
                    if program.discount_line_product_id.id not in order.generated_coupon_ids.filtered(lambda coupon: coupon.state in ['new', 'reserved']).mapped('discount_line_product_id').ids:
                        coupon = order._cargo_create_reward_coupon(program)
                        return {
                            'generated_coupon': {
                                'reward': coupon.program_id.discount_line_product_id.name,
                                'code': coupon.code,
                            }
                        }
                else:  # The program is applied on this order
                    order._cargo_create_reward_line(program)
                    order.code_promo_program_id = program
        else:
            coupon = self.env['loyalty.reward'].search([('code', '=', coupon_code)], limit=1)
            if coupon:
                error_status = coupon._cargo_check_coupon_code(order)
                if not error_status:
                    order._cargo_create_reward_line(coupon.program_id)
                    order.applied_coupon_ids += coupon
                    coupon.write({'state': 'used'})
            else:
                error_status = {'not_found': _('The code %s is invalid') % (coupon_code)}
        return error_status
