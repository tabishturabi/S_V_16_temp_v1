from odoo  import models, fields, api, _

class PaymentTransactionPartialRefund(models.TransientModel):
    _name = 'payment.transaction.partial.refund'