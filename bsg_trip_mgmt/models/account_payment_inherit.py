# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# Account Payment
class AccountPayment(models.Model):
	_inherit = 'account.payment'

	is_pay_trip_money = fields.Boolean(string="Is Pay Trip Money")
	is_pay_driver_rewards = fields.Boolean(string="Pay Driver Reward")
	fleet_trip_id = fields.Many2one('fleet.vehicle.trip',string="Trip ID")

class BsgPriceConfig(models.Model):
	_inherit = 'bsg_price_config'

	# @api.multi
	def unlink(self):
		if self.env.user.has_group('bsg_trip_mgmt.group_price_config'):
			raise UserError(_('You cannot Delete these Record'))
		result = super(AccountPayment, self).unlink()
		return result
