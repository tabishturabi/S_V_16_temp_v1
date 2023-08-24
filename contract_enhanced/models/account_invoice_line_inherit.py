# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    branch_id = fields.Many2one('bsg_branches.bsg_branches', string="Branch ID")
    department_id = fields.Many2one('hr.department', string="Department", track_visibility='always')
    fleet_id = fields.Many2one('fleet.vehicle', string="Truck")
    trailer_id = fields.Many2one('bsg_fleet_trailer_config','Trailer')
