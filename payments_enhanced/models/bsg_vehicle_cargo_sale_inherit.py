# -*- coding: utf-8 -*-

from odoo import _, api, fields, models,_
from odoo.exceptions import UserError


class CargoSale(models.Model):
    _inherit = "bsg_vehicle_cargo_sale"

    # @api.multi
    def print_voucher(self):
        payment_ids = self.env['account.payment'].search([('invoice_ids', 'in', self.sudo().invoice_ids.ids), ('is_reconciled', '=', True)]).filtered(lambda r: r.state != 'reversal_entry')
        if self.sudo().invoice_ids and payment_ids:
            return self.sudo().env.ref('payments_enhanced.report_payment_receipt_report').report_action(payment_ids[0])
        else:
            raise UserError(_('No Invoice or payment found against this order'))

    # @api.multi
    def print_return_voucher(self):
        if self.reversal_move_id and self.reversal_move_id.payment_ids:
            return self.env.ref('payments_enhanced.report_payment_receipt_report').report_action(self.reversal_move_id[0].payment_ids[0])
