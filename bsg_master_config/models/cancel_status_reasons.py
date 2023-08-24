# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions,_


class CancelStatusReasons(models.Model):
    _name = 'cancel.status.reasons'
    _description = 'Cancel Status Reasons'

    reason_id = fields.Integer("ID",tracking=True)
    name = fields.Char("Reason Name",tracking=True,translate=True)