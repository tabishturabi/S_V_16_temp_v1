# -*- coding: utf-8 -*-
from odoo import models, fields, api ,_

class resPartner(models.Model):
    _inherit = 'res.partner'

    # name = fields.Char(translate=True, required=True)
    # street = fields.Char(translate=True)
    # street2 = fields.Char(translate=True)
    # city = fields.Char(translate=True)

class resCountryState(models.Model):
    _inherit = 'res.country.state'    

    name = fields.Char(translate=True)