# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BsgInheritResUsers(models.Model):
	_inherit = 'res.users'

	user_branch_id = fields.Many2one("bsg_branches.bsg_branches", string="Branch")
	user_branch_ids = fields.Many2many("bsg_branches.bsg_branches", string="Branches")
	discount_cargo_id = fields.Many2one("discount.cargo", string="Allowed Discount")