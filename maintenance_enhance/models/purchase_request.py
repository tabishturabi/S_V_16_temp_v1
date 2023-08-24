from odoo import models, fields, api, _


class PurchaseRequest(models.Model):
    _inherit = 'purchase.req'

    maintenance_request_id = fields.Many2one('maintenance.request.enhance', string="Maintenance Work Order Request")
