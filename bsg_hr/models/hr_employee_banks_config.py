# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class BsgHrBanksDeatils(models.Model):
    _name = 'hr.banks.details'
    _description = 'Hr Banks Configuration'
    _rec_name = 'swift_code'
    
    swift_code = fields.Char('Swift Code')
    bank_name = fields.Char('Bank Name')
    
    