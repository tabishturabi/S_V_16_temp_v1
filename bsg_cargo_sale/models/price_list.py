# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError,ValidationError
from pytz import timezone, UTC
class ProductPricelist(models.Model):
	_inherit = 'product.pricelist'

	is_cash = fields.Boolean("IS CASH PAYMENT ONLY",default=False)
	is_public = fields.Boolean("Is Public",default=False)
	location_domain = fields.Boolean("By Locations",default=False,track_visibility='onchange')
	loc_from_ids = fields.Many2many('bsg_route_waypoints','product_pricelist_from_location_rel','pricelist_id', 'location_from_id',string="From Loctions",track_visibility='onchange')
	loc_to_ids = fields.Many2many('bsg_route_waypoints','product_pricelist_to_location_rel','pricelist_id', 'location_to_id',string="To Loctions",track_visibility='onchange')
	shipment_type = fields.Many2many(string="Shipment Type", comodel_name="bsg.car.shipment.type")
	partner_types = fields.Many2many("partner.type",track_visibility='onchange',string="Partner Type")
	date_from = fields.Datetime(string="Date From")
	date_to = fields.Datetime(string="Date To")
	is_attachment_required = fields.Boolean('Is attachment required', default=False)
	is_qr_required = fields.Boolean('Is Qr Code required', default=False)
	agreement_type = fields.Selection(string="Agreement Type", selection=[
		('return', 'Round Trip'),
		('oneway', 'Oneway')
	],track_visibility='onchange')
	pricelist_code = fields.Char("Code")
  
	@api.constrains('date_from', 'date_to')
	def _check_dates(self):
		for rec in self:
			if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
				raise ValidationError(_('Date From Must Be Before Date To'))

	@api.onchange('date_from','date_to')
	def onchange_default_time(self):
		tz = timezone(self.env.context.get('tz') or self.env.user.tz)
		
		if self.date_from:
			from_date_tz = UTC.localize(self.date_from).astimezone(tz).replace(hour=00, minute=00, second=00).replace(tzinfo=None)
			self.date_from  = tz.localize(from_date_tz).astimezone(UTC).replace(tzinfo=None)

		if self.date_to:
			to_date_tz = UTC.localize(self.date_to).astimezone(tz).replace(hour=23, minute=59, second=59).replace(tzinfo=None)
			self.date_to  = tz.localize(to_date_tz).astimezone(UTC).replace(tzinfo=None)



