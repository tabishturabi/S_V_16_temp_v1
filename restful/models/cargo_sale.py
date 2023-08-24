from odoo import models, fields
class BsgVehicleCargoSale(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale'
    
    app_payment_method = fields.Selection([('cash', 'Cash'), ('credit', 'Credit')], strin="App Payment Method", readonly=True)
    app_paid_amount = fields.Float('App Paid Amount', readonly=True)
    app_fortid = fields.Char('Payfort Transaction ID', readonly=True)
    transaction_reference = fields.Char('Transaction Reference', readonly=True)
    gps_location_from = fields.Char('GPS Location From', readonly=True)
    gps_location_to = fields.Char('GPS Location To', readonly=True)
    gps_distance = fields.Float('GPS Distance (KM)', readonly=True)
    gps_time = fields.Float('GPS Time (Muintes)', readonly=True)
    api_request_vals = fields.Text()