# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BsgSponsorInfo(models.Model):
    _name = 'bsg.sponsor.info'
    _description = "Sponser Info"

    name = fields.Char(string='Sponsor Name', required=True, store=True)
    sponsor_id = fields.Integer(string='Sponsor ID', required=True)
    partner_id = fields.Many2one('res.partner', string='Contact Person', required=True)
    cr_no = fields.Char(string='CR No')
    street = fields.Char()
    street2 = fields.Char()
    zip_code = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', string="Fed. State")
    country_id = fields.Many2one('res.country', string="Country")
    pob = fields.Char(string='P.O Box No')
    email = fields.Char(related='partner_id.email', store=True)
    phone = fields.Char(related='partner_id.phone', store=True)
    website = fields.Char(related='partner_id.website')
    fax = fields.Char(string="Fax")
    mobile = fields.Char(string='Mobile No')
    branch_id = fields.Many2one('bsg_branches.bsg_branches')
    active = fields.Boolean(string="Active", default=True)
