# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class MaxDailySoPerBranch(models.Model):
	_name = 'max_daily_so_per_branch'
	_description = "MAX Daily SO per Branch's"
	_inherit = ['mail.thread']

	#Fields Declaration 
	name = fields.Many2one('bsg_branches.bsg_branches', string="Branch From", tracking=True)
	branch_to_ids = fields.Many2many('bsg_branches.bsg_branches', string="Branches TO", tracking=True)
	shipment_type_ids = fields.Many2many('bsg.car.shipment.type', string='Shipment Types', tracking=True)
	max_so_per_day = fields.Integer(string="MAX SO",tracking=True)
	number_of_day = fields.Integer(string='Number of Day to add it to  Delivery Date',tracking=True)
