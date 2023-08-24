# -*- coding: utf-8 -*-
from odoo import _, api, fields, models,tools
import logging

class bsg_vehicle_cargo_sale_line(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale_line'

    # @api.multi
    def print_tag_report(self):
        return self.env.ref('cargo_tag_report.report_cargo_tag').report_action(self.id)

