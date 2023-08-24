# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class RoundTripCancel(models.Model):
	_name = 'round.trip.cancel'
	_inherit = ['mail.thread']
	_description = "Round Trip Cancel"
	_rec_name = "rtc_from_km"

	rtc_reason_name = fields.Char()
	active = fields.Boolean(string="Active", tracking=True, default=True)
	rtc_from_km = fields.Integer(srting="From")
	rtc_to_km = fields.Integer(srting="To")
	rtc_percentage = fields.Float(string="Percentate %")
	is_cancel = fields.Boolean(string="Cancel")
