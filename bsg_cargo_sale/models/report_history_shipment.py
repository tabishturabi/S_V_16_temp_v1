# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ReportHistoryShipment(models.Model):
	_name = 'report.history.shipment'
	_description = "Shipment Report History"
	_inherit = ['mail.thread']
	_rec_name = "sr_print_no"

	active = fields.Boolean(string="Active", track_visibility=True, default=True)
	sr_print_no = fields.Char(
		string='Seq#',
	)
	sr_user_id = fields.Many2one(string="User Name", comodel_name="res.users")
	sr_print_date = fields.Datetime(string='Print Date')

	cargo_so_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line', string='CSO line') 
