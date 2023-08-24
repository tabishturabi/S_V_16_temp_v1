# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class bsg_driver_history(models.Model):
	_inherit = 'fleet.vehicle.assignation.log'

	bsg_driver_id = fields.Many2one(string="Driver", comodel_name="hr.employee",related="vehicle_id.bsg_driver",store=True)
	driver_id = fields.Many2one(string="Driver ID", comodel_name="res.partner", required=False)