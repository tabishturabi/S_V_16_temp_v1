from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError



class BsgVehicleCargoSale(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale'

    tamara_transaction_ids = fields.Many2many('payment.transaction', 'tamara_cargo_sale_transaction_rel', 'cargo_sale_id',
                                               'transaction_id',domain=[('is_tamara','=',True)],
                                               string='Tamara Transactions', copy=False, readonly=True)
    is_tamara_checkout = fields.Boolean("Tamara Checkout Sent",default=False)
    is_tamara_call_second = fields.Boolean("Tamara Call Second",default=False)
    tamara_payment_sms_mobile_no = fields.Char('Tamara Payment SmS Mobile No.', readonly=True)
    is_paid_by_tamra = fields.Boolean()

    
    def pay_via_tamara_wizard(self):
        view_id = self.env.ref('payment_tamara.cargo_sale_tamara_wiz_form').id

        tot_amount = sum(self.env['account.move'].search(
            [('move_type', '=', 'out_invoice'), ('payment_state', '!=', 'paid'), ('cargo_sale_id', '=', self.env.context.get('active_id'))]).mapped('amount_residual'))
        if tot_amount <= 0:
            raise ValidationError(_("Already paid with tamara pls reload your page"))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Cargo Sale Tamara',
            'view_mode': 'form',
            'res_model': 'cargo.sale.tamara.wiz',
            'view_id': view_id,
            'target': 'new',
        }
