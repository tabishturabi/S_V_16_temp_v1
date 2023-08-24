# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FineForLateArrival(models.Model):
	_name = 'fine_for_late_arrival'
	_description = "Fine For Late Arrival"
	_inherit = ['mail.thread','mail.activity.mixin']
	_rec_name = 'deduction_from_reqard'

	from_km = fields.Integer(srting="From")
	to_km = fields.Integer(srting="To")
	deduction_from_reqard = fields.Integer(string="Deduction From  Rewards %")
