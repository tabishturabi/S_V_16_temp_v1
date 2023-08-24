
# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BsgCustomerLocations(models.Model):
	_name = 'bsg.customer.locations'
	_description = "Region Configuration"
	_inherit = ['mail.thread']
	_rec_name="bsg_loc_customer_id"

	bsg_loc_customer_id = fields.Many2one('res.partner',string="Customer")
	bsg_locations_ids = fields.One2many('bsg.customer.locations.line','bsg_location_id','Locations')


class BsgCustomerLocationsLine(models.Model):
	_name = 'bsg.customer.locations.line'
	_description = "Location"

	location_name = fields.Char('Location Name')
	bsg_location_id = fields.Many2one('bsg.customer.locations','Location ID')