from odoo import models, fields


class BsgVehicleCargoSaleLine(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale_line'

    drive_cash_credit_collection_ids = fields.One2many('driver.cash.credit.collection', 'cargo_sale_line_id')
    customer_otp = fields.Char('Customer OTP')
