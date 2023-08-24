# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DriverRewardByRevenue(models.Model):
	_name = 'driver_reward_by_revenue'
	_description = "Driver Rewards By Revenue"
	_inherit = ['mail.thread','mail.activity.mixin']
	_rec_name = 'leval_stage'

	from_km = fields.Integer(srting="From")
	to_km = fields.Integer(srting="To")
	amount_per_car = fields.Integer(string="Amount per Car")
	leval_stage = fields.Selection([('level_1','Level 1'),('level_2','Level 2'),
		('level_3','Level 3'),('level_4','Level 4')],string="Level Stage")
