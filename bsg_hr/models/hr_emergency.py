# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class BsgEmergencyContact(models.Model):
    _name = 'hr.emergency.contact'
    _description = "Emergency Contact"
    _rec_name = "bsg_name"

    bsg_name = fields.Char("Contact Person Name")
    bsg_contact = fields.Char("Contact Number ")
    bsg_relation = fields.Char("Relation")
    emergency_employee = fields.Many2one('hr.employee', string="Emergency Ref")