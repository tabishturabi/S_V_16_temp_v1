# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class BsgHrEmployeesAccessManagemennt(models.Model):
    _name = 'hr.emp.access.mgt'
    _description = "Employee Acess Management"
    _rec_name = "bsg_accesstype"

    bsg_accesstype = fields.Many2one('hr.access.type',string="Access Type")

    bsg_appro = fields.Many2one('hr.employee',string="Approved by")
    access_emp = fields.Many2one('hr.employee',string="Ref")


class BsgHrAssetType(models.Model):
    _name = 'hr.access.type'
    _description = "Employee Asset Type"
    _rec_name = "bsg_name"

    # hracc = fields.Many2one('hr.emp.access.mgt',string="Access Ref")
    bsg_name = fields.Char("Name")