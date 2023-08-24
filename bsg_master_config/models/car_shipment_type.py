# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BsgCarShipmentType(models.Model):
	_name = 'bsg.car.shipment.type'
	_inherit = ['mail.thread']
	_description = "Shipment Type"
	_rec_name = "car_shipment_name"

	car_shipment_name = fields.Char('Arabic Name')
	car_shipment_name_en = fields.Char('English Name')
	car_size = fields.Many2one(string="Car Size", comodel_name="bsg_car_size")
	is_normal = fields.Boolean(string="Is Normal")
	calculation_type = fields.Selection([('percentage', 'Percentage %'), ('fixed_amount', 'Fixed Amount')],string="Calculation Type")
	is_express_shipment = fields.Boolean(string="Is Express Shipment")
	percentage_express_shipment = fields.Float(string="Percentage Express Shipment")
	shipment_extra_charges = fields.Float(string="Shipment Extra Charges", default=0.0)
	is_vip = fields.Boolean(string="Is VIP")
	is_satha = fields.Boolean(string="Is Satha")
	is_coupon_applicable = fields.Boolean('Is Coupon Applicable')
	has_demurage_config = fields.Boolean('Has Demmrage Config')
	car_model = fields.Many2many("bsg_car_model",string="Car Model")
	active = fields.Boolean(string="Active", track_visibility=True, default=True)

	@api.onchange('is_normal')
	def _onchange_is_normal(self):
		if self.is_normal:
			self.car_shipment_name = "Normal"

	@api.onchange('car_size')
	def _onchange_car_size(self):
		if self.car_size:
			self.car_shipment_name = self.car_size.car_size_name