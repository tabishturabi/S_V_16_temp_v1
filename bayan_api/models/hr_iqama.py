# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions,_


class BsgHrIqama(models.Model):
    _inherit = 'hr.iqama'

    bayan_issue_number = fields.Integer("Bayan Issue Number",track_visibility='always')