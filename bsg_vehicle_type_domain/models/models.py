# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class VehicleDomain(models.Model):
    _name = 'vehicle.type.domain'
    _description = 'Vehicle Type Domain'

    name = fields.Char(string='Domain')
    sequence = fields.Integer(help="Used to order the note stages")
    sales_analytic_account = fields.Many2one('account.analytic.account',string="Sales Analytic Account")
    sales_analytic_tag = fields.Many2one('account.account.tag',string="Sales Analytic Tags")
    _sql_constraints = [
        ('name_uniq','unique (name)','Domain name already exists!')
    ]


class VehicleTypeTableInherit(models.Model):
    _inherit = 'bsg.vehicle.type.table'

    domain_name = fields.Many2one('vehicle.type.domain',string='Domain Name')




