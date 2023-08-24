# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class BsgHrAsset(models.Model):
    _name = 'hr.asset'
    _description = "Employee Assets"
    _rec_name = "bsg_typeasset"

    bsg_assettype = fields.Char("Assets Type")
    bsg_issuedate = fields.Date("Issue Date")
    bsg_appro = fields.Many2one('hr.employee',string="Approved by")
    bsg_typeasset = fields.Many2one('hr.asset.type', string="Asset Type")
    assets_emp = fields.Many2one('hr.employee', string="Insurance Ref")
class BsgHrAssetType(models.Model):
    _name = 'hr.asset.type'
    _description = "Employee Asset Type"
    _rec_name = "bsg_name"

    bsg_name = fields.Char("Name")