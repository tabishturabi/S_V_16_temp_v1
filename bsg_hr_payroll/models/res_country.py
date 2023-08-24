# -*- coding: utf-8 -*-
from odoo import models,fields,api,_


class ResCountry(models.Model):
    _inherit = 'res.country'

    employee_count = fields.Integer('Employees count', default=0)
    active = fields.Boolean(string="Active", default=True)


     