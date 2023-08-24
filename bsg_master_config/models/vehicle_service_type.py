# -*- coding: utf-8 -*-

from odoo import models, fields, api

class bsg_vehicle_service_type(models.Model):
    _name = 'bsg_vehicle_service_type'
    _description = "Service Type"
    _inherit = ['mail.thread']
    _rec_name = "v_service_type_name"

    v_service_type_name = fields.Char()
    active = fields.Boolean(string="Active", tracking=True, default=True)
    bsg_ser_income_acc = fields.Many2one(string="Income Account", comodel_name="account.account")
    bsg_ser_expense_acc = fields.Many2one(string="Expense Account", comodel_name="account.account")