from odoo import api, models, fields, _


class BsgCarSize(models.Model):
    _inherit = 'bsg_car_size'

    weight = fields.Integer("Weight")

