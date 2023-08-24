# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.company"

    sequnce_id = fields.Many2one('ir.sequence', string="Internal Sequence")
