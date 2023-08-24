# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BsgInheritHrEmployee(models.Model):
    _inherit = 'hr.employee'

    bsg_branch_id = fields.Many2one(string="Branch ID", comodel_name="bsg_branches.bsg_branches")
