# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class ApprovalsConfiguration(models.Model):
    _name = 'approvals.config'
    _description = 'Approvals Configuration'
    _rec_name = 'code'

    code = fields.Char(string='Code',required=True)
    position_ids = fields.Many2many('hr.job',string="Positions",required=True)
