# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BsgImportResUsers(models.Model):
        _inherit = 'res.users'

        can_import = fields.Boolean("Can Import Data",default=False)