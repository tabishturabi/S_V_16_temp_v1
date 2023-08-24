# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
# Migration Note
# account.asset.category not in base
# class AccountAssetCategory(models.Model):
#     _inherit = 'account.asset.category'
#
#     bsg_branches_id = fields.Many2one('bsg_branches.bsg_branches', string="Branch")
#     department_id = fields.Many2one('hr.department',string="Department")
#     fleet_vehicle_id = fields.Many2one('fleet.vehicle',string="Truck")