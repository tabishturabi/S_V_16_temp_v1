from odoo import models, fields
class AccountPayment(models.Model):
    _inherit = 'account.payment'
    transaction_reference = fields.Char('Transaction Reference', readonly=True)
    app_fortid = fields.Char('Payfort Transaction ID', readonly=True)
    driver_collection_id = fields.Many2one('driver.cash.credit.collection')

    def action_validate_invoice_payment(self):
        driver_collection_id = self._context.get('driver_collection_id', False)
        res = super(AccountPayment, self).action_validate_invoice_payment()
        if driver_collection_id:
            collection_id = self.env['driver.cash.credit.collection'].browse(driver_collection_id)
            collection_id.write({'state': 'processed', 'payment_id':self.id})
        return res

