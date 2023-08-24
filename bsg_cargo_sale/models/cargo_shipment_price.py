# -*- coding: utf-8 -*-
import math
import re
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError
import requests
from odoo.addons import decimal_precision as dp


class BsgShipmentPrice(models.TransientModel):
    _name = 'bsg_shipment_price'

    @api.model
    def _default_get_pricelist(self):
        price_id = self.env['product.pricelist'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                     company_id=self.env.user.company_id.id).search(
            [('is_public', '=', 'True')], limit=1)

        if price_id:
            return price_id.id
        else:
            return False

    @api.model
    def _default_get_tax_id(self):
        tax_id = self.env['account.tax'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                             company_id=self.env.user.company_id.id).search(
            [('amount', '=', 15), ('type_tax_use', '=', 'sale')], limit=1)

        if tax_id:
            return tax_id.id
        else:
            return False

    customer_type = fields.Selection(string='Customer Type', selection=[
        ('individual', 'Individual'),
        ('corporate', 'Corporate')
    ], default="individual")
    shipment_type = fields.Selection(string="Agreement Type", selection=[
        ('return', 'Round Trip'),
        ('oneway', 'Oneway')
    ], default="oneway")
    customer_price_list = fields.Many2one('product.pricelist', string="Pricelist", default=_default_get_pricelist)
    ship_type = fields.Many2one(string="Shipment Type", comodel_name="bsg.car.shipment.type")
    loc_from = fields.Many2one(string="From", comodel_name="bsg_route_waypoints")
    loc_to = fields.Many2one(string="To", comodel_name="bsg_route_waypoints")
    car_make = fields.Many2one(string="Car Maker", comodel_name="bsg_car_config")
    car_model = fields.Many2one(string="Model", comodel_name="bsg_car_model")
    car_size = fields.Many2one(string="Car Size", comodel_name="bsg_car_size", compute="_get_car_size")
    tax_id = fields.Many2one(string="Taxes", comodel_name="account.tax", default=_default_get_tax_id)
    discount = fields.Float(string="Discount Amount", readonly=True)
    amount = fields.Float(string="Agreement Amount", readonly=True)
    total_amount = fields.Float(string="Total Agreement Amount", readonly=True)
    order_date = fields.Datetime(string="Order Date", default=lambda self: fields.datetime.now())
    est_no_delivery_days = fields.Integer(string='Est No of Days', store=True)
    est_no_hours = fields.Float(string='Est No of Hours', store=True)
    est_max_no_delivery_days = fields.Integer(string='Est Max No of Days', store=True)
    est_max_no_hours = fields.Float(string='Est Max No of Hours', store=True)

    @api.onchange('car_make')
    def onchange_car_make(self):
        if self.car_make:
            self.car_model = False
            car_models = []
            for line in self.car_make.car_line_ids:
                car_models.append(line.car_model.id)
            return {'domain': {'car_model': [('id', 'in', car_models)]}}

    # 
    @api.depends('car_model', 'car_make', 'ship_type')
    def _get_car_size(self):
        self.car_size = False
        if self.car_model and self.car_make:
            for car_line in self.car_make.car_line_ids:
                if car_line.car_model.id == self.car_model.id:
                    self.car_size = car_line.car_size.id

        if self.ship_type:
            if not self.ship_type.is_normal:
                self.car_size = self.ship_type.car_size.id

    @api.onchange('ship_type', 'loc_from', 'loc_to')
    def _onchange_order_price_list_domain(self):
        for rec in self:
            domain = ['|', ('location_domain', '!=', True), '|', ('loc_from_ids', '=', False),
                      ('loc_from_ids', 'in', rec.loc_from.id), '|', ('loc_to_ids', '=', False),
                      ('loc_to_ids', 'in', rec.loc_to.id)
                , '|', ('shipment_type', '=', False), ('shipment_type', 'in', rec.ship_type.id),
                      '|', ('date_from', '=', False), ('date_from', '<=', rec.order_date), '|', ('date_to', '=', False),
                      ('date_to', '>=', rec.order_date)]
            if rec.customer_price_list:
                customer_price = self.env['product.pricelist'].search(domain)
                if not customer_price or rec.customer_price_list.id not in customer_price.ids:
                    rec.customer_price_list = self._default_get_pricelist()
                    rec.onchange_get_price()
                    rec.onchange_total_price()
            if rec.loc_from and rec.loc_to and rec.ship_type:
                est_delivery_days_id = self.env['bsg.estimated.delivery.days'].search(
                    [('shipemnt_type', '=', rec.ship_type.id), ('loc_from_id', '=', rec.loc_from.id),
                     ('loc_to_id', '=', rec.loc_to.id)], limit=1)
                rec.est_no_delivery_days = est_delivery_days_id.est_no_delivery_days
                rec.est_no_hours = est_delivery_days_id.est_no_hours
                rec.est_max_no_delivery_days = est_delivery_days_id.est_max_no_delivery_days
                rec.est_max_no_hours = est_delivery_days_id.est_max_no_hours

    @api.onchange('car_make', 'car_model', 'car_size', 'loc_from', 'loc_to', 'customer_type', 'shipment_type',
                  'customer_price_list', 'ship_type')
    def onchange_get_price(self):
        if self.car_size and self.loc_from and self.loc_to and self.customer_type and self.shipment_type:
            search_id = self.env['bsg_price_line'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                       company_id=self.env.user.company_id.id).search(
                [('price_config_id.waypoint_from', '=', self.loc_from.id),
                 ('price_config_id.waypoint_to', '=', self.loc_to.id),
                 ('price_config_id.customer_type', '=', self.customer_type), ('car_size', '=', self.car_size.id)],
                limit=1)
            if search_id:
                if self.shipment_type == 'return' and self.customer_price_list.is_public:
                    self.amount = search_id.price * 2
                    self.discount = 10
                    self.onchange_total_price()
                elif self.shipment_type == 'return' and not self.customer_price_list.is_public:
                    self.amount = search_id.price * 2
                    price_id = self.env['product.pricelist.item'].sudo().with_context(
                        force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                        [('pricelist_id.id', '=', self.customer_price_list.id)], limit=1)
                    if price_id:
                        if price_id.percent_price:
                            self.discount = self.amount * price_id.percent_price / 100
                        else:
                            self.discount = 0.0
                    self.onchange_total_price()
                else:
                    self.amount = search_id.price
            else:
                self.amount = 0

            if self.customer_price_list:
                price_id = self.env['product.pricelist.item'].sudo().with_context(
                    force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                    [('pricelist_id.id', '=', self.customer_price_list.id)], limit=1)
                if price_id:
                    if price_id.pricelist_id.is_public and self.shipment_type == 'oneway':
                        self.discount = 0
                    elif not price_id.pricelist_id.is_public and self.shipment_type == 'oneway':
                        self.discount = self.amount * price_id.percent_price / 100
                    elif price_id.pricelist_id.is_public and self.shipment_type == 'return':
                        self.discount = self.amount * 10 / 100
                    elif not price_id.pricelist_id.is_public and self.shipment_type == 'return':
                        self.discount = self.amount * price_id.percent_price / 100
                    else:
                        self.discount = 0
                else:
                    self.discount = 0

    @api.onchange('discount', 'amount', 'tax_id')
    def onchange_total_price(self):
        value = 0
        if self.tax_id:
            value = (self.amount - self.discount) * (self.tax_id.amount / 100)
        self.total_amount = (self.amount - self.discount) + value

    
    def close_wizard(self):
        pass

    
    def new_wizard(self):
        return {'name': 'Shipment Price',
                'domain': [],
                'res_model': 'bsg_shipment_price',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new', }






