# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DriverRewardPerDelivery(models.Model):
	_name = 'driver_reward_per_delivery'
	_description = "Driver Reward Delivery"
	_inherit = ['mail.thread','mail.activity.mixin']
	_rec_name = 'amount_per_car'

	from_km = fields.Integer(srting="From")
	to_km = fields.Integer(srting="To")
	amount_per_car = fields.Integer(string="Type A")
	amount_per_car_b = fields.Integer(string="Type B")
	empty_amount_per_car = fields.Integer(string="Amount per Car.")