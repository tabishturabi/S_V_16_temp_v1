# -*- coding: utf-8 -*-

from odoo import models,fields,api

class AccountPayment(models.Model):
    _inherit='account.payment'
    
    bx_transport_id = fields.Many2one('transport.management',string='Bx Transport')
    transport = fields.Boolean(string='Transport')