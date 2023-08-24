# #-*- coding:utf-8 -*-

import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import api, models, fields
from odoo.exceptions import Warning, ValidationError
from odoo.tools import config
import base64
import string
import sys


class SaleRevenueByBranch(models.TransientModel):
    _name = "sale.revenue.by.branch"

    form = fields.Datetime(string="From", required=True)
    to = fields.Datetime(string="To", required=True)
    report_type = fields.Selection([('summary', 'Summary'),
                                    ('details_shipped', 'Details Shipped'),
                                    ('details_not_shipped', 'Details Not Shipped'),
                                    ('cash_flow', 'Cash Flow'),
                                    ], 'Report Type', default='cash_flow')
    satha_only = fields.Boolean('Include Satha only?')
    # cargo_sale_type = fields.Selection([('local', 'Local'), ('international', 'International')], 'Sale type')
    link = fields.Boolean('Link?')
    affected_records = fields.Integer('Affected Records', readonly=True)
    payment_method_ids = fields.Many2many('cargo_payment_method', string="Payment Methods")
    ship_loc = fields.Many2many('bsg_route_waypoints', 'from_bsg_route_waypoints_branch_revenue_rel', 'wizard_id',
                                'from_id', string="Shipping Location")
    drop_loc = fields.Many2many('bsg_route_waypoints', 'to_bsg_route_waypoints_branch_revenue_rel', 'wizard_id',
                                'to_id', string="Drop Location")
    users = fields.Many2many('res.users', string="Users")
    customer_ids = fields.Many2many('res.partner', string="Customers")
    state = fields.Selection(
        [
            ('all', 'All'),
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('awaiting', 'Awaiting Return'),
            ('shipped', 'Shipped'),
            ('on_transit', 'On Transit'),
            ('Delivered', 'Delivered On Branch'),
            ('done', 'Done'),
            ('released', 'Released'),
            ('cancel', 'Declined'),
            ('received', 'Received'),
            ('not_received', 'Not Received'),
            ('shipping', 'Shipping'),
            ('unshipping', 'Unshipping'),
            ('both_shipping_unshipping', 'Both Shipping/Unshipping'),
        ], default='all', )
    trip_type = fields.Selection([
        ('all', 'All'),
        ('auto', 'تخطيط تلقائي'),
        ('manual', 'تخطيط يدوي'),
        ('local', 'خدمي')
    ], string="Trip Type", default="all")
    pay_case = fields.Selection([
        ('both', 'All'),
        ('paid', 'Paid'),
        ('not_paid', 'Not Paid')], string='Payment State', required=True, default="both")
    cargo_sale_type = fields.Selection(string="Cargo Sale Type", default="all", selection=[
        ('all', 'All'),
        ('local', 'Local'),
        ('international', 'International')])
    user_type = fields.Selection(string="User Type", default="all", selection=[
        ('all', 'All'),
        ('specific', 'Specific'),
    ], required=True)
    branch_type = fields.Selection(string="Ship Location Filter", default="all", selection=[
        ('all', 'All'),
        ('specific', 'Specific'),
    ], required=True)
    branch_type_to = fields.Selection(string="Drop Location Filter", default="all", selection=[
        ('all', 'All'),
        ('specific', 'Specific'),
    ], required=True)
    payment_method_filter = fields.Selection(string="Pay Methods Filter", default="all", selection=[
        ('all', 'All'),
        ('specific', 'Specific'),
    ], required=True)
    customer_filter = fields.Selection(string="Customer Filter", default="all", selection=[
        ('all', 'All'),
        ('specific', 'Specific'),
    ], required=True)
    sale_order_state = fields.Selection(
        [('all', 'All'),
         ('confirm', 'Confirm'),
         ('pod', 'Delivery'),
         ('done', 'Done'),
         ('Delivered', 'Delivered'),
         ], string='Sale Order State', default="all")
    invoicep_line_filter = fields.Selection(
        [('all', 'All'),
         ('paid', 'Paid'),
         ('unpaid', 'Unpaid'),
         ], string='Invoice Paid/Unpaid', default="all")
    with_cc = fields.Selection(string="Add To CC", default="all", selection=[
        ('all', 'All'),
        ('add_to_cc', 'Add To CC'),
        ('not_add_to_cc', 'Not Add To CC'),
    ], required=True)
    with_summary = fields.Boolean(string='With Summary')
    so_line_state = fields.Selection(
        [('all', 'All'),
         ('paid', 'Paid'),
         ('unpaid', 'Unpaid'),
         ], string='SO Line State', default="all")
    create_from = fields.Selection(
        [('all', 'All'),
         ('mobile_app', 'From Mobile App'),
         ('portal', 'From Portal'),
         ('branch', 'From Branch'),
         ], string='Create From', default="all")
    partner_type_filter = fields.Selection(string="Partner Type Filter", default="all", selection=[
        ('all', 'All'),
        ('specific', 'Specific'),
    ], required=True)
    Partner_type_ids = fields.Many2many('partner.type', string="Partner Type")
    shipment_type_filter = fields.Selection(string="Shipment Type Filter", default="all", selection=[
        ('all', 'All'),
        ('specific', 'Specific'),
    ], required=True)
    shipment_type_ids = fields.Many2many('bsg.car.shipment.type', string="Shipment Type")
    car_size_filter = fields.Selection(string="Car Size Filter", default="all", selection=[
        ('all', 'All'),
        ('specific', 'Specific'),
    ], required=True)
    car_size_ids = fields.Many2many('bsg_car_size', string="Car Size")

    # @api.multi
    def print_xls_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bassami_sale_revenue_branch_report.revenue_branch_id').report_action(self, data=data)

    def generate_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bassami_sale_revenue_branch_report.revenue_by_branch').report_action(self, data=data)




