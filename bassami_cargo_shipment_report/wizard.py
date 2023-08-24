# #-*- coding:utf-8 -*-

import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta, timezone
import datetime
import time
from odoo import api, models, fields
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
import string
import sys
import logging
import pytz

_logger = logging.getLogger(__name__)

class BsgVehicleCargoSale(models.Model):
	_inherit = 'bsg_vehicle_cargo_sale'

	order_date_date = fields.Date(string="Order Date Date",store=True, default=lambda self: fields.Date.today())

	@api.model
	def create(self,vals):
		res = super(BsgVehicleCargoSale, self).create(vals)
		res.order_date_date = res.order_date and res.order_date.date() or False
		return res
	
	# @api.multi
	def write(self,vals):
		res = super(BsgVehicleCargoSale, self).write(vals)
		if vals.get('order_date', False):
			self.order_date_date = self.order_date and self.order_date.date() or False
		return res
  
class bsg_vehicle_cargo_sale_line(models.Model):
	_inherit = 'bsg_vehicle_cargo_sale_line'

	order_date_date = fields.Date(string="Order Date Date",related="bsg_cargo_sale_id.order_date_date",store=True)

class CargoSaleLineState(models.Model):
	_name = 'cargo.sale.line.state'
	_rec_name = 'state_label'

	state_label = fields.Char('Label', compute="_compute_label", readonly=True)
	name = fields.Selection([
		('draft', 'Draft'),
		('confirm', 'Confirm'),
		('awaiting', 'Awaiting Return'),
		('shipped', 'Shipped'),
		('on_transit', 'On Transit'),
		('Delivered', 'Delivered On Branch'),
		('done', 'Done'),
		('released', 'Released'),
		('cancel', 'Declined')
		], string='State', required=True)
	
	_sql_constraints = [
	('name_uniq', 'unique (name)', 'State name already exist!')
	]

	@api.depends('name')
	def _compute_label(self):
		for rec in self:
			rec.state_label = dict(self._fields['name'].selection).get(rec.name)


class CargoShipmentReportBassami(models.TransientModel):
	_name = "cargo.shipment.report"

	form = fields.Datetime(string="From",required=True)
	to = fields.Datetime(string="To",required=True)
	partner_types = fields.Many2one("partner.type",string="Partner Type", domain="['|',('is_custoemer','=',True),('is_dealer','=',True)]")
	payment_method_ids = fields.Many2many('cargo_payment_method', string="Payment Methods")
	customer_id = fields.Many2one(comodel_name="res.partner", string="Customer")
	user_id = fields.Many2one(comodel_name="res.users", string="User")
	loc_from = fields.Many2one(string="Location From", comodel_name="bsg_route_waypoints")
	loc_to = fields.Many2one(string="Location To", comodel_name="bsg_route_waypoints")
	# sale_line_state_ids = fields.Many2many('cargo.sale.line.state', string='States')
	state = fields.Selection([
		('shipped','Shipped'),    
		('unshipped','Not shipped')], string="State") #TODO fix naming and show actual shipped and not shipped SO lines acorrding to new criteria .. Gaga
	cc_invoice = fields.Selection([('invoiced','CC Invoiced'),('not_invoiced','CC Not Invoiced')], string='CC Invoice')
	invoice_status = fields.Selection([('paid','Paid'), ('not_paid', 'Not Paid')], 'Invoice Status')
	cargo_sale_type = fields.Selection(string="Cargo Sale Type", selection=[
		('local', 'Local'),
		('international', 'International')])
	report_type = fields.Selection(string="Filter",required=True,selection=[
		('detail','Detail'),    
		('summary','Summary'),
		('revenue', 'Revenue') 
	])

	
	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['form','to','partner_types','payment_method_ids','loc_from','loc_to','customer_id','user_id', 'create_uid','state', 'cargo_sale_type', 'cc_invoice', 'invoice_status'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['form','to','partner_types','payment_method_ids','loc_from','loc_to','customer_id','user_id','state', 'cargo_sale_type', 'cc_invoice', 'invoice_status'])[0])
		rec = self.read(['form','to','partner_types','payment_method_ids','loc_from','loc_to','customer_id','user_id', 'create_uid', 'state', 'cargo_sale_type', 'cc_invoice', 'invoice_status'])[0]
		return self.env.ref('bassami_cargo_shipment_report.report_for_branches_ledger').report_action(self, data=data)
	

class SaleRevenueByPartnerType(models.TransientModel):
	_name = "sale.revenue.by.partner.type"

	form = fields.Datetime(string="From",required=True)
	to = fields.Datetime(string="To",required=True)
	report_type = fields.Selection([('summary','Summary'),
									('details_shipped','Details Shipped'),
									('details_not_shipped','Details Not Shipped'),
									('cash_flow', 'Cash Flow'),
									],'Report Type', default='cash_flow')
	satha_only = fields.Boolean('Include Satha only?')
	cargo_sale_type = fields.Selection([('local', 'Local'), ('international', 'International')], 'Sale type')
	link = fields.Boolean('Link?')
	affected_records = fields.Integer('Affected Records', readonly=True)
	
	# @api.multi
	def print_xls_report(self):
		data = {}
		data['form'] = self.read(['form','to', 'cargo_sale_type', 'satha_only','report_type',])[0]
		return self.env.ref('bassami_cargo_shipment_report.sale_revenue_partner_type_report_id').report_action(self, data=data)
	
	# @api.multi
	def generate_report(self):
		data = {}
		data['form'] = self.read(['form','to', 'cargo_sale_type', 'satha_only'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['form','to', 'cargo_sale_type', 'satha_only'])[0])
		self.write({'form': data['form']['form'] + timedelta(hours=3), 'to': data['form']['to'] + timedelta(hours=3)})
		if self.report_type in ['summary', 'cash_flow']:
			return self.env.ref('bassami_cargo_shipment_report.revenue_by_partner').report_action(self, data=data)
		else:
			return self.env.ref('bassami_cargo_shipment_report.revenue_details_report').report_action(self, data=data)


	# @api.multi
	def link_trip_to_sale_line(self):
		trip_ids = self.env['fleet.vehicle.trip'].search([('state','not in', ['draft', 'cancelled'])])
		trip_history = self.env['bsg.sale.line.trip.history']
		affected_recs = 0
		for trip_id in trip_ids:
			for line in trip_id.stock_picking_id:
				if (not line.picking_name.fleet_trip_id or (line.picking_name.fleet_trip_id and line.picking_name.fleet_trip_id.id != trip_id.id))\
					 and (not line.picking_name.trip_history_ids or(line.picking_name.trip_history_ids and trip_id.id not in [trip.id for trip in line.picking_name.trip_history_ids.mapped('fleet_trip_id')])):
					if self.link:
						trip_history.create({
							'cargo_sale_line_id':line.picking_name.id,
							'fleet_trip_id':trip_id.id
						})
					else:
						affected_recs+=1
		self.affected_records = affected_recs
		return {"type": "ir.actions.do_nothing"}


