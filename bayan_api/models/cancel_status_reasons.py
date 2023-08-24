# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions,_


class CancelStatusReasons(models.Model):
    _name = 'cancel.status.reasons'

    reason_id = fields.Integer("ID",track_visibility='always')
    name = fields.Char("Reason Name",track_visibility='always',translate=True)